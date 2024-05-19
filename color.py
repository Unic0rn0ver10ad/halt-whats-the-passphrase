# MODULES
from colorama import init, Fore, Back, Style


class Color:
  def __init__(self):
    init(autoreset=True)

  def p(self, text, color_str=None):
    # currently can only change foreground 'f' color
    # Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    # Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    # Style: DIM, NORMAL, BRIGHT, RESET_ALL
    try:
      color_str = color_str.lower()
    except:
      pass
    
    if color_str == 'red':
      return(self.color('RED', 'f') + text)
    elif color_str == 'green':
      return(self.color('GREEN', 'f') + text)
    elif color_str == 'blue':
      return(self.color('BLUE', 'f') + text)
    elif color_str == 'yellow':
      return(self.color('YELLOW', 'f') + text)
    elif color_str == 'magenta':
      return(self.color('MAGENTA', 'f') + text)
    elif color_str == 'cyan':
      return(self.color('CYAN', 'f') + text)
    elif color_str == 'white':
      return(self.color('WHITE', 'f') + text)
    else:
      return(self.color('RESET_ALL', 's') + text)

  def color(self, color_str, fbs='f'):
    try:
      color_str = color_str.upper()
    except:
      pass
    fbs = fbs.lower()
    if color_str == 'BLACK':
      if fbs == 'f':
        return Fore.BLACK
      elif fbs == 'b':
        return Back.BLACK
    elif color_str == 'RED':
      if fbs == 'f':
        return Fore.RED
      elif fbs == 'b':
        return Back.RED
    elif color_str == 'GREEN':
      if fbs == 'f':
        return Fore.GREEN
      elif fbs == 'b':
        return Back.GREEN
    elif color_str == 'YELLOW':
      if fbs == 'f':
        return Fore.YELLOW
      elif fbs == 'b':
        return Back.YELLOW
    elif color_str == 'BLUE':
      if fbs == 'f':
        return Fore.BLUE
      elif fbs == 'b':
        return Back.BLUE
    elif color_str == 'MAGENTA':
      if fbs == 'f':
        return Fore.MAGENTA
      elif fbs == 'b':
        return Back.MAGENTA
    elif color_str == 'CYAN':
      if fbs == 'f':
        return Fore.CYAN
      elif fbs == 'b':
        return Back.CYAN
    elif color_str == 'WHITE':
      if fbs == 'f':
        return Fore.WHITE
      elif fbs == 'b':
        return Back.WHITE
    elif color_str == 'DIM':
      return Style.DIM
    elif color_str == 'NORMAL':
      return Style.NORMAL
    elif color_str == 'BRIGHT':
      return Style.BRIGHT
    else:
      if fbs == 'f':
        return Fore.RESET
      elif fbs == 'b':
        return Back.RESET
      elif fbs == 's':
        return Style.RESET_ALL

  def banner(self, text1, text2, text3, color1=None, color2=None, color3=None, color=True):
    text_len = len(text2 + text3)
    """
    =================
    This is a Banner!
    =================
    """
    bar = text1 * text_len
    print(self.color(color1) + bar)
    print(self.color(color2) + text2 + self.color(color3) + text3)
    print(self.color(color1) + bar)

  def arrow(self, text1, text2, text3, color1=None, color2=None, color3=None):
    """
    ===> This is an Arrow!
    """
    print(self.color(color1) + text1 + self.color(color2) + text2 + self.color(color3) + text3)
