import os

import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from ui.events_hub import EventsHub, Event


class OpenGLApp:
    """Create a basic OpenGL window using pygame."""

    def __init__(self, event_hub: EventsHub):
        self.event_hub = event_hub
        self._add_listeners()

    def setup(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "400,200"  # Ask Window Manager to position window there

        pg.init()
        display = (800, 700)
        pg.display.set_mode(display, DOUBLEBUF | OPENGL)

        # Camera view
        gluPerspective(30, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0, 0, -10)

        glEnable(GL_DEPTH_TEST)
        glLineWidth(5.0)
        glPushMatrix()

    def _pygame_event_to_event(self, pg_event):
        """Translate pygame event to homemade event object,
        and discard the ones not interesting."""
        print(pg_event)
        event = Event(origin="pygame")
        if pg_event.type == pg.QUIT or (pg_event.type == pg.KEYDOWN and pg_event.unicode == "q"):
            event.type = Event.QUIT
        elif pg_event.type == pg.KEYDOWN and pg_event.unicode == Event.SPACE:
            event.type = Event.CAMERA_TOGGLE_ROT
        elif pg_event.type in [pg.KEYDOWN, pg.KEYUP]:
            if pg_event.type == pg.KEYDOWN and pg_event.unicode.lower() in ["f", "b", "u", "d", "l", "r"]:
                event.type = Event.CUBE_MOVE_FACE
                event.face = pg_event.unicode.capitalize()
                event.reverse = pg_event.unicode.isupper()
            # TODO figure out keys and mouse press

        # TODO add mouse

        #     elif pg_event.type == pg.KEYUP:
        #         event.type = Event.KEYUP
        # elif pg_event.type == pg.MOUSEMOTION:
        #     event.type = Event.MOUSEMOTION
        #     event.pos = pg_event.pos
        #     event.rel = pg_event.rel
        # elif pg_event.type == pg.MOUSEBUTTONDOWN:
        #     event.type = Event.MOUSEBUTTONDOWN
        #     event.button = pg_event.button
        # elif pg_event.type == pg.MOUSEBUTTONUP:
        #     event.type = Event.MOUSEBUTTONUP
        #     event.button = pg_event.button
        if hasattr(event, "type"):  # Check if event not discarded
            return event

    def _gather_events(self, newframe_event):
        for pg_event in pg.event.get():
            event = self._pygame_event_to_event(pg_event)
            if event is not None:
                self.event_hub.raise_event(event)

    def close(self, event):
        pg.quit()
        quit()

    def _add_listeners(self):
        self.event_hub.add_callback(Event.NEWFRAME, self._gather_events)
        self.event_hub.add_callback(Event.QUIT, self.close)

    def draw_frame(self, cube):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube.draw()
        pg.display.flip()