"""Full reconstructed Sep 28-Oct 4 week for V2 integration testing.

Recipe quantities below are a V2 reconstruction of the approved historical menu,
not a claim that every quantity was preserved in the old V1 conversation. The
point is to exercise the complete deterministic pipeline with realistic meals.
"""


def alloc(family=True, lunch=False, adults_only=False):
    rows = [
        {"consumerId": "marcus", "portionFactor": 1.0, "purpose": "dinner"},
        {"consumerId": "bron", "portionFactor": 1.0, "purpose": "dinner"},
    ]
    if family and not adults_only:
        rows.append({"consumerId": "barney", "portionFactor": 0.5, "purpose": "dinner"})
    if lunch:
        rows += [
            {"consumerId": "marcus", "portionFactor": 1.0, "purpose": "lunch"},
            {"consumerId": "bron", "portionFactor": 1.0, "purpose": "lunch"},
        ]
    return rows


def ing(i, name, qty, unit="g"):
    return {"ingredientId": i, "name": name, "quantity": qty, "unit": unit}


def meal(i, date, title, ingredients, allocations):
    return {"id": i, "date": date, "title": title, "mealMode": "cook", "allocations": allocations,
            "ingredients": ingredients, "method": ["Prepare and cook all components as one complete meal."]}


MEALS = {
    "mon-dinner": meal("mon-dinner", "2026-09-28", "Lemon garlic feta chicken traybake", [
        ing("chicken-breast", "Chicken breast", 900), ing("potatoes", "Potatoes", 900),
        ing("courgette", "Courgette", 300), ing("tomatoes", "Tomatoes", 300), ing("red-onion", "Red onion", 1, "each"),
        ing("feta", "Feta", 120), ing("lemon", "Lemon", 1, "each"), ing("olive-oil", "Olive oil", 45, "ml")], alloc()),
    "tue-dinner": meal("tue-dinner", "2026-09-29", "Slow-cooker beef and apricot Moroccan tagine", [
        ing("diced-beef", "Diced beef", 1000), ing("onion", "Onion", 2, "each"), ing("carrot", "Carrots", 400),
        ing("apricots", "Dried apricots", 150), ing("chopped-tomatoes", "Chopped tomatoes", 800),
        ing("couscous", "Couscous", 300), ing("olive-oil", "Olive oil", 30, "ml")], alloc()),
    "wed-dinner": meal("wed-dinner", "2026-09-30", "Creamy Tuscan sausage rigatoni", [
        ing("sausages", "Sausages", 750), ing("rigatoni", "Rigatoni", 550), ing("passata", "Passata", 500),
        ing("spinach", "Spinach", 250), ing("parmesan", "Parmesan", 100), ing("onion", "Onion", 1, "each"),
        ing("cream", "Cream", 200, "ml")], alloc(lunch=True)),
    "thu-lunch": {"id": "thu-lunch", "date": "2026-10-01", "title": "Creamy Tuscan sausage rigatoni", "mealMode": "planned_leftover", "sourceMealId": "wed-dinner", "allocations": [{"consumerId": "marcus", "portionFactor": 1.0, "purpose": "lunch"}, {"consumerId": "bron", "portionFactor": 1.0, "purpose": "lunch"}]},
    "thu-dinner": meal("thu-dinner", "2026-10-01", "Teriyaki salmon rice bowls", [
        ing("salmon", "Salmon fillets", 680), ing("rice", "Rice", 400), ing("broccoli", "Broccoli", 300),
        ing("carrot", "Carrots", 250), ing("spring-onion", "Spring onions", 1, "each"), ing("teriyaki", "Teriyaki sauce", 120, "ml")], alloc(family=False, lunch=True, adults_only=True)),
    "fri-lunch": {"id": "fri-lunch", "date": "2026-10-02", "title": "Teriyaki salmon rice bowls", "mealMode": "planned_leftover", "sourceMealId": "thu-dinner", "allocations": [{"consumerId": "marcus", "portionFactor": 1.0, "purpose": "lunch"}, {"consumerId": "bron", "portionFactor": 1.0, "purpose": "lunch"}]},
    "fri-dinner": meal("fri-dinner", "2026-10-02", "Slow-cooker chicken shawarma", [
        ing("chicken-thigh", "Chicken thighs", 1000), ing("flatbread", "Flatbreads", 6, "each"), ing("lettuce", "Lettuce", 1, "each"),
        ing("tomatoes", "Tomatoes", 300), ing("red-onion", "Red onion", 1, "each"), ing("tahini", "Tahini", 100), ing("lemon", "Lemon", 1, "each")], alloc()),
    "sat-dinner": meal("sat-dinner", "2026-10-03", "Beef burgers and wedges", [
        ing("beef-mince", "Beef mince", 500), ing("burger-bun", "Burger buns", 4, "each"), ing("potatoes", "Potatoes", 800),
        ing("lettuce", "Lettuce", 1, "each"), ing("tomatoes", "Tomatoes", 200), ing("cheddar", "Cheddar", 100)], alloc()),
    "sun-dinner": meal("sun-dinner", "2026-10-04", "Roast pork dinner", [
        ing("pork-joint", "Pork joint", 1100), ing("potatoes", "Potatoes", 1000), ing("carrot", "Carrots", 400),
        ing("parsnip", "Parsnips", 400), ing("broccoli", "Broccoli", 300), ing("gravy", "Gravy granules", 50)], alloc()),
}

