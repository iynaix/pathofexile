from collections import defaultdict, Counter
import itertools

from flask import request, render_template
from flask.views import View, MethodView
from jinja2.filters import do_mark_safe
from sqlalchemy import false

from app import app, db
import constants
from models import (Item, Location, Property, Requirement, Modifier,
                    in_page_group)
from utils import normfind, group_items_by_level, groupsortby, get_constant

#  init constants
CHROMATIC_RE = r"B+G+R+"
GEMS = get_constant("GEMS", as_dict=True)
QUIVERS = get_constant("QUIVERS", as_dict=True)


@app.template_filter('percent')
def percent_filter(x):
    return "%.2f%%" % (x * 100)


@app.template_filter('socket')
def socket_filter(x):
    """outputs nice html for a socket string"""
    out = []
    for c in x:
        if c == "B":
            out.append('<span class="label label-primary">&nbsp;</span>')
        elif c == "G":
            out.append('<span class="label label-success">&nbsp;</span>')
        elif c == "R":
            out.append('<span class="label label-danger">&nbsp;</span>')
        else:
            out.append('&nbsp;')
    # join with hair spaces
    return do_mark_safe("&#8202;".join(out))


@app.context_processor
def location_nav():
    locations = {"stash": [], "characters": []}
    for loc in Location.query.order_by(Location.page_no).all():
        if loc.is_character:
            locations["characters"].append(loc)
        else:
            locations["stash"].append(loc)
    return dict(locations=locations)


@app.route('/search/', methods=["POST"])
def simple_search():
    """
    Performs a simple full text search for items
    """
    search_term = request.form["simple_search"].replace(" ", " & ")
    items = Item.query.filter(
        Item.full_text.op('@@')(db.func.to_tsquery(search_term))
    ).all()
    return render_template('items.html', items=items)


@app.route('/delete/<item_id>', methods=["POST"])
def item_mark_delete(item_id):
    """
    Marks or unmarks an item as deleted
    """
    Item.query.get(item_id).is_deleted = bool(int(request.form["checked"]))
    db.session.commit()
    return "success"


@app.route('/deleted/')
def deleted_items():
    """
    Performs a simple full text search for items
    """
    items = Item.query.join(Location).filter(
        Item.is_deleted
    ).order_by(
        Location.page_no,
        Item.x,
        Item.y
    ).all()
    return render_template('deleted.html', items=items)


@app.route('/test/')
def test_items():
    """For displaying tests on a subset of items"""
    low_attr_items = db.session.query(
        Item,
        db.func.count(Modifier.id),
    ).join(Modifier, Location).group_by(
        Item,
        Location.page_no,
    ).filter(
        Modifier.is_implicit == false(),
        *in_page_group("rare")
    ).having(
        db.func.count(Modifier.id) <= 4
    ).order_by(Location.page_no)

    items = []
    for item, _ in low_attr_items:
        # keep items with double resist mods
        if sum(1 for m in item.explicit_mods
               if "Resist" in m.value) >= 2:
            items.append(item)

    return render_template(
        'test.html',
        title="<= 4 Explicit Mods",
        items=items,
    )


