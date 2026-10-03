"""Hard QA gates. Qualitative meal review remains an AI responsibility."""

from __future__ import annotations

from .reconcile import validate_ledger


def run_qa(*, ledger: list[dict], budget: dict, days: list[dict], meals: dict) -> dict:
    errors = validate_ledger(ledger)
    warnings = []

    if len(days) != 7:
        errors.append(f"Plan must contain exactly 7 days; found {len(days)}")

    if not budget.get("complete"):
        errors.append("Budget forecast is incomplete because one or more purchases are unpriced")

    if budget.get("variance", 0) > 0:
        warnings.append(f"Forecast is £{budget['variance']:.2f} over target")

    for day in days:
        for meal_id in day.get("mealIds", []):
            if meal_id not in meals:
                errors.append(f"{day.get('date', 'unknown date')}: missing meal {meal_id}")

    for meal_id, meal in meals.items():
        if meal.get("mealMode") == "planned_leftover":
            source = meal.get("sourceMealId")
            if not source or source not in meals:
                errors.append(f"{meal_id}: planned leftover has no valid source meal")
            if meal.get("ingredients"):
                errors.append(f"{meal_id}: planned leftover must not contain separately counted ingredients")

    return {"publishable": not errors, "errors": errors, "warnings": warnings}
