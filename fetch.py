"""Fetching data about the characters and the stash.

Usage:
  fetch.py [--dump]
  fetch.py [--league=<league>]
  fetch.py (-h | --help)

Options:
  -h --help             Show this screen.
  --dump                Show version.
  --league=<league>     Only download data for these leagues [default: all].

"""

from __future__ import print_function
import os
import requests

from docopt import docopt
from path import path
from lxml import html

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


if __name__ == '__main__':
    arguments = docopt(__doc__)

    #clear all the old data
    empty_folder("data")

    #login and get the session
    s = get_login_session()

    print("FETCHING CHARACTER DATA... ", end=' ')
    char_data = s.get(CHAR_URL).json()
    print("DONE")

    league_arg = arguments.get("--league", "all")
    if league_arg == "all":
        leagues = set([char["league"].lower() for char in char_data])
    else:
        leagues = set([x.strip().lower() for x in league_arg.split(",")])

    print("FETCHING CHARACTER ITEM DATA... ", end=' ')
    for char in char_data:
        char_league = char["league"].lower()
        if char_league not in leagues:
            continue
        name = char["name"]
        req = s.post(ITEM_URL, data={"character": name})
        path("data/items_%s.json" % name).write_text(req.text)
    print("DONE")

    print("FETCHING STASH ITEM DATA... ", end=' ')
    #first page has different fetching params to read the names of the rest of
    #the tabs
    for league in leagues:
        req = s.post(STASH_URL, data={
            "league": league.title(),
            "tabs": 1,
            "tabIndex": 0,
        })
        path("data/stash_%s_1.json" % league).write_text(req.text)

        #fetch the rest of the pages
        for page_no in range(1, int(req.json()["numTabs"])):
            req = s.post(STASH_URL, data={
                "league": league.title(),
                "tabs": 0,
                "tabIndex": page_no,
            })
            path("data/stash_%s_%s.json" % (league, page_no + 1)).\
                write_text(req.text)
    print("DONE")

    #do the dump if we ask for it
    if arguments.get("--dump", False):
        print("DUMPING DATA INTO DATABASE...")
        os.system("python dump.py")
