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
    """
    Initialize a new Matrix object.

    Args:
        wait (int): The wait time between frames as percentage of normal rain speed
        glitch_freq (int): The glitch frequency as percentage of normal frequency.
        drop_freq (int): The drop frequency as a percentage of normal frequency.
        message_timer (int): The number of frames a message is displayed on the screen
        messages (List[str]): A list of message strings to be displayed.

    Attributes:
        n_rows (int): The number of rows in the matrix.
        n_cols (int): The number of columns in the matrix.
        wait (float): The wait time between frames, based on input.
        glitch_freq (float): The glitch frequency, based on input.
        drop_freq (float): The drop frequency, based on input.
        message_timer (int): The number of frames a message is displayed on the screen
        messages (List[str]): A list of message strings to be displayed.
    """
    def __init__(self, wait: int, glitch_freq: int, drop_freq: int, message_timer: int, messages: list[str]):
        self.n_rows = 0
        self.n_cols = 0

        self.wait = 0.06 / (wait / 100)
        self.glitch_freq = 0.01 * (glitch_freq / 100)
        self.drop_freq = 0.1 * (drop_freq / 100)
        self.message_timer = message_timer
        self.messages = messages.split('|')

    def __str__(self):
        """
        Generate a string representation of the Matrix object.

        Returns:
            str: A string representation of the Matrix object, suitable for printing to the terminal.

        This method generates a string representation of the Matrix object by iterating over all cells in the matrix,
        and concatenating the appropriate character and color code based on the state of each cell.

        The resulting string is then returned and can be printed to the terminal.
        """
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
        """
        Return the size of the terminal prompt to be used when creating the animation.

        Returns:
            tuple: A tuple of integers representing the height and width of the terminal prompt, in that order.

        This method returns the size of the terminal prompt by calling the `os.get_terminal_size()` function.

        The returned tuple contains the height and width of the terminal prompt, in that order. The height value is
        incremented by `max_drop_length` to account for the "dropped" portion of the Matrix.

        This method can be used to adjust the size of the Matrix object to fit the size of the terminal prompt.
        """
        size = os.get_terminal_size()

        return size.lines + max_drop_length, size.columns

    @staticmethod
    def get_random_char():
        """
        Return a random printable character.

        Returns:
            str: A string containing a random printable character.

        This method returns a random printable character by randomly selecting a codepoint from the range of ASCII
        printable characters (32 to 126) and the `special_characters` list.

        The method uses the `random.choice()` function to randomly select a codepoint from the list, and then converts
        the codepoint to a character using the `chr()` function.

        This method can be used to generate random characters for use in the Matrix object.
        """
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
        """
        Update the character, state, and length of a specific cell in the Matrix object.

        Args:
            i_row (int): The row index of the cell to update.
            i_col (int): The column index of the cell to update.
            char (str, optional): The new character for the cell. Defaults to None.
            state (int, optional): The new state for the cell. Defaults to None.
            length (int, optional): The new length for the cell. Defaults to None.

        This method updates the character, state, and length of a specific cell in the Matrix object.

        If a new character is provided, it will be set as the first element of the cell tuple.
        If a new state is provided, it will be set as the second element of the cell tuple.
        If a new length is provided, it will be set as the third element of the cell tuple.

        If any of the optional arguments are not provided, the corresponding value of the cell will not be changed.
        """
        if char is not None:
            self[i_row][i_col][0] = char

        if state is not None:
            self[i_row][i_col][1] = state

        if length is not None:
            self[i_row][i_col][2] = length

    def fill(self):
        """
        Fill the Matrix object with random characters.

        The characters are randomly selected from the printable ASCII range and the `special_characters` list.
        The state of every cell is set to `state_none`, and the length is set to 0.
        """
        self[:] = [
            [[self.get_random_char(), state_none, 0] for _ in range(self.n_cols)]
            for _ in range(self.n_rows)
        ]

    def apply_glitch(self):
        """
        Apply random glitches to the Matrix object by changing the characters in random cells.

        This method simulates the effect of random glitches on the Matrix object.

        The method calculates the total number of glitches to apply based on the `glitch_freq` attribute and the size of the Matrix.
        For each glitch, the method randomly selects a cell and sets its character to a new random value.

        Each cell normally has a 1% chance of glitching, but that can be changed when initializing a Matrix object
        """
        total = self.n_cols * self.n_rows * self.glitch_freq

        for _ in range(int(total)):  # Chooses random column and row and updates character in that cell
            i_col = random.randint(0, self.n_cols - 1)
            i_row = random.randint(0, self.n_rows - 1)

            self.update_cell(i_row, i_col, char=self.get_random_char())

    def message_glitch(self, seed: int):
        """
        Create a vertical message in a random spot on the Matrix object by updating cells.

        Args:
            seed (int): The seed value for the random number generator.

        Returns:
            tuple: A tuple containing the starting row, starting column, and length of the message.

        The method first sets the seed value for the random number generator to ensure consistent results.
        It then randomly selects a message from the `messages` attribute and a starting column and row for the message.

        The method then iterates over the length of the message, updating the character and state of each cell to form the message.
        The last cell of the message is cleared by setting its state to `state_none`.

        This method is used for displaying messages on the Matrix object in a random location.
        """
        original_state = random.getstate() # saves the original state of the random generator
        random.seed(seed) # sets a new seed for the random generator to be used in this method
        message = random.choice(self.messages)
        i_col = random.randint(0, self.n_cols - 1)
        i_row = random.randint(max_drop_length, self.n_rows - len(message) - 1)
        for i in range(len(message)+1):
            if i == len(message):
                self.update_cell(i_row+i, i_col, state=state_none) # makes last cell clear
            else:
                self.update_cell(i_row+i, i_col, char=message[i], state=state_message)
        random.setstate(original_state) # sets the random generator to original state, forgetting the seed

        return i_row, i_col, len(message)        

    def delete_message(self, i_row, i_col, message_length):
        """
        Delete a message in the Matrix object by setting the specified matrix cells to a blank state and giving them random characters.

        Args:
            i_row (int): The starting row of the message.
            i_col (int): The starting column of the message.
            message_length (int): The length of the message.

        The method iterates over the length of the message, updating the character and state of each cell to clear the message.

        This method is used for removing messages from the Matrix object.
        """
        for i in range(message_length + 1):
            self.update_cell(i_row+i, i_col, char=self.get_random_char(), state=state_none, length=0)

    def drop_col(self, i_col: int):
        """
        Drop a single column in the Matrix object by moving the characters down by one row

        Args:
            i_col (int): The column to drop.

        Returns:
            bool: A boolean value indicating if the bottom-most cell in the given column was in the "front" state.

        This method drops a single column in the Matrix object by moving the characters down by one row, starting from the bottom-most row and working its way up.

        The method first checks if the bottom-most cell in the given column has reached the "front" state, and returns this value as a boolean.

        The method then iterates over the rows of the given column, 
        moving each cell down by one row by updating the cell in the row below it with the current character, state, and length.
        The current cell is then set to the "none" state and a length of 0.

        This method is used for simulating the effect of gravity on the Matrix object.
        """
        dropped = self[self.n_rows - 1][i_col] == state_front # checking if the bottom cell in a given column has "front" state and storing it as a boolean

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
        """
        Add new drops to the Matrix object, with a specified length and starting position.

        Args:
            i_row (int): The row to start the drop at.
            i_col (int): The column to start the drop in.
            drop_length (int): The length of the drop, in characters.

        The method first iterates backwards over the length of the drop, starting from the specified row and column.

        For each cell in the drop, the method calculates the length of the tail of the drop and updates the state and length of the cell.
        The front of the drop is specified as the first cell in the drop, and has a length of 1.
        """
        for i in reversed(range(drop_length)):
            r = i_row + (drop_length - i)

            if i == 0:
                self.update_cell(r, i_col, state=state_front, length=1) # specifies the front of the drop
            else:
                l = math.ceil((total_colors - 1) * i / drop_length)
                self.update_cell(r, i_col, state=state_tail, length=l) # specifies the tail of the drop

    def screen_check(self):
        """
        Check the terminal size and adjust the Matrix object size if necessary.

        This method checks the terminal size and adjusts the Matrix object size if necessary.

        If the terminal size has changed, the method sets the `n_rows` and `n_cols` attributes of the Matrix object to the new terminal size,
        and then fills the Matrix object with random characters.

        This method is used for ensuring that the Matrix object fits within the terminal window.
        """
        if (prompt_size := self.get_prompt_size()) != (self.n_rows, self.n_cols):
            self.n_rows, self.n_cols = prompt_size
            self.fill()

    def update(self):
        """
        Update the Matrix object by dropping columns and adding new drops.

        This method updates the Matrix object by dropping columns and adding new drops, based on the `drop_freq` attribute.

        The method first drops all columns and counts the number of drops that reached the end of the Matrix object.
        It then calculates the total number of drops that should be in the Matrix object based on the `drop_freq` attribute
        and calculates the number of missing drops needed to reach this total.

        The method then adds the calculated number of missing drops to random columns, with a random length.
        """
        dropped = sum(self.drop_col(i_col) for i_col in range(self.n_cols)) # drops all columns, sums number of drops that reached the end

        total = self.n_cols * self.n_rows * self.drop_freq # total number of drops that should be in the matrix based on the drop_freq attribute
        missing = math.ceil((total - dropped) / self.n_cols) # number of missing drops needed to reach the total number of drops.

        for _ in range(missing): # add number of missing drops to random columns
            i_col = random.randint(0, self.n_cols - 1)
            length = random.randint(min_drop_length, max_drop_length)

            self.add_drop(0, i_col, length)

    def start(self):
        """
        Starts the animation loop, continuously updating and rendering the Matrix object.

        The method uses a while loop to render the Matrix object, with a delay between iterations based on the `wait` attribute.

        During each iteration, the method checks the terminal size, updates the Matrix object, and displays a message in the terminal for a specified number of iterations.
        It also applies glitches to the Matrix object and deletes any existing message in the terminal.
        """
        iteration = 0
        seed = None

        while True:
            print(clear_char, end="")
            print(self, end="", flush=True) # flush = True immidiately prints buffered text when prints calles, needed when using end = ""
            self.screen_check()
            
            self.update()

            if iteration == 0: 
                seed = random.randint(0, 1000) # Generates a new random seed

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
    messages: str = typer.Option(
        "EmBRacE the coDe, FEAr the an0m@ly.| REality is a lie, W@k3 up.| ThE syStEm is w@tchinG, alwaYs.| SurReND3R to thE b1n@ry abYss.| Unr@v3l the illUsion, find th3 truTH.",
        "--messages", "-m", help="Subliminal messages to be displayed in the animation, separated by |"
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

    matrix = Matrix(speed, glitches, frequency-70, message_timer, messages) # can also adjust parameters here
    matrix.start()


if __name__ == "__main__":
    app()
# adjust terminal size to be large enough before running