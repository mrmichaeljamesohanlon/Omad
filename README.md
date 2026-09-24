# OMAD

A JSON-first, mobile-friendly recipe page for low-cost one-meal-a-day ideas.

## Run it

Start a local web server in this folder with `python3 -m http.server 8000`, then open <http://localhost:8000>. The page loads the recipe list from `recipes.json`; opening `index.html` directly may block that fetch.

## Browse and edit

The current catalogue has 205 meals, including the original favourites. Browse Specials, Breakfast, Lunch, Dinner and Snacks; search by recipe or ingredients; filter by vegetarian, vegan, pescatarian or seasonal produce; and sort by estimated cost, protein or fibre.

Each recipe card shows energy, protein, fibre, potassium and iron as daily percentages. Open **Nutrition and daily percentages** for estimated energy, macros, salt, nine vitamins/minerals and their adult reference percentages. Protein also shows the 80g target. Fibre uses the NHS adult 30g/day recommendation.

Prices and nutrient totals are estimates from generic food values and low-cost price assumptions. Brands, drained weights, cooking method and portions vary, so check packets and adjust the quantities. The percentages use adult food-label Reference Intakes/Nutrient Reference Values; they are not an individual medical nutrition plan. The UK food-composition resource for checking generic values is [CoFID](https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid); adult label reference values are in [Annex XIII](https://www.legislation.gov.uk/eur/2011/1169/annex/XIII).

`recipes.json` is the file the website reads. `generate_catalog.py` rebuilds the 205-entry catalogue and its rough nutrition estimates from inexpensive meal patterns; rerunning it replaces manual edits to the generated JSON.
