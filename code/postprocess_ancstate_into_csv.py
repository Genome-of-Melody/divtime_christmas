#!/usr/bin/env python
"""This is a script that takes the results of ancestral state reconstruction
and outputs a cantuscorpus-style CSV file that retains the aligned ancestral melodies.

The number codes for interal tree nodes are retained as sigla, with a NODE_ prefix."""


import argparse
import logging
import time

import csv


def normalize_christmas_siglum(siglum):
    siglum = siglum.replace('.', '')
    siglum = siglum.replace('(', '')
    siglum = siglum.replace(')', '')
    siglum = siglum.replace('*', '')
    siglum = siglum.replace('/', ' ')   # For whatever reason...
    return siglum


def normalize_ancstate_siglum(siglum):
    return siglum.replace('_', ' ')


def create_internal_node_siglum(node_number):
    return 'NODE_{}'.format(node_number)


def find_default_chant_fields_dict_for_internal_nodes(christmas_matched_chants):

    populated_default_fields = ['full_text', 'genre_id', 'incipit', 'mode', 'feast_id', 'office_id']
    defaults = {}
    for field in populated_default_fields:
        if field not in christmas_matched_chants[0]:
            raise ValueError('Field {} not found in Christmas matched chants.'.format(field))
        # Get most frequent value of that field.
        _values = [row[field] for row in christmas_matched_chants]
        most_frequent_value = max(set(_values), key=_values.count)
        defaults[field] = most_frequent_value

    return defaults


