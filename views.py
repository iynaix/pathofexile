from collections import defaultdict, Counter
from decimal import Decimal
import itertools

from flask import request, render_template, send_from_directory, jsonify
from flask.views import View, MethodView
from jinja2 import contextfilter
from jinja2.filters import do_mark_safe
from sqlalchemy import false, not_, and_

from app import app, db, api
import resources
import constants
from models import (Item, Location, Property, Requirement, Modifier,
                    in_page_group, filter_item_type)
from utils import get_constant

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


@app.template_filter('macro')
@contextfilter
def call_macro_by_name(context, macro_name, *args, **kwargs):
    """
    Meta filter that allows the dynamic calling of a macro

    http://stackoverflow.com/questions/10629838/
    """
    return context.vars[macro_name](*args, **kwargs)


@app.context_processor
def main_context_processor():
    locations = {"stash": [], "characters": []}
    for loc in Location.query.order_by(Location.page_no).all():
        if loc.is_character:
            locations["characters"].append(loc)
        else:
            locations["stash"].append(loc)
    return dict(locations=locations)


def currency_stats():
    currencies = defaultdict(int)
    for item in Item.query.join(Property).filter(
        Item.rarity == "currency",
    ).all():
        # look for the stack property
        for p in item.properties:
            if p.name.startswith("Stack"):
                # get the size of the stack
                currencies[item.type_] += int(p.value.split("/")[0])
                break

    # handle shards and fragments
    currencies["Scroll of Wisdom"] += \
            Decimal(currencies.pop("Scroll Fragment", 0)) / 20
    currencies["Orb of Transmutation"] += \
            Decimal(currencies.pop("Transmutation Shard", 0)) / 20
    currencies["Orb of Alteration"] += \
            Decimal(currencies.pop("Alteration Shard", 0)) / 20
    currencies["Orb of Alchemy"] += \
            Decimal(currencies.pop("Alchemy Shard", 0)) / 20
    return currencies


def sufficient_resists(item, threshold):
    """
    determines if the given item has enough resists
    threshold is the absolute min value of each resist
    """
    resist_mods = [m for m in item.explicit_mods if "Resist" in m.normalized]

    # triple / quad resists, good to go
    if len(resist_mods) > 2:
        return True

    # check for min resist values
    return sum(
        1 for m in resist_mods
        if "All" not in m.normalized and m.values[0] > threshold
    ) >= 2


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
    return render_template(
        'list.html',
        items=items,
        title="To Delete",
        item_renderer="item_table",
    )


class LowModsView(View):
    """For displaying rare items with too few mods"""
    def get_items(self):
        low_attr_items = db.session.query(
            Item,
            db.func.count(Modifier.id),
        ).join(Modifier, Location).group_by(
            Item,
            Location.page_no,
        ).filter(
            Modifier.is_implicit == false(),
            # modifiers that we aren't interested in
            and_(
                not_(Modifier.normalized.like('%Light Radius%')),
                not_(Modifier.normalized.like('%Accuracy Rating%')),
                not_(Modifier.normalized.like('%Stun Recovery%')),
                not_(Modifier.normalized.like('%Reduced Attribute%')),
            ),
            *in_page_group("rare")
        ).having(
            db.func.count(Modifier.id) <= 4
        ).order_by(Location.page_no, Item.type_)

        # items = []
        # for item, _ in low_attr_items:
        #     # keep items with double resist mods
        #     if sum(1 for m in item.mods if "Resist" in m.normalized) >= 2:
        #         continue
        #     items.append(item)
        # return items
        return [item for item, _ in low_attr_items]

    def dispatch_request(self):
        items = self.get_items()
        items = [item for item in items if not sufficient_resists(item, 20)]

        return render_template(
            'list.html',
            title="< 5 Explicit Mods",
            items=items,
            item_renderer="item_table",
        )
app.add_url_rule('/low_mods/', view_func=LowModsView.as_view('low_mods'))


class LowRAJView(View):
    """For displaying rare items with too few mods"""
    def get_items(self):
        low_attr_items = db.session.query(
            Item,
            db.func.count(Modifier.id),
        ).join(Modifier, Location).group_by(
            Item,
            Location.page_no,
        ).filter(
            not_(Item.type_.like('%Jewel%')),
            Modifier.is_implicit == false(),
            # modifiers that we aren't interested in
            and_(
                not_(Modifier.normalized.like('%Light Radius%')),
                not_(Modifier.normalized.like('%Accuracy Rating%')),
                not_(Modifier.normalized.like('%Stun Recovery%')),
                not_(Modifier.normalized.like('%Reduced Attribute%')),
            ),
            *in_page_group("RAJ")
        ).having(
            db.func.count(Modifier.id) <= 3
        ).order_by(Location.page_no, Item.type_)

        # items = []
        # for item, _ in low_attr_items:
        #     # keep items with double resist mods
        #     if sum(1 for m in item.mods if "Resist" in m.normalized) >= 2:
        #         continue
        #     items.append(item)
        # return items
        return [item for item, _ in low_attr_items]

    def dispatch_request(self):
        items = self.get_items()
        items = [item for item in items if not sufficient_resists(item, 15)]

        return render_template(
            'list.html',
            title="Low RAJ",
            items=items,
            item_renderer="item_table",
        )
app.add_url_rule('/low_raj/', view_func=LowRAJView.as_view('low_raj'))


