from contextlib import contextmanager
from threading import Lock
import numpy as np

class Color:
    WHITE = (0.9, 0.9, 0.9)
    BLACK = (0, 0, 0)
    RED = (1, 0, 0)
    GREEN = (0, 1, 0)
    BLUE = (0, 0, 1)
    YELLOW = (1, 1, 0)
    MAGENTA = (1, 0, 1)
    CYAN = (0, 1, 1)
    ORANGE = (1, 0.4, 0)
    GRAY = (0.3, 0.3, 0.3)
    HIDDEN = BLACK


class Queue:
    """Thread-safe implementation of a Queue with peek capabilities."""
    def __init__(self):
        self._lock = Lock()
        self._list = []

    def peek(self):
        with self._lock:
            return self._list[0]

    def put(self, item):
        with self._lock:
            self._list.append(item)

    def pop(self):
        with self._lock:
            return self._list.pop(0)

    def empty(self):
        with self._lock:
            return len(self._list) == 0

    def remove_all(self):
        with self._lock:
            self._list = []


@contextmanager
def profile(on=True):
    if not on:
        yield
        return

    import time
    import yappi

    yappi.set_clock_type("cpu")
    yappi.start()
    start = time.time()

    yield

    end = time.time()
    stats = yappi.get_func_stats()
    cpu = max([s.ttot for s in stats])
    wall = end - start
    stats.print_all()
    yappi.get_thread_stats().print_all()
    print(f"\nTotal wall time: {wall}")
    print(f"Total CPU time: {cpu}")
    print(f"Ratio: {cpu / wall: %}")


def angle(v1, v2, ignore_axis=None):
    if ignore_axis is not None:
        select = [i for i in range(3) if i != ignore_axis]
        v1 = v1[select]
        v2 = v2[select]
    cosang = np.dot(v1, v2)
    sinang = np.linalg.det([v1, v2])
    return np.arctan2(sinang, cosang)


def rotate_list(l, n):
    return l[n:] + l[:n]

