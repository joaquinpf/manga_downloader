#!/usr/bin/env python

# ###################

import re
import string

# ####################

from plugins.base import SiteParserBase
from util.util import get_source_code, fix_formatting

# ####################

class MangaFox(SiteParserBase):
    re_get_series = re.compile('a href="http://.*?mangafox.*?/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
    # re_get_series = re.compile('a href="/manga/([^/]*)/[^"]*?" class=[^>]*>([^<]*)</a>')
    # re_get_chapters = re.compile('"(.*?Ch.[\d.]*)[^"]*","([^"]*)"')
    re_get_image = re.compile('"><img src="([^"]*)"')
    re_get_max_pages = re.compile('var total_pages=([^;]*?);')

    def __init__(self, options):
        SiteParserBase.__init__(self, options, 'http://mangafox.me')

    def get_manga_url(self):
        url = '%s/manga/%s/' % (self.base_url, fix_formatting(self.options.manga, '_', remove_special_chars=True, lower_case=True, use_ignore_chars=False))
        return url

    def parse_site(self, url):

        source, redirect_url = get_source_code(url, self.options.proxy, True)

        if redirect_url != url or source is None or 'the page you have requested cannot be found' in source:
            # Could not find the manga page by guessing
            # Use the website search
            url = '%s/search.php?name_method=bw&name=%s&is_completed=&advopts=1' % (self.base_url, '+'.join(
                self.options.manga.split()))
            if self.options.verbose_FLAG:
                print(url)
            try:
                source = get_source_code(url, self.options.proxy)
                series_results = []
                if source is not None:
                    series_results = MangaFox.re_get_series.findall(source)

                if 0 == len(series_results):
                    url = '%s/search.php?name_method=cw&name=%s&is_completed=&advopts=1' % (self.base_url, '+'.join(
                        self.options.manga.split()))
                    if self.options.verbose_FLAG:
                        print(url)
                    source = get_source_code(url, self.options.proxy)
                    if source is not None:
                        series_results = MangaFox.re_get_series.findall(source)

            # 0 results
            except AttributeError:
                raise self.MangaNotFound('It doesn\'t exist, or cannot be resolved by autocorrect.')
            else:
                keyword = self.select_from_results(series_results)
                if self.options.verbose_FLAG:
                    print ("Keyword: %s" % keyword)
                url = self.base_url % keyword
                if self.options.verbose_FLAG:
                    print ("URL: %s" % url)
                source = get_source_code(url, self.options.proxy)

                if source is None:
                    raise self.MangaNotFound('Search Failed to find Manga.')
        else:
            # The Guess worked
            keyword = fix_formatting(self.options.manga)
            if self.options.verbose_FLAG:
                print ("Keyword: %s" % keyword)

        if 'it is not available in Manga Fox.' in source:
            raise self.MangaNotFound('It has been removed.')

        # that's nice of them
        # url = 'http://mangafox.me/cache/manga/%s/chapters.js' % keyword
        # source = getSourceCode(url, self.proxy)
        # chapters is a 2-tuple
        # chapters[0] contains the chapter URL
        # chapters[1] contains the chapter title

        is_chapter_only = False

        # can't pre-compile this because relies on class name
        re_get_chapters = re.compile('a href="http://.*?mangafox.*?/manga/%s/(v[\d]+)/(c[\d]+)/[^"]*?" title' % keyword)
        self.chapters = re_get_chapters.findall(source)
        if not self.chapters:
            if self.options.verbose_FLAG:
                print ("Trying chapter only regex")
            is_chapter_only = True
            re_get_chapters = re.compile('a href="http://.*?mangafox.*?/manga/%s/(c[\d]+)/[^"]*?" title' % keyword)
            self.chapters = re_get_chapters.findall(source)

        self.chapters.reverse()

        lower_range = 0

        if is_chapter_only:
            for i in range(0, len(self.chapters)):
                if self.options.verbose_FLAG:
                    print("%s" % self.chapters[i])
                if not self.options.auto:
                    print('(%i) %s' % (i + 1, self.chapters[i]))
                else:
                    if self.options.lastDownloaded == self.chapters[i]:
                        lower_range = i + 1

                self.chapters[i] = (
                    '%s/manga/%s/%s' % (self.base_url, keyword, self.chapters[i]), self.chapters[i], self.chapters[i])

        else:
            for i in range(0, len(self.chapters)):
                if self.options.verbose_FLAG:
                    print("%s %s" % (self.chapters[i][0], self.chapters[i][1]))
                self.chapters[i] = (
                    '%s/manga/%s/%s/%s' % (self.base_url, keyword, self.chapters[i][0], self.chapters[i][1]),
                    self.chapters[i][0] + "." + self.chapters[i][1], self.chapters[i][1])
                if not self.options.auto:
                    print('(%i) %s' % (i + 1, self.chapters[i][1]))
                else:
                    if self.options.lastDownloaded == self.chapters[i][1]:
                        lower_range = i + 1

        upper_range = len(self.chapters)

        # which ones do we want?
        if not self.options.auto:
            self.chapters_to_download = self.select_chapters(self.chapters)
        # XML component
        else:
            if lower_range == upper_range:
                raise self.NoUpdates

            for i in range(lower_range, upper_range):
                self.chapters_to_download.append(i)
        return

    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        for page in range(1, max_pages + 1):
            page_url = '%s/%i.html' % (url, page)
            self.download_image(page, page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('MangaFox', MangaFox)