#!/usr/bin/env python

# ####################

import os
import traceback
import sys

# ####################

from plugins.base import SiteParserBase
from plugins.factory import SiteParserFactory
from util.util import is_site_up
from termcolor import cprint
import copy
import datetime
from util.util import fix_formatting


# ####################


class MangaDownloader:
    def download_chapters_from_config(self, configuration, base_options):

        for manga in configuration['manga_series']:
            series_options = copy.copy(base_options)
            series_options.manga = manga['name']
            series_options.site = manga['host_site']
            last_downloaded = manga.get('last_chapter_downloaded', "")
            download_path = manga.get('download_path',
                                      ('./' + fix_formatting(series_options.manga, series_options.spaceToken)))

            if base_options.downloadPath != 'DEFAULT_VALUE' and not os.path.isabs(download_path):
                download_path = os.path.join(base_options.downloadPath, download_path)

            series_options.downloadPath = download_path
            series_options.lastDownloaded = last_downloaded

            result, last_chapter = self.download_new_chapters(series_options)

            if result:
                t = datetime.datetime.today()
                timestamp = "%d-%02d-%02d %02d:%02d:%02d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)
                manga['timestamp'] = timestamp
                manga['last_chapter_downloaded'] = last_chapter

    def download_new_chapters(self, options):
        try:
            site_parser = SiteParserFactory.Instance().get_instance(options)

            if not is_site_up(site_parser.base_url):
                cprint("Warn: %s seems to be down, won't try to download for now" % site_parser.options.site, 'yellow',
                       attrs=['bold'], file=sys.stderr)
                return False, None

            print("Beginning '%s' check for '%s'" % (options.site, options.manga))

            url = site_parser.get_manga_url()
            if options.verbose_FLAG:
                print("Will check: %s" % url)

            if not is_site_up(url):
                cprint(
                    "Warn: Manga url seems to be down in '%s', was it removed? Won't try to download for now" % site_parser.options.site,
                    'yellow', attrs=['bold'], file=sys.stderr)
                return False, None

            site_parser.parse_chapters(url)
            site_parser.select_chapters_to_download()
            last_chap = None
            for current_chapter in site_parser.chapters:
                last_chap = current_chapter[1]

            if not last_chap:
                raise Exception("Error: Couldn't fetch the last chapter number")

            # create download directory if not found
            if not os.path.exists(options.downloadPath):
                os.makedirs(options.downloadPath)

            site_parser.download()

            return True, last_chap

        except OSError:
            cprint("""Error: Unable to create download directory. There may be a file
                with the same name, or you may not have permissions to write
                there.""", 'red', attrs=['bold'], file=sys.stderr)
            raise
        except site_parser.NoUpdates:
            cprint("Manga '%s' up-to-date." % options.manga, 'green', attrs=['bold'], file=sys.stdout)
            return False, 0
        except SiteParserBase.MangaNotFound:
            cprint("Warn: Manga '%s' not found, temporary?" % options.manga, 'yellow', attrs=['bold'], file=sys.stderr)
            return False, 0
        except SiteParserBase.MangaLicenced:
            cprint("Warn: Manga '%s' was licenced and removed from the site" % options.manga, 'yellow', attrs=['bold'],
                   file=sys.stderr)
            return False, 0
        except KeyboardInterrupt:
            raise
        except Exception:
            cprint("Error: Unknown error trying to download manga '%s'" % options.manga, 'red', attrs=['bold'],
                   file=sys.stderr)
            if options.verbose_FLAG:
                cprint(traceback.format_exc(), 'red', attrs=['bold'], file=sys.stderr)
            return False, 0
