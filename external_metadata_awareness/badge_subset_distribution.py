#!/usr/bin/env python3
"""
Report how many records would earn each metadata-quality badge, at each qualifying bar.

A badge subset is any LinkML subset carrying a qualifying-bar annotation
(`badge_minimum_slots` in nmdc-schema). A record earns the badge when it populates at
least that many of the subset's slots. This reports the earn rate at every bar from 1 up,
and marks the bar the schema currently ships, so a bar can be chosen against real fill
rates rather than guessed.

Counts documents in the NMDC production MongoDB, so a slot is populated when its key is
present and non-empty. Needs the jump-server tunnel:

    ssh -f -N -i ~/.ssh/jump-dev.microbiomedata.org.private_key \\
        -L 27124:runtime-api-mongodb-headless.nmdc-prod.svc.cluster.local:27017 \\
        ssh-mongo@jump-dev.microbiomedata.org

and local/nmdc-prod.env holding MONGO_USER and MONGO_PASSWORD for production. That is a
different file from local/.env, whose credentials are for a local MongoDB.

Run it through make, which names the target after the TSV it produces:

    make local/badge_subset_distribution.tsv
    make local/badge_subset_distribution.tsv SCHEMA_REF=v11.23.0
"""

import csv
import logging
import pathlib
from typing import Any, Iterable

import click
from linkml_runtime.utils.schemaview import SchemaView

from external_metadata_awareness.mongodb_connection import get_mongo_client

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

SCHEMA_URL_TEMPLATE = (
    'https://raw.githubusercontent.com/microbiomedata/nmdc-schema/{ref}/'
    'nmdc_schema/nmdc_materialized_patterns.yaml'
)
DEFAULT_BAR_ANNOTATION = 'badge_minimum_slots'
# directConnection is required: over the tunnel the driver otherwise discovers the
# replica set's internal cluster hostnames and cannot resolve them.
DEFAULT_MONGO_URI = 'mongodb://localhost:27124/nmdc?directConnection=true'
EMPTY = (None, '', [], {})


def badge_subsets(view: SchemaView, annotation: str) -> dict[str, dict[str, Any]]:
    """Subsets carrying the qualifying-bar annotation, with their slots and that bar.

    Discovered from the annotation rather than a hardcoded list, so a subset added later
    is picked up without editing this module.
    """
    subsets: dict[str, dict[str, Any]] = {}
    for name in view.all_subsets():
        found = (view.get_subset(name).annotations or {}).get(annotation)
        if found is not None:
            subsets[name] = {'bar': int(found.value), 'slots': []}
    for slot_name in view.all_slots():
        for subset in view.get_slot(slot_name).in_subset or []:
            if str(subset) in subsets:
                subsets[str(subset)]['slots'].append(slot_name)
    return subsets


def populated_counts(
    collection, subsets: dict[str, dict[str, Any]]
) -> tuple[dict[str, list[int]], dict[str, dict[str, int]]]:
    """How many slots each document populates, and how many documents populate each slot.

    One pass over the collection, projecting only the slots any badge subset names, so
    the wide Biosample documents are not pulled over the tunnel in full.

    The per-slot totals are what show whether a subset is carrying slots nobody fills,
    which is a different question from where to set the bar and bears on whether a slot
    belongs in the subset at all.
    """
    slots = sorted({slot for spec in subsets.values() for slot in spec['slots']})
    projection = {slot: 1 for slot in slots}
    projection['_id'] = 0

    counts: dict[str, list[int]] = {name: [] for name in subsets}
    per_slot: dict[str, dict[str, int]] = {
        name: dict.fromkeys(spec['slots'], 0) for name, spec in subsets.items()
    }
    for document in collection.find({}, projection):
        for name, spec in subsets.items():
            populated = [slot for slot in spec['slots'] if document.get(slot) not in EMPTY]
            counts[name].append(len(populated))
            for slot in populated:
                per_slot[name][slot] += 1
    return counts, per_slot


