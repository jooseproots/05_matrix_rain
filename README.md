# Matrix rain animation

## Description
The aim of this project is to use an existing script for a digital rain effect from The Matrix, refactor it and add forestry related symbols and messages to it.

The script creates a digital rain animation in the terminal with customizable parameters 

## Features

- Simulates falling raindrops represented by characters in a terminal window.
- Random glitches add visual effects to the animation.
- Displays subliminal messages intermittently throughout the animation.
- Customizable parameters including rain speed, glitch frequency, drop frequency, message display duration, and messages themselves.

## Installation

1. Ensure you have Python installed on your system.
2. Install the required dependencies by running: `pip install typer`
3. Download the Python script (`matrix_rain.py`) from this repository.

## Usage

Adjust the terminal size to fit the messages and run the script or run the following command in your terminal to start the matrix rain animation:

`python matrix_rain.py`

You can also customize the animation parameters using optional flags:

- `--speed`: Percentage of normal rain speed (default: 100).
- `--glitches`: Percentage of normal glitch amount (default: 100).
- `--frequency`: Percentage of normal drop frequency (default: 100).
- `--message_timer`: Number of iterations when a static message is displayed in the animation (default: 20).
- `--messages`: Subliminal messages to be displayed in the animation, separated by `|` (default messages provided).

Example usage with custom parameters:

`python matrix_rain.py --speed 80 --frequency 90 --messages "Message 1| Message 2| Message 3"`

Parameters can also be adjusted at the end of the code. 

For extra help run:

`python matrix_rain.py --help`