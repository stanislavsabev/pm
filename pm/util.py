import functools
import json
import os
import time

profiler = {}


def timeit(fn):
    global profiler

    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        end = time.perf_counter()
        profiler[fn.__name__] = max(end - start, profiler.get(fn.__name__, 0))
        return result

    return wrapped


start = 0
elapsed = 0


def tik():
    global start
    start = time.perf_counter()


def tok():
    global start
    global elapsed
    end = time.perf_counter()
    elapsed = end - start


def print_profiler():
    if not os.environ.get("PERF", 1):
        return
    global profiler
    global elapsed
    sorted_profiler = {
        k: f"{v:0.4f}"
        for k, v in reversed(sorted(profiler.items(), key=lambda kv: kv[1]))
    }
    print(json.dumps(sorted_profiler, indent=2))
    print(f"Total elapsed time {elapsed:0.4f}")
