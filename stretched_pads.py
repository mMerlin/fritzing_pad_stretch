#!/usr/bin/env python3
# coding=utf-8

'''
generate svg with stretched pad(s) for pcb view of Fritzing parts
'''

# pipenv shell
# pipenv run pylint stretched_pads.py

# standard library imports
import argparse

# related third party imports
from jinja2 import Environment, FileSystemLoader, StrictUndefined
# Template #, escape

STRETCHED_PADS_VERSION = '0.0.1'

def validate_parameter_relations(parameters: argparse.Namespace) -> dict:
    '''check the limits for parameter values that are not easy to valid
    within argparse

    The individual limit checks could be added with custom action methods,
    but comparing the value of one argument to another is a lot more
    difficult. There does not seem to be a way for an argparse validation
    to be run after all of a set of arguments have been proccessed (or
    defaulted)
    '''
    #pylint: disable=too-many-branches
    error_count = 0
    exception_messages = []

    if parameters.hole_diameter < 0:
        error_count += 1
        exception_messages.append(
            'hole diameter can not be negative: use 0 to create an smd pad')
    if parameters.pad_width <= 0:
        error_count += 1
        exception_messages.append(
            'pad width must be positive')
    if parameters.pad_length <= 0:
        error_count += 1
        exception_messages.append(
            'pad length must be positive')
    if parameters.hole_padding < 0:
        error_count += 1
        exception_messages.append(
            'hole pad can not be negative')
    if parameters.first_connector < 0:
        error_count += 1
        exception_messages.append(
            'connector id number can not be negative')
    if parameters.row_pins <= 0:
        error_count += 1
        exception_messages.append(
            'the number of pins in a row must be positive (at least 1)')
    if parameters.pad_spacing <= 0:
        error_count += 1
        exception_messages.append(
            'the pad spacing distance must be positive')
    if parameters.keepout <= 0:
        error_count += 1
        exception_messages.append(
            'the keepout distance must be positive')

    if parameters.pad_width <= parameters.hole_diameter:
        error_count += 1
        exception_messages.append(
            'pad width must be larger than the hole diameter')
    if parameters.pad_length < parameters.pad_width:
        error_count += 1
        exception_messages.append((
            'pad length can not be less than the pad width: '
            'use the same value as the width to get a circular pad'))
    if parameters.pad_spacing < parameters.pad_width + parameters.keepout:
        error_count += 1
        exception_messages.append((
            'pad spacing must be at least pad width plus keepout to '
            'prevent design rules check conflicts'))
    if parameters.pad_width == parameters.pad_length:
        if parameters.hole_position != 'centre':
            error_count += 1
            exception_messages.append('hole position must be `centre` for a circular pad')
    if parameters.hole_position == 'centre':
        if parameters.hole_padding != 0:
            error_count += 1
            exception_messages.append(
                'hole padding can not be applied when the hole is centred')
    else:
        offset_limit = ( # maximum possible offset from centre
            (parameters.pad_length / 2) -
            (parameters.hole_diameter / 2) -
            (parameters.pad_width - parameters.hole_diameter))
        if parameters.hole_padding >= offset_limit:
            error_count += 1
            exception_messages.append((
                'with the specified length, width, and diameter, the hole'
                ' padding must be less than {0}').format(offset_limit))
        raise NotImplementedError(
            'current version of the code only supports pads centred around the hole')
    # end else not parameters.hole_position == 'center'
    if parameters.pad_length == parameters.pad_width:
        raise NotImplementedError(
            'current version of the code does not support creating only circular pads')


    # parameters.hole_diameter
    # parameters.pad_width
    # parameters.pad_length
    # parameters.hole_position
    # parameters.hole_padding

    return {
        'errors': error_count,
        'messages': exception_messages
    }
# end def validate_parameter_relations:

def float2int(value: float) -> float:
    '''return an integral representation of a float value where that is equivalent'''
    int_value = int(value)
    if value == int_value:
        return int_value
    return value
# end def float2int:

