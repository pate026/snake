# Task: Terminal Snake game in Python

You are building a small, fun Snake game that runs in the terminal. Work step by step, run the tests after each step, and do not move on until they pass.

## Goal

A playable classic Snake game using Python's built-in `curses` module. It must run on Linux (Fedora) with Python 3.10+ and **no third-party runtime dependencies**. Only `pytest` is allowed, and only for development.

## Rules and constraints

- Use only the Python standard library for the game itself.
- Keep **game logic separate from drawing**. The logic module must not import `curses`, so it can be unit tested.
- All code, comments, identifiers and the README are in English.
- File and folder names are lowercase.
- Keep it simple: small functions, type hints, clear names. No over-engineering, no classes you don't need.
- Do not add features that are not listed below.

## Project structure

Create exactly this layout:

```
snake/
├── main.py              # entry point: python main.py
├── snake/
│   ├── __init__.py
│   ├── game.py          # pure game logic (no curses!)
│   └── ui.py            # curses drawing + input handling
├── tests/
│   └── test_game.py     # pytest tests for game.py
├── requirements-dev.txt # contains: pytest
├── .gitignore           # __pycache__/, .venv/, highscore.txt
└── README.md
```

## Game rules / features

1. The board is a rectangle with a visible border. The snake starts in the middle with length 3, moving right.
2. Controls: arrow keys **and** WASD. The snake cannot reverse directly into itself (e.g. pressing left while moving right is ignored).
3. One food item is on the board at a time, placed at a random free cell (never on the snake).
4. Eating food: the snake grows by 1, the score goes up by 10, and a new food item appears.
5. Speed: starts at a comfortable pace and gets slightly faster every 50 points, with a minimum tick delay so it stays playable.
6. Game over when the snake hits a wall or itself.
7. `p` = pause/resume, `q` = quit, `r` = restart (on the game over screen).
8. Score shown at the top. High score is saved to `highscore.txt` in the project folder and shown alongside the score.
9. If the terminal is too small (smaller than 30x15), show a friendly message instead of crashing.
10. Quitting with `q` or Ctrl+C must restore the terminal properly (use `curses.wrapper`).

## Design of `game.py`

Suggested API (you may adjust names slightly, but keep the idea):

- `Direction`: an enum with `UP`, `DOWN`, `LEFT`, `RIGHT`.
- `GameState`: a dataclass with `width`, `height`, `snake` (list of `(x, y)` tuples, head first), `direction`, `food`, `score`, `game_over`.
- `new_game(width, height, rng) -> GameState`
- `change_direction(state, new_direction) -> GameState` (ignores reverse moves)
- `step(state, rng) -> GameState` advances the game one tick
- `tick_delay(score) -> float` returns seconds per tick

Pass a `random.Random` instance in as `rng` so tests can use a fixed seed.

## Steps

Do these in order. After each step, run `python -m pytest -q` and make sure everything passes.

1. **Setup**: create the folder structure, `requirements-dev.txt`, `.gitignore`, and an empty test that passes.
2. **Logic**: implement `game.py` and write tests for:
   - starting state (length 3, centered, moving right)
   - moving one step
   - reverse direction is ignored
   - eating food grows the snake and adds 10 points
   - wall collision ends the game
   - self collision ends the game
   - food never spawns on the snake
   - `tick_delay` gets smaller as the score grows but never goes below the minimum
3. **UI**: implement `ui.py` with curses (drawing, non-blocking input, pause, game over screen, restart, small-terminal message).
4. **High score**: load and save `highscore.txt` safely (a missing or broken file means high score 0).
5. **Entry point**: `main.py` starts the game with `curses.wrapper`.
6. **README**: a short description, how to run the game, how to run the tests, and the controls.

## Definition of done

- `python -m pytest -q` passes with at least 8 tests.
- `python main.py` starts the game and it is playable from start to game over.
- `game.py` contains no `curses` import.
- No third-party runtime dependencies.
- The README explains how to run and test the game.

When you finish, write a short summary: what you built, how to run it, and anything you couldn't do.
