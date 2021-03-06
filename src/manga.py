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
import copy
import os.path

from colorama import init

from plugins.factory import SiteParserFactory





# #########

from manga_downloader import MangaDownloader
from util.util import fix_formatting, is_image_lib_available
from json_parser import MangaJsonParser
from output_manager.progress_bar_manager import ProgressBarManager

# #########

VERSION = 'v0.8.8'
siteDict = {}

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

    #Load available plugins
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
        conversion_FLAG=False,
        convert_Directory=False,
        device='Kindle 3',
        downloadFormat='.cbz',
        downloadPath='DEFAULT_VALUE',
        inputDir=None,
        outputDir='DEFAULT_VALUE',
        overwrite_FLAG=False,
        verbose_FLAG=False,
        timeLogging_FLAG=False,
        maxChapterThreads=3,
        useShortName=False,
        spaceToken='.',
        proxy=None,
        check_every_minutes=-1,
        no_progress_bars=False
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

    parser.add_option('-c', '--convertFiles',
                      action='store_true',
                      dest='conversion_FLAG',
                      help='Converts downloaded files to a Format/Size acceptable to the device specified by the '
                           '--device parameter.')

    parser.add_option('--device',
                      dest='device',
                      help='Specifies the conversion device. Omitting this option default to %default.')

    parser.add_option('--convertDirectory',
                      action='store_true',
                      dest='convert_Directory',
                      help='Converts the image files stored in the directory specified by --inputDirectory. Stores the '
                           'converted images in the directory specified by --outputDirectory')

    parser.add_option('--inputDirectory',
                      dest='inputDir',
                      help='The directory containing the images to convert when --convertDirectory is specified.')

    parser.add_option('--outputDirectory',
                      dest='outputDir',
                      help='The directory to store the images when --convertDirectory is specified.')

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

    parser.add_option('--noProgressBars',
                      action='store_true',
                      dest='no_progress_bars',
                      help='Disable progress bars.')

    (options, args) = parser.parse_args()

    try:
        options.maxChapterThreads = int(options.maxChapterThreads)
    except:
        options.maxChapterThreads = 2

    if options.maxChapterThreads <= 0:
        options.maxChapterThreads = 2

    if len(args) == 0 and (not (options.convert_Directory or options.json_file_path is not None)):
        parser.error('Manga not specified.')

    set_download_path_to_name_flag = False
    set_output_path_to_default_flag = False
    if len(args) > 0:

        # Default Directory is the ./MangaName
        if options.downloadPath == 'DEFAULT_VALUE':
            set_download_path_to_name_flag = True

        # Default outputDir is the ./MangaName
        if options.outputDir == 'DEFAULT_VALUE':
            set_output_path_to_default_flag = True

    pil_available = is_image_lib_available()
    # Check if PIL Library is available if either of convert Flags are set
    if (not pil_available) and (options.convert_Directory or options.conversion_FLAG):
        print ("\nConversion Functionality Not available.\nMust install the PIL (Python Image Library)")
        sys.exit()
    elif pil_available:
        from convert.convert_file import ConvertFile

    if options.convert_Directory:
        options.inputDir = os.path.abspath(options.inputDir)

    # Changes the working directory to the script location
    if os.path.dirname(sys.argv[0]) != "":
        os.chdir(os.path.dirname(sys.argv[0]))

    options.notificator = None
    options.outputMgr = ProgressBarManager()
    if not options.no_progress_bars:
        options.outputMgr.start()

    try:
        if options.convert_Directory:
            if options.outputDir == 'DEFAULT_VALUE':
                options.outputDir = '.'
            print("Converting Files: %s" % options.inputDir)
            ConvertFile.convert(options.outputMgr, options.inputDir, options.outputDir, options.device,
                                options.verbose_FLAG)

        elif options.json_file_path is not None:
            json_parser = MangaJsonParser(options)
            json_parser.download_manga()
        else:
            for manga in args:
                series_options = copy.copy(options)
                print(manga)
                series_options.manga = manga

                if set_download_path_to_name_flag:
                    series_options.downloadPath = (
                        './' + fix_formatting(series_options.manga, series_options.spaceToken))

                if set_output_path_to_default_flag:
                    series_options.outputDir = series_options.downloadPath

                series_options.downloadPath = os.path.realpath(series_options.downloadPath) + os.sep

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
                    series_options.site = siteDict[site]
                except KeyError:
                    raise InvalidSite('Site selection invalid.')

                serie = MangaDownloader(series_options)
                serie.download_new_chapters()

    except KeyboardInterrupt:
        sys.exit(0)

    finally:
        # Must always stop the manager
        if not options.no_progress_bars:
            options.outputMgr.stop()


if __name__ == '__main__':
    main()
