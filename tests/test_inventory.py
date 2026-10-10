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


def test_sell_decreases_stock_by_amount():
    inventory = Inventory()
    inventory.add_item("Coffee", 5, 10.0)

    assert inventory.sell("Coffee", 2) == 3
    assert inventory._items["Coffee"].quantity == 3


def test_sell_all_remaining_stock_leaves_zero():
    inventory = Inventory()
    inventory.add_item("Coffee", 5, 10.0)

    assert inventory.sell("Coffee", 5) == 0
    assert inventory._items["Coffee"].quantity == 0


def test_sell_zero_amount_is_rejected_without_changing_stock():
    inventory = Inventory()
    inventory.add_item("Coffee", 5, 10.0)

    with pytest.raises(ValueError):
        inventory.sell("Coffee", 0)

    assert inventory._items["Coffee"].quantity == 5


def test_sell_negative_amount_is_rejected_without_changing_stock():
    inventory = Inventory()
    inventory.add_item("Coffee", 5, 10.0)

    with pytest.raises(ValueError):
        inventory.sell("Coffee", -1)

    assert inventory._items["Coffee"].quantity == 5


def test_sell_more_than_available_is_rejected_without_changing_stock():
    inventory = Inventory()
    inventory.add_item("Coffee", 5, 10.0)

    with pytest.raises(ValueError, match="ไม่เพียงพอ"):
        inventory.sell("Coffee", 6)

    assert inventory._items["Coffee"].quantity == 5


def test_sell_unknown_item_raises_key_error_with_item_name():
    inventory = Inventory()

    with pytest.raises(KeyError, match="Coffee"):
        inventory.sell("Coffee", 1)


def test_sell_fractional_amount_is_rejected_without_changing_stock():
    inventory = Inventory()
    inventory.add_item("Coffee", 5, 10.0)

    with pytest.raises(TypeError):
        inventory.sell("Coffee", 1.5)

    assert inventory._items["Coffee"].quantity == 5


def test_sell_text_amount_is_rejected_without_changing_stock():
    inventory = Inventory()
    inventory.add_item("Coffee", 5, 10.0)

    with pytest.raises(TypeError):
        inventory.sell("Coffee", "2")

    assert inventory._items["Coffee"].quantity == 5
