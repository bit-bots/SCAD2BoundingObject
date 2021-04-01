#!/usr/bin/env python
# coding=utf-8
"""
Copyright 2019-2099 Rhoban Team <Grégoire Passault>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys, os

if len(sys.argv) < 2:
    print('Usage: edit-shape.py [stl file]')
else:
    fileName = sys.argv[1]
    parts = fileName.split('.')
    parts[-1] = 'scad'
    fileName = '.'.join(parts)
    if not os.path.exists(fileName):
        scad = "% scale(1000) import(\""+os.path.basename(sys.argv[1])+"\");\n"
        scad += "\n"
        scad += "// Append pure shapes (cube, cylinder and sphere), e.g:\n"
        scad += "// cube([10, 10, 10], center=true);\n"
        scad += "// cylinder(r=10, h=10, center=true);\n"
        scad += "// sphere(10);\n"
        f = open(fileName, 'w')
        f.write(scad)
        f.close()
    directory = os.path.dirname(fileName)
    os.system('cd '+directory+'; openscad '+os.path.basename(fileName))