class MakeStretched:
    '''Create Fritzing SVG PCB view stretched pads from parameter constraints'''
    TEMPLATE_PATH = 'templates'
    DBG_SCALE_100_TIMES = 0x1

    def __init__(self, cmd_args: argparse.Namespace):
        '''gather constraint parameters from command line arguments'''
        # http://zetcode.com/python/jinja/
        # see 'import Environment'
        self.command_arguments = cmd_args
        result = validate_parameter_relations(cmd_args)
        if result['errors'] > 0:
            print(result) # DEBUG
            print('Can not process request\n')
            for msg in result['messages']:
                print(msg)
            return
        self.jinja_env = self.create_jinja_environment()
        self.generate_svg_pads()
    # end def __init__()

    def create_jinja_environment(self):
        '''create an initialize an environment to use for templating'''
        file_loader = FileSystemLoader(self.TEMPLATE_PATH)
        env = Environment(loader=file_loader, undefined=StrictUndefined)
        env.globals.update(clean_number=float2int)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.keep_trailing_newline = True
        return env
    # end def self.create_jinja_environment():

    def print_base_arguments(self) -> None: # DEBUG
        '''debug method to dump the main run time parameters'''
        parm = self.command_arguments
        print('hole diameter: {0}'.format(parm.hole_diameter))
        print('pad width: {0}'.format(parm.pad_width))
        print('pad length: {0}'.format(parm.pad_length))
        print('hole position: {0}'.format(parm.hole_position))
        print('hole padding: {0}'.format(parm.hole_padding))
        print('debug: {0}'.format(bin(parm.debug)))
    # end def print_base_arguments(): # DEBUG

    def build_drawing_data(self) -> dict:
        '''populate dictionary with drawing level data for the generated image file'''
        parm = self.command_arguments
        data = {
            'units': 'in',
            'px_width': parm.pad_width + (parm.row_pins - 1) * parm.pad_spacing,
            'px_height': parm.pad_length
        }
        scale_factor = 10 if parm.debug & self.DBG_SCALE_100_TIMES else 1000
        data['unit_height'] = float2int(data['px_height'] / scale_factor)
        data['unit_width'] = float2int(data['px_width'] / scale_factor)
        return data
    # end def build_drawing_data():

    def build_pad_data(self) -> dict:
        '''populate dictionary with pad level data for the generated image file'''
        parm = self.command_arguments
        data = {}
        data['connector_prefix'] = 'connector'
        data['connector_suffix'] = 'pad'
        data['starting_connector'] = parm.first_connector
        data['pin_spacing'] = parm.pad_spacing
        data['hole_width'] = parm.hole_diameter
        data['hole_radius'] = float2int(parm.hole_diameter / 2)
        data['full_width'] = parm.pad_width
        data['half_width'] = float2int(parm.pad_width / 2)
        data['full_length'] = parm.pad_length
        data['circle_radius'] = float2int((
            (parm.hole_diameter / 2) +
            (parm.pad_width - parm.hole_diameter) / 4))
        data['inner_padding'] = 1 # px/mil
        return data
    # end def build_pad_data():

    def generate_svg_pads(self) -> None:
        '''create and output a complete svg file based on the instance parameters'''
        # control whitespace summary : https://stackoverflow.com/a/35777386
        # control whitespace docs:
        #   https://jinja.palletsprojects.com/en/master/templates/#whitespace-control
        self.print_base_arguments() # DEBUG
        drawing_data = self.build_drawing_data()
        pad_data = self.build_pad_data()
        # Hole center is the origin (0,0) point for the pad
        # template = env.get_template('wrapped_pad_holes.svg')
        template = self.jinja_env.get_template('tht_separate_hold_pad.svg')
        output = template.render(
            pad=pad_data,
            drawing=drawing_data,
            connectors=range(self.command_arguments.row_pins))
        self.command_arguments.svg_file.write(output)
        # create macro, use indent https://stackoverflow.com/a/10997352
        # do not indent first https://stackoverflow.com/a/31856334
        # use `set` (and namespace) to carry indent increments through nesting
        # https://jinja.palletsprojects.com/en/2.11.x/templates/#assignments
        # from above, maybe block assignment instead of macro
        # report statistics about the generated hole set:
        #  trace width that will fit between pads at specified keepout
        #    assuming more than one pin
        #  trace width that will fit 2 traces between pads at specified keepout
        #  number of `zero` width «keepout width» traces that will fit between pads
        #    int(separation / keepout) - 1
        #    (int(separation / keepout) - 1) % 2 - 1 ??
    # end def generate_svg_pads:
# end class MakeStretched


