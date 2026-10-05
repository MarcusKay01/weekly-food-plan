# V2 persistent state

The database is the private source of truth for household state. GitHub stores only schema, engine and tests; no live household records belong in the public repository.

## State ownership

- `households` / `household_members`: household settings and configurable serving factors.
- `preferences`: durable food preferences, feedback-derived rules and standing planning rules.
- `inventory`: current confirmed stock only. Historical stock is not assumed.
- `weeks`: lifecycle of draft -> confirmed -> current -> archived.
- `meals`, `meal_allocations`, `meal_ingredients`: the structured weekly plan.
- `shopping_items`: one shared shopping state across devices, including household/non-food needs.
- `inventory_movements`: auditable opening stock + purchases - recipe use +/- adjustments = current stock.
- `meal_feedback`: learning history without modifying old confirmed weeks.
- `week_events`: exceptions such as meals out, nights away, work/nursery changes and explicit requests.

## Week transition

Starting a new week is an atomic state transition:

1. Archive the previous `current` week.
2. Carry forward only reconciled/confirmed inventory remainders.
3. Create the new draft week.
4. Apply current household preferences and standing rules.
5. Apply only explicitly confirmed week events and stock adjustments.
6. Generate and reconcile the proposed plan.
7. Confirm only after deterministic QA is publishable.
8. Promote the confirmed week to `current` and initialise its shopping state.

Shopping ticks are database state, not browser-local state, so household devices see the same list.

## Security boundary

The production database must use authentication and row-level access so one household cannot read another household's data. Service credentials must never be committed to GitHub. A hosted PostgreSQL service such as Supabase can implement this schema, but the engine is intentionally database-provider-light.

## Migration

V1 remains live while V2 is developed. The Google Drive -> GitHub JSON publishing chain remains untouched until the V2 database-backed app has passed integration testing. At cutover, historical plans can be imported as archived weeks while current confirmed stock is established explicitly rather than inferred from old plans.
