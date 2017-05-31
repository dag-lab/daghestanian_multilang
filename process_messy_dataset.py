#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
import sys
import csv
import os
import codecs
import argparse


def get_value(cell, fail=0, bool_=False):
    try:
        return int(cell)
    except ValueError:
        if bool_:
            if cell.strip() in {'+', 'да', '1', 'yes'}:
                return 1
            elif cell.strip():
                return 0
        return fail


non_langs = {
    'name', 'female', 'year_of_birth',
    'close_multiling_list', 'personal', 'village'
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('mapping')
    args = parser.parse_args()

    mapping = {}
    with codecs.open(args.mapping, 'r', 'utf8') as f:
        for line in f:
            tabs = line.strip().split('\t')
            if len(tabs) < 2:
                continue
            mapping[tabs[0]] = tabs[1]

    results = []
    firstline = None
    notinmapping = set()
    with codecs.open(args.filename, 'r', 'utf8') as f:
        for line in csv.reader(f, delimiter=';'):
            if not firstline:
                firstline = list(line)
                continue
            result = {}
            sp = list(line)
            if len(sp) < len(firstline):
                continue
            for i, col in enumerate(firstline):
                if col == 'female':
                    result[col] = 1 if sp[i] == 'ж' else 0
                elif col == 'village':
                    clean = sp[i].strip().lower()
                    try:
                        result[col] = mapping[clean]
                    except KeyError:
                        notinmapping.add(clean)
                        result[col] = clean
                    # result[col] = clean
                elif col == 'знание':
                    result[firstline[i - 1]] = get_value(sp[i])
                elif col == 'учет':
                    if get_value(sp[i]) == 0:
                        result[firstline[i - 2]] = 0
                elif col == 'personal':
                    result[col] = get_value(sp[i], fail=2, bool_=True)
                elif col == 'year_of_birth':
                    result[col] = get_value(sp[i])
                elif col == 'close_multiling_list':
                    clean = sp[i].strip().replace(' ', '')
                    result['close_multiling_list'] = clean
                    close_langs = set(clean.split(','))
                    known_langs = {
                        x for x in (set(result) - non_langs) if result[x]
                    }
                    result['multiling'] = len(known_langs)
                    result['multiling_without_rus'] = len(
                        known_langs - {'rus'}
                    )
                    result['close_multiling'] = len(
                        (known_langs - {'rus'}) & close_langs
                    )
                    result['far_multiling'] = len(
                        known_langs - {'rus'} - close_langs
                    )
                    result['far_multiling_list'] = ','.join(
                        sorted(known_langs - {'rus'} - close_langs)
                    )
                else:
                    result[col] = sp[i]
            results.append(result)
    print('\n'.join(sorted(notinmapping)))

    good_headers = [x for x in firstline if x in results[0]] + [
        'multiling', 'multiling_without_rus',
        'close_multiling', 'far_multiling', 'far_multiling_list'
    ]

    bn, ext = os.path.splitext(args.filename)

    with codecs.open('{}-out.csv'.format(bn), 'w', 'utf8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(
            [good_headers] + [
                [res[x] for x in good_headers] for res in results
            ]
        )


if __name__ == "__main__":
    main()
