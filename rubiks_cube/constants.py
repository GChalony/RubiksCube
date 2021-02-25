import numpy as np

X, Y, Z = np.eye(3, dtype=np.int8)
ALL_MOVES = ["F", "F'", "R", "R'", "L", "L'", "U", "U'", "D", "D'", "B", "B'"]
FACE_ORDER = ["U", "R", "F", "D", "L", "B"]
NORMAL_FOR_FACE = {
    "F": Z, "B": -Z, "L": -X, "R": X, "U": Y, "D": -Y
}