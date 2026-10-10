# Coverage Note

**Command:** `python -m pytest --cov=. --cov-report=term-missing --cov-report=html`
**Result:** 35 tests passed; statement coverage is **100%** (94/94) for the maintained application modules `inventory.py` and `pricing_refactored.py`. The HTML report is generated at `htmlcov/index.html`.

Pytest is configured to collect Lab 5 tests from `tests/` only. Coverage omits the Lab 4 exercise copies, the provided handout, the archived `pricing_legacy.py`, and test files; the reported 100% therefore describes the two maintained application modules, not every Python file in the repository.

## Coverage questions

1. **Which lines have not yet run successfully, and what is the risk?** The current report has no unexecuted statements in `inventory.py` or `pricing_refactored.py`. Before adding the tests for `InventoryItem`, duplicate additions, `restock`, and `get_total_value`, those lines were uncovered: invalid item data could enter the inventory, stock adjustments could fail unnoticed, or the reported inventory value could be wrong. The corresponding tests now exercise those paths. The coverage report is for line execution, not proof of correct results for every possible input.
2. **Why does 100% coverage not mean good tests?** A line can run without its important behavior being asserted. For example, the `sell` type guard runs for strings and floats, but without a Boolean-specific test it would be possible to remove the `bool` rejection and still execute that same line. Since Python treats `bool` as a subclass of `int`, `True` could then sell one item. `test_sell_boolean_amount_is_rejected_without_changing_stock` now checks that boundary explicitly.
3. **If only three tests could be added, which would come first?** I would prioritize a Boolean sale amount (it is an integer subtype in Python), a non-integer `restock` amount (stock counts should be whole units, subject to confirming that contract), and duplicate-name behavior after whitespace normalization (the item stores a trimmed name, so the key/uniqueness rule should be made explicit). These target type and identity boundaries that ordinary happy-path tests are unlikely to expose.

The Lab prompt leaves negative `threshold` behavior to the student. This implementation and its test reject negative thresholds with `ValueError`, because a negative low-stock cutoff is not meaningful for this inventory model.
