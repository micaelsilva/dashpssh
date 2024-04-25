#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import dashpssh.parse
from urllib.parse import urljoin, urlsplit
from dashpssh.httpclient import DefaultHTTPClient

def load(
        uri,
        psshtype=False,
        timeout=None,
        headers={},
        http_client=DefaultHTTPClient(),
        verify_ssl=True,
    ):
    if urlsplit(uri).scheme:
        content, base_uri = http_client.download(uri, timeout, headers, verify_ssl)
    else:
        with open(uri, encoding="utf8") as fileobj:
            content = fileobj.read().strip()
        base_uri = os.path.join(os.path.dirname(uri), '')
    return dashpssh.parse.parse(content, base_uri=base_uri, psshtype=psshtype)

	