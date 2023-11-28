import functools
import json
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


def print_profiler():
    global profiler
    sorted_profiler = {
        k: f"{v:0.4f}" for k, v in reversed(sorted(profiler.items(), key=lambda kv: kv[1]))
    }
    print(json.dumps(sorted_profiler, indent=2))
