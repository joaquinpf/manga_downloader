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

class MangaStream(SiteParserBase):
    re_get_image = re.compile('img id="manga-page"[ \t]+src="//([^"]*)".*')
    re_get_max_pages = re.compile(ur'Last Page \((\d*)\)', re.DOTALL)

    def __init__(self):
        SiteParserBase.__init__(self, 'http://www.mangastream.com', 'MangaStream')

    def get_manga_url(self, manga):
        manga = fix_formatting(manga, '_', remove_special_chars=True, lower_case=True, use_ignore_chars=True, extra_ignore_chars=[':', '/'])
        manga = manga.replace(':', '_')
        manga = manga.replace('/', '_')
        url = '%s/manga/%s' % (self.base_url, manga)
        return url

    def parse_chapters(self, url, manga):

        source = get_source_code(url, config.proxy)
        soup = BeautifulSoup(source, 'html.parser')
        r_chapters = soup.find("table", class_="table table-striped").find_all("tr")
        r_chapters.pop(0)
        chapters = [[]]

        for row in r_chapters:
            info = row.find_all('td')[0].a
            c_url = 'http://mangastream.com' + info['href']
            chapter_line = info.get_text().strip()
            chapter = chapter_line.rsplit('-', 1)[0]
            chapter = re.sub(manga.lower().replace('-', '.'), '', chapter.lower()).replace('read online', '').replace('chapter', '').strip()
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
        return int(self.__class__.re_get_max_pages.search(source).group(1))

    def download_chapter(self, url, manga_chapter_prefix, current_chapter):
        max_pages = self.get_max_pages(url)
        self.parse_image_page(1, url, manga_chapter_prefix, max_pages, current_chapter)
        page_base_url = url.rsplit('/', 1)[0]
        for page in range(2, max_pages + 1):
            page_url = '%s/%i' % (page_base_url, page)
            self.parse_image_page(page, page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('MangaStream', MangaStream)