import json
from typing import Generator

import scrapy
from scrapy import Request, Spider
from scrapy.http import Response


class OffersSpider(scrapy.Spider):
    name = "offers"
    price_max = "&price_max=600"
    start_urls = [
        "https://www.airbnb.com/s/Tbilisi--Georgia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&monthly_start_date=2023-09-01&monthly_length=3&price_filter_input_type=0&price_filter_num_nights=5&channel=EXPLORE&query=Tbilisi%2C%20Georgia&date_picker_type=flexible_dates&flexible_trip_lengths%5B%5D=one_month&flexible_trip_dates%5B%5D=september&adults=0" + price_max]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total = 0

    def parse(self, response: Response):
        script: str = response.css("script#data-deferred-state::text").get()
        data: dict = json.loads(script).get("niobeMinimalClientData")[0][
            1].get("data")
        gen_search: Generator = self.__gen_dict_extract("searchResults", data)
        result: list = next(gen_search)

        gen_pagination: Generator = self.__gen_dict_extract("nextPageCursor",
                                                            data)
        next_page: str = next(gen_pagination)
        if next_page:
            url: str = self.start_urls[0] + f"&cursor={next_page}"
            request: Request = response.follow(url, callback=self.parse)
            yield request

        for room in result:
            if x := room.get("listing"):
                print(x.get("id"))

            if y := room.get("listingParamOverrides"):
                print(y.get("checkin"), y.get("checkout"), sep=" --> ")

            try:
                gen_price = self.__gen_dict_extract("discountedPrice", room)
                price = next(gen_price)
                print(price)
            except StopIteration:
                print("error")



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

    def closed(self, spider: Spider):
        print(self.total)
