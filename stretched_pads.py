#!/usr/bin/env python3
# coding=utf-8

'''
generate svg with stretched pad(s) for pcb view of Fritzing parts

stretched: think stretched limousine: cut it in half, and insert an extension.
'''

# pipenv shell
# pipenv run pylint stretched_pads.py

# standard library imports
import sys
import argparse

# related third party imports
from jinja2 import Environment, FileSystemLoader, StrictUndefined

STRETCHED_PADS_VERSION = '0.0.1'
# Pad related constants that are also needed for command line parsing
PAD_POS_TOP = 'top'               # most of pad above circle with horizontal pin row
PAD_POS_BOTTOM = 'bottom'         # most of pad below circle with horizontal pin row
PAD_POS_LEFT = 'left'             # most of pad to left of circle with vertical pin row
PAD_POS_RIGHT = 'right'           # most of pad to right of circle with vertical pin row
PAD_POS_HORIZONTAL = 'horizontal' # centred pad with horizontal pin row
PAD_POS_VERTICAL = 'vertical'     # centred pad with vertical pin row

def err_print(*args, **kwargs) -> None:
    '''function to print to stderr the 'same way' as print to stdout'''
    print(*args, file=sys.stderr, **kwargs)

def float2int(value: float) -> float:
    '''return an integral representation of a float value where that is equivalent

    purpose: keep unneeded decimal fractions out of generated content
    '''
    int_value = int(value)
    if value == int_value:
        return int_value
    return value
# end def float2int()

def represents_int(value: str) -> bool:
    '''detect when a string can be represented as an integer by python'''
    try:
        int(value)
        return True
    except ValueError:
        return False
# end def represents_int(s: str) -> bool:

def natural_number(value: str) -> int:
    '''argparse validation for a positive integer parameter value (> 0)'''
    if not represents_int(value):
        msg = 'invalid int value: {0}'.format(value)
        raise argparse.ArgumentTypeError(msg)
    int_value = int(value)
    if int_value <= 0:
        msg = 'invalid positive int value: {0}'.format(value)
        raise argparse.ArgumentTypeError(msg)
    return int_value
# end def positive_numeric()

def whole_number(value: str) -> int:
    '''argparse validation for a non-negative integer parameter value'''
    if not represents_int(value):
        msg = 'invalid int value: {0}'.format(value)
        raise argparse.ArgumentTypeError(msg)
    int_value = int(value)
    if int_value < 0:
        msg = 'invalid non-negative int value: {0}'.format(value)
        raise argparse.ArgumentTypeError(msg)
    return int_value
# end def positive_numeric()

