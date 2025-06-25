"""
Halt! What's the Passphrase?
Passphrase generator module.
"""

# Standard library imports
import os
import re
import random
import secrets
import requests
import string
from typing import List

# Local application imports
import entropy
import color
from pathlib import Path
from pp_utils import (
    CACHE_DIR,
    json_read as jr,  # JSON Read
    list_available_dictionaries,
    dictionary_exists,
)

def safe_capitalize(word: str) -> str:
    """Capitalize first ASCII alphabetic character, if present."""
    return (word[0].upper() + word[1:]) if word[:1].isalpha() and word[:1].isascii() else word

class passphrase:
    def __init__(self, verbose: bool = False, colorize: bool = False,
                 dictionary: str | None = None,
                 start_n: int | None = None,
                 end_n: int | None = None):
        self.verbose = verbose
        self.color = colorize
        self.default_dictionary = "eff_large_wordlist"
        self.dictionary = dictionary or self.default_dictionary
        self.start_n = start_n
        self.end_n = end_n

        self.data_file = CACHE_DIR / f"{self.dictionary}_data.json"

        if not dictionary_exists(self.dictionary):
            print(f"[ERROR] Required dictionary files for '{self.dictionary}' not found.")
            list_available_dictionaries()
            exit(1)

        # instantiate crypto‐secure RNG
        self._crypto = secrets.SystemRandom()
        

        # WORDLENGTH AND PARTITIONS DICTS
        data = jr(self.data_file.name, convert_keys=False)
        self.wordlength_dict = {int(k): v for k, v in data.get("wordlength", {}).items()}
        self.partitions_dict = {int(k): v for k, v in data.get("partitions", {}).items()}
        self.min_word_length = data.get("min_word_length")
        self.max_word_length = data.get("max_word_length")
        if self.min_word_length is None or self.max_word_length is None:
            self.min_word_length = min(self.wordlength_dict)
            self.max_word_length = max(self.wordlength_dict)
        if self.verbose:
            print(f"Imported passphrase data: {self.data_file}")
            # 1. Pull out the keys and convert to int
            keys = list(map(int, self.wordlength_dict.keys()))

            # 2. Sort them
            keys.sort()

            # 3. Join into a comma-separated string
            out = ", ".join(str(k) for k in keys)
            print(f"  Possible word lengths found from {len(self.wordlength_dict)} : {out}")

        # START/END RANGES
        self.start_n = self.start_n if self.start_n is not None else self.min_word_length * 2
        self.end_n = self.end_n if self.end_n is not None else self.max_word_length * 5
        if self.verbose:
            print(f"  Possible partition keys found: {len(self.partitions_dict)}")
            keys = list(map(int, self.partitions_dict.keys()))
            print(f"  Available partition keys: {keys}")
        
        # COLOR and ENTROPY OBJECTS
        self.c = color.Color()
        self.e = entropy.Entropy()

    def get_passphrase(self, num_chars=20, num_reps=1, num_words=False, verbose=False, augenbaumize=False, pad=False):
        # ERROR CHECKING FOR INPUTS
        if not isinstance(num_chars, int):
            print(f"Invalid type for num_chars: {num_chars}. Must be an integer between 10 and 100.")
            exit(1)
        if num_chars < 10 or num_chars > 100:
            print(f"Invalid number of passphrase chars entered: {num_chars}. Must be between 10 and 100.")
            exit(1)
        if num_words is not False and not isinstance(num_words, int):
            print(f"Invalid type for num_words: {num_words}. Must be an integer.")
            exit(1)

        self.num_chars = num_chars
        self.num_reps = num_reps
        self.num_words = num_words
        self.verbose = verbose
        self.augenbaumize = augenbaumize
        self.pad = pad

        # GENERATE PASSPHRASE LIST
        return self.generate_passphrase_list()

    def generate_passphrase_list(self):
        result = []
        for _ in range(self.num_reps):
            # Determine frame based on fixed words or character count
            if self.num_words is not False:
                # FIXED NUMBER OF WORDS
                frame = [w.capitalize() for w in self.get_random_words_from_list(self.num_words)]
            else:
                # FIXED NUMBER OF CHARACTERS
                partitions = self.partitions_dict[self.num_chars]
                rand_part = self._crypto.choice(partitions)
                self._crypto.shuffle(rand_part)

                frame = []
                used = set()
                for length in rand_part:
                    word = self.get_random_word_of_length(length)
                    while word in used:
                        word = self.get_random_word_of_length(length)
                    used.add(word)
                    frame.append(word)

            # PAD
            if self.pad:
                pad_str, pad_pos = self.pad
                if pad_pos == 1:
                    frame.insert(0, pad_str)
                elif pad_pos == 2:
                    mid = len(frame) // 2
                    frame.insert(mid, pad_str)
                elif pad_pos == 3:
                    frame.append(pad_str)

            # AUGENBAUMIZE
            if self.augenbaumize:
                aug = self.augenbaumize
                frame = [aug] + frame + [aug[::-1]]

            # BUILD PASSPHRASE
            phrase = ''.join(frame)
            
            # COLORIZE
            if self.color:
                phrase = self.colorize_passphrase(phrase)
            
            result.append(phrase)

        return result

    def get_random_word_of_length(self, length):
        return safe_capitalize(self._crypto.choice(self.wordlength_dict[length]))

    def colorize_passphrase(self, text):
        colored = ''
        for ch in text:
            if ch.isalpha():
                colored += self.c.p(ch, 'red' if ch.isupper() else 'blue')
            elif ch.isnumeric():
                colored += self.c.p(ch, 'green')
            else:
                colored += self.c.p(ch, 'magenta')
        colored += self.c.p('')
        return colored

    def generate_passphrase_wikipedia(self, num_titles=3, num_reps=1, colorize=False, augenbaumize=False, verbose=False):
        session = requests.Session()
        url = "https://en.wikipedia.org/w/api.php"
        params = {"action":"query","format":"json","list":"random","rnnamespace":"0","rnlimit":str(num_titles*num_reps)}
        titles = [item['title'] for item in session.get(url=url, params=params).json()["query"]["random"]]
        chunks = list(self.chunker(titles, num_titles))
        if self.verbose:
            for chunk in chunks:
                print(f"TITLE : {chunk}")
        pp_frame = [self.de_wikify(' '.join(chunk)) for chunk in chunks]

        if augenbaumize:
            pp_frame = [augenbaumize + w + augenbaumize[::-1] for w in pp_frame]
        if colorize:
            pp_frame = [self.colorize_passphrase(w) for w in pp_frame]

        return pp_frame

    def chunker(self, seq, size):
        return (seq[i:i+size] for i in range(0, len(seq), size))

    def de_wikify(self, text):
        if self.verbose:
            print(f"START : {text}")
        text = re.sub(r"[\(\[].*?[\)\]]", "", text).strip()
        text = text.replace('-', ' ')
        words = text.split()
        cleaned = ''
        for word in words:
            for idx, ch in enumerate(word):
                if ch.isalnum():
                    cleaned += ch.upper() if idx == 0 else ch
        if self.verbose:
            print(f"CLEAN : {cleaned}")
        return cleaned
    
    def get_random_words_from_list(self, num_words: int) -> List[str]:
        """
        Return *num_words* random words without duplicates, using self.wordlength_dict
        """
        pool = [w for sub in self.wordlength_dict.values() for w in sub]
        if num_words > len(pool):
            print(f"Requested {num_words} words, but only {len(pool)} available.")
            exit(1)
        chosen = set()
        result = []
        while len(result) < num_words:
            w = self._crypto.choice(pool)
            if w not in chosen:
                chosen.add(w)
                result.append(safe_capitalize(w))
        return result
