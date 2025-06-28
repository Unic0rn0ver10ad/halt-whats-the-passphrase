"""
Halt! What's the Passphrase?
Passphrase utilities.
"""

# Standard library imports
import time
import json
from pathlib import Path
from functools import lru_cache
from collections import defaultdict
from typing import Union, List, Dict

# Base directory for locating wordlists and cache regardless of where the
# script is executed from
BASE_DIR = Path(__file__).resolve().parent

# Constants for directory paths, resolved relative to this file's location
DICTIONARY_DIR = BASE_DIR / 'wordlists'
CACHE_DIR = BASE_DIR / 'cache'

# --------------------------
# File Handling Utilities
# --------------------------
def file_generic_read(path_to_file: Path) -> Union[str, bool]:
    try:
        with path_to_file.open("r", encoding="utf-8") as my_file:
            return my_file.read()
    except Exception as error:
        print(f"Couldn't read file: {path_to_file} Error: {error}")
        return False

def file_generic_write(path_to_file: Path, data_to_save: str) -> bool:
    try:
        with path_to_file.open("w", encoding="utf-8") as my_file:
            my_file.write(str(data_to_save))
        return True
    except Exception as error:
        print(f"Failed to save file: {path_to_file} Error: {error}")
        return False

def json_write(path: Path, data: Union[dict, list]) -> bool:
    try:
        with path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))  # compact JSON
        return True
    except Exception as e:
        print(f"[ERROR] Failed to write JSON file: {path}. Error: {e}")
        return False

def json_read(filename: str, convert_keys: bool = True) -> Union[dict, list, bool]:
    """
    Read JSON data from a file in the cache directory.
    `filename` should be the name of the JSON file (with extension).
    If convert_keys is True and the root JSON object is a dict, convert its keys from strings to ints.
    """
    path = CACHE_DIR / filename
    try:
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        if convert_keys and isinstance(data, dict):
            try:
                return {int(k): v for k, v in data.items()}
            except ValueError as e:
                print(f"[ERROR] Converting keys to int failed for {path}: {e}")
                return data
        return data
    except Exception as e:
        print(f"[ERROR] Failed to read JSON file: {path}. Error: {e}")
        return False

# --------------------------
# Partition Generation
# --------------------------
def create_partitions(
    partition_path: Path | None = None,
    start_n: int = 10,
    end_n: int = 50,
    min_val: int = 4,
    max_val: int = 9,
    verbose: bool = False,
) -> Dict[int, List[List[int]]]:
    """Generate partitions and optionally write them to ``partition_path``."""
    start_time = time.time()
    partitions_dict: Dict[int, List[List[int]]] = {}

    for n in range(start_n, end_n + 1):
        partition_start_time = time.time()
        partitions = generate_partitions_for_n(n, min_val, max_val)
        time_taken = time.time() - partition_start_time

        if verbose:
            print(
                f"N = {n}, Total Partitions = {len(partitions)}, "
                f"Time taken = {time_taken:.2f} seconds"
            )
        partitions_dict[n] = partitions

    total_time = time.time() - start_time
    if partition_path is not None:
        json_write(partition_path, partitions_dict)
        print(
            "Partition generation completed. Time: "
            f"{total_time:.2f} seconds. Results written to {partition_path}."
        )
    else:
        print(f"Partition generation completed. Time: {total_time:.2f} seconds.")

    return partitions_dict

@lru_cache(maxsize=None)
def generate_partitions_for_n(n: int, min_val: int, max_val: int) -> List[List[int]]:
    if n < min_val:
        return []

    partitions = set()
    if min_val <= n <= max_val:
        partitions.add((n,))

    for i in range(min_val, min(max_val, n) + 1):
        remaining = n - i
        if remaining >= min_val:
            for sub_partition in generate_partitions_for_n(remaining, min_val, max_val):
                partitions.add(tuple(sorted((i,) + tuple(sub_partition))))

    return [list(partition) for partition in partitions]

