#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .AxiElement import AxiElement
from .Polyline import Polyline
from .Bbox import Bbox
from .hershey_fonts import *
from .tools import transform

class Text(AxiElement):
    def __init__( self, text, center, **kwargs ):
        AxiElement.__init__(self, **kwargs);
        self.text = str(text)
        self.center = center

        self.font =  kwargs.pop('font', FUTURAL)
        self.spacing =  kwargs.pop('spacing', 0)
        self.extra =  kwargs.pop('extra', 0)


    def getWidth(self):
        x = 0
        for ch in self.text:
            index = ord(ch) - 32
            if index < 0 or index >= 96:
                x += self.spacing
                continue

            lt, rt, coords = self.font[index]
            x += rt - lt + self.spacing

        if isinstance(self.scale, tuple) or isinstance(self.scale, list):
            x *= self.scale[0]
        else:
            x *= self.scale

        return x


    def getPolylines(self, **kwargs ):
        # Based on hershey implementation by Michael Fogleman https://github.com/fogleman/axi/blob/master/axi/hershey.py
        result = []

        bbox = Bbox()

        x = 0
        for ch in self.text:
            index = ord(ch) - 32
            if index < 0 or index >= 96:
                x += self.spacing
                continue

            lt, rt, coords = self.font[index]
            for path in coords:
                path = [ (x + i - lt, j) for i, j in path]
                if path:
                    pol = Polyline(path)
                    bbox.join( pol.getBbox() )
                    result.append( pol )
            x += rt - lt + self.spacing
            if index == 0:
                x += self.extra

        toCenter = transform(bbox.center, rotate=self.rotate, scale=self.scale)

        for i in range(len(result)):  
            result[i].translate = [ self.translate[0] + self.center[0] - toCenter[0],
                                    self.translate[1] + self.center[1] - toCenter[1]]
            result[i].scale = self.scale
            result[i].rotate = self.rotate
            result[i].origin = bbox.center
            result[i].stroke_width = self.stroke_width / self.scale
       
        return result


    def getPoints(self, **kwargs ):
        points = []
        polys = self.getPolylines()

        for poly in polys:
            pts = poly.getPoints()
            for p in pts:
                points.append(p)
        return points


    def getBbox(self):
        return Bbox(points=self.getPoints())


    def getPathString(self):
        lines = self.getPolylines()

        path_str = ''
        for line in lines:
            path_str += line.getPathString()

        return path_str

    