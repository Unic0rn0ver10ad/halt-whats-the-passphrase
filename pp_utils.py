"""
Halt! What's the Passphrase?
Passphrase utilities.
"""

# Standard library imports
import os
from functools import lru_cache
import time
import secrets
import linecache
from collections import defaultdict

# Local application imports
import toolkit


def create_partitions(partition_path, start_n=10, end_n=50, min_val=4, max_val=9):
    partitions_dict = {}

    start_time = time.time()
    for n in range(start_n, end_n + 1):
        partition_start_time = time.time()
        partitions = generate_partitions_for_n(n, min_val, max_val)
        time_taken = time.time() - partition_start_time

        print(f"N = {n}, Total Partitions = {len(partitions)}, Time taken = {time_taken:.2f} seconds")
        partitions_dict[n] = partitions

    total_time = time.time() - start_time
    print(f"Partition generation completed. Time: {total_time:.2f} seconds. Results written to {partition_path}.")
    toolkit.file_generic_write(partition_path, partitions_dict)

@lru_cache(maxsize=None)
def generate_partitions_for_n(n, min_val, max_val):
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

def divide_and_save_partitions(base_dir, all_partitions_dict):
    """
    Save the partitions to multiple files. As the number of partitions grows exponentially based on N, for a web app we might want to only load the partitions that are needed.
    """
    # Define the ranges for splitting dictionaries
    ranges = [(None, 32), (33, 50), (51, 75)]

    # Current range being processed
    current_range = 0

    # Temporary dictionary to hold the current range's partitions
    temp_dict = {}

    # Loop through each item in the sorted dictionary
    for key, value in sorted(all_partitions_dict.items()):
        # Check if the key falls within the current range or if it should be in its own file
        if current_range < len(ranges) and ranges[current_range][0] <= key <= ranges[current_range][1]:
            # Add to current temp dict
            temp_dict[key] = value
        else:
            # Save the current temp dict if it's not empty
            if temp_dict:
                filename = f"partitions_up_to_{max(temp_dict.keys())}.txt"
                toolkit.file_generic_write(os.path.join(base_dir, filename), temp_dict)
                temp_dict = {}  # Reset for the next range

            # Move to the next range if needed
            if current_range < len(ranges)-1 and key > ranges[current_range][1]:
                current_range += 1

            # If the key is greater than the last range, each key gets its own file
            if key > ranges[-1][1]:
                # single file for each key outside the defined ranges
                toolkit.file_generic_write(os.path.join(base_dir, f"partition_{key}.txt"), {key: value})
            else:
                # Add to temp dict for anything within the range
                temp_dict[key] = value

    # Save the last range's dictionary if not empty
    if temp_dict:
        filename = f"partitions_up_to_{max(temp_dict.keys())}.txt"
        toolkit.file_generic_write(os.path.join(base_dir, filename), temp_dict)

def get_random_words_from_file(path_to_in_file, num_words):
    """
    Returns *num_words* random words from *path_to_in_file*.
    Not used; use get_random_words_from_list instead.
    """
    try:
        with open(path_to_in_file, "r") as in_file:
            word_list = []
            total_words = sum(1 for _ in in_file)
            in_file.seek(0)  # Reset file pointer to the beginning after counting
            for _ in range(num_words):
                random_line = secrets.randbelow(total_words)
                next_word = linecache.getline(path_to_in_file, random_line).strip()
                word_list.append(next_word)
            linecache.clearcache()
            return word_list
    except Exception as error:
        print(f"Couldn't read file: {path_to_in_file} Error: {error}")

def generate_wordlist_from_dicelist(path_to_in_file):
    """
    Offline tool. Use for converting the EFF Dicelist to a usable wordlist.
    """
    print(f'gen wordlist from dicelist: {path_to_in_file}')
    try:
        with open(path_to_in_file, "r") as in_file:
            return_list = [x.replace('\t', ' ').rstrip().split(' ')[1] for x in in_file]

        newfile = 'new_' + path_to_in_file
        returntext = '\n'.join(return_list)

        toolkit.file_generic_write(newfile, returntext)
        toolkit.wordlist_cache.save_to_cache('cache_wordlist.txt', return_list)

        return return_list
    except Exception as error:
        print(f"Couldn't read file: {path_to_in_file} Error: {error}")
        return False

