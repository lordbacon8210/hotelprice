# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# 如何实现item嵌套
# https://www.it1352.com/1504955.html

import scrapy


# 酒店信息
class hotelItem(scrapy.Item):
    hotel_name = scrapy.Field()
    hotel_address = scrapy.Field()
    rooms_info = scrapy.Field()


# 房间信息
class roomItem(scrapy.Item):
    room_name = scrapy.Field()
    room_description = scrapy.Field()
    details_info = scrapy.Field()


# 房间细节
class detailItem(scrapy.Item):
    bed = scrapy.Field()
    break_fast = scrapy.Field()
    gov = scrapy.Field()
    price = scrapy.Field()

