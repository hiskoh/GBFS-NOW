# -*- coding: utf-8 -*-

import http.client
import json
import socket
from urllib.parse import urljoin, urlsplit

from .compat import Discovery, feed_url


class GbfsClientError(RuntimeError):
    pass


DEFAULT_TIMEOUT_SECONDS = 20
ALLOWED_URL_SCHEMES = frozenset(("http", "https"))
MAX_REDIRECTS = 5
REDIRECT_STATUS_CODES = frozenset((301, 302, 303, 307, 308))


def validate_http_url(url):
    value = str(url or "").strip()
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in ALLOWED_URL_SCHEMES or not parsed.netloc:
        raise GbfsClientError("Only HTTP(S) URLs with a host are supported: {}".format(value))
    return value


class GbfsClient:
    def __init__(self, timeout=DEFAULT_TIMEOUT_SECONDS):
        self.timeout = timeout
        self.headers = {"User-Agent": "GBFS-NOW QGIS Plugin"}

    def get_json(self, url):
        return json.loads(self.get_text(url))

    def get_text(self, url):
        content, encoding = self._get_response(url)
        return content.decode(encoding)

    def _get_response(self, url):
        current_url = validate_http_url(url)
        for _ in range(MAX_REDIRECTS + 1):
            parsed = urlsplit(current_url)
            connection_class = (
                http.client.HTTPSConnection
                if parsed.scheme.lower() == "https"
                else http.client.HTTPConnection
            )
            connection = connection_class(parsed.hostname, parsed.port, timeout=self.timeout)
            request_target = parsed.path or "/"
            if parsed.query:
                request_target = "{}?{}".format(request_target, parsed.query)
            try:
                connection.request("GET", request_target, headers=self.headers)
                response = connection.getresponse()
                try:
                    encoding = response.headers.get_content_charset() or "utf-8"
                    content = response.read()
                    location = response.getheader("Location")
                finally:
                    response.close()
            except (socket.timeout, TimeoutError) as error:
                raise GbfsClientError("Timed out while loading {}".format(current_url)) from error
            except (http.client.HTTPException, OSError) as error:
                raise GbfsClientError("{}: {}".format(current_url, error)) from error
            finally:
                connection.close()

            if response.status in REDIRECT_STATUS_CODES and location:
                current_url = validate_http_url(urljoin(current_url, location))
                continue
            if response.status >= 400:
                raise GbfsClientError("HTTP {} for {}".format(response.status, current_url))
            return content, encoding

        raise GbfsClientError("Too many redirects while loading {}".format(url))

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
