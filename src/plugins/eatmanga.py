#!/usr/bin/python

import re

from plugins.base import SiteParserBase
from util.util import get_source_code, fix_formatting

from collections import OrderedDict

class EatManga(SiteParserBase):
    re_get_chapters = re.compile('<a href="([^"]*)" title="([^"]*)">([^<]*)</a>([^<]*)</th>')
    re_get_max_pages = re.compile('</select> of (\d*)')
    re_get_page = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_get_image = re.compile('img id="eatmanga_image.*" src="([^"]*)')

    def __init__(self, options):
        SiteParserBase.__init__(self, options, 'http://eatmanga.com')

    def get_manga_url(self):
        url = '%s/Manga-Scan/%s' % (self.base_url, fix_formatting(self.options.manga, '-', remove_special_chars=True, lower_case=False, use_ignore_chars=False))
        return url

    def parse_chapters(self, url):

        source = get_source_code(url, self.options.proxy)

        self.chapters = EatManga.re_get_chapters.findall(source)
        self.chapters.reverse()

        if not self.chapters:
            raise self.MangaNotFound

        for i in range(0, len(self.chapters)):
            if 'upcoming' in self.chapters[i][0]:
                # Skip not available chapters
                del self.chapters[i]
                continue

            chapter_number = 'c' + self.chapters[i][2].lower().replace(self.options.manga.lower(), '').strip()
            self.chapters[i] = ('%s%s' % (self.base_url, self.chapters[i][0]), chapter_number, chapter_number)

    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        pages = EatManga.re_get_page.findall(get_source_code(url, self.options.proxy))

        # Remove duplicate pages if any and ensure order
        pages = list(OrderedDict.fromkeys(pages))

        for page in pages:
            page_url = 'http://eatmanga.com%s' % page[0]
            self.parse_image_page(page[1], page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('EatManga', EatManga)