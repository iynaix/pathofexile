import csv
import time

from scrapy.spiders import Spider
from scrapy.selector import Selector


class PoEex(Spider):
    name = "poeex"
    allowed_domains = ["poeex.info"]
    start_urls = ["http://poeex.info/"]

    def parse(self, response):
        sel = Selector(response)
        # extract the updated time
        dt = sel.css("div.disclaimer::text").extract()[-1]
        dt = dt.split(":").pop().strip()
        dt = time.strptime(dt, "%B %d, %Y")
        dt = time.strftime("%Y%m%d", dt)

        # extract the currency data
        rows = list(sel.css("table#currencyRateTable tr"))
        with open("poeex.csv", "wb") as fp:
            writer = csv.writer(fp)

            header = rows[0].xpath("td/img/@alt").extract()
            writer.writerow([''] + header)

            for row_no, row in enumerate(rows[1:]):
                row = [header[row_no]] + row.xpath("td/text()").extract()
                row[row_no + 1:row_no + 1 + 2] = ["1:1"]
                writer.writerow(row)

            writer.writerow([dt])
