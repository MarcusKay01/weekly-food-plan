import pytest

from v2.engine.week_transition import carry_forward_inventory, transition_week


def ledger():
    return [
        {"ingredientId": "passata", "unit": "g", "intentionalRemainder": 200, "balanced": True},
        {"ingredientId": "chicken", "unit": "g", "intentionalRemainder": 0, "balanced": True},
        {"ingredientId": "rice", "unit": "g", "intentionalRemainder": 350, "balanced": True},
    ]


def test_only_positive_reconciled_remainders_carry_forward():
    stock = carry_forward_inventory(ledger())
    assert stock == {("passata", "g"): 200, ("rice", "g"): 350}
    assert ("chicken", "g") not in stock


def test_transition_archives_current_week_and_resets_shop():
    result = transition_week(
        current_week={"id": "week-1", "status": "current"},
        reconciled_ledger=ledger(),
        next_start_date="2026-10-05",
    )
    assert result["archiveWeekId"] == "week-1"
    assert result["archiveStatus"] == "archived"
    assert result["newWeek"] == {"startDate": "2026-10-05", "status": "draft"}
    assert result["resetShoppingState"] is True
    assert result["openingStock"][("passata", "g")] == 200


def test_explicit_new_stock_check_overrides_carried_quantity():
    result = transition_week(
        current_week={"id": "week-1", "status": "current"},
        reconciled_ledger=ledger(),
        next_start_date="2026-10-05",
        confirmed_stock_adjustments=[
            {"ingredientId": "rice", "quantity": 100, "unit": "g"},
            {"ingredientId": "feta", "quantity": 80, "unit": "g"},
        ],
    )
    assert result["openingStock"][("rice", "g")] == 100
    assert result["openingStock"][("feta", "g")] == 80


def test_unbalanced_week_can_never_seed_next_week():
    bad = ledger()
    bad[0]["balanced"] = False
    with pytest.raises(ValueError, match="unbalanced"):
        carry_forward_inventory(bad)


def test_historical_plan_does_not_become_stock_by_inference():
    result = transition_week(
        current_week={"id": "week-1", "status": "current", "historicalShopping": {"feta": 200}},
        reconciled_ledger=ledger(),
        next_start_date="2026-10-05",
    )
    assert ("feta", "g") not in result["openingStock"]
