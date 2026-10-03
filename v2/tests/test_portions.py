from v2.engine.portions import Eater, PortionProfile, build_allocation, scale_recipe


ADULT = PortionProfile("adult", 1.0)
CHILD = PortionProfile("young-child", 0.5)


def test_family_dinner_plus_two_adult_lunches_scales_once():
    allocation = build_allocation(
        dinner_eaters=[Eater("marcus", ADULT), Eater("bron", ADULT), Eater("barney", CHILD)],
        lunch_adult_portions=2,
    )
    assert allocation["dinnerAdultEquivalents"] == 2.5
    assert allocation["totalAdultEquivalents"] == 4.5

    ingredients = scale_recipe(
        [{"ingredientId": "chicken", "name": "Chicken", "quantity": 200, "unit": "g"}],
        base_adult_equivalents=1,
        target_adult_equivalents=allocation["totalAdultEquivalents"],
    )
    assert ingredients[0]["quantity"] == 900


def test_thursday_adults_only_plus_two_lunches():
    allocation = build_allocation(
        dinner_eaters=[Eater("marcus", ADULT), Eater("bron", ADULT)],
        lunch_adult_portions=2,
    )
    assert allocation["totalAdultEquivalents"] == 4
