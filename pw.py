"""
Halt! What's the Passphrase?
Password generator module.
Read about the difference between the secrets and random modules in Python's standard library:
https://docs.python.org/3/library/secrets.html
"""
# LIBRARIES
import random
import secrets
import string
from typing import List

# MODULES
import entropy
import color


class password:
  def __init__(self):
    # COLOR OBJECT    
    self.c = color.Color()

    # ENTROPY TESTER OBJECT
    self.e = entropy.Entropy()

  def get_password(self, uppercase=True, lowercase=True, digits=True, min_digits=0,
                   specials=True, min_specials=0, specials_override=str(),
                   specials_deny=str(), suppress=list(), no_consecutives=False,
                   extra_shuffle=False, ambiguous=False, bookend=False,
                   colorize=False, verbose=False, num_chars=20,
                   num_reps=1) -> List[str]:
    """
    Returns a list of (possibly colorized) passwords given the user's paramters.
    Some interesting parameters to note:
     * no_consecutives: disallow adjacent consecutive chars (Aa, AA, aa, 88, **)
     * ambiguous: don't use chars 'l', '1', 'I', 'O', '0'
     * bookend: upper- and lowercase letters only at start and end of password
    """
    self.use_uppercase = uppercase
    self.use_lowercase = lowercase
    self.use_digits = digits
    self.min_digits = min_digits
    self.use_specials = specials
    self.min_specials = min_specials
    self.specials_override = str(specials_override)  # just in case
    self.specials_deny = str(specials_deny)  # just in case
    self.no_consecutives = no_consecutives
    self.extra_shuffle = extra_shuffle
    self.num_chars = num_chars
    self.num_reps = num_reps
    self.remove_ambiguous = ambiguous
    self.bookend = bookend
    self.suppress = suppress
    self.color = colorize
    self.verbose = verbose

    self.ambiguous_characters = ['l', '1', 'I', 'O', '0']

    # ERROR CHECK: ARGUMENTS FROM CLI
    # min_digits + min_specials cannot be greater than the total number of chars asked for in the password
    if self.min_digits + self.min_specials > self.num_chars:
      print(f"You've asked for a {self.num_chars}-character password with {self.min_digits} digits and {self.min_specials} special characters. {self.min_digits} + {self.min_specials} = {self.min_digits + self.min_specials} which is greater than {self.num_chars}. Your password is: password. Exiting.")
      exit(1)

    # specials_override string cannot be longer than 100 characters
    if len(self.specials_override) >= 100:
      print(f"You've tried to add a list of special characters that is {len(self.specials_override)} characters long. That's just too many characters (100 is the maximum). Your password is: hack3r. Exiting.")
      exit(1)

    # COMPREHENSIVE VALIDATION: Check for conflicting parameter combinations
    self._validate_password_parameters()

    # CREATE UPPER, LOWER, DIGITS ALPHABETS
    # create the uppercase, lowercase, and digits alphabets (strings of usable characters by class) that can be used to generate passwords from system defaults
    self.alphabet_uppercase = string.ascii_uppercase
    self.alphabet_lowercase = string.ascii_lowercase
    self.alphabet_digits = string.digits

    # CREATE SPECIALS ALPHABET
    # the specials alphabet includes all sytem default punctuation, but the user can remove items from the default specials list, or override it entirely
    if self.specials_override != str():  # not an empty string
      self.specials_override = self.specials_override.replace(' ', '') # error check
      self.specials_override = ''.join(set(self.specials_override))  # error check
      self.specials_list = list(self.specials_override)
    else:
      self.specials_list = [x for x in string.punctuation]
  
    if self.specials_deny != str():  # not an empty string
      # try to remove anything in self.specials_deny list from self.specials_list
      for i in self.specials_deny:
        try:
          self.specials_list.remove(i)
        except ValueError:
          pass

    self.alphabet_specials = ''.join(self.specials_list)

    # REMOVE AMBIGUOUS
    # remove anything in self.ambiguous_characters from all alphabets if requested
    if self.remove_ambiguous is True:
      self.alphabet_uppercase = ''.join([x for x in self.alphabet_uppercase if x not in self.ambiguous_characters])
      self.alphabet_lowercase = ''.join([x for x in self.alphabet_lowercase if x not in self.ambiguous_characters])
      self.alphabet_digits = ''.join([x for x in self.alphabet_digits if x not in self.ambiguous_characters])
      self.alphabet_specials = ''.join([x for x in self.alphabet_specials if x not in self.ambiguous_characters])

    # CREATE USER DEFINED ALPHABETS
    # create self.alphabet, a string of all allowable characters that can be used to construct the password if there are no other conditions
    self.alphabet = ""

    # create self.user_alphas, a string of all allowable non-special and non-digit characters, used if the bookend option is invoked to prevent a password from beginning or ending with digits or special characters
    self.user_alphas = ""  # could be all uppercase, all lowercase, both, or none (empty string)

    if self.use_uppercase:
      self.alphabet += self.alphabet_uppercase
      self.user_alphas += self.alphabet_uppercase

    if self.use_lowercase:
      self.alphabet += self.alphabet_lowercase
      self.user_alphas += self.alphabet_lowercase

    if self.use_digits:
      self.alphabet += self.alphabet_digits

    if self.use_specials:
      self.alphabet += self.alphabet_specials

    # ERROR CHECK: ALPHABETS
    # check to make sure self.alphabet is not an empty string!
    if self.alphabet == str():
      print("You've asked for a password but have disallowed all possible characters. Very clever! Your password is: n0thingness. Exiting.")
      exit(1)

    # you can't bookend without any actual letters
    if self.bookend is True and self.user_alphas == str():
      print("You've asked for a bookended password that doesn't start with digits or special characters, but disallowed upper and lowercase letters as well. Your password is: n1c3try. Exiting.")
      exit(1)

    # ENTROPY TESTER
    if self.verbose is True:
      self.entropy_val = self.e.test_entropy(self.num_chars, len(self.alphabet))
      print(f"Entropy for all passwords of length {self.num_chars} with {len(self.alphabet)} possible values per character = {round(self.entropy_val)}")

    # GENERATE PASSWORD LIST
    self.password_list = self.generate_password_list()
    
    return self.password_list

  def generate_password_list(self) -> List[str]:
    return_list = list()
    for n in range(self.num_reps):
      self.password = str()  # the generated password
      self.must_include = list()  # min_digits and min_specials go here

      # create a frame (list) to implement bookend
      self.pw_frame: List[str] = [str()] * self.num_chars
  
      # include min_digits
      self.must_include += [self.choose_from_alphabet(self.alphabet_digits) for x in range(self.min_digits)]

      # include min_specials
      self.must_include += [self.choose_from_alphabet(self.alphabet_specials) for x in range(self.min_specials)]

      # add bookends to the frame
      if self.bookend is True:
        self.pw_frame[0] = self.choose_from_alphabet(self.user_alphas)
        self.pw_frame[-1] = self.choose_from_alphabet(self.user_alphas)
        
      # add min_digits and min_specials to the frame
      for x in self.must_include:
        self.pw_frame[self.pw_frame.index(str())] = x
  
      # generate the remaining number of characters for the password
      for next_pos, next_item in enumerate(self.pw_frame):
        if next_item == str():
          self.pw_frame[next_pos] = self.choose_from_alphabet(self.alphabet)
      
      # shuffle the frame
      self.pw_frame = self.shuffle_frame(self.pw_frame)
  
      # randomly shuffle the frame one extra time if asked
      if self.extra_shuffle is True:
        self.pw_frame = self.shuffle_frame(self.pw_frame)

      # convert frame to a string
      self.password = ''.join(self.pw_frame)

      # NO CONSECUTIVE DUPLICATE CHARACTERS
      # shuffling again past this point could re-introduce consecutive duplicate characters
      if self.no_consecutives is True:
        self.password = self.de_consecutivize(self.password)
  
      # COLORIZE PASSWORD
      if self.color is True:
        self.password = self.colorize_password(self.password)
      
      return_list.append(self.password)

    return return_list
  
  def colorize_password(self, plain_text):
    color_password = str()
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
      color_password += next_char
    color_password += self.c.p('')  # terminate color commands
    return color_password
  
  def de_consecutivize(self, old_password):
    """Replace consecutive duplicate characters with a different character of the same type."""
    plist = list(old_password)
    i = 0
    while i < len(plist) - 1:
        if plist[i].lower() == plist[i + 1].lower():
            if plist[i + 1].isalpha():
                plist[i + 1] = self.choose_from_alphabet(self.user_alphas, disallow=plist[i])
            elif plist[i + 1].isnumeric():
                plist[i + 1] = self.choose_from_alphabet(self.alphabet_digits, disallow=plist[i])
            else:
                plist[i + 1] = self.choose_from_alphabet(self.alphabet_specials, disallow=plist[i])
        i += 1
    new_password = ''.join(plist)
    if old_password != new_password and self.verbose:
        old_highlight, new_highlight = self.highlight_consecutive_changes(old_password, new_password)
        print(old_highlight + self.c.color('WHITE') + ' >===NO CONSECUTIVES===> ' + new_highlight + self.c.p(''))
    return new_password

  def highlight_consecutive_changes(self, old_password, new_password):
    """Return colorized strings highlighting changed characters, including both characters in consecutive pairs."""
    # Find indices of consecutive duplicates in old_password
    consecutive_indices = set()
    for i in range(len(old_password) - 1):
        if old_password[i].lower() == old_password[i + 1].lower():
            consecutive_indices.add(i)
            consecutive_indices.add(i + 1)

    # Find indices of changed characters in new_password
    changed_indices = set()
    for i, (o_char, n_char) in enumerate(zip(old_password, new_password)):
        if o_char != n_char:
            changed_indices.add(i)

    old_col = ""
    new_col = ""
    for i, (o_char, n_char) in enumerate(zip(old_password, new_password)):
        if i in consecutive_indices:
            old_col += self.c.p(o_char, 'red')
        else:
            old_col += self.c.p(o_char, 'white')
        if i in changed_indices or i in consecutive_indices:
            new_col += self.c.p(n_char, 'green')
        else:
            new_col += self.c.p(n_char, 'white')
    return old_col, new_col
  
  def choose_from_alphabet(self, alphabet, disallow=None):
    # if disallow is not None, iterate until a non-matching entry is produced
    next_char = secrets.choice(alphabet)
    if disallow is not None and next_char.lower() == disallow:
      return self.choose_from_alphabet(alphabet, disallow=disallow)
    return next_char

  def shuffle_frame(self, frame):
    # uses the random module, not the secrets module because secrets module does not support shuffling
    if self.bookend is True:
      # turning this into a one-liner does not work
      # apparently list slices cannot be shuffled
      # this doesn't work: random.SystemRandom().shuffle(frame[1:-1])
      shuffle_this = frame[1:-1]
      random.SystemRandom().shuffle(shuffle_this)
      frame[1:-1] = shuffle_this
    else:
      random.SystemRandom().shuffle(frame)
    return frame

  def _validate_password_parameters(self):
    """Comprehensive validation of password generation parameters to catch conflicting combinations."""
    
    # Check if specials_override contains only special characters when min_specials > 0
    if self.min_specials > 0 and self.specials_override != str():
      specials_override_clean = self.specials_override.replace(' ', '')
      if not any(c in string.punctuation for c in specials_override_clean):
        print(f"You've asked for {self.min_specials} special characters but your specials override '{self.specials_override}' contains no special characters (punctuation). Your password is: hack3r. Exiting.")
        exit(1)
    
    # Check if specials_deny removes all special characters when min_specials > 0
    if self.min_specials > 0 and self.specials_deny != str():
      # Create a test specials list to see what would remain
      test_specials = [x for x in string.punctuation]
      for char in self.specials_deny:
        try:
          test_specials.remove(char)
        except ValueError:
          pass
      if not test_specials:
        print(f"You've asked for {self.min_specials} special characters but your specials deny list '{self.specials_deny}' removes all available special characters. Your password is: hack3r. Exiting.")
        exit(1)
    
    # Check if specials_override + specials_deny results in no special characters when min_specials > 0
    if self.min_specials > 0 and self.specials_override != str() and self.specials_deny != str():
      specials_override_clean = ''.join(set(self.specials_override.replace(' ', '')))
      remaining_specials = [c for c in specials_override_clean if c not in self.specials_deny]
      if not remaining_specials:
        print(f"You've asked for {self.min_specials} special characters but your specials override '{self.specials_override}' combined with specials deny '{self.specials_deny}' leaves no special characters available. Your password is: hack3r. Exiting.")
        exit(1)
    
    # Check if specials_override results in no special characters when min_specials > 0
    if self.min_specials > 0 and self.specials_override != str():
      specials_override_clean = ''.join(set(self.specials_override.replace(' ', '')))
      if not any(c in string.punctuation for c in specials_override_clean):
        print(f"You've asked for {self.min_specials} special characters but your specials override '{self.specials_override}' contains no special characters (punctuation). Your password is: hack3r. Exiting.")
        exit(1)
    
    # Check if disallowing character classes conflicts with minimum requirements
    if not self.use_digits and self.min_digits > 0:
      print(f"You've asked for {self.min_digits} digits but disallowed all digits with -no d. Your password is: hack3r. Exiting.")
      exit(1)
    
    if not self.use_specials and self.min_specials > 0:
      print(f"You've asked for {self.min_specials} special characters but disallowed all special characters with -no s. Your password is: hack3r. Exiting.")
      exit(1)
    
    # Check if bookend is requested but no letters are allowed
    if self.bookend and not self.use_uppercase and not self.use_lowercase:
      print("You've asked for a bookended password but disallowed both uppercase and lowercase letters. Your password is: n1c3try. Exiting.")
      exit(1)
    
    # Check if ambiguous character removal would eliminate all characters of a required type
    if self.remove_ambiguous:
      if self.use_uppercase:
        remaining_upper = [c for c in string.ascii_uppercase if c not in self.ambiguous_characters]
        if not remaining_upper:
          print("You've asked for uppercase letters but the ambiguous character filter removes all uppercase letters. Your password is: hack3r. Exiting.")
          exit(1)
      
      if self.use_lowercase:
        remaining_lower = [c for c in string.ascii_lowercase if c not in self.ambiguous_characters]
        if not remaining_lower:
          print("You've asked for lowercase letters but the ambiguous character filter removes all lowercase letters. Your password is: hack3r. Exiting.")
          exit(1)
      
      if self.use_digits:
        remaining_digits = [c for c in string.digits if c not in self.ambiguous_characters]
        if not remaining_digits:
          print("You've asked for digits but the ambiguous character filter removes all digits. Your password is: hack3r. Exiting.")
          exit(1)
