from scrapy import Spider, Selector, Request
# from blessings import Terminal


class ItemDataSpider(Spider):
    name = "item_data"
    start_urls = [
        "http://www.pathofexile.com/item-data/",
    ]

    def parse(self, resp):
        sel = Selector(resp)

        for link in sel.css(".viewMore a"):
            txt = link.xpath("text()").extract_first().replace(
                                                    "View all ", "").strip()
            href = link.xpath("@href").extract_first()

            req = Request(
                resp.urljoin(href),
                callback=self.parse_data_page
            )
            req.meta["title"] = txt
            yield req

    def table_extractor(self, table):
        ret = []
        for row in table.xpath("tr"):
            cells = [s.strip() for s in row.xpath("td/text()").extract()]
            if not cells:
                continue
            ret.append(cells)
        return ret

    def parse_data_page(self, resp):
        # print t.green(resp.meta["title"].upper())
        headers = resp.css("h1::text").extract_first()

        tables = resp.css("table.itemDataTable")
        for header, table in zip(headers, tables):
            return {
                "header": header,
                "data": self.table_extractor(table),
            }

        # not standard item data list, probably a gem page, handle separately
        if not tables:
            return self.parse_gem_page(resp)

    def parse_gem_page(self, resp):
        ret = []
        gems = resp.css("div.content")
        for gem in gems:
            ret.append([
                gem.css("h1::text").extract_first(),
                gem.css("p::text").extract()[-1],
            ])

        # special case for support gem page
        if not gems:
            gems = resp.css("td.support-gem-desc p")
            # print gems.css("strong::text").extract()
            for gem in gems.css("::text").extract():
                lines = [x.strip() for x in gem.splitlines()]
                ret.extend([l for l in lines if l])

            # create from alternate elements
            ret = zip(ret[::2], ret[1::2])

        return {
            "header": resp.meta["title"],
            "data": ret,
        }
