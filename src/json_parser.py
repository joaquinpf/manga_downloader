#!/usr/bin/env python

######################

import json
import datetime

######################

from notifications.factory import NotificationFactory
from parsers.manga_downloader import MangaDownloader
from util import fixFormatting
import os
import time
import copy

######################

class MangaJsonParser:
    def __init__(self, optDict):
        self.options = optDict
        for elem in vars(optDict):
            setattr(self, elem, getattr(optDict, elem))

    def download_manga(self):
        while True:
            self._download_manga()

            if not self.check_every_minutes or self.check_every_minutes < 0:
                break

            print "Will check again in %s minutes" % self.options.check_every_minutes
            time.sleep(60 * self.options.check_every_minutes)

    def _download_manga(self):
        print("Parsing JSON File...")
        if (self.verbose_FLAG):
            print("JSON Path = %s" % self.json_file_path)

        with open(self.json_file_path) as data:
            configuration = json.load(data)

        self.options.auto = True

        if 'configuration' in configuration:
            self.options.notificator = NotificationFactory.getInstance(configuration['configuration']['notificator'])

        # Default OutputDir is the ./MangaName
        set_output_path_to_name = False
        if (self.options.outputDir == 'DEFAULT_VALUE'):
            set_output_path_to_name = True

        for manga in configuration['manga_series']:
            series_options = copy.copy(self.options)
            series_options.manga = manga['name']
            series_options.site = manga['host_site']
            lastDownloaded = manga.get('last_chapter_downloaded', "")
            download_path =	manga.get('download_path', ('./' + fixFormatting(series_options.manga, series_options.spaceToken)))

            if self.options.downloadPath != 'DEFAULT_VALUE' and not os.path.isabs(download_path):
                download_path = os.path.join(self.options.downloadPath, download_path)

            series_options.downloadPath = download_path
            series_options.lastDownloaded = lastDownloaded
            if set_output_path_to_name:
                series_options.outputDir = download_path

            serie = MangaDownloader(series_options)
            result, last_chapter = serie.download_new_chapters()

            if result == True:
                t = datetime.datetime.today()
                timeStamp = "%d-%02d-%02d %02d:%02d:%02d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)
                manga['timestamp'] = timeStamp
                manga['last_chapter_downloaded'] = last_chapter

        #Backs up file
        backup_file_name = self.json_file_path + "_bak"
        os.rename(self.json_file_path, backup_file_name)

        with open(self.json_file_path, 'w') as outfile:
            json.dump(configuration, outfile, indent=4, sort_keys=True)

        # The file was succesfully saved and now remove backup
        os.remove(backup_file_name)

