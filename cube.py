import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import Color
from scipy.spatial.transform.rotation import Rotation

from utils import Color


class Cube:
    SURFACES = {
        "U": (2, 3, 7, 6),
        "D": (4, 5, 1, 0),
        "L": (0, 1, 3, 2),
        "R": (6, 7, 5, 4),
        "F": (1, 5, 7, 3),
        "B": (4, 0, 2, 6)
    }
    EDGES = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6),
             (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)]

    COLORS = {"U": Color.WHITE, "D": Color.YELLOW,
              "L": Color.BLUE, "R": Color.GREEN,
              "F": Color.ORANGE, "B": Color.RED}

    base_verticies = np.array([(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]) / 2

    def __init__(self, initial_position=None, colors=None, tesselation=1):
        self.position = np.zeros(3) if initial_position is None else initial_position
        self.rotation: Rotation = Rotation.identity()
        self.colors = self.COLORS if colors is None else colors
        self.tesselation = tesselation

    @property
    def verticies(self):
        return self.rotation.apply(self.base_verticies) + self.position

    def rotate(self, rot):
        self.rotation = rot * self.rotation
        self.position = rot.apply(self.position)

    def _draw_square(self, corners, color):
        """Draw a square using the tesselation factor"""
        normal = np.cross(corners[3] - corners[0], corners[1] - corners[0])
        normal = normal / np.linalg.norm(normal)
        glNormal3fv(tuple(normal))
        for i in np.arange(0, 1, 1/self.tesselation):
            for j in np.arange(0, 1, 1/self.tesselation):
                top_left = corners[0] + i * (corners[1] - corners[0]) + j * (corners[3] - corners[0])
                top_right = top_left + (corners[1] - corners[0]) / self.tesselation
                bottom_left = top_left + (corners[3] - corners[0]) / self.tesselation
                bottom_right = top_left + (corners[2] - corners[0]) / self.tesselation
                glColor3fv(color)
                glBegin(GL_QUADS)
                glVertex3fv(tuple(top_left))
                glVertex3fv(tuple(top_right))
                glVertex3fv(tuple(bottom_right))
                glVertex3fv(tuple(bottom_left))
                glEnd()
                glColor3fv(Color.WHITE)
                # glBegin(GL_LINES)
                # glVertex3fv(tuple(top_left))
                # glVertex3fv(tuple(top_right))
                # glVertex3fv(tuple(top_right))
                # glVertex3fv(tuple(bottom_right))
                # glVertex3fv(tuple(bottom_right))
                # glVertex3fv(tuple(bottom_left))
                # glVertex3fv(tuple(bottom_left))
                # glVertex3fv(tuple(top_left))
                # glEnd()

    def draw(self, rot=None):
        if rot is None:
            rot = Rotation.identity()
        for face in self.SURFACES.keys():
            surface = self.SURFACES[face]
            color = self.colors[face]
            corners = [rot.apply(self.verticies[v]) for v in surface]
            self._draw_square(corners, color)

        glBegin(GL_LINES)
        glColor3fv(Color.BLACK)
        for edge in self.EDGES:
            for v in edge:
                vertex = rot.apply(self.verticies[v])
                glVertex3fv(tuple(vertex))
        glEnd()


if __name__=="__main__":
    cube = Cube()

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glEnable(GL_DEPTH_TEST)

    glTranslatef(0.1, -0.2, -4)
    glRotatef(20, 1, 0, 0)

    start = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
        glRotatef(0.1, 0, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        cube.draw()
        pygame.display.flip()
        pygame.time.wait(10)
