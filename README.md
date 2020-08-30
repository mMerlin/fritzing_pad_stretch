<!-- cSpell:enable -->
# Stretched PCB pads for Fritzing parts

<link href="css/markdown.css" rel="stylesheet"/>

This is «started as» a small script to generate Fritzing pcb view svg graphics for elongated through-hole pcb pads, based on a few numeric parameter constraints. These pads are generated in 2 parts. A circle, and a path. The circle element defines the hole size and postition to be drilled, and the path is the copper pad around the hole.

This was (is being) developed using python 3.7.8 with the Jinja2 v2.11.2 templating engine package. Pylint v2.5.3 is used to keep the python code up to standards and conventions. Earlier versions (especially python) may or may not work. I have no interest in that sort of regression testing for this application. It has no reason to stay backward compatible at that level.

* [The Math](#link_math)
* [Ideas](#link_ideas)
* [Planning](#link_planning)
* [References](#link_references)

<!--
* [Link](#link_link)
## <a name="link_link">⚓</a> Link
-->

## <a name="link_planning">⚓</a> Planning

* command line parameters
  * validation ¦ the numeric value limits of most parameters are interdependent
    * argparse can not (seem to) do the interdependent checks, but the class that builds the parser can
* simple code currently turns float to integer value when possible
  * extend to add rounding, whether (smart) cast to integer or not. Do not want decimal fraction values that end with …999 or …0000n
* the (drilled) hole center is the origin (0,0) point for the pad. That is the reference point for offset distances to the pad graphics, the next pad, the next row, and the edge of the image
  * with the pad offset from the hole, the gap between rows can vary independent of row spacing and pad maximum. The pads could be 'pointing out', or centered, for the same dimensions.
* for pad dimensions, avoid using terms (and variables) like width and height. Those would overlap with the width and height attributes of svg elements, and the context reverses depending on whether working with a horizontal or vertical pin row.

## <a name="link_math">⚓</a> Math

Notes on formulas and relationships between parameters and numbers in the svg file.

For convenience, pads can be described as having short and long cross section dimensions. These will be referenced as pad minimum and pad maximum to differentiate from width, height, and length, that could be confussed with svg element attributes, or trace widths for a pcb. For the same reason, the calculated coordinate delta values are not x and y offsets, which transpose depending on the direction. They are u, v, where (u, v) maps to (x, y) for a horizontal pin row, and (y, x) for a vertical pin row.

* the stroke width for the circle is the (pad minimum minus the hole diameter) / 2
* the radius of the circle is either (equivalent)
  * the pad minimum minus the (stroke width / 2)
  * the hole diameter plus the (stroke width / 2)
  * (pad minimum + hole diameter) / 4
* each end of a pad is a circular arc with a diameter of pad minimum
* starting from the center of the hole (circle), the offset to the start of the outer arc (semi-circle) of the pad, is:
  * u = ± (pad minimum / 2)
  * for a pad centered around the circle
    * v = ± (pad maximum - pad minimum) / 2
  * with the pad offset so that one end just wraps the circle (constant trace thickness around that side of the hole)
    * v = 0 (the centre of the pad ending arc is the same as the center of the hole), or
    * v = pad maximum - pad minimum
* the offset from there to the other end of the circular arc is:
  * u = ± pad minimum
  * v = 0

Note: The resulting circle and pad will be technically correct as long as the inner cutout (double half circles) do not get outside the extents of the (inner or outer edge of the) stroke for the circle that defines the hole to be drilled. However, the current version of the Fritzing code checks the percentage overlap between the circle and other (non connector) copper graphics to determine when to include that graphics as part of the connector pad. If that overlap gets too small, the pad gets treated as a separate, disconnected net, causing problems with (at least) the design rules checking. The implementation used here sets maximal overlap, completely covering the stroke for the hole, by exactly following the inner boundary with the pad cutout. Similarly, the graphics pair is technically correct as long as the outer edge of the hole stroke is completely within the non-cutout portion of the pad graphic. Again, to maximize overlap, the circle radius and stroke width are manipulated to be as large as possible within those constraints, so that the outer edge of the circle stroke exactly reaches to, but does not cross, the outside boundary of the pad graphics.

## <a name="link_ideas">⚓</a> Ideas

* create as html, css, javascript, such that it can be hosted on github.io, and images easily «displayed and» downloaded
* «future» functions
  * number or rows
  * row spacing
  * merged or separate (groups) for circles and paths
  * multiple row vertical numbering sequence will have first pin at the top left, going down, then up the second side. Keeps the first pin at the origin, whereas with the horizontal layout, the second row `pushes` the first row down.
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
* options for preformatted help text: longer (clean line breaks and indenting) descriptions for pad positions and debug flags
  * argparse.ArgumentParser(…, formatter_class)
    * try making the debug entry into a sub-parser, and set
      * `formatter_class=argparse.RawTextHelpFormater` in call that creates instance
    * or put everything else into a sub-parser
      * [Multiple lines in python argparse help display](https://stackoverflow.com/questions/29613487/multiple-lines-in-python-argparse-help-display)
    * alternate implementation subclassing HelpFormatter, then use inline tag so only affects the specific help string
      * [How to insert newline in the help text](https://exceptionshub.com/python-argparse-how-to-insert-newline-in-the-help-text.html)
      * a markdown formatter would be `nice`, but well beyond the scope here. Maybe import a markdown view processing library? «not one that generates html»
      * use parent class method(s) to wrap lines after initial processing?
* allow abbreviation of pad position to (minimum of) first letter
  * needs a custom argparse action, and choices entry may not work
* add verbose reporting (option) for pins, connector ids, dimensions of created image
* input connector id prefix text
* input connector id suffix «pin¦pad»
* input complete first connector id "connector«n»«pin¦pad»"
  * connector id template regex: «prefix»«first_connector»«suffix»
* save as defaults (create file that can be used with `@` prefix)
* ignore min and max limits
* reverse hole position for 2nd row
* drawing margin (css style: top, right, bottom, left)
  * -- margin
* silkscreen: horizontal¦vertical brackets; "L" corners; Cut marks; end notched chip
* `man` «web» page with longer descriptions for the parameter usage

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

Minimal Unittest for parameter values

```sh
./_hpd_unittest 2> test.out
diff test.out _hpd_ut_exceptions.out
# «only» line numbers likely to change, barring intended implementation changes

./stretched_pads.py @sample
diff test.svg _hpd_h_c_40_60_90_0.svg
./stretched_pads.py @sample -P top
diff test.svg _hpd_h_t_40_60_90_0.svg
./stretched_pads.py @sample -P bottom
diff test.svg _hpd_h_b_40_60_90_0.svg
./stretched_pads.py @sample -P vertical
diff test.svg _hpd_v_c_40_60_90_0.svg
./stretched_pads.py @sample -P left
diff test.svg _hpd_v_l_40_60_90_0.svg
./stretched_pads.py @sample -P right
diff test.svg _hpd_v_r_40_60_90_0.svg
```

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
