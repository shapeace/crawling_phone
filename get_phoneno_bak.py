#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "Terence Haejin Lee <shapeacelee@me.com>"
__date__ = "2021/09/14"
__modified__ = "2021/09/14"
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__license__ = "GPL"

import pandas as pd
from datetime import datetime
import re
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, Request


class GetPhoneno(object):
    def __init__(self):
        self.hostname = 'https://kr.christianitydaily.com'
        # self.url = 'https://kr.christianitydaily.com/address/'
        self.url = 'https://kr.christianitydaily.com/address/result.htm?findzip=&findminister=&findchurch=%EA%B5%90%ED%9A%8C%EB%AA%85%2B%EB%AA%A9%ED%9A%8C%EC%9E%90%EB%AA%85+%EB%98%90%EB%8A%94+%EA%B5%90%ED%9A%8C%EB%AA%85%EC%9C%BC%EB%A1%9C+%EA%B2%80%EC%83%89%ED%95%B4%EB%B3%B4%EC%84%B8%EC%9A%94+ex%29%EC%A0%9C%EC%9D%BC%EA%B5%90%ED%9A%8C'
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
        page = None
        html = urlopen(Request(url, headers=self.headers)).read().decode('utf8')
        soup = bs(html, "html.parser")
        item_thumbs = soup.find_all('td', class_='paging')
        for item_thumb in item_thumbs:
            base_url = item_thumb.find('a')
            if base_url:
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
    st = datetime.now()
    cls = GetPhoneno()
    url = cls.url
    results = []
    temp_cnt = 0
    limit = 10000
    region_infos = cls.get_region_urls(url)
    for region_info in region_infos:
        if temp_cnt > limit:
            break
        base_url = region_info['base_url']
        region = region_info['region']
        last_page = cls.get_address_last_page(base_url)
        if last_page is None:
            last_page = 1

        for page in range(int(last_page)):
            if temp_cnt > limit:
                break
            address_url = f'{base_url}&page={page + 1}'
            church_infos = cls.get_address_urls(address_url)
            for church_info in church_infos:
                if temp_cnt > limit:
                    break
                church_url = church_info['base_url']
                church_name = church_info['church_name']
                phone_infos = cls.get_phone_no(church_url)
                for phone_info in phone_infos:
                    temp_cnt += 1
                    if temp_cnt > limit:
                        break
                    phone_info = phone_info.replace('\r', '')
                    phone_info = phone_info.replace('\n', '')
                    phone_info = phone_info.replace('\t', '')
                    phone_info = phone_info.replace('\xa0', '')
                    regex1 = re.compile(r'(\d\d\d)')
                    regex2 = re.compile(r'\d\d\d-\d\d\d\d')
                    matchobj1 = regex1.search(phone_info)
                    matchobj2 = regex2.search(phone_info)
                    if matchobj1:
                        phone_no1 = matchobj1.group()
                    else:
                        phone_no1 = None

                    if matchobj2:
                        phone_no2 = matchobj2.group()
                    else:
                        phone_no2 = None

                    if phone_no1 and phone_no2:
                        result_list = []
                        phone_no = f'({phone_no1}) {phone_no2}'
                        result_list.append(region)
                        result_list.append(church_name)
                        result_list.append(phone_no)
                        print(f'{result_list}')
                        results.append(result_list)
    print(f'Laps: {datetime.now() - st}')
    df = pd.DataFrame(results, columns=['Region', 'Church Name', 'Phone No'])
    df.to_csv('phone_list.csv', index=False, encoding='utf8')
    # df.to_csv('phone_list.csv', index=False, encoding='cp949')
