#!/usr/bin/python

import re

from parsers.base import SiteParserBase
from util import getSourceCode

class Starkana(SiteParserBase):

    #re_getPage = re.compile("<option.*?value=\"([^']*?)\"[^>]*>\s*(\d*)</option>")
    re_getMaxPages = re.compile('</select> of <strong>(\d*)')
    re_getImage = re.compile('img.*?class="dyn" src="([^"]*)')
    re_getChapters = re.compile('<a class="download-link" href="([^"]*)">([^<]*) <em>chapter</em> <strong>(\d*)</strong></a>')

    def fixFormatting(self, s):
        p = re.compile( '\s+')
        s = p.sub( ' ', s )

        s = s.strip().replace(' ', '_')
        return s

    def parseSite(self):
        print('Beginning Starkana check: %s' % self.manga)
        url = 'http://starkana.com/manga/%s/%s' % (self.manga[0], self.fixFormatting( self.manga ))
        if self.verbose_FLAG:
            print(url)

        source = getSourceCode(url, self.proxy)

        self.chapters = Starkana.re_getChapters.findall(source)
        self.chapters.reverse()

        if not self.chapters:
            raise self.MangaNotFound

        lowerRange = 0

        for i in range(0, len(self.chapters)):
            self.chapters[i] = ('http://starkana.com%s' % self.chapters[i][0], self.chapters[i][2], self.chapters[i][2])
            if (not self.auto):
                print('(%i) %s' % (i + 1, self.chapters[i][1]))
            else:
                if (self.lastDownloaded == self.chapters[i][1]):
                    lowerRange = i + 1

        # this might need to be len(self.chapters) + 1, I'm unsure as to whether python adds +1 to i after the loop or not
        upperRange = len(self.chapters)

        if (not self.auto):
            self.chapters_to_download = self.selectChapters(self.chapters)
        else:
            if (lowerRange == upperRange):
                raise self.NoUpdates

            for i in range (lowerRange, upperRange):
                self.chapters_to_download .append(i)

        return

    def downloadChapter(self, downloadThread, max_pages, url, manga_chapter_prefix, current_chapter):

        for page in range(1, max_pages + 1):
            if (self.verbose_FLAG):
                print(self.chapters[current_chapter][1] + ' | ' + 'Page %s / %i' % (page, max_pages))

            self.downloadImage(downloadThread, page, '%s/%s' % (url, page), manga_chapter_prefix)