# --------------------------
# Dictionary Utilities
# --------------------------
def process_all_dictionaries(min_word_length: int = 4,
                             max_word_length: int = 9,
                             start_n: int | None = None,
                             end_n: int | None = None,
                             min_chars: int | None = None,
                             language: str | None = None,
                             include_partitions: bool = True,
                             verbose: bool = False) -> None:
    """
    Process every dictionary file in the wordlists directory.
    Automatically detects whether the file is a dicelist based on the first line format.
    ``include_partitions`` determines whether partition data is generated and
    stored in the resulting JSON files.
    """
    if min_chars is None:
        print("[ERROR] --min-chars is required when processing dictionaries.")
        return

    for dictionary_path in DICTIONARY_DIR.glob("*.txt"):
        # validate script goes here
        # throw error messages if inputs are out of range
        try:
            with dictionary_path.open("r", encoding="utf-8") as file:
                first_line = file.readline().strip()
                is_dicelist = bool(
                    first_line and
                    '\t' in first_line and
                    first_line.split('\t')[0].isdigit() and
                    first_line.split('\t')[1].isalpha()
                )
            print(f"{dictionary_path.name} is a Dicelist: {str(is_dicelist).upper()}")
            process_raw_dictionary(
                raw_dictionary_filename=dictionary_path.name,
                min_word_length=min_word_length,
                max_word_length=max_word_length,
                start_n=start_n,
                end_n=end_n,
                is_dicelist=is_dicelist,
                language=language or dictionary_path.stem,
                include_partitions=include_partitions,
                min_chars=min_chars,
                verbose=verbose
            )
        except Exception as e:
            print(f"[ERROR] Failed to process {dictionary_path.name}: {e}")

def process_raw_dictionary(raw_dictionary_filename: str,
                           min_word_length: int = 4,
                           max_word_length: int = 9,
                           start_n: int | None = None,
                           end_n: int | None = None,
                           is_dicelist: bool | None = None,
                           language: str | None = None,
                           min_chars: int | None = None,
                           include_partitions: bool = True,
                           verbose: bool = False) -> bool:

    print(f"Processing {raw_dictionary_filename}")
    if min_chars is None:
        print("[ERROR] --min-chars is required when processing dictionaries.")
        return False
    try:
        stem = Path(raw_dictionary_filename).stem
        lang_name = language or "Unknown"

        if is_dicelist is None:
            try:
                with (DICTIONARY_DIR / raw_dictionary_filename).open("r", encoding="utf-8") as file:
                    first_line = file.readline().strip()
                    is_dicelist = bool(
                        first_line and "\t" in first_line and first_line.split("\t")[0].isdigit()
                    )
            except Exception:
                is_dicelist = False

        wordlist = (
            convert_dicelist_to_dictionary(raw_dictionary_filename)
            if is_dicelist else
            generate_wordlist_from_dictionary(raw_dictionary_filename)
        )
        original_length = len(wordlist) if wordlist else 0
        wordlist = filter_word_list(
            wordlist,
            min_word_length,
            max_word_length,
            verbose=verbose,
        )
        rejected_count = original_length - len(wordlist) if wordlist else original_length
        if verbose:
            print(
            f"Rejected {rejected_count} words from Wordlist {raw_dictionary_filename}"
            )
        if not wordlist:
            print(f"No valid words found in {raw_dictionary_filename}")
            return False

        wordlength_dict = generate_wordlength_dict(wordlist)

        # validate wordlength_dict
        actual_lengths = sorted(wordlength_dict)
        if not actual_lengths:
            print(f"[ERROR] No words remain after filtering {raw_dictionary_filename}")
            return False

        missing_lengths = [
            n for n in range(min_word_length, max_word_length + 1)
            if n not in wordlength_dict
        ]

        if missing_lengths:
            rec_min = actual_lengths[0]
            rec_max = actual_lengths[-1]
            missing_str = ', '.join(str(n) for n in missing_lengths)
            print(
                "[ERROR] The selected word length range does not match the "
                f"dictionary contents. Missing lengths: {missing_str}."
            )
            print(f"Try --min-word-length {rec_min} --max-word-length {rec_max}")
            return False

        sn = start_n if start_n is not None else min_word_length * 2
        en = end_n if end_n is not None else max_word_length * 5

        partitions_dict = {}
        if include_partitions:
            partitions_dict = create_partitions(
                partition_path=None,
                start_n=sn,
                end_n=en,
                min_val=min_word_length,
                max_val=max_word_length,
                verbose=verbose,
            )

        data = {
            "metadata": {
                "language": lang_name,
                "has_partitions": bool(partitions_dict),
                "min_word_length": min_word_length,
                "max_word_length": max_word_length,
                "min_chars": min_chars,
            },
            "wordlengths": {str(k): v for k, v in wordlength_dict.items()},
        }
        if partitions_dict:
            data["partitions"] = {str(k): v for k, v in partitions_dict.items()}

        data_path = CACHE_DIR / f"{stem}_data.json"
        if not json_write(data_path, data):
            raise RuntimeError("Failed to write dictionary data.")

        print(f"Processing of {raw_dictionary_filename} completed successfully.")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def generate_wordlist_from_dictionary(dictionary_name_in: str, cache: bool = False) -> Union[List[str], bool]:
    """
    Load a wordlist from a dictionary file.
    If cache is True, looks in CACHE_DIR; otherwise, looks in DICTIONARY_DIR.
    `dictionary_name_in` should be the filename including extension.
    """
    try:
        directory = CACHE_DIR if cache else DICTIONARY_DIR
        dictionary_path_in = directory / dictionary_name_in
        with dictionary_path_in.open("r", encoding="utf-8") as in_file:
            return [x.strip() for x in in_file]
    except Exception as error:
        loc = "cache" if cache else "wordlists"
        print(f"Couldn't read file from {loc}: {dictionary_name_in} Error: {error}")
        return False