class CommandLineParser:
    '''handle command line argument parsing'''
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.parser = CommandLineParser.build_parser()
        self.command_arguments = self.parser.parse_args()

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        '''create command line argument parser'''
        parser = argparse.ArgumentParser(
            description='Fritzing SVG Stretched PCB pad builder',
            prefix_chars='-',
            fromfile_prefix_chars='@',
            usage='%(prog)s [options] [@parameter_file] output_file',
            allow_abbrev=True)
        parser.add_argument(
            '--version', action='version',
            version='%(prog)s ' + STRETCHED_PADS_VERSION)
        parser.add_argument(
            'svg_file', metavar='output-svg-file',
            action='store',
            type=argparse.FileType('w'),
            help='SVG file to create')
        parser.add_argument(
            '-v', '--verbose', action='count', required=False,
            default=0,
            help='increase verbosity')
        parser.add_argument(
            '-d', '--diameter', metavar='d',
            dest='hole_diameter',
            action='store', required=False, type=int,
            default=38,
            help='connector hole diameter in mils (1/1000 in)')
        parser.add_argument(
            '-w', '--width', metavar='w',
            dest='pad_width',
            action='store', required=False, type=int,
            default=45,
            help='narrowest dimension of pad in mils (1/1000 in, must be > diameter')
        parser.add_argument(
            '-l', '--length', metavar='l',
            dest='pad_length',
            action='store', required=False, type=int,
            default=90,
            help='longest dimension of pad in mils (1/1000 in, must be > width)')
        parser.add_argument(
            '-P', '--position', metavar='pos',
            dest='hole_position',
            action='store', required=False,
            default='centre',
            choices=['centre', 'start', 'end'],
            help='position of the hole within the elongated pad: %(choices)s')
        parser.add_argument(
            '-p', '--padding', metavar='p',
            dest='hole_padding',
            action='store', required=False, type=int,
            default=0,
            help='''for positions other than `centre`, extra room to leave beyond
                that provided by the difference between diameter and width''')
        parser.add_argument(
            '-f', '--first-connector', metavar='n',
            dest='first_connector',
            action='store', required=False, type=int,
            default=0,
            help='The number (id) of the first (lowest) connector pad to generate')
        parser.add_argument(
            '-r', '--row-pins', metavar='n',
            dest='row_pins',
            action='store', required=False, type=int,
            default=0,
            help='The number of pins to included in a single row')
        parser.add_argument(
            '-s', '--pad-spacing', metavar='d',
            dest='pad_spacing',
            action='store', required=False, type=int,
            default=100,
            help='The centre to center distance between adjacent connector pads')
        parser.add_argument(
            '-k', '--keepout', metavar='d',
            dest='keepout',
            action='store', required=False, type=int,
            default=10,
            help='The minimum separation between traces to satisfy design rules')
        # connector id prefix text; connector id suffix text
        # connector id template regex: «prefix»«first_connector»«suffix»
        # save as defaults (create file that can be used with `@` prefix)
        # keep out distance

        # try making the debug entry into a sub-parser, and set
        # `formatter_class=argparse.RawTextHelpFormater` in call that creates instance
        # or put everything else into a sub-parser
        #   https://stackoverflow.com/questions/29613487/
        #     multiple-lines-in-python-argparse-help-display
        # alternate implementation subclassing HelpFormatter, then use inline tag so only
        # affects the specific help string
        #  https://exceptionshub.com/python-argparse-how-to-insert-newline-in-the-help-text.html
        parser.add_argument(
            '-D', '--debug', metavar='bits',
            dest='debug',
            action='store', required=False, type=int,
            default=0,
            help='''debug flags\n
            A single integer value that represents the binary `or` of the desired debug control flags\n
            bit\n
             0 100 times scaling\n
            ''')
        # ignore min and max limits
        # reverse hole position for 2nd row
        # connector id suffix «pin¦pad»
        # first connector id "connector«n»«pin¦pad»"
        # drawing margin (css style: top, right, bottom, left)
        # silkscreen: horizontal¦vertical brackets; "L" corners; Cut marks; end notched chip
        # -- margin
        return parser
    # end def build_parser:
# end class CommandLineParser:

def my_main() -> None:
    '''wrapper for test/start code so that variables do not look like constants'''
    print('\n\n') #DEBUG
    cli_parser = CommandLineParser()
    stretch_parameters = (cli_parser.command_arguments)
    MakeStretched(stretch_parameters)
# end def my_main:

# Standalone module execution
if __name__ == "__main__":
    my_main()

# variables, options, flags
#   cSpell:words
# cSpell:enableCompoundWords
