# Ethics for the Inventory System

## Responsibility

The store is responsible for its pricing rules and the team is responsible for implementing and verifying them, even when AI drafted code. Tests for discount order, rounding, tax, stock boundaries, and member points reduce the chance of incorrect charges; CI prevents a change from merging when lint, tests, or the coverage threshold fail. A passing suite is evidence, not a transfer of accountability.

## Copyright and licenses

Before committing generated or copied code, review its origin, dependencies, and applicable licenses. Prefer original implementations based on documented behavior, keep required notices, and ask for review when provenance or license obligations are unclear.

## Personal data and PDPA

Member names and point balances can identify customers. Collect only what the inventory and loyalty features need, explain the purpose, restrict access, protect stored and transmitted data, define retention/deletion procedures, and support applicable data-subject rights. Never include real member records in AI prompts or test fixtures.

## AI recommendation bias

If recommendations are added, define what a fair outcome means for the store, compare exposure and recommendation rates across relevant product and customer groups, inspect missing or skewed sales data, and let staff override recommendations. Review the metrics regularly rather than assuming the model is neutral.

## My responsible-use practice

On this inventory project, I will treat AI as a drafting assistant, not an owner of the result. Before using generated code, I will provide the current interfaces, business rules, and tests; I will inspect the diff and verify that pricing order, rounding, stock updates, and member-point side effects remain intentional. I will first record legacy behavior with characterization tests, then refactor in a separate file and run the same tests. I will add boundary and failure-path tests for zero, invalid quantities, insufficient stock, coupon dates, and persistent state. Every change must pass local Ruff and pytest checks, and the GitHub Actions workflow must pass its coverage threshold before merge. A red check is a useful stop signal: I will read the failing log, reproduce the cause, fix it, and retain truthful evidence rather than hiding or weakening the test. I will never paste real member names, contact details, or transaction records into an AI prompt. I will review licenses and retain required notices before committing generated or copied code. For recommendations, I will compare outcomes across customer groups and keep a human override. The team remains responsible for customer charges and will document decisions and rollback paths.
