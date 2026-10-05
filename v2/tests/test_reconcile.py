from v2.engine.reconcile import Pack, Requirement, reconcile, validate_ledger


def test_stock_plus_purchase_equals_use_plus_remainder():
    requirements = [
        Requirement("chicken-thigh", "Chicken thighs", 900, "g", "wed-dinner"),
        Requirement("chicken-thigh", "Chicken thighs", 450, "g", "thu-lunch"),
    ]
    ledger = reconcile(
        requirements=requirements,
        opening_stock={("chicken-thigh", "g"): 400},
        pack_options={("chicken-thigh", "g"): [Pack(500, 3.50), Pack(1000, 6.50)]},
    )
    row = ledger[0]
    assert row["recipeUse"] == 1350
    assert row["openingStock"] == 400
    assert row["purchaseQuantity"] == 1000
    assert row["intentionalRemainder"] == 50
    assert validate_ledger(ledger) == []


def test_no_purchase_when_stock_covers_requirement():
    ledger = reconcile(
        requirements=[Requirement("rice", "Rice", 300, "g", "mon-dinner")],
        opening_stock={("rice", "g"): 500},
        pack_options={},
    )
    assert ledger[0]["purchaseQuantity"] == 0
    assert ledger[0]["intentionalRemainder"] == 200
    assert validate_ledger(ledger) == []
