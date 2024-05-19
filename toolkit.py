# LIBRARIES
import linecache
import os


def loc():
  cwd = os.getcwd()
  scripts_list = [
    'hwtp.py',
    'cache.py',
    'cli.py',
    'color.py',
    'entropy.py',
    'hibp.py',
    'pp.py',
    'pp_utils.py',
    'pw.py'
  ]

  longest_script_chars = (max([len(x) for x in scripts_list])) + 2

  print("""+------------------+
| LINES  OF  CODE  |
+------------------+""")
  loc = 0
  total_func = 0
  for next_file in scripts_list:
    fp = os.path.join(cwd, next_file)
    with open(fp, 'r') as my_file:
      my_func = 0
      for count, line in enumerate(my_file):
        if "def " in line:
          my_func +=1
      total_func += my_func
    text_padding = longest_script_chars - len(next_file)
    num_padding = 4 - len(str(count))
    func_padding = 2 - len(str(my_func))
    print(f"{next_file[:-3] + ('.' * (text_padding + num_padding))}{count}  [{(' ' * func_padding) + str(my_func)}]")
    loc += count
  print("+------------------+")
  
  print(f"TOTAL SCRIPTS: {len(scripts_list)}")
  print(f"TOTAL LINES OF CODE: {loc}")
  print(f"TOTAL FUNCTIONS: {total_func}")

def file_exists(file_path):
  return os.path.exists(file_path)

def file_generic_read(path_to_file):
    try:
        my_file = open(path_to_file, "r")
    except Exception as error:
        print(f"Couldn't read file: {path_to_file} Error: {error}")
        return False
    else:
        file_contents = my_file.read()
        my_file.close()
        return file_contents

def file_generic_write(path_to_file, data_to_save):
  try:
    my_file = open(path_to_file, "w")
  except Exception as error:
    print(f"Failed to save file: {path_to_file} Error: {error}")
    return False
  else:
    my_file.write(str(data_to_save))
    my_file.close()
    return True

def file_read_line(path_to_file, line_number):
    try:
        return_text = linecache.getline(path_to_file, line_number)
    except Exception as error:
        print(
            f"Unable to read line: {line_number} from: {path_to_file} Error: {error}"
        )
        return False
    else:
        return_text = return_text.rstrip()  # remove \n
        linecache.clearcache()
        return return_text

def get_number_of_lines_in_text_file(fp):
  """
  Open a text file.
  Determine how many total lines are in the text file
  Use a context manager to open the file.
  """
  try:
    with open(fp, 'r') as f:
      data = f.read()
      return len(data.splitlines())
      
  except Exception as error:
    print(f"Unable to read file: {fp} Error: {error}")
    return False
