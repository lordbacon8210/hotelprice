# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import codecs
import json
import os

from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter


class HotelPricePipeline:
    def __init__(self):
        settings = get_project_settings()
        start_time = settings['START_TIME']
        end_time = settings['END_TIME']
        city = settings['CITY']
        filename = 'results/' + 'qunar&' + city + '&' + start_time + 'to' + end_time + '.xml'
        if os.path.exists(filename):
            os.remove(filename)
        self.file = codecs.open(filename=filename, mode='w+', encoding='utf-8')

    def process_item(self, item, spider):
        try:
            print('开始保存酒店信息……')
            dict_hotel = dict(item)
            hotel_info = json.dumps(dict_hotel, ensure_ascii=False)
            self.file.write(hotel_info)
            self.file.write(',\n')
        except Exception as ex:
            print("保存酒店信息出现异常： %s" % ex)
