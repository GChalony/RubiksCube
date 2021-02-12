from threading import Lock


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

