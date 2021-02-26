"""This module contains some fundamental functions regarding rubiks_cube states and representation."""
from functools import lru_cache

import numpy as np

from rubiks_cube.constants import Z, X, Y, FACE_ORDER, NORMAL_FOR_FACE
from rubiks_cube.cubic_mathematics import CubicRotation, invert_permutation


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


def get_normal(face):
    # See https://learnopengl.com/Getting-started/Coordinate-Systems for convention
    return NORMAL_FOR_FACE[face]


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


# @lru_cache(maxsize=6)
def get_face_for_normal(normal):
    if normal[0] > 0.9:
        return "R"
    elif normal[0] < -0.9:
        return "L"
    elif normal[1] > 0.9:
        return "U"
    elif normal[1] < -0.9:
        return "D"
    elif normal[2] > 0.9:
        return "F"
    elif normal[2] < -0.9:
        return "B"
    else:
        raise ValueError(f"No face for normal {normal}")


offset_for_direction = {tuple(Y): 0, tuple(X): 9, tuple(Z): 18, tuple(-Y): 27, tuple(-X): 36, tuple(-Z): 45}


def get_color_from_state_str(state_str, pos, direction):
    """Return color letter corresponding to sticker on cube as position pos and in direction direction."""
    direction = direction.astype(np.int8)
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
    assert len(basis) == 3
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
    return CubicRotation(np.array(basis).T)


@lru_cache(maxsize=18)
def neg_move(move):
    if len(move) == 0:
        return ""
    if "2" in move:
        return move
    elif "'" in move:
        return move[0]
    return move + "'"


CUBIC_ROT_FOR_FACE = {
    f: CubicRotation.from_rotvec(-np.pi / 2 * get_normal(f)) for f in FACE_ORDER
}


def get_rot(face, reverse, double):
    """Returns the CubicRotation instance corresponding to a rotation
    on the given face."""
    mat = CUBIC_ROT_FOR_FACE[face]
    if reverse:
        mat = mat.inv()
    if double:
        mat = mat * mat
    return mat


def _compute_cube_ids_on_face(face):
    """Returns the 9 cubes indexes on given face, ordered from top_left to bottom right."""
    center = 13
    n = get_normal(face)
    up = get_up_on_face(face)
    up_face = get_face_for_normal(up)
    right = np.cross(up, n)
    right_face = get_face_for_normal(right)
    dx, dy, dz = 9, 3, 1
    dis = {"F": dz, "B": -dz, "R": dx, "L": -dx, "U": dy, "D": -dy}
    face_center = center + dis[face]
    ids = []
    for u in (1, 0, -1):
        for r in (-1, 0, 1):
            i = face_center + u * dis[up_face] + r * dis[right_face]
            if i > 13:
                i = i - 1
            ids.append(i)
    return ids


CUBE_IDS_FOR_FACE = {f: _compute_cube_ids_on_face(f) for f in FACE_ORDER}


def get_cube_ids_on_face(f):
    return CUBE_IDS_FOR_FACE[f]


BASE_PERMUTATION = [6, 3, 0, 7, 4, 1, 8, 5, 2]


def get_permutation(face, reverse, double=False):
    # returns a permutation from 26 to 26 elements corresponding to rotating the given face
    perm = np.arange(26)
    # Get 9 cube ids
    face_ids = get_cube_ids_on_face(face)
    # Permute those ids
    face_permutation = BASE_PERMUTATION if not reverse else invert_permutation(BASE_PERMUTATION)
    if double:
        face_permutation = np.array(face_permutation)[face_permutation]
    # Compute overall permutation
    perm[face_ids] = perm[face_ids][face_permutation]
    return perm


