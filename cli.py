"""
Command Line Interface (CLI) object. Once the CLI is initiated, call get_arg(arg) to get the value of a command line argument.
"""

# Standard library imports
import argparse


class CLI:
  def __init__(self):
    self.arg_parser = None
    self.args = None
    self.cli()

  # def get_arg(self, arg):
  #   return self.args[arg]

  def get_arg(self, arg):
    return self.args.get(arg)  # .get() method returns None if the key doesn't exist, avoiding KeyError

  def cli(self):
    # Create the parser
    self.arg_parser = argparse.ArgumentParser(
      description="Halt! What's the Passphrase? generates passphrases as well as traditional passwords. Try the -w Wikipedia passphrase option!", 
      prog="Halt! What's the Passphrase?")
    
    # Create the subparser
    subparsers = self.arg_parser.add_subparsers(dest='subparser_name')

    # Create the parser for the "password" command
    pw_parser = subparsers.add_parser('pw', 
                                      help='Generate passwords',
                                      prog="Halt! What's the Passphrase?",
                                      epilog="'Friends don't let friends use weak or compromised passwords!'")

    # Create the parser for the "passphrase" command
    pp_parser = subparsers.add_parser('pp', 
                                      help='Generate passphrases',
                                      prog="Halt! What's the Passphrase?",
                                      epilog="'Friends don't let friends use weak or compromised passwords!'")

    # Create the parser for the "pwnage" command
    pwn_parser = subparsers.add_parser('pwn', 
                                      help='Check password pwnage',
                                      prog="Halt! What's the Passphrase?",
                                      epilog="'Friends don't let friends use weak or compromised passwords!'")

    # Create the parser for the "utils" command
    utils_parser = subparsers.add_parser('utils',
                                         help='Utilities',
                                         prog="Halt! What's the Passphrase?",
                                         epilog="'Friends don't let friends use weak or compromised passwords!'")

    # Enable subcommands for the utils command
    utils_subparsers = utils_parser.add_subparsers(dest='utils_command')

    # Create the parser for the "part" (Partitions) option under "utils"
    part_parser = utils_subparsers.add_parser('part', help='Generate partitions dict.')

    # Add arguments specific to the 'part' option
    part_parser.add_argument('-minp', type=int, help='Minimum partition size. Default = 10.', default=10)
    part_parser.add_argument('-maxp', type=int, help='Maximum partition size. Default = 50.', default=50)
    part_parser.add_argument('-minw', type=int, help='Minimum word length in partitions. Default = 4.', default=4)
    part_parser.add_argument('-maxw', type=int, help='Maximum word length in partitions. Default = 9.', default=9)
    part_parser.add_argument('-file', type=str, help='Specify a file for additional processing or output. Default = none.', default=None)

                      # Create the parser for the "dict" (Dictionary) option under "utils"
    dict_parser = utils_subparsers.add_parser('dict', help='Generate all dictionary files from a raw dictionary.')

    # Add arguments specific to the 'dict' option
    dict_parser.add_argument('-d', type=str, help='Name of the raw dictionary file. Must be a .txt file. Do not include .txt suffix. Text file must be located in the raw_dictionaries folder.')
    
    # Add arguments to the pwnage subparser
    pwn_parser.add_argument('password')
    
    # Add arguments to the password subparser
    pw_parser.add_argument('-c', '--chars',
                          help='Number of characters per password. Default = 20.',
                          type=int,
                          default=20)
    pw_parser.add_argument('-n', '--num',
                          help='Number of passwords to generate. Default = 1.',
                          type=int,
                          default=1)
    pw_parser.add_argument('-co', '--color',
                          help='Colorize the output text. Default = no colorization.',
                          action='store_true',
                          default=False)
    pw_parser.add_argument('-v', '--verbose',
                          help='Print verbose output. Default = off.',
                          action='store_true',
                          default=False)
    pw_parser.add_argument('-nc', '--noconsec',
                          help='Disallow consecutive duplicate characters in the passphrase. Default = consecutive duplicates are allowed.',
                          action='store_true',
                          default=False)
    pw_parser.add_argument("-no", 
                           type=str, 
                           nargs="*", 
                           choices=['u', 'l', 'd', 's'], 
                           default=list(), 
                           metavar='Disallow Character Classes', 
                           help='Disallow entire classes of characters. Possible values are: \
                           (u)ppercase, (l)owercase, (d)igits, and (s)pecial characters (i.e., punctuation). Default = all character classes allowed.')
    pw_parser.add_argument('-x', '--xtra', help="Give the passphrase an extra shuffle for good luck. Default = don't shuffle an extra time", action='store_true')
    pw_parser.add_argument('-md', '--mindigits',
                          help='Minimum number of digits to use in the passphrase. Default = 0.',
                          type=int,
                          default=0)
    pw_parser.add_argument('-ms', '--minspecials',
                          help='Minimum number of special characters to use in the passphrase. Default = 0.',
                          type=int,
                          default=0)
    pw_parser.add_argument('-a', '--ambiguous',
                          help='Disallow ambiguous characters in the passphrase. Default =\
                          ambiguous characters allowed.',
                          action='store_true',
                          default=False)
    pw_parser.add_argument('-b', '--bookend',
                          help="Only use uppercase or lowercase characters at the start and end \
                          of the passphrase. Default = don't bookend.",
                          action='store_true',
                          default=False)
    pw_parser.add_argument('-so', '--specialsoverride',
                          metavar='Override Special Characters', 
                          help='String of special characters to override the default set of special characters. Default = no override.',
                          default=str())
    pw_parser.add_argument('-sd', '--specialsdeny',
                          help='Remove the specified characters from the default specials alphabet (if present). Default = allow all default special characters.',
                          default=str())
    pw_parser.add_argument('-pwn',
                          help="Submit generated passwords to HaveIBeenPwned to check if they have already been found in a databreach.",
                          action='store_true',
                          default=False)

    # Add arguments to the passphrase subparser
    pp_parser.add_argument('-c', '--chars',
                          help='Number of characters per passphrase.',
                          type=int,
                          default=20)
    pp_parser.add_argument('-n', '--num',
                          help='Number of passphrases to generate.',
                          type=int,
                          default=1)
    pp_parser.add_argument('-co', '--color',
                          help='Colorize the output text.',
                          action='store_true',
                          default=False)
    pp_parser.add_argument('-v', '--verbose',
                          help='Print verbose output.',
                          action='store_true',
                          default=False)
    pp_parser.add_argument('-nw', '--numwords',
                          help='Specify a number of whole words to use for '
                               'the passphrase - do not limit the passphrase based on character '
                               'length. Enter an integer value to specify the number of whole '
                               'words to use for the passphrase. This command overrides the -c '
                               '--chars command (if specified or left at the default value of 20).',
                          type=int,
                          default=False)
    pp_parser.add_argument('-w', '--wikipedia',
                          help='Use Wikipedia as the source for passphrases. Smushes together three (3) randomly selected Wikipedia article titles as the base of the passphrase.',
                          action='store_true',
                          default=False)
    pp_parser.add_argument('-au', '--augenbaumize',
                          help="Use the Augenbaum method. Default = Don't do it.",
                          default=False)
    pp_parser.add_argument('-pwn',
                          help="Submit generated passwords to HaveIBeenPwned to check if they have already been found in a databreach.",
                          action='store_true',
                          default=False)
    pp_parser.add_argument("-pad", 
                           type=str, 
                           nargs=2, 
                           default=False, 
                           metavar='Add a custom string to the beginning, middle, or end of the password.', 
                           help='Enter the string you wish to include in the passphrase, followed by 1, 2, or 3. 1 = pad at beginning, 2 = pad in the middle, 3 = pad at the end. Example: -pad m0nk3y! 1 will produce passphrase: "m0nk3y!PPPPPPPP". -pad m0nk3y! 2 will produce passphrase: "PPPPm0nk3y!PPPP". -pad m0nk3y! 3 will produce passphrase: "PPPPPPPPm0nk3y!".')

    # Get arguments from the command line
    self.args = vars(self.arg_parser.parse_args())
