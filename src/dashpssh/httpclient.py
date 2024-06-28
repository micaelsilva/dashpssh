#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssl
import urllib.request

from urllib.parse import urljoin


class DefaultHTTPClient:
    def __init__(self, proxies=None, headers={}, verify_ssl=True):
        self.proxies = proxies
        self.verify_ssl = verify_ssl
        self.headers = headers

    def download(self, uri, timeout=None, binary=False):
        proxy_handler = urllib.request.ProxyHandler(self.proxies)
        https_handler = HTTPSHandler(verify_ssl=self.verify_ssl)
        opener = urllib.request.build_opener(proxy_handler, https_handler)
        opener.addheaders = self.headers.items()
        resource = opener.open(uri, timeout=timeout)
        base_uri = urljoin(resource.geturl(), ".")
        content = resource.read() if binary else resource.read().decode(
            resource.headers.get_content_charset(failobj="utf-8")
        )
        return content, base_uri


class HTTPSHandler:
    def __new__(self, verify_ssl=True):
        context = ssl.create_default_context()
        if not verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return urllib.request.HTTPSHandler(context=context)