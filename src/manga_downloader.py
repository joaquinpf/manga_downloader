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

# ####################


class MangaDownloader:
    def __init__(self, options):
        self.options = options
        self.site_parser = SiteParserFactory.Instance().get_instance(options)

    def download_new_chapters(self):
        try:
            if not is_site_up(self.site_parser.base_url):
                cprint("Warn: %s seems to be down, won't try to download for now" % self.site_parser.options.site, 'yellow', attrs=['bold'], file=sys.stderr)
                return False, None

            print("Beginning '%s' check for '%s'" % (self.options.site, self.options.manga))

            url = self.site_parser.get_manga_url()
            if self.options.verbose_FLAG:
                print("Will check: %s" % url)

            if not is_site_up(url):
                cprint("Warn: Manga url seems to be down in '%s', was it removed? Won't try to download for now" % self.site_parser.options.site, 'yellow', attrs=['bold'], file=sys.stderr)
                return False, None

            self.site_parser.parse_site(url)
            last_chap = None
            for current_chapter in self.site_parser.chapters:
                last_chap = current_chapter[1]

            if not last_chap:
                raise Exception("Error: Couldn't fetch the last chapter number")

            # create download directory if not found
            if not os.path.exists(self.options.downloadPath):
                os.makedirs(self.options.downloadPath)

            self.site_parser.download()

            return True, last_chap

        except OSError:
            cprint("""Error: Unable to create download directory. There may be a file
                with the same name, or you may not have permissions to write
                there.""", 'red', attrs=['bold'], file=sys.stderr)
            raise
        except self.site_parser.NoUpdates:
            cprint("Manga '%s' up-to-date." % self.options.manga, 'green', attrs=['bold'], file=sys.stdout)
            return False, 0
        except SiteParserBase.MangaNotFound:
            cprint("Warn: Manga '%s' not found, temporary?" % self.options.manga, 'yellow', attrs=['bold'], file=sys.stderr)
            return False, 0
        except SiteParserBase.MangaLicenced:
            cprint("Warn: Manga '%s' was licenced and removed from the site" % self.options.manga, 'yellow', attrs=['bold'], file=sys.stderr)
            return False, 0
        except KeyboardInterrupt:
            raise
        except Exception:
            cprint("Error: Unknown error trying to download manga '%s'" % self.options.manga, 'red', attrs=['bold'], file=sys.stderr)
            if self.options.verbose_FLAG:
                cprint(traceback.format_exc(), 'red', attrs=['bold'], file=sys.stderr)
            return False, 0
