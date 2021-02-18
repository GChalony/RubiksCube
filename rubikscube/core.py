"""This module contains some fundamental functions regarding rubikscube states and representation."""
import kociemba
import numpy as np
from scipy.spatial.distance import cdist
from scipy.spatial.transform.rotation import Rotation

from rubikscube.cube import Cube

X, Y, Z = np.eye(3, dtype=np.int8)
ALL_MOVES = ["F", "F'", "R", "R'", "L", "L'", "U", "U'", "D", "D'", "B", "B'"]
FACE_ORDER = ["U", "R", "F", "D", "L", "B"]


def state_str_to_state_description(state_str):
    [u, r, f, d, l, b] = [state_str[9 * i: 9 * (i + 1)] for i in range(6)]
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


def generate_cubes():
    cubes = []
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                if x == y == z == 0:
                    continue
                colors = [
                    "U" if y == 1 else None,
                    "R" if x == 1 else None,
                    "F" if z == 1 else None,
                    "D" if y == -1 else None,
                    "L" if x == -1 else None,
                    "B" if z == -1 else None
                ]
                pos = np.array([x, y, z])
                cube = Cube(pos, colors=colors)
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
    if face in ["F", "R", "B", "L"]:
        return Y
    elif face == "U":
        return -Z
    elif face == "D":
        return Z
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


def get_cube_ids_on_face(cubes, face):
    """Returns the 9 cubes on given face, ordered from top_left to bottom right."""
    normal = get_normal(face)
    up = get_up_on_face(face)
    right = np.cross(up, normal)
    positions = [normal + x * right + y * up
                 for y in (1, 0, -1) for x in (-1, 0, 1)]
    current_positions = [c.position for c in cubes]
    dist_matrix = cdist(current_positions, positions)
    cubes_ids = np.where((dist_matrix < 0.1).T)[1]
    return cubes_ids


def get_color_from_state_str(state_str, pos, direction):
    """Return color letter corresponding to sticker on cube as position pos and in direction direction."""
    direction = direction.astype(np.int8)
    offset_for_direction = {tuple(Y): 0, tuple(X): 9, tuple(Z): 18, tuple(-Y): 27, tuple(-X): 36, tuple(-Z): 45}
    axis = np.where(direction != 0)[0][0]
    assert pos[axis] == direction[axis]  # Check valid face for cube
    up = get_up_on_face(get_face_for_normal(direction))
    right = np.cross(up, direction)

    face_offset = offset_for_direction[tuple(direction)]
    up_offset = 3 * (1 - np.dot(pos, up))
    right_offset = np.dot(right, pos) + 1
    index = int(face_offset + up_offset + right_offset)

    return state_str[index]


def get_rot_from_basis(basis):
    """Returns a rotation that sends (X,Y,Z) to the vectors given.
    Vectors can be None to pass no requirement.
    """
    basis = list(basis).copy()
    n = sum(i is None for i in basis)
    if n == 1:
        i = np.where([i is None for i in basis])[0][0]
        j = (i + 1) % 3
        k = (i + 2) % 3
        vect = np.cross(basis[j], basis[k])
        basis[i] = vect
    elif n == 2:
        i = np.where([i is not None for i in basis])[0][0]
        v1 = basis[i]
        axis = np.where(v1 != 0)[0][0]
        v2 = [0, 0, 0]
        v2[(axis + 1) % 3] = 1
        v3 = np.cross(v1, v2)
        basis[(i + 1) % 3] = v2
        basis[(i + 2) % 3] = v3
    return Rotation.from_matrix(basis)


def generate_cubes_from_state_str(state_str):
    # Check valid
    try:
        kociemba.solve(state_str)
    except ValueError as e:
        raise ValueError(f"Invalid state string {state_str}")

    base = np.eye(3)
    cubes = []
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                if x == y == z == 0:  # Skip center cube
                    continue
                pos = np.array([x, y, z])

                basis = [None] * 3
                for axis in np.where(pos != 0)[0]:
                    color = get_color_from_state_str(state_str, pos, pos[axis] * base[axis])
                    norm = get_normal(color)
                    basis[axis] = norm * pos[axis]

                rot = get_rot_from_basis(basis)
                colors = [
                    "U" if y == 1 else None,
                    "R" if x == 1 else None,
                    "F" if z == 1 else None,
                    "D" if y == -1 else None,
                    "L" if x == -1 else None,
                    "B" if z == -1 else None
                ]
                cube = Cube(initial_position=pos, initial_rotation=rot, colors=colors)
                cubes.append(cube)
    return np.array(cubes)
