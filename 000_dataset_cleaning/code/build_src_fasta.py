#!/usr/bin/env python
"""This is a script that processes the cleaned Christmas dataset from CantusCorpus CSV
into FASTA files that can then directly serve as inputs to MSA and subsequente phylogeny
building."""

import argparse
import logging
import os
import time

import csv

# These defaults are used for the ISMIR2023 and ISMIR2024 experiments.
DEFAULT_CANTUS_IDS = ['001737', '002000', '003511', '004195', '007040a', '605019']
DEFAULT_FASTA_NAMES = ['bethnon', 'cumesset', 'judjer1', 'orisic', 'consest', 'judjer2']
DEFAULT_SOURCE_SELECTION = ['A-VOR Cod. 259/I', 'A-Wn 1799**', 'CDN-Hsmu M2149.L4',
                            'CH-E 611', 'CZ-HKm II A 4', 'CZ-PLm 504 C 004',
                            'CZ-Pn XV A 10', 'CZ-Pu I D 20', 'CZ-Pu XVII E 1',
                            'D-KA Aug. LX', 'D-KNd 1161', 'F-Pn lat. 12044',
                            'F-Pn lat. 15181', 'NL-Uu 406']

def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--input_csv', '-i', action='store', required=True,
                        help='Input Christmas dataset cantuscorpus-style CSV. Should at this point'
                             ' contain melodies that are sufficiently cleaned so that they can directly'
                             ' be used in the FASTA files (the output of running clean_christmas.py).')
    parser.add_argument('--output_directory', action='store', required=True,
                        help='Outputs the FASTA files -- one for each specified Cantus ID.')
    parser.add_argument('--cantus_ids', action='store', nargs='+',
                        default=DEFAULT_CANTUS_IDS,
                        help='List of Cantus IDs for which to build the FASTA files.')
    parser.add_argument('--siglas', action='store', nargs='+',
                        default=DEFAULT_SOURCE_SELECTION,
                        help='Only use melodies from this selection of sources.')
    parser.add_argument('--fasta_names', action='store', nargs='+',
                        default=DEFAULT_FASTA_NAMES,
                        help='List of names for the files for the individual Cantus IDs. Must have'
                             ' the same length as the --cantus_ids array.')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def main(args):
    logging.info('Starting main...')
    _start_time = time.process_time()

    # Load the given CSV file.
    with open(args.input_csv, 'r', newline='') as fh:
        csv_reader = csv.DictReader(fh)
        christmas_csv = [row for row in csv_reader]

    siglum_melody_dicts_for_cids = dict()
    for cid in args.cantus_ids:
        siglum_melody_dicts_for_cids[cid] = dict()

    for row in christmas_csv:
        siglum = row['siglum']
        melody = row['volpiano']
        cid = row['cantus_id']
        if cid in siglum_melody_dicts_for_cids:
            _melody_dict = siglum_melody_dicts_for_cids[cid]
            # Have to keep only the longest melody for the given CID from each source.
            if siglum not in _melody_dict:
                _melody_dict[siglum] = []
            _melody_dict[siglum].append(melody)
            # else:
            #     _best_length = len(_melody_dict[siglum])
            #     _current_length = len(melody)
            #     if _current_length > _best_length:
            #         _melody_dict[siglum] = melody

    if not os.path.isdir(args.output_directory):
        logging.warning('Output directory does not exist. Creating: {}'.format(args.output_directory))
        os.makedirs(args.output_directory)

    cid_to_fasta_name_dict = {cid: name for cid, name in zip(args.cantus_ids, args.fasta_names)}
    for cid in siglum_melody_dicts_for_cids.keys():
        output_basename = cid_to_fasta_name_dict[cid] + '_src.fasta'
        output_file = os.path.join(args.output_directory, output_basename)
        with open(output_file, 'w') as output_fh:
            current_cid_melody_dict = siglum_melody_dicts_for_cids[cid]
            for siglum, melodies in sorted(current_cid_melody_dict.items()):
                for melody in melodies:
                    output_fh.write('> {}\n'.format(siglum))
                    output_fh.write('{}\n'.format(melody))

    _end_time = time.process_time()
    logging.info('build_src_fasta.py done in {0:.3f} s'.format(_end_time - _start_time))


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main(args)
