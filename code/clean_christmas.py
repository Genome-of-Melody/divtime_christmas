#!/usr/bin/env python
"""This is a script that..."""

import argparse
import logging
import time

import pandas as pd
import volpiano     # Local relative import. Bad practice, but quick dirty solution for now.


def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--input_csv', '-i', type=str, required=True,
                        help='Path to the CSV file with the Christmas chants to clean.')
    parser.add_argument('--output_csv', '-o', type=str, required=True,
                        help='Path to the output CSV file with the cleaned Christmas chants.')

    parser.add_argument('--clean_volpiano', '-c', action='store_true',
                        help='Perform bacor/ISMIR2020 style cleaning'
                             ' of the volpiano melodies, so that only the'
                             ' note characters remain.')
    parser.add_argument('--clean_volpiano_retain_boundaries', '-b', action='store_true',
                        help='Perform bacor/ISMIR2020 style cleaning'
                             ' that retains neume, syllable and word boundaries as hyphens.')
    parser.add_argument('--normalize_liquescents', '-n', action='store_true',
                        help='Change all liquescents to normal notes.')
    parser.add_argument('--discard_differentiae', '-d', action='store_true',
                        help='Remove all differentiae from antiphons.'
                             ' Only makes sense if we are really processing'
                             ' antiphons.')
    parser.add_argument('--discard_repetenda', '-r', action='store_true',
                        help='In addition to discarding differentiae (everything after a \'4\''
                             ' in volpiano), discards repetenda cues and other elements like'
                             ' verse incipits (applies the same logic to a single barline -- '
                             ' a \'3\' in volpiano).')
    parser.add_argument('--expand_accidentals', '-e', action='store_true',
                        help='Expands accidentals according to bacor/ISMIR2020'
                             ' rules (volpiano.expand_accidentals())')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def main(args):
    logging.info('Starting main...')
    _start_time = time.process_time()

    chants_df = pd.read_csv(args.input_csv)

    # Differentiae have to be cleaned out before clean_volpiano
    # strips all the barlines out.
    if args.discard_differentiae:
        logging.info('Discarding differentiae...')
        if args.discard_repetenda:
            logging.info('\tIncluding repetenda.')
        cleaned_volpiano = [volpiano.discard_differentia(v, apply_to_repetenda=args.discard_repetenda)
                            for v in chants_df.volpiano.to_list()]
        chants_df.volpiano = pd.Series(cleaned_volpiano)
    if args.expand_accidentals:
        logging.info('Expanding accidentals...')
        expanded_volpiano = [volpiano.expand_accidentals(v, omit_notes=True)
                             for v in chants_df.volpiano.to_list()]
        chants_df.volpiano = pd.Series(expanded_volpiano)
    if args.clean_volpiano:
        logging.info('Cleaning volpiano...')
        if args.clean_volpiano_retain_boundaries:
            bounds = {'neume_boundary': '-', 'syllable_boundary': '--', 'word_boundary': '---'}
            cleaned_volpiano = [volpiano.clean_volpiano(v, strip_boundaries_at_ends=True, keep_boundaries=True, **bounds)
                                for v in chants_df.volpiano.to_list()]
            chants_df.volpiano = pd.Series(cleaned_volpiano)
        else:
            cleaned_volpiano = [volpiano.clean_volpiano(v)
                                for v in chants_df.volpiano.to_list()]
            chants_df.volpiano = pd.Series(cleaned_volpiano)
    if args.normalize_liquescents:
        logging.info('Normalizing liquescents...')
        normalized_volpiano = [volpiano.normalize_liquescents(v)
                               for v in chants_df.volpiano.to_list()]
        chants_df.volpiano = pd.Series(normalized_volpiano)

    chants_df.to_csv(args.output_csv, index=False)

    _end_time = time.process_time()
    logging.info('scrape_cantus_db_sources.py done in {0:.3f} s'.format(_end_time - _start_time))


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main(args)
