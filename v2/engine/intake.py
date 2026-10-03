"""Boundary validation between AI meal creation and deterministic V2 arithmetic."""

from __future__ import annotations

ALLOWED_UNITS = {"g", "ml", "each"}


def validate_meal(meal: dict) -> list[str]:
    errors: list[str] = []
    meal_id = meal.get("id") or "<unknown meal>"
    mode = meal.get("mealMode")

    for field in ("id", "date", "title", "mealMode", "allocations"):
        if not meal.get(field):
            errors.append(f"{meal_id}: missing {field}")

    allocations = meal.get("allocations") or []
    for i, allocation in enumerate(allocations):
        if not allocation.get("consumerId"):
            errors.append(f"{meal_id}: allocation {i + 1} missing consumerId")
        if not isinstance(allocation.get("portionFactor"), (int, float)) or allocation.get("portionFactor", 0) <= 0:
            errors.append(f"{meal_id}: allocation {i + 1} has invalid portionFactor")
        if allocation.get("purpose") not in {"dinner", "lunch", "other"}:
            errors.append(f"{meal_id}: allocation {i + 1} has invalid purpose")

    if mode == "planned_leftover":
        if not meal.get("sourceMealId"):
            errors.append(f"{meal_id}: planned leftover missing sourceMealId")
        if meal.get("ingredients"):
            errors.append(f"{meal_id}: planned leftover must not repeat ingredients")
        return errors

    if mode not in {"cook", "standalone"}:
        errors.append(f"{meal_id}: invalid mealMode")
        return errors

    ingredients = meal.get("ingredients") or []
    if not ingredients:
        errors.append(f"{meal_id}: cooked meal has no structured ingredients")
    for i, ingredient in enumerate(ingredients):
        prefix = f"{meal_id}: ingredient {i + 1}"
        for field in ("ingredientId", "name", "quantity", "unit"):
            if ingredient.get(field) is None or ingredient.get(field) == "":
                errors.append(f"{prefix} missing {field}")
        quantity = ingredient.get("quantity")
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            errors.append(f"{prefix} has invalid quantity")
        if ingredient.get("unit") not in ALLOWED_UNITS:
            errors.append(f"{prefix} must use a normalised unit: g, ml or each")

    method = meal.get("method") or []
    if not method:
        errors.append(f"{meal_id}: cooked meal has no method")
    return errors


def validate_plan_meals(meals: list[dict]) -> list[str]:
    errors: list[str] = []
    by_id = {meal.get("id"): meal for meal in meals if meal.get("id")}
    for meal in meals:
        errors.extend(validate_meal(meal))
        if meal.get("mealMode") == "planned_leftover":
            source_id = meal.get("sourceMealId")
            source = by_id.get(source_id)
            if source is None:
                errors.append(f"{meal.get('id', '<unknown meal>')}: source meal {source_id!r} does not exist")
            elif source.get("mealMode") == "planned_leftover":
                errors.append(f"{meal.get('id')}: source meal cannot itself be a planned leftover")
    return errors
