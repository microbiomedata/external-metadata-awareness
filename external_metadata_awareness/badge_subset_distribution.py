#!/usr/bin/env python3
"""
Report how many records would earn each metadata-quality badge, at each qualifying bar.

A badge subset is any LinkML subset carrying a qualifying-bar annotation
(`badge_minimum_slots` in nmdc-schema). A record earns the badge when it populates at
least that many of the subset's slots. This reports the earn rate at a range of bars so
a bar can be chosen against real fill rates rather than guessed.

Reads flattened parquet rather than MongoDB, so it needs no tunnel and no credentials.
Side tables are counted: multivalued slots such as host_diet are not columns in the main
table, and ignoring them undercounts any subset that contains one.

The schema is a path or URL, so this is not tied to nmdc-schema.

Run it through make, which names the target after the TSV it produces:

    make local/badge_subset_distribution.tsv
    make local/badge_subset_distribution.tsv NMDC_DUMP_DIR=/path/to/a/newer/dump
"""

import csv
import logging
import pathlib
from typing import Any, Iterable

import click
import numpy as np
import pyarrow.parquet as pq
from linkml_runtime.utils.schemaview import SchemaView

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

DEFAULT_SCHEMA = (
    'https://raw.githubusercontent.com/microbiomedata/nmdc-schema/main/'
    'nmdc_schema/nmdc_materialized_patterns.yaml'
)
DEFAULT_BAR_ANNOTATION = 'badge_minimum_slots'
SIDE_TABLE_ID_COLUMNS = ('biosample_set_id', 'id', '_source_id', 'parent_id')


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


def side_table_members(dump_dir: pathlib.Path, stem: str) -> dict[str, set[str]]:
    """Record ids present in each side table, keyed by the slot that table holds.

    Only the id column is read. Side tables carry every flattened field of the nested
    value, and reading all of them to collect one column costs memory proportional to
    the whole dump for no gain.
    """
    members: dict[str, set[str]] = {}
    for path in dump_dir.glob(f'{stem}_*.parquet'):
        available = pq.ParquetFile(path).schema_arrow.names
        id_columns = [c for c in SIDE_TABLE_ID_COLUMNS if c in available]
        if not id_columns:
            logger.warning('no id column in %s, its slot will read as unpopulated', path.name)
            continue
        column = pq.read_table(path, columns=[id_columns[0]]).column(id_columns[0])
        members[path.stem[len(stem) + 1:]] = set(column.to_pylist())
    return members


def slot_populated(
    slot: str,
    table: Any,
    columns: set[str],
    ids: np.ndarray,
    side: dict[str, set[str]],
) -> tuple[np.ndarray, bool]:
    """Per-record mask for one slot, and whether the slot was found at all.

    The prefix match is what picks up a QuantityValue slot's expansion into
    `<slot>_has_numeric_value` and its siblings.

    This runs once per slot per subset, so it stays in numpy. Going through
    `to_pylist()` here builds a Python list per column and dominates the runtime.
    """
    mask = np.zeros(table.num_rows, dtype=bool)
    matched = [c for c in columns if c == slot or c.startswith(f'{slot}_')]
    for column in matched:
        mask |= table.column(column).is_valid().to_numpy(zero_copy_only=False)
    if slot in side:
        mask |= np.isin(ids, list(side[slot]))
    return mask, bool(matched) or slot in side


def write_tsv(path: pathlib.Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)


@click.command()
@click.option(
    '--dump-dir',
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    help='Directory holding the flattened parquet and its side tables.',
)
@click.option('--stem', default='biosample_set', show_default=True,
              help='Parquet basename, without .parquet. Side tables are <stem>_*.parquet.')
@click.option('--schema', default=DEFAULT_SCHEMA, show_default=True,
              help='LinkML schema path or URL supplying subset membership.')
@click.option('--bar-annotation', default=DEFAULT_BAR_ANNOTATION, show_default=True,
              help='Subset annotation carrying the qualifying bar.')
@click.option('--max-bar', default=5, show_default=True, type=click.IntRange(min=1),
              help='Highest bar to report.')
@click.option('--output', type=click.Path(path_type=pathlib.Path),
              help='Write the distribution to this TSV as well as logging it.')
def main(
    dump_dir: pathlib.Path,
    stem: str,
    schema: str,
    bar_annotation: str,
    max_bar: int,
    output: pathlib.Path | None,
) -> None:
    """Report badge earn rates per record, at bars 1 through --max-bar."""
    main_table = dump_dir / f'{stem}.parquet'
    if not main_table.exists():
        raise click.ClickException(f'no {main_table.name} in {dump_dir}')

    view = SchemaView(schema)
    subsets = badge_subsets(view, bar_annotation)
    if not subsets:
        raise click.ClickException(f'no subset in {schema} carries a {bar_annotation} annotation')

    table = pq.read_table(main_table)
    columns = set(table.column_names)
    ids = table.column('id').to_numpy(zero_copy_only=False)
    side = side_table_members(dump_dir, stem)

    logger.info('schema %s, %s records from %s', view.schema.version, f'{table.num_rows:,}', dump_dir.name)
    rows = []

    for name, spec in sorted(subsets.items()):
        counts = np.zeros(table.num_rows, dtype=int)
        per_slot, unfound = {}, []
        for slot in spec['slots']:
            mask, found = slot_populated(slot, table, columns, ids, side)
            if not found:
                unfound.append(slot)
            counts += mask.astype(int)
            per_slot[slot] = int(mask.sum())

        logger.info('')
        logger.info('%s: %d slots, shipped bar %d', name, len(spec['slots']), spec['bar'])
        if unfound:
            # Neither a column nor a side table. That is a finding about the flattening,
            # not about the data, so it is worth surfacing rather than silently zeroing.
            logger.info('  absent from the dump: %s', ', '.join(sorted(unfound)))
        logger.info('  bar  earners      pct')
        for bar in range(1, max_bar + 1):
            earners = int((counts >= bar).sum())
            pct = 100 * earners / table.num_rows
            logger.info('   %d   %7s   %6.2f%%', bar, f'{earners:,}', pct)
            rows.append({
                'subset': name,
                'bar': bar,
                'earners': earners,
                'records': table.num_rows,
                'pct': f'{pct:.2f}',
                'shipped_bar': spec['bar'],
            })
        logger.info('  most slots on any one record: %d', int(counts.max()))
        logger.info('  slots populated on no record: %d',
                    sum(1 for count in per_slot.values() if count == 0))
        top = sorted(per_slot.items(), key=lambda item: -item[1])[:8]
        logger.info('  most populated: %s', ', '.join(f'{k}={v:,}' for k, v in top))

    if output:
        write_tsv(output, rows)
        logger.info('')
        logger.info('wrote %s', output)


if __name__ == '__main__':
    main()
