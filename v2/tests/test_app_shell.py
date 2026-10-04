from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "index.html"
CONFIG = ROOT / "app" / "config.js"


def test_v2_app_files_exist():
    assert APP.exists()
    assert CONFIG.exists()


def test_app_uses_publishable_not_service_role_key():
    text = CONFIG.read_text()
    assert "sb_publishable_" in text
    assert "service_role" not in text.lower()


def test_app_has_auth_and_dynamic_week_actions():
    text = APP.read_text()
    assert "signInWithOtp" in text
    assert "set_meal_status" in text
    assert "move_meal" in text
    assert "toggleShop" in text
    assert "localStorage" not in text


def test_v1_is_not_loaded_by_v2_shell():
    text = APP.read_text()
    assert "data/current-week.json" not in text
