import importlib.util
from pathlib import Path

from v2.engine.pipeline import run_pipeline
from v2.engine.reconcile import Pack


fixture_path = Path(__file__).parents[1] / "fixtures" / "real-week-2026-09-28.py"
spec = importlib.util.spec_from_file_location("real_week", fixture_path)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


def pack_options():
    return {key: [Pack(quantity=q, price=p) for q, p in options] for key, options in fixture.PACKS.items()}


def test_real_week_reconciles_and_is_publishable():
    result = run_pipeline(
        plan=fixture.PLAN,
        opening_stock=fixture.OPENING_STOCK,
        pack_options=pack_options(),
        budget_target=110.0,
    )
    assert result["status"] == "PUBLISHABLE", result
    assert result["errors"] == []
    assert len(result["ingredientLedger"]) > 20
    assert result["budget"]["complete"] is True


def test_work_lunches_do_not_duplicate_source_dinner_ingredients():
    result = run_pipeline(
        plan=fixture.PLAN,
        opening_stock=fixture.OPENING_STOCK,
        pack_options=pack_options(),
        budget_target=110.0,
    )
    sausage = next(row for row in result["ingredientLedger"] if row["ingredientId"] == "sausages")
    salmon = next(row for row in result["ingredientLedger"] if row["ingredientId"] == "salmon")
    assert sausage["recipeUse"] == 750
    assert salmon["recipeUse"] == 680
    assert "thu-lunch" not in [u["mealId"] for u in sausage["uses"]]
    assert "fri-lunch" not in [u["mealId"] for u in salmon["uses"]]


def test_opening_stock_reduces_purchases_and_remains_balanced():
    result = run_pipeline(
        plan=fixture.PLAN,
        opening_stock=fixture.OPENING_STOCK,
        pack_options=pack_options(),
        budget_target=110.0,
    )
    couscous = next(row for row in result["ingredientLedger"] if row["ingredientId"] == "couscous")
    apricots = next(row for row in result["ingredientLedger"] if row["ingredientId"] == "apricots")
    assert couscous["purchaseQuantity"] == 0
    assert apricots["purchaseQuantity"] == 0
    assert all(row["balanced"] for row in result["ingredientLedger"])
