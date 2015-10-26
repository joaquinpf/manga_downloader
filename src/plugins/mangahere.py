#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ###################

import re
import time

from bs4 import BeautifulSoup

# ####################

from plugins.base import SiteParserBase
from util.util import get_source_code, fix_formatting

# ####################

class MangaHere(SiteParserBase):
    re_get_series = re.compile('a href="http://.*?mangahere.*?/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
    re_get_image = re.compile('<img src="([^"]*.jpg)[^"]*"')
    re_get_max_pages = re.compile('var total_pages = ([^;]*?);')
    re_non_decimal = re.compile(r'[^\d.]+')

    def __init__(self, options):
        SiteParserBase.__init__(self, options, 'http://www.mangahere.co')

    def get_manga_url(self):
        url = '%s/manga/%s/' % (self.base_url, fix_formatting(self.options.manga, '_', remove_special_chars=True, lower_case=True, use_ignore_chars=False))
        return url

    def parse_chapters(self, url):

        source = get_source_code(url, self.options.proxy)

        if source is None or 'the page you have requested can' in source:
            # do a 'begins-with' search, then a 'contains' search
            url = '%s/search.php?name=%s' % (self.base_url, '+'.join(self.options.manga.split()))

            try:
                source = get_source_code(url, self.options.proxy)
                if 'Sorry you have just searched, please try 5 seconds later.' in source:
                    print('Searched too soon, waiting 5 seconds...')
                    time.sleep(5)

                series_results = []
                if source is not None:
                    series_results = MangaHere.re_get_series.findall(source)

                if 0 == len(series_results):
                    url = '%s/search.php?name=%s' % (self.base_url, '+'.join(self.options.manga.split()))
                    source = get_source_code(url, self.options.proxy)
                    if source is not None:
                        series_results = MangaHere.re_get_series.findall(source)

            # 0 results
            except AttributeError:
                raise self.MangaNotFound('It doesn\'t exist, or cannot be resolved by autocorrect.')
            else:
                keyword = self.select_from_results(series_results)
                url = '%s/manga/%s/' % (self.base_url, keyword)
                source = get_source_code(url, self.options.proxy)

        else:
            # The Guess worked
            keyword = fix_formatting(self.options.manga, '_', remove_special_chars=True, lower_case=True, use_ignore_chars=False)

        # other check for manga removal if our initial guess for the name was wrong
        if 'it is not available in' in source or "It's not available in" in source:
            raise self.MangaLicenced('It has been removed.')

        soup = BeautifulSoup(source, 'html.parser')
        r_chapters = soup.find("div", class_="detail_list").find_all("ul")[0].find_all('li')
        self.chapters = [[]]

        for row in r_chapters:
            info = row.find('a')
            c_url = info['href']
            title = info.get_text().strip()
            chapter = c_url[:-1] if c_url.endswith('/') else c_url
            chapter = chapter.split('/')
            chapter = chapter[-2] + '.' + chapter[-1] if chapter[-2].startswith('v') else chapter[-1]
            group = ''
            tu = (c_url, title, chapter, group)
            self.chapters.append(tu)

        if self.chapters == [[]]:
            raise self.MangaNotFound('Nothing to download.')

        #Remove [[]] and reverse to natural order
        self.chapters.pop(0)
		
        # Sort chapters by volume and chapter number. Needed because next chapter isn't always accurate.
        self.chapters = sorted(self.chapters, cmp=self.chapter_compare)

        # Validate whether the last chapter is available
        source = get_source_code(self.chapters[-1][0], self.options.proxy)

        if ('not available yet' in source) or ('Sorry, the page you have requested can’t be found' in source):
            # If the last chapter is not available remove it from the list
            del self.chapters[-1]


    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        for page in range(1, max_pages + 1):
            page_url = '%s/%i.html' % (url, page)
            self.parse_image_page(page, page_url, manga_chapter_prefix, max_pages, current_chapter)

    def chapter_compare(self, x, y):
        xp = x[2].split('.c')
        yp = y[2].split('.c')

        x_vol = float(self.re_non_decimal.sub('', xp[0])) if len(xp) == 2 else -1
        y_vol = float(self.re_non_decimal.sub('', yp[0])) if len(yp) == 2 else -1
        if x_vol != y_vol:
            return 1 if x_vol > y_vol else -1

        if not x[1] or not y[1]:
            return 0

        x_chapter = float(self.re_non_decimal.sub('', xp[1])) if len(xp) == 2 else float(self.re_non_decimal.sub('', xp[0]))
        y_chapter = float(self.re_non_decimal.sub('', yp[1])) if len(xp) == 2 else float(self.re_non_decimal.sub('', yp[0]))
        if x_chapter != y_chapter:
            return 1 if x_chapter > y_chapter else -1

        return 0

#Register plugin
def setup(app):
    app.register_plugin('MangaHere', MangaHere)