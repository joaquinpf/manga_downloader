#!/usr/bin/python

import re

from parsers.base import SiteParserBase
from util import get_source_code

from collections import OrderedDict

class EatManga(SiteParserBase):
    re_get_chapters = re.compile('<a href="([^"]*)" title="([^"]*)">([^<]*)</a>([^<]*)</th>')
    re_get_max_pages = re.compile('</select> of (\d*)')
    re_get_page = re.compile("<option value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_get_image = re.compile('img id="eatmanga_image.*" src="([^"]*)')

    def __init__(self, options):
        SiteParserBase.__init__(self, options, 'http://eatmanga.com')

    def parse_site(self):
        print('Beginning EatManga check: %s' % self.options.manga)
        url = '%s/Manga-Scan/%s' % (self.base_url, self.fix_formatting(self.options.manga))
        if self.options.verbose_FLAG:
            print(url)

        source = get_source_code(url, self.options.proxy)

        self.chapters = EatManga.re_get_chapters.findall(source)
        self.chapters.reverse()

        if not self.chapters:
            raise self.MangaNotFound

        lower_range = 0

        for i in range(0, len(self.chapters)):
            if 'upcoming' in self.chapters[i][0]:
                # Skip not available chapters
                del self.chapters[i]
                continue

            chapter_number = self.chapters[i][2].replace(self.options.manga, '').strip()
            self.chapters[i] = ('%s%s' % (self.chapters[i][0], self.base_url), chapter_number, chapter_number)
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
        page_index = 0
        pages = EatManga.re_get_page.findall(get_source_code(url, self.options.proxy))

        # Remove duplicate pages if any and ensure order
        pages = list(OrderedDict.fromkeys(pages))

        for page in pages:
            if self.options.verbose_FLAG:
                print(self.chapters[current_chapter][1] + ' | ' + 'Page %s / %i' % (page[1], max_pages))

            page_url = 'http://eatmanga.com%s' % page[0]
            self.download_image(page[1], page_url, manga_chapter_prefix)
            page_index += 1

    def fix_formatting(self, s):
        p = re.compile('\s+')
        s = p.sub(' ', s)

        s = s.strip().replace(' ', '-')
        return s

#Register plugin
def setup(app):
    app.register_plugin('eatmanga', EatManga)