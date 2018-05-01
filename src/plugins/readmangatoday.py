#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ###################

import re

import config


# ####################

from bs4 import BeautifulSoup
from plugins.base import SiteParserBase
from util.util import get_source_code, fix_formatting

# ####################

class ReadMangaToday(SiteParserBase):
    re_get_image = re.compile('img src="(.*)" class="img-responsive" id="chapter_img"')

    def __init__(self):
        SiteParserBase.__init__(self, 'http://www.readmng.com', 'ReadMangaToday')

    def get_manga_url(self, manga):
        manga = fix_formatting(manga, '-', remove_special_chars=True, lower_case=True, use_ignore_chars=False, extra_ignore_chars=[])
        url = '%s/%s' % (self.base_url, manga)
        return url

    def parse_chapters(self, url, manga):

        source = get_source_code(url, config.proxy)
        soup = BeautifulSoup(source, 'html.parser')
        r_chapters = soup.find("ul", class_="chp_lst").find_all("li")
        chapters = [[]]

        for row in r_chapters:
            info = row.find("span", class_="val")
            c_url = row.a['href']
            chapter_line = info.get_text().strip()
            chapter = 'c' + chapter_line.rsplit('-', 1)[1].strip()
            group = ''
            title = manga + ' ' + chapter
            tu = {'url': c_url, 'title': title, 'chapter': chapter, 'group': group}
            chapters.append(tu)

        if chapters == [[]]:
            raise self.MangaNotFound('Nothing to download.')

        #Remove [[]] and reverse to natural order
        chapters.pop(0)
        chapters.reverse()

        #Remove header
        chapters.pop(0)

        return chapters

    def get_max_pages(self, url):
        source = get_source_code(url, config.proxy)
        soup = BeautifulSoup(source, 'html.parser')
        pages = soup.find_all("select", class_="form-control input-sm jump-menu")[2].find_all("option")

        return len(pages)

    def download_chapter(self, url, manga_chapter_prefix, current_chapter):
        max_pages = self.get_max_pages(url)
        self.parse_image_page(1, url, manga_chapter_prefix, max_pages, current_chapter)
        for page in range(2, max_pages + 1):
            page_url = '%s/%i' % (url, page)
            self.parse_image_page(page, page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('ReadMangaToday', ReadMangaToday)