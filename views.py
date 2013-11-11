from collections import defaultdict
from flask import render_template
from flask.views import View
from jinja2.filters import do_mark_safe

from app import app, db
from constants import CURRENCIES
from models import (Item, Location, Property, get_chromatic_stash_pages,
                    get_rare_stash_pages)

CHROMATIC_RE = r"B+G+R+"


def search_items():
    query = Item.query.filter(
        Item.socket_str.op('~')(CHROMATIC_RE),
        Item.is_identified,
    )
    return query.all()


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
    #join with hair spaces
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


@app.route('/')
def search_results():
    return render_template('items.html', items=search_items())


@app.route('/browse/<slug>/')
def browse(slug):
    """renders all the details of a location"""
    loc = Location.query.filter(Location.name == slug.capitalize()).one()
    items = Item.query.filter(Item.location == loc).order_by(
        Item.x, Item.y
    ).all()

    return render_template('browse.html', items=items, title=str(loc))


class PurgeView(View):
    """
    Displays all the items that should be removed
    """
    #non-chromatic items in chromatic pages
    def get_chromatic_purge(self):
        return Item.query.join(Location).filter(
            Location.page_no.in_(get_chromatic_stash_pages()),
            Item.socket_str.op('!~')(CHROMATIC_RE),
            Item.is_identified,
        )

    def get_rare_purge(self):
        #non-rare items in rare pages
        return Item.query.join(Location).filter(
            Location.page_no.in_(get_rare_stash_pages()),
            Item.rarity != "rare",
            Item.is_identified,
        )

    def get_unidentified(self):
        #non-rare items in rare pages
        return Item.query.join(Location).filter(
            Item.is_identified == False,
        )

    def dispatch_request(self):
        context = {
            "chromatics": self.get_chromatic_purge(),
            "rares": self.get_rare_purge(),
            "unidentifieds": self.get_unidentified(),
        }
        #apply default ordering for the items
        for k, v in context.iteritems():
            context[k] = v.order_by(
                Location.id, Item.x, Item.y
            ).all()

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
            #look for the stack property
            for p in item.properties.all():
                if p.name.startswith("Stack"):
                    #get the size of the stack
                    currency_stats[item.type] += int(p.value.split("/")[0])
                    break

        #handle shards and fragments
        currency_stats["Scroll of Wisdom"] += \
                currency_stats.pop("Scroll Fragment", 0) / 20.0
        currency_stats["Orb of Transmutation"] += \
                currency_stats.pop("Transmutation Shard", 0) / 20.0
        currency_stats["Orb of Alteration"] += \
                currency_stats.pop("Alteration Shard", 0) / 20.0
        currency_stats["Orb of Alchemy"] += \
                currency_stats.pop("Alchemy Shard", 0) / 20.0

        currencies = []
        for name, effect in CURRENCIES.iteritems():
            if name not in currency_stats:
                continue
            #format the total string
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
            "rarities": reversed(sorted(stats)),
            "rarities_total": sum(s[0] for s in stats),
        }

    def get_item_socket_stats(self):
        stats = db.session.query(
            Item.num_sockets,
            db.func.count(Item.id),
        ).filter(Item.is_identified).group_by(Item.num_sockets).all()
        return {
            "item_sockets": reversed(sorted(stats)),
            "item_sockets_total": sum(s[1] for s in stats),
        }

    def get_item_socket_links_stats(self):
        stats = db.session.query(
            #first instance of space, since the strings are sorted in order
            #of length
            db.func.strpos(Item.socket_str, " ").label("link_length"),
            db.func.count(Item.id),
        ).filter(Item.is_identified).group_by("link_length").all()

        return {
            "item_sockets_links": reversed(sorted(stats)),
            "item_sockets_links_total": sum(s[1] for s in stats),
        }

    def get_chromatics_stats(self):
        stats = db.session.query(
            #first instance of space, since the strings are sorted in order
            #of length
            db.cast(Item.socket_str.op('~')(CHROMATIC_RE), db.Integer).
            label("is_chromatic"),
            db.func.count(Item.id),
        ).filter(Item.is_identified).group_by("is_chromatic").all()

        return {
            "chromatics": reversed(sorted(stats)),
            "chromatics_total": sum(s[1] for s in stats),
        }

    def get_gem_stats(self):
        stats = defaultdict(int)

        gems = Item.query.join(Item.requirements).filter(
            Item.properties.any(name="Experience")
        )
        import q
        for gem in gems:
            stats[gem.type] += 1
        q(stats)

        return {
            # "chromatics": reversed(sorted(stats)),
            # "chromatics_total": sum(s[1] for s in stats),
        }

    def dispatch_request(self):
        context = {
            "currencies": self.get_currency_stats()
        }
        context.update(self.get_item_rarity_stats())
        context.update(self.get_item_socket_stats())
        context.update(self.get_item_socket_links_stats())
        context.update(self.get_chromatics_stats())
        context.update(self.get_gem_stats())

        return render_template('stats.html', **context)
app.add_url_rule('/stats/', view_func=StatsView.as_view('stats'))


if __name__ == '__main__':
    app.run(debug=True)
