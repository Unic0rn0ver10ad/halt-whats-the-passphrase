"""
Halt! What's the Passphrase?
Passphrase generator module.

Move generate_wordlist_from_file and generate_wordlength_dict to pp_utils.py

Refactor get_random_words_from_list to use self.wordlength_dict
"""

# Standard library imports
import os
import re
import random
import secrets
import requests
import string
from collections import defaultdict

# Local application imports
import entropy
import color
import cache
import pp_utils


class passphrase:
  def __init__(self, verbose=False, colorize=False):
    self.verbose = verbose
    self.color = colorize
    self.wordlist = 'new_eff_large_wordlist.txt'
    self.min_word_length = 4
    self.max_word_length = 9
    self.dictionary_fp = os.path.join("dictionaries")             
    self.cache_fp = os.path.join("cache")
    self.wordlist_file = os.path.join(self.dictionary_fp, self.wordlist)
    self.alphabet_uppercase = string.ascii_uppercase
    self.alphabet_lowercase = string.ascii_lowercase
    self.alphabet_digits = string.digits
    self.alphabet = self.alphabet_uppercase + self.alphabet_lowercase + self.alphabet_digits

    # WORDLIST
    # a single list with every possible dictionary word
    self.wordlist_cache_file = os.path.join(self.cache_fp, 'cache_wordlist.txt')
    self.wordlist_cache = cache.Cache(self.wordlist_cache_file)
    if self.wordlist_cache.cache_exists():
      self.wordlist = self.wordlist_cache.read_from_cache(self.wordlist_cache_file)
      if self.verbose is True: print("Successfully read wordlist from cache")
    else:
      if self.verbose is True: print("Unable to read wordlist from cache")
      self.wordlist = self.generate_wordlist_from_file(self.wordlist_file)
      self.wordlist_cache.save_to_cache(self.wordlist_cache_file, self.wordlist)
    self.wordlist_length = len(self.wordlist)
    if self.verbose is True: print(f"{self.wordlist_length} words in {self.wordlist_file}")

    # WORDLENGTH DICT
    # The wordlength dict has the desired word length as the key, and a single list of all possible words of that length as the value.
    # Example: {6: ['abacus', 'ablaze', 'abroad', ...]}
    self.wordlength_cache_file = os.path.join(self.cache_fp, 'cache_wordlength.txt')
    self.wordlength_cache = cache.Cache(self.wordlength_cache_file)
    if self.wordlength_cache.cache_exists():
      self.wordlength_dict = self.wordlength_cache.read_from_cache(self.wordlength_cache_file)
      if self.verbose is True: print("Successfully read wordlength dict from cache")
    else:
      if self.verbose is True: print("Unable to read wordlength dict from cache")
      self.wordlength_dict = self.generate_wordlength_dict(self.wordlist)
      self.wordlength_cache.save_to_cache(self.wordlength_cache_file, self.wordlength_dict)
    if self.verbose is True: print(f"{len(self.wordlength_dict)} possible wordlengths found in self.wordlength_dict")

    # PARTITIONS LIST
    # The partition list is a list of lists with all the ways that a passphrase of a given number of characters can be constructed.
    # Example: For num_chars = 10, min_word_length = 4, partions = [[5, 5], [6, 4]]
    self.partition_cache_file = os.path.join(self.cache_fp, 'cache_partitions.txt')
    self.parition_cache = cache.Cache(self.partition_cache_file)

    # COLOR OBJECT
    self.c = color.Color()

    # ENTROPY TESTER OBJECT
    self.e = entropy.Entropy()

  def generate_wordlist_from_file(self, path_to_in_file):
    """
    Turn a text file with one dictionary word per line into a list in memory.
    """
    print(f"gen wordlist: {path_to_in_file}")
    try:
      in_file = open(path_to_in_file, "r")
    except Exception as error:
      print(f"Couldn't read file: {path_to_in_file} Error: {error}")
      return False
    else:
      return_list = [x.strip() for x in in_file]
      
      # save results to cache
      self.wordlist_cache.save_to_cache('cache_wordlist.txt', return_list)
      
      return return_list

  def generate_wordlength_dict(self, word_list):
    """
    Turn an in-memory list of words into a wordlength dictionary like this: {1:['a', 'I'], 2:['no', 'an'], 3:['ape', 'bee']}. Grabbing a random item from the list from the key returns a random word of the desired length.
    source: https://wordaligned.org/articles/partitioning-with-python
    """
    words_dict = defaultdict(list)  # does not throw keyerror
    for word in word_list:
      words_dict[len(word)].append(word)

    # save results to cache
    words_dict = dict(words_dict)  # convert from defaultdict to dict
    self.wordlength_cache.save_to_cache('cache_wordlength.txt', words_dict)
    
    return(words_dict)

  def get_passphrase(self, num_chars=20, num_reps=1, num_words=False, verbose=False, augenbaumize=False, pad=False):
    # ERROR CHECKING FOR INPUTS
    if type(num_chars) != int:
      print(f"Invalid type for num_chars: {num_chars}. Must be a number between 10 and 100")
      exit()
    if num_chars < 10 or num_chars > 100:
      print(f"Invalid number of passphrase chars entered: {num_chars}. Must be between 10 and 100.")
      exit()
    if num_words is not False and type(num_words)!= int:
      print(f"Invalid type for num_words: {num_words}. Must be an integer.")
      exit()

    self.num_chars = num_chars
    self.num_reps = num_reps
    self.num_words = num_words
    self.verbose = verbose
    self.augenbaumize = augenbaumize
    self.pad = pad

    # GENERATE PASSPHRASE LIST
    self.passphrase_list = self.generate_passphrase_list()
    
    return self.passphrase_list

  def generate_passphrase_list(self):
    # Return a list with the number and type of passphrases requested
    return_list = list()
    for n in range(self.num_reps):
      self.passphrase = str()  # the generated passphrase
      # FIXED NUMBER OF WORDS OR CHARACTERS?
      if self.num_words is not False:
        # FIXED NUMBER OF WORDS
        self.pp_frame = [x.capitalize() for x in self.get_random_words_from_list(self.num_words)]
      else:
        # FIXED NUMBER OF CHARACTERS
        # CREATE PARTITIONS THAT ADD UP TO NUM_CHARS
        self.possible_partitions = self.parition_cache.read_from_cache(self.num_chars)
        if self.possible_partitions is False:
          if self.verbose is True: print(f"Generating Partition List for: {self.num_chars}")
          # self.possible_partitions = self.generate_partitions(self.num_chars)
          self.possible_partitions = pp_utils.generate_partitions_for_n(n, self.min_word_length, self.max_word_length)
          self.parition_cache.save_to_cache(self.num_chars, self.possible_partitions)
        
        # SELECT A RANDOM PARTITION TO USE
        rand_partition = secrets.choice(self.possible_partitions)
    
        # SHUFFLE THE ORDER OF PARTITION ITEMS
        random.SystemRandom().shuffle(rand_partition)
    
        # GRAB A RANDOM WORD OF CORRECT LENGTH FOR EACH ITEM IN FINAL PARTITION
        self.pp_frame = [self.get_random_word_of_length(x).capitalize() for x in rand_partition]

      # PAD
      if self.pad is not False:
        pad_str = self.pad[0]
        pad_pos = self.pad[1]
        if pad_pos == 1:
          # beginning
          self.pp_frame = [pad_str] + self.pp_frame
        elif pad_pos == 2:
          # middle
          middle = len(self.pp_frame) // 2
          self.pp_frame = self.pp_frame[:middle] + [pad_str] + self.pp_frame[middle:]
        elif pad_pos == 3:
          # end
          self.pp_frame = self.pp_frame + [pad_str]
        
      # AUGENBAUMIZE
      if self.augenbaumize is not False:
        self.pp_frame = [self.augenbaumize] + self.pp_frame + [self.augenbaumize[::-1]]
  
      # CREATE PASSPHRASE STRING
      self.passphrase = ''.join(self.pp_frame)
  
      # COLORIZE
      if self.color is True:
        self.passphrase = self.colorize_passphrase(self.passphrase)

      return_list.append(self.passphrase)

    return return_list

  def get_random_word_of_length(self, word_length):
    return secrets.choice(self.wordlength_dict[word_length]).capitalize()
    
  def colorize_passphrase(self, plain_text):
    color_passphrase = str()
    for next_char in plain_text:
      if next_char.isalpha() is True:
        if next_char.isupper() is True:
          # uppercase letter
          next_char = self.c.p(next_char, 'red')
        else:
          # lowercase letter
          next_char = self.c.p(next_char, 'blue')
      elif next_char.isnumeric() is True:
        # digit
        next_char = self.c.p(next_char, 'green')
      else:
        # punctuation
        next_char = self.c.p(next_char, 'magenta')
      color_passphrase += next_char
    color_passphrase += self.c.p('')  # terminate color commands
    return color_passphrase
  
  def generate_passphrase_wikipedia(self, num_titles=3, num_reps=1, colorize=False, augenbaumize=False, verbose=False):
    s = requests.Session()
    url = "https://en.wikipedia.org/w/api.php"
    params = {
      "action": "query",
      "format": "json",
      "list": "random",
      "rnnamespace": "0",
      "rnlimit": str(num_titles * num_reps)
    }
    pp_frame = [self.de_wikify(' '.join(x)) for x in list(self.chunker([x['title'] for x in s.get(url=url, params=params).json()["query"]["random"]], num_titles))]

    # AUGENBAUMIZE
    if augenbaumize is not False:
      new_frame = []
      for next_pp in pp_frame:
        next_pp = augenbaumize + next_pp + augenbaumize[::-1]
        new_frame.append(next_pp)
      pp_frame = new_frame

    # COLORIZE
    if colorize is True:
      new_frame = []
      for next_pp in pp_frame:
        next_pp = self.colorize_passphrase(next_pp)
        new_frame.append(next_pp)
      pp_frame = new_frame
      
    return pp_frame

  def chunker(self, seq, size):
    # takes a sequence and generates chunks of it, each chunk being a smaller sequence of length size (except possibly the last chunk, which may be shorter if there are not enough elements left in the original sequence). This method can be used for processing data in smaller, manageable pieces.
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

  def de_wikify(self, text):
    # clean up and standardize the Wikipedia titles so they can be used as part of a passphrase.
    if self.verbose is True: print(f"START : {text}")

    # remove anything in and including ( )
    text = re.sub("[\(\[].*?[\)\]]", "", text).strip()
    if self.verbose is True: print(f"-PAREN: {text}")

    # replace hyphens with spaces for better capitalization
    text.replace('-', ' ')

    # add each word to a list to make it easier to colorize the text
    text_list = text.split(' ')
    if self.verbose is True: print(f"!   {text_list}")
    
    # remove all punctuation
    # capitalize first letter of each word
    new_text_list = list()
    for next_word in text_list:
      new_word = str()
      cap_flag = True
      for next_char in next_word:
        if next_char.isalnum():
          if cap_flag is True:
            next_char = next_char.upper()
            cap_flag = False
          new_word += next_char
      new_text_list.append(new_word)
    text = ''.join(new_text_list)
    if self.verbose is True: print(f"!!!  {text}")
    return text
  
  def get_random_words_from_list(self, num_words):
    """
    used by generate_passphrase_list() to return a passphrase with a fixed number of words of any length
    currently uses self.wordlist but could be refactored to only use self.wordlist_dict, so that self.wordlist does not need to be kept in memory
    Returns *num_words* random words from self.wordlist
    Need to make sure no duplicate words are returned!
    """
    # break out new function to get a single word so it can be called recursively
    # make sure no. of words requested is less than size of dictionary used
    
    # return [self.wordlist[random.SystemRandom().randrange(self.wordlist_length)] for x in range(num_words)]
    return [self.wordlist[secrets.randbelow(self.wordlist_length)] for x in range(num_words)]
