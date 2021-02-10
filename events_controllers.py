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

    DIRECTION_FOR_KEY = {pg.K_UP: "UP", pg.K_DOWN: "DOWN", pg.K_LEFT: "LEFT", pg.K_RIGHT: "RIGHT"}

    def __init__(self, cube):
        self.keys_pressed = {}
        self.mouse_pos_on_click = None
        self.cube = cube
        self.camera_rot = Rotation.identity()
        self.rot_delta = Rotation.from_rotvec([0, self.ROT_DELTA, 0])

    def toggle_cube_rot(self):
        if np.linalg.norm(self.rot_delta.as_rotvec()) < 0.01:
            self.rot_delta = Rotation.from_rotvec([0, self.ROT_DELTA, 0])
        else:
            self.rot_delta = Rotation.identity()

    def reset_view(self):
        self.camera_rot = Rotation.identity()

    def start_move(self, direction):
        self.keys_pressed[direction] = pg.time.get_ticks()

    def handle_event(self, event):
        # print(event)
        if event.type in [pg.KEYUP, pg.KEYDOWN] and event.key in self.HANDLED_KEYS:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.toggle_cube_rot()
            # Reset view
            elif event.type == KEYDOWN and event.key == pg.K_ESCAPE:
                self.reset_view()
            # Register key down
            elif event.type == pg.KEYDOWN:
                self.start_move(self.DIRECTION_FOR_KEY[event.key])
            # Unregister key down
            elif event.type == pg.KEYUP:
                dir = self.DIRECTION_FOR_KEY.get(event.key, None)
                self.keys_pressed.pop(dir, None)
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.mouse_pos_on_click = pg.mouse.get_pos()
        elif event.type == pg.MOUSEBUTTONUP:
            self.mouse_pos_on_click = None

    def _update_view(self):
        glPopMatrix()
        glPushMatrix()
        rotvec = self.camera_rot.as_rotvec()
        glRotate(np.degrees(np.linalg.norm(rotvec)), *rotvec)

    def animate(self, dt):
        self._animate_keys(dt)
        self._animate_mouse(dt)

    def _animate_keys(self, dt):
        for direction, time in self.keys_pressed.items():
            rot_speed = self._rot_speed(dt)
            if direction in ["RIGHT", "LEFT"]:
                sign = 1 if direction == "RIGHT" else -1
                rot = Rotation.from_rotvec([0, sign * rot_speed, 0])
                self.camera_rot = rot * self.camera_rot
            else:
                sign = 1 if direction == "UP" else -1
                rot = Rotation.from_rotvec([sign * rot_speed, 0, 0])
                self.camera_rot = rot * self.camera_rot
        self.camera_rot = self.rot_delta * self.camera_rot
        self._update_view()

    def _rot_speed(self, dt):
        return dt / 2000

    def _animate_mouse(self, dt):
        if self.mouse_pos_on_click is not None:
            prev_x, prev_y = self.mouse_pos_on_click
            x, y = pg.mouse.get_pos()
            dx, dy = x - prev_x, y - prev_y
            # Find vector around which to rotate
            scale = 2
            v = [dy / dt / scale, dx / dt / scale, 0]
            rot = Rotation.from_rotvec(v)
            self.camera_rot = rot * self.camera_rot
            self.mouse_pos_on_click = (x, y)


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
                self.cube.move_face("F", reverse=reverse)
            elif event.key == pg.K_b:
                self.cube.move_face("B", reverse=reverse)
            elif event.key == pg.K_l:
                self.cube.move_face("L", reverse=reverse)
            elif event.key == pg.K_r:
                self.cube.move_face("R", reverse=reverse)
            elif event.key == pg.K_u:
                self.cube.move_face("U", reverse=reverse)
            elif event.key == pg.K_d:
                self.cube.move_face("D", reverse=reverse)

    def animate(self, dt):
        self.cube.animate(dt)
        pass


def animate_controllers(controllers, dt):
    for controller in controllers:
        controller.animate(dt)


def handle_events(controllers):
    for event in pg.event.get():
        # TODO close both windows
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
            pg.quit()
            quit()
        else:
            for controller in controllers:
                controller.handle_event(event)


if __name__ == '__main__':

    cube = RubiksCube()
    cube.shuffle()

    controls = [NavigationController(cube), CubeController(cube)]

    pg.init()
    display = (800, 600)
    pg.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Camera view
    gluPerspective(30, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0, 0, -10)

    glEnable(GL_DEPTH_TEST)
    glLineWidth(5.0)
    glPushMatrix()

    while True:
        handle_events(controls)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube.draw()
        pg.display.flip()

        pg.time.wait(10)
