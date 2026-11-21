"""Curses user interface for the Snake game."""

from __future__ import annotations

import curses
import random
from pathlib import Path

from .game import Direction, GameState, change_direction, new_game, step, tick_delay

HIGHSCORE_FILE = Path(__file__).resolve().parent.parent / "highscore.txt"

MIN_TERM_WIDTH = 30
MIN_TERM_HEIGHT = 15
MAX_BOARD_WIDTH = 60
MAX_BOARD_HEIGHT = 25

KEY_DIRECTIONS = {
    curses.KEY_UP: Direction.UP,
    curses.KEY_DOWN: Direction.DOWN,
    curses.KEY_LEFT: Direction.LEFT,
    curses.KEY_RIGHT: Direction.RIGHT,
    ord("w"): Direction.UP,
    ord("s"): Direction.DOWN,
    ord("a"): Direction.LEFT,
    ord("d"): Direction.RIGHT,
    ord("W"): Direction.UP,
    ord("S"): Direction.DOWN,
    ord("A"): Direction.LEFT,
    ord("D"): Direction.RIGHT,
}


def load_highscore() -> int:
    """Read the high score; a missing or broken file means zero."""
    try:
        return max(0, int(HIGHSCORE_FILE.read_text(encoding="utf-8").strip()))
    except (OSError, ValueError):
        return 0


def save_highscore(score: int) -> None:
    """Write the high score, ignoring filesystem errors."""
    temp_file = HIGHSCORE_FILE.with_suffix(".tmp")
    try:
        temp_file.write_text(f"{max(0, score)}\n", encoding="utf-8")
        temp_file.replace(HIGHSCORE_FILE)
    except OSError:
        pass


def run() -> None:
    """Start the game and restore the terminal on exit."""
    try:
        curses.wrapper(_run)
    except KeyboardInterrupt:
        pass


def _run(stdscr: curses.window) -> None:
    _setup(stdscr)
    rng = random.Random()
    high_score = load_highscore()
    state: GameState | None = None
    paused = False

    try:
        while True:
            size = _board_size(stdscr)
            if size is None:
                _draw_too_small(stdscr)
                stdscr.timeout(-1)
                if stdscr.getch() in (ord("q"), ord("Q")):
                    break
                continue

            if state is None or (state.width, state.height) != size:
                state = new_game(size[0], size[1], rng)
                paused = False

            if state.game_over:
                _draw(stdscr, state, high_score, paused=False)
                _draw_game_over(stdscr, state, high_score)
                stdscr.timeout(-1)
                key = stdscr.getch()
                if key in (ord("q"), ord("Q")):
                    break
                if key in (ord("r"), ord("R")):
                    high_score = max(high_score, state.score)
                    state = new_game(state.width, state.height, rng)
                    paused = False
                continue

            _draw(stdscr, state, high_score, paused)
            delay = 150 if paused else max(1, round(tick_delay(state.score) * 1000))
            stdscr.timeout(delay)
            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                continue
            if key in (ord("q"), ord("Q")):
                break
            if key in (ord("p"), ord("P")):
                paused = not paused
                continue

            direction = KEY_DIRECTIONS.get(key)
            if direction is not None:
                state = change_direction(state, direction)
            elif key == -1 and not paused:
                state = step(state, rng)
    finally:
        if state is not None:
            high_score = max(high_score, state.score)
        save_highscore(high_score)


def _setup(stdscr: curses.window) -> None:
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.keypad(True)
    stdscr.nodelay(False)


def _board_size(stdscr: curses.window) -> tuple[int, int] | None:
    term_height, term_width = stdscr.getmaxyx()
    if term_height < MIN_TERM_HEIGHT or term_width < MIN_TERM_WIDTH:
        return None
    width = min(MAX_BOARD_WIDTH, term_width - 2)
    height = min(MAX_BOARD_HEIGHT, term_height - 5)
    return width, height


def _draw(stdscr: curses.window, state: GameState, high_score: int, paused: bool) -> None:
    stdscr.erase()
    term_height, term_width = stdscr.getmaxyx()
    left = max(0, (term_width - (state.width + 2)) // 2)
    top = 1
    best = max(high_score, state.score)

    _addstr(stdscr, 0, 1, f"Score: {state.score}   High: {best}", curses.A_BOLD)
    _addstr(stdscr, top, left, "+" + "-" * state.width + "+")
    for row in range(state.height):
        _addstr(stdscr, top + 1 + row, left, "|" + " " * state.width + "|")
    _addstr(stdscr, top + state.height + 1, left, "+" + "-" * state.width + "+")

    if state.food is not None:
        _put(stdscr, top + 1, left + 1, state.food, "*", curses.A_BOLD)
    for index, cell in enumerate(state.snake):
        char = "@" if index == 0 else "o"
        _put(stdscr, top + 1, left + 1, cell, char, curses.A_BOLD if index == 0 else curses.A_NORMAL)

    hint = "PAUSED - p to resume" if paused else "arrows move  p pause  q quit"
    hint_row = top + state.height + 2
    if hint_row < term_height:
        _addstr(
            stdscr,
            hint_row,
            max(0, (term_width - len(hint)) // 2),
            hint,
            curses.A_BOLD if paused else curses.A_DIM,
        )
    stdscr.refresh()


def _draw_game_over(stdscr: curses.window, state: GameState, high_score: int) -> None:
    term_height, term_width = stdscr.getmaxyx()
    best = max(high_score, state.score)
    lines = [
        "GAME OVER",
        f"Score: {state.score}   High: {best}",
        "",
        "[r] restart   [q] quit",
    ]
    box_width = max(len(line) for line in lines) + 4
    box_height = len(lines) + 2
    top = max(0, (term_height - box_height) // 2)
    left = max(0, (term_width - box_width) // 2)

    _addstr(stdscr, top, left, "+" + "-" * (box_width - 2) + "+")
    for offset, line in enumerate(lines, start=1):
        _addstr(stdscr, top + offset, left, "|" + line.center(box_width - 2) + "|")
    _addstr(stdscr, top + box_height - 1, left, "+" + "-" * (box_width - 2) + "+")
    stdscr.refresh()


def _draw_too_small(stdscr: curses.window) -> None:
    stdscr.erase()
    term_height, term_width = stdscr.getmaxyx()
    lines = [
        "Terminal too small.",
        f"Need at least {MIN_TERM_WIDTH}x{MIN_TERM_HEIGHT}.",
        "",
        "Press q to quit.",
    ]
    top = max(0, (term_height - len(lines)) // 2)
    for offset, line in enumerate(lines):
        _addstr(stdscr, top + offset, max(0, (term_width - len(line)) // 2), line)
    stdscr.refresh()


def _put(
    stdscr: curses.window,
    top: int,
    left: int,
    cell: tuple[int, int],
    char: str,
    attr: int,
) -> None:
    _addstr(stdscr, top + cell[1], left + cell[0], char, attr)


def _addstr(stdscr: curses.window, row: int, column: int, text: str, attr: int = 0) -> None:
    try:
        stdscr.addstr(row, column, text, attr)
    except curses.error:
        pass
