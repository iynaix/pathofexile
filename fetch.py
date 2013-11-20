import requests
from path import path
import os
import time
from selenium import webdriver
from credentials import USERNAME, PASSWORD

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


def get_login_cookies():
    ACCOUNT_URL = "http://www.pathofexile.com/my-account"

    d = webdriver.Firefox(firefox_profile=get_firefox_profile())
    #try going directly to the account page
    d.get(ACCOUNT_URL)
    #gotta sign in
    if "login" in d.current_url:
        for form in d.find_elements_by_tag_name("form"):
            if "steam" in form.get_attribute("action"):
                form.submit()
                break

        #start signing in via steam by filling out the login form
        login_form = d.find_element_by_id("loginForm")
        login_form.find_element_by_id("steamAccountName").send_keys(USERNAME)
        login_form.find_element_by_id("steamPassword").send_keys(PASSWORD)
        login_form.submit()
        time.sleep(10)

    cookies = {}
    for c in d.get_cookies():
        if "pathofexile" in c["domain"]:
            cookies[c["name"]] = c["value"]
    d.close()
    return cookies


if __name__ == "__main__":
    #clear all the old data
    empty_folder("data")

    #use selenium to get the cookies needed for requests
    cookies = get_login_cookies()

    print("FETCHING CHARACTER DATA... ", end=' ')
    req = requests.get(CHAR_URL, cookies=cookies)
    path("data/characters.json").write_text(req.text)
    print("DONE")

    print("FETCHING CHARACTER ITEM DATA... ", end=' ')
    for char in req.json():
        name = char["name"]
        req = requests.post(ITEM_URL, cookies=cookies,
                            data={"character": name})
        path("data/items_%s.json" % name).write_text(req.text)
    print("DONE")

    print("FETCHING STASH ITEM DATA... ", end=' ')
    #first page has different fetching params to read the names of the rest of
    #the tabs
    req = requests.post(STASH_URL, cookies=cookies, data={
        "league": "Domination",
        "tabs": 1,
        "tabIndex": 0,
    })
    path("data/stash_1.json").write_text(req.text)

    #fetch the rest of the pages
    for page_no in range(1, int(req.json()["numTabs"])):
        req = requests.post(STASH_URL, cookies=cookies, data={
            "league": "Domination",
            "tabs": 0,
            "tabIndex": page_no,
        })
        path("data/stash_%s.json" % (page_no + 1)).write_text(req.text)
    print("DONE")

    print("DUMPING DATA INTO DATABASE...")
    os.system("python dump.py")
