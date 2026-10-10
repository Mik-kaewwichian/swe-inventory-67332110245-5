# Coverage Note — `Inventory`

**Command:** `python -m pytest tests/test_inventory.py -v --cov=inventory --cov-report=term-missing`
**Result:** 14 tests passed; statement coverage for `inventory.py` is **76%** (34/45 statements).

## Coverage review

1. **What is not covered?** Coverage reports `InventoryItem` validation at lines 6, 8, and 10; duplicate-name handling in `add_item` at line 23; all branches and successful mutation in `restock` at lines 30–35; and `get_total_value` at line 66.
2. **What tests should be added next?** Add parameterized tests for blank names, negative quantity, and non-positive price; duplicate item names; restock success, missing item, and invalid amount; and total value for an empty and populated inventory.
3. **Does 76% coverage prove the inventory is safe?** No. The current tests specifically cover low-stock boundary/filter/sort behavior and sell edge cases. They do not exercise restock or total valuation, and line coverage alone does not establish correctness, concurrency safety, or that assertions verify every business invariant.

## Threshold decision

The Lab prompt leaves negative `threshold` behavior to the student. This implementation and its test choose to reject negative thresholds with `ValueError`, because item quantities cannot be negative and a negative low-stock cutoff is not meaningful for this inventory model.
