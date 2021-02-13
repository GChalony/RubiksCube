import pygame as pg
from pygame.locals import *
from scipy.spatial.transform.rotation import Rotation

from camera import Camera


class NavigationController:
    ROT_DELTA = 0.02
    HANDLED_KEYS = [pg.K_SPACE, pg.K_UP, pg.K_DOWN,
                    pg.K_LEFT, pg.K_RIGHT, pg.K_ESCAPE]

    DIRECTION_FOR_KEY = {pg.K_UP: "UP", pg.K_DOWN: "DOWN", pg.K_LEFT: "LEFT", pg.K_RIGHT: "RIGHT"}

    def __init__(self, cube):
        self.camera = Camera()
        self.keys_pressed = {}
        self.mouse_pos_on_click = None

    def start_move(self, direction):
        self.keys_pressed[direction] = pg.time.get_ticks()

    def handle_event(self, event):
        # print(event)
        if event.type in [pg.KEYUP, pg.KEYDOWN] and event.key in self.HANDLED_KEYS:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.camera.toggle_cube_rot()
            # Reset view
            elif event.type == KEYDOWN and event.key == pg.K_ESCAPE:
                self.camera.reset_view()
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

    def animate(self, dt):
        self._animate_keys(dt)
        self._animate_mouse(dt)
        self.camera.apply_view()

    def _animate_keys(self, dt):
        for direction, time in self.keys_pressed.items():
            rot_speed = self._rot_speed(pg.time.get_ticks() - time)
            self.camera.rotate(direction, rot_speed)
        self.camera.camera_rot = self.camera.rot_delta * self.camera.camera_rot

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
            self.camera.camera_rot = rot * self.camera.camera_rot
            self.mouse_pos_on_click = (x, y)


class CubeController:
    def __init__(self, cube):
        self.cube = cube

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


def handle_events(controllers, close):
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
            pg.quit()   # Close pygame window
            close()     # Close Tkinter window
            quit()      # Close Thread
        else:
            for controller in controllers:
                controller.handle_event(event)
