# coding=utf-8
"""
Copyright 2019-2099 Rhoban Team <Grégoire Passault>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json
import re
import os
import numpy as np

"""
These functions are responsible for parsing CSG files (constructive solid geometry), which are files
produced by OpenSCAD, containing no loop, variables etc.
"""

def multmatrix_parse(parameters):
    matrix = np.matrix(json.loads(parameters), dtype=float)
    matrix[0, 3] /= 1000.0
    matrix[1, 3] /= 1000.0
    matrix[2, 3] /= 1000.0
    return matrix


def cube_parse(parameters):
    results = re.findall(r'^size = (.+), center = (.+)$', parameters)
    if len(results) != 1:
        print("! Can't parse CSG cube parameters: "+parameters)
        exit()
    return np.array(json.loads(results[0][0]), dtype=float)/1000.0, results[0][1] == 'true'


def cylinder_parse(parameters):
    results = re.findall(r'h = (.+), r1 = (.+), r2 = (.+), center = (.+)', parameters)
    if len(results) != 1:
        print("! Can't parse CSG cylinder parameters: "+parameters)
        exit()
    result = results[0]
    return np.array([result[0], result[1]], dtype=float)/1000.0, result[3] == 'true'


def sphere_parse(parameters):
    results = re.findall(r'r = (.+)$', parameters)
    if len(results) != 1:
        print("! Can't parse CSG sphere parameters: "+parameters)
        exit()
    return float(results[0])/1000.0


def extract_node_parameters(line):
    line = line.strip()
    parts = line.split('(', 1)
    node = parts[0]
    parameters = parts[1]
    if parameters[-1] == ';':
        parameters = parameters[:-2]
    if parameters[-1] == '{':
        parameters = parameters[:-3]
    return node, parameters


def parse_csg(data):
    shapes = []
    lines = data.split("\n")
    matrices = []
    for line in lines:
        line = line.strip()
        if line != '':
            if line[-1] == '{':
                node, parameters = extract_node_parameters(line)
                if node == 'multmatrix':
                    matrix = multmatrix_parse(parameters)
                else:
                    matrix = np.matrix(np.identity(4))
                matrices.append(matrix)
            elif line[-1] == '}':
                matrices.pop()
            else:
                node, parameters = extract_node_parameters(line)
                transform = np.matrix(np.identity(4))
                for entry in matrices:
                    transform = transform*entry
                if node == 'cube':
                    size, center = cube_parse(parameters)
                    if not center:
                        transform[0, 3] += size[0]/2.0
                        transform[1, 3] += size[1]/2.0
                        transform[2, 3] += size[2]/2.0
                    shapes.append({
                        'type': 'cube',
                        'parameters': size,
                        'transform': transform
                    })
                if node == 'cylinder':
                    size, center = cylinder_parse(parameters)
                    if not center:
                        transform[2, 3] += size[0]/2.0
                    shapes.append({
                        'type': 'cylinder',
                        'parameters': size,
                        'transform': transform
                    })
                if node == 'sphere':
                    shapes.append({
                        'type': 'sphere',
                        'parameters': sphere_parse(parameters),
                        'transform': transform
                    })
    return shapes


def process(filename):
    os.system('openscad '+filename+' -o /tmp/data.csg')
    f = open('/tmp/data.csg')
    data = f.read()
    f.close()

    return parse_csg(data)
