import json

from scrapy import Spider, Request, FormRequest
from urllib2 import HTTPError

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
        try:
            import credentials
            username, password = credentials.USERNAME, credentials.PASSWORD
        except ImportError:
            import getpass
            print "NO CREDENTIALS"
            username = raw_input("Username (Email): ").strip()
            password = getpass.getpass("Password: ")

        return FormRequest.from_response(
            resp,
            formxpath="//form[contains(@class,'poeForm')]",
            formdata={
                'login_email': username,
                'login_password': password,
            },
            callback=self.after_login,
        )

    def after_login(self, resp):
        if "Logged in as" not in resp.body_as_unicode():
            raise SystemExit("NOT LOGGED IN.")

        # get the character data
        yield Request(
            CHAR_URL,
            callback=self.parse_char_data
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
                    "accountName": "iynaix",
                },
                meta={'league': league},
                callback=self.parse_stash_data
            )

    def parse_char_data(self, resp):
        data = json.loads(resp.body_as_unicode())
        if "error" in data:
            raise HTTPError("Request Throttled")

        for char in data:
            # no need to scrape
            if char["league"].lower() not in self.leagues:
                continue

            yield FormRequest(
                ITEM_URL,
                formdata={
                    "character": char["name"],
                    "accountName": "iynaix",
                },
                meta={
                    'league': char["league"].title(),
                    'location': {
                        "name": char["name"],
                        "is_premium": False,
                        "is_character": True,
                    },
                },
                callback=self.parse_item
            )

    def parse_stash_data(self, resp):
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
                callback=self.parse_item
            )

    def parse_item(self, resp):
        data = json.loads(resp.body_as_unicode())
        if "error" in data:
            raise HTTPError("Request Throttled")

        # we need the location as extra data
        data["location"] = resp.meta["location"]

        # download item image
        data["file_urls"] = []
        for item in data.get("items", []):
            item["icon"] = self.img_url(resp, item["icon"])
            data["file_urls"].append(item["icon"])
            for i in item.get("socketedItems", []):
                i["icon"] = self.img_url(resp, i["icon"])
                data["file_urls"].append(i["icon"])
        yield data

    def img_url(self, resp, url):
        """some image urls are relative, so normalize the image url"""
        if url.startswith("http"):
            return url
        return resp.urljoin(url)
