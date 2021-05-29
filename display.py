class Display:
  __connector_lookup = {
    (0, 0): "|",
    (0, 1): "\\",
    (0, 2): "|",
    (0, 3): "/",
    (1, 0): "\\",
    (1, 1): "-",
    (1, 2): "/",
    (1, 3): "-",
    (2, 0): "|",
    (2, 1): "/",
    (2, 2): "|",
    (2, 3): "\\",
    (3, 0): "/",
    (3, 1): "-",
    (3, 2): "\\",
    (3, 3): "-",
  }

  def __init__(self, width=1, height=1):
    self.__width = width
    self.__height = height
    self.__lines = [[" " for i in range(width)] for j in range(height)] 

  def print(self):
    for line in self.__lines:
      print("".join(line))

  def draw(self, pos, char):
    x = pos[0]
    y = pos[1]
    if x != None and y != None and char != None:
      if -1 < x < self.__width and -1 < y < self.__height and len(char) == 1:
        self.__lines[y][x] = char

  def fill(self, text):
    fill_lines = [x for x in text.split("\n") if x != ""][:self.__height]
    for i in range(len(fill_lines)):
      fill_line = fill_lines[i][:self.__width]
      while len(fill_line) < self.__width:
        fill_line += " "
      self.__lines[i] = list(fill_line)

  def draw_text(self, pos, text):
    for i in range(len(text)):
      self.draw((pos[0] + i, pos[1]), text[i])

  def draw_line_simple(self, pos1, pos2):
    x1 = pos1[0]
    y1 = pos1[1]
    x2 = pos2[0]
    y2 = pos2[1]
    if x1 != x2 and y1 != y2:
      return
    if x1 == x2 and y1 == y2:
      return
    if x1 == x2:
      for y in range(min(y1, y2), max(y1, y2) + 1):
        self.draw((x1, y), "|")
    if y1 == y2:
      for x in range(min(x1, x2), max(x1, x2) + 1):
        self.draw((x, y1), "-")

  def draw_line_complex(self, positions):
    # Draw base lines
    for i in range(len(positions) - 1):
      self.draw_line_simple(positions[i], positions[i + 1])

    # Draw connectors
    for i in range(1, len(positions) - 1):
      current = positions[i]

      prev = positions[i - 1]
      if prev[0] != current[0] and prev[1] != current[1]:
        continue
      if prev[0] == current[0] and prev[1] == current[1]:
        continue
      if prev[0] == current[0]:
        prev_direction = 2 if prev[1] > current[1] else 0
      if prev[1] == current[1]:
        prev_direction = 1 if prev[0] > current[0] else 3

      next = positions[i + 1]
      if next[0] != current[0] and next[1] != current[1]:
        continue
      if next[0] == current[0] and next[1] == current[1]:
        continue
      if next[0] == current[0]:
        next_direction = 2 if next[1] > current[1] else 0
      if next[1] == current[1]:
        next_direction = 1 if next[0] > current[0] else 3
      
      self.draw(current, self.__connector_lookup[(prev_direction, next_direction)])