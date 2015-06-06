#!/usr/bin/python

import re

from parsers.base import SiteParserBase
from util import get_source_code

class Starkana(SiteParserBase):
    # re_get_page = re.compile("<option.*?value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_get_max_pages = re.compile('</select> of <strong>(\d*)')
    re_get_image = re.compile('img.*?class="dyn" src="([^"]*)')
    re_get_chapters = re.compile(
        '<a class="download-link" href="([^"]*)">([^<]*) <em>chapter</em> <strong>([\d\.]*)</strong></a>')

    def __init__(self, options):
        SiteParserBase.__init__(self, options, 'http://starkana.com')

    def parse_site(self):
        print('Beginning Starkana check: %s' % self.options.manga)
        url = '%s/manga/%s/%s' % (self.base_url, self.options.manga[0], self.fix_formatting(self.options.manga))
        if self.options.verbose_FLAG:
            print(url)

        source = get_source_code(url, self.options.proxy)

        self.chapters = Starkana.re_get_chapters.findall(source)
        self.chapters.reverse()

        if not self.chapters:
            raise self.MangaNotFound

        lower_range = 0

        for i in range(0, len(self.chapters)):
            self.chapters[i] = ('%s%s' % (self.chapters[i][0], self.base_url), self.chapters[i][2], self.chapters[i][2])
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

        for page in range(1, max_pages + 1):
            if self.options.verbose_FLAG:
                print(self.chapters[current_chapter][1] + ' | ' + 'Page %s / %i' % (page, max_pages))

            self.download_image(page, '%s/%s' % (url, page), manga_chapter_prefix)

    def fix_formatting(self, s):
        p = re.compile('\s+')
        s = p.sub(' ', s)

        s = s.strip().replace(' ', '_')
        return s

#Register plugin
def setup(app):
    app.register_plugin('starkana', Starkana)