import itertools
import json

from scrapy import Spider, Request, FormRequest
from urllib2 import HTTPError

LOGIN_URL = "https://www.pathofexile.com/login"
CHAR_URL = "https://www.pathofexile.com/character-window/get-characters"
ITEM_URL = "https://www.pathofexile.com/character-window/get-items"
STASH_URL = "https://www.pathofexile.com/character-window/get-stash-items"
PASSIVE_URL = "https://www.pathofexile.com/character-window/get-passive-skills"

STANDARD_TAB = {'b': 54, 'g': 84, 'r': 124}


def page_group_delims(tabs):
    """returns indexes of the tabs that are page group delimiters"""
    for idx, tab in enumerate(tabs):
        if tab['colour'] == {'b': 54, 'g': 84, 'r': 124}:
            continue

        if tab['hidden']:
            continue

        try:
            int(tab['n'])  # valid ints are not numbers
        except ValueError:
            yield idx


def get_pages(tabs, page_groups=None):
    # no page groups, specified, return everything
    if page_groups is None:
        for tab in tabs:
            if tab["hidden"]:
                continue
            yield tab

    group_idxs = list(page_group_delims(tabs))
    group_idxs.append(None)

    for page_group in page_groups:
        for start, end in zip(group_idxs, group_idxs[1:]):
            if tabs[start]["n"].lower() in page_groups:
                for tab in itertools.islice(tabs, start, end):
                    if tab["hidden"]:
                        continue
                    yield tab
        else:
            raise LookupError("Page group '%s' not found." % page_group)


class MainSpider(Spider):
    """
    Spider that fetches the inventory info
    """
    name = "main"
    start_urls = [LOGIN_URL]
    download_delay = 3

    def __init__(self, *args, **kwargs):
        super(MainSpider, self).__init__(*args, **kwargs)
        leagues = kwargs.get("leagues", "All")
        self.leagues = set(l.strip().title() for l in leagues.split(","))

        # handle the page groups to fetch
        self.page_groups = set()
        page_groups = kwargs.get("page_groups", "")
        if page_groups:
            self.page_groups = set(g.strip().lower() for g in
                                    page_groups.split(","))

        # handle the pages
        self.pages = set()
        pages = kwargs.get("pages", "")
        if pages:
            self.pages = set(p.strip().lower() for p in
                                pages.split(","))

    def valid_league(self, league):
        if "All" in self.leagues:
            return True
        return league.title() in self.leagues

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

    def parse_char_data(self, resp):
        data = json.loads(resp.body_as_unicode())
        if "error" in data:
            raise HTTPError("Request Throttled")

        # do we need to parse any characters?
        parse_chars = self.page_groups or self.pages

        stash_leagues = set()
        for char in data:
            # no need to scrape
            if not self.valid_league(char["league"]):
                continue

            # get the leagues to fetch for stashes
            stash_leagues.add(char["league"])

            metadata = {
                'league': char["league"],
                'location': {
                    "name": char["name"],
                    "is_character": True,
                }
            }

            # get items for the user if needed
            if not parse_chars:
                continue

            yield FormRequest(
                ITEM_URL,
                formdata={
                    "character": char["name"],
                    "accountName": "iynaix",
                },
                meta=metadata,
                callback=self.parse_item,
            )

            # get jewels in passive tree for the user
            yield FormRequest(
                PASSIVE_URL,
                formdata={
                    "character": char["name"],
                    "accountName": "iynaix",
                    "reqData": "0",
                },
                meta=metadata,
                callback=self.parse_item,
            )

        # get the stash data
        # called from within get_char_data as we need to get the leagues
        # before parsing
        for league in stash_leagues:
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

    def parse_stash_data(self, resp):
        league = resp.meta['league']
        data = json.loads(resp.body_as_unicode())
        if "error" in data:
            raise HTTPError("Request Throttled")

        pages = data["tabs"]
        for page_no, tab in enumerate(pages):
            tab = data["tabs"][page_no]
            if tab["hidden"]:
                continue

            tab_name = tab["n"]

            # see if the name is numeric to determine if premium
            is_premium = False
            try:
                int(tab_name)
            except ValueError:
                is_premium = True
            # different color means premium
            if tab['colour'] != STANDARD_TAB:
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
