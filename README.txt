SPACE INVADERS
==============

ABOUT THE GAME
--------------
Space Invaders is a small, single-player arcade game written in Python. Move
the purple ship along the bottom of the screen and shoot the incoming alien
formation. Clear every alien to begin the next wave. Each alien destroyed
earns 10 points.

The aliens move back and forth across the screen and descend when they reach
an edge. They also fire at the player. The game ends if an alien reaches the
player's area or an alien bullet hits the ship. The score and wave number are
shown during play; the final score and last wave are shown on the game-over
screen.

CONTROLS
--------
During the game:
  Left Arrow or A     Move left
  Right Arrow or D    Move right
  Spacebar            Fire

On the welcome screen, press any key or click the window to start.
On the game-over screen:
  R                   Start a new game
  Escape              Exit
  Click "PLAY AGAIN"  Start a new game
  Click "EXIT"        Exit

The ship moves while a movement key is held. Keep holding Spacebar to fire
repeatedly; shots have a short cooldown.

RUNNING THE GAME
----------------
1. Make sure Python 3.9 or later is installed.
2. Open a terminal in the folder containing game.py.
3. Run:

     python game.py

On Windows, if the python command is not available, try:

     py game.py

The game opens in its own desktop window. Close the window to exit at any
time.

IMPORTANT NOTES
---------------
- The game uses tkinter, Python's standard GUI library. No third-party
  packages are required. Some Linux installations may require installing
  the system's tkinter package separately.
- The game window has a fixed size of 800 by 600 pixels and cannot be resized.
- There is no pause button or extra-life system. A hit ends the current game.
- Starting a new game resets the score and returns to wave 1.
- The game loop updates approximately 60 times per second. Actual smoothness
  depends on the computer and desktop environment.
