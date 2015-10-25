#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ###################

import re
import string
import time
import urllib

# ####################

from bs4 import BeautifulSoup
from plugins.base import SiteParserBase
from util.util import get_source_code, fix_formatting

# ####################

class MangaEden(SiteParserBase):
    re_get_image = re.compile(ur'<img.*id="mainImg".*src="//(.*)"/>')
    re_get_max_pages = re.compile(ur'<span id="pageInfo_page">.* of (.*)</div>')

    def __init__(self, options):
        SiteParserBase.__init__(self, options, 'http://www.mangaeden.com')

    def get_manga_url(self):
        url = '%s/en/en-manga/%s' % (self.base_url, fix_formatting(self.options.manga, '-', remove_special_chars=True, lower_case=True, use_ignore_chars=False))
        return url

    def parse_site(self, url):

        source = get_source_code(url, self.options.proxy)
        soup = BeautifulSoup(source, 'html.parser')
        r_chapters = soup.find("div", id="mangaPage").find("div", id="leftContent").find_all("tr")
        r_chapters.pop(0)
        self.chapters = [[]]

        for row in r_chapters:
            cells = row.find_all('td')
            chapter = str(row['id'])[1:]
            c_url = self.base_url + cells[0].a['href']
            title = cells[0].a.get_text().replace('\n', ' ').strip()
            group = cells[1].get_text().replace('\n', ' ').strip()
            tu = (c_url, title, chapter, group)
            self.chapters.append(tu)

        if self.chapters == [[]]:
            raise self.MangaNotFound('Nothing to download.')

        #Remove [[]] and reverse to natural order
        self.chapters.pop(0)
        self.chapters.reverse()

        # Look for first chapter that should be downloaded in auto mode
        lower_range = 0
        if self.options.auto:
            for row in range(0, len(self.chapters)):
                if self.options.lastDownloaded == self.chapters[row][1]:
                    lower_range = row + 1

        upper_range = len(self.chapters)

        # which ones do we want?
        if not self.options.auto:
            for n, chapter in enumerate(self.chapters):
                print("{:03d}. {}".format(n + 1, chapter[1].encode('utf-8')))
            self.chapters_to_download = self.select_chapters(self.chapters)
        # XML component
        else:
            if lower_range == upper_range:
                raise self.NoUpdates

            for row in range(lower_range, upper_range):
                self.chapters_to_download.append(row)
        return

    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        base_url = url[:url.rfind("/"):]
        base_url = base_url[:base_url.rfind("/"):]
        for page in range(1, max_pages + 1):
            page_url = base_url + '/' + str(page) + '/'
            self.parse_image_page(page, page_url, manga_chapter_prefix, max_pages, current_chapter)


#Register plugin
def setup(app):
    app.register_plugin('MangaEden', MangaEden)