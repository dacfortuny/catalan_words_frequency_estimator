# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

#

# +
import copy
import ebooklib
import glob
import pandas as pd
import re
import string
import warnings

from bs4 import BeautifulSoup
from ebooklib import epub
from tqdm import tqdm
# -

warnings.filterwarnings("ignore")

# # Settings

EPUBS_PATH = "data/epub/*.epub"
WORDS_FILE = "data/Paraules.cat"
OUTPUT_FILE = "data/Paraules_recompte.cat"


# # Functions

# +
def find_non_alphanumeric_characters(text):
    nonalnum = []
    for character in text:
        if character != " ":
            if not character.isalnum():
                nonalnum.append(character)
    return set(nonalnum)

def extract_full_text(file_name):
    book = epub.read_epub(file_name)
    items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    texts = []
    for item in items:
        soup = BeautifulSoup(item.get_body_content(), "html.parser")
        text = [para.get_text() for para in soup.find_all("p")]
        texts.append(" ".join(text))
    return " ".join(texts)

def sanitize_gemination_lowercase(text_lower):
    wrong_geminations = ["l.l", "l•l", "l∙l", "l-l", "ŀl"]
    for case in wrong_geminations:
        text_lower = re.sub(case, "l·l", text_lower)
    return text_lower

def separate_special_characters(text):
    separation_characters = ["\n", "￼", "︎",
                             "-", "―", "—", "–", "−", "¯", "⁻",
                             "'", "’", "‘", "´", "́", "̀", "′"]
    for case in separation_characters:
        text = re.sub(case, " ", text) 
    return text

def remove_punctuation(text):
    return ''.join(x for x in text if (x.isalpha() or x == "·" or x == " "))

def sanitize_white_spaces(text):
    return re.sub(" +", " ", text.strip())

def extract_dictionary_counts(text):
    return dict(pd.Series(text.split(" ")).value_counts())


# -

# # Count words

# ## Read files

# ### Epub files
# Based on ["Getting Text from epub Files in Python" by Andrew Muller](https://andrew-muller.medium.com/getting-text-from-epub-files-in-python-fbfe5df5c2da)

files = glob.glob(EPUBS_PATH)

# ### Words list

words = pd.read_csv(WORDS_FILE, sep=";", names = ["word", "word_root", "types", "type_1",
                                                  "type_2", "type_3", "type_4", "type_5",
                                                  "type_6", "type_7", "word_sanitized"]).fillna("")
words.head()

# ## Word counts

counts_all = []
for file in tqdm(files):
    try:
        text = extract_full_text(file)
        text = text.lower()
        text = sanitize_gemination_lowercase(text)
        text = separate_special_characters(text) 
        text = remove_punctuation(text)
        text = sanitize_white_spaces(text)
        counts_text = extract_dictionary_counts(text)
        counts_df = pd.DataFrame.from_dict(counts_text, orient="index").reset_index()
        counts_df = counts_df.rename(columns={"index": "word", 0: "counts"})
        counts_all.append(counts_df)
    except TypeError:
        print(f"Error reading file {file}")
        continue
counts_all = pd.concat(counts_all)

counts_all = counts_all.groupby("word", as_index=False).sum()
counts_all = counts_all.sort_values("counts", ascending=False).reset_index(drop=True)
counts_all.to_csv("data/tmp_counts.csv", sep=";", index=False, header=False)
counts_all.head()

words_counts = words.merge(counts_all, how="left", on="word").fillna(0)
words_counts["counts"] = words_counts["counts"].astype(int)
words_counts.head()

# ## Count words with same root

counts_root_df = words_counts[["word", "word_root", "counts"]].drop_duplicates().reset_index(drop=True)
counts_root_df = counts_root_df.groupby("word_root", as_index=False)["counts"].sum()
counts_root_df = counts_root_df.rename(columns={"counts": "counts_root"})
counts_root_df.head()

words_counts = words_counts.merge(counts_root_df, how="left", on="word_root").fillna(0)
words_counts["counts_root"] = words_counts["counts_root"].astype(int)
words_counts.head()

# # Export result

words_counts.to_csv(OUTPUT_FILE, sep=";", index=False, header=False)
