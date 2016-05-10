#!/usr/bin/env python

# ####################

import tempfile
import os
import config



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

    class ErrorDownloading(Exception):

        def __init__(self, error_msg=''):
            self.error_msg = 'Error downloading. %s' % error_msg

        def __str__(self):
            return self.error_msg

    class MangaLicenced(Exception):

        def __init__(self, error_msg=''):
            self.error_msg = 'Manga was licenced and removed from the site. %s' % error_msg

        def __str__(self):
            return self.error_msg

    # File config reports nothing to do
    class NoUpdates(Exception):

        def __init__(self, error_msg=''):
            self.error_msg = 'No updates. %s' % error_msg

        def __str__(self):
            return self.error_msg

    def __init__(self, base_url, site):
        self.base_url = base_url
        self.temp_folder = tempfile.mkdtemp()
        self.site = site

        # should be defined by subclasses
        self.re_get_image = None

    # this takes care of removing the temp directory after the last successful download
    def __del__(self):
        try:
            shutil.rmtree(self.temp_folder)
        except:
            pass

    def download_chapter(self, url, manga_chapter_prefix, current_chapter):
        raise NotImplementedError('Should have implemented this')

    def parse_chapters(self):
        raise NotImplementedError('Should have implemented this')

    def get_manga_url(self):
        raise NotImplementedError('Should have implemented this')

    def get_max_pages(self, url):
        raise NotImplementedError('Should have implemented this')

    def select_chapters_to_download(self, chapters, last_downloaded):
		# Look for first chapter that should be downloaded in auto mode
        lower_range = 0
        if config.auto:
            for row in range(0, len(chapters)):
                if last_downloaded == chapters[row]['chapter']:
                    lower_range = row + 1

        upper_range = len(chapters)

        chapters_to_download = []

        # which ones do we want?
        if not config.auto:
            for n, chapter in enumerate(chapters):
                print("{:03d}. {}".format(n + 1, chapter['title'].encode('utf-8')))
            chapters_to_download = self.select_chapters(chapters)
        # XML component
        else:
            if lower_range == upper_range:
                raise self.NoUpdates

            for row in range(lower_range, upper_range):
                chapters_to_download.append(row)

        return chapters_to_download

    def select_chapters(self, chapters):
        """
        Prompts user to select list of chapters to be downloaded from total list.
        """

        # this is the array form of the chapters we want
        chapter_array = []

        input_chapter_string = 'all'
        if not config.all_chapters_FLAG:
            input_chapter_string = raw_input('\nDownload which chapters?\n')

        if config.all_chapters_FLAG or input_chapter_string.lower() == 'all':
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

    def select_from_results(self, results, manga):
        """
        Basic error checking for manga titles, queries will return a list of all mangas that
        include the query, case-insensitively.
        """

        found = False

        # Translate the manga name to lower case
        # Need to handle if it contains NonASCII characters
        actual_name = (manga.decode('utf-8')).lower()

        # each element in results is a 2-tuple
        # elem[0] contains a keyword or string that needs to be passed back (generally the URL to the manga homepage)
        # elem[1] contains the manga name we'll be using
        # When asking y/n, we pessimistically only accept 'y'

        for elem in results:
            proposed_name = (elem[1].decode('utf-8')).lower()

            if actual_name in proposed_name:
                # manual mode
                if not config.auto:
                    print(elem[1])

                # exact match
                if proposed_name == actual_name:
                    manga = elem[1]
                    keyword = elem[0]
                    found = True
                    break
                else:
                    # only request input in manual mode
                    if not config.auto:
                        print('Did you mean: %s? (y/n)' % elem[1])
                        answer = raw_input()

                        if answer == 'y':
                            manga = elem[1]
                            keyword = elem[0]
                            found = True
                            break
        if not found:
            raise self.MangaNotFound('No strict match found. Check query.')
        return keyword

    # ####

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
                if config.verbose_FLAG:
                    print(page_url)
                source_code = get_source_code(page_url, config.proxy)
                img_url = self.__class__.re_get_image.search(source_code).group(1)
                if 'ucredits' in img_url:
                    return
                if config.verbose_FLAG:
                    print("Image URL: %s" % img_url)
            except (AttributeError, TypeError):
                if max_retries == 0:
                    temp_path = os.path.join(self.temp_folder, manga_chapter_prefix + '_' + str(page).zfill(3))
                    raise self.ErrorDownloading(temp_path)
                else:
                    # random dist. for further protection against anti-leech
                    # idea from wget
                    time.sleep(random.uniform(0.5 * wait_retry_time, 1.5 * wait_retry_time))
                    max_retries -= 1
            else:
                break

        self.download_image(page, img_url, manga_chapter_prefix, max_pages, current_chapter)

    def download_image(self, page, img_url, manga_chapter_prefix, max_pages, current_chapter):

        if config.verbose_FLAG:
            print(current_chapter['title'] + ' | ' + 'Page %s / %i' % (page, max_pages))

        if not img_url.startswith('https://') and not img_url.startswith('http://'):
            img_url = 'http://' + img_url

        # Loop to protect against server denies for requests and/or minor disconnects
        while True:
            try:
                temp_path = os.path.join(self.temp_folder, manga_chapter_prefix + '_' + str(page).zfill(3))

                r = requests.get(img_url, timeout=180)
                with open(temp_path, "wb") as code:
                    code.write(r.content)
                    # urllib.urlretrieve(img_url, temp_path)
                if os.path.getsize(temp_path) <= 0:
                    raise self.ErrorDownloading(temp_path)
            except IOError:
                pass
            else:
                break

    def process_chapter(self, current_chapter, manga, download_path):
        """
        Calculates prefix for filenames, creates download directory if
        nonexistent, checks to see if chapter previously downloaded, returns
        data critical to downloadChapter()
        """

        # Clean name with space token replacement
        clean_name = fix_formatting(manga, config.spaceToken)

        # Do not need to ZeroFill the manga name because this should be consistent
        if config.useShortName_FLAG:
            manga_chapter_prefix = clean_name + config.spaceToken + '-' + config.spaceToken + zero_fill_str(
                fix_formatting(current_chapter['chapter'], config.spaceToken), 3)
        else:
            manga_chapter_prefix = clean_name + '.' + self.site + '.' + zero_fill_str(
                fix_formatting(current_chapter['title'].encode('utf-8'), config.spaceToken), 3)

        # we already have it
        if os.path.exists(os.path.join(download_path, manga_chapter_prefix) + config.downloadFormat) \
                and not config.overwrite_FLAG:
            print(
                current_chapter['title'].encode('utf-8') + ' already downloaded, skipping to next chapter...')
            return

        if config.timeLogging_FLAG:
            print(manga_chapter_prefix + " (Start Time): " + str(time.time()))

        # get the URL of the chapter homepage
        url = current_chapter['url']

        if config.verbose_FLAG:
            print("PrepareDownload: " + url)

        self.download_chapter(url, manga_chapter_prefix, current_chapter)
        self.post_download_processing(manga_chapter_prefix, download_path)

    # Post process download by compressing and sending necesary notifications
    def post_download_processing(self, manga_chapter_prefix, download_path):
        if config.timeLogging_FLAG:
            print("%s (End Time): %s" % (manga_chapter_prefix, str(time.time())))

        compress(self.temp_folder, manga_chapter_prefix, download_path, config.downloadFormat, config.overwrite_FLAG)

        if config.notificator:
            config.notificator.push_note("MangaDownloader: %s finished downloading" % manga_chapter_prefix,
                                               "%s finished downloading" % manga_chapter_prefix)
