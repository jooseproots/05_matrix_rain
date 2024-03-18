import math
import os
import random
import time

import typer

# Initializing cli
app = typer.Typer()

BLANK_CHAR = " "
CLEAR_CHAR = "\x1b[H"

# Drop state of each cell, specifies position in a "raindrop"
STATE_NONE = 0
STATE_FRONT = 1
STATE_TAIL = 2

# Drop lengths
MIN_LEN = 5
MAX_LEN = 12

# Drop colours
BODY_CLRS = [
    "\x1b[38;5;48m",
    "\x1b[38;5;41m",
    "\x1b[38;5;35m",
    "\x1b[38;5;238m",
]
FRONT_CLR = "\x1b[38;5;231m"
TOTAL_CLRS = len(BODY_CLRS)

class Matrix(list):
    def __init__(self, wait: int, glitch_freq: int, drop_freq: int):
        self.rows = 0
        self.cols = 0

        self.wait = 0.06 / (wait / 100)
        self.glitch_freq = 0.01 / (glitch_freq / 100)
        self.drop_freq = 0.1 * (drop_freq / 100)

    def __str__(self):
        '''returns a string representation of the matrix, which is then printed to the terminal.'''
        text = ""

        for (c, s, l) in sum(self[MAX_LEN:], []):
            if s == STATE_NONE:
                text += BLANK_CHAR
            elif s == STATE_FRONT:
                text += f"{FRONT_CLR}{c}"
            else:
                text += f"{BODY_CLRS[l]}{c}"

        return text

    def get_prompt_size(self):
        '''returns the size of the terminal prompt, which is used to adjust the matrix size if necessary.'''
        size = os.get_terminal_size()

        return size.lines + MAX_LEN, size.columns

    @staticmethod
    def get_random_char():
        return chr(random.choice([random.randint(32, 126), 9906, 985, 1993, 11439, 9880, 11801, 10047, 10048, 9753, 10086, 10087, 1126]))

    def update_cell(
        self,
        r: int,
        c: int,
        *,
        char: str = None,
        state: int = None,
        length: int = None,
    ):
        '''updates the character, state, and length of a specific cell in the matrix.'''
        if char is not None:
            self[r][c][0] = char

        if state is not None:
            self[r][c][1] = state

        if length is not None:
            self[r][c][2] = length

    def fill(self):
        '''fills the matrix with random characters.'''
        self[:] = [
            [[self.get_random_char(), STATE_NONE, 0] for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

    def apply_glitch(self):
        '''applies random glitches to the matrix by changing the characters in random cells.'''
        total = self.cols * self.rows * self.glitch_freq

        for _ in range(int(total)):  # Chooses random column and row and updates character in that cell
            c = random.randint(0, self.cols - 1)
            r = random.randint(0, self.rows - 1)

            self.update_cell(r, c, char=self.get_random_char())

    def message_glitch(self, seed: int):
        '''creates a vertical message in a random spot on the terminal by updating cells.
        Also returns the starting position (row and column) and the length of the message'''
        random.seed(seed)
        message = "Hello World"
        c = random.randint(0, self.cols - 1)
        r = random.randint(MAX_LEN, self.rows - len(message) - 1)
        for i in range(len(message)+1):
            if i == len(message):
                self.update_cell(r+i, c, state=0)
            else:
                self.update_cell(r+i, c, char=message[i], state=1)

        return r, c, len(message)        

    def delete_message(self, r, c, message_length):
        '''deletes a message in the terminal by setting the specified matrix cells 
        to a blank state and giving them random characters'''
        for i in range(message_length + 1):
            self.update_cell(r+i, c, char=self.get_random_char(), state=0)

    def drop_col(self, col: int):
        '''drops a single column in the matrix by moving the characters down by one row, starting from the bottom-most row and working its way up.
        It also returns a boolean value indicating if the bottom-most cell in the given column was in the "front" state.'''
        dropped = self[self.rows - 1][col] == STATE_FRONT # checking if the bottom-most cell in a given column has reached the "front" state and storing it as a boolean

        for r in reversed(range(self.rows)): 
            _, state, length = self[r][col]

            if state == STATE_NONE:
                continue

            if r != self.rows - 1: 
                self.update_cell(r + 1, col, state=state, length=length) 
                # move the cell down by one row by updating the cell in the row below it with the current character, state, and length.

            self.update_cell(r, col, state=STATE_NONE, length=0) # Set the current cell to the "none" state and a length of 0.

        return dropped

    def add_drop(self, row: int, col: int, length: int):
        '''adds new drops to the matrix, with a specified length and random starting position.'''
        for i in reversed(range(length)):
            r = row + (length - i)

            if i == 0:
                self.update_cell(r, col, state=STATE_FRONT, length=length) # specifies the front of the drop
            else:
                l = math.ceil((TOTAL_CLRS - 1) * i / length)

                self.update_cell(r, col, state=STATE_TAIL, length=l) # specifies the tail of the drop

    def screen_check(self):
        '''checks the terminal size and adjusts the matrix size if necessary.'''
        if (p := self.get_prompt_size()) != (self.rows, self.cols):
            self.rows, self.cols = p
            self.fill()

    def update(self):
        '''updates the matrix by dropping columns and adding new drops.'''
        dropped = sum(self.drop_col(c) for c in range(self.cols)) # drops all columns, sums number of drops that reached the end

        total = self.cols * self.rows * self.drop_freq # total number of drops that should be in the matrix based on the drop_freq attribute
        missing = math.ceil((total - dropped) / self.cols) # number of missing drops needed to reach the total number of drops.

        for _ in range(missing): # add number of missing drops to random columns
            col = random.randint(0, self.cols - 1)
            length = random.randint(MIN_LEN, MAX_LEN)

            self.add_drop(0, col, length)

    def start(self):
        '''starts the animation loop, continuously updating and rendering the matrix.'''
        iterations = 0
        seed = None
        message_time = 20

        while True:
            print(CLEAR_CHAR, end="")
            print(self, end="", flush=True)

            self.screen_check()
            
            self.update()

            if iterations == 0: 
                seed = random.randint(0, 1000)  # Generates a new random seed

            if iterations <= message_time - 1: # Displays a message in the terminal for 'message_time' number of iterations
                r, c, message_length = self.message_glitch(seed=seed) 
            else:
                self.delete_message(r, c, message_length)

            time.sleep(self.wait) # Time until new iteration
            iterations += 1
            iterations %= message_time + 1 # Resets iterations counter after specified number


@app.command() # makes start() a callable command for the Typer CLI application.
def start(
    speed: int = typer.Option(
        100, "--speed", "-s", help="Percentage of normal rain speed"
    ),
    glitches: int = typer.Option(
        100, "--glitches", "-g", help="Percentage of normal glitch amount"
    ),
    frequency: int = typer.Option(
        100, "--frequency", "-f", help="Percentage of normal drop frequency"
    ),
):
    """Start the matrix rain"""

    # Argument validation
    for arg in (speed, glitches, frequency):
        if not 0 <= arg <= 1000:
            raise typer.BadParameter("must be between 1 and 1000")

    matrix = Matrix(speed, glitches, frequency-50)
    matrix.start()


if __name__ == "__main__":
    app()
