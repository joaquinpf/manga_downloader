#!/usr/bin/python

import re
from collections import OrderedDict

import config
from plugins.base import SiteParserBase
from util.util import get_source_code, fix_formatting


class EatManga(SiteParserBase):
    re_get_chapters = re.compile('<a href="([^"]*)" title="([^"]*)">([^<]*)</a>([^<]*)</th>')
    re_get_max_pages = re.compile('</select> of (\d*)')
    re_get_page = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_get_image = re.compile('img id="eatmanga_image.*" src="([^"]*)')

    def __init__(self):
        SiteParserBase.__init__(self, 'http://eatmanga.com', 'EatManga')

    def get_manga_url(self, manga):
        url = '%s/Manga-Scan/%s' % (self.base_url, fix_formatting(manga, '-', remove_special_chars=True, lower_case=False, use_ignore_chars=False))
        return url

    def parse_chapters(self, url, manga):

        source = get_source_code(url, config.proxy)

        chapters = EatManga.re_get_chapters.findall(source)
        chapters.reverse()

        if not chapters:
            raise self.MangaNotFound

        for i in range(0, len(chapters)):
            if 'upcoming' in chapters[i][0]:
                # Skip not available chapters
                del chapters[i]
                continue

            chapter_number = 'c' + chapters[i][2].lower().replace(manga.lower(), '').strip()
            tu = {'url': '%s%s' % (self.base_url, chapters[i][0]), 'title': chapter_number, 'chapter': chapter_number, 'group': None}
            chapters[i] = tu

        return chapters

    def get_max_pages(self, url):
        source = get_source_code(url, config.proxy)
        return int(self.__class__.re_get_max_pages.search(source).group(1))

    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        pages = EatManga.re_get_page.findall(get_source_code(url, config.proxy))

        # Remove duplicate pages if any and ensure order
        pages = list(OrderedDict.fromkeys(pages))

        for page in pages:
            page_url = 'http://eatmanga.com%s' % page[0]
            self.parse_image_page(page[1], page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('EatManga', EatManga)