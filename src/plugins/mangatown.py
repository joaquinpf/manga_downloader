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

class MangaTown(SiteParserBase):
    re_get_image_urls = re.compile(ur'lstImages\.push\("(.*)"\);')
    re_get_image = re.compile('img src="([^"]*)" .* id="image" .*')

    def __init__(self):
        SiteParserBase.__init__(self, 'http://www.mangatown.com', 'MangaTown')

    def get_manga_url(self, manga):
        # Example: http://www.mangatown.com/manga/one_piece/
        manga = fix_formatting(manga, '_', remove_special_chars=True, lower_case=True, use_ignore_chars=True, extra_ignore_chars=[':', '/'])
        manga = manga.replace(':', '_')
        manga = manga.replace('/', '_')
        manga = re.sub(r'_+', '_', manga)
        url = '%s/manga/%s' % (self.base_url, manga)
        return url

    def parse_chapters(self, url, manga):

        source = get_source_code(url, config.proxy)
        soup = BeautifulSoup(source, 'html.parser')
        r_chapters = soup.find("ul", class_="chapter_list").find_all("li")
        chapters = [[]]

        for row in r_chapters:
            info = row.a
            c_url = info['href']
            c_url = 'http:' + c_url if not c_url.startswith('http') else c_url
            chapter_line = info.get_text().strip()
            chapter = re.sub(manga.lower().replace('-', '.').replace(' ', '.'), '', chapter_line.lower().replace('-', '.')).replace('read online', '').replace('chapter', '').strip()
            chapter = re.sub("(vol\.[\d.]+)", '', chapter)
            chapter = re.sub("(:.*)", '', chapter)
            chapter = re.sub("-*\s*", '', chapter)
            chapter = 'c' + re.sub("ch\.", '', chapter).strip()
            group = ''
            title = manga + ' ' + chapter
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
        soup = BeautifulSoup(source, 'html.parser')
        page_count = 0

        for page in soup.find("div", class_="page_select").find_all("option"):
            page_count = page_count + 1 if page.text != "Featured" else page_count

        return page_count

    def download_chapter(self, url, manga_chapter_prefix, current_chapter):
        max_pages = self.get_max_pages(url)
        self.parse_image_page(1, url, manga_chapter_prefix, max_pages, current_chapter)
        for page in range(2, max_pages + 1):
            page_url = '%s%i.html' % (url, page)
            self.parse_image_page(page, page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('MangaTown', MangaTown)
