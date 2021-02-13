# All threading logic is done here
from threading import Thread

import pygame as pg

from camera import Camera
from opengl_app import OpenGLApp
from rubikscube_drawer import RubiksCubeDrawer
from ui.dashboard import Dashboard
from ui.events_hub import EventsHub, Event


def run_cube_sim():
    global cube, event_hub, app

    app.setup()

    clock = pg.time.Clock()
    clock.tick()

    while True:
        app.draw_frame(cube)

        dt = clock.tick(30)
        event_hub.raise_event(Event(origin=Event.APPLICATION, type=Event.NEWFRAME, dt=dt))
        event_hub.handle_events()


def run_controls_ui():
    global dash
    dash.mainloop()


event_hub = EventsHub()
cube = RubiksCubeDrawer(event_hub)
camera = Camera(event_hub)

app = OpenGLApp(event_hub)
dash = Dashboard(event_hub)


tCube = Thread(target=run_cube_sim)
tCube.start()

run_controls_ui()  # Tkinter needs to be called from main thread
tCube.join()
