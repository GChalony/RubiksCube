# All threading logic is done here
import os
from threading import Thread

import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from events_controllers import NavigationController, CubeController, handle_events, animate_controllers
from rubikscube_drawer import RubiksCubeDrawer
from ui.dashboard import Dashboard


def setup():
    os.environ['SDL_VIDEO_WINDOW_POS'] = "400,200"  # Ask Window Manager to position window there

    pg.init()
    display = (800, 700)
    pg.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Camera view
    gluPerspective(30, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0, 0, -10)
    # glRotatef(20, 0, 1, 0)
    # glRotatef(30, 1, 0, 0)

    glEnable(GL_DEPTH_TEST)
    glLineWidth(5.0)
    glPushMatrix()


def run_cube_sim(close_all):
    global finish_signal, cube, controls

    clock = pg.time.Clock()
    setup()
    clock.tick()

    while not finish_signal:
        handle_events(controls, close_all)
        # Drawing
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube.draw()
        pg.display.flip()

        dt = clock.tick(30)
        animate_controllers(controls, dt)

    pg.quit()


def run_controls_ui():
    global dash
    dash.mainloop()


finish_signal = False

cube = RubiksCubeDrawer()
controls = [NavigationController(cube), CubeController(cube)]

dash = Dashboard(cube, controls[0])


def close_all():
    dash.quit()


tCube = Thread(target=run_cube_sim, args=(close_all,))
tCube.start()

run_controls_ui()  # Tkinter needs to be called from main thread

finish_signal = True    # If Tkinter windows is closed, run_controls_ui will return,
                        # the signal will be changed so pygame will exit its main loop.
tCube.join()
