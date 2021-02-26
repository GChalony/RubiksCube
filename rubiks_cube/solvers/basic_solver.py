import numpy as np
from scipy.spatial.transform.rotation import Rotation

from rubiks_cube.core import get_color_from_state_str, Y, X, Z, get_normal, get_face_for_normal, neg_move
from rubiks_cube.rubikscube import RubiksCube
from utils import angle, profile, rotate_list


def is_white_cross_done(state_str):
    for x in (-1, 1):
        pos = np.array([x, 1, 0])
        # print(pos, get_color_from_state_str(state_str, pos, Y), get_color_from_state_str(state_str, pos, x * X), get_face_for_normal(x * X))
        if get_color_from_state_str(state_str, pos, Y) != "U" or \
                get_color_from_state_str(state_str, pos, x * X) != get_face_for_normal(x * X):
            return False
    for z in (-1, 1):
        pos = np.array([0, 1, z])
        if get_color_from_state_str(state_str, pos, Y) != "U" or \
                get_color_from_state_str(state_str, pos, z * Z) != get_face_for_normal(z * Z):
            return False
    return True


def is_white_corners_done(state_str):
    for x in (-1, 1):
        for z in (-1, 1):
            pos = np.array([x, 1, z])
            cu = get_color_from_state_str(state_str, pos, Y)
            cx = get_color_from_state_str(state_str, pos, x*X)
            cz = get_color_from_state_str(state_str, pos, z*Z)
            if cu != "U" or cx != get_face_for_normal(x*X) or cz != get_face_for_normal(z*Z):
                return False
    return True


def is_second_crown_done(state_str):
    for x in (-1, 1):
        for z in (-1, 1):
            pos = np.array([x, 0, z])
            cx = get_color_from_state_str(state_str, pos, x*X)
            cz = get_color_from_state_str(state_str, pos, z*Z)
            if cx != get_face_for_normal(x * X) or cz != get_face_for_normal(z * Z):
                return False
    return True


def is_yellow_cross_done(state_str):
    for n in (X, -X, Z, -Z):
        pos = np.array([0, -1, 0]) + n
        c_down = get_color_from_state_str(state_str, pos, -Y)
        if c_down != "D":
            return False
    return True


def is_yellow_cross_oriented(state_str):
    for n in (X, -X, Z, -Z):
        pos = np.array([0, -1, 0]) + n
        c_down = get_color_from_state_str(state_str, pos, -Y)
        c_side = get_color_from_state_str(state_str, pos, n)
        if c_down != "D" or get_face_for_normal(n) != c_side:
            return False
    return True


def is_yellow_corners_positioned(state_str):
    side_faces = ["F", "R", "B", "L"]
    for i, f in enumerate(side_faces):
        n = get_normal(f)
        m = np.cross(Y, n)
        pos = -Y + n + m
        corner = {
            get_color_from_state_str(state_str, pos, -Y),
            get_color_from_state_str(state_str, pos, n),
            get_color_from_state_str(state_str, pos, m)
        }
        aim_corner = {"D", side_faces[i], side_faces[(i + 1) % 4]}
        if aim_corner != corner:
            return False
    return True


def is_yellow_corners_oriented(state_str):
    return state_str == RubiksCube.SOLVED_STR


def _get_up_turn(v1, v2):
    theta = angle(v1, v2, ignore_axis=1)
    theta = (np.round(theta / np.pi * 2) * 90) % 360
    # print(f"{theta=}")
    m1 = []
    if theta == 90:
        m1 = ["U"]
    elif theta == 180:
        m1 = ["U2"]
    if theta == 270:
        m1 = ["U'"]
    m3 = [neg_move(m1[0])] if len(m1) != 0 else []
    return m1, m3


def white_cross(state_str):
    # Start with 2nd crown edges
    for x in (-1, 1):
        for z in (-1, 1):
            pos = np.array([x, 0, z])
            cols = [get_color_from_state_str(state_str, pos, x * X), get_color_from_state_str(state_str, pos, z * Z)]
            if "U" in cols:
                # print("2nd crown")
                i = [c != "U" for c in cols].index(True)
                col = cols[i]
                n = [x * X, z * Z][i]
                v = get_normal(col)
                # print(n, v)
                u = [x * X, z * Z][1 - i]

                m1, m3 = _get_up_turn(n, v)

                m2 = get_face_for_normal(n)
                if np.cross(n, u)[1] > 0:
                    m2 += "'"
                # print(m1, m2, m3)

                return m1 + [m2] + m3

    # Then down edges
    for x, z, n in [(-1, 0, -X), (1, 0, X), (0, -1, -Z), (0, 1, Z)]:
        pos = np.array([x, -1, z])
        c_side = get_color_from_state_str(state_str, pos, n)
        c_down = get_color_from_state_str(state_str, pos, -Y)
        if c_down == "U":
            # print("Down - down")
            m1, m3 = _get_up_turn(get_normal(c_side), n)
            m2 = get_face_for_normal(n) + "2"
            # print(m1, m2, m3)
            return m1 + [m2] + m3
        elif c_side == "U":
            # print("Down - side")
            m1, m3 = _get_up_turn(get_normal(c_side), n)
            m = get_face_for_normal(n)
            mm = get_face_for_normal(np.cross(n, Y))
            m2 = [m, "U", mm, "U'"]

            return m1 + m2 + m3

    # Then up edges (if misplaced)
    for x, z, n in [(-1, 0, -X), (1, 0, X), (0, -1, -Z), (0, 1, Z)]:
        pos = np.array([x, 1, z])
        # print(pos, get_color_from_state_str(state_str, pos, n))
        if get_color_from_state_str(state_str, pos, n) != get_face_for_normal(n):
            # print("Misplaced", pos, n)
            return [get_face_for_normal(n)]  # Simply get it out

    raise ValueError("No move found, it cross done?")


