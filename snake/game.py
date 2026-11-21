"""Pure game logic for Snake.

This module is free of terminal dependencies so the rules can be unit tested.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from enum import Enum

START_LENGTH = 3
FOOD_SCORE = 10
BASE_TICK_DELAY = 0.15
MIN_TICK_DELAY = 0.06
SPEED_SCORE_STEP = 50
SPEED_DECREASE = 0.01

Cell = tuple[int, int]


class Direction(Enum):
    """Movement directions with their (dx, dy) offsets."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def delta(self) -> Cell:
        return self.value

    def is_opposite(self, other: "Direction") -> bool:
        return self.delta == (-other.delta[0], -other.delta[1])


@dataclass
class GameState:
    width: int
    height: int
    snake: list[Cell]
    direction: Direction
    food: Cell | None
    score: int
    game_over: bool


def new_game(width: int, height: int, rng: random.Random) -> GameState:
    """Create a fresh game with a length-3 snake in the centre."""
    if width < START_LENGTH + 2 or height < 3:
        raise ValueError("board is too small for the starting snake")

    center_x, center_y = width // 2, height // 2
    snake = [(center_x - offset, center_y) for offset in range(START_LENGTH)]
    state = GameState(
        width=width,
        height=height,
        snake=snake,
        direction=Direction.RIGHT,
        food=None,
        score=0,
        game_over=False,
    )
    return replace(state, food=_spawn_food(state, rng))


def change_direction(state: GameState, new_direction: Direction) -> GameState:
    """Turn the snake, ignoring moves straight back into its own neck."""
    if state.game_over or state.direction.is_opposite(new_direction):
        return state
    return replace(state, direction=new_direction)


def step(state: GameState, rng: random.Random) -> GameState:
    """Advance the game by one tick."""
    if state.game_over:
        return state

    dx, dy = state.direction.delta
    head = (state.snake[0][0] + dx, state.snake[0][1] + dy)

    if not (0 <= head[0] < state.width and 0 <= head[1] < state.height):
        return replace(state, game_over=True)

    eating = head == state.food
    body = state.snake if eating else state.snake[:-1]
    if head in body:
        return replace(state, game_over=True)

    snake = [head, *body]
    if not eating:
        return replace(state, snake=snake)

    grown = replace(state, snake=snake, score=state.score + FOOD_SCORE)
    return replace(grown, food=_spawn_food(grown, rng))


def tick_delay(score: int) -> float:
    """Seconds per tick, getting shorter as the score grows."""
    speed_ups = max(0, score) // SPEED_SCORE_STEP
    return max(MIN_TICK_DELAY, BASE_TICK_DELAY - speed_ups * SPEED_DECREASE)


def _spawn_food(state: GameState, rng: random.Random) -> Cell | None:
    occupied = set(state.snake)
    free = [
        (x, y)
        for y in range(state.height)
        for x in range(state.width)
        if (x, y) not in occupied
    ]
    return rng.choice(free) if free else None
