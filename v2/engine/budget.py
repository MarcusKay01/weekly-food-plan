"""Budget calculations derived from the reconciled ingredient ledger."""

from __future__ import annotations


def shopping_from_ledger(ledger: list[dict]) -> list[dict]:
    shopping = []
    for row in ledger:
        if row.get("purchaseQuantity", 0) <= 0:
            continue
        selections = (row.get("pack") or {}).get("selections", [])
        cost = sum(x["cost"] for x in selections if x.get("cost") is not None)
        cost_known = selections and all(x.get("cost") is not None for x in selections)
        shopping.append({
            "ingredientId": row["ingredientId"],
            "name": row["name"],
            "purchaseQuantity": row["purchaseQuantity"],
            "unit": row["unit"],
            "estimatedCost": round(cost, 2) if cost_known else None,
            "reason": [u["mealId"] for u in row.get("uses", [])],
        })
    return shopping


def budget_summary(shopping: list[dict], target: float) -> dict:
    unknown = [x["ingredientId"] for x in shopping if x.get("estimatedCost") is None]
    forecast = round(sum(x["estimatedCost"] or 0 for x in shopping), 2)
    return {
        "currency": "GBP",
        "target": target,
        "forecast": forecast,
        "variance": round(forecast - target, 2),
        "complete": not unknown,
        "unpricedIngredientIds": unknown,
    }
