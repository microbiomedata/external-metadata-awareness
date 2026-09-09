"""Unit tests for badge subset discovery, slot counting, and bar flagging.

The failure that matters here is silent: a wrong emptiness rule or a wrong bar flag
changes the reported earn rate without raising anything, and the number goes into a
squad decision about where to set the bar.
"""

import pytest
from linkml_runtime.linkml_model.annotations import Annotation
from linkml_runtime.linkml_model.meta import (
    SchemaDefinition,
    SlotDefinition,
    SubsetDefinition,
)
from linkml_runtime.utils.schemaview import SchemaView

from external_metadata_awareness import badge_subset_distribution as bsd


class FakeCollection:
    """Stands in for a pymongo collection, recording the projection it was given."""

    def __init__(self, documents):
        self.documents = documents
        self.projection = None

    def find(self, query, projection):
        self.projection = projection
        return iter(self.documents)


@pytest.fixture
def view():
    """One subset carrying a bar of 3, one carrying none."""
    schema = SchemaDefinition(id="https://example.invalid/test", name="test")
    scored = SubsetDefinition(name="scored")
    scored.annotations["badge_minimum_slots"] = Annotation(tag="badge_minimum_slots", value=3)
    schema.subsets["scored"] = scored
    schema.subsets["unscored"] = SubsetDefinition(name="unscored")
    schema.slots["ph"] = SlotDefinition(name="ph", in_subset=["scored"])
    schema.slots["host_diet"] = SlotDefinition(name="host_diet", in_subset=["scored"])
    schema.slots["elsewhere"] = SlotDefinition(name="elsewhere", in_subset=["unscored"])
    return SchemaView(schema)


def test_badge_subsets_reads_only_annotated_subsets(view):
    subsets = bsd.badge_subsets(view, "badge_minimum_slots")

    assert set(subsets) == {"scored"}
    assert subsets["scored"]["bar"] == 3
    assert sorted(subsets["scored"]["slots"]) == ["host_diet", "ph"]


def test_badge_subsets_is_empty_when_no_subset_carries_the_annotation(view):
    assert bsd.badge_subsets(view, "no_such_annotation") == {}


def test_projection_asks_only_for_badge_slots():
    """Biosample documents are wide; pulling them whole over the tunnel is the slow path."""
    subsets = {"scored": {"bar": 2, "slots": ["ph", "host_diet"]}}
    collection = FakeCollection([{}])

    bsd.populated_counts(collection, subsets)

    assert collection.projection == {"ph": 1, "host_diet": 1, "_id": 0}


@pytest.mark.parametrize(
    "value, populated",
    [
        (7.0, True),
        (0, True),  # a real measurement of zero is data, not absence
        ({"has_numeric_value": 7.0}, True),
        (None, False),
        ("", False),
        ([], False),
        ({}, False),
    ],
)
def test_emptiness_rule(value, populated):
    subsets = {"scored": {"bar": 1, "slots": ["ph"]}}
    collection = FakeCollection([{"ph": value}])

    counts, _ = bsd.populated_counts(collection, subsets)

    assert counts["scored"] == [1 if populated else 0]


def test_absent_key_counts_as_unpopulated():
    subsets = {"scored": {"bar": 1, "slots": ["ph", "host_diet"]}}
    collection = FakeCollection([{"ph": 7.0}])

    assert bsd.populated_counts(collection, subsets)[0]["scored"] == [1]


def test_counts_are_independent_per_subset():
    subsets = {
        "a": {"bar": 1, "slots": ["ph"]},
        "b": {"bar": 1, "slots": ["host_diet", "ph"]},
    }
    collection = FakeCollection([{"ph": 7.0, "host_diet": "grain"}])

    counts, _ = bsd.populated_counts(collection, subsets)

    assert counts == {"a": [1], "b": [2]}


def test_per_slot_totals_include_slots_no_document_populates():
    """A slot nobody fills must appear with a zero, not vanish from the tally."""
    subsets = {"scored": {"bar": 1, "slots": ["ph", "never_filled"]}}
    collection = FakeCollection([{"ph": 7.0}, {"ph": 8.0}])

    _, per_slot = bsd.populated_counts(collection, subsets)

    assert per_slot == {"scored": {"ph": 2, "never_filled": 0}}


def test_distribution_is_cumulative_and_flags_the_current_bar():
    spec = {"bar": 2, "slots": ["a", "b", "c"]}

    rows = bsd.distribution_rows("scored", spec, [0, 1, 2, 3], max_bar=3)

    assert [row["earners"] for row in rows] == [3, 2, 1]
    assert [row["is_current_bar"] for row in rows] == [False, True, False]
    assert rows[0]["pct"] == "75.00"


def test_no_bar_is_flagged_when_the_current_bar_is_above_max_bar():
    spec = {"bar": 9, "slots": ["a"]}

    rows = bsd.distribution_rows("scored", spec, [1], max_bar=3)

    assert not any(row["is_current_bar"] for row in rows)


def test_slot_rows_are_ordered_by_fill_then_name():
    rows = bsd.slot_rows("scored", {"a": 1, "b": 3, "c": 1}, records=4)

    assert [row["slot"] for row in rows] == ["b", "a", "c"]
    assert [row["populated"] for row in rows] == [3, 1, 1]
    assert rows[0]["pct"] == "75.00"


def test_slot_rows_keep_slots_no_record_populates():
    """The zeros are the point: they show a subset carrying slots nobody fills."""
    rows = bsd.slot_rows("scored", {"filled": 2, "empty": 0}, records=2)

    assert [(row["slot"], row["populated"]) for row in rows] == [("filled", 2), ("empty", 0)]


def test_write_tsv_round_trips(tmp_path):
    path = tmp_path / "nested" / "out.tsv"

    bsd.write_tsv(path, [{"subset": "scored", "bar": 1, "earners": 2}])

    lines = path.read_text().splitlines()
    assert lines[0] == "subset\tbar\tearners"
    assert lines[1] == "scored\t1\t2"
