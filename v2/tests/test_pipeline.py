from v2.engine.pipeline import run_pipeline
from v2.engine.reconcile import Pack


def seven_days(meal_id="wed-dinner"):
    return [{"date": f"2026-09-{28+i:02d}", "mealIds": [meal_id] if i == 2 else []} for i in range(3)] + [
        {"date": "2026-10-01", "mealIds": ["thu-lunch"]},
        {"date": "2026-10-02", "mealIds": []},
        {"date": "2026-10-03", "mealIds": []},
        {"date": "2026-10-04", "mealIds": []},
    ]


def complete_plan():
    return {
        "days": seven_days(),
        "meals": {
            "wed-dinner": {
                "id": "wed-dinner", "date": "2026-09-30", "title": "Chicken and rice", "mealMode": "cook",
                "allocations": [
                    {"consumerId": "marcus", "portionFactor": 1.0, "purpose": "dinner"},
                    {"consumerId": "bron", "portionFactor": 1.0, "purpose": "dinner"},
                    {"consumerId": "barney", "portionFactor": 0.5, "purpose": "dinner"},
                    {"consumerId": "marcus", "portionFactor": 1.0, "purpose": "lunch"},
                    {"consumerId": "bron", "portionFactor": 1.0, "purpose": "lunch"},
                ],
                "ingredients": [
                    {"ingredientId": "chicken", "name": "Chicken", "quantity": 900, "unit": "g"},
                    {"ingredientId": "rice", "name": "Rice", "quantity": 450, "unit": "g"},
                ],
                "method": ["Cook chicken and rice."],
            },
            "thu-lunch": {
                "id": "thu-lunch", "date": "2026-10-01", "title": "Chicken and rice", "mealMode": "planned_leftover",
                "sourceMealId": "wed-dinner",
                "allocations": [
                    {"consumerId": "marcus", "portionFactor": 1.0, "purpose": "lunch"},
                    {"consumerId": "bron", "portionFactor": 1.0, "purpose": "lunch"},
                ],
            },
        },
    }


def test_complete_plan_is_publishable_and_lunch_is_not_double_counted():
    result = run_pipeline(
        plan=complete_plan(),
        opening_stock={("rice", "g"): 200},
        pack_options={
            ("chicken", "g"): [Pack(1000, 6.50)],
            ("rice", "g"): [Pack(500, 1.50)],
        },
        budget_target=20.0,
    )
    assert result["status"] == "PUBLISHABLE"
    chicken = next(x for x in result["ingredientLedger"] if x["ingredientId"] == "chicken")
    assert chicken["recipeUse"] == 900
    assert result["budget"]["forecast"] == 8.0


def test_incomplete_historical_recipe_fails_at_intake_before_arithmetic():
    plan = complete_plan()
    plan["meals"]["wed-dinner"].pop("method")
    result = run_pipeline(
        plan=plan,
        opening_stock={},
        pack_options={},
        budget_target=20.0,
    )
    assert result["status"] == "FAILED"
    assert result["stage"] == "intake"
    assert any("no method" in error for error in result["errors"])


def test_missing_pack_fails_reconciliation_not_silently_underbuying():
    result = run_pipeline(
        plan=complete_plan(),
        opening_stock={("rice", "g"): 450},
        pack_options={("chicken", "g"): []},
        budget_target=20.0,
    )
    assert result["status"] == "FAILED"
    assert result["stage"] == "reconciliation"
    assert any("No purchasable pack" in error for error in result["errors"])
