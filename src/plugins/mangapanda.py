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

from parsers.base import SiteParserBase
from util import get_source_code

# ####################

class MangaPanda(SiteParserBase):
    re_get_series = re.compile('<li><a href="([^"]*)">([^<]*)</a>')
    re_get_chapters = re.compile('<a href="([^"]*)">([^<]*)</a>([^<]*)</td>')
    re_get_page = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_get_image = re.compile('img id="img" .* src="([^"]*)"')
    re_get_max_pages = re.compile('</select> of (\d*)(\s)*</div>')

    def __init__(self, options):
        SiteParserBase.__init__(self, options, 'http://www.mangapanda.com')

    def get_manga_url(self):
        url = '%s/alphabetical' % self.base_url
        source = get_source_code(url, self.options.proxy)
        all_series = MangaPanda.re_get_series.findall(source[source.find('series_col'):])
        keyword = self.select_from_results(all_series)
        url = (self.base_url + '%s') % keyword
        return url

    def parse_site(self, url):

        source = get_source_code(url, self.options.proxy)

        self.chapters = MangaPanda.re_get_chapters.findall(source)

        lower_range = 0

        for i in range(0, len(self.chapters)):
            chapter_number = self.chapters[i][1].replace(self.options.manga, '').strip()
            self.chapters[i] = (
                '%s%s' % (self.chapters[i][0], self.base_url), '%s%s' % (chapter_number, self.chapters[i][2]),
                chapter_number)
            if not self.options.auto:
                print('(%i) %s' % (i + 1, self.chapters[i][1]))
            else:
                if self.options.lastDownloaded == self.chapters[i][1]:
                    lower_range = i + 1

        upper_range = len(self.chapters)
        if not self.options.auto:
            self.chapters_to_download = self.select_chapters(self.chapters)
        else:
            if lower_range == upper_range:
                raise self.NoUpdates

            for i in range(lower_range, upper_range):
                self.chapters_to_download.append(i)

        return

    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        for page in MangaPanda.re_get_page.findall(get_source_code(url, self.options.proxy)):
            page_url = 'http://www.mangapanda.com' + page[0]
            self.download_image(page[1], page_url, manga_chapter_prefix, max_pages, current_chapter)

#Register plugin
def setup(app):
    app.register_plugin('MangaPanda', MangaPanda)