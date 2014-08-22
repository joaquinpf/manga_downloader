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


class MangaReader(SiteParserBase):
    re_get_series = re.compile('<li><a href="([^"]*)">([^<]*)</a>')
    re_get_chapters = re.compile('<a href="([^"]*)">([^<]*)</a>([^<]*)</td>')
    re_get_page = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_get_image = re.compile('img id="img" .* src="([^"]*)"')
    re_get_max_pages = re.compile('</select> of (\d*)(\s)*</div>')

    def __init__(self, options):
        SiteParserBase.__init__(self, options)

    def parse_site(self):
        print('Beginning MangaReader check: %s' % self.options.manga)

        url = 'http://www.mangareader.net/alphabetical'

        source = get_source_code(url, self.options.proxy)
        all_series = MangaReader.re_get_series.findall(source[source.find('series_col'):])

        keyword = self.select_from_results(all_series)

        url = 'http://www.mangareader.net%s' % keyword
        source = get_source_code(url, self.options.proxy)

        self.chapters = MangaReader.re_get_chapters.findall(source)

        lower_range = 0

        for i in range(0, len(self.chapters)):
            chapter_number = self.chapters[i][1].replace(self.options.manga, '').strip()
            self.chapters[i] = (
                'http://www.mangareader.net%s' % self.chapters[i][0], '%s%s' % (chapter_number, self.chapters[i][2]),
                chapter_number)
            if not self.options.auto:
                print('(%i) %s' % (i + 1, self.chapters[i][1]))
            else:
                if self.options.lastDownloaded == self.chapters[i][1].decode('utf-8'):
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

    def download_chapter(self, download_thread, max_pages, url, manga_chapter_prefix, current_chapter):
        page_index = 0
        for page in MangaReader.re_get_page.findall(get_source_code(url, self.options.proxy)):
            if self.options.verbose_FLAG:
                print(self.chapters[current_chapter][1] + ' | ' + 'Page %s / %i' % (page[1], max_pages))

            page_url = 'http://www.mangareader.net' + page[0]
            self.download_image(download_thread, page[1], page_url, manga_chapter_prefix)
            page_index += 1
