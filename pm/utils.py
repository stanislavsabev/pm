"""Project utilities."""

import functools
import logging
import time
from pathlib import Path
from typing import Any, Callable, Iterable

from pm.models import Cmd, Flag, Flags
from pm.typedef import AnyDict, AnyList

profiler: dict[str, float] = {}


logger = logging.getLogger(__name__)


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


def expand_flag_name(flag: str) -> list[str]:
    """Takes a flag name like `h/help` and returns `[-h, --help]`."""
    return ["-" * i + name for i, name in enumerate(flag.split("/"), start=1)]


def find_in_names(flag: str, flags: list[str]) -> str | None:
    """Searches fir a flag name in list of split names.

    Returns:
        A str with the plit name found or None.
    """
    if not flag.startswith("-"):
        return None
    for split_name in flags:
        if any(flag == name for name in expand_flag_name(split_name)):
            return split_name
    return None


def get_flag_by_name(name: str, flags: Flags) -> Flag | None:
    """Finds flag in flags definitions by name."""
    flag_name = find_in_names(name, [f.name for f in flags])
    if not flag_name:
        return None
    return [f for f in flags if f.name == flag_name][0]


def check_npositional(
    positional: list[str], *, mn: int | None = None, mx: int | None = None
) -> None:
    """Check number of positional arguments and raise a ValueError."""
    n = len(positional)
    if mn and mx and mx < n < mn:
        raise ValueError(f"Invalid number of positional arguments {n}")
    if mn and n < mn:
        raise ValueError(f"Invalid number of positional arguments {n}")
    if mx and n > mx:
        raise ValueError(f"Invalid number of positional arguments {n}")


def set_positional(obj: Cmd, positional: list[str], names: list[str]) -> None:
    """Set positional arguments."""
    try:
        for pos, attr_name in zip(positional, names, strict=True):
            setattr(obj, attr_name, pos)
    except ValueError:
        logger.debug(f"{obj.name}: ValueError, {pos=}, {attr_name=}")


def get_proj_path(config_path: str, proj_name: str, worktree: str) -> str:
    """Gets project path from name and worktree."""
    path = Path(config_path).joinpath(proj_name)
    if worktree:
        path = path.joinpath(worktree)

    if not path.is_dir():
        raise FileNotFoundError(f"Could not find proj path `{str(path)}`")
    return str(path)


def path_name_and_parent(root: str) -> tuple[str, str]:
    """Returns absolute path from name."""
    path = Path(root).absolute()
    if not path.is_dir():
        raise FileNotFoundError(f"Cannot find project path '{root}'")
    return path.name, str(path.parent)


def chunks(lst: list[Any], n: int) -> Iterable[AnyList]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
