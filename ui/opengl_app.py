import os

import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from events_hub import EventsHub, Event


class OpenGLApp:
    """Create a basic OpenGL window using pygame."""

    def __init__(self, event_hub: EventsHub):
        self.event_hub = event_hub
        self.closed = False  # Close flag to interupt main loop
        self._start_animation_events = {}
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
        glLineWidth(20.0)
        glPushMatrix()

    def _pygame_event_to_event(self, pg_event):
        """Translate pygame event to homemade event object,
        and discard the ones not interesting."""
        # print(pg_event)
        event = Event(origin="pygame")
        time = pg.time.get_ticks()
        if pg_event.type == pg.QUIT or (pg_event.type == pg.KEYDOWN and pg_event.unicode == "q"):
            event.type = Event.QUIT
        elif pg_event.type == pg.KEYDOWN and pg_event.unicode == Event.SPACE:
            event.type = Event.CAMERA_TOGGLE_ROT
        elif pg_event.type == pg.KEYDOWN and pg_event.unicode == Event.ESCAPE:
            event.type = Event.CAMERA_RESET
        elif pg_event.type == pg.KEYDOWN:
            if pg_event.unicode.lower() in ["f", "b", "u", "d", "l", "r"]:
                event.type = Event.CUBE_MOVE_FACE
                event.face = pg_event.unicode.capitalize()
                if pg_event.unicode.isupper():
                    event.face += "'"
            elif pg_event.key in [pg.K_UP, pg.K_RIGHT, pg.K_LEFT, pg.K_DOWN]:
                self._start_animation_events[pg_event.key] = time
        elif pg_event.type == pg.KEYUP:
            self._start_animation_events.pop(pg_event.key, None)
        elif pg_event.type == pg.MOUSEBUTTONDOWN and pg_event.button == pg.BUTTON_LEFT:
            self._start_animation_events[pg.MOUSEBUTTONDOWN] = time
            pg.mouse.get_rel()
        elif pg_event.type == pg.MOUSEBUTTONUP:
            self._start_animation_events.pop(pg.MOUSEBUTTONDOWN, None)

        if hasattr(event, "type"):  # Check if event not discarded
            return event

    def _direction_for_key(self, key):
        if key == Event.ARROW_UP:
            return "UP"
        elif key == Event.ARROW_DOWN:
            return "DOWN"
        elif key == Event.ARROW_RIGHT:
            return "RIGHT"
        elif key == Event.ARROW_LEFT:
            return "LEFT"

    def _add_animation_events(self):
        """Process animations (registered in self._start_animation_event)
        to create an event at each frame until the end of animation.
        """
        time = pg.time.get_ticks()
        for source, start in self._start_animation_events.items():
            if source in [Event.ARROW_RIGHT, Event.ARROW_UP, Event.ARROW_DOWN, Event.ARROW_LEFT]:  # Arrow key press
                event = Event(origin=Event.PYGAME, type=Event.CAMERA_MOVE,
                              angle=(time - start) / 4000,
                              direction=self._direction_for_key(source))
            elif source == pg.MOUSEBUTTONDOWN:  # Mouse click and drag
                dx, dy = pg.mouse.get_rel()
                dt = time - start
                if dt == 0:
                    continue
                scale = 2
                event = Event(origin=Event.PYGAME, type=Event.CAMERA_MOVE_ABOUT,
                              rot_vec=[dy / dt / scale, dx / dt / scale, 0])
                self._start_animation_events[source] = time
            else:
                raise ValueError(f"Unknown animation key {source}")
            self.event_hub.raise_event(event)

    def _gather_events(self, newframe_event):
        """Read input events in pygame and register them to event_hub"""
        if not self.closed:
            for pg_event in pg.event.get():
                event = self._pygame_event_to_event(pg_event)
                if event is not None:
                    self.event_hub.raise_event(event)
            self._add_animation_events()

    def close(self, close_event):
        self.closed = True
        pg.quit()

    def _add_listeners(self):
        self.event_hub.add_callback(Event.NEWFRAME, self._gather_events)
        self.event_hub.add_callback(Event.QUIT, self.close)

    def draw_frame(self, cube):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube.draw()
        pg.display.flip()
