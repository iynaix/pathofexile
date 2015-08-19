import click

from app import db
from models import Item, Modifier, Location, in_page_group
from sqlalchemy.sql.expression import false


def find_gaps(loc):
    """returns the coordinates that have not been used"""
    # a page is 12 * 12
    page = []
    for i in range(12):
        page.append([0] * 12)


    for item in Item.query.filter(Item.location == loc).all():
        for x in range(item.x, item.x + item.w):
            for y in range(item.y, item.y + item.h):
                page[y][x] = 1

    gaps = []
    for y in range(12):
        for x in range(12):
            if not page[y][x]:
                gaps.append((x, y))
    return gaps


locs = Location.query.filter(
    *in_page_group("Rare")
).order_by(Location.page_no).all()
for loc in locs:
    gaps = find_gaps(loc)
    if not gaps:
        continue
    click.echo(loc)
    click.echo(gaps)
    print

# for item in items:
#     click.echo(item)
