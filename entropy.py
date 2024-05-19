"""
Entropy tester for passwords!
"""

# LIBRARIES
import math


class Entropy:
  def __init__(self):
    self.entropy = None

  def test_entropy(self, password_len, alphabet_size):
    # source: https://github.com/gerardovitale/strong-random-password-generator
    # https://crypto.stackexchange.com/questions/374/how-should-i-calculate-the-entropy-of-a-password
    # pass in the password and the number of possible characters for each position
    return password_len * math.log2(alphabet_size)
