"""Unit tests for badge subset discovery and slot-population counting.

Two behaviours here are easy to break silently and both change the reported earn
rate rather than raising: a slot whose value lives only in a side table must not
read as unpopulated, and a QuantityValue slot must be found through its flattened
`<slot>_has_numeric_value` columns rather than an exact name match.
"""

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from linkml_runtime.linkml_model.annotations import Annotation
from linkml_runtime.linkml_model.meta import (
    SchemaDefinition,
    SlotDefinition,
    SubsetDefinition,
)
from linkml_runtime.utils.schemaview import SchemaView

from external_metadata_awareness import badge_subset_distribution as bsd


@pytest.fixture
def view():
    """Two subsets, one carrying a bar and one not, with three slots between them."""
    schema = SchemaDefinition(id="https://example.invalid/test", name="test")
    scored = SubsetDefinition(name="scored")
    scored.annotations["badge_minimum_slots"] = Annotation(tag="badge_minimum_slots", value=3)
    schema.subsets["scored"] = scored
    schema.subsets["unscored"] = SubsetDefinition(name="unscored")
    schema.slots["ph"] = SlotDefinition(name="ph", in_subset=["scored"])
    schema.slots["host_diet"] = SlotDefinition(name="host_diet", in_subset=["scored"])
    schema.slots["elsewhere"] = SlotDefinition(name="elsewhere", in_subset=["unscored"])
    return SchemaView(schema)


@pytest.fixture
def dump(tmp_path):
    """A main table and one side table, in the shape the lakehouse ETL writes."""
    pq.write_table(
        pa.table(
            {
                "id": ["a", "b", "c"],
                "ph_has_numeric_value": [7.0, None, None],
                "elsewhere": ["x", None, None],
            }
        ),
        tmp_path / "biosample_set.parquet",
    )
    pq.write_table(
        pa.table({"biosample_set_id": ["b"], "has_raw_value": ["grain"]}),
        tmp_path / "biosample_set_host_diet.parquet",
    )
    return tmp_path


def test_badge_subsets_reads_only_annotated_subsets(view):
    subsets = bsd.badge_subsets(view, "badge_minimum_slots")

    assert set(subsets) == {"scored"}
    assert subsets["scored"]["bar"] == 3
    assert sorted(subsets["scored"]["slots"]) == ["host_diet", "ph"]


def test_badge_subsets_is_empty_when_no_subset_carries_the_annotation(view):
    assert bsd.badge_subsets(view, "no_such_annotation") == {}


def test_side_table_members_keys_on_the_slot_name(dump):
    assert bsd.side_table_members(dump, "biosample_set") == {"host_diet": {"b"}}


def test_side_table_without_an_id_column_is_skipped(tmp_path):
    pq.write_table(pa.table({"value": [1]}), tmp_path / "biosample_set_orphan.parquet")

    assert bsd.side_table_members(tmp_path, "biosample_set") == {}


def _fixture_args(dump):
    table = pq.read_table(dump / "biosample_set.parquet")
    return (
        table,
        set(table.column_names),
        table.column("id").to_numpy(zero_copy_only=False),
        bsd.side_table_members(dump, "biosample_set"),
    )


def test_quantity_value_slot_is_found_through_its_flattened_column(dump):
    table, columns, ids, side = _fixture_args(dump)

    mask, found = bsd.slot_populated("ph", table, columns, ids, side)

    assert found
    assert list(mask) == [True, False, False]


def test_side_table_only_slot_counts_as_populated(dump):
    table, columns, ids, side = _fixture_args(dump)

    mask, found = bsd.slot_populated("host_diet", table, columns, ids, side)

    assert found
    # Record b has no column for this slot at all, only a side-table row.
    assert list(mask) == [False, True, False]


def test_absent_slot_reports_not_found_rather_than_all_false(dump):
    table, columns, ids, side = _fixture_args(dump)

    mask, found = bsd.slot_populated("never_flattened", table, columns, ids, side)

    assert not found
    assert not mask.any()


def test_prefix_match_does_not_leak_across_slot_names(dump):
    """`ph` must not pick up a hypothetical `phosphate`; the separator is required."""
    table = pa.table({"id": ["a"], "phosphate": [1.0]})
    ids = np.array(["a"])

    mask, found = bsd.slot_populated("ph", table, set(table.column_names), ids, {})

    assert not found
    assert not mask.any()


def test_write_tsv_round_trips(tmp_path):
    path = tmp_path / "nested" / "out.tsv"

    bsd.write_tsv(path, [{"subset": "scored", "bar": 1, "earners": 2}])

    lines = path.read_text().splitlines()
    assert lines[0] == "subset\tbar\tearners"
    assert lines[1] == "scored\t1\t2"
