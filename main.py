from models import (CapacityExceeded, CenterTooFar, CenterTooClose,
                    AlreadyPrimaryCenter, Infeasible)

from localsearch import LocalSearchSolver
from greedy import GreedySolver
from data import cities, centers, types, d_center

import argparse

def run_greedy():
    print("----- RUNNING GREEDY -----")
    gs = GreedySolver(cities, centers, types, d_center)
    gs.solve()

    print("----- GREEDY RESULTS -----")
    for idx, c in enumerate(cities):
        print(f"City {idx} {c.x, c.y}:")
        print(f"\tPrimary center: ({c.pc.x}, {c.pc.y}) of type {c.pc.t.tid}")
        print(f"\tSecondary center: ({c.sc.x}, {c.sc.y}) of type {c.sc.t.tid}")

    total_cost = 0
    for idx, cn in enumerate(centers):
        if cn.active:
            print("Location %d, has a center of type %d." % (idx+1, cn.t.tid))
            total_cost += cn.cost
    print("Total cost: %d" % total_cost)

def run_localsearch():
    print("----- RUNNING LOCAL SEARCH -----")

    lss = LocalSearchSolver(cities, centers, types, d_center)
    lss.solve()

    print("----- LOCAL SEARCH RESULTS -----")
    for idx, c in enumerate(cities):
        print(f"City {idx} {c.x, c.y}:")
        print(f"\tPrimary center: ({c.pc.x}, {c.pc.y}) of type {c.pc.t.tid}")
        print(f"\tSecondary center: ({c.sc.x}, {c.sc.y}) of type {c.sc.t.tid}")

    total_cost = 0
    for idx, cn in enumerate(centers):
        if cn.active:
            print("Location %d, has a center of type %d." % (idx+1, cn.t.tid))
            total_cost += cn.cost
    print("Total cost: %d" % total_cost)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Heuristics for AMMM final project")
    parser.add_argument(
        '-a', '--algorithm', action='store', 
        choices=['greedy', 'localsearch', 'grasp'], required=True
        )
    args = parser.parse_args()

    if args.algorithm == "greedy":
        run_greedy()

    if args.algorithm == "localsearch":
        run_greedy()
        run_localsearch()

    if args.algorithm == "grasp":
        raise NotImplementedError
