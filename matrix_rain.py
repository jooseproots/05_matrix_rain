import math
import os
import random
import time

import typer

# Initializing cli
app = typer.Typer()

blank_char = " "
clear_char = "\x1b[H"

# Drop state of each cell, specifies position in a "raindrop"
state_none = 0
state_front = 1
state_tail = 2
state_message = 3

# Drop lengths
min_drop_length = 5
max_drop_length = 12

# Drop colours
body_colors = [
    "\x1b[38;5;48m",
    "\x1b[38;5;41m",
    "\x1b[38;5;35m",
    "\x1b[38;5;238m",
]
front_color = "\x1b[38;5;231m"
total_colors = len(body_colors)

class Matrix(list):
    def __init__(self, wait: int, glitch_freq: int, drop_freq: int, message_timer: int, messages: list[str]):
        self.n_rows = 0
        self.n_cols = 0

        self.wait = 0.06 / (wait / 100)
        self.glitch_freq = 0.01 / (glitch_freq / 100)
        self.drop_freq = 0.1 * (drop_freq / 100)
        self.message_timer = message_timer
        self.messages = messages

    def __str__(self):
        '''returns a string representation of the matrix, which is then printed to the terminal.'''
        text = ""

        for (char, state, length) in sum(self[max_drop_length:], []): # iterates over all cells
            if state == state_none:
                text += blank_char
            elif state == state_front:
                text += f"{front_color}{char}"
            elif state == state_tail:
                text += f"{body_colors[length]}{char}"
            else:
                text += f"{body_colors[1]}{char}"

        return text

    def get_prompt_size(self):
        '''returns the size of the terminal prompt, which is used to adjust the matrix size if necessary.'''
        size = os.get_terminal_size()

        return size.lines + max_drop_length, size.columns

    @staticmethod
    def get_random_char():
        special_characters = [9906, 985, 1993, 11439, 9880, 11801, 10047, 10048, 9753, 10086, 10087, 1126]
        return chr(random.choice([random.randint(32, 126)] + special_characters))

    def update_cell(
        self,
        i_row: int,
        i_col: int,
        *,
        char: str = None,
        state: int = None,
        length: int = None,
    ):
        '''updates the character, state, and length of a specific cell in the matrix.'''
        if char is not None:
            self[i_row][i_col][0] = char

        if state is not None:
            self[i_row][i_col][1] = state

        if length is not None:
            self[i_row][i_col][2] = length

    def fill(self):
        '''fills the matrix with random characters.'''
        self[:] = [
            [[self.get_random_char(), state_none, 0] for _ in range(self.n_cols)]
            for _ in range(self.n_rows)
        ]

    def apply_glitch(self):
        '''applies random glitches to the matrix by changing the characters in random cells.'''
        total = self.n_cols * self.n_rows * self.glitch_freq

        for _ in range(int(total)):  # Chooses random column and row and updates character in that cell
            i_col = random.randint(0, self.n_cols - 1)
            i_row = random.randint(0, self.n_rows - 1)

            self.update_cell(i_row, i_col, char=self.get_random_char())

    def message_glitch(self, seed: int):
        '''creates a vertical message in a random spot on the terminal by updating cells.
        Also returns the starting position (row and column) and the length of the message'''
        random.seed(seed)
        message = random.choice(self.messages)
        i_col = random.randint(0, self.n_cols - 1)
        i_row = random.randint(max_drop_length, self.n_rows - len(message) - 1)
        for i in range(len(message)+1):
            if i == len(message):
                self.update_cell(i_row+i, i_col, state=state_none) # makes last cell clear
            else:
                self.update_cell(i_row+i, i_col, char=message[i], state=state_message)

        return i_row, i_col, len(message)        

    def delete_message(self, i_row, i_col, message_length):
        '''deletes a message in the terminal by setting the specified matrix cells 
        to a blank state and giving them random characters'''
        for i in range(message_length + 1):
            self.update_cell(i_row+i, i_col, char=self.get_random_char(), state=state_none, length=0)

    def drop_col(self, i_col: int):
        '''drops a single column in the matrix by moving the characters down by one row, starting from the bottom-most row and working its way up.
        It also returns a boolean value indicating if the bottom-most cell in the given column was in the "front" state.'''
        dropped = self[self.n_rows - 1][i_col] == state_front # checking if the bottom-most cell in a given column has reached the "front" state and storing it as a boolean

        for i_row in reversed(range(self.n_rows)): 
            _, state, length = self[i_row][i_col]

            if state == state_none:
                continue

            if i_row != self.n_rows - 1: 
                self.update_cell(i_row + 1, i_col, state=state, length=length) 
                # move the cell down by one row by updating the cell in the row below it with the current character, state, and length.

            self.update_cell(i_row, i_col, state=state_none, length=0) # Set the current cell to the "none" state and a length of 0.

        return dropped

    def add_drop(self, i_row: int, i_col: int, drop_length: int):
        '''adds new drops to the matrix, with a specified length and random starting position.'''
        for i in reversed(range(drop_length)):
            r = i_row + (drop_length - i)

            if i == 0:
                self.update_cell(r, i_col, state=state_front, length=1) # specifies the front of the drop
            else:
                l = math.ceil((total_colors - 1) * i / drop_length)
                self.update_cell(r, i_col, state=state_tail, length=l) # specifies the tail of the drop

    def screen_check(self):
        '''checks the terminal size and adjusts the matrix size if necessary.'''
        if (prompt_size := self.get_prompt_size()) != (self.n_rows, self.n_cols):
            self.n_rows, self.n_cols = prompt_size
            self.fill()

    def update(self):
        '''updates the matrix by dropping columns and adding new drops.'''
        dropped = sum(self.drop_col(i_col) for i_col in range(self.n_cols)) # drops all columns, sums number of drops that reached the end

        total = self.n_cols * self.n_rows * self.drop_freq # total number of drops that should be in the matrix based on the drop_freq attribute
        missing = math.ceil((total - dropped) / self.n_cols) # number of missing drops needed to reach the total number of drops.

        for _ in range(missing): # add number of missing drops to random columns
            i_col = random.randint(0, self.n_cols - 1)
            length = random.randint(min_drop_length, max_drop_length)

            self.add_drop(0, i_col, length)

    def start(self):
        '''starts the animation loop, continuously updating and rendering the matrix.'''
        iteration = 0
        seed = None

        while True:
            print(clear_char, end="")
            print(self, end="", flush=True)

            self.screen_check()
            
            self.update()

            if iteration == 0: 
                seed = random.randint(0, 1000)  # Generates a new random seed

            if iteration <= self.message_timer - 1: # Displays a message in the terminal for 'message_time' number of iterations
                r, c, message_length = self.message_glitch(seed=seed) 
            else:
                self.delete_message(r, c, message_length)

            self.apply_glitch()

            iteration += 1
            iteration %= self.message_timer + 1 # Resets iterations counter after specified number
            time.sleep(self.wait) # Time until new iteration


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
    message_timer: int = typer.Option(
        20, "--message_timer", "-t", help="Number of iterations when static message is displayed in the animation"
    ),
    messages: list[str] = typer.Option(
        ["EmBRacE the coDe, FEAr the an0m@ly.",
        "REality is a lie, W@k3 up.",
        "ThE syStEm is w@tchinG, alwaYs.", 
        "SurReND3R to thE b1n@ry abYss.", 
        "Unr@v3l the illUsion, find th3 truTH."],
        "--messages", "-m", help="List of subliminal messages to be displayed in the animation"
    )
):
    """Start the matrix rain"""

    # Argument validation
    for arg in (speed, glitches, frequency, message_timer):
        if not 0 <= arg <= 1000:
            raise typer.BadParameter("must be between 1 and 1000")
        
    # Messages validation
    for message in messages:
        if not 0 <= len(message) <= 40:
            raise typer.BadParameter("message too long to display")

    matrix = Matrix(speed, glitches, frequency, message_timer+20, messages)
    matrix.start()


if __name__ == "__main__":
    app()
# adjust terminal size to be large enough before running