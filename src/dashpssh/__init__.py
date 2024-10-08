#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import dashpssh.parse
from urllib.parse import urlsplit
from dashpssh.httpclient import DefaultHTTPClient
from urllib.error import HTTPError, URLError
from http.client import RemoteDisconnected


def load(
        uri,
        psshtype=False,
        timeout=20,
        headers=None,
        verify_ssl=True):
    """
    Load MPD and return the PSSH
    """
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42"}
    http_client = DefaultHTTPClient(headers=headers, verify_ssl=verify_ssl)
    if urlsplit(uri).scheme:
        content, base_uri = http_client.download(uri, timeout)
    else:
        with open(uri, encoding="utf8") as fileobj:
            content = fileobj.read().strip()
        base_uri = os.path.join(os.path.dirname(uri), '')
    return dashpssh.parse.parse(
        content,
        base_uri=base_uri,
        psshtype=psshtype,
        http_client=http_client)
