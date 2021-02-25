import numpy as np
from scipy.spatial.transform.rotation import Rotation

from rubiks_cube.constants import X, Y, Z


class CubicRotation:
    def __init__(self, matrix=None):
        # if matrix is not None and np.sum((matrix < 1) & (matrix > 0)) > 0:
        #     print("Warning: rounding matrix", matrix)
        self.matrix = matrix.astype(int) if matrix is not None else np.eye(3, dtype=int)

    @staticmethod
    def from_rotvec(rotvec):
        return CubicRotation(Rotation.from_rotvec(rotvec).as_matrix())

    def as_matrix(self):
        return self.matrix

    def apply(self, vect) -> np.ndarray:
        return np.dot(self.matrix, vect)

    def inv(self):
        return CubicRotation(self.matrix.T)

    @staticmethod
    def identity():
        return CubicRotation(np.eye(3))

    def __mul__(self, other):
        assert isinstance(other, CubicRotation)
        return CubicRotation(np.dot(self.matrix, other.matrix))

    def __repr__(self):
        return f"CubicRotation({self.matrix.__str__()})"

    def __str__(self):
        return self.matrix.__str__()

    def __eq__(self, other):
        return np.array_equal(self.matrix, other.matrix)


CubicRotation.rx = CubicRotation.from_rotvec(np.pi / 2 * X)
CubicRotation.ry = CubicRotation.from_rotvec(np.pi / 2 * Y)
CubicRotation.rz = CubicRotation.from_rotvec(np.pi / 2 * Z)

def invert_permutation(perm):
    matrix = np.eye(len(perm), dtype=bool)[perm]
    return np.where(matrix.T)[1]
