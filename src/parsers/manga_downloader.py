#!/usr/bin/env python

#####################

import os

#####################

from parsers.base import SiteParserBase
from parsers.factory import SiteParserFactory

#####################

class MangaDownloader:

    def __init__ (self, optDict):
        for elem in vars(optDict):
            setattr(self, elem, getattr(optDict, elem))

        self.siteParser = SiteParserFactory.getInstance(self)

    def download_new_chapters(self):
        try:
            self.siteParser.parseSite()
            for current_chapter in self.siteParser.chapters:
                iLastChap = current_chapter[1]

            # create download directory if not found
            if not os.path.exists(self.downloadPath):
                os.makedirs(self.downloadPath)

            success = self.siteParser.download()

            return success, iLastChap

        except OSError:
            print("""Unable to create download directory. There may be a file
                with the same name, or you may not have permissions to write
                there.""")
            raise

        except self.siteParser.NoUpdates:
            print ("Manga ("+self.manga+") up-to-date.")
            return False, 0

        except SiteParserBase.MangaNotFound as Instance:
            print("Error: Manga ("+self.manga+")")
            print(Instance)
            return False, 0
