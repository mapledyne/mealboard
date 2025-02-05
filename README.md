# Mealboard Recipe Exporter
This script goes to your [Mealboard](http://mealboard.com) account and downloads all of the recipes. Mealboard has switched to storing and returning the recipes as JSON, so we're just leaving them as-is in that format for now.

## Usage
This script looks for two environment variables: `USERNAME` and `PASSWORD`. These should match what you use for Mealboard to sync.

Run the file:

`python3 mealboard.py`

This will download all of the recipes from Mealboard's website as json, leaving the converted files in the recipes folder.

### Warnings:
This doesn't well handle unexpected situations yet. Feel free to fix and make a PR for it, or I'll get to it eventually. For now:

* Supports Python 3 only
* Requires recipes folder to exist before running

TODO: Smoother support of bearer tokens after login