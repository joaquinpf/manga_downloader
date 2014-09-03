#!/usr/bin/env python

# ###################

import gzip
import io
import random
import re
import string
import time
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


def fix_formatting(s, space_token):
    """
    Special character fix for filesystem paths.
    """

    for i in string.punctuation:
        if i not in IGNORE_CHARS and i != space_token:
            s = s.replace(i, '')
    return s.lstrip(space_token).strip().replace(' ', space_token)


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
                return ret, requested_url.geturl()
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
