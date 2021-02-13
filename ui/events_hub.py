import pygame as pg


class Event:
    """Dummy event class."""
    # types
    QUIT = "QUIT"
    NEWFRAME = "NEWFRAME"
    ANIMATIONFINISHED = "ANIMATIONFINISHED"

    CUBE_MOVE_FACE = "MOVE_FACE"
    CUBE_SHUFFLE = "CUBE_SHUFFLE"

    CAMERA_MOVE = "MOVE_CAMERA"
    CAMERA_RESET = "CAMERA_RESET"
    CAMERA_TOGGLE_ROT = "CAMERA_TOGGLE_ROT"

    # keys
    ESCAPE = "\x1b"
    SPACE = " "

    # origins
    PYGAME = "PYGAME"
    TKINTER = "TKINTER"
    APPLICATION = "APPLICATION"

    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def __repr__(self):
        return f"<Event: {self.__dict__}>"


class EventsHub:
    # TODO Thread safety
    """Implements an event aggregator to gather events from both interfaces as well as the application itself.
    Similar to an Observer pattern.

    Warning:
        Events need to be processed regularly by calling `.handle_events()`
        to avoid overflowing the event queue.

    Events types:
     - pygame events (mouse / key press / quit)
     - tkinter events (mouse / key press / quit)
        - all buttons
     - application events, like "AnimationFinishedEvent"
    """

    def __init__(self):
        self._events = []  # TODO change to Queue
        self._callbacks = {}

    def raise_event(self, event):
        self._events.append(event)

    def add_callback(self, event_name, callback):
        self._callbacks.setdefault(event_name, []).append(callback)

    def handle_events(self):
        for event in self._events:
            if event.type in [Event.CUBE_MOVE_FACE, Event.CAMERA_MOVE, Event.CAMERA_TOGGLE_ROT]:
                print("Handling", event, self._callbacks.get(event.type, []))
            for callback in self._callbacks.get(event.type, []):
                callback(event)
        self._events = []


if __name__ == '__main__':
    pg.init()
    display = (800, 700)
    pg.display.set_mode(display, pg.DOUBLEBUF | pg.OPENGL)

    while True:
        for event in pg.event.get():
            print(event, event.__dict__)