PLAN = {
    "days": [
        {"date": "2026-09-28", "mealIds": ["mon-dinner"]},
        {"date": "2026-09-29", "mealIds": ["tue-dinner"]},
        {"date": "2026-09-30", "mealIds": ["wed-dinner"]},
        {"date": "2026-10-01", "mealIds": ["thu-lunch", "thu-dinner"]},
        {"date": "2026-10-02", "mealIds": ["fri-lunch", "fri-dinner"]},
        {"date": "2026-10-03", "mealIds": ["sat-dinner"]},
        {"date": "2026-10-04", "mealIds": ["sun-dinner"]},
    ],
    "meals": MEALS,
}

OPENING_STOCK = {
    ("red-onion", "each"): 1, ("feta", "g"): 50, ("lemon", "each"): 2,
    ("couscous", "g"): 300, ("apricots", "g"): 150, ("tahini", "g"): 100,
    ("lettuce", "each"): 0.5, ("broccoli", "g"): 150, ("gravy", "g"): 50,
}

# Representative supermarket packs and estimated prices for deterministic testing.
PACKS = {
    ("chicken-breast", "g"): [(1000, 7.00)], ("potatoes", "g"): [(2500, 2.50)],
    ("courgette", "g"): [(500, 1.25)], ("tomatoes", "g"): [(500, 1.50)], ("red-onion", "each"): [(3, 1.10)],
    ("feta", "g"): [(200, 2.00)], ("lemon", "each"): [(4, 1.20)], ("olive-oil", "ml"): [(500, 4.00)],
    ("diced-beef", "g"): [(500, 5.00)], ("onion", "each"): [(3, 1.00)], ("carrot", "g"): [(1000, 0.70)],
    ("apricots", "g"): [(250, 2.00)], ("chopped-tomatoes", "g"): [(400, 0.50)], ("couscous", "g"): [(500, 1.00)],
    ("sausages", "g"): [(400, 2.75)], ("rigatoni", "g"): [(500, 0.85)], ("passata", "g"): [(500, 0.65)],
    ("spinach", "g"): [(250, 1.50)], ("parmesan", "g"): [(200, 2.50)], ("cream", "ml"): [(300, 1.25)],
    ("salmon", "g"): [(480, 5.50)], ("rice", "g"): [(1000, 1.60)], ("broccoli", "g"): [(350, 0.90)],
    ("spring-onion", "each"): [(1, 0.65)], ("teriyaki", "ml"): [(150, 1.50)], ("chicken-thigh", "g"): [(1000, 4.50)],
    ("flatbread", "each"): [(6, 1.50)], ("lettuce", "each"): [(1, 0.80)], ("tahini", "g"): [(300, 2.50)],
    ("beef-mince", "g"): [(500, 4.00)], ("burger-bun", "each"): [(4, 1.25)], ("cheddar", "g"): [(400, 2.50)],
    ("pork-joint", "g"): [(1200, 6.50)], ("parsnip", "g"): [(500, 0.90)], ("gravy", "g"): [(200, 1.50)],
}
