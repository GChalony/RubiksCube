import numpy as np

from rubiks_cube.constants import Z, Y, X, FACE_ORDER
from rubiks_cube.core import state_str_to_state_description, get_normal, get_up_on_face, get_face_for_normal, \
    get_color_from_state_str, get_rot_from_basis, neg_move, get_rot, get_cube_ids_on_face, get_permutation


def test_state_str_to_state_description():
    state = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    expected = """    |UUU|
    |UUU|
    |UUU|
|LLL|FFF|RRR|BBB|
|LLL|FFF|RRR|BBB|
|LLL|FFF|RRR|BBB|
    |DDD|
    |DDD|
    |DDD|"""
    assert state_str_to_state_description(state) == expected


def test_get_normal():
    assert np.array_equal(get_normal("F"), Z)
    assert np.array_equal(get_normal("B"), -Z)
    assert np.array_equal(get_normal("R"), X)
    assert np.array_equal(get_normal("L"), -X)
    assert np.array_equal(get_normal("U"), Y)
    assert np.array_equal(get_normal("D"), -Y)


def test_get_up_on_face():
    assert np.array_equal(get_up_on_face("F"), Y)
    assert np.array_equal(get_up_on_face("B"), Y)
    assert np.array_equal(get_up_on_face("L"), Y)
    assert np.array_equal(get_up_on_face("R"), Y)
    assert np.array_equal(get_up_on_face("U"), -Z)
    assert np.array_equal(get_up_on_face("D"), Z)


def test_get_face_for_normal():
    assert get_face_for_normal(X) == "R"
    assert get_face_for_normal(-X) == "L"
    assert get_face_for_normal(Y) == "U"
    assert get_face_for_normal(-Y) == "D"
    assert get_face_for_normal(Z) == "F"
    assert get_face_for_normal(-Z) == "B"


def test_get_color_from_state_str():
    state = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                if x == y == z == 0:
                    continue
                pos = np.array([x, y, z])
                for n in (x*X, y*Y, z*Z):
                    if np.linalg.norm(n) != 0:
                        assert get_color_from_state_str(state, pos, n) == get_face_for_normal(n)


def test_get_rot_from_basis():
    canonical = [X, Y, Z]
    test_cases = [
        canonical,
        [Z, None, Y],
        [Z, None, None],
        [X, Z, -Y]
    ]
    for basis in test_cases:
        rot = get_rot_from_basis(basis)
        for n, m in zip(canonical, basis):
            if m is not None:
                np.array_equal(rot.apply(n), m)


def test_neg_move():
    test_cases = [
        ("F", "F'"), ("R2", "R2"), ("L'", "L"), ("D", "D'")
    ]
    for f, neg in test_cases:
        assert neg_move(f) == neg


def test_get_rot():
    test_cases = [
        ("F", False, False, Z, Z),
        ("F", False, False, X, -Y),
        ("F", False, False, -Y, -X),
        ("R", True, False, Z, -Y),
        ("R", True, False, X, X),
        ("R", True, False, -Y, -Z),
        ("D", False, True, Z, -Z),
        ("D", False, True, Y, Y),
        ("D", False, True, X, -X),
    ]
    for face, reverse, double, vect, expected in test_cases:
        rot = get_rot(face, reverse, double)
        assert np.array_equal(rot.apply(vect), expected)


def test_get_cube_ids_on_face():
    test_cases = [
        ("F", [8, 16, 25, 5, 13, 22, 2, 11, 19]),
        ("L", [6, 7, 8, 3, 4, 5, 0, 1, 2]),
        ("U", [6, 14, 23, 7, 15, 24, 8, 16, 25]),
        ("B", [23, 14, 6, 20, 12, 3, 17, 9, 0]),
        ("R", [25, 24, 23, 22, 21, 20, 19, 18, 17]),
        ("D", [2, 11, 19, 1, 10, 18, 0, 9, 17])
    ]
    for face, expected in test_cases:
        assert list(get_cube_ids_on_face(face)) == expected


def test_get_permutation():
    test_cases = [
        ("F", False, False, [0, 1, 19, 3, 4, 11, 6, 7, 2, 9, 10, 22, 12, 13, 14, 15, 5, 17, 18, 25, 20, 21, 16, 23, 24, 8]),
        ("L", True, True, [8, 7, 6, 5, 4, 3, 2, 1, 0, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    ]
    for face, reverse, double, expected in test_cases:
        perm = get_permutation(face, reverse, double)
        assert list(perm) == expected

    identity = np.arange(26)
    for face in FACE_ORDER:
        perm = get_permutation(face, False, False)
        perm_reverse = get_permutation(face, True, False)
        perm_double = get_permutation(face, False, True)
        perm_double_reverse = get_permutation(face, True, True)
        assert np.array_equal(perm_double, perm_double_reverse)
        # 4 turns
        assert np.array_equal(identity[perm][perm][perm][perm], identity)
        # 2 turn + 1 double turn
        assert np.array_equal(identity[perm][perm][perm_double], identity)
        # 1 turn + 1 turn reverse
        assert np.array_equal(identity[perm][perm_reverse], identity)
        # 1 reverse + 1 turn
        assert np.array_equal(identity[perm_reverse][perm], identity)
        # 1 double turn + 2 reverse
        assert np.array_equal(identity[perm_double][perm_reverse][perm_reverse], identity)
