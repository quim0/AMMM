from models import City, LogisticCenterLocation, LogisticCenterType
from models import (CapacityExceeded, CenterTooFar, CenterTooClose,
                    AlreadyPrimaryCenter, Infeasible)

class GreedySolver:
    def __init__(self, cities, centers, types, d_center):
        self.cities = cities
        self.centers = centers
        self.types = types
        self.d_center = d_center

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
                    # print(f"Infeasible center because capacity c({c.x}, {c.y}) -> l({l.x, l.y})")
                    raise Infeasible

            except CenterTooFar:
                # print(f"Infeasible center because too far c({c.x}, {c.y}) -> l({l.x, l.y})")
                raise Infeasible

            except AlreadyPrimaryCenter:
                # print(f"Infeasible center because already primary c({c.x}, {c.y}) -> l({l.x, l.y})")
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
                    l.active = None
                    return t.cost

                except CenterTooClose:
                    # d_center not satisfied
                    l.t = None
                    l.active = False
                    # print(f"Infeasible center because too close to another center c({c.x}, {c.y}) -> l({l.x, l.y})")
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
                    # print(f"Infeasible center because too far from the city c({c.x}, {c.y}) -> l({l.x, l.y})")
                    raise Infeasible

            if l.t == None:
                # print(f"Infeasible new center because of capacity c({c.x}, {c.y}) -> l({l.x, l.y})")
                raise Infeasible
            else:
                return l.cost

    def solve(self):
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

            sorted_costs_p = sorted(costs_primary, key=lambda x: x[1])
            sorted_costs_s = sorted(costs_secondary, key=lambda x: x[1])
            primary_center_assigned = sorted_costs_p[0][0]

            print(f"City ({c.x}, {c.y}) assigned PC at ({primary_center_assigned.x},"
                  f" {primary_center_assigned.y}). Type {primary_center_assigned.t.tid}")
            if not primary_center_assigned.active:
                primary_center_assigned.activate(self.centers, self.d_center)
            primary_center_assigned.add_city_primary(c)

            secondary_center_assigned = None
            for sc in sorted_costs_s:
                try:
                    secondary_center_assigned = sc[0]
                    if not secondary_center_assigned.active:
                        secondary_center_assigned.activate(
                            self.centers, self.d_center
                            )
                    secondary_center_assigned.add_city_secondary(c)
                    break
                except CenterTooClose:
                    secondary_center_assigned.active = None
                    continue
                except AlreadyPrimaryCenter:
                    continue

            print(f"City ({c.x}, {c.y}) assigned SC at ({secondary_center_assigned.x},"
                  f" {secondary_center_assigned.y}). Type {secondary_center_assigned.t.tid}")

if __name__ == "__main__":
    """
    posCities       = [ [1 1] [2 3] [4 1] [1 2] [2 2] [0 1] [3 4] [2 4] ]; // [x,y]
    posLocations    = [ [2 3] [1 2] [1 1] [0 2] [1 3] ];                   // [x,y]
    population_city = [   5     3     6     1     2     2     3     1   ];
    """
    cities = [City(1, 1, 5), City(2, 3, 3), City(4, 1, 6), City(1, 2, 1),
              City(2, 2, 2), City(0, 1, 2), City(3, 4, 3), City(2, 4, 1)]
    centers = [
        LogisticCenterLocation(2, 3),
        LogisticCenterLocation(1, 2),
        LogisticCenterLocation(1, 1),
        LogisticCenterLocation(0, 2),
        LogisticCenterLocation(1, 3)
        ]

    """
    working_distance_center = [ 2  4  7];
 	capacity_center    = [18 14 5];
 	cost_center   = [50 45 15]; 
    """

    types = [
        LogisticCenterType(0, 18, 2, 50),
        LogisticCenterType(1, 14, 4, 45),
        LogisticCenterType(2, 5, 7, 15)
    ]

    d_center = 1.2

    gs = GreedySolver(cities, centers, types, d_center)
    gs.solve()

    print("RESULTS:")
    for idx, c in enumerate(cities):
        print(f"City {idx} ({c.x, c.y}):")
        print(f"\tPrimary center: ({c.pc.x}, {c.pc.y}) of type {c.pc.t.tid}")
        print(f"\tSecondary center: ({c.sc.x}, {c.sc.y}) of type {c.sc.t.tid}")
