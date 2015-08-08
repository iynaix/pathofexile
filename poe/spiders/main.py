import json

from scrapy import Spider, Request, FormRequest
from urllib2 import HTTPError

import credentials

# from poe.items import CurrencyItem

LOGIN_URL = "https://www.pathofexile.com/login"
CHAR_URL = "https://www.pathofexile.com/character-window/get-characters"
ITEM_URL = "https://www.pathofexile.com/character-window/get-items"
STASH_URL = "https://www.pathofexile.com/character-window/get-stash-items"


class MainSpider(Spider):
    """
    Spider that fetches the inventory info
    """
    name = "main"
    start_urls = [LOGIN_URL]
    leagues = ["warbands"]
    download_delay = 3

    def parse(self, resp):
        return FormRequest.from_response(
            resp,
            formxpath="//form[contains(@class,'poeForm')]",
            formdata={
                'login_email': credentials.USERNAME,
                'login_password': credentials.PASSWORD,
            },
            callback=self.after_login,
        )

    def after_login(self, resp):
        if "Logged in as" not in resp.body_as_unicode():
            raise SystemExit("NOT LOGGED IN.")

        # get the character data
        yield Request(
            CHAR_URL,
            callback=self.fetch_all_char_data
        )

        # get the league data
        for league in self.leagues:
            league = league.title()
            yield FormRequest(
                STASH_URL,
                formdata={
                    "league": league,
                    "tabs": "1",
                    "tabIndex": "0",
                },
                meta={'league': league},
                callback=self.fetch_all_stash_data
            )

    def fetch_all_char_data(self, resp):
        data = json.loads(resp.body_as_unicode())
        if "error" in data:
            raise HTTPError("Request Throttled")

        for char in data:
            # no need to scrape
            if char["league"].lower() not in self.leagues:
                continue

            loc = dict(
                name=char["name"],
                is_premium=False,
                is_character=True,
            )

            yield FormRequest(
                ITEM_URL,
                formdata={"character": char["name"]},
                meta={
                    'league': char["league"].title(),
                    'location': loc,
                },
                callback=self.fetch_item_data
            )

    def fetch_all_stash_data(self, resp):
        league = resp.meta['league']
        data = json.loads(resp.body_as_unicode())
        if "error" in data:
            raise HTTPError("Request Throttled")

        for page_no, tab in enumerate(data["tabs"]):
            tab = data["tabs"][page_no]
            tab_name = tab["n"]

            # see if the name is numeric to determine if premium
            is_premium = False
            try:
                int(tab_name)
            except ValueError:
                is_premium = True
            # different color means premium
            if tab['colour'] != {'b': 54, 'g': 84, 'r': 124}:
                is_premium = True

            # create the location to be passed on for the individual stash page
            loc = dict(
                name=tab_name,
                page_no=page_no + 1,
                is_premium=is_premium,
                is_character=False,
            )

            yield FormRequest(
                STASH_URL,
                formdata={
                    "league": league.title(),
                    "tabs": "0",
                    "tabIndex": str(page_no),
                },
                meta={
                    'league': league,
                    'location': loc,
                },
                callback=self.fetch_item_data
            )

    def fetch_item_data(self, resp):
        data = json.loads(resp.body_as_unicode())
        if "error" in data:
            raise HTTPError("Request Throttled")

        yield data
        # from pprint import pprint
        # print resp.meta["location"]
        # for item in data["items"]:
        #     # ITEM SQL_DUMP HERE
        #     pprint(item)
