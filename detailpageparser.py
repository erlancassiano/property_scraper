from bs4 import BeautifulSoup
import requests
import re
import logging

logger = logging.getLogger(__name__)

constants = {
    'UNDER_CONSULT': 'Sob Consulta',
    'NOT_INFORMED': 'Não informado',
}

viva_real_domain = 'https://www.vivareal.com.br'


class DetailPageParser:
    def __init__(self, page_url):
        self.page_url = viva_real_domain+page_url
        self.parsing_complete = False

    def parse(self):
        if self.parsing_complete:
            raise Exception('Parsing already done')

        detail_page = requests.get(self.page_url)

        if detail_page.ok:
            soup = BeautifulSoup(detail_page.text, 'lxml')
            logger.info('Starting [%s] detail parsing...', self.page_url)

            breadcumbs_links = soup.find_all(class_='breadcrumb__item-name')
            neighborhood_breadcumb = breadcumbs_links[4] if breadcumbs_links else None
            if neighborhood_breadcumb and neighborhood_breadcumb.text is not None:
                self.neighborhood = neighborhood_breadcumb.text.strip()
            else:
                self.neighborhood = None

            area_tag = soup.find(class_='features__item--area')
            self.area = area_tag.span.text if area_tag.span else 'N/A'

            bedrooms_tag = soup.find(class_='features__item--bedroom')
            self.bedrooms = (bedrooms_tag.span.text
                             if bedrooms_tag.span else 'N/A')

            bathrooms_tag = soup.find(class_='features__item--bathroom')
            self.bathrooms = (bathrooms_tag.span.text
                              if bedrooms_tag.span else 'N/A')

            features_extra_tag = soup.find(class_='feature__extra-info')
            if features_extra_tag and features_extra_tag.text:
                has_suite = (True if 'suíte'
                             in features_extra_tag.text else False)
                if has_suite:
                    self.suites = features_extra_tag.text.strip()[0]
                else:
                    self.suites = 'N/A'
            else:
                self.suites = 'N/A'

            parking_tag = soup.find(class_='features__item--parking')
            self.parking = parking_tag.span.text if parking_tag.span else 'N/A'

            rent_tag = soup.find(class_='price__price-info js-price-sale')
            self.rent = rent_tag.text.replace('R$', '').replace(
                '/Mês', '').strip() if rent_tag else 'N/A'

            condominium_tag = soup.find(class_='condominium')
            self.condominium = condominium_tag.text.replace(
                'R$', '').strip() if condominium_tag else 'N/A'

            iptu_tag = soup.find(class_='iptu')
            self.iptu = iptu_tag.text.replace(
                'R$', '').strip() if iptu_tag else 'N/A'

            property_header_tag = soup.find(
                class_='title__title js-title-view'
            )
            property_type_re = re.compile(
                r'^((?P<property_type>.*?)( com \d{1,2} Quartos?)? para Alugar)'
            )
            if property_header_tag:
                property_header_text = property_header_tag.text.strip()
                re_result = property_type_re.match(property_header_text)
                if re_result and re_result.group('property_type'):
                    self.property_type = re_result.group(
                        'property_type'
                    ).strip().lower()
                else:
                    self.property_type = 'N/A'
            else:
                self.property_type = 'N/A'

            logger.info('complete')

            self.parsing_complete = True

    def page_info(self):
        if self.parsing_complete:
            return {
                'bairro': self.neighborhood,
                'tipo': self.property_type,
                'area': self.area,
                'quartos': self.bedrooms,
                'banheiros': self.bathrooms,
                'suites': self.suites,
                'vagas': self.parking,
                'aluguel': self.get_rent(),
                'condominio': self.get_condominium(),
                'iptu': self.get_iptu(),
            }
        raise Exception('Parsing not done yet')

    def get_rent(self):
        if self.rent == constants['UNDER_CONSULT']:
            return 'N/A'
        elif self.rent == 'N/A':
            return self.rent
        else:
            rent = self.rent.replace('.', '')
            return int(rent)

    def get_condominium(self):
        if self.condominium == constants['NOT_INFORMED']:
            return 'N/A'
        elif self.condominium == 'N/A':
            return self.condominium
        else:
            condominium = self.condominium.replace('.', '')
            return int(condominium)

    def get_iptu(self):
        if self.iptu == constants['NOT_INFORMED']:
            return 'N/A'
        elif self.iptu == 'N/A':
            return self.iptu
        else:
            iptu = self.iptu.replace('.', '')
            return int(iptu)
