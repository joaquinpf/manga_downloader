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

class MangaEden(SiteParserBase):
    re_get_image = re.compile(ur'<img.*id="mainImg".*src="//(.*?)".*/>')
    re_get_max_pages = re.compile(ur'<span id="pageInfo_page">.* of (.*)</div>')

    def __init__(self):
        SiteParserBase.__init__(self, 'http://www.mangaeden.com', 'MangaEden')

    def get_manga_url(self, manga):
        url = '%s/en/en-manga/%s' % (self.base_url, fix_formatting(manga, '-', remove_special_chars=True, lower_case=True, use_ignore_chars=False))
        return url

    def parse_chapters(self, url, manga):

        source = get_source_code(url, config.proxy)
        soup = BeautifulSoup(source, 'html.parser')
        r_chapters = soup.find("div", id="mangaPage").find("div", id="leftContent").find_all("tr")
        r_chapters.pop(0)
        chapters = [[]]

        for row in r_chapters:
            cells = row.find_all('td')
            chapter = 'c' + str(row['id'])[1:]
            c_url = self.base_url + cells[0].a['href']
            title = cells[0].a.get_text().replace('\n', ' ').strip()
            group = cells[1].get_text().replace('\n', ' ').strip()
            tu = {'url': c_url, 'title': title, 'chapter': chapter, 'group': group}
            chapters.append(tu)

        if chapters == [[]]:
            raise self.MangaNotFound('Nothing to download.')

        #Remove [[]] and reverse to natural order
        chapters.pop(0)
        chapters.reverse()

        return chapters

    def get_max_pages(self, url):
        source = get_source_code(url, config.proxy)
        return int(self.__class__.re_get_max_pages.search(source).group(1))

    def download_chapter(self, url, manga_chapter_prefix, current_chapter):
        max_pages = self.get_max_pages(url)
        base_url = url[:url.rfind("/"):]
        base_url = base_url[:base_url.rfind("/"):]
        for page in range(1, max_pages + 1):
            page_url = base_url + '/' + str(page) + '/'
            self.parse_image_page(page, page_url, manga_chapter_prefix, max_pages, current_chapter)


#Register plugin
def setup(app):
    app.register_plugin('MangaEden', MangaEden)