def distribution_rows(
    name: str, spec: dict[str, Any], counts: list[int], max_bar: int
) -> list[dict[str, Any]]:
    """One row per bar, flagging the bar the schema currently ships."""
    rows = []
    for bar in range(1, max_bar + 1):
        earners = sum(1 for count in counts if count >= bar)
        rows.append({
            'subset': name,
            'bar': bar,
            'earners': earners,
            'records': len(counts),
            'pct': f'{100 * earners / len(counts):.2f}' if counts else '',
            'is_current_bar': bar == spec['bar'],
        })
    return rows


def write_tsv(path: pathlib.Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)


@click.command()
@click.option('--mongo-uri', default=DEFAULT_MONGO_URI, show_default=True,
              help='MongoDB URI, including the database. Default is the jump-server tunnel.')
@click.option('--env-file', default='local/nmdc-prod.env', show_default=True,
              help='Env file supplying MONGO_USER and MONGO_PASSWORD for NMDC production. '
                   'Kept separate from local/.env, which holds local MongoDB credentials.')
@click.option('--collection', default='biosample_set', show_default=True,
              help='Collection to count.')
@click.option('--schema-ref', default='main', show_default=True,
              help='nmdc-schema branch, tag or commit supplying subset membership and bars.')
@click.option('--schema', default=None,
              help='Schema path or URL, overriding --schema-ref.')
@click.option('--bar-annotation', default=DEFAULT_BAR_ANNOTATION, show_default=True,
              help='Subset annotation carrying the qualifying bar.')
@click.option('--max-bar', default=5, show_default=True, type=click.IntRange(min=1),
              help='Highest bar to report.')
@click.option('--output', type=click.Path(path_type=pathlib.Path),
              help='Write the distribution to this TSV as well as logging it.')
def main(
    mongo_uri: str,
    env_file: str,
    collection: str,
    schema_ref: str,
    schema: str | None,
    bar_annotation: str,
    max_bar: int,
    output: pathlib.Path | None,
) -> None:
    """Report badge earn rates per record, at bars 1 through --max-bar."""
    source = schema or SCHEMA_URL_TEMPLATE.format(ref=schema_ref)
    view = SchemaView(source)
    subsets = badge_subsets(view, bar_annotation)
    if not subsets:
        raise click.ClickException(f'no subset in {source} carries a {bar_annotation} annotation')

    client = get_mongo_client(mongo_uri, env_file=env_file)
    database = client.get_database()
    counts, per_slot = populated_counts(database[collection], subsets)

    # The materialized-patterns file carries no release version, so the ref the user
    # named is the only honest identifier for which schema these bars came from.
    logger.info('schema %s', schema or f'nmdc-schema {schema_ref}')
    logger.info('%s.%s', database.name, collection)

    rows = []
    for name, spec in sorted(subsets.items()):
        subset_rows = distribution_rows(name, spec, counts[name], max_bar)
        rows.extend(subset_rows)
        logger.info('')
        logger.info('%s: %d slots, current bar %d', name, len(spec['slots']), spec['bar'])
        logger.info('  bar  earners      pct')
        for row in subset_rows:
            marker = '  <- current bar' if row['is_current_bar'] else ''
            logger.info('   %d   %7s   %6s%%%s',
                        row['bar'], f"{row['earners']:,}", row['pct'], marker)
        if spec['bar'] > max_bar:
            # The shipped bar is off the end of the report, so nothing was flagged.
            logger.info('  current bar %d is above --max-bar %d', spec['bar'], max_bar)
        logger.info('  most slots on any one record: %d', max(counts[name], default=0))
        dead = sorted(slot for slot, count in per_slot[name].items() if count == 0)
        if dead:
            logger.info('  populated on no record (%d): %s', len(dead), ', '.join(dead))
        top = sorted(per_slot[name].items(), key=lambda item: -item[1])[:8]
        logger.info('  most populated: %s', ', '.join(f'{k}={v:,}' for k, v in top))

    if output:
        write_tsv(output, rows)
        logger.info('')
        logger.info('wrote %s', output)


if __name__ == '__main__':
    main()
