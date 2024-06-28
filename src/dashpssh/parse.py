#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import xmltodict, json, time
from urllib.parse import urljoin, urlsplit
from pymp4.parser import Box
from pymp4.util import BoxUtil
from uuid import UUID
from base64 import b64encode, b64decode

from dashpssh.httpclient import DefaultHTTPClient

def pssh_kid(pssh):
    box = Box.parse(b64decode(pssh))
    for pssh_box, _ in BoxUtil.find(box, b'pssh'):
        return pssh_box.box_body.init_data[4:20].hex()

def find_wv_pssh(par):
    for t in par['ContentProtection']:
        if t['@schemeIdUri'].lower() == "urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed":
            return t["cenc:pssh"]["#text"] if isinstance(t["cenc:pssh"], dict) else t["cenc:pssh"]

def load_content(uri, http_client):
    if urlsplit(uri).scheme:
        return http_client.download(uri, binary=True)[0] # content, base_uri =
    else:
        with open(uri, "rb") as fileobj:
            content = fileobj.read()
        return content

def from_files(periods, http_client, mimeType, base_uri, psshtype):
    options = []
    if isinstance(periods, list):
        periods = periods[-1]
    for ad_set in periods['AdaptationSet']:
        if ad_set['@mimeType'] == mimeType:
            rep_set = ""
            if isinstance(ad_set['Representation'], list):
                for t in ad_set['Representation']:
                    rep_set = t
            else:
                rep_set = ad_set['Representation']

            items_params = list( ad_set['SegmentTemplate']['SegmentTimeline'].items() )[0][1]
            
            rep_set["init"] = urljoin(base_uri, ad_set['SegmentTemplate']['@initialization'].replace("$RepresentationID$", rep_set['@id']))

            if psshtype == "firstsegment":
                if isinstance(items_params, dict):
                    rep_set["segments"] = [urljoin(base_uri, ad_set['SegmentTemplate']['@media'].replace("$RepresentationID$", rep_set['@id']).replace("$Time$", items_params['@t']))]
                else:
                    rep_set["segments"] = [urljoin(base_uri, ad_set['SegmentTemplate']['@media'].replace("$RepresentationID$", rep_set['@id']).replace("$Time$", items_params[0]['@t']))]

            if psshtype == "segments":
                if isinstance(items_params, dict):
                    rep_set["segments"] = [ urljoin(base_uri, ad_set['SegmentTemplate']['@media'].replace("$RepresentationID$", rep_set['@id']).replace("$Time$", items_params['@t'])) ]
                else:
                    rep_set["segments"] = [ urljoin(base_uri, ad_set['SegmentTemplate']['@media'].replace("$RepresentationID$", rep_set['@id']).replace("$Time$", i['@t'])) for i in items_params ]

            options.append( rep_set )

    pssh = set()

    match psshtype:
        case "firstsegment":
            urls = [ options[-1]['segments'][0] ]
        case "segments":
            urls = options[-1]['segments']
        case _:
            urls = [ options[-1]['init'] ]

    for i in urls:
        content = load_content(i, http_client)
        
        pos = 0
        init_data = None
        init_segment = b''
        data = content
        while data[pos:]:
            if init_data is None:
                try:
                    box = Box.parse(data[pos:])
                except Exception as e:
                    #print(e)
                    break
                else:
                    if box.type in [b'moov', b'moof']:
                        for pssh_box, _ in BoxUtil.find(box, b'pssh'):
                            if pssh_box.box_body.system_ID == UUID('edef8ba9-79d6-4ace-a3c8-27dcd51d21ed'):
                                pssh.add(b64encode(Box.build(pssh_box)).decode("utf-8"))
                    else:
                        init_segment += data[pos : pos + box.length]
                    pos += box.length
            else:
                init_segment += data[pos:]
                break
        time.sleep(1)
    return pssh

def parse(content, base_uri=None, psshtype=False, http_client=False, mediatype="video"):
    if mediatype == "video":
        mimeType = 'video/mp4'
    elif mediatype == "audio":
        mimeType = 'audio/mp4'
        
    pssh = set()
    try:
        #r = s.get(url=mpd_url)
        #r.raise_for_status()
        xml = xmltodict.parse(content)
        mpd = json.loads(json.dumps(xml))
        periods = mpd['MPD']['Period']
    except Exception as e:
        return False
    try: 
        if isinstance(periods, list):
            for idx, period in enumerate(periods):
                if isinstance(period['AdaptationSet'], list):
                    for ad_set in period['AdaptationSet']:
                        if ad_set['@mimeType'] == mimeType:
                            try:
                                t = find_wv_pssh(ad_set)
                                if t != None:
                                    pssh.add(t)

                            except Exception as e:
                                pass
                            try:
                                for rep_set in ad_set['Representation']:
                                    t = find_wv_pssh(rep_set)
                                    if t != None:
                                        pssh.add(t)
                            except Exception as e:
                                pass 
                else:
                    if period['AdaptationSet']['@mimeType'] == mimeType:
                        try:
                            t = find_wv_pssh(period['AdaptationSet'])
                            if t != None:
                                pssh.add(t)
                        except Exception:
                            pass   
        else:
            for ad_set in periods['AdaptationSet']:
                if ad_set['@mimeType'] == 'video/mp4':
                    try:
                        t = find_wv_pssh(ad_set)
                        if t != None:
                            pssh.add(t)
                    except Exception:
                        pass

                    try:
                        for rep_set in ad_set['Representation']:
                            t = find_wv_pssh(rep_set)
                            if t != None:
                                pssh.add(t)
                    except Exception:
                        pass 
    except Exception:
        pass                      
    if not pssh:
        pssh = from_files(periods, http_client, mimeType, base_uri, psshtype)
    return pssh

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(prog='pssh', description='Parse PSSH from DASH manifests')
    parser.add_argument('--rotation', action='store_true', default=False, help='If true look out for PSSH boxes in the fragments, used in rotation key schemes')
    parser.add_argument('--mpd', default=False, help='URL of the manifest MPD')
    parser.add_argument('--kid', action='store_true', default=False, help='print KID from PSSH')
    parser.add_argument('--headers', default=False, help='Pass headers to the MPD request. Use: \'Referer=https://somesite.com/&Origin=https://somesite.com/\'')
    args = parser.parse_args()

    head = {x.split("=", 1)[0]: x.split("=", 1)[1] for x in args.headers.split("&")} if args.headers else False

    if args.mpd:
        pssh = parse(args.mpd, psshtype=args.rotation, http_client=DefaultHTTPClient(headers=head) )
        if args.kid:
            for i in pssh:
                print( pssh_kid(i) )
        else:
            print (pssh)