def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--input_tsv', '-i', type=str, required=True,
                        help='Path to the input TSV file with ancestral state reconstruction results.'
                             ' Expects the first column to be the source siglum, the other columns '
                             ' to correspond to positions in the aligned melodies.')
    parser.add_argument('--output_csv', '-o', type=str, required=True,
                        help='Path to the output CSV file in CantusCorpus format. Make sure to name it'
                             ' in a way that makes it clear that it contains ancestral state information.'
                             ' This means that the dashes in the Volpiano are not the usual neume/syllable/word'
                             ' boundaries, but they record critical alignment information.')
    parser.add_argument('--cantus_id', '-c', type=str, required=True,
                        help='The Cantus ID to assign to the output chants.')
    parser.add_argument('--christmas_csv', type=str, required=True,
                        help='Path to the CSV file with Christmas chants. This file will be used to'
                             ' add the Christmas information to the output CSV file, via a combination'
                             ' of the siglum field and the provided --cantus_id')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def main(args):
    logging.info('Starting main...')
    _start_time = time.process_time()

    # Load input TSV
    with open(args.input_tsv, 'r', newline='') as fh:
        tsv_reader = csv.reader(fh, delimiter='\t')
        tsv = [row for row in tsv_reader]

    logging.info('Loaded input TSV, with {} items.'.format(len(tsv)))

    # Concatenate the melodies into a single string.
    ancstate_siglum_and_full_melody = [(row[0], ''.join([row[i] for i in range(1, len(row))])) for row in tsv]

    # Remove rows that have all-dash melodies (indicating that for this Cantus ID,
    # no melody existed in the given source).
    ancstate_siglum_and_full_melody = [row for row in ancstate_siglum_and_full_melody
                                       if row[1].strip() != '-' * (len(row[1].strip()))]

    print(ancstate_siglum_and_full_melody)

    # Load Christmas CSV
    with open(args.christmas_csv, 'r', newline='') as fh:
        christmas_reader = csv.DictReader(fh)
        christmas = [row for row in christmas_reader]

    logging.info('Loaded Christmas dataset, with {} items.'.format(len(christmas)))

    # Pair melodies from input TSV with a Christmas dataset chant
    # according to the siglum and --cantus_id.

    #  - Filter Christmas records that correspond to one of the input TSV melodies.

    #    Note that in the ancstate TSV, the sigla have underscores instead of spaces for technical
    #    reasons related to MrBayes. We need to replace those.
    ancstate_sigla_in_tsv = [row[0] for row in ancstate_siglum_and_full_melody]
    sigla_in_tsv = [normalize_ancstate_siglum(siglum) for siglum in ancstate_sigla_in_tsv]
    logging.debug('Sigla in TSV:\n{}\n'.format('\n'.join(sorted(sigla_in_tsv))))
    logging.debug('Sigla in Christmas:\n{}\n'.format('\n'.join(sorted(set([row['siglum'] for row in christmas])))))

    christmas_matched_chants = []
    for row in christmas:
        if row['cantus_id'] != args.cantus_id:
            continue
        christmas_siglum = row['siglum']
        # Matching sigla is problematic because they had to be changed for mrbayes processing to conform
        # to allowed species names. We already replaced underscores with spaces, but there are further
        # issues: removed dots, removed parentheses, etc. The matching will have to ignore these characters.
        siglum = normalize_christmas_siglum(christmas_siglum)
        # Now we can match the siglum.
        if siglum in sigla_in_tsv:
            christmas_matched_chants.append(row)

    logging.info('Matched {} Christmas records to the input TSV.'.format(len(christmas_matched_chants)))
    logging.debug('First matched Christmas record: {}'.format(christmas_matched_chants[0]))
    logging.info('Matched Christmas sigla: {}'.format([row['siglum'] for row in christmas_matched_chants]))

    #  - Change the melody of the matched Christmas records to the input TSV aligned melody.
    christmas_melody_field = 'volpiano'
    # print('Melody of first matched Christmas record: {}'.format(christmas_matched[0][christmas_melody_field]))
    _aligned_melodies_dict = {normalize_ancstate_siglum(siglum): melody for siglum, melody in ancstate_siglum_and_full_melody}
    logging.info('Aligned sigla: {}'.format(sorted(_aligned_melodies_dict.keys())))
    for row in christmas_matched_chants:
        christmas_siglum = row['siglum']
        siglum = normalize_christmas_siglum(christmas_siglum)
        if siglum in _aligned_melodies_dict:
            logging.debug('Replacing melody for siglum: {}'.format(siglum))
            row[christmas_melody_field] = _aligned_melodies_dict[siglum]
        else:
            logging.debug('Siglum {} not found in aligned melodies.'.format(normalize_christmas_siglum(siglum)))

    logging.debug('First matched Christmas record after melody replacement: {}'.format(christmas_matched_chants[0]))

    # Create sigla for internal nodes
    # Reformat internal node data as chant records.
    logging.debug('Matched Christmas rows:\n{}'.format('\n'.join(str([row['siglum'], row['cantus_id']]) for row in christmas_matched_chants)))
    _sigla_found_in_christmas = [normalize_christmas_siglum(row['siglum']) for row in christmas_matched_chants]
    unmatched_ancstate_sigla = [row[0] for row in ancstate_siglum_and_full_melody
                                if normalize_ancstate_siglum(row[0]) not in _sigla_found_in_christmas]
    print('Sigla in ancstate that have nonempty melodies and are not matched in Christmas: {}'.format(unmatched_ancstate_sigla))
    # Internal node sigla only consist of numbers.
    internal_node_ancstate_sigla = [siglum for siglum in unmatched_ancstate_sigla if siglum.isdigit()]
    print('Internal node sigla: {}'.format(internal_node_ancstate_sigla))

    internal_node_chants = []

    default_fields_dict = find_default_chant_fields_dict_for_internal_nodes(christmas_matched_chants)

    for siglum in internal_node_ancstate_sigla:
        chant = {'siglum': create_internal_node_siglum(siglum),
                 'cantus_id': args.cantus_id,
                 'volpiano': _aligned_melodies_dict[siglum],
                 'incipit': default_fields_dict['incipit'],
                 'genre_id': default_fields_dict['genre_id'],
                 'feast_id': default_fields_dict['feast_id'],
                 'office_id': default_fields_dict['office_id'],
                 'mode': default_fields_dict['mode'],
                 'full_text': default_fields_dict['full_text'],
                 }
        internal_node_chants.append(chant)

    # Write the output CSV.

    # Take CSV header from Christmas
    header = christmas[0].keys()
    print(header)

    # christmas_matched_chants contains the Christmas records with the melodies replaced.
    # internal_node_chants contains the chant records constructed for internal nodes.
    with open(args.output_csv, 'w') as fh:
        csv_writer = csv.DictWriter(fh, fieldnames=header)
        csv_writer.writeheader()
        for row in christmas_matched_chants:
            csv_writer.writerow(row)
        for row in internal_node_chants:
            csv_writer.writerow(row)

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
