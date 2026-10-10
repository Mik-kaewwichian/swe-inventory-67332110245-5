import pytest

from inventory import Inventory


def test_low_stock_items_returns_empty_when_every_item_is_above_threshold():
    inventory = Inventory()
    inventory.add_item("Coffee", 6, 10.0)
    inventory.add_item("Tea", 9, 5.0)

    assert inventory.low_stock_items(5) == []


def test_low_stock_items_includes_item_equal_to_threshold():
    inventory = Inventory()
    inventory.add_item("Coffee", 5, 10.0)

    assert inventory.low_stock_items(5) == ["Coffee"]


def test_low_stock_items_sorts_qualifying_names_alphabetically():
    inventory = Inventory()
    inventory.add_item("Tea", 2, 5.0)
    inventory.add_item("Coffee", 1, 10.0)
    inventory.add_item("Rice", 2, 20.0)

    assert inventory.low_stock_items(2) == ["Coffee", "Rice", "Tea"]


def test_low_stock_items_returns_empty_for_empty_inventory():
    inventory = Inventory()

    assert inventory.low_stock_items(5) == []


def test_low_stock_items_with_zero_threshold_returns_only_zero_quantity_items():
    inventory = Inventory()
    inventory.add_item("Coffee", 0, 10.0)
    inventory.add_item("Tea", 1, 5.0)

    assert inventory.low_stock_items(0) == ["Coffee"]


def test_low_stock_items_rejects_negative_threshold():
    inventory = Inventory()
    inventory.add_item("Coffee", 0, 10.0)

    with pytest.raises(ValueError, match="threshold"):
        inventory.low_stock_items(-1)
