#!/usr/bin/env python

import logging
import unittest

import dashpssh

log = logging.getLogger(__name__)

class PsshTests(unittest.TestCase):
  def test_fixed_on_manifest_1(self):
    self.assertEqual(
      dashpssh.load("tests/manifests/on_manifest/adaptationset.mpd"),
         {'AAAAZnBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAEYIARIQo2hWCauiSGufnJRmvwtINxoKdGVsZWZvbmljYSIkYTM2ODU2MDktYWJhMi00ODZiLTlmOWMtOTQ2NmJmMGI0ODM3'},
      )
  def test_fixed_on_manifest_2(self):
    self.assertEqual(
      dashpssh.load("https://cdn.bitmovin.com/content/assets/art-of-motion_drm/mpds/11331.mpd"),
         {'AAAAW3Bzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAADsIARIQ62dqu8s0Xpa7z2FmMPGj2hoNd2lkZXZpbmVfdGVzdCIQZmtqM2xqYVNkZmFsa3IzaioCSEQyAA=='},
      )
  def test_init(self):
    self.assertEqual(
      dashpssh.load("tests/manifests/fixed/manifest.mpd"),
         {'AAAAcXBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAFEIARIQPOwbHql5ndpVluZPN+XtIBoVdmVyaW1hdHJpeGNhYmxldmlzaW9uIh5yPXZteF93aWRld2luZV9UZWxlZmVIRFImcz05NTAqAlNEOAA='},
      )
  def test_rotation_init(self):
    self.assertEqual(
      dashpssh.load("tests/manifests/rotation/manifest.mpd", psshtype="init"),
         {'AAAAaHBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAEgIARIQU1yLEzKhgN5s2uOQeT3X+hoPdmVyaW1hdHJpeGNsYXJvIhpyPVNQT0hCU0hEX2Rhc2hfY2Umcz0yMzIwNioFU0RfSEQ='},
      )
  def test_rotation_segment(self):
    self.assertEqual(
      dashpssh.load("tests/manifests/rotation/manifest.mpd", psshtype="firstsegment"),
         {'AAAAaHBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAAEgIARIQBoqmCirRBx8WmAxl+p9SqxoPdmVyaW1hdHJpeGNsYXJvIhpyPVNQT0hCU0hEX2Rhc2hfY2Umcz0yMzIwNioFU0RfSEQ='},
      )

if __name__ == '__main__':
  unittest.main()