class MakeStretched:
    '''Create Fritzing SVG PCB view stretched pads from parameter constraints'''
    TEMPLATE_PATH = 'templates'
    DBG_SHOW_PARAMS = 0x1
    DBG_SHOW_PAD = 0x2
    DBG_SHOW_DRAWING = 0x4
    DBG_SCALE_100_TIMES = 0x8
    DBG_SHOW_MULTIPLE_EXCEPTIONS = 0x1000
    CON_PREFIX_DEFAULT = 'connector'
    CON_SUFFIX_DEFAULT = 'pad'
    UNITS_INCHES = 'in'
    UNITS_MILLIMETER = 'mm'
    MIL_FACTOR = 1000 # conversion factor: inches to mils

    def __init__(self, cmd_args: argparse.Namespace):
        '''gather constraint parameters from command line arguments'''
        self.command_arguments = cmd_args
        self.horizontal_factor = None
        self.vertical_factor = None
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
    # end def self.create_jinja_environment()

    def print_base_arguments(self) -> None:
        '''debug method to dump the main run time parameters'''
        parm = self.command_arguments
        if not parm.debug & self.DBG_SHOW_PARAMS:
            return
        print('\nbase argument values')
        print('hole diameter: {0}'.format(parm.hole_diameter))
        print('pad minimum: {0}'.format(parm.pad_min))
        print('pad maximum: {0}'.format(parm.pad_max))
        print('pad position: {0}'.format(parm.pad_position))
        print('hole padding: {0}'.format(parm.hole_padding))
        print('pins in a row: {0}'.format(parm.row_pins))
        print('debug: {0}'.format(bin(parm.debug)))
    # end def print_base_arguments()

    def print_pad_parameters(self, pad: dict) -> None:
        '''debug method to dump the calculated pad parameters'''
        if not self.command_arguments.debug & self.DBG_SHOW_PAD:
            return
        print('\npad parmeters')
        print('Starting connector id: "{0}{1}{2}"'.format(
            pad['connector_prefix'], pad['starting_connector'], pad['connector_suffix']))
        print('pin spacing: {0}'.format(pad['pin_spacing']))
        print('hole width: {0}'.format(pad['hole_width']))
        print('hole radius: {0}'.format(pad['hole_radius']))
        print('full width {0}'.format(pad['full_width']))
        print('half width {0}'.format(pad['half_width']))
        print('full length {0}'.format(pad['full_length']))
        print('circle radius {0}'.format(pad['circle_radius']))
        print('centre offset {0}'.format(pad['centre_offset']))
    # end def print_pad_parameters()

    def print_drawing_parameters(self, draw: dict) -> None:
        '''debug method to dump the calculated pad parameters'''
        if not self.command_arguments.debug & self.DBG_SHOW_DRAWING:
            return
        print('\ndrawing parmeters')
        print('units: "{0}"'.format(draw['units']))
        print('px height {0}'.format(draw['px_height']))
        print('px width {0}'.format(draw['px_width']))
        print('unit height {0}'.format(draw['unit_height']))
        print('unit width {0}'.format(draw['unit_width']))
    # end def print_drawing_parameters()

    def configure_for_direction(self) -> None:
        '''configure constants that allow simple orientation independent calculations

        Set flags so that the rest of the code (mostly) does not need to care
        about the orientation of pads and rows
        The `factors` set here can be used either as multipliers or booleans

        x_value = horizontal_factor * u_value + vertical_factor * v_value
        y_value = horizontal_factor * v_value + vertical_factor * u_value
        '''
        if self.command_arguments.pad_position in (
                PAD_POS_HORIZONTAL, PAD_POS_BOTTOM, PAD_POS_TOP):
            self.horizontal_factor = 1
            self.vertical_factor = 0
        else:
            self.horizontal_factor = 0
            self.vertical_factor = 1
    # end def configure_for_direction()

    def build_drawing_data(self) -> dict:
        '''populate dictionary with drawing level data for the generated image file'''
        parm = self.command_arguments
        data = {
            'units': self.UNITS_INCHES
        }
        if bool(self.horizontal_factor):
            data['px_width'] = parm.pad_min + (parm.row_pins - 1) * parm.pad_spacing
            data['px_height'] = parm.pad_max
        else:
            data['px_height'] = parm.pad_min + (parm.row_pins - 1) * parm.pad_spacing
            data['px_width'] = parm.pad_max
        scale_factor = self.MIL_FACTOR
        if parm.debug & self.DBG_SCALE_100_TIMES:
            scale_factor = float2int(self.MIL_FACTOR / 100)
        data['unit_height'] = float2int(data['px_height'] / scale_factor)
        data['unit_width'] = float2int(data['px_width'] / scale_factor)
        self.print_drawing_parameters(data)
        return data
    # end def build_drawing_data()

    def build_pad_data(self) -> dict:
        '''populate dictionary with pad level data for the generated image file'''
        parm = self.command_arguments
        data = {}
        data['connector_prefix'] = self.CON_PREFIX_DEFAULT
        data['connector_suffix'] = self.CON_SUFFIX_DEFAULT
        data['starting_connector'] = parm.first_connector
        data['pin_spacing'] = parm.pad_spacing
        data['hole_width'] = parm.hole_diameter
        data['hole_radius'] = float2int(parm.hole_diameter / 2)
        data['full_width'] = parm.pad_min
        data['half_width'] = float2int(parm.pad_min / 2)
        data['full_length'] = parm.pad_max
        data['circle_radius'] = float2int((parm.pad_min + parm.hole_diameter) / 4)
        if parm.pad_position in (PAD_POS_HORIZONTAL, PAD_POS_VERTICAL):
            data['centre_offset'] = float2int((parm.pad_max - parm.pad_min) / 2)
        elif parm.pad_position in (PAD_POS_BOTTOM, PAD_POS_RIGHT):
            data['centre_offset'] = parm.hole_padding
        else: # parm.pad_position in (PAD_POS_TOP, PAD_POS_LEFT):
            data['centre_offset'] = parm.pad_max - parm.pad_min - parm.hole_padding
        self.print_pad_parameters(data)
        return data
    # end def build_pad_data()

    def generate_svg_pads(self) -> None:
        '''create and output a complete svg file based on the instance parameters'''
        self.print_base_arguments() # DEBUG
        self.configure_for_direction()
        drawing_data = self.build_drawing_data()
        pad_data = self.build_pad_data()
        template = self.jinja_env.get_template('tht_separate_hole_pad.svg')
        output = template.render(
            pad=pad_data,
            drawing=drawing_data,
            connectors=range(self.command_arguments.row_pins))
        self.command_arguments.svg_file.write(output)
    # end def generate_svg_pads()
