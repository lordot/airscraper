import json
import re
from typing import Generator

import scrapy
from scrapy import Request, Spider
from scrapy.http import Response

from notificator.items import RoomItem


class OffersSpider(scrapy.Spider):
    name = "offers"
    price_max = "&price_max=400"
    start_urls = [
        "https://www.airbnb.com/s/Tbilisi--Georgia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&monthly_start_date=2023-09-01&monthly_length=3&price_filter_input_type=0&price_filter_num_nights=5&channel=EXPLORE&query=Tbilisi%2C%20Georgia&date_picker_type=flexible_dates&flexible_trip_lengths%5B%5D=one_month&flexible_trip_dates%5B%5D=september&adults=0" + price_max]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse(self, response: Response):
        script: str = response.css("script#data-deferred-state::text").get()
        data: dict = json.loads(script).get("niobeMinimalClientData")[0][
            1].get("data")
        result: list = data["presentation"]["explore"]["sections"]["sectionIndependentData"]["staysSearch"]["searchResults"]

        gen_pagination: Generator = self.__gen_dict_extract("nextPageCursor",
                                                            data)
        next_page: str = next(gen_pagination)
        if next_page:
            url: str = self.start_urls[0] + f"&cursor={next_page}"
            request: Request = response.follow(url, callback=self.parse)
            yield request

        item = RoomItem()
        for room in result:
            item.clear()

            listening = room.get("listing")
            if listening:
                item["id"] = listening.get("id")
                try:
                    match = re.match(r"^(.*) \((.*)\)",
                                     listening.get("avgRatingLocalized"))
                    item["rate"] = float(match.group(1))
                    item["reviews"] = int(match.group(2))
                except (TypeError, AttributeError):
                    pass
            else:
                break

            params = room.get("listingParamOverrides")
            if params:
                item["checkin"] = params.get("checkin")
                item["checkout"] = params.get("checkout")

            for key in ["discountedPrice", "originalPrice", "price"]:
                try:
                    gen_price = self.__gen_dict_extract(key, room)
                    price = next(gen_price)
                    while not price:
                        price = next(gen_price)
                    item["price"] = price
                    break
                except StopIteration:
                    continue

            yield item

    def __gen_dict_extract(self, key: str, var: dict):
        if hasattr(var, 'items'):
            for k, v in var.items():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    for result in self.__gen_dict_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self.__gen_dict_extract(key, d):
                            yield result
