import os
import time
import requests
from lxml import html
from path import path

import credentials

CHAR_URL = "http://www.pathofexile.com/character-window/get-characters"
ITEM_URL = "http://www.pathofexile.com/character-window/get-items"
STASH_URL = "http://www.pathofexile.com/character-window/get-stash-items"


def empty_folder(pth):
    """
    empties the given path of its contents
    """
    if not isinstance(pth, path):
        pth = path(pth)

    #delete and recreate the folder
    pth.rmtree_p()
    pth.mkdir()


def get_firefox_profile():
    """returns the directory of the default firefox profile"""
    for folder in path("~/.mozilla/firefox").expand().listdir():
        if folder.endswith("default"):
            return webdriver.firefox.firefox_profile.FirefoxProfile(
                profile_directory=folder)


def get_login_session():
    LOGIN_URL = "https://www.pathofexile.com/login"

    s = requests.Session()

    #need to get a special hash (probably csrf-like token for submission)
    resp = s.get(LOGIN_URL)
    tree = html.fromstring(resp.text)

    resp = s.post(LOGIN_URL, data={
        "login_email": credentials.USERNAME,
        "login_password": credentials.PASSWORD,
        "hash": tree.xpath("//input[@name='hash']")[0].attrib["value"],
    })
    return s


if __name__ == "__main__":
    #clear all the old data
    empty_folder("data")

    #login and get the session
    s = get_login_session()

    print("FETCHING CHARACTER DATA... ", end=' ')
    req = s.get(CHAR_URL)
    path("data/characters.json").write_text(req.text)
    print("DONE")

    print("FETCHING CHARACTER ITEM DATA... ", end=' ')
    leagues = set()
    for char in req.json():
        name = char["name"]
        leagues.add(char["league"])  # we want all the available leagues
        req = s.post(ITEM_URL, data={"character": name})
        path("data/items_%s.json" % name).write_text(req.text)
    print("DONE")

    print("FETCHING STASH ITEM DATA... ", end=' ')
    #first page has different fetching params to read the names of the rest of
    #the tabs
    for league in leagues:
        req = s.post(STASH_URL, data={
            "league": league,
            "tabs": 1,
            "tabIndex": 0,
        })
        path("data/stash_%s_1.json" % league.lower()).write_text(req.text)

        #fetch the rest of the pages
        for page_no in range(1, int(req.json()["numTabs"])):
            req = s.post(STASH_URL, data={
                "league": league,
                "tabs": 0,
                "tabIndex": page_no,
            })
            path("data/stash_%s_%s.json" % (league.lower(), page_no + 1)).\
                write_text(req.text)
    print("DONE")

    print("DUMPING DATA INTO DATABASE...")
    os.system("python dump.py")
