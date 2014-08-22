#!/usr/bin/env python

# #####################

import json
import datetime

# #####################

from notifications.factory import NotificationFactory
from parsers.manga_downloader import MangaDownloader
from util import fix_formatting
import os
import time
import copy

# #####################


class MangaJsonParser:
    def __init__(self, options):
        self.options = options

    def download_manga(self):
        while True:
            self._download_manga()

            if not self.options.check_every_minutes or self.options.check_every_minutes < 0:
                break

            print "Will check again in %s minutes" % self.options.check_every_minutes
            time.sleep(60 * self.options.check_every_minutes)

    def _download_manga(self):
        print("Parsing JSON File...")
        if self.options.verbose_FLAG:
            print("JSON Path = %s" % self.options.json_file_path)

        with open(self.options.json_file_path) as data:
            configuration = json.load(data)

        self.options.auto = True

        if 'configuration' in configuration:
            self.options.notificator = NotificationFactory.get_instance(configuration['configuration']['notificator'])

        # Default OutputDir is the ./MangaName
        set_output_path_to_name = False
        if self.options.outputDir == 'DEFAULT_VALUE':
            set_output_path_to_name = True

        for manga in configuration['manga_series']:
            series_options = copy.copy(self.options)
            series_options.manga = manga['name']
            series_options.site = manga['host_site']
            last_downloaded = manga.get('last_chapter_downloaded', "")
            download_path = manga.get('download_path',
                                      ('./' + fix_formatting(series_options.manga, series_options.spaceToken)))

            if self.options.downloadPath != 'DEFAULT_VALUE' and not os.path.isabs(download_path):
                download_path = os.path.join(self.options.downloadPath, download_path)

            series_options.downloadPath = download_path
            series_options.lastDownloaded = last_downloaded
            if set_output_path_to_name:
                series_options.outputDir = download_path

            serie = MangaDownloader(series_options)
            result, last_chapter = serie.download_new_chapters()

            if result:
                t = datetime.datetime.today()
                timestamp = "%d-%02d-%02d %02d:%02d:%02d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)
                manga['timestamp'] = timestamp
                manga['last_chapter_downloaded'] = last_chapter

        # Backs up file
        backup_file_name = self.options.json_file_path + "_bak"
        os.rename(self.options.json_file_path, backup_file_name)

        with open(self.options.json_file_path, 'w') as outfile:
            json.dump(configuration, outfile, indent=4, sort_keys=True)

        # The file was succesfully saved and now remove backup
        os.remove(backup_file_name)

