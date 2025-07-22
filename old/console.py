
import os
def bold(text):
    """Return text formatted in bold."""
    return f'\x1b[1m{text}\x1b[0m'
def uline(text):
    """Return text formatted with underline."""
    return f'\x1b[4m{text}\x1b[0m'
def italic(text):
    """Return text formatted in italic."""
    return f'\x1b[3m{text}\x1b[0m'
def show_cursor(val):
    """Show or hide the cursor in the console."""
    if val:
        print('\033[?25h', end='')
    else:
        print('\033[?25l', end='')

def hcenter(text, width=None, char=' ', mode = 0):
    """Center text in a given width with a specified character."""
    if width is None:
        width = os.get_terminal_size().columns
    text = str(text)
    text_lines = text.split('\n')
    res = ''
    for line in text_lines:
        if mode == 0:
            while LineLength(line) < width:
                if len(line) % 2 == 0:
                    line = char + line 
                else:
                    line = line + char
        elif mode == 1:
            line = " "*(width - LineLength(line)) + line 
        elif mode == 2:
             line =  line + " "*(width - LineLength(line))
        res += line + '\n'
    return res.rstrip('\n')

def LineLength(text):
    count = 0
    open = False
    for char in text:
        if (char == '\x1b'):
            open = True
        elif (char == 'm' and open):
            open = False
        elif (not open):
            count += 1
    return count

def getMaxWidth(textArray: list) -> int:
    max_width = 0
    for line in textArray:
        if LineLength(line) > max_width:
            max_width = LineLength(line)
    return max_width

def mergeLines(sprite1:str, sprite2:str, padding=4):
    lines1 = sprite1.split('\n')
    #lines1_len = lines1.reduce(lambda x, y: max(x, len(y)), 0)
    line1_len= getMaxWidth(lines1)
    lines2 = sprite2.split('\n')
    lines2_len = getMaxWidth(lines2)
    max_lines = max(len(lines1), len(lines2))
    merged_lines = []
    for i in range(max_lines):
        line1 = lines1[i] if i < len(lines1) else ''
        line2 = lines2[i] if i < len(lines2) else ''
        line1 = hcenter(line1, line1_len, ' ', 0)
        line2 = hcenter(line2, lines2_len, ' ', 0)
        merged_line = line1 + ' ' * padding + line2
        merged_lines.append(merged_line)
    merged_sprite = '\n'.join(merged_lines)
    return merged_sprite

def clear_screen():
    print('\033[2J\033[3J\033[H', end='')

def insert_color(text, color):
    res = f"\x1b[{color}m{text}"
    res = res.replace("\x1b[0m",f"\x1b[0m\x1b[{color}m") 
    return f"{res}\x1b[0m"

def home():
    print('\033[1;1H', end='')
    pass

def line():
    """Print a horizontal line across the console."""
    print('\033[1;30m' + '#' * os.get_terminal_size().columns + '\x1b[0m', end='')
def hprint(text, mode= 0):
    """Print text centered in the console."""
    print(hcenter(text,mode=mode, width=os.get_terminal_size().columns), end='\033[0k\n')
def fprint(text):
    """Print text and clear the rest of the line."""
    hprint(text, 2)
def fow_clear():
    print('\033[J', end='')
arrowLeft = "←"
arrowRight = "→"
arrowUp = "↑"
arrowDown = "↓"
arrowUpDown = "↕"
arrowLeftRight = "↔"
nullSideArrow = "⥙"
sNodeLink = "\n\n--" + arrowRight + "\n\n\n\n" 
DoubleLink = "\n\n--" + arrowRight +"\n" + arrowLeft  +"--\n\n\n" 
sNodeRightLinkNull = "\n\n-+\n  | \n " + nullSideArrow + "\n\n"
sNodeLeftLinkNull = "\n\n +-\n | \n " + nullSideArrow + " \n\n"
