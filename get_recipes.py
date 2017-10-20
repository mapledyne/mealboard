#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from lxml.html import fromstring, tostring, parse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import re
import os

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

userName = os.environ['MEALBOARD_USER']
userPin = os.environ['MEALBOARD_PIN']


def login(url, loginData):
    """ Login into mealboard and create variable session,
        to keep all cookies necessary for obtaining all recipes
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko)\
         Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,\
        image/webp,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'http://mealboard.macminicolo.net/mealboard/login.jsp',
    }

    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))

    try:
        r = s.post(url,
                   headers=headers,
                   timeout=30,
                   verify=False,
                   data=loginData,
                   allow_redirects=True
                   )

        if r.status_code == 200:
            content = (r.content).decode('utf-8')
            return content, s
        else:
            return None, None

    except Exception as E:
        print(E)
        return None, None


def getHtml(url, session):
    """
        Simple Get requests to get all html pages
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/58.0.3029.110 '
        'Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
        'image/webp,*/*;q=0.8',
        'Referer': 'http://mealboard.macminicolo.net/mealboard/recipeedit.jsp'
    }

    try:
        r = session.get(url,
                        headers=headers,
                        timeout=30,
                        verify=False,
                        allow_redirects=True
                        )

        if r.status_code == 200:
            content = (r.content).decode('utf-8')
            return content, session
        else:
            return None, None

    except Exception as E:
        print(E)
        return None, None


def parseRecipeEditPage(content, recipeData):
    """
        Parse and extract
        Category / Makes / Prep Time / Cook Time
        from Edit Page
    """

    html = fromstring(content)

    # Get categories
    try:
        categories = list()

        categories = html.xpath(
            '//select[@name="category"]/option[@selected="selected"]/@value'
        )

        recipeData.update({'Category': ", ".join(categories)})
    except Exception as E:
        print(E)
        pass

    # Servings (Makes)
    try:
        servings = html.xpath('//input[@name="num_servings"]/@value')[0]
        recipeData.update({'Servings': servings})
    except BaseException:
        pass

    # Prep Time
    try:
        PrepTimeContent = 'PT'
        PrepTime = ''

        prepHour = html.xpath('//input[@name="prep_time_hr"]/@value')[0]
        if len(prepHour.strip()) > 0:
            PrepTimeContent = "{0}{1}H".format(PrepTimeContent, prepHour)
            PrepTime = "{0} H".format(prepHour)

        prepMin = html.xpath('//input[@name="prep_time_min"]/@value')[0]
        if len(prepMin.strip()) > 0:
            PrepTimeContent = "{0}{1}M".format(PrepTimeContent, prepMin)
            PrepTime = "{0} {1} Min".format(PrepTime, prepMin)

        if len(PrepTimeContent) > 2:
            recipeData.update({'PrepTimeContent': PrepTimeContent})
            recipeData.update({'PrepTime': PrepTime.strip()})
    except BaseException:
        pass

    # Cook Time
    try:
        CookTimeContent = 'PT'
        CookTime = ''

        cookHour = html.xpath('//input[@name="cooking_time_hr"]/@value')[0]
        if len(cookHour.strip()) > 0:
            CookTimeContent = "{0}{1}H".format(CookTimeContent, cookHour)
            CookTime = "{0} H".format(cookHour)

        cookMin = html.xpath('//input[@name="cooking_time_min"]/@value')[0]
        if len(cookMin.strip()) > 0:
            CookTimeContent = "{0}{1}M".format(CookTimeContent, cookMin)
            CookTime = "{0} {1} Min".format(CookTime, cookMin)

        if len(CookTimeContent) > 2:
            recipeData.update({'CookTimeContent': CookTimeContent})
            recipeData.update({'CookTime': CookTime.strip()})
    except BaseException:
        pass

    return recipeData


