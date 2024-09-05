#!/usr/bin/env python
"""This is a script that takes the Solesmes probs tables and compiles a table
of Solesmes melody probabilities at the individual internal nodes."""

import argparse
import logging
import os
import pprint
import time

import csv


def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--input_tsv_folder', '-i', type=str, action='store',
                        help='Path to the folder with the Solesmes probs tables.')
    parser.add_argument('--ouptut_table', '-o', type=str, action='store',
                        help='Path to the output table with the compiled probabilities.')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def main(args):
    logging.info('Starting main...')
    _start_time = time.process_time()

    node_prob_tables = {}
    for file in os.listdir(args.input_tsv_folder):
        if not os.path.isfile(os.path.join(args.input_tsv_folder, file)):
            continue
        if not file.endswith('.tsv'):
            continue
        # Last part of the filename, delimited by underscores, is node name.
        node_name = file.split('_')[-1].split('.')[0]

        # Load the table
        with open(os.path.join(args.input_tsv_folder, file), 'r') as fh:
            data_reader = csv.DictReader(fh, delimiter=' ')
            data = [row for row in data_reader]
            node_prob_tables[node_name] = data

    logging.info('Loaded {} node probability tables.'.format(len(node_prob_tables)))
    # pprint.pprint(node_prob_tables)

    # Collect melody names.
    melodies = set()
    for node_name, node_table in node_prob_tables.items():
        for row in node_table:
            melodies.add(row['melody'])
    logging.info('Available melodies: {}'.format(sorted(melodies)))

    node_names = sorted(node_prob_tables.keys())
    logging.info('Available node names: {}'.format(sorted(node_names)))

    output_columns_names = ['melody'] + node_names
    output_table = [[] for _ in range(len(melodies))]
    for i, melody in enumerate(sorted(melodies)):
        output_table[i].append(melody)
        for node_name in node_names:
            for row in node_prob_tables[node_name]:
                if row['type'] != 'solesmes':
                    continue
                if row['melody'] == melody:
                    output_table[i].append(row['logprob'])
                    break
            else:
                output_table[i].append('nan')

    logging.info('Output table:')
    logging.info(output_columns_names)
    logging.info(pprint.pformat(output_table))
    logging.info('Row lengths: {}'.format([len(row) for row in output_table]))

    with open(args.ouptut_table, 'w', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(output_columns_names)
        for row in output_table:
            writer.writerow(row)

    # Draw a heatmap of the table.
    import seaborn as sns
    import numpy as np
    output_table_data = [[float(r) for r in row[1:]] for row in output_table]
    # As we have logprobs in the data table, we need to first exponentiate, then average,
    # and then logarithmize them back.
    average_row = [np.log(sum([np.exp(row[i]) for row in output_table_data]) / len(output_table_data))
                   for i in range(len(output_table_data[0]))]
    # We might be more interested, however, in the joint probability of observing
    # all the solesmes melodies there. Which, fortuantely, is just summing in the log space.
    joint_prob_row = [sum([row[i] for row in output_table_data])
                      for i in range(len(output_table_data[0]))]
    output_table_data_with_joint = output_table_data + [joint_prob_row]
    # print('Output table data shape: {} x {}'.format(len(output_table_data_with_joint), len(output_table_data_with_joint[0])))
    # print('Output data with joint:')
    # print(pprint.pformat(output_table_data_with_joint))
    _yticklabels = sorted(melodies) + ['joint prob.']
    heatmap = sns.heatmap(output_table_data_with_joint,
                          xticklabels=output_columns_names[1:],
                          yticklabels=_yticklabels,
                          cbar_kws={'label': 'Solesmes log probability', 'shrink': 0.5},
                          square=True
                          )
    # Y ticks should be oriented horizontally.
    heatmap.set_yticklabels(_yticklabels, rotation=0)
    heatmap.set_title('Solesmes melodies in relation to the inferred ancestral melodies')
    heatmap.get_figure().savefig(args.ouptut_table + '.png')

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
