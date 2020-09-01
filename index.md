<!-- cSpell:enable -->
# Fritzing Stretched PCB THT pads

<link href="css/github_override.css" rel="stylesheet"/>

This project is a tool to generate svg images to use as the base for the PCB view of Fritzing parts. The focus is on through-hole connectors with non-circular pads.

Runtime parameters can be used to control many things about the generated connectors and pads.

* [man page](man.md)
* [github repository](https://github.com/mMerlin/fritzing_pad_stretch)
* [installation](#link_installation)
* [examples](#link_examples)

<!--
* [Link](#link_link)
## <a name="link_link">⚓</a> Link
-->

## <a name="link_installation">⚓</a> Installation

This has been created using python 3.7.8 with the Jinja2 v2.11.2 templating engine package. Pylint v2.5.3 is used to keep the python code up to standards and conventions. Earlier versions (especially python) may or may not work. I have no interest in that sort of regression testing for this application. It has no reason to stay backward compatible at that level.

The application can be downloaded as a zip file from the github repository page, or created from a terminal window with

```sh
git clone https://github.com/mMerlin/fritzing_pad_stretch.git
```

To directly run the program a recent version of python is needed, and the jinja2 library. If you are setup to use pipenv, a virtual environment can be setup by changing to the downloaded folder, and running `pipenv install`.

From there `./stretched_pads.py -h` (on linux) will get the basic help information. If your environment does not support the "shebang" header (or the executable tag was lost during installation) to inform the operating system that the file is to be run using python, `python stretched_pads.py -h` or `python3 stretched_pads.py -h` should work.

## <a name="link_examples">⚓</a> Examples

Starting from [this parameter file](examples/base_parameters.txt), the following 6 svg files were generated, using only overrides to the position and padding. Because of the debug option used, these are scaled to 100 times the size they would need to be for use as a PCB view of a fritzing part, then scaled back down to about 10 times (depending on the screen and browser concept of pixels per inch) for viewing here. If you right click, view image, you will get the full 100 times size image, and the browser controls can be used to zoom in, out, and pan.

<img src="examples/horizontal-centred.svg"
 alt="image of horizontally aligned connectors with stretched and centred pads"
 title="4 horizontally aligned connectors with stretched and centred pads"
 width="300">

<img src="examples/horizontal-top.svg"
 alt="image of horizontally aligned connectors with stretched pads shifted to the far top"
 title="4 horizontally aligned connectors with stretched pads shifted to the far top"
 width="300">

<img src="examples/horizontal-top10.svg"
 alt="image of horizontally aligned connectors with stretched pads shifted to the top minus 10 mil padding"
 title="4 horizontally aligned connectors with stretched pads shifted to the top minus 10 mil padding"
 width="300">

<img src="examples/vertical-centred.svg"
 alt="image of vertically aligned connectors with stretched and centred pads"
 title="4 vertically aligned connectors with stretched and centred pads"
 height="300"> &nbsp; <img src="examples/vertical-left.svg"
 alt="image of vertically aligned connectors with stretched pads shifted to the far left"
 title="4 vertically aligned connectors with stretched pads shifted to the far left"
 height="300"> &nbsp; <img src="examples/vertical-right.svg"
 alt="image of vertically aligned connectors with stretched pads shifted to the far right"
 title="4 vertically aligned connectors with stretched pads shifted to the far right"
 height="300">

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
