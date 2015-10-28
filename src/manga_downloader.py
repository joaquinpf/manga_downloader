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
import datetime
from util.util import fix_formatting
import config


# ####################


class MangaDownloader:

    # Download chapters based on configuration most likely coming from JSON
    def download_chapters_from_config(self, configuration, base_download_path):

        for manga in configuration['manga_series']:
            name = manga['name']
            site = manga['host_site']
            last_downloaded = manga.get('last_chapter_downloaded', "")
            download_path = manga.get('download_path', ('./' + fix_formatting(name, config.spaceToken)))

            if base_download_path != 'DEFAULT_VALUE' and not os.path.isabs(download_path):
                download_path = os.path.join(base_download_path, download_path)

            result, last_chapter = self.download_new_chapters(name, site, download_path, last_downloaded)

            if result:
                t = datetime.datetime.today()
                timestamp = "%d-%02d-%02d %02d:%02d:%02d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)
                manga['timestamp'] = timestamp
                manga['last_chapter_downloaded'] = last_chapter

    # Download specified chapters
    def download_new_chapters(self, manga, site, download_path, last_downloaded):

        try:
            site_parser = SiteParserFactory.Instance().get_instance(site)

            if not is_site_up(site_parser.base_url):
                cprint("Warn: %s seems to be down, won't try to download for now" % site, 'yellow',
                       attrs=['bold'], file=sys.stderr)
                return False, None

            print("Beginning '%s' check for '%s'" % (site, manga))

            url = site_parser.get_manga_url(manga)
            if config.verbose_FLAG:
                print("Will check: %s" % url)

            if not is_site_up(url):
                cprint(
                    "Warn: Manga url seems to be down in '%s', was it removed? Won't try to download for now" % site,
                    'yellow', attrs=['bold'], file=sys.stderr)
                return False, None

            chapters = site_parser.parse_chapters(url, manga)
            chapters_to_download = site_parser.select_chapters_to_download(chapters, last_downloaded)
            last_chap = chapters[-1]['chapter']

            if not last_chap:
                raise Exception("Error: Couldn't fetch the last chapter number")

            # create download directory if not found
            if not os.path.exists(download_path):
                os.makedirs(download_path)

            for current_chapter in chapters_to_download:
                site_parser.process_chapter(chapters[current_chapter], manga, download_path)

            return True, last_chap

        except OSError:
            cprint("""Error: Unable to create download directory. There may be a file
                with the same name, or you may not have permissions to write
                there.""", 'red', attrs=['bold'], file=sys.stderr)
            raise
        except site_parser.NoUpdates:
            cprint("Manga '%s' up-to-date." % manga, 'green', attrs=['bold'], file=sys.stdout)
            return False, 0
        except SiteParserBase.MangaNotFound:
            cprint("Warn: Manga '%s' not found, temporary?" % manga, 'yellow', attrs=['bold'], file=sys.stderr)
            return False, 0
        except SiteParserBase.MangaLicenced:
            cprint("Warn: Manga '%s' was licenced and removed from the site" % manga, 'yellow', attrs=['bold'],
                   file=sys.stderr)
            return False, 0
        except KeyboardInterrupt:
            raise
        except Exception:
            cprint("Error: Unknown error trying to download manga '%s'" % manga, 'red', attrs=['bold'],
                   file=sys.stderr)
            if config.verbose_FLAG:
                cprint(traceback.format_exc(), 'red', attrs=['bold'], file=sys.stderr)
            return False, 0
