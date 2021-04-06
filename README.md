# SCAD2BoundingObject

This is a script to convert SCAD models containing cylinders, spheres, and boxes into webots boundingObjects used in proto files.

A config file needs to be specified to specify the transformation between the origin of the solid in relation to the part origin.
For an examples of such configs see [here](test/config_shoulder.yaml), [here](test/config_foot.yaml), and [here](test/config_stollen.yaml).

For creating the scad file from an existing stl use:
```
python src/scad2boundingobject/edit_shape.py <path_to_your.stl>
```

For an example open the stl files in the test folder:
```
python src/scad2boundingobject/edit_shape.py test/foot_cover.stl>
```

Further documentation is located at https://onshape-to-robot.readthedocs.io/en/latest/pure-shapes.html.

For running the script to convert the scad file to a bounding object use:
```
python src/scad2boundingobject/scad2boundingobject.py [-o OUTPUT] -c CONFIG scad_file [scad_file ...]
```

For further info:
```
python src/scad2boundingobject/scad2boundingobject.py -h
```