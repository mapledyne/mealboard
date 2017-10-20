# Mealboard Recipe Exporter
This script goes to your [Mealboard](http://mealboard.com) account and downloads all of the recipes. It then converts them to a standardized format ([schema.org's recipe format](http://schema.org/Recipe)) so they can be used in other places as desired.

## Usage
This script looks for two environment variables: `MEALBOARD_USER` and `MEALBOARD_PIN`. These should match what you use for Mealboard to sync.

Create a `recipe` directory for everything to end up in and run the file:

`python3 get_recipes.py`

This will download all of the HTML recipes from Mealboard's website and convert them, leaving the converted files in the recipes folder.

### Warnings:
This doesn't well handle unexpected situations yet. Feel free to fix and make a PR for it, or I'll get to it eventually. For now:

* Supports Python 3 only
* Requires recipes folder to exist before running
* Only supports username/pin in env variables