def parseRecipeHtml(content, recipeData):
    """ parseRecipe(content, recipeName)
        parse missing informations and convert recipe html code
        into new format. using http://schema.org/Recipe """

    html = fromstring(content)

    # Load images and generate html code
    try:
        recipeImages = list()

        images = html.xpath('//div[@class="photo"]/img/@src')
        for image in images:
            image = "<img itemprop=\"image\" src=\"{0}\" alt=\"{0}\" />".format(
                    image,
                    recipeData['Name']
                )
            recipeImages.append(image)

        recipeData.update({'Images': "\n".join(recipeImages)})
    except Exception as E:
        print(E)
        pass

    # get recipe description
    try:
        recipeDescription = html.xpath('//div[@class="description"]/text()')[0]
        recipeData.update({'Description': recipeDescription})
    except Exception as E:
        # print(E)
        pass

    # Load ingredients and generate html code
    try:
        recipeIngredients = list()

        ingredients = html.xpath('//div[@class="ingredientsBox"]/text()')
        for ingredient in ingredients:
            if len(ingredient.strip()) > 0:
                ingredient = "<span itemprop=\"recipeIngredient\">{0}</span><br />".format(
                    ingredient.strip())
                recipeIngredients.append(ingredient)

        recipeData.update({'Ingredients': "\n".join(recipeIngredients)})
    except Exception as E:
        # print(E)
        pass

    # Load instructions and generate html code
    try:
        recipeInstructions = list()

        instructions = html.xpath('//div[@class="preparationBox"]/text()')
        for instruction in instructions:
            if len(instruction.strip()) > 0:
                instruction = "<span itemprop=\"recipeInstructions\">{0}</span><br />\n".format(
                    instruction.strip())
                recipeInstructions.append(instruction)

        recipeData.update({'Instructions': "\n".join(recipeInstructions)})
    except Exception as E:
        # print(E)
        pass

    # New html5 template
    recipeHtml = """
        <!doctype html>
        <html>
            <head>
                <title>{0}</title>
            </head>
            <body>
                <div itemscope itemtype="http://schema.org/Recipe">\n
                <h1>
                    <a href="{11}" title="{0}">
                        <span itemprop="name">{0}</span>
                    </a>
                </h1>\n
                <strong>Category :</strong>
                    <span itemprop="recipeCategory">{1}</span>\n
                <br />\n
                {2}
                <br />\n
                <strong>Description:</strong><br />\n
                <span itemprop="description">{3}</span><br />\n
                <br />\n
                <strong>Prep Time:</strong>
                <meta itemprop="prepTime" content="{4}">{5}<br />\n
                <strong>Cook time:</strong>
                <meta itemprop="cookTime" content="{6}">{7}<br />\n
                <strong>Servings: </strong>
                <span itemprop="recipeYield">{8}</span><br />\n
                <br />\n
                <strong>Ingredients:</strong><br />\n
                {9}
                <br />\n
                <strong>Instructions:</strong><br />\n
                {10}
            </body>
        </html>""".format(
        recipeData['Name'],
        recipeData['Category'],
        recipeData['Images'],
        recipeData['Description'],
        recipeData['PrepTimeContent'],
        recipeData['PrepTime'],
        recipeData['CookTimeContent'],
        recipeData['CookTime'],
        recipeData['Servings'],
        recipeData['Ingredients'],
        recipeData['Instructions'],
        recipeData['sourceUrl']
    )

    return recipeHtml


def main():

    loginData = {
        'username': userName,
        'pin': userPin
    }

    # Login
    content, session = login(
        'http://mealboard.macminicolo.net/mealboard/loginsubmit.jsp',
        loginData)

    if content is None:
        print('Login Failed')
    else:
        if 'name="recipe_detail_frame"' in content:
            print('login OK')

            # Get recipes list
            content, session = getHtml(
                'http://mealboard.macminicolo.net/mealboard/recipelist.jsp'
                '?RECIPE_NAME=NEW%20RECIPE', session)

            if content is not None:
                if 'recipelist.css' in content:

                    html = fromstring(content)
                    if html is not None:

                        # Load all recipe names in the left menu
                        recipes = html.xpath('//table/tr/@onclick')
                        for recipe in recipes[2:]:

                            recipeData = {
                                'Name': '',
                                'Images': '',
                                'Servings': '',
                                'PrepTime': '',
                                'PrepTimeContent': '',
                                'CookTime': '',
                                'CookTimeContent': '',
                                'Category': '',
                                'Description': '',
                                'Ingredients': '',
                                'Instructions': '',
                                'sourceUrl': '',
                                'fileName': ''
                            }

                            if "loadRecipeDetail" in recipe:
                                recipeName = recipe.split(
                                    "loadRecipeDetail(\'")[1]
                                recipeName = recipeName.split('\')')[0].strip()

                                recipeData.update({'Name': recipeName})

                                print(recipeName.encode())

                                fileName = "".join(
                                    [c for c in recipeName if re.match(r'\w', c)])
                                recipeData.update({'fileName': fileName})

                                # Load "Edit Page" to get propper values for
                                # Category / Makes / PrepTime / CookTime
                                recipeEditUrl = "http://mealboard.macminicolo.net/mealboard/recipeform.jsp?RECIPE_NAME={0}".format(
                                    recipeData['Name'])
                                content, session = getHtml(
                                    recipeEditUrl,
                                    session
                                )
                                if content is not None:
                                    recipeData = parseRecipeEditPage(
                                        content,
                                        recipeData
                                    )

                                # Download html page for recipe
                                recipeHtmlUrl = "http://mealboard.macminicolo.net/mealboard/recipeview.jsp?RECIPE_NAME={0}".format(
                                    recipeData['Name'])
                                recipeData.update({'sourceUrl': recipeHtmlUrl})

                                content, session = getHtml(
                                    recipeHtmlUrl, session)
                                if content is not None:

                                    # save orginal html page
                                    fileName = "./html/{0}.html".format(
                                        recipeData['fileName'])
                                    with open(fileName, 'w', encoding="utf-8") as fp:
                                        fp.write(content)

                                    # parse and convert recipe html page
                                    recipeHtml = parseRecipeHtml(
                                        content, recipeData)

                                    # Save new html page
                                    fileName = "./recipes/{0}.html".format(
                                        recipeData['fileName']
                                        )
                                    with open(fileName, 'w', encoding='utf-8') as fp:
                                        fp.write(recipeHtml)


if __name__ == "__main__":
    main()
