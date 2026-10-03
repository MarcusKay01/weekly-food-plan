"""Deterministic reconciliation primitives for Weekly Food Planner V2."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Iterable


@dataclass(frozen=True)
class Pack:
    quantity: float
    price: float | None = None


@dataclass(frozen=True)
class Requirement:
    ingredient_id: str
    name: str
    quantity: float
    unit: str
    meal_id: str


def aggregate_requirements(requirements: Iterable[Requirement]) -> dict[tuple[str, str], dict]:
    totals: dict[tuple[str, str], dict] = {}
    for req in requirements:
        key = (req.ingredient_id, req.unit)
        row = totals.setdefault(key, {"ingredientId": req.ingredient_id, "name": req.name, "unit": req.unit, "recipeUse": 0.0, "uses": []})
        row["recipeUse"] += req.quantity
        row["uses"].append({"mealId": req.meal_id, "quantity": req.quantity})
    return totals


def choose_purchase(net_required: float, packs: list[Pack]) -> tuple[float, list[dict]]:
    """Choose the smallest single pack size repeated enough times to cover demand.

    This intentionally simple first implementation is deterministic. A later pack
    optimiser can minimise price/remainder across mixed pack sizes without changing
    the reconciliation contract.
    """
    if net_required <= 0:
        return 0.0, []
    if not packs:
        raise ValueError("No purchasable pack supplied for required ingredient")
    candidates = []
    for pack in packs:
        count = ceil(net_required / pack.quantity)
        purchased = count * pack.quantity
        cost = None if pack.price is None else count * pack.price
        candidates.append((purchased, float("inf") if cost is None else cost, pack, count, cost))
    purchased, _, pack, count, cost = min(candidates, key=lambda x: (x[0], x[1]))
    return purchased, [{"packQuantity": pack.quantity, "count": count, "cost": cost}]


def reconcile(*, requirements: Iterable[Requirement], opening_stock: dict[tuple[str, str], float], pack_options: dict[tuple[str, str], list[Pack]]) -> list[dict]:
    totals = aggregate_requirements(requirements)
    keys = set(totals) | set(opening_stock)
    ledger = []
    for key in sorted(keys):
        row = totals.get(key, {"ingredientId": key[0], "name": key[0], "unit": key[1], "recipeUse": 0.0, "uses": []})
        stock = opening_stock.get(key, 0.0)
        net = max(0.0, row["recipeUse"] - stock)
        purchase, packs = choose_purchase(net, pack_options.get(key, [])) if net > 0 else (0.0, [])
        available = stock + purchase
        remainder = available - row["recipeUse"]
        balanced = remainder >= -1e-9 and abs(available - row["recipeUse"] - remainder) < 1e-9
        ledger.append({**row, "openingStock": stock, "purchaseQuantity": purchase, "totalAvailable": available, "intentionalRemainder": remainder, "balanced": balanced, "pack": {"selections": packs} if packs else None})
    return ledger


def validate_ledger(ledger: Iterable[dict]) -> list[str]:
    errors = []
    for row in ledger:
        if not row.get("balanced"):
            errors.append(f"{row['name']}: stock + purchases does not reconcile with use + remainder")
        if row.get("intentionalRemainder", 0) < -1e-9:
            errors.append(f"{row['name']}: ingredient shortage")
    return errors
