import kociemba

from rubikscube.rubikscube import RubiksCube


class KociembaSolver:
    def __init__(self):
        self._solution = None

    def get_next_move(self):
        print(f"Next move: {self._solution=}")
        return self._solution.split(" ")[0] if not self.is_solved() else None

    def get_all_moves(self):
        return self._solution.split(" ") if not self.is_solved() else []

    def is_solved(self):
        return len(self._solution) == 0

    def compute_solution(self, state, callback):
        if state == RubiksCube.SOLVED_STR:
            self._solution = ""
            return
        solution = kociemba.solve(state)
        self._solution = solution
        callback(solution)
