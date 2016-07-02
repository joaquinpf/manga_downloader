#!/usr/bin/env python

# Copyright (C) 2010
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# #########

import optparse
import os
import sys
import os.path
import time

from termcolor import cprint
from colorama import init

import config
from plugins.factory import SiteParserFactory
from notifications.factory import NotificationFactory



# #########

from manga_downloader import MangaDownloader
from util.util import fix_formatting
from json_parser import MangaJsonParser
from collections import OrderedDict

# #########

VERSION = 'v0.8.8'
siteDict = OrderedDict()


# #########

class InvalidSite(Exception):
    pass


def print_license_info():
    print("\nProgram: Copyright (c) 2010. GPL v3 (http://www.gnu.org/licenses/gpl.html).")
    print("Icon:      Copyright (c) 2006. GNU Free Document License v1.2 (Author:Kasuga).")
    print("           http://ja.wikipedia.org/wiki/%E5%88%A9%E7%94%A8%E8%80%85:Kasuga\n")


# #########

def main():
    # Initialize Colorama
    init()

    # Load available plugins
    i = 1
    for plugin_name in SiteParserFactory.Instance().plugins:
        siteDict[str(i)] = plugin_name
        i += 1

    print_license_info()

    # for easier parsing, adds free --help and --version
    # optparse (v2.3-v2.7) was chosen over argparse (v2.7+) for compatibility (and relative similarity) reasons
    # and over getopt(v?) for additional functionality
    parser = optparse.OptionParser(usage='usage: %prog [options] <manga name>',
                                   version=('Manga Downloader %s' % VERSION))

    parser.set_defaults(
        all_chapters_FLAG=False,
        auto=False,
        downloadFormat='.cbz',
        downloadPath='DEFAULT_VALUE',
        overwrite_FLAG=False,
        verbose_FLAG=False,
        timeLogging_FLAG=False,
        maxChapterThreads=3,
        useShortName=False,
        spaceToken='.',
        proxy=None,
        check_every_minutes=-1
    )

    parser.add_option('--all',
                      action='store_true',
                      dest='all_chapters_FLAG',
                      help='Download all available chapters.')

    parser.add_option('-d', '--directory',
                      dest='downloadPath',
                      help='The destination download directory.  Defaults to the directory of the script.')

    parser.add_option('--overwrite',
                      action='store_true',
                      dest='overwrite_FLAG',
                      help='Overwrites previous copies of downloaded chapters.')

    parser.add_option('--verbose',
                      action='store_true',
                      dest='verbose_FLAG',
                      help='Verbose Output.')

    parser.add_option('-j', '--json',
                      dest='json_file_path',
                      help='Parses the .json file and downloads all chapters newer than the last chapter downloaded for'
                           ' the listed mangas.')

    parser.add_option('-z', '--zip',
                      action='store_const',
                      dest='downloadFormat',
                      const='.zip',
                      help='Downloads using .zip compression.  Omitting this option defaults to %default.')

    parser.add_option('-t', '--threads',
                      dest='maxChapterThreads',
                      help='Limits the number of chapter threads to the value specified.')

    parser.add_option('--timeLogging',
                      action='store_true',
                      dest='timeLogging_FLAG',
                      help='Output time logging.')

    parser.add_option('--useShortName',
                      action='store_true',
                      dest='useShortName_FLAG',
                      help='To support devices that limit the size of the filename, this parameter uses a short name')

    parser.add_option('--spaceToken',
                      dest='spaceToken',
                      help='Specifies the character used to replace spaces in the manga name.')

    parser.add_option('--proxy',
                      dest='proxy',
                      help='Specifies the proxy.')

    parser.add_option('--checkEveryMinutes',
                      dest='check_every_minutes',
                      help='When used with -x sets the time in minutes between checks for your bookmarked manga.',
                      type="int")

    (options, args) = parser.parse_args()

    try:
        options.maxChapterThreads = int(options.maxChapterThreads)
    except:
        options.maxChapterThreads = 2

    if options.maxChapterThreads <= 0:
        options.maxChapterThreads = 2

    if len(args) == 0 and (not (options.json_file_path is not None)):
        parser.error('Manga not specified.')

    set_download_path_to_name_flag = False
    if len(args) > 0:
        # Default Directory is the ./MangaName
        if options.downloadPath == 'DEFAULT_VALUE':
            set_download_path_to_name_flag = True

    # Changes the working directory to the script location
    if os.path.dirname(sys.argv[0]) != "":
        os.chdir(os.path.dirname(sys.argv[0]))

    if options.json_file_path is not None:
        options.auto = True

    options.notificator = None

    try:

        downloader = MangaDownloader()
        config.__dict__.update(options.__dict__)
        del config.__dict__['downloadPath']

        if config.json_file_path is not None:
            # Load configuration from JSON file and process all manga
            json_parser = MangaJsonParser()
            while True:
                configuration = json_parser.parse_config(config.json_file_path)
                options.notificator = NotificationFactory.Instance().get_instance(configuration)
                config.__dict__.update(options.__dict__)

                downloader.download_chapters_from_config(configuration, options.downloadPath)

                json_parser.save_config(config.json_file_path, configuration)

                if not config.check_every_minutes or config.check_every_minutes < 0:
                    break

                cprint("Will check again in %s minutes" % config.check_every_minutes, 'white', attrs=['bold'], file=sys.stdout)
                time.sleep(60 * config.check_every_minutes)

        else:
            # Download manga specified in the command line parameters
            download_path = options.downloadPath
            for manga in args:
                print(manga)

                if set_download_path_to_name_flag:
                    download_path = ('./' + fix_formatting(manga, config.spaceToken))

                download_path = os.path.realpath(download_path) + os.sep

                # site selection
                print('\nWhich site?')
                for index in siteDict:
                    print('(%s) %s' % (index, siteDict[index]))

                # Python3 fix - removal of raw_input()
                try:
                    site = raw_input()
                except NameError:
                    site = input()

                try:
                    site = siteDict[site]
                except KeyError:
                    raise InvalidSite('Site selection invalid.')

                downloader.download_new_chapters(manga, site, download_path, "")

    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
