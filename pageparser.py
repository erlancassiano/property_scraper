from bs4 import BeautifulSoup
from detailpageparser import DetailPageParser
import requests
import csv

viva_real_domain = 'https://www.vivareal.com.br'


class IndexPageParser:

    def __init__(
        self,
        page_url,
        uf,
        city,
    ):
        self.uf = uf
        self.city = city
        self.page_url = page_url
        self.parsing_complete = False
        self.detail_pages_urls = []

    def parse(self):
        index_page = requests.get(self.page_url)

        if index_page.ok:
            soup = BeautifulSoup(index_page.text, 'lxml')
            page_property_urls = soup.find_all(
                'a',
                class_='property-card__main-link'
            )
            detail_pages_urls = [
                anchor['href'] for anchor in page_property_urls
            ]
            self.detail_pages_urls.extend(detail_pages_urls)
            self.parsing_complete = True

    def get_detail_pages_urls(self):
        if self.parsing_complete:
            return self.detail_pages_urls
        else:
            raise Exception('Index parsing not done yet')
