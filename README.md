## Overview

"po-tr-helper" is an auto-translation helper for PO files.

It is suitable for making translation drafts.

Note: Some translations might cause errors. You need to fix them manually.

## License

Apache License, Version 2.0

## Usage

### 1. Generate messages suitable for auto-translation

```
cd src/
# Change '/ja/' to your locale.
# https://websvn.kde.org/branches/stable/l10n-kf6/
wget https://websvn.kde.org/branches/stable/l10n-kf6/ja/messages/dolphin/dolphin.po?view=co -O dolphin.po

python generate_messages.py dolphin.po
```

It generates these files.

```dolphin_en.txt``` English messages to translate.

```dolphin_tmp.po``` A temporary file to merge translations.

```dolphin_tr.txt``` Paste translations to this file.

### 2. Translate messages with Chromium Translate

Drop "dolphin_en.txt" to Chromium. Right-click and select "Translate to".

Wait a second and scroll down the page to check if the translation is complete.

Press "Ctrl+A"  to select all translations. Right-click and select "Copy".

Paste them to "dolphin_tr.txt".

- [Google Translate](https://translate.google.com/) generates better translation, but is limited up to 5000 characters at once.

- ChatGPT or DeepL might generate better translation, but I am not a registered user.

### 3. Merge translations to a PO file

```
python merge_translations.py dolphin_tr.txt
```

Open "dolphin_merged.po" with poedit. Check for any errors.

## Options

```generate_messages.py file.po``` Generate all messages (default).

```generate_messages.py -f file.po``` Generate fuzzy/untranslated messages.

```generate_messages.py -u file.po``` Generate untranslated messages.

```merge_translations.py file_tr.txt``` Mark translations as "translated" (default).

```merge_translations.py -f file_tr.txt``` Mark translations as "fuzzy".
