from v2.engine.intake import validate_meal, validate_plan_meals


def test_rejects_title_and_protein_only_recipe():
    meal = {
        "id": "wed-dinner",
        "date": "2026-09-30",
        "title": "Tuscan sausage rigatoni",
        "mealMode": "cook",
        "allocations": [
            {"consumerId": "marcus", "portionFactor": 1.0, "purpose": "dinner"},
            {"consumerId": "bron", "portionFactor": 1.0, "purpose": "dinner"},
            {"consumerId": "barney", "portionFactor": 0.5, "purpose": "dinner"},
        ],
        "ingredients": [{"ingredientId": "sausage", "name": "Sausages", "quantity": 750, "unit": "g"}],
    }
    errors = validate_meal(meal)
    assert "wed-dinner: cooked meal has no method" in errors


def test_complete_meal_passes_boundary():
    meal = {
        "id": "wed-dinner",
        "date": "2026-09-30",
        "title": "Tuscan sausage rigatoni",
        "mealMode": "cook",
        "allocations": [
            {"consumerId": "marcus", "portionFactor": 1.0, "purpose": "dinner"},
            {"consumerId": "bron", "portionFactor": 1.0, "purpose": "dinner"},
            {"consumerId": "barney", "portionFactor": 0.5, "purpose": "dinner"},
        ],
        "ingredients": [
            {"ingredientId": "sausage", "name": "Sausages", "quantity": 750, "unit": "g"},
            {"ingredientId": "rigatoni", "name": "Rigatoni", "quantity": 350, "unit": "g"},
        ],
        "method": ["Cook the pasta and prepare the sauce."],
    }
    assert validate_meal(meal) == []


def test_planned_leftover_references_source_without_ingredients():
    dinner = {
        "id": "wed-dinner", "date": "2026-09-30", "title": "Dinner", "mealMode": "cook",
        "allocations": [{"consumerId": "marcus", "portionFactor": 1.0, "purpose": "dinner"}],
        "ingredients": [{"ingredientId": "rice", "name": "Rice", "quantity": 100, "unit": "g"}],
        "method": ["Cook."]
    }
    lunch = {
        "id": "thu-lunch", "date": "2026-10-01", "title": "Dinner", "mealMode": "planned_leftover",
        "sourceMealId": "wed-dinner",
        "allocations": [{"consumerId": "marcus", "portionFactor": 1.0, "purpose": "lunch"}]
    }
    assert validate_plan_meals([dinner, lunch]) == []
