#!/usr/bin/env python
"""This is a script that takes a set of CantusCorpus CSV files, names
of sources (can be internal nodes for ASR output files, or actual source sigla),
and computes the most significant differences between the melodies in the selected sources.

The differences are unigrams for now. Maybe bigrams later.
"""

import argparse
import csv
import logging
import pprint
import time


def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--input_csvs', '-i', type=str, nargs='+', required=True,
                        help='Paths to the input CSV files in CantusCorpus format.'
                             ' The statistics will be computed across all of them.'
                             ' Assumes only one melody in each of the CSVs belongs to'
                             ' each of the sigla, and that the CSVs are aligned.')
    parser.add_argument('--sigla', '-s', type=str, nargs='+', required=True,
                        help='Source sigla or internal node names to compare.'
                             ' The statistics will be computed for these sources pairwise.')


    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def main(args):
    logging.info('Starting main...')
    _start_time = time.process_time()

    # Load the input CSVs.
    chants_per_csv = {}
    for input_csv in args.input_csvs:
        with open(input_csv, 'r', newline='') as fh:
            chants_reader = csv.DictReader(fh)
            chants = [row for row in chants_reader]
        chants_per_csv[input_csv] = chants

    # Debug: how many chants in each CSV?
    #logging.debug('Read chants from {0} CSVs.'.format(len(chants_per_csv)))
    #logging.debug('Chants per CSV: {0}'.format({k: len(v) for k, v in chants_per_csv.items()}))

    # Filter out only the chants that belong to the sigla we are interested in.
    # If a siglum is not found in a CSV, warn (later: fill in with gaps, for now: None).
    chants_per_csv_with_sigla = {}
    for chant_csv in chants_per_csv:
        chants_per_csv_with_sigla[chant_csv] = {}
        for chant in chants_per_csv[chant_csv]:
            if chant['siglum'] in args.sigla:
                siglum = chant['siglum']
                if siglum not in chants_per_csv_with_sigla[chant_csv]:
                    chants_per_csv_with_sigla[chant_csv][siglum] = []
                chants_per_csv_with_sigla[chant_csv][siglum].append(chant)

    # Debug: how many chants for each siglum in each CSV?
    logging.debug('Chants for sigla per CSV: {0}'.format(pprint.pformat({csv: {siglum: len(chants) for siglum, chants in chants_per_csv_with_sigla[csv].items()} for csv in chants_per_csv})))

    melodies_per_csv_with_sigla = {}
    for chant_csv in chants_per_csv_with_sigla:
        melodies_per_csv_with_sigla[chant_csv] = {}
        for siglum in chants_per_csv_with_sigla[chant_csv]:
            melodies_per_csv_with_sigla[chant_csv][siglum] = [chant['volpiano'] for chant in chants_per_csv_with_sigla[chant_csv][siglum]]

    # Now we have a data structure ready for counting differences.
    # We will count unigram differences for now.
    # Let's assume we only have two sigla for now.
    differences_dict = {}  # Keys: (note_siglum1, note_siglum2), values: count of differences
    bigram_differences_dict = {}  # Keys: (note1_siglum1 + note2_siglum1, note1_siglum2 +note2_siglum2),
                                  # values: count of differences
    permissive_bigram_differences_dict = {}  # Keys: (note1_siglum1 + note2_siglum1, note1_siglum2 +note2_siglum2),
                                             # values: count of differences in the non-gap regime.
    for chant_csv in melodies_per_csv_with_sigla:
        logging.debug('...counting differences in {0}'.format(chant_csv))
        _n_differences_in_csv = 0
        _n_positions_in_csv = 0

        _seen_sigla_pairs = set()
        for siglum1 in args.sigla:
            for siglum2 in args.sigla:
                if siglum1 == siglum2:
                    continue
                if (siglum1, siglum2) in _seen_sigla_pairs:
                    continue
                if (siglum2, siglum1) in _seen_sigla_pairs:
                    continue
                _seen_sigla_pairs.add((siglum1, siglum2))

                # Debug: what's a melody?
                logging.debug('\t\tMelody for siglum 1 = {} : {}'.format(siglum1, melodies_per_csv_with_sigla[chant_csv][siglum1][0]))
                _n_positions_in_csv = len(melodies_per_csv_with_sigla[chant_csv][siglum1][0])

                # Unigram differences
                for melody1, melody2 in zip(melodies_per_csv_with_sigla[chant_csv][siglum1],
                                            melodies_per_csv_with_sigla[chant_csv][siglum2]):
                    logging.debug('\t\t\tComparing melodies: {0} vs. {1}'.format(melody1, melody2))
                    for note1, note2 in zip(melody1,
                                            melody2):
                        if note1 != note2:
                            if (note1, note2) not in differences_dict:
                                differences_dict[(note1, note2)] = 0
                            differences_dict[(note1, note2)] += 1
                            _n_differences_in_csv += 1

                # Bigram differences
                _n_bigram_differences_in_csv = 0
                for melody1, melody2 in zip(melodies_per_csv_with_sigla[chant_csv][siglum1],
                                            melodies_per_csv_with_sigla[chant_csv][siglum2]):
                    logging.debug('\t\t\tComparing melodies: {0} vs. {1}'.format(melody1, melody2))
                    for (note1_1, note1_2), (note2_1, note2_2) in zip(zip(melody1[:-1], melody1[1:]),
                                                                    zip(melody2[:-1], melody2[1:])):
                        if (note1_1, note1_2) != (note2_1, note2_2):
                            _bigram_pair = (note1_1 + note1_2, note2_1 + note2_2)
                            if _bigram_pair not in bigram_differences_dict:
                                bigram_differences_dict[_bigram_pair] = 0
                            bigram_differences_dict[_bigram_pair] += 1
                            _n_bigram_differences_in_csv += 1

                # Permissive bigram differences: if the second note is a gap, find the next non-gap
                # and use that.
                _n_permissive_bigram_differences_in_csv = 0
                _end_of_melody = False
                for melody1, melody2 in zip(melodies_per_csv_with_sigla[chant_csv][siglum1],
                                            melodies_per_csv_with_sigla[chant_csv][siglum2]):
                    logging.debug('\t\t\tComparing melodies: {0} vs. {1}'.format(melody1, melody2))
                    _i1 = 0 # Position in forst melody
                    _i2 = 0 # position in second melody
                    while _i1 < len(melody1) - 1 and _i2 < len(melody2) - 1:
                        # No bigrams starting on a gap.
                        while melody1[_i1] == '-':
                            _i1 += 1
                            if _i1 >= len(melody1):
                                _end_of_melody = True
                                break
                        if _end_of_melody: break

                        while melody2[_i2] == '-':
                            _i2 += 1
                            if _i2 >= len(melody2):
                                _end_of_melody = True
                                break
                        if _end_of_melody: break

                        # Get second character of bigram.
                        _offset_i1 = 1
                        while melody1[_i1 + _offset_i1] == '-':
                            _offset_i1 += 1
                            if _i1 + _offset_i1 >= len(melody1):
                                _end_of_melody = True
                                break
                        if _end_of_melody: break
                        _bigram_1 = melody1[_i1] + melody1[_i1 + _offset_i1]

                        _offset_i2 = 1
                        while melody2[_i2 + _offset_i2] == '-':
                            _offset_i2 += 1
                            if _i2 + _offset_i2 >= len(melody2):
                                _end_of_melody = True
                                break
                        if _end_of_melody: break
                        _bigram_2 = melody2[_i2] + melody2[_i2 + 1]

                        # If we are at the end of the melody, stop - doesn't make sense to compare anything.
                        if _end_of_melody:
                            break

                        if _bigram_1 != _bigram_2:
                            _n_permissive_bigram_differences_in_csv += 1
                            _bigram_pair = (_bigram_1, _bigram_2)
                            if _bigram_pair not in permissive_bigram_differences_dict:
                                permissive_bigram_differences_dict[_bigram_pair] = 0
                            permissive_bigram_differences_dict[_bigram_pair] += 1

                        # Move positions of next 1st character to where the 2nd character is in both
                        # melodies. Note that one melody may have moved so far ahead (in case of a long
                        # gap) that the second one must catch up.
                        if _i1 + _offset_i1 < _i2 + _offset_i2:
                            _i1 += _offset_i1
                        elif _i2 + _offset_i2 < _i1 + _offset_i1:
                            _i2 += _offset_i2
                        else:
                            _i1 += _offset_i1
                            _i2 += _offset_i2


        # Debug: how many differences in this CSV?
        logging.debug('...Differences in {0}: {1} / {2}'.format(chant_csv, _n_differences_in_csv, _n_positions_in_csv))
        logging.debug('...Bigram differences in {0}: {1} / {2}'.format(chant_csv, _n_differences_in_csv, _n_positions_in_csv))

    # Debug: print the differences.
    logging.info('Total differences in all CSVs: {0}'.format(sum(differences_dict.values())))
    logging.info('Differences: {0}'.format(pprint.pformat(differences_dict)))

    logging.info('Total bigram differences in all CSVs: {0}'.format(sum(bigram_differences_dict.values())))
    logging.info('Bigram differences: {0}'.format(pprint.pformat(bigram_differences_dict)))

    logging.info('Total permissive bigram differences in all CSVs: {0}'.format(sum(permissive_bigram_differences_dict.values())))
    logging.info('Permissive bigram differences: {0}'.format(pprint.pformat(permissive_bigram_differences_dict)))

    # chants_for_sigla = {}
    # for siglum in args.sigla:
    #     chants_for_sigla[siglum] = [chant for chants in chants_for_sigla_per_csv[siglum].values() for chant in chants if chants]
    #
    # # Debug: how many chants for each siglum?
    # logging.debug('Chants for sigla: {0}'.format({siglum: len(chants) for siglum, chants in chants_for_sigla.items()}))

    # Difference counting is done per CSV, because we assume one CSV = one CantusID.
    # (This should be done better -- from any input CSV, match chants by CantusID.)


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
