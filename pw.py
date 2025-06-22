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

# MODULES
import entropy
import color


class password:
  def __init__(self):
    # COLOR OBJECT    
    self.c = color.Color()

    # ENTROPY TESTER OBJECT
    self.e = entropy.Entropy()

  def get_password(self, uppercase=True, lowercase=True, digits=True, min_digits=0, specials=True, min_specials=0, specials_override=str(), specials_deny=str(), suppress=list(), no_consecutives=False, extra_shuffle=False, ambiguous=False, bookend=False, colorize=False, verbose=False, num_chars=20, num_reps=1):
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

  def generate_password_list(self):
    return_list = list()
    for n in range(self.num_reps):
      self.password = str()  # the generated password
      self.must_include = list()  # min_digits and min_specials go here

      # create a frame (list) to implement bookend
      self.pw_frame = [-1] * self.num_chars
  
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
        self.pw_frame[self.pw_frame.index(-1)] = x
  
      # generate the remaining number of characters for the password
      for next_pos, next_item in enumerate(self.pw_frame):
        if next_item == -1:
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
    # replace consecutive characters (AA, aa, Aa, 88, **) with a different character from the same category of characters (alpha, numeric, punctuation)
    plist = list(old_password)
    a_count = 0
    b_count = 1
    while True:
      a_char = plist[a_count]
      b_char = plist[b_count]
      if a_char.lower() == b_char.lower():
        # replace 'in kind': ABC=>ABC, 012=>012, !@#=>!@#
        if b_char.isalpha():
          b_char = self.choose_from_alphabet(self.user_alphas, disallow=a_char)
        elif b_char.isnumeric():
          b_char = self.choose_from_alphabet(self.alphabet_digits, disallow=a_char)
        else:
          b_char = self.choose_from_alphabet(self.alphabet_specials, disallow=a_char)
        plist[b_count] = b_char
      else:
        a_count += 1
        b_count += 1
        if b_count == len(plist):
          break
        else:
          a_char = plist[a_count]
          b_char = plist[b_count]
    
    new_password = ''.join(plist)
    
    if old_password != new_password:
      if self.verbose is True:
        old_highlight, new_highlight = self.highlight_consecutive_changes(old_password, new_password)
        print(old_highlight + self.c.color('WHITE') + ' >===NO CONSECUTIVES===> ' + new_highlight + self.c.p(''))
      
    return new_password

  def highlight_consecutive_changes(self, old_password, new_password):
    """Return colorized strings highlighting changed characters."""
    old_col = str()
    new_col = str()
    for o_char, n_char in zip(old_password, new_password):
      if o_char != n_char:
        old_col += self.c.p(o_char, 'red')
        new_col += self.c.p(n_char, 'green')
      else:
        old_col += self.c.p(o_char, 'white')
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
