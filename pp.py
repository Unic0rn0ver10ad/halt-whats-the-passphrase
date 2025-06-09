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
from pp_utils import json_read as jr, file_generic_read as tr  # JSON Read, Text Read
from pp_utils import generate_wordlist_from_dictionary as gwfd

class passphrase:
    def __init__(self, verbose=False, colorize=False):
        # instantiate crypto‐secure RNG
        self._crypto = secrets.SystemRandom()
        
        self.verbose = verbose
        self.color = colorize
        self.dn = "eff_large_wordlist"  # Dictionary Name is hardcoded here
        self.dn = "hwtp_short_test_3"  # Dictionary Name is hardcoded here
        self.wordlist_file = self.dn + "_filtered.txt"
        self.wordlength_file = self.dn + "_wordlength.json"
        self.partitions_file = self.dn + "_partitions.json"
        self.min_word_length = 4  # hardcoded
        self.max_word_length = 9  # hardcoded

        # WORDLIST
        self.wordlist = gwfd(self.wordlist_file, cache=True)
        self.wordlist_length = len(self.wordlist)
        if self.verbose:
            print(f"Got wordlist: {self.wordlist_file}")
            print(f"  {self.wordlist_length} words in {self.wordlist_file}")

        # WORDLENGTH DICT
        self.wordlength_dict = jr(self.wordlength_file)
        if self.verbose:
            print(f"Imported wordlength dictionary: {self.wordlength_file}")
            # 1. Pull out the keys and convert to int
            keys = list(map(int, self.wordlength_dict.keys()))

            # 2. Sort them
            keys.sort()

            # 3. Join into a comma-separated string
            out = ", ".join(str(k) for k in keys)
            print(f"  Possible word lengths found from {len(self.wordlength_dict)} : {out}")

        # PARTITIONS DICT
        self.partitions_dict = jr(self.partitions_file)
        if self.verbose:
            print(f"Imported partitions dictionary from: {self.partitions_file}")
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
        return self._crypto.choice(self.wordlength_dict[length]).capitalize()

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
                result.append(w.capitalize())
        return result
