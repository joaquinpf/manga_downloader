#!/usr/bin/python

import re
from bs4 import BeautifulSoup

from parsers.base import SiteParserBase
from util import get_source_code

class Batoto(SiteParserBase):
    class PointlessThing2:
        def __init__(self):
            self.r = 0

        def group(self, x):
            return self.r

    class PointlessThing1:
        def __init__(self):
            pass

        @staticmethod
        def search(source):
            soup = BeautifulSoup(source)
            ol = soup.find("select", id="page_select")("option")
            a = Batoto.PointlessThing2()
            a.r = len(ol)
            return a

    re_get_max_pages = PointlessThing1()  # This is a terrible hack.
    re_get_image = re.compile("<img id=\"comic_page\".*?src=\"([^\"]+)\"")

    def __init__(self, options):
        SiteParserBase.__init__(self, options, "http://bato.to")

    def get_next_url(self, c):
        s = get_source_code(c, self.options.proxy)
        soup = BeautifulSoup(s)
        l = soup.find("img", title="Next Chapter").parent
        return l['href']

    def get_manga_url(self):
        url = "{}/search?name={}&name_cond=c".format(self.base_url, '+'.join(self.options.manga.split()))
        s = get_source_code(url, self.options.proxy)
        soup = BeautifulSoup(s)
        a = soup.find("div", id="comic_search_results")
        r = a.tbody.find_all("tr")[1:]
        seriesl = []
        for i in r:
            try:
                e = i.td.findAll('a')[1]
                u = e['href']
                t = e.img.next_sibling[1:]
                seriesl.append((u, t.encode('utf-8')))
            except:
                pass
        if not seriesl:
            # signifies no manga found
            raise self.MangaNotFound("Nonexistent.")
        url = self.select_from_results(seriesl)

        return url

    def parse_site(self, url):

        s = get_source_code(url, self.options.proxy)
        soup = BeautifulSoup(s)
        t = soup.find("table", class_="chapters_list").tbody
        cl = t.find_all("tr", class_="lang_English")
        self.chapters = [[]]
        cnum = self.chapters[0]

        for i in cl:
            u = i.td.a['href']
            t = i.td.a.img.next_sibling[1:]
            g = i.find_all("td")[2].get_text().strip()

            try:
                c = float(re.search("ch([\d.]+)", u).group(1))
                c = str(int(c)) if c.is_integer() else str(c)
            except AttributeError:
                c = '0'
            tu = (u, t, c, g)
            if len(cnum) == 0 or cnum[0][3] == c:
                cnum.append(tu)
            else:
                self.chapters.append([])
                cnum = self.chapters[-1]
                cnum.append(tu)

        self.chapters.reverse()

        if self.chapters == [[]]:
            raise self.MangaLicenced('It has been removed.')

        # Look for first chapter that should be downloaded in auto mode
        lower_range = 0
        if self.options.auto:
            for i in range(0, len(self.chapters)):
                if self.options.lastDownloaded == self.chapters[i][0][1]:
                    lower_range = i + 1

        sc = None
        for i in self.chapters:
            if len(i) == 1 or sc is None:
                sc = i[0]
                del i[1:]
                continue
            ll = [n for n in i if n[2] == sc[2]]
            if len(ll) != 1:
                c = self.get_next_url(sc[0])
                i[0] = [n for n in i if n[0] == c][0]
                if self.options.verbose_FLAG:
                    print("Anomaly at chapter {} ({} matches, chose {})".format(i[0][3], len(ll), i[0][2]))
                del i[1:]
                sc = i[0]
                continue
            i[0] = ll[0]
            sc = i[0]
            del i[1:]
        self.chapters = [i[0] for i in self.chapters]

        upper_range = len(self.chapters)
        # which ones do we want?
        if not self.options.auto:
            for n, c in enumerate(self.chapters):
                print("{:03d}. {}".format(n + 1, c[1].encode('utf-8')))
            self.chapters_to_download = self.select_chapters(self.chapters)
        # XML component
        else:
            if lower_range == upper_range:
                raise self.NoUpdates

            for i in range(lower_range, upper_range):
                self.chapters_to_download.append(i)
        return

    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        """We ignore max_pages, because you can't regex-search that under Batoto."""
        s = get_source_code(url, self.options.proxy)
        soup = BeautifulSoup(s)
        ol = soup.find("select", id="page_select")("option")
        n = 1
        for i in ol:
            self.download_image(n, i['value'], manga_chapter_prefix, max_pages, current_chapter)
            n += 1

#Register plugin
def setup(app):
    app.register_plugin('Batoto', Batoto)