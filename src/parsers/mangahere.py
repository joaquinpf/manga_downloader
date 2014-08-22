#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ###################

import re
import string
import time

# ####################

from parsers.base import SiteParserBase
from util import get_source_code

# ####################


class MangaHere(SiteParserBase):
    re_get_series = re.compile('a href="http://.*?mangahere.*?/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
    # re_getSeries = re.compile('a href="/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
    # re_get_chapters = re.compile('"(.*?Ch.[\d.]*)[^"]*","([^"]*)"')
    re_get_image = re.compile('<img src="([^"]*.jpg)[^"]*"')
    re_get_max_pages = re.compile('var total_pages = ([^;]*?);')
    re_non_decimal = re.compile(r'[^\d.]+')

    def __init__(self, options):
        SiteParserBase.__init__(self, options)

    def parse_site(self):
        """
        Parses list of chapters and URLs associated with each one for the given manga and site.
        """

        print('Beginning MangaHere check: %s' % self.options.manga)

        # jump straight to expected URL and test if manga removed
        url = 'http://www.mangahere.com/manga/%s/' % fix_formatting(self.options.manga)
        if self.options.verbose_FLAG:
            print(url)
        source = get_source_code(url, self.options.proxy)

        if source is None or 'the page you have requested can' in source:
            # do a 'begins-with' search, then a 'contains' search
            url = 'http://www.mangahere.com/search.php?name=%s' % '+'.join(self.options.manga.split())
            if self.options.verbose_FLAG:
                print(url)

            try:
                source = get_source_code(url, self.options.proxy)
                if 'Sorry you have just searched, please try 5 seconds later.' in source:
                    print('Searched too soon, waiting 5 seconds...')
                    time.sleep(5)

                series_results = []
                if source is not None:
                    series_results = MangaHere.re_get_series.findall(source)

                if 0 == len(series_results):
                    url = 'http://www.mangahere.com/search.php?name=%s' % '+'.join(self.options.manga.split())
                    if self.options.verbose_FLAG:
                        print(url)
                    source = get_source_code(url, self.options.proxy)
                    if source is not None:
                        series_results = MangaHere.re_get_series.findall(source)

            # 0 results
            except AttributeError:
                raise self.MangaNotFound('It doesn\'t exist, or cannot be resolved by autocorrect.')
            else:
                keyword = self.select_from_results(series_results)
                if self.options.verbose_FLAG:
                    print ("Keyword: %s" % keyword)
                url = 'http://www.mangahere.com/manga/%s/' % keyword
                if self.options.verbose_FLAG:
                    print(url)
                source = get_source_code(url, self.options.proxy)

        else:
            # The Guess worked
            keyword = fix_formatting(self.options.manga)
            if self.options.verbose_FLAG:
                print ("Keyword: %s" % keyword)

        # other check for manga removal if our initial guess for the name was wrong
        if 'it is not available in.' in source:
            raise self.MangaNotFound('It has been removed.')

        # that's nice of them
        # url = 'http://www.mangahere.com/cache/manga/%s/chapters.js' % keyword
        # source = getSourceCode(url, self.proxy)

        # chapters is a 2-tuple
        # chapters[0] contains the chapter URL
        # chapters[1] contains the chapter title

        is_chapter_only = False

        # can't pre-compile this because relies on class name
        re_get_chapters = re.compile(
            'a.*?href="http://.*?mangahere.*?/manga/%s/(v[\d]+)/(c[\d]+(\.[\d]+)?)/[^"]*?"' % keyword)
        self.chapters = re_get_chapters.findall(source)
        if not self.chapters:
            if self.options.verbose_FLAG:
                print ("Trying chapter only regex")
            is_chapter_only = True
            re_get_chapters = re.compile(
                'a.*?href="http://.*?mangahere.*?/manga/%s/(c[\d]+(\.[\d]+)?)/[^"]*?"' % keyword)
            self.chapters = re_get_chapters.findall(source)

        # Sort chapters by volume and chapter number. Needed because next chapter isn't always accurate.
        self.chapters = sorted(self.chapters, cmp=chapter_compare)

        lower_range = 0

        if is_chapter_only:
            for i in range(0, len(self.chapters)):
                if self.options.auto:
                    if self.options.lastDownloaded == self.chapters[i][0]:
                        lower_range = i + 1

                ch_number = self.re_non_decimal.sub('', self.chapters[i][0])
                self.chapters[i] = (
                    'http://www.mangahere.com/manga/%s/%s' % (keyword, self.chapters[i][0]), self.chapters[i][0],
                    ch_number)

        else:
            for i in range(0, len(self.chapters)):

                ch_number = self.re_non_decimal.sub('', self.chapters[i][1])
                self.chapters[i] = (
                    'http://www.mangahere.com/manga/%s/%s/%s' % (keyword, self.chapters[i][0], self.chapters[i][1]),
                    self.chapters[i][0] + "." + self.chapters[i][1], ch_number)
                if self.options.auto:
                    if self.options.lastDownloaded == self.chapters[i][1]:
                        lower_range = i + 1

        upper_range = len(self.chapters)

        # Validate whether the last chapter is a
        if self.options.verbose_FLAG:
            print(self.chapters[upper_range - 1])
            print("Validating chapter: %s" % self.chapters[upper_range - 1][0])
        source = get_source_code(self.chapters[upper_range - 1][0], self.options.proxy)

        if ('not available yet' in source) or ('Sorry, the page you have requested can’t be found' in source):
            # If the last chapter is not available remove it from the list
            del self.chapters[upper_range - 1]
            upper_range -= 1

        # which ones do we want?
        if not self.options.auto:
            for i in range(0, upper_range):
                if is_chapter_only:
                    print('(%i) %s' % (i + 1, self.chapters[i][0]))
                else:
                    print('(%i) %s' % (i + 1, self.chapters[i][1]))

            self.chapters_to_download = self.select_chapters(self.chapters)
        # XML component
        else:
            if lower_range == upper_range:
                raise self.NoUpdates

            for i in range(lower_range, upper_range):
                self.chapters_to_download.append(i)
        return

    def download_chapter(self, download_thread, max_pages, url, manga_chapter_prefix, current_chapter):
        for page in range(1, max_pages + 1):
            if self.options.verbose_FLAG:
                print(self.chapters[current_chapter][1] + ' | ' + 'Page %i / %i' % (page, max_pages))

            page_url = '%s/%i.html' % (url, page)
            self.download_image(download_thread, page, page_url, manga_chapter_prefix)


def chapter_compare(x, y):
    non_decimal = re.compile(r'[^\d.]+')

    x_vol = float(non_decimal.sub('', x[0]))
    y_vol = float(non_decimal.sub('', y[0]))
    if x_vol != y_vol:
        return 1 if x_vol > y_vol else -1

    if not x[1] or not y[1]:
        return 0

    x_chapter = float(non_decimal.sub('', x[1]))
    y_chapter = float(non_decimal.sub('', y[1]))
    if x_chapter != y_chapter:
        return 1 if x_chapter > y_chapter else -1

    return 0


def fix_formatting(s):

    for i in string.punctuation:
        s = s.replace(i, " ")

    p = re.compile('\s+')
    s = p.sub(' ', s)

    s = s.lower().strip().replace(' ', '_')
    return s
