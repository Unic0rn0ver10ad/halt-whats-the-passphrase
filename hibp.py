"""
Submit passphrases and passwords to HaveIBeenPwned using the pwned passwords API. Checking passwords for breach in this way does not require an API Key. Only the first 5 characters of the password are submitted as a SHA-1 hash, and the optional security padding for returned results is in place.
https://haveibeenpwned.com/API/v3#PwnedPasswords
"""
# LIBRARIES
import hashlib
import requests

# MODULES
import os

class HIBP:
  def __init__(self):
    self.hibp_url = 'https://api.pwnedpasswords.com/range/'
    self.headers = {'Add-Padding': 'true'}
    self.timeout = (15, 60)  # (connect, read)

  def check_password_pwnage(self, password, verbose=False):
    """
    Returns a tuple (True/False, Int/-1)
    True = password has been pwned
    False = password has not been pwned
    Int 1+ = # of times it's been pwned
    Int = -1 = something went wrong
    """
    # get sha-1 hash of password
    sha1_hash = hashlib.sha1()
    sha1_hash.update(password.encode("UTF-8"))
    hashed_pwd = sha1_hash.hexdigest()
    first_5 = hashed_pwd[0:5]
    hash_remainder = hashed_pwd[5:]

    try:
      self.r = requests.request(
        "GET", 
        url=f"{self.hibp_url}{first_5}", 
        headers=self.headers, 
        timeout=self.timeout
      )
    except Exception as error:
      print(f"!!! Problem getting data from HIBP: {error}")
      return (False, -1)
    
    try:
      hibp_hash_list = [line.strip() for line in self.r.text.split(os.linesep)]
    except Exception as error:
      print(f"!!! Problem processing data returned from HIBP: {error}")
      return (False, -1)
    else:
      total_hashes_returned = 0
      padded_hashes = 0
      for line in hibp_hash_list:
        total_hashes_returned += 1
        next_hash, pwn_count = line.split(':')
        if pwn_count == '0':
          # no need to check hash values for padded results
          padded_hashes += 1
        elif next_hash.lower() == hash_remainder.lower():
          # password was found in a databreach
          return (True, pwn_count)
      # password not found in any databreaches
      if verbose is True: print(f"Total hashes returned from HIBP: {total_hashes_returned} (including {padded_hashes} padded hashes.)")
      return (False, 0)

  def test_password_pwnage(self):
    pwd_list = [
    'chicken1',
    'pokemon1',
    'f00tl00se',
    'pa$$w0rd!'
    ]
    for next_pwd in pwd_list:
      pwned, times = self.check_password_pwnage(next_pwd)
      print(next_pwd, pwned, times)
