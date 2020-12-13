from models import Solution
from models import (CapacityExceeded, CenterTooFar, CenterTooClose,
                    AlreadyPrimaryCenter, Infeasible)

from localsearch import LocalSearchSolver
from greedy import GreedySolver
from grasp import GRASPSolver
from data import cities, centers, types, d_center

import argparse

def run_greedy(initial_solution):
    print("----- RUNNING GREEDY -----")
    gs = GreedySolver(initial_solution, d_center)
    solution = gs.solve()

    print("----- GREEDY RESULTS -----")
    print(solution)
    return solution

def run_localsearch(initial_solution):
    print("----- RUNNING LOCAL SEARCH -----")

    lss = LocalSearchSolver(initial_solution, d_center)
    solution = lss.solve()

    print("----- LOCAL SEARCH RESULTS -----")
    print(solution)
    return solution

def run_grasp(initial_solution):
    print("----- RUNNING GRASP -----")

    gs = GRASPSolver(initial_solution, d_center)
    solution = gs.solve()

    print("----- GRASP RESULTS -----")
    print(solution)
    return solution

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Heuristics for AMMM final project")
    parser.add_argument(
        '-a', '--algorithm', action='store', 
        choices=['greedy', 'localsearch', 'grasp'], required=True
        )
    args = parser.parse_args()

    initial_solution = Solution(cities, centers, types)

    if args.algorithm == "greedy":
        run_greedy(initial_solution)

    if args.algorithm == "localsearch":
        greedy_solution = run_greedy(initial_solution)
        run_localsearch(greedy_solution)

    if args.algorithm == "grasp":
        grasp_solution = run_grasp(initial_solution)
        run_localsearch(grasp_solution)
