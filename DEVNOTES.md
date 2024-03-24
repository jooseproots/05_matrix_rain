### 10.03.2024

Original scripts runs, also works with different terminal sizes

ord() function can be used to find corresponding Unicode character number used in chr()

Unicode displays in terminal, emojis display but script stops working properly

possible characters: ⚲, ϙ, ߉, ⲯ, ⚘, ⸙, ✿, ❀, ☙, ❦, ❧, Ѧ

### 11.03.2024

emoji package also doesn’t work for showing emojis in terminal

many text characters turn to emoji, Unicode [text presentation selector](http://www.unicode.org/reports/tr51/#def_text_presentation_selector) FE0E can be used in JavaScript and HTML to force text vs emoji, but it doesn’t seen to work in python. 

- added forestry symbols to matrix rain

### 12.03.2024

using @staticmethod means the method is bound to the class and can be called without creating an instance of the class. It does not receive a **`self`** parameter and does not have access to the instance variables of the class.

- created docstrings for Matrix class methods
- added comments to some methods for clarity

:= operator allows to define a variable within an expression, example: 

```python
num = 15
print(num)

#same as

print(num := 15)

```

### 13.03.2024

- experimented with adding messages to the script, didn’t work yet

### 18.03.2024

Could add subliminal messages by adding method similar to `drop_col()`?

- `drop_col()` as a message dropper works, have to give message backwards

`apply_glitch()` stops working when dropping only messages, because then visible characters will always be the message. Also difficult to implement in addition to regular drops.

Maybe better to add static message?

- created `message_glitch()` method to display static messages.

Static messages are not immune to column drops, should display message at certain spot for a few iterations, then disappear.

- Added random seed generator to `start()` method that is passed on to `message_glitch()` method for choosing the location of the message. The seed stays the same for a certain number of iterations to display static messages for a longer time.
- Created `delete_message()` method to remove the message from the display (changes all characters to random and sets their state to blank)
- Added `delete_message()` to `start()`method so now a message is created for a specified number of iterations and deleted after that.

→ this created a bug where drops sometimes have large front sections of white letters.

→ bug where animation does not display on small terminal sizes, probably due to messages not being able to display if they don’t fit in the terminal

To-do: add different messages, apply regular glitches as well

- added different subliminal messages that randomly appear and disappear

### 19.03.2024

- added option to choose the time a message is displayed when initializing the matrix

→ when messages are displayed for shorter times then drops do not get long front sections of white letters, 

- added list of subliminal to be displayed as an option when initializing the matrix
- added extra cell state for displaying messages, to be able to change message color.
- created loop to check that subliminal messages are not too long to display.
- put back regular glitches as well

→ long front sections of drops has the same length as `message_timer`, why? Also frequency of drops changes when `message_timer` changes. Looks like update only runs after time specified in `message_timer`.

- updated variable names

### 20.03.2024

- created better doctrings for methods

### 24.03.2024

→ bug with `message_timer` probably because of seed

`random.getstate()` and `random.setstate()` methods can be used to save and restore the state of a random generator. Using these methods a certain seed could only be used in a snippet of code and not anywhere else.

- fixed bug of long front sections and frequency of drops by using `random.getstate()` and `random.setstate()`to specify the seed only for the `message_glitch()` method.

- added `split(|)` method to messages so `--messages` parameter could be used properly when initializing the animation.
