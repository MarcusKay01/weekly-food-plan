# Weekly Food Planner V2

V2 separates creative meal planning from deterministic reconciliation.

## Product contract

Input can be natural language or voice. The planner interprets household circumstances, confirmed stock, requests and constraints. The output is a fully reconciled weekly plan for the family app.

## Pipeline

1. Intake: turn natural conversation into a structured planning brief.
2. Creative planning: design enjoyable, varied meals and deliberate lunch portions.
3. Portion scaling: calculate every recipe component for all allocated eaters.
4. Ingredient ledger: reconcile opening stock, recipe demand, purchases and intentional remainders.
5. Pack engine: convert net requirements to realistic purchasable quantities.
6. Budget: price the resulting shop and compare it with the target.
7. QA: deterministic checks plus qualitative food-quality review.
8. Approval: user reviews the proposed week conversationally.
9. Publish: create the app-facing weekly plan and reset week-specific shopping state.

## Authority boundaries

AI owns interpretation, recipe design, flavour, variety, sensible stock incorporation and qualitative review.

Deterministic code owns arithmetic: portions, ingredient totals, stock subtraction, pack quantities, purchase totals, remainders, budget sums and validation.

Persistent application data owns household settings, recipe feedback, inventory/remainders, weekly plans, shopping state and budget history.

## Hard invariants

- Opening stock + purchases = recipe use + intentional remainder for every tracked ingredient.
- Dinner-derived lunch is the identical complete meal and is scaled into the source dinner exactly once.
- Every eater and planned lunch has an explicit allocation.
- Every purchased item has a reason for purchase and a reconciled quantity.
- Perishable stock is considered before new purchases, but meal quality takes precedence over forced use of shelf-stable ingredients.
- A plan cannot be published while deterministic QA has errors.

## Migration

The existing PWA and current-week plan remain untouched on `main` while V2 is developed on this branch. The first milestone is the data contract and reconciliation engine; UI/backend migration follows once the engine can prove a week balances.