def white_corners(state_str):
    # Down corners
    for x in (-1, 1):
        for z in (-1, 1):
            pos = np.array([x, -1, z])
            csx = get_color_from_state_str(state_str, pos, x * X)
            csz = get_color_from_state_str(state_str, pos, z * Z)
            c_down = get_color_from_state_str(state_str, pos, -Y)
            if csx == "U" or csz == "U":
                # White on side
                # print("Down - side", csx, csz, c_down)
                n = x*X if csx == "U" else z*Z
                v = z*Z if csx == "U" else x*X
                col = csz if csx == "U" else csx
                m1, m3 = _get_up_turn(get_normal(col), v)
                to_right = np.cross(v, n)[1] > 0
                m2 = [get_face_for_normal(n), "D"]
                if to_right:
                    m2[0] += "'"
                    m2[1] += "'"
                m2.append(neg_move(m2[0]))
                return m1 + m2 + m3
            elif c_down == "U":
                # White down -> just move it on side
                csx = get_color_from_state_str(state_str, pos, x * X)
                csz = get_color_from_state_str(state_str, pos, z * Z)
                # print("Down - down", csx, csz)
                m1, m3 = _get_up_turn(get_normal(csx), z*Z)  # Rotate around x
                f = get_face_for_normal(x * X)
                m2 = [f, "D'", neg_move(f)]
                if x*z > 0:
                    m2 = [neg_move(m) for m in m2]
                # print(m1 + m2 + m3)
                return m1 + m2 + m3
    # Up corners -> move it down
    for x in (-1, 1):
        for z in (-1, 1):
            pos = np.array([x, 1, z])
            cu = get_color_from_state_str(state_str, pos, Y)
            csx = get_color_from_state_str(state_str, pos, x * X)
            csz = get_color_from_state_str(state_str, pos, z * Z)
            if cu != "U" or csx != get_face_for_normal(x*X) or csz != get_face_for_normal(z*Z):
                # print("Corner wrongly oriented")
                n = x*X if csx == "U" else z*Z
                v = z*Z if csx == "U" else x*X
                m2 = [get_face_for_normal(n), "D", neg_move(get_face_for_normal(n))]
                to_right = np.cross(v, n)[1] > 0
                if to_right:
                    m2 = [neg_move(m) for m in m2]
                return m2
    raise ValueError("No move found: is white face finished?")


def rotate_moves_about_y(moves, normal):
    ORDER = ["F", "L", "B", "R"]
    di = round(angle(Z, normal, ignore_axis=1) / np.pi * 2) + 4
    res = []
    for m in moves:
        l = m[0]
        ll = m[1:]
        if l in ORDER:
            move = ORDER[(ORDER.index(l) + di) % 4] + ll
            res.append(move)
        else:
            res.append(m)
    return res


def flip_left_right(moves):
    res = []
    for m in moves:
        if "R" in m:
            move = "L" + neg_move(m)[1:]
        elif "L" in m:
            move = "R" + neg_move(m)[1:]
        else:
            move = neg_move(m)
        res.append(move)
    return res


def flip_up_down(moves):
    res = []
    for m in moves:
        if "U" in m:
            move = "D" + neg_move(m)[1:]
        elif "D" in m:
            move = "U" + neg_move(m)[1:]
        else:
            move = neg_move(m)
        res.append(move)
    return res


BASE_SECOND_CROWN_MOVE = ["D'", "R'", "D", "R", "D", "F", "D'", "F'"]


