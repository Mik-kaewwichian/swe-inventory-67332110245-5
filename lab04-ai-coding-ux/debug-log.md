# Phase 3B — Debug Log

**Module:** `discount.py`  
**Tests:** `tests/test_discount.py`  
**AI use:** AI-assisted explanation and debugging. The failing behavior was reproduced, compared against test expectations, then fixed and rerun.

## Reproduce

Command run from `lab04-ai-coding-ux/`:

```powershell
python -m pytest tests/test_discount.py -v
```

Baseline: **4 failed, 2 passed**.

| Test | Traceback / assertion observed | Hypothesis and root cause | Confirmation | Fix |
|---|---|---|---|---|
| `test_apply_discount_basic` | Expected `90.0`, got `99.9` for price `100.0`, percent `10` | `apply_discount` subtracts `percent / 100` as a currency amount instead of subtracting 10% of the price | Old expression is `100 - 10 / 100 = 99.9`; required expression is `100 * (1 - 10 / 100) = 90` | Calculate remaining price as `price * (1 - percent / 100)` |
| `test_bulk_total` | Expected `270.0`, got `299.9` for three prices of `100.0`, discount `10` | `bulk_total` delegates to `apply_discount`, so the same percentage formula bug affects the aggregate | Total before discount is 300; old calculation gives `300 - 0.1 = 299.9`, while 10% off gives `300 * 0.9 = 270` | Fixed by correcting shared `apply_discount`; no duplicate formula added |
| `test_average_price_empty` | Traceback ends at `sum(prices) / len(prices)` with `ZeroDivisionError: division by zero` | Empty input reaches division with a zero-length denominator | For `[]`, `sum([]) == 0` and `len([]) == 0`; the test explicitly requires `0.0` | Return `0.0` when `prices` is empty |
| `test_cheapest_n` | Expected `[10.0, 20.0]`, got `[20.0]` | The slice starts at index 1, dropping the cheapest item | Sorted input is `[10.0, 20.0, 30.0, 50.0]`; `ordered[1:2]` is `[20.0]` | Return `ordered[:n]` |

## Fix verification

After applying the three root-cause fixes, command run from `lab04-ai-coding-ux/`:

```powershell
python -m pytest tests/test_discount.py -v
```

Result: **6 passed**.

## Commit record

Each root-cause fix is committed separately with a message that describes the defect:

1. Discount percentage calculation
2. Empty-input average
3. Cheapest-items slice boundary
