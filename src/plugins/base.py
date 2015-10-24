#!/usr/bin/env python

# ####################

import imghdr
import os
import shutil
import tempfile
import zipfile
import traceback
import requests
# import urllib

# ####################

from util.util import *

# ####################


class SiteParserBase:
    # ####
    # typical misspelling of title and/or manga removal
    class MangaNotFound(Exception):

        def __init__(self, error_msg=''):
            self.error_msg = 'Manga not found. %s' % error_msg

        def __str__(self):
            return self.error_msg

    class MangaLicenced(Exception):

        def __init__(self, error_msg=''):
            self.error_msg = 'Manga was licenced and removed from the site. %s' % error_msg

        def __str__(self):
            return self.error_msg

    # XML file config reports nothing to do
    class NoUpdates(Exception):

        def __init__(self, error_msg=''):
            self.error_msg = 'No updates. %s' % error_msg

        def __str__(self):
            return self.error_msg

            # ####

    def __init__(self, options, base_url):
        self.base_url = base_url
        self.options = options
        self.chapters = []
        self.chapters_to_download = []
        self.temp_folder = tempfile.mkdtemp()
        self.garbage_images = {}
        self.output_idx = None

        # should be defined by subclasses
        self.re_get_image = None
        self.re_get_max_pages = None

    # this takes care of removing the temp directory after the last successful download
    def __del__(self):
        try:
            shutil.rmtree(self.temp_folder)
        except:
            pass
        if len(self.garbage_images) > 0:
            print('\nSome images were not downloaded due to unavailability on the site or temporary ip banning:\n')
            for elem in self.garbage_images.keys():
                print('Manga keyword: %s' % elem)
                print('Pages: %s' % self.garbage_images[elem])
                # ####

    def download_chapter(self, max_pages, url, manga_chapter_prefix, current_chapter):
        raise NotImplementedError('Should have implemented this')

    def parse_site(self):
        raise NotImplementedError('Should have implemented this')

    def get_manga_url(self):
        raise NotImplementedError('Should have implemented this')

    # ####

    def compress(self, manga_chapter_prefix, max_pages):
        """
        Looks inside the temporary directory and zips up all the image files.
        """
        if self.options.verbose_FLAG:
            print('Compressing...')

        compressed_file = os.path.join(self.temp_folder, manga_chapter_prefix) + self.options.downloadFormat

        z = zipfile.ZipFile(compressed_file, 'w')

        for page in range(1, max_pages + 1):
            temp_path = os.path.join(self.temp_folder, manga_chapter_prefix + '_' + str(page).zfill(3))
            # we got an image file
            if os.path.exists(temp_path) is True and imghdr.what(temp_path) is not None:
                z.write(temp_path, manga_chapter_prefix + '_' + str(page).zfill(3) + '.' + imghdr.what(temp_path))
            # site has thrown a 404 because image unavailable or using anti-leeching
            else:
                if manga_chapter_prefix not in self.garbage_images:
                    self.garbage_images[manga_chapter_prefix] = [page]
                else:
                    self.garbage_images[manga_chapter_prefix].append(page)

        z.close()

        if self.options.overwrite_FLAG:
            prior_path = os.path.join(self.options.downloadPath, manga_chapter_prefix) + self.options.downloadFormat
            if os.path.exists(prior_path):
                os.remove(prior_path)

        shutil.move(compressed_file, self.options.downloadPath)

        # The object conversionQueue (singleton) stores the path to every compressed file that
        # has been downloaded. This object is used by the conversion code to convert the downloaded images
        # to the format specified by the Device errorMsg

        compressed_file = os.path.basename(compressed_file)
        compressed_file = os.path.join(self.options.downloadPath, compressed_file)
        return compressed_file

    def parse_image_page(self, page, page_url, manga_chapter_prefix, max_pages, current_chapter):
        """
        Given a page URL to download from, it searches using self.imageRegex
        to parse out the image URL, and downloads and names it using
        manga_chapter_prefix and page.
        """

        # while loop to protect against server denies for requests
        # note that disconnects are already handled by getSourceCode, we use a
        # regex to parse out the image URL and filter out garbage denies
        max_retries = 5
        wait_retry_time = 5
        while True:
            try:
                if self.options.verbose_FLAG:
                    print(page_url)
                source_code = get_source_code(page_url, self.options.proxy)
                img_url = self.__class__.re_get_image.search(source_code).group(1)
                if self.options.verbose_FLAG:
                    print("Image URL: %s" % img_url)
            except (AttributeError, TypeError):
                if max_retries == 0:
                    if not self.options.verbose_FLAG:
                        self.options.outputMgr.update_output_obj(self.output_idx)
                    return
                else:
                    # random dist. for further protection against anti-leech
                    # idea from wget
                    time.sleep(random.uniform(0.5 * wait_retry_time, 1.5 * wait_retry_time))
                    max_retries -= 1
            else:
                break

        self.download_image(page, img_url, manga_chapter_prefix, max_pages, current_chapter)

    def download_image(self, page, img_url, manga_chapter_prefix, max_pages, current_chapter):

        if self.options.verbose_FLAG:
            print(self.chapters[current_chapter][1] + ' | ' + 'Page %s / %i' % (page, max_pages))

        if not img_url.startswith('https://') and not img_url.startswith('http://'):
            img_url = 'http://' + img_url

        # Loop to protect against server denies for requests and/or minor disconnects
        while True:
            try:
                temp_path = os.path.join(self.temp_folder, manga_chapter_prefix + '_' + str(page).zfill(3))

                r = requests.get(img_url, timeout=10)
                with open(temp_path, "wb") as code:
                    code.write(r.content)
                    # urllib.urlretrieve(img_url, temp_path)
            except IOError:
                pass
            else:
                break
        if not self.options.verbose_FLAG and self.output_idx:
            self.options.outputMgr.update_output_obj(self.output_idx)

    def process_chapter(self, current_chapter):
        """
        Calculates prefix for filenames, creates download directory if
        nonexistent, checks to see if chapter previously downloaded, returns
        data critical to downloadChapter()
        """

        # Clean name with space token replacement
        clean_name = fix_formatting(self.options.manga, self.options.spaceToken)

        # Do not need to ZeroFill the manga name because this should be consistent
        # MangaFox already prepends the manga name
        if self.options.useShortName_FLAG:
            manga_chapter_prefix = clean_name + self.options.spaceToken + '-' + self.options.spaceToken + zero_fill_str(
                fix_formatting(self.chapters[current_chapter][2], self.options.spaceToken), 3)
        else:
            manga_chapter_prefix = clean_name + '.' + self.options.site + '.' + zero_fill_str(
                fix_formatting(self.chapters[current_chapter][1].encode('utf-8'), self.options.spaceToken), 3)

        # we already have it
        if os.path.exists(os.path.join(self.options.downloadPath, manga_chapter_prefix) + self.options.downloadFormat) \
                and not self.options.overwrite_FLAG:
            print(
                self.chapters[current_chapter][1].encode('utf-8') + ' already downloaded, skipping to next chapter...')
            return

        if self.options.timeLogging_FLAG:
            print(manga_chapter_prefix + " (Start Time): " + str(time.time()))
        # get the URL of the chapter homepage
        url = self.chapters[current_chapter][0]

        # mangafox .js sometimes leaves up invalid chapters
        if url is None:
            return

        if self.options.verbose_FLAG:
            print("PrepareDownload: " + url)

        source = get_source_code(url, self.options.proxy)

        max_pages = int(self.__class__.re_get_max_pages.search(source).group(1))

        if self.options.verbose_FLAG:
            print ("Pages: " + str(max_pages))
        if not self.options.verbose_FLAG:
            self.output_idx = self.options.outputMgr.create_output_obj(manga_chapter_prefix, max_pages)

        self.download_chapter(max_pages, url, manga_chapter_prefix, current_chapter)

        # Post processing
        # Release locks/semaphores
        # Zip Them up
        self.post_download_processing(manga_chapter_prefix, max_pages)

    def select_chapters(self, chapters):
        """
        Prompts user to select list of chapters to be downloaded from total list.
        """

        # this is the array form of the chapters we want
        chapter_array = []

        input_chapter_string = 'all'
        if not self.options.all_chapters_FLAG:
            input_chapter_string = raw_input('\nDownload which chapters?\n')

        if self.options.all_chapters_FLAG or input_chapter_string.lower() == 'all':
            print('\nDownloading all chapters...')
            for i in range(0, len(chapters)):
                chapter_array.append(i)
        else:
            # parsing user input

            # ignore whitespace, split using comma delimiters
            chapter_list_array = input_chapter_string.replace(' ', '').split(',')

            for i in chapter_list_array:
                iteration = re.search('([0-9]*)-([0-9]*)', i)

                # it's a range
                if iteration is not None:
                    for j in range(int(iteration.group(1)), int(iteration.group(2)) + 1):
                        chapter_array.append(j - 1)
                # it's a single chapter
                else:
                    chapter_array.append(int(i) - 1)
        return chapter_array

    def select_from_results(self, results):
        """
        Basic error checking for manga titles, queries will return a list of all mangas that
        include the query, case-insensitively.
        """

        found = False

        # Translate the manga name to lower case
        # Need to handle if it contains NonASCII characters
        actual_name = (self.options.manga.decode('utf-8')).lower()

        # each element in results is a 2-tuple
        # elem[0] contains a keyword or string that needs to be passed back (generally the URL to the manga homepage)
        # elem[1] contains the manga name we'll be using
        # When asking y/n, we pessimistically only accept 'y'

        for elem in results:
            proposed_name = (elem[1].decode('utf-8')).lower()

            if actual_name in proposed_name:
                # manual mode
                if not self.options.auto:
                    print(elem[1])

                # exact match
                if proposed_name == actual_name:
                    self.options.manga = elem[1]
                    keyword = elem[0]
                    found = True
                    break
                else:
                    # only request input in manual mode
                    if not self.options.auto:
                        print('Did you mean: %s? (y/n)' % elem[1])
                        answer = raw_input()

                        if answer == 'y':
                            self.options.manga = elem[1]
                            keyword = elem[0]
                            found = True
                            break
        if not found:
            raise self.MangaNotFound('No strict match found. Check query.')
        return keyword

    def download(self):
        """
        for loop that goes through the chapters we selected.
        """
        for current_chapter in self.chapters_to_download:
            self.process_chapter(current_chapter)

    def post_download_processing(self, manga_chapter_prefix, max_pages):
        if self.options.timeLogging_FLAG:
            print("%s (End Time): %s" % (manga_chapter_prefix, str(time.time())))

        self.compress(manga_chapter_prefix, max_pages)

        if self.options.notificator:
            self.options.notificator.push_note("MangaDownloader: %s finished downloading" % manga_chapter_prefix,
                                               "%s finished downloading" % manga_chapter_prefix)
