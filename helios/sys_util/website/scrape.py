#  -*- coding: UTF8 -*-

from __future__ import division

import requests
import ssl


def scrape_hostile_page(url):
    """
        Downloads content from a webpage that uses anti-robot countermeasures. This method works for any
        page that doesn't use JS-based browser fingerprinting.

        :param url: URL to download.
        :return: data dict
    """

    # Set the ssl module to an unverified context to stop it raising exceptions
    # when we disable SSL verification
    # ===========================================================================

    requests.packages.urllib3.disable_warnings()

    try:
        # Legacy Python that doesn't verify HTTPS certificates by default
        _create_unverified_https_context = ssl._create_unverified_context

    except AttributeError:
        pass

    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    # Try to fetch the file using requests
    # ===========================================================================

    try:

        # Use a session so that the instance stores cookies. This defeats 'set-cookie'->'redirect'->'check-cookie'
        # bot detection schemes

        s = requests.Session()

        response = s.get(

            url,
            # Stream must be True to prevent broken downloads of large pages
            stream=True,
            allow_redirects=True,

            # Disable SSL verification so requests doesn't reject broken TLS configurations. A *huge* number of
            # sites have misconfigured TLS, even big ones. Etsy, for example.

            verify=False,

            headers={

                # The headers we send are *precisely* the ones Firefox sends (with the exception of Accept-Encoding
                # (we don't accept 'deflate') and Connection (we use 'close' instead of 'keep-alive').

                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip',
                'Connection': 'close',
                'Accept-Language': 'en-US,en;q=0.5'
            }
        )

    except Exception as e:

        return {

            'exception': str(e),
            'success': False
        }

    # Check if page can be iframed
    # ===========================================================================

    can_iframe = True

    # Technically, 'X-Frame-Options' is the only valid header name in the W3C standard, but some browsers will
    # probably accept it with different capitalization, so we'll include a few possibilities.
    #
    # https://en.wikipedia.org/wiki/List_of_HTTP_header_fields#Frame-Options

    blocked_a = (response.headers.get('X-Frame-Options', 'allowall') != 'allowall')
    blocked_b = (response.headers.get('x-frame-options', 'allowall') != 'allowall')
    blocked_c = (response.headers.get('X-FRAME-OPTIONS', 'allowall') != 'allowall')

    if blocked_a or blocked_b or blocked_c:
        can_iframe = False

    # The other way they can block us iframing the page is via the 'Content-Security-Policy' header. The docs
    # on this are 4 screens long, have about thirty subcases, and in typical 'Linux spirit' contain zero examples.
    # It would take days of work to write a proper parser for this. So if we see a directive containing the string
    # 'frame-ancestors', we'll just assume its being used to block iframing.
    #
    # http://www.w3.org/TR/CSP11/#directive-frame-ancestors

    csp_header = response.headers.get('Content-Security-Policy', None)

    if csp_header and ('frame-ancestors' in csp_header):
        can_iframe = False

    # Handle the case where the Python Requests module raises an exception because the
    # remote server sends back no content, causing Requests to raise an exception

    try:
        text = response.text

    except:
        text = ""

    return {

        'success': True,
        'real_url': response.url,
        'status_code': response.status_code,
        'headers': response.headers,
        'text': text,
        'can_iframe': can_iframe
    }
