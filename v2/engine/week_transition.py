"""Deterministic transition from one reconciled week to the next."""

from __future__ import annotations


def carry_forward_inventory(ledger: list[dict]) -> dict[tuple[str, str], float]:
    """Carry only explicit reconciled remainders into the next week.

    This deliberately does not infer stock from old plans or shopping lists.
    """
    stock: dict[tuple[str, str], float] = {}
    for row in ledger:
        if not row.get("balanced"):
            raise ValueError(f"Cannot carry unbalanced ledger row: {row.get('ingredientId')}")
        remainder = float(row.get("intentionalRemainder", 0) or 0)
        if remainder < 0:
            raise ValueError(f"Negative remainder for {row.get('ingredientId')}")
        if remainder > 0:
            stock[(row["ingredientId"], row["unit"])] = remainder
    return stock


def apply_confirmed_adjustments(stock: dict[tuple[str, str], float], adjustments: list[dict]) -> dict[tuple[str, str], float]:
    """Apply only explicitly confirmed stock corrections for the new week."""
    result = dict(stock)
    for item in adjustments:
        key = (item["ingredientId"], item["unit"])
        quantity = float(item["quantity"])
        if quantity < 0:
            raise ValueError(f"Confirmed stock cannot be negative: {item['ingredientId']}")
        result[key] = quantity
    return result


def transition_week(*, current_week: dict, reconciled_ledger: list[dict], next_start_date: str,
                    confirmed_stock_adjustments: list[dict] | None = None) -> dict:
    """Return atomic state changes needed to open a new draft week."""
    if current_week.get("status") != "current":
        raise ValueError("Week transition requires exactly one current source week")
    carried = carry_forward_inventory(reconciled_ledger)
    opening_stock = apply_confirmed_adjustments(carried, confirmed_stock_adjustments or [])
    return {
        "archiveWeekId": current_week["id"],
        "archiveStatus": "archived",
        "newWeek": {"startDate": next_start_date, "status": "draft"},
        "openingStock": opening_stock,
        "resetShoppingState": True,
    }
