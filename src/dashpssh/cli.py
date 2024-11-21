#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import dashpssh
from dashpssh.httpclient import DefaultHTTPClient


def dump():
    parser = argparse.ArgumentParser(
        prog='dashpssh',
        description='Parse PSSH from DASH manifests')
    parser.add_argument(
        '--mpd',
        default=False,
        help='URL of the manifest MPD')
    parser.add_argument(
        '-r',
        '--rotation',
        action='store_true',
        default=False,
        help='If true look out for PSSH boxes in the fragments, used in rotation key schemes')
    parser.add_argument(
        '-k',
        '--kid',
        action='store_true',
        default=False,
        help='print KID from PSSH')
    parser.add_argument(
        '--headers',
        default=False,
        help='Pass headers to the MPD request. Use: \'Referer=https://somesite.com/&Origin=https://somesite.com/\'')
    args = parser.parse_args()

    head = {
        x.split("=", 1)[0]: x.split("=", 1)[1] for x in args.headers.split("&")
    } if args.headers else False

    if args.mpd:
        pssh = dashpssh.parse.parse(
            args.mpd,
            psshtype=args.rotation,
            http_client=DefaultHTTPClient(headers=head))
        if args.kid:
            for i in pssh:
                print(dashpssh.parse.pssh_kid(i))
        else:
            print(pssh)
