from app import db
from models import Item, Modifier, Location, in_page_group, Property
from sqlalchemy import case, CHAR
from sqlalchemy.dialects import postgresql


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


def print_sql(q):
    print str(q.statement.compile(dialect=postgresql.dialect()))


def resist_cases(include_all=True, include_chaos=True):
    """
    returns the case statement needed for searching for resists

    include_all determines if + to all resists is counted
    include_chaos determines if + to chaos resists is counted
    """
    resist_map = [
        ("%to Fire Resistance", "Fire"),
        ("%to Cold Resistance", "Cold"),
        ("%to Lightning Resistance", "Lightning"),
        ("%to Fire and Cold Resistances", "Fire Cold"),
        ("%to Fire and Lightning Resistances", "Fire Lightning"),
        ("%to Cold and Lightning Resistances", "Cold Lightning"),
    ]
    if include_all:
        resist_map.append(
            ("%to all Elemental Resistances", "Fire Cold Lightning")
        )
    if include_chaos:
        resist_map.append(
            ("%to Chaos Resistance", "Chaos")
        )

    ret = []
    for mod, resists in resist_map:
        ret.append(
            (Modifier.normalized.like(mod),
             postgresql.array(resists.split(), type_=CHAR))
        )
    return case(ret)


# for mod in Modifier.query.filter(
#     Modifier.normalized.like("%Resistance%")
# ).distinct(Modifier.normalized):
#     print mod.normalized

def filter_resist_counts():
    res = db.session.query(
        Item,
        db.func.array_agg(resist_cases()),
    ).join(
        Modifier,
    ).group_by(
        Item,
    ).filter(
        Modifier.normalized.like("%Resistance%")
    )

    print_sql(res)


def locs_by_item_count():
    item_count = db.func.count(Location.items)

    locs = db.session.query(
        Location,
        item_count,
    ).join(Item).group_by(Location).filter(
        Location.name.like("% (Remove-only)"),
    ).order_by(
        item_count,
    ).all()

    for loc in locs:
        print loc


"""
SELECT item.id,
       item.name,
       item.type_,
       item.location_id,
       array_agg(DISTINCT row(CASE
            WHEN( modifier.normalized LIKE '%to Fire Resistance' ) THEN ARRAY[ 'Fire' ]
            WHEN( modifier.normalized LIKE '%to Cold Resistance' ) THEN ARRAY[ 'Cold' ]
            WHEN( modifier.normalized LIKE '%to Lightning Resistance' ) THEN ARRAY[ 'Lightning' ]
            WHEN( modifier.normalized LIKE '%to Fire and Cold Resistances' ) THEN ARRAY[ 'Fire', 'Cold' ]
            WHEN( modifier.normalized LIKE '%to Fire and Lightning Resistances' ) THEN ARRAY[ 'Fire', 'Lightning' ]
            WHEN( modifier.normalized LIKE '%to Cold and Lightning Resistances' ) THEN ARRAY[ 'Cold', 'Lightning' ]
            WHEN( modifier.normalized LIKE '%to all Elemental Resistances' ) THEN ARRAY[ 'Fire', 'Cold', 'Lightning' ]
            WHEN( modifier.normalized LIKE '%to Chaos Resistance' ) THEN ARRAY[ 'Chaos' ]
       END)::text[])
       AS resists
FROM   item
JOIN   modifier
ON     item.id = modifier.item_id
WHERE  modifier.normalized LIKE '%Resistance%'
GROUP BY item.id,
       item.name,
       item.type_,
       item.location_id,
       modifier.normalized
ORDER BY item.location_id
"""
