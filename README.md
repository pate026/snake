# Snake

A classic Snake game for the terminal, written in Python with the standard
library `curses` module. There are no third-party runtime dependencies.

## Requirements

- Python 3.10 or newer
- A terminal that is at least 30 columns wide and 15 rows tall
- Linux or macOS (the `curses` module is not bundled with Python on Windows)

## Run the game

```sh
cd snake
python main.py
```

## Controls

| Key            | Action                          |
| -------------- | ------------------------------- |
| Arrow keys     | Move the snake                  |
| `W` `A` `S` `D`| Move the snake                  |
| `p`            | Pause or resume                 |
| `q`            | Quit                            |
| `r`            | Restart after game over         |
| `Ctrl+C`       | Quit and restore the terminal   |

The snake cannot reverse directly into itself. Eating food grows the snake by
one segment and adds 10 points. The game speeds up every 50 points, down to a
minimum delay so it stays playable. The game ends when the snake hits a wall or
its own body.

The score and the best score are shown at the top of the screen. The high score
is stored in `highscore.txt` in the project folder and is created automatically.

## Run the tests

```sh
cd snake
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Project layout

```
snake/
├── main.py              # entry point
├── snake/
│   ├── __init__.py
│   ├── game.py          # pure game logic (no terminal code)
│   └── ui.py            # curses drawing, input and high score file
├── tests/
│   └── test_game.py     # pytest tests for game.py
├── requirements-dev.txt # pytest
├── .gitignore
└── README.md
```

`game.py` holds all of the rules and can be tested without a terminal. `ui.py`
handles drawing, keyboard input, pause, the game over screen, restart and the
small-terminal message.
