# Pricing Legacy: Behavior Walkthrough and Code Smells

## What `calc` does, in order

1. Starts a subtotal at zero and walks through each `(name, quantity, unit_price)` item.
2. Skips items whose quantity is zero or negative; for other items it multiplies quantity by unit price.
3. Applies a per-item bulk discount: 10% for quantity 100 or more, otherwise 5% for quantity 50–99.
4. Adds the discounted line amount to the running subtotal.
5. If a member is supplied, initializes its stored points if needed, applies 5% to the subtotal, and adds one point per 100 baht of that post-member-discount subtotal.
6. Applies the selected coupon after membership: `SAVE50` subtracts 50, `HALF` halves the subtotal, and `NEWYEAR` applies 20% off only in January.
7. Floors a negative subtotal at zero, adds 7% tax, rounds to two decimal places, appends `(member, final_amount)` to the global `LOG`, and returns the final amount.

## Readability and maintainability smells

| Location | Code smell | Why it makes changes risky |
|---|---|---|
| `calc`, lines 12–29 | One function mixes line-item pricing, tiers, membership, coupon, tax, rounding, and state updates | A change to one pricing policy can accidentally alter the order or behavior of another policy. |
| `calc`, line 16 | Tuple elements are accessed as `i[1]` and `i[2]` | The meaning of each position is implicit, so a reordered tuple can silently calculate the wrong amount. |
| `calc`, lines 20–24 | The running values `t` and `sub` are abbreviated | Readers must repeatedly infer whether each value is a line subtotal, discounted subtotal, or final total. |
| `calc`, lines 21–24 | Quantity thresholds and discount rates are embedded as numeric literals | Policy changes have no named values and the tier boundaries are easy to miss. |
| `calc`, lines 26–29 | Membership discount and points calculation are interleaved | Points are based on the discounted subtotal before coupons and tax; that sequencing is not explicit in the structure. |
| `calc`, lines 31–40 | Coupon behavior is a nested conditional and `today` is mutated to obtain a default | Eligibility and price calculation are coupled, making date-dependent behavior difficult to test and follow. |
| module lines 8–9 and `calc`, line 46 | Member points and the log are mutable module globals | Calls affect later calls and tests unless state is deliberately isolated. |
| `calc`, lines 43–45 | Tax, rounding, append-to-log, and return are compressed at the end | The final amount's composition and the side effect are easy to overlook during review. |