# end class MakeStretched


class CommandLineParser:
    '''handle command line argument parsing'''
    DBG_SHOW_MULTIPLE_EXCEPTIONS = 0x1000

    def __init__(self):
        self.parser = CommandLineParser.build_parser()
        self.command_arguments = self.parser.parse_args()
        self.exception_detected = False
        # add interdependent parameter value checking
        self.validate_interdependent_constraints()
    # END def validate_simple_limits()

    def report_exception(self, msg: str) -> None:
        '''Either raise exception, or set flag and report error, based on debug flag'''
        if not self.command_arguments.debug & self.DBG_SHOW_MULTIPLE_EXCEPTIONS:
            raise ValueError(msg)
        self.exception_detected = True
        err_print(msg)
    # end def report_exception()

    def validate_interdependent_constraints(self) -> None:
        '''check the limits for parameter values that are constrained by other parameters

        The initial parsing context is gone, so do not have the parameter parsing properties.
        Can not «easily» use `raise argparse.ArgumentError()` and similar. Can not raise any
        exception and have it automatically caught
        '''
        # pylint: disable=too-many-branches
        parameters = self.command_arguments
        try:
            if parameters.pad_min <= parameters.hole_diameter:
                self.report_exception(
                    'pad minimum ({0}) must be larger than the hole diameter ({1})'.format(
                        parameters.pad_min, parameters.hole_diameter))
            if parameters.pad_max < parameters.pad_min:
                self.report_exception((
                    'pad maximum ({0}) can not be less than the pad minimum ({1}):'
                    ' use identical values to get a circular pad'.format(
                        parameters.pad_max, parameters.pad_min)))
            if parameters.pad_spacing < parameters.pad_min + parameters.keepout:
                self.report_exception((
                    'pad spacing ({0}) must be at least pad minimum ({1}) plus keepout ({2}) to'
                    ' prevent design rules check conflicts'.format(
                        parameters.pad_spacing, parameters.pad_min, parameters.keepout)))
            if parameters.pad_min == parameters.pad_max:
                if parameters.pad_position not in (PAD_POS_HORIZONTAL, PAD_POS_VERTICAL):
                    self.report_exception(
                        'pad position ({0}) must be `horizontal` or `vertical` for a'
                        ' circular pad'.format(parameters.pad_position))
            if parameters.pad_position in (PAD_POS_HORIZONTAL, PAD_POS_VERTICAL):
                if parameters.hole_padding != 0:
                    self.report_exception(
                        'hole padding can not be applied when the pad is centred')
            else: # not parameters.pad_position in (PAD_POS_HORIZONTAL,  PAD_POS_VERTICAL)
                # The maximum padding would (almost) move the pad from the end position
                # back to centred over the circle
                offset_limit = float2int((parameters.pad_max - parameters.pad_min) / 2)
                if parameters.hole_padding >= offset_limit:
                    self.report_exception((
                        'with the specified minimum ({0}) and maximum ({1}), the'
                        ' hole padding ({2}) must be less than {3}').format(
                            parameters.pad_min, parameters.pad_max, parameters.hole_padding,
                            offset_limit))
            # end else not parameters.pad_position in (PAD_POS_HORIZONTAL,  PAD_POS_VERTICAL)

            if parameters.pad_max == parameters.pad_min:
                raise NotImplementedError(
                    'current version of the code does not support creating only circular pads')
            if parameters.pad_position not in (PAD_POS_HORIZONTAL, PAD_POS_BOTTOM, PAD_POS_TOP):
                raise NotImplementedError('vertical pad positioning options not implemented yet')
            if parameters.hole_padding > 0:
                raise NotImplementedError('hold padding offset not implemented yet')
        except ValueError as exception:
            sys.exit(exception)
        if self.exception_detected:
            sys.exit()
    # end def validate_interdependent_constraints()

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        '''create command line argument parser'''
        parser = argparse.ArgumentParser(
            description='Fritzing SVG Stretched PCB pad builder',
            prefix_chars='-',
            fromfile_prefix_chars='@',
            epilog='All size values are in mils (1/1000th inch)',
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
        # parser.add_argument(
        #     '-v', '--verbose', action='count', required=False,
        #     default=0,
        #     help='increase verbosity')
        parser.add_argument(
            '-d', '--diameter', metavar='d',
            dest='hole_diameter',
            action='store', required=False, type=natural_number,
            default=38,
            help='connector hole diameter. Default: %(default)s')
        parser.add_argument(
            '-w', '--minimum', metavar='w',
            dest='pad_min',
            action='store', required=False, type=natural_number,
            default=45,
            help='narrowest dimension of a pad (must be > diameter). Default: %(default)s')
        parser.add_argument(
            '-l', '--maximum', metavar='l',
            dest='pad_max',
            action='store', required=False, type=natural_number,
            default=90,
            help='longest dimension of a pad (must be > width). Default: %(default)s')
        parser.add_argument(
            '-P', '--position', metavar='pos',
            dest='pad_position',
            action='store', required=False,
            default=PAD_POS_HORIZONTAL,
            choices=[PAD_POS_TOP, PAD_POS_BOTTOM, PAD_POS_LEFT, PAD_POS_RIGHT,
                     PAD_POS_HORIZONTAL, PAD_POS_VERTICAL],
            help='position of the pad relative to the hole: %(choices)s. Default: %(default)s')
        parser.add_argument(
            '-p', '--padding', metavar='p',
            dest='hole_padding',
            action='store', required=False, type=whole_number,
            default=0,
            help='''for positions other than `horizontal` or `vertical` (centred),
                extra room to leave beyond that provided by the
                difference between diameter and width. Default: %(default)s''')
        parser.add_argument(
            '-f', '--first-connector', metavar='n',
            dest='first_connector',
            action='store', required=False, type=whole_number,
            default=0,
            help='''The number (id) of the first (lowest) connector pad to generate.
                Default: %(default)s''')
        parser.add_argument(
            '-r', '--row-pins', metavar='n',
            dest='row_pins',
            action='store', required=False, type=whole_number,
            default=1,
            help='The number of pins to included in a single row. Default: %(default)s')
        parser.add_argument(
            '-s', '--pad-spacing', metavar='d',
            dest='pad_spacing',
            action='store', required=False, type=natural_number,
            default=100,
            help='''The centre to centre distance between adjacent
                connector pads in a row. Default: %(default)s''')
        parser.add_argument(
            '-k', '--keepout', metavar='d',
            dest='keepout',
            action='store', required=False, type=natural_number,
            default=10,
            help='''The minimum separation distance between traces to satisfy
                design rules. Default: %(default)s''')

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
        return parser
    # end def build_parser()
# end class CommandLineParser:

def my_main() -> None:
    '''wrapper for test/start code so that variables do not look like constants'''
    cli_parser = CommandLineParser()
    stretch_parameters = (cli_parser.command_arguments)
    MakeStretched(stretch_parameters)
# end def my_main()

# Standalone module execution
if __name__ == "__main__":
    my_main()

# variables, options, flags
#   cSpell:words
# cSpell:enableCompoundWords
