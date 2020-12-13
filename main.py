from models import Solution
from models import (CapacityExceeded, CenterTooFar, CenterTooClose,
                    AlreadyPrimaryCenter, Infeasible)

from localsearch import LocalSearchSolver
from greedy import GreedySolver
from grasp import GRASPSolver
from data import cities, centers, types, d_center

import argparse
import time

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

    ini_time = time.time()
    if args.algorithm == "greedy":
        run_greedy(initial_solution)
        time_greedy = time.time() - ini_time
        print("Time Greedy: %f" % time_greedy)

    if args.algorithm == "localsearch":
        greedy_solution = run_greedy(initial_solution)
        time_greedy = time.time() - ini_time
        run_localsearch(greedy_solution)
        time_localsearch = time.time() - ini_time - time_greedy
        print("Time Greedy: %f" % time_greedy)
        print("Time LS: %f" % time_localsearch)

    if args.algorithm == "grasp":
        grasp_solution = run_grasp(initial_solution)
        time_grasp = time.time() - ini_time
        run_localsearch(grasp_solution)
        time_localsearch = time.time() - ini_time - time_grasp
        print("Time GRASP: %f" % time_grasp)
        print("Time LS: %f" % time_localsearch)



