"""Portion allocation and recipe scaling for Weekly Food Planner V2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortionProfile:
    id: str
    adult_equivalent: float


@dataclass(frozen=True)
class Eater:
    person_id: str
    profile: PortionProfile


def total_adult_equivalents(eaters: list[Eater], extra_adult_portions: float = 0) -> float:
    if extra_adult_portions < 0:
        raise ValueError("extra_adult_portions cannot be negative")
    return sum(e.profile.adult_equivalent for e in eaters) + extra_adult_portions


def scale_recipe(base_ingredients: list[dict], *, base_adult_equivalents: float, target_adult_equivalents: float) -> list[dict]:
    """Scale every quantified recipe ingredient by the same portion factor."""
    if base_adult_equivalents <= 0:
        raise ValueError("base_adult_equivalents must be positive")
    if target_adult_equivalents <= 0:
        raise ValueError("target_adult_equivalents must be positive")
    factor = target_adult_equivalents / base_adult_equivalents
    scaled = []
    for ingredient in base_ingredients:
        if "quantity" not in ingredient or ingredient["quantity"] is None:
            raise ValueError(f"Ingredient {ingredient.get('name', '<unknown>')} has no numeric quantity")
        scaled.append({**ingredient, "quantity": ingredient["quantity"] * factor})
    return scaled


def build_allocation(*, dinner_eaters: list[Eater], lunch_adult_portions: float = 0) -> dict:
    """Return the explicit allocation used to scale a cooked source meal.

    Planned leftover lunches are represented here, on the source meal, so their
    ingredients are never counted a second time by reconciliation.
    """
    dinner_ae = total_adult_equivalents(dinner_eaters)
    total_ae = dinner_ae + lunch_adult_portions
    return {
        "dinner": [{"personId": e.person_id, "adultEquivalent": e.profile.adult_equivalent} for e in dinner_eaters],
        "plannedLunchAdultPortions": lunch_adult_portions,
        "dinnerAdultEquivalents": dinner_ae,
        "totalAdultEquivalents": total_ae,
    }
