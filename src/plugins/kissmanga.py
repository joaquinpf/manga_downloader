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

class KissManga(SiteParserBase):
    re_get_image_urls = re.compile(ur'lstImages\.push\("(.*)"\);')
    re_get_max_pages = re.compile(ur'lstImages\.push\(".*/([\d.]+)\..*"\);', re.DOTALL)

    def __init__(self, options):
        SiteParserBase.__init__(self, options, 'http://kissmanga.com')

    def get_manga_url(self):
        url = '%s/Manga/%s' % (self.base_url, fix_formatting(self.options.manga, '-', remove_special_chars=True, lower_case=True, use_ignore_chars=False))
        return url

    def parse_site(self, url):

        source = get_source_code(url, self.options.proxy)
        soup = BeautifulSoup(source, 'html.parser')
        r_chapters = soup.find("table", class_="listing").find_all("tr")
        r_chapters.pop(0)
        r_chapters.pop(0)
        self.chapters = [[]]

        for row in r_chapters:
            info = row.find_all('td')[0].a
            c_url = self.base_url + info['href']
            title = info.get_text().strip()
            chapter = title.lower().replace(self.options.manga.lower(), '').replace('Read Online', '').strip()
            chapter = re.sub("(vol\.[\d.]+)", '', chapter)
            chapter = re.sub("(:.*)", '', chapter)
            chapter = re.sub("ch\.", '', chapter).strip()
            group = ''
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
        s = get_source_code(url, self.options.proxy)
        pages = re.findall(self.re_get_image_urls, s)
        n = 1
        for page in pages:
            self.download_image(n, page, manga_chapter_prefix, max_pages, current_chapter)
            n += 1

#Register plugin
def setup(app):
    app.register_plugin('KissManga', KissManga)