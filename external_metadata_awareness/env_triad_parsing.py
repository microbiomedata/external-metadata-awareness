"""Pure parsing helpers for environmental triad values.

Standard library only, so the unit tests do not pull in click, requests,
oaklib or pymongo at import time. See issue #481.
"""

import re
import string

improved_curie_pattern = re.compile(
    r"""
    ^                                   # start of string
    (?:(?P<label_before>.*?)(?:(?<=[a-z])(?=[A-Z])|\s+|(?=[\[\(\{])))?  # optional label before
    (?:[\[\(\{])?                       # optional opening bracket
    (?P<prefix>[A-Za-z][A-Za-z0-9]+)      # prefix
    [:\-_ \uFF1A]+                      # one or more separators
    (?P<local>[A-Za-z0-9]{2,})           # local identifier
    (?:\s*[\]\)\}])?                    # optional closing bracket
    (?:(?:\s*[:\-_ \uFF1A]\s*)(?P<label_after>.+))?  # optional label after
    $                                   # end of string
    """, re.VERBOSE
)

bracketed_pattern = re.compile(
    r"""
    (?P<label>.*?)\s*            # capture any text before the bracket as the label
    [\[\(\{]                    # opening bracket
    (?P<prefix>[A-Za-z][A-Za-z0-9]+)   # prefix
    [:\-_ \uFF1A]+             # separator(s)
    (?P<local>[A-Za-z0-9]{2,})   # local identifier
    \s*[\]\)\}]                # closing bracket
    """, re.VERBOSE
)

trailing_curie_pattern = re.compile(
    r"""
    ^(?P<label>.*?)\s+                   # any text at start as the label (non-greedy)
    (?P<prefix>[A-Za-z][A-Za-z0-9]+)       # prefix
    [:\-_ \uFF1A]+                       # separator(s)
    (?P<local>[A-Za-z0-9]{2,})\s*$         # local identifier until end-of-string
    """, re.VERBOSE
)


def make_plain_component(ann):
    norm = normalize_label(ann)
    return {
        'label': norm,
        'label_digits_only': is_digits_only(norm),
        'lingering_envo': ("envo" in norm),
        'local': None,
        'local_digits_only': False,
        'prefix_uc': None,
        'raw': ann,
        'uses_bioportal_prefix': False,
        'uses_obo_prefix': False,
    }


def is_digits_only(label):
    if label:
        return label.isdigit()
    else:
        return False


def normalize_label(label):
    # Convert to lowercase
    label = label.lower()
    # Replace punctuation and underscore with space
    label = re.sub(rf"[{re.escape(string.punctuation)}]", " ", label)
    # Normalize whitespace
    label = re.sub(r"\s+", " ", label).strip()
    return label


def extract_components(text,
                       known_envo_curies=None,
                       obo_ontology_indicators_lc=None,
                       bioportal_ontology_indicators_lc=None,
                       known_prefixes=None):
    if not isinstance(text, str):
        return []

    components = []

    # Pre-clean the text.
    text = text.strip().strip('“”"\'')
    text = re.sub(r'\b(ENVO:){2,}', 'ENVO:', text, flags=re.IGNORECASE)

    # If text contains a bracketed CURIE, use that branch.
    if re.search(r'[\[\(\{].+[\]\)\}]', text):
        found = False
        for m in bracketed_pattern.finditer(text):
            found = True
            raw = m.group(0)
            label = m.group('label').strip() if m.group('label') else None
            if label:
                label = normalize_label(label)
            components.append({
                'label': label,
                'label_digits_only': is_digits_only(label) if label else False,
                'lingering_envo': (("ENVO" in label.upper()) if label else False),
                'local': m.group('local'),
                'local_digits_only': is_digits_only(m.group('local')),
                'prefix_uc': m.group('prefix').upper() if m.group('prefix') else None,
                'raw': raw,
                'uses_bioportal_prefix': bool(bioportal_ontology_indicators_lc and
                                              m.group('prefix').upper() in {x.upper() for x in
                                                                            bioportal_ontology_indicators_lc}),
                'uses_obo_prefix': bool(obo_ontology_indicators_lc and
                                        m.group('prefix').upper() in {x.upper() for x in obo_ontology_indicators_lc}),
            })
        if found:
            return components
        return [make_plain_component(text)]

    # Otherwise, split text on delimiters (pipe, semicolon, comma).
    annotations = re.split(r'\|+|;+|,+', text)
    for ann in annotations:
        ann = ann.strip()
        if not ann:
            continue

        # If no obvious separator is found, treat as plain text.
        if not any(sep in ann for sep in [":", "-", "_", "\uFF1A"]):
            components.append(make_plain_component(ann))
            continue

        ann = ann.strip('“”"\'')
        ann = re.sub(r'\b(ENVO:){2,}', 'ENVO:', ann, flags=re.IGNORECASE)

        # If the annotation ends with a CURIE-like pattern, force use of the trailing matcher.
        if re.search(r'\s+[A-Za-z][A-Za-z0-9]+[:\-_ \uFF1A][A-Za-z0-9]{2,}\s*$', ann):
            m = trailing_curie_pattern.match(ann)
        else:
            m = improved_curie_pattern.match(ann)

        if m:
            candidate_prefix = m.group('prefix').upper()
            # Validate the prefix using the passed-in known_prefixes.
            if candidate_prefix not in known_prefixes:
                components.append(make_plain_component(ann))
                continue

            prefix = candidate_prefix
            local = m.group('local')
            label = None
            if "label_after" in m.groupdict() and m.group('label_after'):
                label = m.group('label_after')
            elif "label_before" in m.groupdict() and m.group('label_before'):
                label = m.group('label_before')
            elif "label" in m.groupdict():
                label = m.group('label')
            if label:
                label = normalize_label(label)
            components.append({
                'label': label,
                'label_digits_only': is_digits_only(label) if label else False,
                'lingering_envo': False,
                'local': local,
                'local_digits_only': is_digits_only(local),
                'prefix_uc': prefix,
                'raw': ann,
                'uses_bioportal_prefix': bool(bioportal_ontology_indicators_lc and
                                               prefix in {x.upper() for x in bioportal_ontology_indicators_lc}),
                'uses_obo_prefix': bool(obo_ontology_indicators_lc and
                                        prefix in {x.upper() for x in obo_ontology_indicators_lc}),
            })
        else:
            components.append(make_plain_component(ann))

    if not components and text.strip():
        components.append(make_plain_component(text))
    return components
