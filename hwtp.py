"""
Halt! What's the Passphrase? is a passphrase and password generator with a command line interface (CLI) implemented through argparse.
"""

# Local application imports
import cli  # command line interface
import pp  # passphrase generator
import pw  # password generator
import hibp  # check passwords for known breached
import pp_utils  # passphrase utilities
from pathlib import Path

if __name__ == '__main__':
    # CLI object
    cli = cli.CLI()

    # handle top-level options
    if cli.get_arg('list_wordlists'):
        print("Available wordlists:")
        names = pp_utils.list_cached_dictionaries()
        if names:
            for name in names:
                print(f"  {name}")
        else:
            print("  No cached dictionaries available.")
        exit()

    # which module are we running?
    ptype = cli.get_arg('subparser_name')
    if ptype is None:
        print(
            "Select 'pp' for passphrase, 'pw' for password, 'pwn' for password pwnage check, or 'utils' for passphrase utilities.'"
        )
        exit()

    if ptype == 'utils':
        utils_type = cli.get_arg('utils_command')
        start_n = cli.get_arg('start_n')
        end_n = cli.get_arg('end_n')
        min_word_length = cli.get_arg('min_word_length')
        max_word_length = cli.get_arg('max_word_length')
        part_choice = cli.get_arg('partitions')
        include_partitions = False if str(part_choice).lower() == 'false' else True

        if include_partitions:
            if start_n is None or end_n is None:
                print("Both --start-n and --end-n must be specified when -p true.")
                exit(1)
            if not isinstance(start_n, int) or not isinstance(end_n, int):
                print("--start-n and --end-n must be integers.")
                exit(1)
            if start_n < 1:
                print("--start-n must be 1 or greater.")
                exit(1)
            if start_n >= end_n:
                print("--start-n must be less than --end-n.")
                exit(1)
            if end_n > 50:
                print("--end-n cannot be greater than 50.")
                exit(1)

        if utils_type == 'part':
            output_file = cli.get_arg('output')
            if output_file is None:
                print("Output filename required for 'part' command.")
            else:
                pp_utils.create_partitions(
                    partition_path=Path(output_file),
                    start_n=start_n if start_n is not None else min_word_length * 2,
                    end_n=end_n if end_n is not None else max_word_length * 5,
                    min_val=min_word_length,
                    max_val=max_word_length,
                )

        elif utils_type == 'process':
            dict_raw_filename = cli.get_arg('dictionary')
            lang_name = cli.get_arg('name')
            if dict_raw_filename is None:
                print("Dictionary filename required for 'process' command.")
            else:
                pp_utils.process_raw_dictionary(
                    dict_raw_filename,
                    min_word_length,
                    max_word_length,
                    start_n=start_n,
                    end_n=end_n,
                    language=lang_name or Path(dict_raw_filename).stem,
                    include_partitions=include_partitions,
                )

        elif utils_type == 'process-all':
            lang_name = cli.get_arg('name')
            pp_utils.process_all_dictionaries(
                min_word_length=min_word_length,
                max_word_length=max_word_length,
                start_n=start_n,
                end_n=end_n,
                language=lang_name,
                include_partitions=include_partitions,
            )

        exit()

    h = hibp.HIBP()  # HIBP object
    
    # these five command line arguments are the same for both pp and pw
    if ptype == 'pp' or ptype == 'pw':
        num_chars = cli.get_arg('chars')
        num_reps = cli.get_arg('num')
        verbose = cli.get_arg('verbose')
        color = cli.get_arg('color')
        pwn = cli.get_arg('pwn')

    if ptype == 'pwn':
        # submit the password to HaveIBeenPwned
        password = cli.get_arg('password')
        pwn = True
        verbose = True
        return_list = [password]
    elif ptype == 'pp':
        dictionary = cli.get_arg('dictionary')
        start_n = cli.get_arg('start_n')
        end_n = cli.get_arg('end_n')
        pp = pp.passphrase(verbose=verbose, colorize=color, dictionary=dictionary,
                           start_n=start_n, end_n=end_n)

        num_words = cli.get_arg('numwords')
        wiki = cli.get_arg('wikipedia')
        augenbaumize = cli.get_arg('augenbaumize')
        pad = cli.get_arg('pad')
        if pad is not False:
            try:
                pad_str = pad[0]
                pad_pos = int(pad[1])
                if pad_pos not in [1, 2, 3]:
                    print(
                        f"-pad position invalid: {pad_pos}. Pad position must be either 1 (beginning), 2 (middle), or 3 (end). Exiting."
                    )
                    exit(1)
            except Exception as error:
                print(
                    f"-pad arguments invalid: {pad}. Error message: {error}. Exiting."
                )
                exit(1)
            else:
                pad = [pad_str, pad_pos]

        if verbose is True:
            consec_str = f"You asked for {num_reps} passphrase(s) of {num_chars} chars each"

            if wiki is True:
                consec_str += ", using Wikipedia as the source"

            if augenbaumize is not False:
                consec_str += f", using the Augenbaum method with: '{augenbaumize}'"

            if pad is not False:
                consec_str += f", padding the passphrase with: {pad_str} in position: {pad_pos}"

            consec_str += "."
            print(consec_str)

        if wiki is True:
            return_list = pp.generate_passphrase_wikipedia(
                num_reps=num_reps,
                colorize=color,
                augenbaumize=augenbaumize,
                num_titles=3,
                verbose=verbose)
        else:
            return_list = pp.get_passphrase(num_chars=num_chars,
                                            num_reps=num_reps,
                                            num_words=num_words,
                                            verbose=verbose,
                                            augenbaumize=augenbaumize,
                                            pad=pad)
    elif ptype == 'pw':
        pw = pw.password()  # password object

        no_consecutives = cli.get_arg(
            'noconsec'
        )  # True = allow, False = disallow consecutive duplicate characters ('AA', 'aa', 'Aa')
        xtra = cli.get_arg(
            'xtra'
        )  # give pw / pp an extra shuffle for good luck - Lingo rules!
        min_digits = cli.get_arg('mindigits')
        min_specials = cli.get_arg('minspecials')
        ambiguous = cli.get_arg('ambiguous')
        bookend = cli.get_arg('bookend')
        specials_override = cli.get_arg('specialsoverride')
        specials_deny = cli.get_arg('specialsdeny')

        # process the suppress list
        suppress = cli.get_arg('no')
        uppercase = False if 'u' in suppress else True
        lowercase = False if 'l' in suppress else True
        digits = False if 'd' in suppress else True
        specials = False if 's' in suppress else True

        if verbose:
            consec_str = f"You asked for {num_reps}x{num_chars}-character password(s) with a minimum of {min_digits} digits and {min_specials} special characters"
            if ambiguous is True:
                consec_str += ", with no ambiguous characters (l, I, 1, 0, O)"

            if suppress != list():
                sltd = {
                    'u': 'uppercase letters',
                    'l': 'lowercase letters',
                    'd': 'digits (0-9)',
                    's': 'special characters'
                }  # Suppress List Translation Dictionary
                consec_str += ', that does not use the following character classes: '
                consec_str += ', '.join([sltd[x] for x in suppress])

            if no_consecutives is True:
                consec_str += ", with no consecutive duplicate characters allowed"

            if bookend is True:
                consec_str += ", that is bookended (no numbers or specials as the first or last character)"

            if specials_override != str():
                consec_str += f", that uses only the following special characters: {specials_override}"

            if specials_deny != str():
                consec_str += f", that does not use any of the following special characters: {specials_deny}"

            consec_str += "."
            print(consec_str)

        return_list = pw.get_password(num_reps=num_reps,
                                      num_chars=num_chars,
                                      verbose=verbose,
                                      colorize=color,
                                      min_digits=min_digits,
                                      min_specials=min_specials,
                                      uppercase=uppercase,
                                      lowercase=lowercase,
                                      digits=digits,
                                      specials=specials,
                                      extra_shuffle=xtra,
                                      no_consecutives=no_consecutives,
                                      ambiguous=ambiguous,
                                      bookend=bookend,
                                      suppress=suppress,
                                      specials_override=specials_override,
                                      specials_deny=specials_deny)

    # generate return string & print results
    return_string = str()
    for n in return_list:
        if pwn is True:
            pwd_tuple = h.check_password_pwnage(n, verbose=verbose)
            if pwd_tuple[0] is True:
                pwn_str = f" - Pwned! This password has been found in databreaches {pwd_tuple[1]} times."
            else:
                if pwd_tuple[1] == -1:
                    pwn_str = "Error getting data back from HaveIBeenPwned - please try again later, status of this password is unknown at this time."
                else:
                    pwn_str = " - OK! This password has not been found in any databreaches."
            return_string += n + pwn_str
        else:
            return_string += n + "\n"

    print(return_string)
