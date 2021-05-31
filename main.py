import string
import os
import time
import fcntl
import termios
import struct
from display import Display
from devices import Plugboard, Rotor, Reflector
import wiring

screen = None
plugboard = None
rotors = []
rotor_numbers = []
reflector = Reflector(wiring.reflector_wiring)

def clear():
  if os.name == "posix":
    _ = os.system("clear")
  else:
    _ = os.system("cls")

def terminal_size():
  th, tw, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
  return tw, th

def create_rotors(rotor_1, rotor_2, rotor_3):
  global rotor_numbers
  rotor_numbers = [rotor_1, rotor_2, rotor_3]
  rotors.append(Rotor(wiring.rotor_wiring[rotor_1 - 1], wiring.rotor_turnovers[rotor_1 - 1]))
  rotors.append(Rotor(wiring.rotor_wiring[rotor_2 - 1], wiring.rotor_turnovers[rotor_2 - 1]))
  rotors.append(Rotor(wiring.rotor_wiring[rotor_3 - 1], wiring.rotor_turnovers[rotor_3 - 1]))
  rotors[2].set_next_rotor(rotors[1])
  rotors[1].set_next_rotor(rotors[0])

def reset_screen():
  global screen
  screen = Display(terminal_size()[0], 31)
  screen.fill("""
 
 
         Rotor ?     Rotor ?     Rotor ?
  UKW       ?           ?           ?       Plugboard
  ___    _______     _______     _______     _______
  """)
  for i in range(26):
    char = string.ascii_uppercase[i]
    screen.draw_text((0, i + 5), "   " + char + ("     " + char) * 8)

def update_rotor_text():
  screen.draw_text((0, 0), key_text)
  screen.draw((15, 2), str(rotor_numbers[0]))
  screen.draw((27, 2), str(rotor_numbers[1]))
  screen.draw((39, 2), str(rotor_numbers[2]))
  screen.draw((12, 3), rotors[0].position)
  screen.draw((24, 3), rotors[1].position)
  screen.draw((36, 3), rotors[2].position)

def calc_input(input, key_text="", plaintext="", prev_ciphertext=""):
  def calc_y(char):
    return string.ascii_uppercase.index(char) + 5

  # Move rotors to next position
  rotors[2].rotate()
  update_rotor_text()

  # Process through plugboard
  screen.draw_text((52, calc_y(input)), "<<< " + plaintext)
  plugboard_output = plugboard.calc(input)
  screen.draw_line_complex([(50, calc_y(input)), (49, calc_y(input)), (49, calc_y(plugboard_output)), (46, calc_y(plugboard_output))])

  # Process through rotors (forwards)
  rotor_outputs = []
  for i in range(len(rotors)):
    base_x = 33 - i * 12
    rotor_input = plugboard_output if i == 0 else rotor_outputs[i - 1]
    screen.draw_line_simple((base_x + 11, calc_y(rotor_input)), (base_x + 7, calc_y(rotor_input)))
    rotor_outputs.append(rotors[::-1][i].calc_forwards(rotor_input))
    screen.draw_line_complex([(base_x + 5, calc_y(rotor_input)), (base_x + 4, calc_y(rotor_input)), (base_x + 4, calc_y(rotor_outputs[-1])), (base_x + 1, calc_y(rotor_outputs[-1]))])

  # Process through reflector
  screen.draw_line_simple((8, calc_y(rotor_outputs[-1])), (4, calc_y(rotor_outputs[-1])))
  reflector_output = reflector.calc(rotor_outputs[-1])
  screen.draw_line_complex([(2, calc_y(rotor_outputs[-1])), (1, calc_y(rotor_outputs[-1])), (1, calc_y(reflector_output)), (2, calc_y(reflector_output))])

  # Process through rotors (backwards)
  rotor_outputs_reverse = []
  for i in range(len(rotors)):
    base_x = 9 + i * 12
    rotor_input = reflector_output if i == 0 else rotor_outputs_reverse[i - 1]
    screen.draw_line_simple((base_x - 5, calc_y(rotor_input)), (base_x - 1, calc_y(rotor_input)))
    rotor_outputs_reverse.append(rotors[i].calc_backwards(rotor_input))
    screen.draw_line_complex([(base_x + 1, calc_y(rotor_input)), (base_x + 2, calc_y(rotor_input)), (base_x + 2, calc_y(rotor_outputs_reverse[-1])), (base_x + 5, calc_y(rotor_outputs_reverse[-1]))])

  # Process through plugboard
  screen.draw_line_simple((40, calc_y(rotor_outputs_reverse[-1])), (44, calc_y(rotor_outputs_reverse[-1])))
  plugboard_output_reverse = plugboard.calc(rotor_outputs_reverse[-1])
  screen.draw_line_complex([(46, calc_y(rotor_outputs_reverse[-1])), (47, calc_y(rotor_outputs_reverse[-1])), (47, calc_y(plugboard_output_reverse)), (50, calc_y(plugboard_output_reverse))])
  screen.draw_text((52, calc_y(plugboard_output_reverse)), ">>> " + prev_ciphertext + plugboard_output_reverse)

  return plugboard_output_reverse

if __name__ == "__main__":
  key_text = ""

  # Print title
  print("          Enigma I Emulator          \n-------------------------------------")

  # Choose plugboard settings
  plugboard_wires = []
  while True:
    raw = input("Add plugboard cable or enter to continue (e.g. \"YP\"): ").upper()
    if raw == "":
      break
    plugboard_wires.append((raw[0], raw[1]))
  if len(plugboard_wires) == 0:
    key_text += "Plugboard=NA"
  else:
    key_text += "Plugboard=" + "/".join([x[0] + x[1] for x in plugboard_wires])
  plugboard = Plugboard(plugboard_wires)

  # Choose rotor arragment
  rotor_arrangement = input("Select rotor arangement (e.g. \"524\"): ")
  create_rotors(int(rotor_arrangement[0]), int(rotor_arrangement[1]), int(rotor_arrangement[2]))
  key_text += ", Arrangement=" + rotor_arrangement[:3]

  # Choose rotor positions
  rotor_positions = input("Select rotor positions (e.g. \"TKA\"): ").upper()
  rotors[0].position = rotor_positions[0]
  rotors[1].position = rotor_positions[1]
  rotors[2].position = rotor_positions[2]
  key_text += ", Positions=" + rotor_positions[:3]

  plaintext = ""
  ciphertext = ""
  reset_screen()
  update_rotor_text()
  clear()
  screen.print()
  while True:
    text = input()
    if text == "":
      plaintext = ""
      ciphertext = ""
      rotors[0].position = rotor_positions[0]
      rotors[1].position = rotor_positions[1]
      rotors[2].position = rotor_positions[2]
    else:
      valid_text = "".join([x for x in list(text.upper()) if x in string.ascii_uppercase])
      for char in valid_text:
        plaintext += char
        reset_screen()
        ciphertext += calc_input(char, key_text, plaintext.lower(), ciphertext)
        clear()
        screen.print()
        time.sleep(1)
      if len(valid_text) > 0:
        continue
    reset_screen()
    update_rotor_text()
    clear()
    screen.print()