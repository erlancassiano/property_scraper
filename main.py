import pageparser
import detailpageparser
import csvmanager
import selenium
import logging
from selenium import webdriver
import time
import argparse

argparser = argparse.ArgumentParser(description="Basic web crawler")
argparser.add_argument("--delay", help="Time interval during requests. defaults to 30")
argparser.add_argument("--output", help="Desired output path. defaults to output.csv")
args = argparser.parse_args()

# CONFIG
config = {}
config['DELAY'] = int(args.delay) if args.delay else 30
config['OUTPUT'] = args.output or 'output.csv'

# LOGGING
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info('Init parsing...')

driver = webdriver.Firefox(executable_path='./geckodriver')
driver.implicitly_wait(30)

url = 'https://www.vivareal.com.br/aluguel/distrito-federal/brasilia/'
city = 'Brasília'
uf = 'DF'

driver.get(url)

with open(config['OUTPUT'], 'a', newline='') as csvfile:
    csvwritter = csvmanager.get_csv_writter(csvfile)
    continue_parsing = True

    page_number = 1
    while continue_parsing:
        continue_parsing = False

        index_url = driver.current_url

        logger.info('Reading page %s', page_number)

        index_page_parser = pageparser.IndexPageParser(
            index_url,
            uf,
            city,
        )

        try:
            index_page_parser.parse()
            time.sleep(config['DELAY'])
        except Exception as e:
            logger.debug(
                'Failed to parse %s INDEX page, exiting...',
                index_url.page_url
            )
            raise e

        for detail_url in index_page_parser.get_detail_pages_urls():
            try:
                detail_page_parser = detailpageparser.DetailPageParser(
                    detail_url)

                detail_page_parser.parse()
                time.sleep(config['DELAY'])
            except Exception as e:
                logger.debug(
                    'Failed to parser %s DETAIL page, trying next page...',
                    detail_page_parser.page_url
                )
                logger.error(e)
                continue

            csvrow = {
                'UF': index_page_parser.uf,
                'cidade': index_page_parser.city,
            }

            csvrow.update(detail_page_parser.page_info())

            csvwritter.writerow(csvrow)

        next_link = driver.find_element_by_partial_link_text('Próxima')

        if next_link:
            next_page = next_link.get_attribute('data-page')
            if next_page != '':
                next_link_clicker = next_link.find_element_by_xpath('..')
                continue_parsing = True
                next_link_clicker.click()
                page_number = page_number + 1

logger.info('Crawling finished!')
