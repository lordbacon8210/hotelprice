# coding=utf-8

from scrapy import Request, Spider
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq

from hotel_price.items import roomItem, detailItem, hotelItem


class QunarSpider(Spider):
    name = 'qunar'
    allowed_domains = ['hotel.qunar.com']
    start_url = 'http://hotel.qunar.com'

    def __init__(self):

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument("blink-settings=imagesEnabled=false")

        self.browser = webdriver.Chrome(executable_path=r'E:\Program Files (x86)\python3.7\Scripts\chromedriver.exe',
                                        chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browser, 20)

        # firefox_options = Options()
        # firefox_options.add_argument('-headless')
        # firefox_options.set_preference('permissions.default.image', 2)
        # firefox_options.set_preference("network.http.use-cache", False)
        # firefox_options.set_preference("browser.cache.memory.enable", False)
        # firefox_options.set_preference("browser.cache.disk.enable", False)
        # firefox_options.set_preference("browser.sessionhistory.max_total_viewers", 3)
        # firefox_options.set_preference("network.dns.disableIPv6", True)
        # firefox_options.set_preference("Content.notify.interval", 750000)
        # firefox_options.set_preference("content.notify.backoffcount", 3)
        # self.browser = webdriver.Firefox(executable_path=r'E:\Program Files (x86)\python3.7\Scripts\geckodriver.exe',
        #                                  options=firefox_options)

    # ???????????????????????????????????????????????????????????????????????????
    def start_requests(self):
        start_time = self.settings.get('START_TIME')
        end_time = self.settings.get('END_TIME')
        city = self.settings.get('CITY')
        max_page = int(self.settings.get('MAX_PAGE'))
        print('?????????????????????????????????')
        self.browser.get(self.start_url)

        try:
            inputs = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'inputText'))
            )

            input_city = inputs[0]
            input_start_date = inputs[1]
            input_end_date = inputs[2]

            # ????????????
            input_city.clear()
            input_city.send_keys(city)
            time.sleep(1)
            input_city.send_keys(Keys.ENTER)
            # ??????????????????
            input_start_date.click()
            input_start_date.send_keys(Keys.CONTROL + 'a')
            input_start_date.send_keys(Keys.BACKSPACE)
            input_start_date.send_keys(start_time)
            time.sleep(1)
            # ??????????????????
            input_end_date.click()
            input_end_date.send_keys(Keys.CONTROL + 'a')
            input_end_date.send_keys(Keys.BACKSPACE)
            input_end_date.send_keys(end_time)
            time.sleep(1)
            # click_search = browser.find_element_by_class_name('main')
            print('??????????????????????????????')
            click_search = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'main'))
            )
            click_search.click()
        except Exception as ex:
            print("????????????????????? %s" % ex)

        try:
            print('??????????????????????????????')
            self.wait.until(
                EC.presence_of_element_located((By.ID, 'hotel_lst_body'))
            )
            print('???????????????1?????????')
            hotels = self.get_hotels()
            for hotel in hotels:
                url_hotel = self.start_url + hotel['url'] + '?fromDate=' + start_time + '&todate' + end_time
                yield Request(url=url_hotel, callback=self.parse,dont_filter=True)

            for current_page in range(2, max_page+1):
                print('?????????????????????')
                next_page = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.next'))
                )
                next_page.click()
                print('???????????????' + str(current_page) + '?????????')
                self.wait.until(
                    EC.presence_of_element_located((By.ID, 'hotel_lst_body'))
                )
                hotels = self.get_hotels()
                for hotel in hotels:
                    url_hotel = self.start_url + hotel['url'] + '?fromDate=' + start_time + '&todate' + end_time
                    print(url_hotel)
                    yield Request(url=url_hotel, callback=self.parse, dont_filter=True)
        except Exception as ex:
            print("????????????????????????????????? %s" % ex)

    def get_hotels(self):
        hotels = []
        doc = pq(self.browser.page_source)
        items = doc('#hotel_lst_body .item').items()
        for item in items:
            hotel = {
                'name': item.find('.hotel-name').text(),
                'adress': item.find('.adress').text(),
                'url': item.find('.hotel-name').attr('href'),
                'price': item.find('.price_new').text()
            }
            hotels.append(hotel)
        return hotels

    # ?????????????????????????????????item
    def parse(self, response):
        print('??????????????????????????????')
        doc_rooms = pq(response.body)
        # ?????????????????????hotel_info ??????????????????
        html_hotel = doc_rooms('.name_cont')
        hotel_info = hotelItem()
        hotel_info['hotel_name'] = html_hotel.find('.name').text()
        hotel_info['hotel_address'] = html_hotel.find('.addr').text().replace('\ue65e????????????', '')

        # ??????????????????
        html_rooms = doc_rooms('.hotel_type_item').items()
        rooms_info = []
        details_info = []
        for room in html_rooms:
            room_info = roomItem()
            room_info['room_name'] = room('.words').text()
            room_info['room_description'] = room('.roomInforList').text()
            subjs = room('.subj').items()
            for subj in subjs:
                detail_info = detailItem()
                detail_info['bed'] = subj('.name').text()
                detail_info['break_fast'] = subj('.bread_fast').text()
                detail_info['gov'] = subj('.gov_words').text()
                detail_info['price'] = subj('.price_new').text()
                details_info.append(dict(detail_info))
            room_info['details_info'] = details_info
            rooms_info.append(dict(room_info))
        hotel_info['rooms_info'] = rooms_info
        yield hotel_info