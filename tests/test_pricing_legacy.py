import datetime

import pytest

import pricing_refactored
from pricing_refactored import calc


@pytest.fixture(autouse=True)
def reset_pricing_state():
    pricing_refactored.member_points.clear()
    pricing_refactored.LOG.clear()
    yield
    pricing_refactored.member_points.clear()
    pricing_refactored.LOG.clear()


def test_regular_single_item_records_total_and_log():
    assert calc([("Tea", 2, 10.0)]) == 21.4
    assert pricing_refactored.LOG == [(None, 21.4)]


@pytest.mark.parametrize(
    ("quantity", "expected"),
    [
        (49, 104.86),
        (50, 101.65),
        (99, 201.27),
        (100, 192.6),
    ],
)
def test_bulk_discount_threshold_outputs(quantity, expected):
    assert calc([("Tea", quantity, 2.0)]) == expected


def test_zero_quantity_item_is_skipped():
    assert calc([("Tea", 0, 20.0)]) == 0.0


def test_member_discount_records_points_and_final_amount():
    assert calc([("Tea", 100, 2.0)], member="Somchai") == 182.97
    assert pricing_refactored.member_points == {"Somchai": 1}
    assert pricing_refactored.LOG == [("Somchai", 182.97)]


@pytest.mark.parametrize(
    ("coupon", "today", "expected"),
    [
        ("SAVE50", None, 53.5),
        ("HALF", None, 53.5),
        ("NEWYEAR", datetime.date(2026, 1, 15), 85.6),
        ("NEWYEAR", datetime.date(2026, 2, 15), 107.0),
    ],
)
def test_known_coupon_outputs_for_eligible_and_ineligible_dates(coupon, today, expected):
    assert calc([("Tea", 10, 10.0)], coupon=coupon, today=today) == expected


def test_coupon_discount_below_zero_is_clamped_before_tax():
    assert calc([("Tea", 1, 10.0)], coupon="SAVE50") == 0.0


def test_newyear_without_date_uses_current_date(monkeypatch):
    class FixedDate(datetime.date):
        @classmethod
        def today(cls):
            return cls(2026, 1, 15)

    monkeypatch.setattr(pricing_refactored.datetime, "date", FixedDate)

    assert calc([("Tea", 10, 10.0)], coupon="NEWYEAR") == 85.6


def test_member_points_and_log_accumulate_between_calls():
    assert calc([("Tea", 100, 2.0)], member="Somchai") == 182.97
    assert calc([("Tea", 100, 2.0)], member="Somchai") == 182.97

    assert pricing_refactored.member_points == {"Somchai": 2}
    assert pricing_refactored.LOG == [
        ("Somchai", 182.97),
        ("Somchai", 182.97),
    ]
