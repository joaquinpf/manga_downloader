#!/usr/bin/env python

# ###################################################################
# For more detailed comments look at MangaFoxParser
#
# The code for this sites is similar enough to not need
# explanation, but dissimilar enough to not warrant any further OOP
# ###################################################################

# ###################

import re

import config


# ####################

from plugins.base import SiteParserBase
from util.util import get_source_code, fix_formatting

# ####################

class MangaReader(SiteParserBase):
    re_get_series = re.compile('<li><a href="([^"]*)">([^<]*)</a>')
    re_get_chapters = re.compile('<a href="([^"]*)">([^<]*)</a>([^<]*)</td>')
    re_get_page = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_get_image = re.compile('img id="img" .* src="([^"]*)"')
    re_get_max_pages = re.compile('</select> of (\d*)(\s)*</div>')

    def __init__(self):
        SiteParserBase.__init__(self, 'http://www.mangareader.net', 'MangaReader')

    def get_manga_url(self, manga):
        url = '%s/%s' % (self.base_url, fix_formatting(manga, '-', remove_special_chars=True, lower_case=True, use_ignore_chars=False))
        return url


    def parse_chapters(self, url, manga):

        source = get_source_code(url, config.proxy)

        chapters = MangaReader.re_get_chapters.findall(source)

        for i in range(0, len(chapters)):
            chapter_number = 'c' + chapters[i][1].replace(manga, '').strip()
            tu = {'url': '%s%s' % (self.base_url, chapters[i][0]), 'title': '%s%s' % (chapter_number, chapters[i][2].decode('utf8')), 'chapter': chapter_number, 'group': None}
            chapters[i] = tu

        return chapters

    def get_max_pages(self, url):
        source = get_source_code(url, config.proxy)
        return int(self.__class__.re_get_max_pages.search(source).group(1))

    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        for page in MangaReader.re_get_page.findall(get_source_code(url, config.proxy)):
            page_url = self.base_url + page[0]
            self.parse_image_page(page[1], page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('MangaReader', MangaReader)