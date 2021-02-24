from time import time
import pandas as pd
from rubikscube.rubikscube import RubiksCube
from rubikscube.solvers.basic_solver import BasicSolver
from rubikscube.solvers.kociemba_solver import KociembaSolver

N = 1000

c = RubiksCube()
ko = KociembaSolver()
basic = BasicSolver()

solvers = {"kociemba": ko, "basic": basic}

results = []
for i in range(N):
    c.shuffle()
    for name, s in solvers.items():
        try:
            start = time()
            s.compute_solution(c.state_string)
            stop = time()
            res = dict(
                solver=name,
                time=stop - start,
                n=len(s._solution.split(" "))
            )
            results.append(res)
        except (Exception, KeyboardInterrupt) as e:
            print(f"Failed: {c.state_string}")
            raise e

df = pd.DataFrame(results)
df.to_csv(f"solvers_comparison-{N}.csv")
