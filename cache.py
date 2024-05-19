"""
Save (cache) pre-generated data as a dict for fast retrieval without having to regenerate the same data. Uses eval() to turn the saved text file into a dict in memory.
=> Redo this using ast instead of eval for safety.
"""

# MODULES
import toolkit


class Cache:
  def __init__(self, cache_filepath):
    self.file = cache_filepath
    self.cache = dict()
    self.cache_already_exists = False

    # check to see if cache already exists
    if toolkit.file_exists(self.file):
      # print(f"Cache found on disk: {self.file}")
      try:
        self.cache = eval(toolkit.file_read_line(self.file, 1))
      except Exception as exception:
        print(f"Unable to parse cache from file: {exception}")
        pass
      else:
        self.cache_already_exists = True
    else:
      # cache not found on disk
      print(f"Cache not found on disk: {self.file}")

  def cache_exists(self):
    return self.cache_already_exists

  def read_from_cache(self, api_call):
    try:
      return self.cache[api_call]
    except:
      return False
  
  def save_to_cache(self, api_call, api_results):
    # add api_results to cache and save to disk
    try:
      self.cache[api_call] = api_results
    except Exception as exception:
      print(f"Unable to update cache for {api_call}: {exception}\nAPI_results: {api_results}\nCache not saved to disk.")
      pass
    else:
      toolkit.file_generic_write(self.file, self.cache)