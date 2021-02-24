# All threading logic is done here
from threading import Thread

import pygame as pg

from open_gl.camera import Camera
from ui.opengl_app import OpenGLApp
from open_gl.rubikscube_drawer import RubiksCubeDrawer
from ui.controls_panel import Dashboard
from events_hub import EventsHub, Event
from utils import profile


def run_cube_sim():
    """Run main pygame loop, and handle events at each loop."""
    global cube, event_hub, app
    app.setup()
    clock = pg.time.Clock()
    clock.tick()

    while not app.closed:
        app.draw_frame(cube)

        dt = clock.tick(30)
        app.event_hub.raise_event(Event(origin=Event.APPLICATION, type=Event.NEWFRAME, dt=dt))
        event_hub.handle_events()


def run_controls_ui():
    dash.mainloop()


if __name__ == '__main__':
    with profile(on=False):
        event_hub = EventsHub()
        cube = RubiksCubeDrawer(event_hub)
        cube.state.pprint()
        # cube.load_state(RubiksCube.SOLVED_STR)

        camera = Camera(event_hub)

        app = OpenGLApp(event_hub)
        dash = Dashboard(event_hub)

        tCube = Thread(target=run_cube_sim)
        tCube.start()

        run_controls_ui()  # Tkinter needs to be called from main thread
        tCube.join()
