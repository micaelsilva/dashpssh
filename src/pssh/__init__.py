#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pssh.parse
from urllib.parse import urljoin, urlsplit
from pssh.httpclient import DefaultHTTPClient

def load(
	    uri,
	    firstsegment=False,
	    timeout=None,
	    headers={},
	    http_client=DefaultHTTPClient(),
	    verify_ssl=True,
	):
    if urlsplit(uri).scheme:
        content, base_uri = http_client.download(uri, timeout, headers, verify_ssl)
        return pssh.parse.parse(content, base_uri=base_uri, firstsegment=firstsegment)
    else:
    	pass
        #return _load_from_file(uri)
