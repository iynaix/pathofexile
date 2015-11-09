from scrapy import Spider, Request


class GamepediaSpider(Spider):
    name = "gamepedia"
    allowed_domains = ["pathofexile.gamepedia.com"]

    start_urls = [
        "http://pathofexile.gamepedia.com/List_of_quivers",
    ]

    def table_extractor(self, table):
        ret = []
        for row in table.xpath("tr"):
            cells = [s.strip() for s in row.css("td *::text").extract()]
            if not cells:
                continue
            ret.append(cells)
        return ret

    def parse(self, resp):
        headers = resp.css("h2 span.mw-headline::text").extract()
        tables = resp.css("table.wikitable")

        ret = {}
        for header, table in zip(headers, tables):
            ret[header] = self.table_extractor(table)
        return ret


class GamepediaUniqueSpider(Spider):
    name = "gamepedia_unique"
    allowed_domains = ["pathofexile.gamepedia.com"]

    start_urls = [
        "http://pathofexile.gamepedia.com/List_of_unique_items"
    ]

    def table_extractor(self, table):
        ret = []
        for row in table.xpath("tr"):
            cells = [s.strip() for s in row.css("td *::text").extract()]
            if not cells:
                continue
            ret.append(cells)
        return ret

    def parse(self, resp):
        unique_urls = set()
        for link in resp.css("table td a"):
            url = link.xpath("@href").extract()[0]
            if url.startswith("/List_of_unique_"):
                unique_urls.add(url)

        for unique_url in unique_urls:
            req = Request(
                resp.urljoin(unique_url),
                callback=self.parse_unique_page
            )
            req.meta["title"] = unique_url[len("/List_of_unique_"):]
            yield req

    def parse_unique_page(self, resp):
        page_header = resp.meta["title"]
        headers = resp.css("h2 span.mw-headline::text").extract()
        tables = resp.css("table.wikitable")

        if headers:
            ret = {page_header: {}}
            for header, table in zip(headers, tables):
                ret[page_header][header] = self.table_extractor(table)
        else:
            ret = {page_header: []}
            for table in tables:
                ret[page_header].append(self.table_extractor(table))
        return ret
