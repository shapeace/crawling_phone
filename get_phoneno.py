#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "Terence Haejin Lee <shapeacelee@me.com>"
__date__ = "2021/09/14"
__modified__ = "2021/09/14"
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__license__ = "GPL"

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, Request


class GetPhoneno(object):
    def __init__(self):
        self.hostname = 'https://kr.christianitydaily.com'
        self.url = 'https://kr.christianitydaily.com/address/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
        html = urlopen(Request(self.url, headers=self.headers)).read().decode('utf8')
        self.soup = bs(html, "html.parser")

    def get_region_urls(self, url):
        region_infos = []
        html = urlopen(Request(url, headers=self.headers)).read().decode('utf8')
        soup = bs(html, "html.parser")
        item_thumbs = soup.find_all('ul', class_='stateall')
        for item_thumb in item_thumbs:
            base_url = item_thumb.find('a')
            region = base_url.text
            base_url = base_url.attrs['href']
            base_url = self.url + base_url
            region_info = {'base_url': base_url, 'region': region}
            region_infos.append(region_info)
        return region_infos

    def get_address_last_page(self, url):
        html = urlopen(Request(url, headers=self.headers)).read().decode('utf8')
        soup = bs(html, "html.parser")
        item_thumbs = soup.find_all('td', class_='paging')
        for item_thumb in item_thumbs:
            base_url = item_thumb.find('a')
            page = base_url.text
            page = page.replace('[', '').replace(']', '')
        return page

    def get_address_urls(self, url):
        church_infos = []
        html = urlopen(Request(url, headers=self.headers)).read().decode('utf8')
        soup = bs(html, "html.parser")
        item_thumbs = soup.find_all('td', class_='address_title_black')
        for item_thumb in item_thumbs:
            base_url = item_thumb.find('a')
            church_name = base_url.text
            church_name = church_name.replace('\r\n\t\t\t\t\t\t', '')
            base_url = base_url.attrs['href']
            base_url = self.url + base_url
            church_info = {'base_url': base_url, 'church_name': church_name}
            church_infos.append(church_info)
        return church_infos

    def get_phone_no(self, url):
        phone_infos = []
        html = urlopen(Request(url, headers=self.headers)).read().decode('utf8')
        soup = bs(html, "html.parser")
        item_thumbs = soup.find_all('div', class_='viewLeft')
        for item_thumb in item_thumbs:
            phone_info = item_thumb.find('li')
            phone_info = phone_info.text.strip()
            phone_infos.append(phone_info)
        return phone_infos


if __name__ == '__main__':
    cls = GetPhoneno()
    url = cls.url
    region_infos = cls.get_region_urls(url)
    for region_info in region_infos:
        base_url = region_info['base_url']
        region = region_info['region']
        last_page = cls.get_address_last_page(base_url)
        for page in range(int(last_page)):
            address_url = f'{base_url}&page={page + 1}'
            church_infos = cls.get_address_urls(address_url)
            for church_info in church_infos:
                church_url = church_info['base_url']
                church_name = church_info['church_name']
                phone_infos = cls.get_phone_no(church_url)
                for phone_info in phone_infos:
                    print(f'{region}, {church_name}, {phone_info}')
