import pygame as pg

from utils import Queue


class Event:
    """Dummy event class."""
    # types
    QUIT = "QUIT"
    NEWFRAME = "NEWFRAME"
    ANIMATIONFINISHED = "ANIMATIONFINISHED"

    CUBE_MOVE_FACE = "MOVE_FACE"
    CUBE_SHUFFLE = "CUBE_SHUFFLE"
    CUBE_STATE_CHANGED = "CUBE_STATE_CHANGED"

    CAMERA_MOVE = "CAMERA_MOVE"
    CAMERA_MOVE_ABOUT = "CAMERA_MOVE_ABOUT"
    CAMERA_RESET = "CAMERA_RESET"
    CAMERA_TOGGLE_ROT = "CAMERA_TOGGLE_ROT"

    # keys
    ESCAPE = "\x1b"
    SPACE = " "
    ARROW_DOWN = pg.K_DOWN
    ARROW_UP = pg.K_UP
    ARROW_LEFT = pg.K_LEFT
    ARROW_RIGHT = pg.K_RIGHT

    # origins
    PYGAME = "PYGAME"
    TKINTER = "TKINTER"
    APPLICATION = "APPLICATION"

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def __repr__(self):
        return f"<Event: {self.__dict__}>"


class EventsHub:
    """Implements an event aggregator to gather events from both interfaces as well as the application itself.
    Similar to an Observer pattern.

    Warning:
        Events need to be processed regularly by calling `.handle_events()`
        to avoid overflowing the event queue.

    Events types:
     - pygame events (mouse / key press / quit)
     - tkinter events (mouse / key press / quit)
        - all buttons
     - application events, like "AnimationFinished" event
    """

    def __init__(self):
        self._events = Queue()
        self._callbacks = {}

    def raise_event(self, event):
        self._events.put(event)

    def add_callback(self, event_name, callback):
        self._callbacks.setdefault(event_name, []).append(callback)

    def handle_events(self):
        while not self._events.empty():
            event = self._events.pop()
            if event.type in [Event.QUIT]:
                # print("Handling", event, self._callbacks.get(event.type, []))
                pass
            for callback in self._callbacks.get(event.type, []):
                callback(event)


if __name__ == '__main__':
    pg.init()
    display = (800, 700)
    pg.display.set_mode(display, pg.DOUBLEBUF | pg.OPENGL)

    while True:
        for event in pg.event.get():
            print(event, event.__dict__)
            if event.type == pg.QUIT:
                pg.quit()
                quit()
