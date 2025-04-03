import click
import pandas as pd
from linkml_runtime import SchemaView
from jsonasobj2 import as_dict
import os
import collections.abc
from linkml_runtime.utils.yamlutils import extended_int


def safe_stringify(value, feature_name=None, class_name=None, slot_name=None):
    try:
        if isinstance(value, extended_int):
            return int(value)
        elif isinstance(value, str):
            return value
        elif isinstance(value, collections.abc.Sequence) and all(isinstance(v, str) for v in value):
            return "|".join(value)
        elif isinstance(value, collections.abc.Sequence):
            result = "|".join(repr(v) for v in value)
            typename = type(value).__name__
            click.echo(f"[SAFE_FLATTENED] {class_name}.{slot_name}.{feature_name} from {typename}")
            return result
        elif isinstance(value, dict) or hasattr(value, "__dict__"):
            result = repr(value)
            typename = type(value).__name__
            click.echo(f"[SAFE_FLATTENED] {class_name}.{slot_name}.{feature_name} from {typename}")
            return result
        else:
            return str(value)
    except Exception as e:
        typename = type(value).__name__
        click.echo(f"[ERROR] {class_name}.{slot_name}.{feature_name} could not stringify {typename}: {e}")
        return f"<<unstringifiable:{typename}>>"


@click.command()
@click.option("--schema", type=str, required=True, help="Path or URL to the LinkML YAML schema.")
@click.option("--output", "-o", type=click.Path(), help="Path to save output as TSV")
def flatten_schema(schema, output):
    click.echo(f"Loading schema from: {schema}")
    schema_view = SchemaView(schema)

    class_names = sorted(schema_view.all_classes().keys())
    report = []
    error_count = 0

    for c_name in class_names:
        ic = schema_view.induced_class(c_name)

        for slot_name in sorted(ic.attributes.keys()):
            ica = ic.attributes[slot_name]
            ica_dict = ica.__dict__
            row = {
                "class": c_name,
                "class_uri": ic.class_uri,
                "slot": slot_name,
                "slot_uri": ica.slot_uri,
            }

            for k, v in ica_dict.items():
                try:
                    if k in ['from_schema', 'name', 'owner', 'domain_of']:
                        click.echo(f"[SKIPPED] {c_name}.{slot_name}.{k}")
                        continue
                    if v is None:
                        continue

                    if k == 'alias':
                        if isinstance(v, list):
                            alias_str = '|'.join(v)
                        else:
                            alias_str = v
                        if alias_str != slot_name:
                            row['alias'] = alias_str
                        else:
                            click.echo(f"[IGNORED] {c_name}.{slot_name}.alias is same as slot name: '{alias_str}'")

                    elif k == 'structured_pattern':
                        row['structured_pattern.syntax'] = v.syntax
                        click.echo(f"[FLATTENED_LOSSY] {c_name}.{slot_name}.structured_pattern.syntax")
                        if not v.interpolated:
                            click.echo(f"  [WARN] Not interpolated")
                        if v.partial_match:
                            click.echo(f"  [WARN] Partial match = TRUE")
                        for i in set(v.__dict__.keys()):
                            if v[i] and i not in ['syntax', 'interpolated', 'partial_match']:
                                click.echo(f"  [WARN] Unexpected field: {i}")

                    elif k == 'examples':
                        example_values = []
                        for example in v:
                            if example.value:
                                example_values.append(example.value)
                                if example.description:
                                    click.echo(
                                        f"[INFO] {c_name}.{slot_name}.example {example.value} has description: {example.description}")
                        row['example_values'] = '|'.join(example_values)
                        click.echo(f"[FLATTENED_LOSSY] {c_name}.{slot_name}.examples")

                    elif k == 'annotations':
                        anndict = as_dict(ica.annotations)
                        for anndictk, anndictv in anndict.items():
                            row[f"annotation_{anndictk}"] = anndictv['value']
                            click.echo(f"[FLATTENED_LOSSY] {c_name}.{slot_name}.annotation_{anndictk}")

                    else:
                        row[k] = safe_stringify(v, feature_name=k, class_name=c_name, slot_name=slot_name)

                except Exception as e:
                    error_count += 1
                    typename = type(v).__name__
                    click.echo(f"[ERROR] {c_name}.{slot_name}.{k} encountered {typename}: {e}")
                    continue

            report.append(row)

    df = pd.DataFrame(report)

    # Drop fully empty rows
    df.dropna(how='all', inplace=True)

    # Drop columns that are all empty or just JsonObj() / {}
    cols_to_drop = []
    for col in df.columns:
        vals = df[col].dropna().map(str).str.strip()
        if vals.empty or vals.eq("").all() or vals.isin(["{}", "JsonObj()"]).all():
            cols_to_drop.append(col)
    if cols_to_drop:
        click.echo(f"Dropping {len(cols_to_drop)} empty or trivial columns: {cols_to_drop}")
        df.drop(columns=cols_to_drop, inplace=True)

    # Reorder columns
    all_columns = list(df.columns)
    base_cols = ['class', 'class_uri', 'slot', 'slot_uri']
    mapping_cols = sorted([c for c in all_columns if 'mappings' in c and c not in base_cols])
    other_cols = sorted([c for c in all_columns if c not in base_cols + mapping_cols])
    ordered_columns = [c for c in base_cols if c in all_columns] + mapping_cols + other_cols
    df = df[ordered_columns]

    df.drop_duplicates(inplace=True)

    if output:
        df.to_csv(output, sep="\t", index=False)
        click.echo(f"TSV output written to: {output}")

    click.echo(f"Processed {len(df)} rows with {df.shape[1]} columns.")
    click.echo(f"Encountered {error_count} feature-level errors during flattening.")


if __name__ == "__main__":
    flatten_schema()
