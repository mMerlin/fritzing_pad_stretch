<!-- cSpell:enable -->
# stretched-pads.py man page

<link href="css/github_override.css" rel="stylesheet"/>

By default (and currently only) this creates oblong connector pads. These are a straight segment with semi-circular ends, with an interior section cutout where the plated through hole will be.

```txt
./stretched_pads.py -h
usage: stretched_pads.py [options] [@parameter_file] output_file

Fritzing SVG Stretched PCB pad builder

positional arguments:
  output-svg-file       SVG file to create

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -d d, --diameter d    connector hole diameter. Default: 38
  -w w, --minimum w     narrowest dimension of a pad (must be > diameter).
                        Default: 45
  -l l, --maximum l     longest dimension of a pad (must be > width). Default:
                        90
  -P pos, --position pos
                        position of the pad relative to the hole: top, bottom,
                        left, right, horizontal, vertical. Default: horizontal
  -p p, --padding p     for positions other than `horizontal` or `vertical`
                        (centred), extra room to leave beyond that provided by
                        the difference between diameter and width. Default: 0
  -f n, --first-connector n
                        The number (id) of the first (lowest) connector pad to
                        generate. Default: 0
  -r n, --row-pins n    The number of pins to included in a single row.
                        Default: 1
  -s d, --pad-spacing d
                        The centre to centre distance between adjacent
                        connector pads in a row. Default: 100
  -k d, --keepout d     The minimum separation distance between traces to
                        satisfy design rules. Default: 10
  -D bits, --debug bits
                        debug flags A single integer value that represents the
                        binary `or` of the desired debug control flags bit 0
                        100 times scaling

All size values are in mils (1/1000th inch)
```

```txt
@parameter_file
```

This application uses a lot of parameters to configure the generated connectors. An later versions are likely to have a few more. It is easy to miss one, or get something wrong. To help with that, the parameters can be put in a text file, and passed directly to the program. Since command line parameters are processed in the order seen, and later parameters override earlier, this can be used to set up personal default value or profiles. Individual values can then be changed, by specifying a new value later in the command line (after the parameter file reference).

For example, to create connectors sized to allow 2 10 mil traces between 100 mil spaced connectors, with 8 mil keepout and 40 mil holes (28 + 8 + 10 + 8 + 10 + 8 + 28), create a file named `double_thin` containing

```txt
--keepout
8
--diameter
40
--pad-spacing
100
--width
56
```

then invoke stretched_pad.py as

`./stretched_pad.py @double_thin`

adding any extra, or alternate, parameters and output svg file name at the end. My example uses long parameters names, but short work as well. Other than the keepout distance, those are the same parmeters needed to allow a single 24 mil trace with 10 mil keep to fit between the connector pads.

```txt
-d diameter
--diameter diameter
```

The diameter of the hole to be drilled for the connectors. The value is in mils.

```txt
-w width
--minimum width
```

The shortest cross-sectional dimension of the pad. This is the distance across the straight segment. The value is in mils.

```txt
-l length
--maximum length
```txt

The longest cross-sectional dimension of the pad. This is the distance along the straight segment, plus the semi-circular end caps. So this is the length of the straight segment plus the width of the straight segment. The width is the diameter of the end cap semi-circles, with a half circle at each end. The value is in mils.

```txt
-P position
--position position
```txt

Position is one of: horizontal, top, bottom, vertical, left, right.

The position specifies the location of the pad relative to the hole, as well as the adjacent connector orientation. horizontal, top and bottom positions will locate the connectors (on the first row) to the right of the previous connector, with the end caps above and below the circle. vertical, left and right positions will locate the connectors (on the first row) below (down from) the previous connector, with the end caps to the left and right of the circle. vertical and horizontal positions centre the end caps around the circle. The top, bottom, left, and right positions move the end cap on the specified side as far from the circle as possible, positioning the opposite end cap so that it's centre point is the same as the centre of the hole

That (non-centred) position can be modified using the padding parameter

```txt
-p padding
--padding padding
```

For position locations other than `horizontal` or `vertical` (the centred positions), additional room to insert between the hole and the nearest end cap. This becomes the distance between the centre point of the hole and the centre point of the end cap semi-circle. Can not be used to move the location back to or past the centred position.
The default value is 0, the value is in mils.

```txt
-f number
--first-connector number
```

The number of the first (lowest) connector pad to generate. This is the numeric (integer) value to insert into the id (svgId in the fzp file) for the circle element used to specify the hole. The default value is 0 «connector0pad»

```txt
-r number
--row-pins number
```

The (integer) number of connectors to included in a single row. For the current implementation, there is always only 1 row, so this is also the total number of connectors to insert into the svg file. The default value is 1.

```txt
-s distance
--pad-spacing distance
```

The centre to centre distance between adjacent connector pads in a row. The distance between hole centres. The default is 100, the value is in mils.

```txt
-k distance
--keepout distance
```

The minimum separation distance between separate copper areas needed to satisfy the design rule constraints. This is currently only used to make sure that adjacent pads do not interfere with each other (based on size and spacing), but is planned to be used to report what size of traces will safely fit between the connectors. The default (here and in Fritzting Design Rules Check) is 10, with the value in mils.

---txt
-D bits
--debug bits
'''

A single integer number, which is the binary OR (sum) of a series of flags used to pass some debug settings into the program. So far there is no logic to the values needed. The meaning could change with every version of the program, as the development needs change. The only think likely to stay consistent, is all flags can be turned on with a value of -1.

To determine the currently understood flag values, look at the source code. There is a block of constant definitions with names starting with "DBG_". Those values are the masks that different pieces of the code use to control operations. Currently all but one related to the amount of terminal output shown. The default value is 0.

* Show Params : Report the parsed run time parameters
* Show Pad : Report the template substitution values calculated for connector pads
* Show Drawing : Report the template substitution values calculated for the drawing file
* Scale 100 times : Multiple the height and width of the drawing by 100, without changing any coordinates. Makes the generated svg much easier to look at with a viewer program that defaults to using the real world units (Used with EOG (Eye-Of-Gnome))
* Show Multiple Exceptions : By default, the application exits on the first error during argument parsing. Anything handled directly by argparse will continue to work that way, but with this flag enabled, the constraint checking between parameters will report all of the exceptions before exiting.

<!--
* [Link](#link_link)
## <a name="link_link">⚓</a> Link
-->

## functional comment block

Header prevents the comments here from being hidden if the previous block is folded in the editor

<!-- cSpell:disable -->
<!-- cSpell:enable -->
<!--
# cSpell:disable
# cSpell:enable
cSpell:words
cSpell:ignore
cSpell:enableCompoundWords
-->
