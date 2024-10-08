#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import argparse
import re
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Merge translations to a PO file')

    parser.add_argument(
        'file', type=str,
        help='specify "*_tr.txt"')

    parser.add_argument(
        '-f', '--mark-as-fuzzy', action='store_true',
        help='mark translations as "fuzzy"')

    parser.add_argument(
        '-t', '--mark-as-translated', action='store_true',
        help='mark translations as "translated" (default)')

    args = parser.parse_args()
    file_tr = args.file
    mark_as_fuzzy = args.mark_as_fuzzy

    if file_tr.split('_')[-1] != 'tr.txt':
        print('specify "*_tr.txt"')
        sys.exit()

    with open(file_tr, 'r', encoding='utf-8') as file:
        lines_tr = file.read().splitlines()

    file_base = file_tr.split('_tr.txt')[0]
    file_po = f'{file_base}_tmp.po'

    with open(file_po, 'r', encoding='utf-8') as file:
        lines_po = re.split('\n\n', file.read())

    header = lines_po[0]
    lines_po = lines_po[1:]

    with open(f'{file_base}_merged.po', 'w', encoding='utf-8') as file:
        file.write(header + '\n\n')

    for i in range(len(lines_tr)):
        line_tr = lines_tr[i]

        # Skip lines that don't start with ">>number<<"
        if re.match(r'>>\d+:\d<<..', line_tr) is None:
            continue

        # For debug
        print(f'merge translation {line_tr}')

        line_tr = fix_po_num(line_tr)

        # line_tr = '>>20:0<< Create New'
        c = line_tr.find(':')
        po_num = int(line_tr[2:c])
        po_num_sub = int(line_tr[(c + 1)])
        line_tr = line_tr[(c + 5):]

        # Locale specific fixes
        line_tr = fix_japanese(line_tr)

        po_block = lines_po[po_num].splitlines()
        line_tr = change_end_of_line(line_tr, po_block)
        line_tr = add_shortcut(line_tr, po_block)
        lines_po[po_num] = merge_translation(
            line_tr, po_block, po_num_sub, mark_as_fuzzy)

    with open(f'{file_base}_merged.po', 'a', encoding='utf-8') as file:
        file.write('\n\n'.join(lines_po))


def fix_po_num(line_tr):
    # Remove Zero Width Space
    line_tr = line_tr.replace('\u200b', '')

    # Change ">>117:0<<Save" to ">>117:0<< Save"
    if re.match(r'>>\d+:\d<< ', line_tr) is None:
        result = re.match(r'>>\d+:\d<<', line_tr)
        result = result.group()
        line_tr = line_tr.replace(result, f'{result} ', 1)

    return line_tr


def fix_japanese(line_tr):
    results = re.findall(r'[ァ-ヿー] [ァ-ヿ]', line_tr)

    if results != []:
        for result in results:
            # Change "ステータス バー" to "ステータスバー"
            line_tr = line_tr.replace(result, result.replace(' ', ''))

    return line_tr


def change_end_of_line(line_tr, po_block):
    for i in range(len(po_block)):
        if po_block[i].find('msgid') != 0:
            continue

        c = po_block[i].find('"')
        po_line = po_block[i][(c + 1):-1]

        # If msgid starts with a space, add a space to msgstr
        if po_line.find(' ') == 0:
            line_tr = ' ' + line_tr

        if po_line[-1] == ' ' and line_tr[-1] != ' ':
            line_tr += ' '
        elif po_line[-1] != ' ' and line_tr[-1] == ' ':
            line_tr = line_tr[:-1]
        elif po_line[-1] != '.' and line_tr[-1] in ['.', '。']:
            line_tr = line_tr[:-1]

    return line_tr


def add_shortcut(line_tr, po_block):
    for i in range(len(po_block)):
        if po_block[i].find('msgid') != 0:
            continue

        # "msgid_plural" is not a shortcut
        c = po_block[i].find('"')
        po_line = po_block[i][(c + 1):-1]

        # Add a shortcut key to translation (&E)
        result = re.search(r'&[a-zA-Z]', po_line)

        if result is None:
            # "G_FILENAME_ENCODING" is not a shortcut
            result = re.search(r'[A-Z]_[A-Z]', po_line)

            if result is None:
                result = re.search(r'_[a-zA-Z]', po_line)

        if result is not None:
            result = f'({result.group().upper()})'

            if po_line[-3:] == '...':
                line_tr = f'{line_tr[:-3]}{result}...'
            elif po_line[-1] in ['…', ':']:
                line_tr = f'{line_tr[:-1]}{result}{po_line[-1]}'
            else:
                line_tr = f'{line_tr}{result}'

    return line_tr


def merge_translation(
        line_tr, po_block, po_num_sub, mark_as_fuzzy):
    for i in range(len(po_block)):
        if po_num_sub == 0 and po_block[i].find('msgstr ') == 0:
            c = po_block[i].find('"')
            po_block[i] = f'{po_block[i][:c]}"{line_tr}"'
            break
        elif po_block[i].find(f'msgstr[{po_num_sub}]') == 0:
            c = po_block[i].find('"')
            po_block[i] = f'{po_block[i][:c]}"{line_tr}"'

    if mark_as_fuzzy is True:
        for i in range(len(po_block)):
            if po_block[i].find('#, fuzzy') == 0:
                break
            elif po_block[i].find('#, ') == 0:
                po_block[i] = po_block[i].replace('#, ', '#, fuzzy, ')
                break
            elif po_block[i][0] != '#':
                po_block.insert(i, '#, fuzzy')
                break

    po_block = '\n'.join(po_block)
    return po_block


if __name__ == "__main__":
    main()
