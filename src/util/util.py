#!/usr/bin/env python

# ###################

import random
import re
import os
import string
import time
import imghdr
import zipfile
import shutil
import glob

import requests

try:
    import socks
    NO_SOCKS = False
except ImportError:
    NO_SOCKS = True
import socket
# ##################

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

# ###################

# overwrite user agent for spoofing, enable GZIP
urlReqHeaders = {'User-agent': """Mozilla/5.0 (X11; U; Linux i686;
                    en-US) AppleWebKit/534.3 (KHTML, like
                    Gecko) Chrome/6.0.472.14 Safari/534.3""",
                 'Accept-encoding': 'gzip'}

# ###################


# something seriously wrong happened
class FatalError(Exception):
    pass


IGNORE_CHARS = ['-', '(', '!', ')', '.']


def fix_formatting(s, space_token, remove_special_chars=True, lower_case=False, use_ignore_chars=True):
    """
    Special character fix for filesystem paths.
    """

    formatted = s.lstrip(space_token).strip().replace(' ', space_token)

    if remove_special_chars:
        for i in string.punctuation:
            if (i not in IGNORE_CHARS or not use_ignore_chars) and i != space_token:
                formatted = formatted.replace(i, '')

    return formatted.lower() if lower_case else formatted


def get_source_code(url, proxy, return_redirect_url=False, max_retries=3, wait_retry_time=3):
    """
    Loop to get around server denies for info or minor disconnects.
    """
    if proxy is not None:
        if NO_SOCKS:
            raise FatalError('socks library required to use proxy (e.g. SocksiPy)')
        proxy_settings = proxy.split(':')
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, proxy_settings[0], int(proxy_settings[1]), True)
        socket.socket = socks.socksocket

    global urlReqHeaders

    ret = None
    requested_url = None

    while ret is None:
        try:
            requested_url = requests.get(url, timeout=10)
            ret = requested_url.content

        except KeyboardInterrupt:
            raise

        except Exception:
            if max_retries == 0:
                break
            else:
                # random dist. for further protection against anti-leech
                # idea from wget
                time.sleep(random.uniform(0.5 * wait_retry_time, 1.5 * wait_retry_time))
                max_retries -= 1
        finally:
            if return_redirect_url:
                if requested_url.is_redirect:
                    return ret, requested_url.url
                else:
                    return ret, url
            else:
                return ret


def is_image_lib_available():
    try:
        from convert.convert_file import ConvertFile

        return True
    except ImportError:
        return False


def zero_fill_str(input_string, num_of_zeros):
    return re.sub('\d+',
                  lambda match_obj:
                  # string formatting trick to zero-pad
                  ('%0' + str(num_of_zeros) + 'i') % int(match_obj.group(0)),
                  input_string)


def is_site_up(url):
    resp = requests.head(url)
    return True if resp.status_code in [200, 301, 302] else False


def compress(temp_folder, manga_chapter_prefix, download_path, format, overwrite):
    """
    Looks inside the temporary directory and zips up all the image files.
    """
    compressed_file = os.path.join(temp_folder, manga_chapter_prefix) + format

    z = zipfile.ZipFile(compressed_file, 'w')
    pages = [f for f in os.listdir(temp_folder) if re.match(re.escape(manga_chapter_prefix) + '_.*', f)]
    for page in pages:
        page_path = os.path.join(temp_folder, page)
        if not os.path.exists(page_path):
            continue
        img_type = imghdr.what(page_path)
        if not img_type:
            continue
        z.write(page_path, page + '.' + img_type)

    z.close()

    if overwrite:
        prior_path = os.path.join(download_path, manga_chapter_prefix) + format
        if os.path.exists(prior_path):
            os.remove(prior_path)

    shutil.move(compressed_file, download_path)

    # The object conversionQueue (singleton) stores the path to every compressed file that
    # has been downloaded. This object is used by the conversion code to convert the downloaded images
    # to the format specified by the Device errorMsg

    compressed_file = os.path.basename(compressed_file)
    compressed_file = os.path.join(download_path, compressed_file)
    return compressed_file