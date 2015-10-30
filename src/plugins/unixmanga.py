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

class UnixManga(SiteParserBase):
    re_get_max_pages = re.compile(ur'<A class="td2" rel="nofollow" .*>([\d.]+)\.jpg</A><BR>', re.DOTALL)

    def __init__(self):
        SiteParserBase.__init__(self, 'http://unixmanga.nl', 'UnixManga')

    def get_manga_url(self, manga):
        url = '%s/onlinereading/%s.html' % (self.base_url, fix_formatting(manga, '_', remove_special_chars=True, lower_case=True, use_ignore_chars=False))
        return url


    def parse_chapters(self, url, manga):

        source = get_source_code(url, config.proxy)
        soup = BeautifulSoup(source, 'html.parser')
        r_chapters = soup.find_all("tr", class_="snF")
        chapters = [[]]
        r_chapters.pop(0)

        for row in r_chapters:
            chapter = row.find_all('td')[1]
            c_url = chapter.a['href']
            title = chapter.a.get_text().strip()
            group = ''

            try:
                chapter = float(re.search("c([\d.]+)", title).group(1))
                chapter = 'c' + str(int(chapter)) if chapter.is_integer() else str(chapter)
            except AttributeError:
                chapter = 'c0'
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
        s = get_source_code(url, config.proxy)
        soup = BeautifulSoup(s, 'html.parser')
        pages = soup.find_all('a', class_="td2")
        n = 1
        for page in pages:
            a_text = page.get_text().strip()
            if a_text == 'z_homeunix.png' or a_text == 'BACK TO MAIN LIST':
                continue
            non_parsed_url = page['href']
            search = re.search("\?image=(.*?)/(.*)&server=(.*).html", non_parsed_url)
            manga = search.group(1)
            page_path = search.group(2)
            server = search.group(3)

            page_url = 'http://%s.unixmanga.net/onlinereading/%s/%s' % (server, manga, page_path)
            self.download_image(n, page_url, manga_chapter_prefix, len(pages), current_chapter)
            n += 1


#Register plugin
def setup(app):
    app.register_plugin('UnixManga', UnixManga)