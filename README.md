# Catalan words frequency estimator

This code is used to calculate the relative frequency between different Catalan words in common texts. It can be used
for any other language.

## Set up

### Input files

- `data/Paraules.cat` CSV with the list of words for which the frequency is calculated.
    - Column 1: Word
    - Column 2: Root word
    - Columns 3-10: Properties of the word
    - Column 11: Sanitized word
    - Separator: ";"
- `data/epub/` Folder with books in epub format used for estimating word frequencies.

## Calculation

The notebook [./count_words.py](./count_words.py) reads the input files and returns a file with the calculated
frequencies.

## Output

- `data/Paraules_recompte.cat` CSV file consisting on the original list of words with two extra columns:
  - Column 12: Counts of the word in the epub files
  - Column 13: Counts of all the words with the same root.