class AdvancedSearchView(MethodView):
    """allows for a more fine grained search of items"""
    def get(self):
        max_lvl = Requirement.query.filter(Requirement.name == "Level").\
                order_by(Requirement.value.desc()).first().value
        return render_template('advanced_search.html', max_lvl=max_lvl)

    def handle_socket_str(self, val):
        # create the regex
        SOCKET_RE = r'[BGR]*'
        val = list(zip(sorted(val), itertools.repeat(SOCKET_RE)))
        val = SOCKET_RE + ''.join(itertools.chain(*val))
        return [Item.socket_str.op('~')(val)]

    def handle_item_name(self, val):
        return [Item.name.ilike('%%%s%%' % val)]

    def handle_item_type(self, val):
        return [Item.type.ilike('%%%s%%' % val)]

    def handle_item_type_select(self, val):
        #  if slug is not None:
        #      if slug.lower() == "misc":
        #          item_types = constants.BELTS
        #          item_types.update(constants.QUIVERS)
        #      else:
        #          item_types = getattr(constants, slug.upper()).keys()
        #      items = items.filter(
        #          Item.type.in_(item_types)
        #      )
        pass

    def handle_item_title(self, val):
        return [Item.name.ilike('%%%s%%' % val) |
                Item.type.ilike('%%%s%%' % val)]

    def handle_is_chromatic(self, val):
        return [Item.socket_str.op('~')(CHROMATIC_RE)]

    def handle_is_socketed(self, val):
        return [Item.num_sockets > 1]

    def handle_rarity(self, val):
        return [Item.rarity.in_(x.lower() for x in val)]

    def handle_sockets(self, val):
        return [Item.num_sockets.in_(int(x) for x in val)]

    def handle_sockets_links(self, val):
        return [Item.socket_str.op('~')(r"[BGR]{%s,}" % max(val))]

    def handle_level(self, val):
        return [
            (~Item.requirements.any()) |
            ((Requirement.name == "Level") & (Requirement.value <= int(val)))
        ]

    def post(self):
        # generates the query in parts
        filter_args = []
        # dispatch the handling of each funtion to the appropriate methods
        for k, v in list(request.form.items()):
            # special handling for multi selects
            if k.endswith("_multi"):
                v = [x.strip() for x in request.form.getlist(k)]
                v = [x for x in v if x]
                k = k[:-6]
            else:
                v = v.strip()
            if v:
                handler = getattr(self, "handle_%s" % k)
                filter_args.extend(handler(v))

        items = Item.query.join(Location).filter(
            Item.is_identified,
            *filter_args
        ).order_by(
            Location.page_no,
            Item.x,
            Item.y
        ).all()
        return render_template('items.html', items=items)

app.add_url_rule('/advanced_search/',
                 view_func=AdvancedSearchView.as_view('adv_search'))


@app.route('/browse/<slug>/')
def browse(slug):
    """renders all the details of a location"""
    loc = Location.query.filter(
        db.func.lower(Location.name) == slug.lower()
    ).one()
    items = Item.query.filter(Item.location == loc).order_by(
        Item.x, Item.y
    ).all()

    return render_template('browse.html', items=items, title=str(loc))


class LevelsView(View):
    """sorts the items into bins of levels"""
    levels_url = "levels"
    levels_slug_url = "levels_slug"
    title = "Levels"

    def item_filters(self):
        """returns a list of filters for the items"""
        return [
            Item.rarity != "normal",
            Item.rarity != "magic",
        ]

    def get_items(self):
        """returns a list of items to be rendered"""
        items = Item.query.join(Item.location).filter(
            Item.is_identified,
            ~Location.is_character,
            *self.item_filters()
        ).order_by(
            Location.page_no,
            Item.x,
            Item.y
        )
        return items

    def dispatch_request(self, slug):
        items = self.get_items()
        if slug is not None:
            if slug.lower() == "misc":
                item_types = constants.BELTS
                item_types.update(QUIVERS)
            else:
                item_types = list(getattr(constants, slug.upper()).keys())
            items = items.filter(
                Item.type.in_(item_types)
            )

        return render_template('levels.html',
            levels_url=self.levels_url,
            levels_slug_url=self.levels_slug_url,
            title=self.title,
            all_items=items.all(),
        )

app.add_url_rule('/levels/', view_func=LevelsView.as_view('levels'),
                 defaults={"slug": None})
app.add_url_rule('/levels/<slug>/',
                 view_func=LevelsView.as_view('levels_slug'))


class PurgeView(View):
    """
    Displays all the items that should be removed
    """
    def __init__(self):
        super(PurgeView, self).__init__()

    def get_duplicate_rares(self):
        """rare items sharing the same type and level reqs in the rare pages"""
        duplicate_rares = []
        rare_items = Item.query.join(Location).filter(
            Item.is_identified,
            *in_page_group("rare")
        )
        grouped_items = group_items_by_level(rare_items)
        for level, items in grouped_items.items():
            grps = groupsortby(items, key=lambda x: x.item_group())
            for k, v in grps:
                if len(v) > 1:
                    v = sorted(v, key=lambda x: x.type)
                    duplicate_rares.extend(v)
        return duplicate_rares

    def get_non_rares(self):
        # non-rare items in rare pages
        return Item.query.join(Location).filter(
            Item.rarity != "rare",
            Item.is_identified,
            *in_page_group("rare")
        )

    def get_unidentified(self):
        # non-rare items in rare pages
        return Item.query.join(Location).filter(
            ~Item.is_identified,
        )

    def dispatch_request(self):
        context = {
            "non_rares": self.get_non_rares(),
            "unidentifieds": self.get_unidentified(),
        }
        # apply default ordering for the items
        for k, v in list(context.items()):
            context[k] = v.order_by(
                Location.id, Item.x, Item.y
            ).all()
        context["duplicate_rares"] = self.get_duplicate_rares()
        return render_template('purge.html', **context)
