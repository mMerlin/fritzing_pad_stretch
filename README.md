<!-- cSpell:enable -->
# Stretched PCB pads for Fritzing parts

<link href="css/markdown.css" rel="stylesheet"/>

This is «starting as» a small script to generate Friting pcb view svg graphics for elongated through-hole pads, based on a few numeric parameter constraints. These pads are generated in 2 parts. A circle, and a path. The circle defines the hole size and postition to be drilled, and the path is the copper pad around the circle.

This was (is being) developed using python 3.7.8 with the Jinja2 v2.11.2 templating engine package. Pylint v2.5.3 is used to keep the python code up to standards and conventions.

* [The Math](#link_math)
* [Ideas](#link_ideas)
* [Planning](#link_planning)
* [References](#link_references)

<!--
* [Link](#link_link)
## <a name="link_link">⚓</a> Link
-->

## <a name="link_planning">⚓</a> Planning

* python3
* command line parameters
  * validation ¦ the numeric values of most parameters are interdependent
    * order of entry on the command line is not fixed
    * order of processing is not known (_probably_ left to right)
    * need to do base sanity check (is numeric, min/max), then set (global) flag to show avaliable
    * later validation can then pick up earlier values for cross-check
    * is there a way to know when the _last_ parameter is being processed?
    * post parameter validation processing, in a context that can still throw the appropriate exceptions?
  * easier (and possible) to do the bare initial type checks, then check constraints after argparse has accepted the parameters
* simple code currently turns float to integer value when possible
  * extend to add rounding, whether (smart) cast to integer or not
* Hole center is the origin (0,0) point for the pad. That is the reference point for offset distances to the next pad, or the next row
  * with pad offset from hole, the gap between rows can vary independent of row spacing. The pads could be 'pointing out', or centered, for the same dimensions

## <a name="link_math">⚓</a> Math

Notes on formulas and relationships between parameters and numbers in the svg file.

* The stroke width for the circle is the (pad width minus the hole diameter) / 2
* The radius of the circle is either (equivalent)
  * The pad width minus the (stroke width / 2)
  * The hole diameter plus the (stroke width / 2)
* the radius of the outer arc of the pad is (pad width / 2)
* assuming pads sequencing from left to right
  * starting from the center of the circle, the offset to the start of the outer arc (semi-circle) of the pad, is:
    * x = ± (pad width / 2)
    * for a pad centered around the circle
      * y = ± (pad length - pad width) / 2
  * the offset to the end point of the other end of the outer circular are is:
    * x = ± pad width
    * y = 0

## <a name="link_ideas">⚓</a> Ideas

* create as html, css, javascript, such that it can be hosted on github.io
* «future» functions
  * number of pins (in a single row)
  * pin spacing (in a single row)
  * number or rows
  * row spacing
  * merged or separate (groups) for circles and paths
  * starting pin number
  * generate vertically instead of horizontally
    * numbering sequence will have first pin will be top left, going down, then up the second side. Keeps the first pin at the origin, where as with the horizontal layout, the second row `pushes` to first row down.
  * generated silkscreen border
    * rectangle
    * brackets
      * horizontal
      * vertical
    * cut mark
    * corners only
* rules, limits, warnings
* multiple templates (files? embedded string?) for different scenarios
* report statistics about the generated hole set:
  * trace width that will fit between pads at specified keepout
    * assuming more than one pin
  * trace width that will fit 2 traces between pads at specified keepout
  * number of `zero` width «keepout width» traces that will fit between pads
    * int(separation / keepout) - 1
    * (int(separation / keepout) - 1) % 2 - 1 ??
  * as above to fit between rows of pins
    * account for any pad (to hole) offsets, and padding

## <a name="link_references">⚓</a> References

* [jinja tutorial](http://zetcode.com/python/jinja/) ¦ see 'import Environment'
* [control whitespace summary](https://stackoverflow.com/a/35777386)
* [control whitespace docs](https://jinja.palletsprojects.com/en/master/templates/#whitespace-control)
* [create macro](https://stackoverflow.com/a/10997352), use indent «filter»
  * can choose to «not» indent [first line](https://stackoverflow.com/a/31856334)
  * use `set` (and namespace) to carry indent increments through nesting
    * not needed: as long as each `extends` uses indent filter for next level, the indent accumulates. Each instance just needs to indent «hard-coded» 2.
* [variables and scoping](https://jinja.palletsprojects.com/en/2.11.x/templates/#assignments)
  * from above, maybe block assignment instead of macro

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