def second_crown(state_str):
    for x, z, n in [(-1, 0, -X), (1, 0, X), (0, -1, -Z), (0, 1, Z)]:
        pos = np.array([x, -1, z])
        c_side = get_color_from_state_str(state_str, pos, n)
        c_down = get_color_from_state_str(state_str, pos, -Y)
        if "D" not in [c_side, c_down]:  # Down edges
            # print("Down edge", c_down, c_side)
            # Move in front of c_side color
            theta = angle(n, get_normal(c_side), ignore_axis=1)
            theta = (np.round(theta / np.pi * 2) * 90) % 360
            m1 = []
            if theta == 90:
                m1 = ["D'"]
            elif theta == 180:
                m1 = ["D2"]
            if theta == 270:
                m1 = ["D"]
            # is_right if c_down is to its right
            to_left = np.cross(get_normal(c_side), get_normal(c_down))[1] > 0
            moves = BASE_SECOND_CROWN_MOVE
            if not to_left:
                # print("to_right")
                moves = flip_left_right(moves)
            moves = rotate_moves_about_y(moves, get_normal(c_side))
            return m1 + moves
    for x in (-1, 1):
        for z in (-1, 1):
            pos = np.array([x, 0, z])
            cs1 = get_color_from_state_str(state_str, pos, x*X)
            cs2 = get_color_from_state_str(state_str, pos, z*Z)
            if cs1 != get_face_for_normal(x*X) or cs2 != get_face_for_normal(z*Z):  # Wrong place / orientation
                # print("Edge misplaced", cs1, cs2, x, z)
                if x * z == -1:
                    rotate_about = x * X
                else:
                    rotate_about = z * Z
                moves = rotate_moves_about_y(BASE_SECOND_CROWN_MOVE, rotate_about)
                return moves
    raise ValueError("No edge for second crown, is second crown done?")


BASE_YELLOW_CROSS = ["F", "L", "D", "L'", "D'", "F'"]
BASE_YELLOW_CROSS2 = ["F", "D", "L", "D'", "L'", "F'"]


def yellow_cross(state_str):
    posx = -Y + X
    posmx = -Y - X
    posz = -Y + Z
    posmz = -Y - Z
    col_x = get_color_from_state_str(state_str, posx, -Y)
    col_mx = get_color_from_state_str(state_str, posmx, -Y)
    col_z = get_color_from_state_str(state_str, posz, -Y)
    col_mz = get_color_from_state_str(state_str, posmz, -Y)
    if "D" not in [col_x, col_mx, col_z, col_mz]:
        # print("No yellow")
        return BASE_YELLOW_CROSS
    elif col_x == col_mx == "D":
        # print("Line along X")
        return rotate_moves_about_y(BASE_YELLOW_CROSS, X)
    elif col_z == col_mz == "D":
        # print("Line along Z")
        return BASE_YELLOW_CROSS
    else:
        # print("Yellow corner")
        corner = (col_x == "D") * X + (col_mx == "D") * (-X) + (col_z == "D") * Z + (col_mz == "D") * (-Z)
        n = Rotation.from_rotvec(Y * np.pi * 3 / 8).apply(corner)
        return rotate_moves_about_y(BASE_YELLOW_CROSS2, -n)


CHAIR = ["L", "D2", "L'", "D'", "L", "D'", "L'"]


def orient_yellow_cross(state_str):
    ALL_DIRECTIONS = [X, -Z, -X, Z]
    # Check if just one color already aligned
    colors = [get_color_from_state_str(state_str, -Y + n, n) for n in ALL_DIRECTIONS]
    aim_colors = [get_face_for_normal(n) for n in ALL_DIRECTIONS]
    is_rightly_positioned = [c == cc for c, cc in zip(colors, aim_colors)]
    if sum(is_rightly_positioned) == 1:
        # print("One is right")
        i = is_rightly_positioned.index(True)
        to_right = colors[(i + 1)%4] == aim_colors[(i + 3)%4]
        moves = CHAIR if not to_right else flip_left_right(CHAIR)
        # print(to_right)
        return rotate_moves_about_y(moves, ALL_DIRECTIONS[i])

    # Else try to rotate Up
    for shift in range(4):
        is_rightly_positioned = [c == cc for c, cc in
                                 zip(rotate_list(colors, shift), aim_colors)]
        if sum(is_rightly_positioned) == 1:
            # print(f"Turn down {shift} times")
            # Just turn they go back to start of function
            return ["D"] * shift
    # Else run CHAIR
    return CHAIR


BELGIUM = ["L", "D'", "R'", "D", "L'", "D'", "R", "D"]


