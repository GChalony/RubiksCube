# All threading logic is done here
from threading import Thread

import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from controls import NavigationController, CubeController, handle_events
from rubikscube import RubiksCube
from ui.dashboard import Dashboard


def setup():
    pg.init()
    display = (800, 600)
    pg.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Camera view
    gluPerspective(30, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0, 0, -10)
    # glRotatef(20, 0, 1, 0)
    # glRotatef(30, 1, 0, 0)

    glEnable(GL_DEPTH_TEST)
    glLineWidth(5.0)
    glPushMatrix()


def run_cube_sim():
    global cube
    setup()

    while True:
        handle_events(controls)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube.draw()
        pg.display.flip()

        pg.time.wait(10)


def run_controls_ui():
    global dash
    dash.mainloop()


cube = RubiksCube()
controls = [NavigationController(cube), CubeController(cube)]

dash = Dashboard()

tCube = Thread(target=run_cube_sim)
tCube.start()

run_controls_ui()  # Tkinter needs to be called from main thread

