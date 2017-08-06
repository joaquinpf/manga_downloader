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

class KissManga(SiteParserBase):
    re_get_image_urls = re.compile(ur'lstImages\.push\("(.*)"\);')
    re_get_max_pages = re.compile(ur'lstImages\.push\(".*/([\d.]+)\..*"\);', re.DOTALL)

    def __init__(self):
        SiteParserBase.__init__(self, 'http://kissmanga.com', 'KissManga')

    def get_manga_url(self, manga):
        manga = fix_formatting(manga, '-', remove_special_chars=True, lower_case=True, use_ignore_chars=True, extra_ignore_chars=[':'])
        manga = manga.replace(':', '-')
        url = '%s/Manga/%s' % (self.base_url, manga)
        return url

    def parse_chapters(self, url, manga):

        source = get_source_code(url, config.proxy)
        soup = BeautifulSoup(source, 'html.parser')
        r_chapters = soup.find("table", class_="listing").find_all("tr")
        r_chapters.pop(0)
        r_chapters.pop(0)
        chapters = [[]]

        for row in r_chapters:
            info = row.find_all('td')[0].a
            c_url = self.base_url + info['href']
            chapter_line = info.get_text().strip()
            chapter = re.sub(manga.lower().replace('-', '.'), '', chapter_line.lower()).replace('read online', '').replace('chapter', '').strip()
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
        return len(re.findall(re.compile(ur'lstImages\.push'), source))

    def download_chapter(self, url, manga_chapter_prefix, current_chapter):
        max_pages = self.get_max_pages(url)
        for page in range(1, max_pages + 1):
            page_url = '%s#%i' % (url, page)
            self.parse_image_page(page, page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('KissManga', KissManga)