def yellow_corners(state_str):
    side_faces = ["F", "R", "B", "L"]
    aim_corners = [{"D", side_faces[i], side_faces[(i+1) % 4]} for i in range(4)]
    corners = []
    for f in side_faces:
        n = get_normal(f)
        m = np.cross(Y, n)
        pos = -Y + n + m
        corners.append({
            get_color_from_state_str(state_str, pos, -Y),
            get_color_from_state_str(state_str, pos, n),
            get_color_from_state_str(state_str, pos, m)
        })
    is_rightly_positioned = [c == cc for c, cc in zip(aim_corners, corners)]
    if sum(is_rightly_positioned) == 1:
        i = is_rightly_positioned.index(True)  # Belgium
        # print("One belgium found", i)
        to_right = aim_corners[(i + 1) % 4] == corners[(i + 3) % 4]
        # print(f"{to_right=}")
        moves = BELGIUM if not to_right else flip_left_right(BELGIUM)
        return rotate_moves_about_y(moves, get_normal(side_faces[(i + to_right)%4]))
    # print("Not belgium found")
    return BELGIUM


DOUBLE_CHAIR = flip_left_right(CHAIR) + CHAIR
FLIPPED_CHAIR = ["D", "R2", "D'", "R'", "D", "R'", "D'"]
FLIPPED_DOUBLE_CHAIR = FLIPPED_CHAIR + flip_up_down(FLIPPED_CHAIR)


def orient_yellow_corners(state_str):
    normals = (Z, X, -Z, -X)
    # Look for two consecutive misoriented corners
    for i, n in enumerate(normals):
        m = np.cross(Y, n)  # Right
        pos = -Y + n + m
        c_down = get_color_from_state_str(state_str, pos, -Y)
        if c_down != "D":
            # print(f"Corner wrongly oriented {i} - {c_down}")
            if get_color_from_state_str(state_str, pos - 2*n, -Y) != "D":
                # print("Next corner also misoriented")
                if c_down == get_face_for_normal(m):
                    # print("Moving corners down")
                    return rotate_moves_about_y(FLIPPED_DOUBLE_CHAIR, n)
                else:
                    # print("Moving corners up")
                    return rotate_moves_about_y(DOUBLE_CHAIR, n)
    # Else only two diagonal misoriented corners
    for i, n in enumerate(normals):
        m = np.cross(Y, n)  # Right
        pos = -Y + n + m
        c_down = get_color_from_state_str(state_str, pos, -Y)
        if c_down != "D":
            # print("Diagonal")
            moves = FLIPPED_DOUBLE_CHAIR if c_down == get_face_for_normal(m) else DOUBLE_CHAIR
            return [neg_move(get_face_for_normal(m))] + rotate_moves_about_y(moves, m) + [get_face_for_normal(m)]
    raise ValueError("No misoriented corner: is cube done?")


def concatenate_moves(moves):
    mm_to_i = {"": 1, "2": 2, "'": 3}
    i_to_mm = {v: k for k, v in mm_to_i.items()}
    m = moves[0][0]
    I = sum(mm_to_i[move[1:]] for move in moves) % 4
    if I == 0:
        return None
    mm = i_to_mm[I]
    return m + mm


def optimise(moves):
    res = []
    N = len(moves)
    i = 0
    while i < N:
        m = moves[i]
        same_moves = [m]
        i += 1
        while i < N and moves[i][0] == m[0]:
            same_moves.append(moves[i])
            i += 1
        r = concatenate_moves(same_moves)
        if r is not None:
            res.append(r)
    print(f"Optimized: {len(moves)} -> {len(res)} (ratio saved {1 - len(res) / len(moves): .2%})")
    return res


def solve(state_str):
    stages = {
        "White cross": (is_white_cross_done, white_cross),
        "White corners": (is_white_corners_done, white_corners),
        "Second crown": (is_second_crown_done, second_crown),
        "Yellow cross": (is_yellow_cross_done, yellow_cross),
        "Orienting yellow cross": (is_yellow_cross_oriented, orient_yellow_cross),
        "Yellow corners": (is_yellow_corners_positioned, yellow_corners),
        "Orienting yellow corners": (is_yellow_corners_oriented, orient_yellow_corners)
    }
    c = RubiksCube()
    c.load_state(state_str)
    all_moves = []
    for stage_name, (is_done, compute) in stages.items():
        print(stage_name)
        while not is_done(c.state_string):
            moves = compute(c.state_string)
            all_moves += moves
            for m in moves:
                c.move(m, lazy=True)
            c._compute_state_string()

    return " ".join(optimise(all_moves))


class BasicSolver:
    def __init__(self):
        self._solution = ""

    def compute_solution(self, state, callback=None):
        if state == RubiksCube.SOLVED_STR:
            self._solution = ""
            return
        solution = solve(state)
        self._solution = solution
        if callback is not None:
            callback(solution)


if __name__ == '__main__':
    c = RubiksCube()
    with profile(True):
        for i in range(10):
            c.shuffle()
            # c.pprint()
            try:
                moves = solve(c.state_string)
                # for m in moves.split(" "):
                #     c.move(m)
                # c.pprint()
                # print("Number of moves", len(moves))
            except (Exception, KeyboardInterrupt) as e:
                print(e, f"Cube state: {c.state_string}")
                c.pprint()
                raise e

