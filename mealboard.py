"""Download all of the mealboard recipes."""
import requests
import sys
import re
import json
import os
import argparse
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def get_config():
    """Retrieve configuration from environment variables or command-line arguments."""
    # Define command-line arguments
    parser = argparse.ArgumentParser(description="Retrieve configuration for the script.")
    parser.add_argument("--username", type=str, help="Mealboard Username.")
    parser.add_argument("--password", type=str, help="Mealboard Password.")
    parser.add_argument("--base_url", type=str, help="Base URL for the API.")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Retrieve configuration from environment variables, falling back to command-line arguments
    config = {
        "username": os.getenv("USERNAME", args.username or ""),
        "password": os.getenv("PASSWORD", args.password or ""),
        "base_url": os.getenv("BASE_URL", args.base_url or "https://server.mealboardapp.com/"),
    }

    if not config["username"]:
        sys.exit("Error: Username must be set via .env file or command line (--username).")
    if not config["password"]:
        sys.exit("Error: Password must be set via .env file or command line (--password).")

    return config

def print_response(response: requests.Response) -> None:
    print(f"Status Code: {response.status_code}\n")
    print(f"Headers: {response.headers}\n")
    print(f"Cookies: {requests.utils.dict_from_cookiejar(response.cookies)}\n")
    print("Body:")
    print(response.text)


def check_response(response, message="Something went wrong"):

    if response.status_code != 200:
        print(f"{message}:")
        print_response(response) 
        sys.exit(1)

def save_recipes(recipes, bearer, req):
    output_dir = "./recipes"
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

    with tqdm(total=len(recipes), desc="Processing Recipes", unit="recipe") as pbar:
        for recipe in recipes:
            try:
                # Update progress bar description with the current recipe name
                pbar.set_description(f"Processing: {recipe['name']}")
                url = f"{base_url}mealboard/getrecipe/Briaball@hotmail.com"
                payload = {'recipeName': recipe['name']}
                headers = {
                    'Authorization': f'Bearer {bearer}',
                    'Content-Type': 'application/json'
                }

                one_recipe = req.post(url, json=payload, headers=headers)
                check_response(one_recipe, f"Error loading recipe: {recipe['name']}")

                # Replace invalid filename characters with "_"
                safe_recipe_name = re.sub(r'[<>:"/\\|?*]', '_', recipe['name'])
                file_path = os.path.join(output_dir, f"{safe_recipe_name}.json")
                with open(file_path, "w", encoding="utf-8") as text_file:
                    json_data = one_recipe.json()
                    text_file.write(json.dumps(json_data, indent=4))
                
                # Advance the progress bar
                pbar.update(1)

            except IOError as e:
                tqdm.write(f"Error saving recipe '{recipe['name']}': {e}")
                raise
            except Exception as e:
                tqdm.write(f"Unexpected error processing recipe '{recipe['name']}': {e}")
                raise
            
            # Advance the progress bar
            pbar.update(1)


if __name__ == "__main__":
    config = get_config()

    req = requests.Session()

    # Construct the payload
    payload = {'email': config['username'], 'password': config['password']}
    base_url = config['base_url']
    bearer = config["bearer"]
    user = config["username"]
    r = req.post(base_url + 'login', data=payload)

    check_response(r, "Unable to log in:")
    print(r.text)

    # Set authorization header with bearer token
    headers = {'Authorization': f'Bearer {bearer}'}

    recipe_list_response = req.get(f'{base_url}mealboard/recipeitems/{user}'), headers=headers)
    check_response(recipe_list_response, "Unable to retrieve recipes:")
    
    recipe_list = recipe_list_response.json()  # Parse the JSON response to a native Python object

    save_recipes(recipe_list, bearer, req)
