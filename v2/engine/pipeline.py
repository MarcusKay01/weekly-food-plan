"""End-to-end deterministic pipeline for Weekly Food Planner V2."""

from __future__ import annotations

from .budget import budget_summary, shopping_from_ledger
from .intake import validate_plan_meals
from .qa import run_qa
from .reconcile import Pack, Requirement, reconcile


def _requirements_from_meals(meals: list[dict]) -> list[Requirement]:
    requirements: list[Requirement] = []
    for meal in meals:
        if meal.get("mealMode") == "planned_leftover":
            continue
        for ingredient in meal.get("ingredients", []):
            requirements.append(Requirement(
                ingredient_id=ingredient["ingredientId"],
                name=ingredient["name"],
                quantity=ingredient["quantity"],
                unit=ingredient["unit"],
                meal_id=meal["id"],
            ))
    return requirements


def run_pipeline(*, plan: dict, opening_stock: dict[tuple[str, str], float], pack_options: dict[tuple[str, str], list[Pack]], budget_target: float) -> dict:
    """Return a reconciled result or a precise non-publishable failure report.

    The AI/planner must supply complete, already-scaled cooked meals. This function
    never invents a missing quantity and never counts planned-leftover ingredients.
    """
    meal_list = list(plan.get("meals", {}).values())
    intake_errors = validate_plan_meals(meal_list)
    if intake_errors:
        return {
            "status": "FAILED",
            "stage": "intake",
            "publishable": False,
            "errors": intake_errors,
            "warnings": [],
        }

    try:
        ledger = reconcile(
            requirements=_requirements_from_meals(meal_list),
            opening_stock=opening_stock,
            pack_options=pack_options,
        )
    except ValueError as exc:
        return {
            "status": "FAILED",
            "stage": "reconciliation",
            "publishable": False,
            "errors": [str(exc)],
            "warnings": [],
        }

    shopping = shopping_from_ledger(ledger)
    budget = budget_summary(shopping, budget_target)
    qa = run_qa(
        ledger=ledger,
        budget=budget,
        days=plan.get("days", []),
        meals=plan.get("meals", {}),
    )
    return {
        "status": "PUBLISHABLE" if qa["publishable"] else "FAILED",
        "stage": "complete" if qa["publishable"] else "qa",
        "publishable": qa["publishable"],
        "ingredientLedger": ledger,
        "shoppingList": shopping,
        "budget": budget,
        "errors": qa["errors"],
        "warnings": qa["warnings"],
    }