@app.route('/test/')
def test_items():
    """For displaying tests on a subset of items"""

    items = db.session.query(
        Item
    ).join(Modifier, Location).filter(
        Location.is_character == false(),
        Modifier.normalized.ilike("%increased rarity of items found%"),
        filter_item_type("helm"),
    ).all()

    return render_template(
        'list_ng.html',
        title="Filter by Item Type",
        items=items,
        item_renderer="item_table",
    )


@app.route('/dup_uniques/')
def duplicate_uniques():
    """Displays sellable uniques"""

    item_grps = defaultdict(list)
    for item in Item.query.filter(
        Item.rarity == "unique",
        *in_page_group("uniques")
    ).join(Location).all():
        item_grps[item.name].append(item)

    items = []
    for name, matches in item_grps.iteritems():
        if len(matches) <= 1:
            continue
        items.extend(matches)

    return render_template(
        'list.html',
        title="Duplicate Uniques",
        items=items,
        item_renderer="item_table",
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
        return [Item.type_.ilike('%%%s%%' % val)]

    def handle_item_type_select(self, val):
        #  if slug is not None:
        #      if slug.lower() == "misc":
        #          item_types = constants.BELTS
        #          item_types.update(constants.QUIVERS)
        #      else:
        #          item_types = getattr(constants, slug.upper()).keys()
        #      items = items.filter(
        #          Item.type_.in_(item_types)
        #      )
        pass

    def handle_item_title(self, val):
        return [Item.name.ilike('%%%s%%' % val) |
                Item.type_.ilike('%%%s%%' % val)]

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


class RatesView(View):
    """allows for a more fine grained search of items"""
    def dispatch_request(self):
        rates_str = request.args.get("q", None)
        if rates_str is None:
            return render_template('rates.html')
        else:
            try:
                return self.parse(rates_str)
            except LookupError as e:
                return jsonify(error=e.message), 500

    def parse(self, rates_str):
        from rates import parse_rate_str, PoeRatesProvider, PoeExProvider

        d = parse_rate_str(rates_str)

        given_rate = d["rate"]

        ret = {}
        providers = (PoeRatesProvider(), PoeExProvider())
        for provider in providers:
            actual_rate = provider.rate(d["from_orb"], d["to_orb"])

            # get the percentage profit or loss
            ret[str(provider)] = (given_rate - actual_rate) / actual_rate * 100
        return jsonify(**ret)


app.add_url_rule('/rates/', view_func=RatesView.as_view('rates'))


@app.route('/browse/<page_no>/')
def browse(page_no):
    """renders all the details of a location"""
    loc = Location.query.filter(Location.page_no == page_no).one()
    items = Item.query.filter(Item.location == loc).order_by(
        Item.x, Item.y
    ).all()

    return render_template(
        'list.html',
        items=items,
        title=str(loc),
        item_renderer="item_list",
    )


class LevelsView(View):
    """Sorts the items into bins of levels"""
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
                Item.type_.in_(item_types)
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

    def get_non_rares(self):
        # non-rare items in rare pages
        return Item.query.join(Location).filter(
            Item.rarity != "rare",
            Item.is_identified,
            *in_page_group("rare")
        )

    def get_non_uniques(self):
        # non-unique items in unique pages
        return Item.query.join(Location).filter(
            Item.rarity != "unique",
            Item.is_identified,
            *in_page_group("unique")
        )

    def get_unidentified(self):
        # non-rare items in rare pages
        return Item.query.join(Location).filter(
            ~Item.is_identified,
            *in_page_group("rare")
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
        return render_template('purge.html', **context)
app.add_url_rule('/purge/', view_func=PurgeView.as_view('purge'))


class StatsView(View):
    """
    Displays a summary of all currency and crafting items
    """

    def in_orb(self, currencies, target_orb):
        from rates import PoeRatesProvider

        poe_rates = PoeRatesProvider()
        total = 0
        for orb, cnt in currencies.iteritems():
            orb = orb.lower()
            orb = orb.replace("orb", "").replace(" of", "").replace("'", "")
            orb = orb.split()[0].strip()  # just need the first word

            try:
                total += (1 / poe_rates.rate(orb, target_orb) * cnt)
            # ignore, items like whetstones have no rates
            except LookupError:
                pass
        return total

    def get_gem_stats(self):
        # get the gems into a dict for easier searching

        gems = Item.query.filter(Item.rarity == "gem").all()
        return {
            "all_gems": Counter(g.type_ for g in gems).most_common()
        }

    def dispatch_request(self):
        currencies = currency_stats()
        context = {
            "currencies": currencies,
            "currencies_chaos": self.in_orb(currencies, "chaos"),
            "currencies_exalts": self.in_orb(currencies, "ex"),
        }
        context.update(self.get_gem_stats())

        return render_template('stats.html', **context)
app.add_url_rule('/', view_func=StatsView.as_view('stats'))


@app.route('/images/<path:filename>')
def base_static(filename):
    return send_from_directory(app.root_path + '/images/',
                               "%s?%s" % (filename, request.query_string))


if __name__ == '__main__':
    # set up the api
    api.add_resource(resources.ItemResource, '/api/items/<item_id>/')
    api.add_resource(resources.ItemListResource, '/api/items/')
    api.add_resource(resources.LocationResource, '/api/locations/<slug>/')
    api.add_resource(resources.LocationListResource, '/api/locations/')

    app.run(debug=True, port=8000)
