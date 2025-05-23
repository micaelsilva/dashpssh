#!/usr/bin/env python

import os
import logging
import unittest

import dashpssh

log = logging.getLogger(__name__)
root = os.path.dirname(os.path.realpath(__file__))


class PsshTests(unittest.TestCase):
    def test_fixed_on_manifest(self):
        self.assertEqual(
            dashpssh.load(
                root + "/manifests/on_manifest/adaptationset.mpd"),
                {'AAAAZnBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAEYIARIQo2hWCauiSGufnJRmvwtINxoKdGVsZWZvbmljYSIkYTM2ODU2MDktYWJhMi00ODZiLTlmOWMtOTQ2NmJmMGI0ODM3'})

    def test_timeline_in_rep(self):
        self.assertEqual(
            dashpssh.load(
                root + "/manifests/timeline_in_rep/manifest.mpd"),
                {'AAAAP3Bzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAB8IARIQgpmI8tbtQ0uk2VRj1CbnnSIJTGl2ZV8wMTY0'})

    def test_fixed_manifest_no_mimetype(self):
        self.assertEqual(
            dashpssh.load(
                root + "/manifests/on_manifest/no_mimetype.mpd"),
                {'AAAAbHBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAEwSEKmx1TapT04wqABVkSnN4iAaDE1lZGlhc3RyZWFtMiIkYTliMWQ1MzYtYTk0Zi00ZTMwLWE4MDAtNTU5MTI5Y2RlMjIwSOPclZsG'})

    def test_fixed_on_manifest_remote(self):
        self.assertEqual(
            dashpssh.load(
                "https://cdn.bitmovin.com/content/assets/art-of-motion_drm/mpds/11331.mpd"),
                {'AAAAW3Bzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAADsIARIQ62dqu8s0Xpa7z2FmMPGj2hoNd2lkZXZpbmVfdGVzdCIQZmtqM2xqYVNkZmFsa3IzaioCSEQyAA=='})

    def test_init(self):
        self.assertEqual(
            dashpssh.load(
                root + "/manifests/fixed/manifest.mpd"),
                {'AAAAcXBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAFEIARIQPOwbHql5ndpVluZPN+XtIBoVdmVyaW1hdHJpeGNhYmxldmlzaW9uIh5yPXZteF93aWRld2luZV9UZWxlZmVIRFImcz05NTAqAlNEOAA='})

    @unittest.skip("temporarily without pssh")
    def test_rotation_init_remote(self):
        self.assertEqual(
            dashpssh.load(
                'https://fq5r6s7t8u9v0wl.clarocdn.com.br/Content/Channel/SPOSPTHD/dsc2/manifest.mpd',
                headers={"Referer": "https://www.clarotvmais.com.br/"},
                psshtype=dashpssh.PsshType.INIT),
                {'AAAAaHBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAEgIARIQogGPIlZC80+D2y7Dil5B1BoPdmVyaW1hdHJpeGNsYXJvIhpyPVNQT1NQVEhEX2Rhc2hfY2Umcz0yMzIwNioFU0RfSEQ='})

    def test_rotation_init_local(self):
        self.assertEqual(
            dashpssh.load(
                root + "/manifests/rotation/manifest.mpd",
                psshtype=dashpssh.PsshType.INIT),
                {'AAAAaHBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAEgIARIQU1yLEzKhgN5s2uOQeT3X+hoPdmVyaW1hdHJpeGNsYXJvIhpyPVNQT0hCU0hEX2Rhc2hfY2Umcz0yMzIwNioFU0RfSEQ='})

    def test_rotation_segment(self):
        self.assertEqual(
            dashpssh.load(
                root + "/manifests/rotation/manifest.mpd",
                psshtype=dashpssh.PsshType.FIRSTSEGMENT),
                {'AAAAaHBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAEgIARIQBoqmCirRBx8WmAxl+p9SqxoPdmVyaW1hdHJpeGNsYXJvIhpyPVNQT0hCU0hEX2Rhc2hfY2Umcz0yMzIwNioFU0RfSEQ='})

    def test_pr_fixed_on_manifest(self):
        self.assertEqual(
            dashpssh.load(
                'https://a121aivottepl-a.akamaihd.net/gru-nitro/live/clients'
                + '/dash/enc/jo3rmhhp2r/out/v1'
                + '/50656942ce4e40a1be824c9d83578fe9/cenc.mpd',
                drm=dashpssh.DrmUuid.PR),
                {('AAADMHBzc2gAAAAAmgTweZhAQoarkuZb4IhflQAAAxAQAwAAAQABAAYDPA'
                  'BXAFIATQBIAEUAQQBEAEUAUgAgAHgAbQBsAG4AcwA9ACIAaAB0AHQAcAA6'
                  'AC8ALwBzAGMAaABlAG0AYQBzAC4AbQBpAGMAcgBvAHMAbwBmAHQALgBjAG'
                  '8AbQAvAEQAUgBNAC8AMgAwADAANwAvADAAMwAvAFAAbABhAHkAUgBlAGEA'
                  'ZAB5AEgAZQBhAGQAZQByACIAIAB2AGUAcgBzAGkAbwBuAD0AIgA0AC4AMA'
                  'AuADAALgAwACIAPgA8AEQAQQBUAEEAPgA8AFAAUgBPAFQARQBDAFQASQBO'
                  'AEYATwA+ADwASwBFAFkATABFAE4APgAxADYAPAAvAEsARQBZAEwARQBOAD'
                  '4APABBAEwARwBJAEQAPgBBAEUAUwBDAFQAUgA8AC8AQQBMAEcASQBEAD4A'
                  'PAAvAFAAUgBPAFQARQBDAFQASQBOAEYATwA+ADwASwBJAEQAPgAyAGwANQ'
                  'BIAE4ASgBHADUAWABxADIAUwBWAEkAcgByADEAeABCAEIAQwBnAD0APQA8'
                  'AC8ASwBJAEQAPgA8AEMASABFAEMASwBTAFUATQA+AFkAYgA1AHYAMQBjAH'
                  'YAeQBGAG4AZwA9ADwALwBDAEgARQBDAEsAUwBVAE0APgA8AEwAQQBfAFUA'
                  'UgBMAD4AaAB0AHQAcABzADoALwAvAHAAcgBsAHMALgBhAHQAdgAtAHAAcw'
                  'AuAGEAbQBhAHoAbwBuAC4AYwBvAG0ALwBjAGQAcAA8AC8ATABBAF8AVQBS'
                  'AEwAPgA8AEMAVQBTAFQATwBNAEEAVABUAFIASQBCAFUAVABFAFMAPgA8AE'
                  'kASQBTAF8ARABSAE0AXwBWAEUAUgBTAEkATwBOAD4ANwAuADEALgAxADQA'
                  'MwA5AC4AMAA8AC8ASQBJAFMAXwBEAFIATQBfAFYARQBSAFMASQBPAE4APg'
                  'A8AC8AQwBVAFMAVABPAE0AQQBUAFQAUgBJAEIAVQBUAEUAUwA+ADwALwBE'
                  'AEEAVABBAD4APAAvAFcAUgBNAEgARQBBAEQARQBSAD4A')})


if __name__ == '__main__':
    unittest.main()
