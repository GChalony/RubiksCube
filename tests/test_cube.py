import numpy as np

from rubiks_cube.constants import Y, X, Z, FACE_ORDER
from rubiks_cube.cube import Cube, generate_cubes_from_state_str, generate_cubes
from rubiks_cube.cubic_mathematic import CubicRotation
from rubiks_cube.rubikscube import RubiksCube


def test_rotate():
    cube = Cube()
    rot = CubicRotation.ry
    cube.rotate(rot)
    assert np.array_equal(cube.rotation.apply(X), -Z)
    assert np.array_equal(cube.rotation.apply(Y), Y)


def test_get_color_on_face():
    cube = Cube()
    for face in FACE_ORDER:
        assert cube.get_color_on_face(face) == face
    cube.rotate(CubicRotation.ry)
    assert cube.get_color_on_face("F") == "L"
    assert cube.get_color_on_face("B") == "R"
    assert cube.get_color_on_face("U") == "U"
    assert cube.get_color_on_face("D") == "D"
    assert cube.get_color_on_face("L") == "B"
    assert cube.get_color_on_face("R") == "F"
    cube.rotate(CubicRotation.rx)
    assert cube.get_color_on_face("F") == "U"
    assert cube.get_color_on_face("R") == "F"
    assert cube.get_color_on_face("B") == "D"


def test_generate_cubes_from_state_str():
    cubes = generate_cubes_from_state_str(RubiksCube.SOLVED_STR)
    canonical_cubes = generate_cubes()
    for c, cc in zip(cubes, canonical_cubes):
        assert c.rotation == cc.rotation
        assert c.colors == cc.colors
        assert c.id == cc.id

    cube = RubiksCube()
    cube.shuffle()
    cubes = generate_cubes_from_state_str(cube.state_string)
    for c, cc in zip(cubes, cube.cubes):
        if len([col for col in cc.colors if col is not None]) > 1:
            # Don't test face centers
            assert c.rotation == cc.rotation
        assert c.colors == cc.colors
        assert c.id == cc.id
