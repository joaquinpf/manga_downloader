#!/usr/bin/env python

# ###################################################################
# For more detailed comments look at MangaFoxParser
#
# The code for this sites is similar enough to not need
# explanation, but dissimilar enough to not warrant any further OOP
# ###################################################################

# ###################

import re

# ####################

from plugins.base import SiteParserBase
from util.util import get_source_code

# ####################

class MangaReader(SiteParserBase):
    re_get_series = re.compile('<li><a href="([^"]*)">([^<]*)</a>')
    re_get_chapters = re.compile('<a href="([^"]*)">([^<]*)</a>([^<]*)</td>')
    re_get_page = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_get_image = re.compile('img id="img" .* src="([^"]*)"')
    re_get_max_pages = re.compile('</select> of (\d*)(\s)*</div>')

    def __init__(self, options):
        SiteParserBase.__init__(self, options, 'http://www.mangareader.net')

    def get_manga_url(self):
        url = '%s/alphabetical' % self.base_url
        source = get_source_code(url, self.options.proxy)
        all_series = MangaReader.re_get_series.findall(source[source.find('series_col'):])
        keyword = self.select_from_results(all_series)
        url = (self.base_url + '%s') % keyword
        return url


    def parse_chapters(self, url):

        source = get_source_code(url, self.options.proxy)

        self.chapters = MangaReader.re_get_chapters.findall(source)

        for i in range(0, len(self.chapters)):
            chapter_number = 'c' + self.chapters[i][1].replace(self.options.manga, '').strip()
            self.chapters[i] = ('%s%s' % (self.base_url, self.chapters[i][0]), '%s%s' % (chapter_number, self.chapters[i][2]), chapter_number)


    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        for page in MangaReader.re_get_page.findall(get_source_code(url, self.options.proxy)):
            page_url = 'http://www.mangareader.net' + page[0]
            self.parse_image_page(page[1], page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('MangaReader', MangaReader)