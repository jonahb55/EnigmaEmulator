import string

# Shifts a letter by the specified value along the alphabet
def shift_char(input, shift):
  char_index = string.ascii_uppercase.index(input) + shift
  while char_index > 25:
    char_index -= 26
  while char_index < 0:
    char_index += 26
  return string.ascii_uppercase[char_index]

class Plugboard:
  __wiring = [] # List of tuples with pairs of letters to swap

  def __init__(self, wiring):
    self.__wiring = wiring

  def calc(self, input):
    for wire in self.__wiring:
      if wire[0] == input:
        return wire[1]
      if wire[1] == input:
        return wire[0]
    return input

class Rotor:
  position = "A"
  __wiring = string.ascii_uppercase # List of 26 characters after scrambling
  __turnover = "A"
  __next_rotor = None

  def __init__(self, wiring, turnover):
    if turnover in string.ascii_uppercase:
      self.__turnover = turnover

    if len(wiring) != 26:
      return
    for wire in wiring:
      if wire not in string.ascii_uppercase:
        return
    self.__wiring = wiring

  def set_next_rotor(self, next_rotor):
    self.__next_rotor = next_rotor
    
  def rotate(self):
    self.position = shift_char(self.position, 1)

    # Trigger turnover
    if self.__next_rotor != None and self.position == shift_char(self.__turnover, 1):
      self.__next_rotor.rotate()

  def calc_forwards(self, input):
    position_shift = string.ascii_uppercase.index(self.position)
    normalized_input = shift_char(input, position_shift)
    normalized_output = self.__wiring[string.ascii_uppercase.index(normalized_input)]
    return shift_char(normalized_output, position_shift * -1)

  def calc_backwards(self, input):
    position_shift = string.ascii_uppercase.index(self.position)
    normalized_input = shift_char(input, position_shift)
    normalized_output = string.ascii_uppercase[self.__wiring.index(normalized_input)]
    return shift_char(normalized_output, position_shift * -1)

class Reflector:
  __wiring = string.ascii_uppercase # List of 26 characters after scrambling

  def __init__(self, wiring):
    if len(wiring) != 26:
      return
    for wire in wiring:
      if wire not in string.ascii_uppercase:
        return
    self.__wiring = wiring

  def calc(self, input):
    return self.__wiring[string.ascii_uppercase.index(input)]