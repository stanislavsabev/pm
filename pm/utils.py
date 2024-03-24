"""Project utilities."""

import functools
import json
import os
import time
from typing import Any, Callable

from pm import const
from pm.typedef import AnyDict

profiler: dict[str, float] = {}


def timeit(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to time a function."""
    global profiler

    @functools.wraps(fn)
    def wrapped(*args: Any, **kwargs: AnyDict) -> Any:
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        end = time.perf_counter()
        profiler[fn.__name__] = max(end - start, profiler.get(fn.__name__, 0))
        return result

    return wrapped


start = 0.0
elapsed = 0.0


def tik() -> None:
    """Start timer."""
    global start
    start = time.perf_counter()


def tok() -> None:
    """Stop timer."""
    global start
    global elapsed
    end = time.perf_counter()
    elapsed = end - start


def print_profiler() -> None:
    """Print time profiler."""
    if not os.environ.get("PERF", 0):
        return
    global profiler
    global elapsed
    sorted_profiler = {
        k: f"{v:0.4f}" for k, v in sorted(profiler.items(), key=lambda kv: kv[1], reverse=True)
    }
    print(json.dumps(sorted_profiler, indent=2))
    print(f"Total elapsed time {elapsed:0.4f}")


def is_help_flag(arg: str) -> bool:
    """Check if flag is -h / --help."""
    return arg in const.HELP_FLAGS


# def expect_flag(val: str):
#     if not val.startswith("-"):
#         ValueError(f"Invalid flag '{val}'. Expected value starting with -")
