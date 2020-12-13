import random
import copy

from models import City, LogisticCenterLocation, LogisticCenterType, Solution
from models import (CapacityExceeded, CenterTooFar, CenterTooClose,
                    AlreadyPrimaryCenter, Infeasible)

class GRASPSolver:
    def __init__(self, solution, d_center, debug=False):
        #self.cities = copy.deepcopy(solution.cities)
        #self.centers = copy.deepcopy(solution.centers)
        #self.types = copy.deepcopy(solution.types)
        self.d_center = d_center
        self.debug = debug
        self.solution = solution

    def cost_and_update(self, c, l, primary=True):
        # Returns cost increment
        if l.active:
            # The location is an actual logistic center
            try:
                if primary:
                    l.check_city_primary(c)
                else:
                    l.check_city_secondary(c)
                # No changes must be made in logistic centers
                return 0
            except CapacityExceeded:
                # Try changing center type
                initial_type = l.t
                for t in self.types:
                    if t.cap > l.t.cap:
                        l.t = t
                        try:
                            if primary:
                                l.check_city_primary(c)
                            else:
                                l.check_city_secondary(c)
                            # Return the cost difference between the new type
                            # and the previous type
                            return t.cost - initial_type.cost
                        except CapacityExceeded:
                            l.t = initial_type
                            continue
                        except CenterTooFar:
                            l.t = initial_type
                            continue

                if l.t.tid == initial_type.tid:
                    # No feasible new center type
                    if self.debug:
                        print(f"Infeasible center because capacity c({c.x}, {c.y}) -> l({l.x, l.y})")
                    raise Infeasible

            except CenterTooFar:
                if self.debug:
                    print(f"Infeasible center because too far c({c.x}, {c.y}) -> l({l.x, l.y})")
                raise Infeasible

            except AlreadyPrimaryCenter:
                if self.debug:
                    print(f"Infeasible center because already primary c({c.x}, {c.y}) -> l({l.x, l.y})")
                # Secondary and primary centers must be different
                raise Infeasible

        else:
            # The location does not have a logistic center yet
            # Pick the center type with the smallest cost that is feasible
            ordered_types = sorted(self.types, key=lambda x: x.cost)
            for t in ordered_types:
                try:
                    l.activate(self.centers, self.d_center)
                    l.t = t
                    if primary:
                        l.check_city_primary(c)
                    else:
                        l.check_city_secondary(c)
                    l.active = False
                    return t.cost

                except CenterTooClose:
                    # d_center not satisfied
                    l.t = None
                    l.active = False
                    if self.debug:
                        print(f"Infeasible center because too close to another center c({c.x}, {c.y}) -> l({l.x, l.y})")
                    raise Infeasible

                except CapacityExceeded:
                    # City is too large for center type
                    l.t = None
                    l.active = False
                    continue

                except CenterTooFar:
                    # Center is too far from the city
                    l.t = None
                    l.active = False
                    if self.debug:
                        print(f"Infeasible center because too far from the city c({c.x}, {c.y}) -> l({l.x, l.y})")
                    raise Infeasible

            if l.t == None:
                if self.debug:
                    print(f"Infeasible new center because of capacity c({c.x}, {c.y}) -> l({l.x, l.y})")
                raise Infeasible
            else:
                return l.cost

    def solve(self):
        solutions = []
        alpha = 0
        for iter_idx in range(3):
            self.cities = copy.deepcopy(self.solution.cities)
            self.centers = copy.deepcopy(self.solution.centers)
            self.types = copy.deepcopy(self.solution.types)
            for c in self.cities:
                costs_primary = []
                costs_secondary = []
                for l in self.centers:
                    try:
                        costs_primary.append(
                            (l, self.cost_and_update(c, l, primary=True))
                            )
                    except Infeasible:
                        pass

                    try:
                        costs_secondary.append(
                            (l, self.cost_and_update(c, l, primary=False))
                            )
                    except Infeasible:
                        pass

                if len(costs_primary) == 0:
                    print(f"Can not assign a primary center to city ({c.x}, {c.y})!")
                    raise Infeasible

                if len(costs_secondary) == 0:
                    print(f"Can not assign a secondary center to city ({c.x}, {c.y})!")
                    raise Infeasible

                sorted_costs_p_raw = sorted(costs_primary, key=lambda x: x[1])
                sorted_costs_s_raw = sorted(costs_secondary, key=lambda x: x[1])

                qmin_primary = sorted_costs_p_raw[0][1]
                qmax_primary = sorted_costs_p_raw[-1][1]
                sorted_costs_p = [
                    x for x in sorted_costs_p_raw 
                    if x[1] <= (qmin_primary + alpha * (qmax_primary - qmin_primary))
                    ]


                pc_idx = random.randint(0, len(sorted_costs_p) - 1)
                primary_center_assigned = sorted_costs_p[pc_idx][0]

                print(f"City ({c.x}, {c.y}) assigned PC at ({primary_center_assigned.x},"
                      f" {primary_center_assigned.y}). Type {primary_center_assigned.t.tid}")
                if not primary_center_assigned.active:
                    primary_center_assigned.activate(self.centers, self.d_center)

                # XXX
                try:
                    primary_center_assigned.add_city_primary(c)
                except:
                    continue

                qmin_secondary = sorted_costs_s_raw[0][1]
                qmax_secondary = sorted_costs_s_raw[-1][1]
                sorted_costs_s = [
                    x for x in sorted_costs_s_raw 
                    if x[1] <= (qmin_secondary + alpha * (qmax_secondary - qmin_secondary))
                    ]


                sc_idx = random.randint(0, len(sorted_costs_p) - 1)
                sc_found = False
                for i in range(len(sorted_costs_s)):
                    secondary_center_assigned = \
                        sorted_costs_s[(sc_idx + i) % len(sorted_costs_s)][0]
                    activated = False
                    try:
                        if not secondary_center_assigned.active:
                            activated = True
                            secondary_center_assigned.activate(
                                self.centers, self.d_center
                                )
                        secondary_center_assigned.add_city_secondary(c)
                        sc_found = True
                        break
                    except CenterTooClose:
                        secondary_center_assigned.active = False
                        continue
                    except AlreadyPrimaryCenter:
                        if activated:
                            # Deactivate
                            secondary_center_assigned.active = False
                        continue

                if not sc_found:
                    print(f"Not feasible secondary center for city {c.coordinates}")

                print(f"City ({c.x}, {c.y}) assigned SC at ({secondary_center_assigned.x},"
                      f" {secondary_center_assigned.y}). Type {secondary_center_assigned.t.tid}")

            print(f"End of iteration {iter_idx} with alpha {alpha}")
            solutions.append(Solution(self.cities, self.centers, self.types))
            alpha += 0.1

        min_cost = float("inf")
        best_solution = None
        for s in solutions:
            if s.cost < min_cost:
                best_solution = s

        return best_solution
