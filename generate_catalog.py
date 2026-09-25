"""Build the static OMAD catalogue from low-cost meal patterns and generic food estimates."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "recipes-v3.json"
LEGACY_DATA_PATH = ROOT / "recipes.json"

# Per 100 g: kcal, protein, fat, saturates, carbs, sugars, fibre, salt,
# calcium mg, iron mg, potassium mg, magnesium mg, vitamin C mg, vitamin D ug,
# vitamin B12 ug, folate ug, zinc mg, estimated cost in GBP.
FIELDS = ("caloriesKcal", "proteinG", "fatG", "saturatesG", "carbohydrateG",
          "sugarsG", "fibreG", "saltG", "calciumMg", "ironMg", "potassiumMg",
          "magnesiumMg", "vitaminCMg", "vitaminDUg", "vitaminB12Ug",
          "folateUg", "zincMg", "costGBP")
FOODS = {
    # staple, cooked, tinned and frozen foods; figures are broad generic estimates
    "oats":                 (389,16.9,6.9,1.2,66.3,1.0,10.6,.02,54,4.7,429,177,0,0,0,56,4.0,.12),
    "rice":                 (360,7.1,.7,.2,79.9,.1,1.3,.02,28,.8,115,25,0,0,0,8,1.1,.12),
    "pasta":                (371,13,1.5,.3,74.7,2.7,3.2,.02,21,1.3,223,53,0,0,0,18,1.4,.15),
    "potatoes":             (77,2,.1,.03,17.5,.8,2.2,.01,12,.8,425,23,19,0,0,15,.3,.10),
    "sweet potatoes":       (86,1.6,.1,.02,20.1,4.2,3,.05,30,.6,337,25,2.4,0,0,11,.3,.16),
    "wholemeal bread":      (247,13,4.2,.8,41.3,5,7,.95,107,2.5,230,82,0,0,0,29,2.1,.16),
    "wholemeal flour":      (340,13.2,2.5,.4,60.5,.5,10.7,.02,34,3.6,363,138,0,0,0,44,2.7,.12),
    "passata":              (29,1.4,.2,.04,5.3,3.8,1.5,.2,14,.5,237,18,9,0,0,13,.3,.16),
    "tinned tomatoes":      (24,1.2,.2,.04,5.1,3.5,1.5,.1,14,.5,292,18,12,0,0,13,.3,.14),
    "onion":                (40,1.1,.1,.03,9.3,4.2,1.7,.01,23,.2,146,10,7,0,0,19,.2,.12),
    "carrot":               (41,.9,.2,.04,9.6,4.7,2.8,.1,33,.3,320,12,5.9,0,0,19,.2,.12),
    "frozen spinach":       (25,2.9,.3,.1,3.8,.4,2.4,.15,99,2.7,558,79,6,0,0,146,.5,.22),
    "frozen peas":          (81,5.4,.4,.1,14.5,5.7,5.7,.1,25,1.5,244,33,40,0,0,65,1.2,.18),
    "broccoli":             (34,2.8,.4,.1,6.6,1.7,2.6,.1,47,.7,316,21,89,0,0,63,.4,.20),
    "cabbage":              (25,1.3,.1,.03,5.8,3.2,2.5,.1,40,.5,170,12,36,0,0,43,.2,.12),
    "courgette":            (17,1.2,.3,.05,3.1,2.5,1,.1,16,.4,261,18,17,0,0,24,.3,.18),
    "leek":                 (61,1.5,.3,.08,14.2,3.9,1.8,.02,59,2.1,180,28,12,0,0,64,.1,.16),
    "red lentils":          (116,9,.4,.1,20.1,1.8,7.9,.02,19,3.3,369,36,1.5,0,0,181,1.3,.24),
    "chickpeas":            (139,7.1,2.8,.3,22.5,4.8,6.4,.4,45,2.2,240,40,1.3,0,0,172,1.5,.25),
    "kidney beans":         (127,8.7,.5,.1,22.8,.3,6.4,.4,28,2.9,405,45,0,0,0,130,2.8,.24),
    "black-eyed peas":      (116,7.7,.5,.1,20.8,.5,6.5,.4,24,2.5,278,53,0,0,0,208,2.5,.28),
    "mung beans":           (105,7,.4,.1,19.2,2,7.6,.02,27,1.4,266,48,4.8,0,0,159,.8,.24),
    "split peas":           (118,8.3,.4,.1,21.1,2.9,8.3,.02,14,1.3,362,36,1.8,0,0,63,1.1,.20),
    "white beans":          (140,9.7,.4,.1,25.1,.3,6.3,.4,90,3.7,561,63,0,0,0,81,1.9,.25),
    "baked beans":          (78,4.9,.5,.1,12.8,4.7,4.8,.6,39,1.4,278,31,0,0,0,50,.7,.24),
    "tuna":                 (116,25.5,.8,.2,0,0,0,.9,11,1.3,237,30,0,1.7,10.9,2,.8,.72),
    "sardines":             (208,24.6,11.4,1.5,0,0,0,1.1,382,2.9,397,39,0,4.8,8.9,10,1.3,.55),
    "salmon":               (167,23,7.5,1.6,0,0,0,.8,250,.5,363,27,0,13,4.5,4,.6,.90),
    "mackerel":             (262,24,17.8,4.2,0,0,0,1,12,1.6,314,76,0,16,19,2,1,.62),
    "corned beef":          (250,26,16,6.5,0,0,0,2.6,6,2,200,20,0,0,1.3,0,3.6,.72),
    "chicken thigh":        (209,26,10.9,3.2,0,0,0,.2,15,1,259,25,0,.1,.3,7,2.5,.78),
    "cottage cheese":       (82,11,2.3,1.5,3.4,2.7,0,.8,103,.1,104,8,0,.1,.4,12,.5,.34),
    "egg":                  (155,12.6,10.6,3.3,1.1,1.1,0,.35,50,1.2,126,10,0,2,1.1,47,1.3,.28),
    "milk":                 (50,3.5,1.8,1.2,4.8,4.8,0,.1,124,0,150,11,.8,.05,.4,5,.4,.07),
    "plain yogurt":         (63,5.3,3.3,2.1,5,4.7,0,.1,183,0,234,17,.5,0,.8,7,.6,.26),
    "cheddar":              (403,25,33,21,1.3,.5,0,1.8,721,.7,98,28,0,.6,.8,27,3.1,.70),
    "rapeseed oil":         (884,0,100,7.5,0,0,0,0,0,0,0,0,0,0,0,0,0,.12),
    "peanut butter":        (588,25,50,10,20,9.2,6,.5,43,1.9,649,154,0,0,0,92,2.5,.35),
    "pumpkin seeds":        (559,30,49,8.7,10.7,1.4,6,.02,46,8.8,809,592,1.9,0,0,58,7.8,.38),
    "apple":                (52,.3,.2,.03,13.8,10.4,2.4,0,6,.1,107,5,4.6,0,0,3,.04,.18),
    "banana":               (89,1.1,.3,.1,22.8,12.2,2.6,0,5,.3,358,27,8.7,0,0,20,.15,.16),
    "pear":                 (57,.4,.1,.02,15.2,9.8,3.1,0,9,.2,116,7,4.3,0,0,7,.1,.20),
    "raisins":              (299,3.1,.5,.1,79.2,59.2,3.7,.05,50,1.9,749,32,2.3,0,0,5,.2,.26),
    "frozen berries":       (50,1,.3,.05,12,8,4,.02,20,.5,150,15,30,0,0,25,.2,.34),
    "curry powder":         (325,14,14,2,56,3,33,.2,150,19,1170,254,11,0,0,56,4,.25),
    "paprika":              (282,14,13,2,54,10,35,.2,229,21,2280,178,0,0,0,49,4,.28),
    "mixed herbs":          (270,10,6,1,40,5,28,.1,300,10,900,120,10,0,0,60,2,.20),
    "chilli powder":        (282,13,14,2,50,8,35,.2,330,17,1900,180,0,0,0,25,4,.24),
    "garlic powder":        (331,17,1,0,73,2,9,.1,79,5.7,1193,77,1.2,0,0,47,2.2,.30),
}

DAILY_REFERENCE_INTAKES = {
    "energyKcal": 2000, "proteinG": 50, "fatG": 70, "saturatesG": 20,
    "carbohydrateG": 260, "sugarsG": 90, "saltG": 6,
    "calciumMg": 800, "ironMg": 14, "potassiumMg": 2000,
    "magnesiumMg": 375, "vitaminCMg": 80, "vitaminDUg": 5,
    "vitaminB12Ug": 2.5, "folateUg": 200, "zincMg": 10,
}
DAILY_TARGETS = {"proteinG": 80, "fibreG": 30}

VEGETABLES = [
    ("frozen peas", 100), ("frozen spinach", 80), ("carrot", 100),
    ("cabbage", 100), ("broccoli", 100),
]
SEASONAL = {
    "carrot": (["UK carrots"], ["autumn", "winter"]),
    "cabbage": (["UK cabbage"], ["autumn", "winter"]),
    "broccoli": (["UK broccoli"], ["autumn", "winter"]),
    "apple": (["UK apples"], ["autumn", "winter"]),
    "pear": (["UK pears"], ["autumn"]),
    "frozen berries": ([], []),
    "frozen peas": ([], []), "frozen spinach": ([], []),
}
TITLE = {
    "red lentils":"Red lentil", "chickpeas":"Chickpea", "kidney beans":"Kidney bean",
    "black-eyed peas":"Black-eyed pea", "mung beans":"Mung bean", "split peas":"Split pea",
    "white beans":"White bean", "baked beans":"Baked bean", "tuna":"Tuna",
    "sardines":"Sardine", "salmon":"Salmon", "mackerel":"Mackerel",
    "corned beef":"Corned beef", "chicken thigh":"Chicken", "cottage cheese":"Cottage cheese",
    "egg":"Egg", "apple":"Apple", "banana":"Banana", "pear":"Pear", "raisins":"Raisin",
    "frozen berries":"Berry", "frozen peas":"Pea", "frozen spinach":"Spinach",
    "carrot":"Carrot", "cabbage":"Cabbage", "broccoli":"Broccoli",
    "pumpkin seeds":"Pumpkin seed", "peanut butter":"Peanut butter",
    "plain yogurt":"Yogurt",
}
SPICES = ("curry powder", "paprika", "mixed herbs", "chilli powder", "garlic powder")

def slug(value):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")

def ingredient(food, grams, display=None):
    return {"food": food, "grams": grams, "amount": display or f"{grams} g", "name": food}

def nutrition(ingredients):
    totals = {key: 0.0 for key in FIELDS if key != "costGBP"}
    cost = 0.0
    for item in ingredients:
        if item["food"] not in FOODS:
            continue
        profile = FOODS[item["food"]]
        factor = item["grams"] / 100.0
        for key, value in zip(FIELDS, profile):
            if key == "costGBP":
                cost += value * factor
            else:
                totals[key] += value * factor
    # Keep calories to the nearest 5 kcal, macros to whole grams and micros sensibly rounded.
    result = {
        "caloriesKcal": int(round(totals["caloriesKcal"] / 5) * 5),
        "proteinG": round(totals["proteinG"]),
        "fatG": round(totals["fatG"]),
        "saturatesG": round(totals["saturatesG"], 1),
        "carbohydrateG": round(totals["carbohydrateG"]),
        "sugarsG": round(totals["sugarsG"]),
        "fibreG": round(totals["fibreG"]),
        "saltG": round(totals["saltG"], 1),
        "micronutrients": {
            "calciumMg": round(totals["calciumMg"]),
            "ironMg": round(totals["ironMg"], 1),
            "potassiumMg": round(totals["potassiumMg"]),
            "magnesiumMg": round(totals["magnesiumMg"]),
            "vitaminCMg": round(totals["vitaminCMg"], 1),
            "vitaminDUg": round(totals["vitaminDUg"], 1),
            "vitaminB12Ug": round(totals["vitaminB12Ug"], 1),
            "folateUg": round(totals["folateUg"]),
            "zincMg": round(totals["zincMg"], 1),
        },
    }
    return result, round(cost, 2)

def make_recipe(name, description, categories, dietary, ingredients, method,
                special=False, tags=None):
    n, cost = nutrition(ingredients)
    produce, seasons = [], []
    for item in ingredients:
        p, s = SEASONAL.get(item["food"], ([], []))
        for label in p:
            if label not in produce:
                produce.append(label)
        for season in s:
            if season not in seasons:
                seasons.append(season)
    if not seasons:
        seasons = ["all-year"]
    safe_ingredients = [{"amount": i["amount"], "name": i["name"]} for i in ingredients]
    foods = [i["food"] for i in ingredients]
    protein, carbs, fibre, kcal = n.get("proteinG",0), n.get("carbohydrateG",0), n.get("fibreG",0), n.get("caloriesKcal",0)
    wartime_staples = {"potatoes","oats","carrot","cabbage","onion","split peas","red lentils","wholemeal flour","wholemeal bread"}
    wartime_luxuries = {"salmon","cheddar","pumpkin seeds","frozen berries","peanut butter"}
    wartime_score = sum(x in wartime_staples for x in foods) - sum(x in wartime_luxuries for x in foods)
    eras = ["modern"] + (["ww2-wartime-inspired"] if wartime_score >= 2 else [])
    if any(x in foods for x in ("corned beef","potatoes","cabbage","baked beans")): eras += ["1950s","1970s"]
    eras = list(dict.fromkeys(eras))
    goals = ["everyday"]
    if protein >= 35 and carbs >= 45 and kcal >= 550: goals.append("athlete")
    if protein >= 45 and fibre >= 10: goals.append("bodybuilder")
    spice_level = "hot" if "chilli powder" in foods else ("medium" if any(x in foods for x in ("curry powder","paprika")) else "mild")
    family = {"adultMultiplier":1.0,"childMultiplier":0.65,"toddlerMultiplier":0.35,
              "note":"Portion scaling only; child/toddler servings are family-meal portions, not an OMAD or fasting recommendation."}
    fancy_extras = ["fresh herbs"]
    if "pasta" in foods: fancy_extras += ["hard cheese", "mushrooms"]
    elif any(x in foods for x in ("potatoes","cabbage","carrot")): fancy_extras += ["wholegrain mustard", "fresh parsley"]
    elif "oats" in foods: fancy_extras += ["berries", "toasted seeds"]
    return {
        "id": slug(name), "name": name, "description": description,
        "categories": categories, "special": special, "dietary": dietary,
        "seasons": seasons, "seasonalProduce": produce,
        "eras": eras, "goals": goals, "spiceLevel": spice_level,
        "familyPortions": family, "fancyExtras": fancy_extras,
        "settings": ["indoor","outdoor"], "wartimeInspired": "ww2-wartime-inspired" in eras,
        "tags": list(dict.fromkeys(["budget"] + (tags or []) +
                                   [i["food"] for i in ingredients])),
        "costGBP": cost, "nutritionPerServing": n,
        "ingredients": safe_ingredients, "method": method,
        "estimateNote": "Modelled per-serving estimate from generic ingredient values and rough low-cost prices. Check your own labels, drained weights, oil, and portions; the percentages are guidance, not a complete diet assessment."
    }

def diet_for(foods):
    animal = {"tuna", "sardines", "salmon", "mackerel", "corned beef", "chicken thigh"}
    fish = {"tuna", "sardines", "salmon", "mackerel"}
    vegetarian = {"egg", "cottage cheese", "milk", "plain yogurt", "cheddar"}
    if any(f in animal for f in foods):
        return ["pescatarian"] if all(f in fish for f in foods if f in animal) else ["omnivore"]
    if any(f in vegetarian for f in foods):
        return ["vegetarian"]
    return ["vegan", "vegetarian"]

def gram_ingredients(base, protein, veg, spice, extras=()):
    items = [ingredient(food, grams, display) for food, grams, display in base]
    items += [ingredient(protein[0], protein[1], protein[2])]
    items += [ingredient(veg[0], veg[1])]
    if spice:
        items += [ingredient(spice, 2)]
    items += [ingredient(food, grams, display) for food, grams, display in extras]
    return items

def variants(family, proteins, vegetables, build, categories, description_fn, method):
    recipes = []
    for protein in proteins:
        for veg in vegetables:
            spice = SPICES[(len(recipes) + len(family)) % len(SPICES)]
            name, description, ingredients = build(protein, veg, spice)
            foods = [i["food"] for i in ingredients]
            recipes.append(make_recipe(
                name, description_fn(description), categories, diet_for(foods),
                ingredients, method, special=(len(recipes) % 9 == 0),
                tags=[family, spice]
            ))
    return recipes

def generate():
    old = json.loads(LEGACY_DATA_PATH.read_text())
    recipes = []
    # Keep the original five favourites and extend them with fuller rough nutrient estimates.
    legacy_micro = {
        "salmon-tuna-pasta": (180,4.5,1150,160,25,7,10,230,3.5),
        "chickpea-spinach-fritters": (140,5.5,1080,180,8,0,0,230,3.5),
        "mung-bean-cottage-cheese-bake": (310,8,1800,220,20,.5,1.3,430,5),
        "corned-beef-hash": (90,5,1800,110,20,0,4,65,7),
        "apple-oat-bakes": (130,5,750,180,10,1.5,.6,90,3.5),
    }
    legacy_macros = {
        "salmon-tuna-pasta": (18,4,91,12,2.1),
        "chickpea-spinach-fritters": (12,2,68,7,.7),
        "mung-bean-cottage-cheese-bake": (15,7,66,10,1.8),
        "corned-beef-hash": (26,10,79,8,4.2),
        "apple-oat-bakes": (15,3,80,28,.8),
    }
    for r in old["recipes"]:
        if r["id"] not in legacy_macros:
            continue
        n = r["nutritionPerServing"]
        fat, sat, carbs, sugars, salt = legacy_macros[r["id"]]
        n.update({"fatG": fat, "saturatesG": sat, "carbohydrateG": carbs,
                  "sugarsG": sugars, "saltG": salt})
        ca, iron, potassium, magnesium, vc, vd, b12, folate, zinc = legacy_micro[r["id"]]
        n["micronutrients"] = {
            "calciumMg": ca, "ironMg": iron, "potassiumMg": potassium,
            "magnesiumMg": magnesium, "vitaminCMg": vc, "vitaminDUg": vd,
            "vitaminB12Ug": b12, "folateUg": folate, "zincMg": zinc
        }
        r["estimateNote"] = "Legacy estimate, expanded with rough micronutrient estimates. Brand, drained weights, cooking and portion sizes can change the result."
        recipes.append(r)

    vegs = [(name, grams) for name, grams in VEGETABLES]
    def protein_choices(keys, grams=140):
        return [(key, grams, f"{grams} g") for key in keys]

    # 1. Rice pots: four pulses x five vegetables.
    recipes += variants(
        "tomato-rice-pot", protein_choices(["red lentils","chickpeas","kidney beans","black-eyed peas"]),
        vegs,
        lambda p,v,s: (
            f'{TITLE[p[0]]} and {TITLE[v[0]]} tomato rice pot',
            "", [ingredient("rice",85,"85 g dry"), ingredient("passata",140),
                 ingredient("onion",50), ingredient("rapeseed oil",5,"1 tsp"),
                 ingredient(p[0],p[1]), ingredient(v[0],v[1]), ingredient(s,2)]
        ),
        ["lunch","dinner"], lambda _: "One-pan rice with a tomato base, a pulse and vegetables.",
        ["Cook rice, using a little extra water for the one-pan style. Soften onion in oil.",
         "Add passata, the pulse, vegetables and seasoning; simmer until hot and tender.",
         "Fold through the rice and serve."]
    )
    # 2. Tomato pasta bowls.
    recipes += variants(
        "tomato-pasta", protein_choices(["tuna","sardines","red lentils","chickpeas"]),
        vegs,
        lambda p,v,s: (
            f'{TITLE[p[0]]} and {TITLE[v[0]]} tomato pasta',
            "", [ingredient("pasta",90,"90 g dry"), ingredient("passata",130),
                 ingredient("onion",40), ingredient("rapeseed oil",5,"1 tsp"),
                 ingredient(p[0],115), ingredient(v[0],v[1]), ingredient(s,2)]
        ),
        ["lunch","dinner"], lambda _: "A cheap tomato pasta bowl with a practical protein and veg swap.",
        ["Boil pasta until tender, adding frozen vegetables for the final few minutes.",
         "Soften onion in oil; add passata, pulse or fish and seasoning.",
         "Stir through the pasta and vegetables. Heat until piping hot."]
    )
    # 3. Loaded jacket potatoes.
    jacket_proteins = [("baked beans",200,"200 g"),("tuna",100,"100 g drained"),
                       ("cottage cheese",180,"180 g"),("corned beef",90,"90 g")]
    recipes += variants(
        "loaded-jacket", jacket_proteins, vegs,
        lambda p,v,s: (
            f'{TITLE[p[0]]} and {TITLE[v[0]]} jacket potato',
            "", [ingredient("potatoes",350,"350 g"), ingredient("onion",35),
                 ingredient(p[0],p[1],p[2]), ingredient(v[0],v[1]),
                 ingredient("plain yogurt",30), ingredient(s,1)]
        ),
        ["lunch","dinner"], lambda _: "A large jacket potato with a low-cost topping and a vegetable side.",
        ["Bake, microwave or air-fry the potato until soft inside.",
         "Heat the chosen topping with onion and seasoning; keep cottage cheese or yogurt cold.",
         "Split the potato, add the topping and serve with the vegetables."]
    )
    # 4. Mung/pulse and cottage cheese bakes.
    recipes += variants(
        "cottage-cheese-bake", protein_choices(["mung beans","red lentils","chickpeas","black-eyed peas"],150),
        vegs,
        lambda p,v,s: (
            f'{TITLE[p[0]]} and {TITLE[v[0]]} cottage cheese bake',
            "", [ingredient(p[0],p[1]), ingredient("cottage cheese",150),
                 ingredient("passata",110), ingredient("onion",45),
                 ingredient(v[0],v[1]), ingredient(s,2)]
        ),
        ["lunch","dinner"], lambda _: "A no-egg pulse and cottage cheese bake with one full hearty portion.",
        ["Mix the cooked pulse with cottage cheese, passata, onion, vegetables and seasoning.",
         "Spoon into an oven-safe dish and bake at 190°C for 25 to 30 minutes, until hot through."]
    )
    # 5. Vegan fritters.
    recipes += variants(
        "pulse-fritters", protein_choices(["chickpeas","red lentils","white beans","mung beans"],160),
        vegs,
        lambda p,v,s: (
            f'{TITLE[p[0]]} and {TITLE[v[0]]} fritters',
            "", [ingredient(p[0],p[1]), ingredient("wholemeal flour",35),
                 ingredient("onion",45), ingredient(v[0],min(v[1],90)),
                 ingredient("rapeseed oil",6,"about 1 tsp"), ingredient(s,2)]
        ),
        ["lunch","snacks"], lambda _: "Crisp-edged, egg-free fritters made from pulses, flour and vegetables.",
        ["Mash the pulse roughly, then mix with flour, onion, vegetables and seasoning.",
         "Shape into patties, adding a splash of water if needed.",
         "Pan-fry with the measured oil until browned and piping hot on both sides."]
    )
    # 6. Hearty soup, with wholemeal bread.
    recipes += variants(
        "soup-and-bread", protein_choices(["red lentils","split peas","chickpeas","black-eyed peas"],150),
        vegs,
        lambda p,v,s: (
            f'{TITLE[p[0]]} and {TITLE[v[0]]} soup with bread',
            "", [ingredient(p[0],p[1]), ingredient("potatoes",100),
                 ingredient("carrot",50), ingredient("onion",45),
                 ingredient(v[0],v[1]), ingredient("rapeseed oil",4,"1 tsp"),
                 ingredient("wholemeal bread",80), ingredient(s,2)]
        ),
        ["lunch","dinner"], lambda _: "A thick pulse soup with vegetables and wholemeal bread.",
        ["Soften onion and carrot in oil. Add potato, the pulse, seasoning and enough water.",
         "Simmer until soft; add the selected vegetables near the end and mash a little to thicken.",
         "Serve with wholemeal bread."]
    )
    # 7. Potato hash with full eggs or a simple protein alternative.
    hash_proteins = [("egg",100,"2 whole eggs"),("baked beans",150,"150 g"),
                     ("corned beef",90,"90 g"),("chickpeas",130,"130 g")]
    recipes += variants(
        "potato-hash", hash_proteins, vegs,
        lambda p,v,s: (
            f'{TITLE[p[0]]} and {TITLE[v[0]]} potato hash',
            "", [ingredient("potatoes",300), ingredient("onion",45),
                 ingredient(p[0],p[1],p[2]), ingredient(v[0],v[1]),
                 ingredient("rapeseed oil",5,"1 tsp"), ingredient(s,2)]
        ),
        ["breakfast","lunch","dinner"], lambda _: "A simple potato hash with a whole-portion topping and vegetables.",
        ["Boil or microwave the potato cubes until just tender, then drain.",
         "Brown the onion and potatoes in the measured oil; add the vegetable and seasoning.",
         "Stir in beans, chickpeas or corned beef until hot. For the egg version, cook two whole eggs into the hash."]
    )
    # 8. Tinned fish potato bakes.
    recipes += variants(
        "fish-potato-bake", protein_choices(["tuna","salmon","sardines","mackerel"],100),
        vegs,
        lambda p,v,s: (
            f'{TITLE[p[0]]} and {TITLE[v[0]]} potato bake',
            "", [ingredient("potatoes",280), ingredient(p[0],p[1],"100 g drained"),
                 ingredient("milk",80), ingredient("wholemeal flour",8),
                 ingredient("rapeseed oil",3,"a little oil"), ingredient(v[0],v[1]),
                 ingredient(s,1)]
        ),
        ["lunch","dinner"], lambda _: "Tinned fish, potato and vegetables in a quick oven or air-fryer bake.",
        ["Cook the potato until nearly tender. Mix flour with a little milk, then stir in the rest.",
         "Fold in the fish, vegetables and seasoning; transfer to an oven-safe dish.",
         "Bake at 190°C for about 20 minutes, until hot and lightly browned."]
    )
    # 9. Sweet oats: five fruits x four small toppings.
    fruits = [("apple",100),("banana",100),("pear",100),("raisins",25),("frozen berries",100)]
    toppings = [("pumpkin seeds",15,"15 g"),("peanut butter",15,"15 g"),
                ("plain yogurt",100,"100 g"),("cottage cheese",80,"80 g")]
    sweet = []
    for fruit in fruits:
        for topping in toppings:
            name = f'{TITLE[fruit[0]]} and {TITLE[topping[0]]} breakfast oats'
            ingredients = [ingredient("oats",80), ingredient("milk",180),
                           ingredient(fruit[0],fruit[1]), ingredient(topping[0],topping[1],topping[2])]
            sweet.append(make_recipe(
                name, "Warm oats with fruit and a low-cost protein or seed topping.",
                ["breakfast","snacks"], diet_for([i["food"] for i in ingredients]),
                ingredients,
                ["Simmer oats and milk gently, stirring until creamy; add a splash of water if you prefer them thinner.",
                 "Top with the fruit and chosen topping. Cook the fruit into the oats if you prefer it soft."],
                special=(len(sweet)%9==0), tags=["oats","breakfast",topping[0]]
            ))
    recipes += sweet
    # 10. One-tray Ninja/oven meals.
    tray_proteins = [("chicken thigh",150,"150 g cooked chicken"),
                     ("chickpeas",150,"150 g"),("corned beef",80,"80 g"),
                     ("baked beans",160,"160 g")]
    recipes += variants(
        "one-tray-meal", tray_proteins, vegs,
        lambda p,v,s: (
            f'{TITLE[p[0]]} and {TITLE[v[0]]} one-tray potato meal',
            "", [ingredient("potatoes",300), ingredient("onion",40),
                 ingredient(p[0],p[1],p[2]), ingredient(v[0],v[1]),
                 ingredient("rapeseed oil",6,"about 1 tsp"), ingredient(s,2)]
        ),
        ["lunch","dinner"], lambda _: "An easy one-tray meal for the oven or Ninja, using familiar low-cost ingredients.",
        ["Cut potatoes and onion into small pieces. Toss with the measured oil and seasoning.",
         "Roast or air-fry at 190°C, turning once, until nearly tender.",
         "Add the protein and vegetable and cook until piping hot; chicken must be fully cooked."]
    )

    ids = [r["id"] for r in recipes]
    if len(ids) != len(set(ids)):
        raise ValueError("Recipe ids are not unique")
    if len(recipes) < 200:
        raise ValueError(f"Expected a few hundred recipes, got {len(recipes)}")
    output = {
        "schemaVersion": 3,
        "currency": "GBP",
        "dailyTargets": DAILY_TARGETS,
        "dailyReferenceIntakes": DAILY_REFERENCE_INTAKES,
        "nutritionNote": (
            "Recipe nutrients and costs are rough model estimates from generic ingredient values and typical low-cost prices. "
            "Adult RI percentages use UK food-label reference intakes; fibre uses the NHS 30g adult recommendation; "
            "protein also shows Michael's chosen 80g target. The figures are not laboratory measurements or a medical diet plan."
        ),
        "recipes": recipes
    }
    rendered = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    DATA_PATH.write_text(rendered)
    LEGACY_DATA_PATH.write_text(rendered)
    print(f"Wrote {len(recipes)} recipes to {DATA_PATH} and {LEGACY_DATA_PATH}")

if __name__ == "__main__":
    generate()
