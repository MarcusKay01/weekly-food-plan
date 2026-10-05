from pathlib import Path


SCHEMA = (Path(__file__).parents[1] / "database" / "schema.sql").read_text()


def test_persistent_state_has_core_tables():
    for table in [
        "households", "household_members", "preferences", "ingredients", "inventory",
        "weeks", "meals", "meal_allocations", "meal_ingredients", "shopping_items",
        "inventory_movements", "meal_feedback", "week_events",
    ]:
        assert f"create table {table}" in SCHEMA


def test_only_one_current_week_per_household():
    assert "one_current_week_per_household" in SCHEMA
    assert "where status = 'current'" in SCHEMA


def test_database_supports_shared_shopping_state():
    assert "purchased boolean not null default false" in SCHEMA
    assert "purchased_at timestamptz" in SCHEMA


def test_inventory_has_auditable_movements():
    for movement in ["opening_stock", "purchase", "recipe_use", "adjustment", "waste", "carry_forward"]:
        assert movement in SCHEMA


def test_preferences_support_full_feedback_scale():
    for rating in ["loved", "good", "okay", "needs_adjustment", "do_not_suggest"]:
        assert rating in SCHEMA