app.add_url_rule('/purge/', view_func=PurgeView.as_view('purge'))


class StatsView(View):
    """
    Displays a summary of all currency and crafting items
    """
    def get_currency_stats(self):
        currency_stats = defaultdict(int)
        items = Item.query.join(Property).filter(
            Property.name.startswith("Stack"),
            Item.is_identified,
        ).all()
        for item in items:
            # look for the stack property
            for p in item.properties:
                if p.name.startswith("Stack"):
                    # get the size of the stack
                    currency_stats[item.type] += int(p.value.split("/")[0])
                    break

        # handle shards and fragments
        currency_stats["Scroll of Wisdom"] += \
                currency_stats.pop("Scroll Fragment", 0) / 20.0
        currency_stats["Orb of Transmutation"] += \
                currency_stats.pop("Transmutation Shard", 0) / 20.0
        currency_stats["Orb of Alteration"] += \
                currency_stats.pop("Alteration Shard", 0) / 20.0
        currency_stats["Orb of Alchemy"] += \
                currency_stats.pop("Alchemy Shard", 0) / 20.0

        currencies = []
        for name, effect in list(constants.CURRENCIES.items()):
            if name not in currency_stats:
                continue
            # format the total string
            total = str(currency_stats[name])
            if int(currency_stats[name]) != currency_stats[name]:
                total = "%.2f" % currency_stats[name]

            currencies.append({
                "name": name,
                "effect": effect,
                "total": total,
            })
        return currencies

    def get_item_rarity_stats(self):
        stats = db.session.query(
            db.func.count(Item.id),
            Item.rarity,
        ).filter(Item.is_identified).group_by(Item.rarity).all()
        return {
            "rarities": sorted(stats, reverse=True),
            "rarities_total": sum(s[0] for s in stats),
        }

    def get_item_socket_stats(self):
        stats = db.session.query(
            Item.num_sockets,
            db.func.count(Item.id),
        ).filter(Item.is_identified).group_by(Item.num_sockets).all()
        return {
            "item_sockets": sorted(stats, reverse=True),
            "item_sockets_total": sum(s[1] for s in stats),
        }

    def get_item_socket_links_stats(self):
        stats = db.session.query(
            # first instance of space, since the strings are sorted in order
            # of length
            db.func.strpos(Item.socket_str, " ").label("link_length"),
            db.func.count(Item.id),
        ).filter(Item.is_identified).group_by("link_length").all()

        return {
            "item_sockets_links": sorted(stats, reverse=True),
            "item_sockets_links_total": sum(s[1] for s in stats),
        }

    def get_gem_stats(self):
        # get the gems into a dict for easier searching

        gems = Item.query.join(Item.requirements).filter(
            Item.properties.any(name="Experience")
        ).all()

        all_gems = {"B": [], "G": [], "R": []}
        for gem_name, count in list(Counter(g.type for g in gems).items()):
            # look for info for the corresponding gem
            gval = normfind(GEMS, gem_name)

            # find the first of the gem for popover
            for g in gems:
                if g.type == gem_name:
                    gval["sample"] = g
                    gval["count"] = count
                    all_gems[gval["color"]].append(gval)
                    break
            else:
                raise IndexError

        return {
            "all_gems": {k: sorted(v, key=lambda x: -x["count"]) for
                        k, v in list(all_gems.items())}
        }

    def dispatch_request(self):
        context = {
            "currencies": self.get_currency_stats()
        }
        context.update(self.get_item_rarity_stats())
        context.update(self.get_item_socket_stats())
        context.update(self.get_item_socket_links_stats())
        context["all_gems"] = {}
        # context.update(self.get_gem_stats())

        return render_template('stats.html', **context)
app.add_url_rule('/', view_func=StatsView.as_view('stats'))


if __name__ == '__main__':
    app.run(debug=True, port=8000)
