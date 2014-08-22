#!/usr/bin/env python

# ####################

import os
import traceback

# ####################

from parsers.base import SiteParserBase
from parsers.factory import SiteParserFactory

# ####################


class MangaDownloader:
    def __init__(self, options):
        self.options = options
        self.site_parser = SiteParserFactory.get_instance(options)

    def download_new_chapters(self):
        try:
            self.site_parser.parse_site()
            last_chap = None
            for current_chapter in self.site_parser.chapters:
                last_chap = current_chapter[1]

            if not last_chap:
                raise Exception('Error: Couldnt fetch the last chapter number')

            # create download directory if not found
            if not os.path.exists(self.options.downloadPath):
                os.makedirs(self.options.downloadPath)

            success = self.site_parser.download()

            return success, last_chap

        except OSError:
            print("""Unable to create download directory. There may be a file
                with the same name, or you may not have permissions to write
                there.""")
            raise
        except self.site_parser.NoUpdates:
            print "Manga (" + self.options.manga + ") up-to-date."
            return False, 0
        except SiteParserBase.MangaNotFound:
            print "Error: Manga (" + self.options.manga + ") not found, temporary?"
            if self.options.verbose_FLAG:
                traceback.print_exc()
            return False, 0
        except Exception:
            print "Error: Unknown error trying to download manga (" + self.options.manga + ")"
            traceback.print_exc()
            return False, 0
