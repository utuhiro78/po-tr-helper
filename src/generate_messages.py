#!/usr/bin/env python
# coding: utf-8

# Author: UTUMI Hirosi (utuhiro78 at yahoo dot co dot jp)
# License: Apache License, Version 2.0

import argparse
import re
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Generate messages suitable for auto-translation')

    parser.add_argument(
        'file', type=str,
        help='specify an original "*.po"')

    parser.add_argument(
        '-a', '--generate-all', action='store_true',
        help='generate all messages (default)')

    parser.add_argument(
        '-f', '--generate-fuzzy', action='store_true',
        help='generate fuzzy/untranslated messages')

    parser.add_argument(
        '-u', '--generate-untranslated', action='store_true',
        help='generate untranslated messages')

    parser.add_argument(
        '-m', '--max-characters', type=int,
        help='skip if the message has more characters than this')

    args = parser.parse_args()
    file_po = args.file
    generate_all = args.generate_all
    generate_fuzzy = args.generate_fuzzy
    generate_untranslated = args.generate_untranslated
    max_characters = args.max_characters

    if generate_fuzzy is False and generate_untranslated is False:
        generate_all = True

    if '.po' not in file_po or file_po[-7:] == '_tmp.po' or \
            file_po[-10:] == '_merged.po':
        print('Specify an original PO file.')
        sys.exit()

    with open(file_po, 'r', encoding='utf-8') as file:
        lines_po = re.split('\n\n', file.read())

    header = lines_po[0]
    c = header.find('nplurals=')
    nplurals = int(header[c + 9])

    lines_po = lines_po[1:]
    file_base = file_po[:-3]

    with open(f'{file_base}_tmp.po', 'w', encoding='utf-8') as file:
        file.write(header + '\n\n')

    with open(f'{file_base}_en.txt', 'w', encoding='utf-8') as file:
        file.write('')

    with open(f'{file_base}_tr.txt', 'w', encoding='utf-8') as file:
        file.write('')

    for i in range(len(lines_po)):
        po_block = lines_po[i].splitlines()
        po_block = combine_continued_messages(po_block)

        if generate_all is True or generate_fuzzy is True:
            po_block = remove_fuzzy(po_block)

        if generate_all is True:
            po_block = remove_translated(po_block)

        with open(f'{file_base}_tmp.po', 'a', encoding='utf-8') as file:
            file.write('\n'.join(po_block) + '\n\n')

        # Check if msgstr is blank
        if po_block[-1][-3:] != ' ""':
            continue

        po_num = str(i)
        en_messages = generate_en_messages(
            po_block, po_num, nplurals, max_characters)
        en_messages = fix_en_messages(en_messages)

        with open(f'{file_base}_en.txt', 'a', encoding='utf-8') as file:
            file.write('\n\n'.join(en_messages) + '\n\n')


def combine_continued_messages(po_block):
    po_block2 = []

    for i in range(len(po_block)):
        if re.match(r' *"', po_block[i]) is None:
            po_block2.append(po_block[i])
        else:
            c = po_block[i].find('"')
            po_block2[-1] = po_block2[-1][:-1] + po_block[i][(c + 1):]

    return po_block2


def remove_fuzzy(po_block):
    fuzzy = 0

    for i in range(len(po_block)):
        if po_block[i].find('#, fuzzy') == 0:
            po_block[i] = po_block[i].replace('#, fuzzy', '#', 1)
            fuzzy = 1
        elif fuzzy == 1 and po_block[i].find('msgstr') == 0:
            c = po_block[i].find('"')
            po_block[i] = po_block[i][:c] + '""'

    return po_block


def remove_translated(po_block):
    for i in range(len(po_block)):
        if po_block[i].find('#, fuzzy') == 0:
            break
        elif po_block[i].find('msgstr') == 0:
            c = po_block[i].find('"')
            po_block[i] = po_block[i][:c] + '""'

    return po_block


def generate_en_messages(po_block, po_num, nplurals, max_characters):
    en_messages = []
    p = 0

    for i in range(len(po_block)):
        if po_block[i][:7] == 'msgstr ':
            en_message = po_block[i - 1]
        elif po_block[i][:7] == 'msgstr[':
            en_message = po_block[i - nplurals]
        else:
            continue

        c = en_message.find('"')

        # AI may mistake "No. 1764" for "the year 1764",
        # so surround PO numbers with ">> <<".
        en_message = f'>>{po_num}:{str(p)}<< ' + en_message[(c + 1):-1]
        p += 1

        # Skip long msgid messages
        if max_characters is not None and \
                len(en_message) > max_characters:
            continue

        en_messages.append(en_message)

    return en_messages


def fix_en_messages(en_messages):
    for i in range(len(en_messages)):
        c = en_messages[i].find('<< ')
        po_num = en_messages[i][:(c + 3)]
        en_messages[i] = en_messages[i][(c + 3):]

        # Use "and" for better translation
        en_messages[i] = en_messages[i].replace(' && ', ' and ')

        # Change "&Edit" to "Edit"
        result = re.search(r'&[a-zA-Z]', en_messages[i])

        if result is None:
            # "G_FILENAME_ENCODING" is not a shortcut
            result = re.search(r'[A-Z]_[A-Z]', en_messages[i])

            if result is None:
                result = re.search(r'_[a-zA-Z]', en_messages[i])

        if result is not None:
            result = result.group()
            en_messages[i] = en_messages[i].replace(result, result[1])

        en_messages[i] = po_num + en_messages[i]

    return en_messages


if __name__ == "__main__":
    main()
