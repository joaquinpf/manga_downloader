#!/usr/bin/python

import re
from bs4 import BeautifulSoup

from parsers.base import SiteParserBase
from util import getSourceCode

class EatManga(SiteParserBase):

    def parseSite(self):
        pass

    def downloadChapter(self, downloadThread, max_pages, url, manga_chapter_prefix, current_chapter):
        pass

