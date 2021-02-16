"""This module contains some fundamental functions regarding rubikscube states and representation."""

import numpy as np

from cube import Cube
from utils import Color


def state_str_to_state_description(state_str):
    [u, r, f, d, l, b] = [state_str[9*i: 9*(i+1)] for i in range(6)]
    ordered = (*u, *l[:3], *f[:3], *r[:3], *b[:3],
               *l[3:6], *f[3:6], *r[3:6], *b[3:6],
               *l[6:9], *f[6:9], *r[6:9], *b[6:9], *d)
    pattern = """    |{}{}{}|
|{}{}{}|
|{}{}{}|
|{}{}{}|{}{}{}|{}{}{}|{}{}{}|
|{}{}{}|{}{}{}|{}{}{}|{}{}{}|
|{}{}{}|{}{}{}|{}{}{}|{}{}{}|
|{}{}{}|
|{}{}{}|
|{}{}{}|"""
    return pattern.format(*ordered)


def generate_cubes(offset):
    cubes = []
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                if x == y == z == 0:
                    continue
                colors = {"U": Color.WHITE if y == 1 else Color.HIDDEN,
                          "D": Color.YELLOW if y == -1 else Color.HIDDEN,
                          "L": Color.BLUE if x == -1 else Color.HIDDEN,
                          "R": Color.GREEN if x == 1 else Color.HIDDEN,
                          "F": Color.ORANGE if z == 1 else Color.HIDDEN,
                          "B": Color.RED if z == -1 else Color.HIDDEN
                          }
                pos = [offset * x, offset * y, offset * z]
                cube = Cube(pos, colors)
                cubes.append(cube)
    return np.array(cubes)


def get_normal(face):
    # See https://learnopengl.com/Getting-started/Coordinate-Systems for convention
    x, y, z = np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])
    if face == "F":
        return z
    elif face == "B":
        return -z
    elif face == "L":
        return -x
    elif face == "R":
        return x
    elif face == "U":
        return y
    elif face == "D":
        return -y
    else:
        raise ValueError(f"Wrong face value: {face}")


def get_up_on_face(face):
    """Returns up vector when looking at given face."""
    x, y, z = np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])
    if face in ["F", "R", "B", "L"]:
        return y
    elif face == "U":
        return -z
    elif face == "D":
        return z
    else:
        raise ValueError(f"Wrong face value: {face}")


def get_face_for_normal(normal):
    [x, y, z] = normal
    if x > 0.9:
        return "R"
    elif x < -0.9:
        return "L"
    elif y > 0.9:
        return "U"
    elif y < -0.9:
        return "D"
    elif z > 0.9:
        return "F"
    elif z < -0.9:
        return "B"
    else:
        raise ValueError(f"No face for normal {normal}")