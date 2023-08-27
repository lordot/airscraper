import scrapy
from scrapy import Field


class RoomItem(scrapy.Item):
    id = Field()
    rate = Field(serializer=float)
    reviews = Field(serializer=int)
    price = Field()
    checkin = Field()
    checkout = Field()
