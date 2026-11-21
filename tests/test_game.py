import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from snake.game import (
    BASE_TICK_DELAY,
    MIN_TICK_DELAY,
    Direction,
    GameState,
    change_direction,
    new_game,
    step,
    tick_delay,
)


def make_state(**overrides: object) -> GameState:
    defaults: dict[str, object] = {
        "width": 10,
        "height": 10,
        "snake": [(4, 5), (3, 5), (2, 5)],
        "direction": Direction.RIGHT,
        "food": None,
        "score": 0,
        "game_over": False,
    }
    defaults.update(overrides)
    return GameState(**defaults)  # type: ignore[arg-type]


def test_starting_state_is_centered_and_moving_right() -> None:
    state = new_game(20, 10, random.Random(0))

    assert state.snake == [(10, 5), (9, 5), (8, 5)]
    assert state.direction is Direction.RIGHT
    assert state.score == 0
    assert state.game_over is False
    assert state.food is not None
    assert state.food not in state.snake


def test_step_moves_snake_one_cell() -> None:
    state = make_state()

    moved = step(state, random.Random(0))

    assert moved.snake == [(5, 5), (4, 5), (3, 5)]
    assert moved.score == 0
    assert moved.game_over is False


def test_reverse_direction_is_ignored() -> None:
    state = make_state(direction=Direction.RIGHT)

    turned = change_direction(state, Direction.LEFT)

    assert turned.direction is Direction.RIGHT


def test_perpendicular_direction_is_allowed() -> None:
    state = make_state(direction=Direction.RIGHT)

    turned = change_direction(state, Direction.UP)

    assert turned.direction is Direction.UP


def test_eating_food_grows_snake_and_adds_points() -> None:
    state = make_state(food=(5, 5))
    rng = random.Random(7)

    eaten = step(state, rng)

    assert eaten.snake == [(5, 5), (4, 5), (3, 5), (2, 5)]
    assert eaten.score == 10
    assert eaten.food is not None
    assert eaten.food not in eaten.snake


def test_wall_collision_ends_game() -> None:
    state = make_state(snake=[(9, 5), (8, 5), (7, 5)])

    crashed = step(state, random.Random(0))

    assert crashed.game_over is True
    assert crashed.snake == [(9, 5), (8, 5), (7, 5)]


def test_self_collision_ends_game() -> None:
    state = make_state(
        snake=[(5, 5), (6, 5), (6, 6), (5, 6), (4, 6)],
        direction=Direction.DOWN,
    )

    crashed = step(state, random.Random(0))

    assert crashed.game_over is True


def test_moving_into_vacated_tail_cell_is_allowed() -> None:
    state = make_state(
        snake=[(5, 5), (6, 5), (6, 6), (5, 6)],
        direction=Direction.DOWN,
    )

    moved = step(state, random.Random(0))

    assert moved.game_over is False
    assert moved.snake == [(5, 6), (5, 5), (6, 5), (6, 6)]


def test_food_never_spawns_on_snake() -> None:
    for seed in range(50):
        rng = random.Random(seed)
        state = new_game(8, 6, rng)
        for _ in range(100):
            if state.food is not None:
                assert state.food not in state.snake
            direction = rng.choice(list(Direction))
            state = change_direction(state, direction)
            state = step(state, rng)
            if state.game_over:
                break


def test_tick_delay_shrinks_with_score_and_has_a_floor() -> None:
    assert tick_delay(0) == BASE_TICK_DELAY
    assert tick_delay(50) < tick_delay(0)
    assert tick_delay(100) < tick_delay(50)
    assert tick_delay(10_000) == MIN_TICK_DELAY
    assert all(tick_delay(score) >= MIN_TICK_DELAY for score in range(0, 5000, 10))


def test_new_game_rejects_too_small_board() -> None:
    with pytest.raises(ValueError):
        new_game(4, 10, random.Random(0))