def generate_wordlist_from_dictionary(path_to_file):
    """
    Parse a text file with one dictionary word per line.
    """

    try:
        my_file = open(path_to_file, "r")
        file_contents = my_file.read()
        return_list = []
        for line in file_contents.splitlines():
            return_list.append(line.strip())
        my_file.close()
        return return_list
    except Exception as error:
        print(f"Couldn't read file: {path_to_file} Error: {error}")
        return False

def generate_dictionary_from_wordlist(wordlist, path_to_file):
    """
    Generate a text file with one dictionary word per line.
    """
    try:
        my_file = open(path_to_file, "w")
        for word in wordlist:
            my_file.write(word + '\n')
        my_file.close()
    except Exception as error:
        print(f"Couldn't write file: {path_to_file} Error: {error}")
        return False

def edit_word_list(word_list, min_word_length, max_word_length):
    """
    Filter word_list. Only accept words that contain [A-Z a-z] (no numbers or special characters) and are between *min_word_length* and *max_word_length* characters long.
    """
    return_list = list()
    try:
        for next_word in word_list:
            wl = len(next_word)
            if next_word.isalpha() and min_word_length <= wl and wl <= max_word_length:
                return_list.append(next_word)
            else:
                print(f'rejected: {next_word}')
        return return_list
    except Exception as error:
        print(f"Couldn't edit word_list: {error}")
        return False

def generate_wordlength_dict(word_list, path_to_out_file):
        """
        Turns an in-memory list of words into a wordlength dictionary and saves it to disk. The dictionary looks like this: {1:['a', 'I'], 2:['no', 'an'], 3:['ape', 'bee']}. Grabbing a random item from the list from the key therefore returns a random word of the desired length.
        """
        words_dict = defaultdict(list)  # does not throw keyerror
        for word in word_list:
          words_dict[len(word)].append(word)

        words_dict = dict(words_dict)  # convert from defaultdict to dict

        # Save word length dictionary to cache
        toolkit.file_generic_write(path_to_out_file, words_dict)

        return(words_dict)

def process_raw_dictionary(raw_dictionary_filename, 
                           min_word_length=None, 
                           max_word_length=None):
    """
    Processes a raw dictionary file and generates the necessary word list and word length dictionary.

    :param raw_dictionary_file: str, name of the raw dictionary file.
    :param min_word_length: int, optional, minimum word length to include.
    :param max_word_length: int, optional, maximum word length to include.
    """
    raw_dictionary_path = os.path.join('raw_dictionaries', raw_dictionary_filename)
    print(f'processing {raw_dictionary_filename}')

    # Generate file names
    dictionary_basename = os.path.splitext(raw_dictionary_filename)[0]
    
    wordlength_cache_path = os.path.join('cache', f'{dictionary_basename}_wordlength.txt')
    
    wordlist_cache_path = os.path.join('cache', f'{dictionary_basename}_wordlist.txt')

    partitions_cache_path = os.path.join('cache', f'{dictionary_basename}_partitions.txt')

    final_dictionary_path = os.path.join('dictionaries', f'new_{dictionary_basename}.txt')

    # Generate words_list
    words_list = generate_wordlist_from_dictionary(raw_dictionary_path)
    print(f'{dictionary_basename} contains {len(words_list)} base words')

    # Edit the word_list
    edited_words_list = edit_word_list(words_list, min_word_length, max_word_length)
    print(f'{dictionary_basename} contains {len(edited_words_list)} edited words between {min_word_length} and {max_word_length} characters')

    # Save the edited word_list
    toolkit.file_generic_write(wordlist_cache_path, edited_words_list)

    # Save the edited dictionary
    generate_dictionary_from_wordlist(edited_words_list, final_dictionary_path)

    # Generate and save the wordlength dictionary
    generate_wordlength_dict(edited_words_list, wordlength_cache_path)

    # Generate and save partitions to cache
    create_partitions(partitions_cache_path, start_n=10, end_n=50, min_val=min_word_length, max_val=max_word_length)

    print("Raw dictionary processing complete. Wordlist, wordlength dictionary, and partitions saved to cache.")
