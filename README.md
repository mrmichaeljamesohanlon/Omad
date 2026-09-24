# Omad

A JSON-first, mobile-friendly recipe page for low-cost one-meal-a-day ideas.

Run this folder with python3 -m http.server 8000 and open http://localhost:8000. The page reads recipes.json; opening index.html directly may block that fetch.

Browse Specials, Breakfast, Lunch, Dinner and Snacks. Filter vegetarian or vegan, show recipes with seasonal produce for the current UK season, search by recipe name or ingredients (comma-separated terms must all match), and sort by cost, protein or fibre.

Edit recipes.json to add recipes. Prices and nutrition figures are rough estimates; check packet labels and local prices before relying on them. The app uses an 80g protein target and a 30g daily fibre target. The NHS states 30g fibre per day for adults: https://www.nhs.uk/live-well/eat-well/digestive-health/how-to-get-more-fibre-into-your-diet/

Each recipe records its categories, dietary tags, seasons, ingredients, method, cost and nutrition per serving. Set special to true to include it in the Specials view.