def filter_word_list(word_list: List[str],
                     min_word_length: int,
                     max_word_length: int,
                     verbose: bool = False) -> Union[List[str], bool]:
    try:
        return_list = []
        for next_word in word_list:
            wl = len(next_word)
            if next_word.isalpha() and min_word_length <= wl <= max_word_length:
                return_list.append(next_word.lower())
            else:
                if verbose:
                    print(f'rejected: {next_word}')
        return return_list
    except Exception as error:
        print(f"Couldn't edit word_list: {error}")
        return False

def save_wordlist_as_dictionary(wordlist: List[str], dictionary_name_out: str) -> bool:
    try:
        dictionary_path_out = CACHE_DIR / dictionary_name_out
        return file_generic_write(dictionary_path_out, '\n'.join(wordlist))
    except Exception as error:
        print(f"Couldn't write file: {dictionary_name_out} Error: {error}")
        return False

def generate_wordlength_dict(word_list: List[str]) -> Dict[int, List[str]]:
    try:
        return {length: [w for w in word_list if len(w) == length] for length in set(map(len, word_list))}
    except Exception as error:
        print(f"Couldn't generate wordlength dictionary: {error}")
        return {}

def convert_dicelist_to_dictionary(dictionary_name_in: str) -> Union[List[str], bool]:
    """Convert a standard Diceware style list to a simple word list."""
    try:
        dictionary_path_in = DICTIONARY_DIR / dictionary_name_in
        words: List[str] = []
        with dictionary_path_in.open("r", encoding="utf-8") as in_file:
            for line in in_file:
                parts = line.strip().split()
                if len(parts) >= 2:
                    words.append(parts[1].lower())
        return words
    except Exception as error:
        print(f"Couldn't read file: {dictionary_name_in} Error: {error}")
        return False


def list_cached_dictionaries() -> List[str]:
    """Return sorted base names of dictionaries found in the cache directory."""
    if not CACHE_DIR.exists():
        return []
    return sorted(
        path.stem.replace("_data", "")
        for path in CACHE_DIR.glob("*_data.json")
    )


def dictionary_exists(name: str) -> bool:
    """Return ``True`` if ``name`` has a processed JSON dictionary."""
    data = CACHE_DIR / f"{name}_data.json"
    return data.exists()


def list_available_dictionaries() -> None:
    """Print a user friendly list of cached dictionaries."""
    cached = list_cached_dictionaries()
    if not cached:
        print("No cached dictionaries available.")
        return
    print("Available cached dictionaries:")
    for name in cached:
        print(f"  {name}")
