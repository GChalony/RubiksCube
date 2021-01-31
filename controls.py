from collections import namedtuple

import numpy as np
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
from scipy.spatial.transform.rotation import Rotation

from rubikscube import RubiksCube

EulerAngles = namedtuple("EulerAngle", ["alpha", "beta"])


class NavigationController:
    DEFAULT_CAMERA_POS = (2, 0, 10)
    ROT_DELTA = 0.02
    HANDLED_KEYS = [pg.K_SPACE, pg.K_UP, pg.K_DOWN,
                    pg.K_LEFT, pg.K_RIGHT, pg.K_ESCAPE]

    def __init__(self, cube):
        self.keys_pressed = {}
        self.cube = cube
        self.camera_rot = Rotation.identity()
        self.rot_delta = Rotation.from_rotvec([0, self.ROT_DELTA, 0])

    def compute_camera_pos(self):
        pos = self.camera_rot.apply(self.DEFAULT_CAMERA_POS)
        return pos

    def toggle_cube_rot(self):
        if np.linalg.norm(self.rot_delta.as_rotvec()) < 0.01:
            print("Enabling")
            return Rotation.from_rotvec([0, self.ROT_DELTA, 0])
        else:
            return Rotation.identity()

    def handle_event(self, event):
        # print(event)
        if event.type in [pg.KEYUP, pg.KEYDOWN] and event.key in self.HANDLED_KEYS:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.rot_delta = self.toggle_cube_rot()
            # Reset view
            elif event.type == KEYDOWN and event.key == pg.K_ESCAPE:
                self.camera_rot = Rotation.identity()
                print("Reset")
            # Register key down
            elif event.type == pg.KEYDOWN:
                self.keys_pressed[event.key] = pg.time.get_ticks()
            # Unregister key down
            elif event.type == pg.KEYUP:
                self.keys_pressed.pop(event.key, None)

    def animate(self):
        # Reset view then recompute camera position
        glPopMatrix()
        glPushMatrix()
        n = pg.time.get_ticks()
        for key, time in self.keys_pressed.items():
            rot_speed = self.rot_speed(n - time)
            if key in [pg.K_RIGHT, pg.K_LEFT]:
                sign = -1 if key == pg.K_RIGHT else 1
                rot = Rotation.from_rotvec([0, sign * rot_speed, 0])
                self.camera_rot = rot * self.camera_rot
            else:
                sign = -1 if key == pg.K_UP else 1
                rot = Rotation.from_rotvec(self.camera_rot.apply([sign * rot_speed, 0, 0]))
                self.camera_rot = rot * self.camera_rot
        self.camera_rot = self.rot_delta * self.camera_rot
        gluLookAt(*self.compute_camera_pos(), 0, 0, 0, 0, 1, 0)

    def rot_speed(self, dt):
        return dt / 3000


class CubeController:
    DEFAULT_CUBE_ROT_SPEED = 0.5

    def __init__(self, cube):
        self.cube = cube
        self.cube_rot_speed = self.DEFAULT_CUBE_ROT_SPEED

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            reverse = event.mod == pg.KMOD_LSHIFT or event.mod == pg.KMOD_RSHIFT
            # Pause / Play rotation
            if event.key == pg.K_f:
                cube.move_face("F", reverse=reverse)
            elif event.key == pg.K_b:
                cube.move_face("B", reverse=reverse)
            elif event.key == pg.K_l:
                cube.move_face("L", reverse=reverse)
            elif event.key == pg.K_r:
                cube.move_face("R", reverse=reverse)
            elif event.key == pg.K_u:
                cube.move_face("U", reverse=reverse)
            elif event.key == pg.K_d:
                cube.move_face("D", reverse=reverse)

    def animate(self):
        # TODO handle cube rot speed
        cube.animate()
        pass


def animate_controls(controllers):
    for controller in controllers:
        controller.animate()


def handle_events(controllers):
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
            pg.quit()
            quit()
        else:
            for controller in controllers:
                controller.handle_event(event)
    animate_controls(controllers)


if __name__ == '__main__':
    cube = RubiksCube()
    cube.shuffle()

    controls = [NavigationController(cube), CubeController(cube)]

    pg.init()
    display = (800, 600)
    pg.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Camera view
    gluPerspective(30, (display[0] / display[1]), 0.1, 50.0)

    glEnable(GL_DEPTH_TEST)
    glLineWidth(5.0)
    glPushMatrix()

    while True:
        handle_events(controls)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube.draw()
        pg.display.flip()

        # TODO constant frame rate ?
        pg.time.wait(10)
