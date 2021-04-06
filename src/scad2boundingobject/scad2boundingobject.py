#!/usr/bin/env python3

import argparse
import csg
import transforms3d
import numpy as np
import yaml
import os

parser = argparse.ArgumentParser("Generate proto syntax from scad models. Default output is bounding_object.proto")
parser.add_argument("scad_file", nargs="+")
parser.add_argument("-o", "--output", help="output file in which the generated proto is saved, defaults to 'bounding_object.proto'", default="bounding_object.proto")
parser.add_argument("-c", "--config", help="config file to specify transform between link origin and scad origin", required=True)
args = parser.parse_args()

outfile = open(args.output, "w")

indent = 0
outfile.write("boundingObject ")

shapes = []
for scad_file in args.scad_file:
    shapes.append(csg.process(scad_file))

if args.config:
    with open(args.config) as f:
        conf = yaml.load(f, Loader=yaml.Loader)

if len(shapes) > 1 or len(shapes[0]) > 1:
    indent += 1
    outfile.write("Group {\n")
    outfile.write(indent * "  " + "children [\n")
    indent += 1

for i,shapes_single_file in enumerate(shapes):
    for shape in shapes_single_file:
        if args.config:
            try:
                # base name without file extension
                base_filename = os.path.basename(args.scad_file[i])
                without_extension = os.path.splitext(base_filename)[0]
                transform_raw = conf[without_extension]
                translation = transform_raw['translation']
                rotation = transform_raw['rotation']
                rot_mat = transforms3d.euler.euler2mat(*rotation)
                transformation = transforms3d.affines.compose(translation, rot_mat, [1, 1, 1])
            except KeyError as ex:
                transformation = np.identity(4)
        else:
            transformation = np.identity(4)
        outfile.write(indent * "  " + "Transform {\n")
        indent += 1
        outfile.write(indent * "  " + "translation ")
        internal_transform = shape["transform"]
        cylinder_offset = np.identity(4)
        if shape["type"] is "cylinder":
            cylinder_offset[:3, :3] = transforms3d.euler.euler2mat(0.5*np.pi, 0, 0)

        transformation = np.matmul(np.matmul(transformation, internal_transform), cylinder_offset)
        T, R, _, _ = transforms3d.affines.decompose44(transformation)
        outfile.write(f"{T[0]} {T[1]} {T[2]}\n")
        outfile.write(indent * "  " + "rotation ")
        axis, angle = transforms3d.axangles.mat2axangle(R)
        outfile.write(f"{axis[0]} {axis[1]} {axis[2]} {angle}\n")
        outfile.write(indent * "  " + "children [\n")
        indent += 1
        if shape["type"] is "cube":
            outfile.write(indent * "  " + "Box {\n")
            indent += 1
            size = shape["parameters"]
            outfile.write(indent * "  " + f"size {size[0]} {size[1]} {size[2]}\n")
            indent -= 1
            outfile.write(indent * "  " + "}\n")
        elif shape["type"] is "cylinder":
            outfile.write(indent * "  " + "Cylinder {\n")
            indent += 1
            size = shape["parameters"]
            outfile.write(indent * "  " + f"height {size[0]}\n")
            outfile.write(indent * "  " + f"radius {size[1]}\n")
            indent -= 1
            outfile.write(indent * "  " + "}\n")
        elif shape["type"] is "sphere":
            outfile.write(indent * "  " + "Sphere {\n")
            indent += 1
            size = shape["parameters"]
            outfile.write(indent * "  " + f"radius {size}\n")
            indent -= 1
            outfile.write(indent * "  " + "}\n")


        # children
        indent -= 1
        outfile.write(indent * "  " + "]\n")
        # transform
        indent -= 1
        outfile.write(indent * "  " + "}\n")


if len(shapes) > 1 or len(shapes[0]) > 1:
    indent -= 1
    outfile.write(indent * "  " + "]\n")
outfile.write("}")
outfile.close()