# -*- coding: utf-8 -*-

import json
import socket
import urllib.error
import urllib.request

from .compat import Discovery, feed_url


class GbfsClientError(RuntimeError):
    pass


DEFAULT_TIMEOUT_SECONDS = 20


class GbfsClient:
    def __init__(self, timeout=DEFAULT_TIMEOUT_SECONDS):
        self.timeout = timeout
        self.headers = {"User-Agent": "GBFS-NOW QGIS Plugin"}

    def get_json(self, url):
        request = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                encoding = response.headers.get_content_charset() or "utf-8"
                return json.loads(response.read().decode(encoding))
        except urllib.error.HTTPError as error:
            raise GbfsClientError("HTTP {} for {}".format(error.code, url)) from error
        except (socket.timeout, TimeoutError) as error:
            raise GbfsClientError("Timed out while loading {}".format(url)) from error
        except urllib.error.URLError as error:
            raise GbfsClientError("{}: {}".format(url, error.reason)) from error

    def load_discovery(self, url):
        raw = self.get_json(url)
        system_information = None
        system_url = feed_url(raw, "system_information")
        if system_url:
            try:
                system_information = self.get_json(system_url)
            except (GbfsClientError, ValueError):
                system_information = None
        return Discovery(url, raw, system_information)

    def get_feed(self, discovery, feed_name, language=None):
        url = discovery.feed_url(feed_name, language)
        if not url:
            return None
        return self.get_json(url)
