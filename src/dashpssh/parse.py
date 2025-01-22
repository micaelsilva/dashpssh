#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmltodict
import json
import time
import logging
from urllib.parse import urljoin, urlsplit
from uuid import UUID
from base64 import b64encode, b64decode
from enum import Enum

from pymp4.parser import Box
from pymp4.util import BoxUtil

# from dashpssh.httpclient import DefaultHTTPClient

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


WV_UUID = "edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"


class PsshType(Enum):
    MANIFEST = "manifest"
    INIT = "init"
    FIRSTSEGMENT = "firstsegment"
    SEGMENTS = "segments"


class MimeType(Enum):
    VIDEO = "video/mp4"
    AUDIO = "audio/mp4"


def pssh_kid(pssh) -> str:
    """
    Return KID from parsing the PSSH
    """
    box = Box.parse(b64decode(pssh))
    for pssh_box, _ in BoxUtil.find(box, b'pssh'):
        return pssh_box.box_body.init_data[4:20].hex()


def find_wv_pssh(par: dict, set_: set) -> None:
    """
    Find a WV PSSH and return
    """
    for item in par['ContentProtection']:
        if item['@schemeIdUri'].lower() == f"urn:uuid:{WV_UUID}":
            set_.add(item["cenc:pssh"]["#text"] if isinstance(item["cenc:pssh"], dict) else item["cenc:pssh"])


def load_content(uri, http_client) -> str:
    """
    Load a file to parse
    """
    if urlsplit(uri).scheme:
        return http_client.download(uri, binary=True)[0]
    else:
        with open(uri, "rb") as fileobj:
            content = fileobj.read()
        return content


def from_files(
        periods,
        http_client,
        mediatype,
        base_uri,
        psshtype=PsshType.MANIFEST) -> str:
    """
    Locate files to parse and parse them to return PSSH
    """
    options = []
    if isinstance(periods, list):
        periods = periods[-1]
    for ad_set in periods['AdaptationSet']:
        if validate_set(ad_set, mediatype):
            rep_set = str()
            if isinstance(ad_set['Representation'], list):
                rep_set = next(t for t in ad_set['Representation'])
            else:
                rep_set = ad_set['Representation']
            # logger.debug(f"Representation: {rep_set}")

            items_params = list(
                ad_set['SegmentTemplate']['SegmentTimeline'].items())[0][1]

            rep_set["init"] = urljoin(
                base_uri,
                ad_set['SegmentTemplate']['@initialization'].replace(
                    "$RepresentationID$",
                    rep_set['@id']))

            _adset_media = ad_set['SegmentTemplate']['@media'].replace(
                "$RepresentationID$",
                rep_set['@id'])

            if psshtype == PsshType.FIRSTSEGMENT:
                if isinstance(items_params, dict):
                    item_ = items_params
                else:
                    item_ = items_params[0]

                rep_set["segments"] = [
                    urljoin(
                        base_uri,
                        _adset_media.replace(
                            "$Time$",
                            item_['@t']))
                ]

            if psshtype == PsshType.SEGMENTS:
                if isinstance(items_params, dict):
                    rep_set["segments"] = [
                        urljoin(
                            base_uri,
                            _adset_media.replace("$Time$", items_params['@t']))
                    ]
                else:
                    rep_set["segments"] = [
                        urljoin(
                            base_uri,
                            _adset_media.replace("$Time$", i['@t']))
                        for i in items_params
                    ]

            options.append(rep_set)

    pssh = set()

    if psshtype == PsshType.FIRSTSEGMENT:
        urls = [options[-1]['segments'][0]]
    elif psshtype == PsshType.SEGMENTS:
        urls = options[-1]['segments']
    else:
        urls = [options[-1]['init']]

    for i in urls:
        data = load_content(i, http_client)
        pos = 0
        init_data = None
        init_segment = b''
        while data[pos:]:
            if init_data is None:
                try:
                    box = Box.parse(data[pos:])
                except Exception:
                    break
                else:
                    if box.type in [b'moov', b'moof']:
                        for pssh_box, _ in BoxUtil.find(box, b'pssh'):
                            if pssh_box.box_body.system_ID == UUID(WV_UUID):
                                pssh.add(
                                    b64encode(
                                        Box.build(pssh_box)
                                    ).decode("utf-8"))
                    else:
                        init_segment += data[pos:pos + box.length]
                    pos += box.length
            else:
                init_segment += data[pos:]
                break
        time.sleep(0.5)
    return pssh


def validate_set(set_, mediatype_):
    """
    Check if set is from right mime type
    """
    if '@mimeType' in set_ and set_['@mimeType'] == mediatype_.value:
        return True
    elif mediatype_.value.startswith("video") and "@maxWidth" in set_:
        return True
    else:
        return False


def parse(
        content,
        base_uri=None,
        psshtype=False,
        http_client=False,
        mediatype=MimeType.VIDEO) -> str:
    """
    Parse manifest MPD and return PSSH
    """
    pssh = set()
    try:
        xml = xmltodict.parse(content)
        mpd = json.loads(json.dumps(xml))
        periods = mpd['MPD']['Period']
    except Exception as e:
        logger.error(e.with_traceback)
    try:
        if isinstance(periods, list):
            for _, period in enumerate(periods):
                if isinstance(period['AdaptationSet'], list):
                    for ad_set in period['AdaptationSet']:
                        if validate_set(ad_set, mediatype):
                            try:
                                find_wv_pssh(ad_set, pssh)
                            except KeyError as e:
                                logger.debug(f"Mising key {e} in adaptation set. Looking for representations next.")
                                try:
                                    for rep_set in ad_set['Representation']:
                                        find_wv_pssh(rep_set, pssh)
                                except KeyError as e:
                                    logger.debug(f"Mising key {e} in representations sets. Looking for media segments next.")
                else:
                    if period['AdaptationSet']['@mimeType'] == mediatype.value:
                        try:
                            find_wv_pssh(period['AdaptationSet'], pssh)
                        except KeyError as e:
                            logger.debug(f"Mising key {e} in representations sets. Looking for media segments next.")
        else:
            for ad_set in periods['AdaptationSet']:
                if validate_set(ad_set, mediatype):
                    try:
                        find_wv_pssh(ad_set, pssh)
                    except KeyError as e:
                        logger.debug(f"Mising key {e} in adaptation set. Looking for representations next.")
                        try:
                            for rep_set in ad_set['Representation']:
                                find_wv_pssh(rep_set, pssh)
                        except KeyError as e:
                            logger.debug(f"Mising key {e} in representations sets. Looking for media segments next.")

    except KeyError as e:
        logger.error(e.with_traceback)
    if not pssh:
        pssh = from_files(
            periods,
            http_client,
            mediatype,
            base_uri,
            psshtype)
    return pssh
