import logging
from datetime import date, timedelta
from urllib import parse

import scrapy

logging.basicConfig(filename='eska.log', level=logging.DEBUG)


def initialize_start_urls():

    BASE_URL = 'http://www.eskarock.pl/archiwum_playlist/'
    ONE_DAY = timedelta(days=1)
    start_date = date(2010, 9, 1)
    END_DATE = date.today()

    result = []
    while END_DATE >= start_date:

        result.append(
            BASE_URL + start_date.isoformat()
        )
        start_date = start_date + ONE_DAY
    return result


class EskaSpider(scrapy.Spider):
    name = 'eska'

    start_urls = initialize_start_urls()
    # start_urls = [
    #     'http://www.eskarock.pl/archiwum_playlist/2018-10-25',
    # ]


    def parse(self, response):

        date_played = response.url.split('/')[-1]

        for li in response.xpath('//div[@id="box-zagrane"]/ul//li'):
            title_band = li.xpath('div[@class="txt"]/div[@class="song"]/a')

            title = title_band.re_first(r'title="(.+?)"').replace('utwór ', '')

            artist = li.xpath(
                'div[@class="txt"]/div[@class="author"]/text()').extract_first(default='BRAK!')

            time_played = li.xpath(
                'div[@class="when"]/b').extract_first().replace('<b>', '').replace('</b>', '')

            song_data = {
                'title': title,
                'artist': artist,
                'date_played': date_played,
                'time_played': time_played
            }

            author_page = title_band.re_first(r'href="(.+?)"')
            
            if artist == 'BRAK!':
                request = scrapy.Request(
                    author_page, callback=self.parse_author_page, dont_filter=True)
                request.meta['song_data'] = song_data
                yield request
            else:
                yield song_data

    def parse_author_page(self, response):
        artist = response.xpath(
            '//h1[contains(@class, "main-title")]/span/text()').extract_first()

        song_data = response.meta['song_data']
        song_data['artist'] = artist.strip()
        yield song_data

    # def make_title_url_like(self, title):
    #     polish = list('ąęćęłóśżźĄĘĆĘŁÓŚ')
    #     _ascii = list('aeceloszz')

    #     for old, new in zip(polish, _ascii + _ascii):
    #         title = title.replace(old, new)

    #     title = title.replace(' ', '_')

    #     return parse.quote(title)
