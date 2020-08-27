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

STRETCHED_PADS_VERSION = '0.0.1'
PAD_BOT_POSITION = 'bottom'
PAD_TOP_POSITION = 'top'
PAD_CEN_POSITION = 'centre'

def float2int(value: float) -> float:
    '''return an integral representation of a float value where that is equivalent'''
    int_value = int(value)
    if value == int_value:
        return int_value
    return value
# end def float2int()

def validate_parameter_relations(parameters: argparse.Namespace) -> list:
    '''check the limits for parameter values that are not easy to valid
    within argparse

    The individual limit checks could be added with custom action methods,
    but comparing the value of one argument to another is a lot more
    difficult. There does not seem to be a way for an argparse validation
    to be run after all of a set of arguments have been proccessed (or
    defaulted)
    '''
    #pylint: disable=too-many-branches,too-many-statements
    exception_messages = []

    if parameters.hole_diameter < 0:
        exception_messages.append(
            'hole diameter can not be negative: use 0 to create an smd pad')
    if parameters.pad_width <= 0:
        exception_messages.append(
            'pad width must be positive')
    if parameters.pad_length <= 0:
        exception_messages.append(
            'pad length must be positive')
    if parameters.hole_padding < 0:
        exception_messages.append(
            'hole pad can not be negative')
    if parameters.first_connector < 0:
        exception_messages.append(
            'connector id number can not be negative')
    if parameters.row_pins <= 0:
        exception_messages.append(
            'the number of pins in a row must be positive (at least 1)')
    if parameters.pad_spacing <= 0:
        exception_messages.append(
            'the pad spacing distance must be positive')
    if parameters.keepout <= 0:
        exception_messages.append(
            'the keepout distance must be positive')

    if parameters.pad_width <= parameters.hole_diameter:
        exception_messages.append(
            'pad width must be larger than the hole diameter')
    if parameters.pad_length < parameters.pad_width:
        exception_messages.append((
            'pad length can not be less than the pad width: '
            'use the same value as the width to get a circular pad'))
    if parameters.pad_spacing < parameters.pad_width + parameters.keepout:
        exception_messages.append((
            'pad spacing must be at least pad width plus keepout to '
            'prevent design rules check conflicts'))
    if parameters.pad_width == parameters.pad_length:
        if parameters.pad_position != PAD_CEN_POSITION:
            exception_messages.append('pad position must be `centre` for a circular pad')
    if parameters.pad_position == PAD_CEN_POSITION:
        if parameters.hole_padding != 0:
            exception_messages.append(
                'hole padding can not be applied when the hole is centred')
    else:
        # The maximum padding would (almost) move the pad from the end position
        # back to centred over the circle
        offset_limit = float2int((parameters.pad_length - parameters.pad_width) / 2)
        if parameters.hole_padding >= offset_limit:
            exception_messages.append((
                'with the specified length, width, and diameter, the hole'
                ' padding must be less than {0}').format(offset_limit))
    # end else not parameters.pad_position == PAD_CEN_POSITION
    if parameters.pad_length == parameters.pad_width:
        raise NotImplementedError(
            'current version of the code does not support creating only circular pads')

    return exception_messages
# end def validate_parameter_relations()

class MakeStretched:
    '''Create Fritzing SVG PCB view stretched pads from parameter constraints'''
    TEMPLATE_PATH = 'templates'
    DBG_SHOW_PARAMS = 0x1
    DBG_SHOW_PAD = 0x2
    DBG_SHOW_DRAWING = 0x4
    DBG_SCALE_100_TIMES = 0x8
    CON_PREFIX_DEFAULT = 'connector'
    CON_SUFFIX_DEFAULT = 'pad'
    UNITS_INCHES = 'in'
    UNITS_MILLIMETER = 'mm'
    MIL_FACTOR = 1000

    def __init__(self, cmd_args: argparse.Namespace):
        '''gather constraint parameters from command line arguments'''
        self.command_arguments = cmd_args
        result = validate_parameter_relations(cmd_args)
        if result:
            self.report_valdation_exceptions(result)
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
    # end def self.create_jinja_environment()

    @staticmethod
    def report_valdation_exceptions(messages: list) -> None:
        '''show what errors were detected validating the parameter values'''
        # print(messages) # DEBUG
        print('Can not process request\n')
        for msg in messages:
            print(msg)
    # end def report_valdation_exceptions()

    def print_base_arguments(self) -> None:
        '''debug method to dump the main run time parameters'''
        parm = self.command_arguments
        if not parm.debug & self.DBG_SHOW_PARAMS:
            return
        print('\nbase argument values')
        print('hole diameter: {0}'.format(parm.hole_diameter))
        print('pad width: {0}'.format(parm.pad_width))
        print('pad length: {0}'.format(parm.pad_length))
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

    def build_drawing_data(self) -> dict:
        '''populate dictionary with drawing level data for the generated image file'''
        parm = self.command_arguments
        data = {
            'units': self.UNITS_INCHES,
            'px_width': parm.pad_width + (parm.row_pins - 1) * parm.pad_spacing,
            'px_height': parm.pad_length
        }
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
        data['full_width'] = parm.pad_width
        data['half_width'] = float2int(parm.pad_width / 2)
        data['full_length'] = parm.pad_length
        data['circle_radius'] = float2int((
            (parm.hole_diameter / 2) +
            (parm.pad_width - parm.hole_diameter) / 4))
        if parm.pad_position == PAD_CEN_POSITION:
            data['centre_offset'] = float2int((parm.pad_length - parm.pad_width) / 2)
        elif parm.pad_position == PAD_BOT_POSITION:
            data['centre_offset'] = parm.hole_padding
        else: # parm.pad_position == PAD_TOP_POSITION:
            data['centre_offset'] = parm.pad_length - parm.pad_width - parm.hole_padding
        self.print_pad_parameters(data)
        return data
    # end def build_pad_data()

    def generate_svg_pads(self) -> None:
        '''create and output a complete svg file based on the instance parameters'''
        self.print_base_arguments() # DEBUG
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
            dest='pad_position',
            action='store', required=False,
            default=PAD_CEN_POSITION,
            choices=[PAD_CEN_POSITION, PAD_TOP_POSITION, PAD_BOT_POSITION],
            help='position of the pad relative to the hole: %(choices)s')
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
