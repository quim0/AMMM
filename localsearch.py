from models import City, LogisticCenterLocation, LogisticCenterType
from models import (CapacityExceeded, CenterTooFar, CenterTooClose,
                    AlreadyPrimaryCenter, Infeasible)

class LocalSearchSolver:
    def __init__(self, cities, centers, types, d_center):
        self.cities = cities
        self.centers = centers
        self.types = sorted(types, key=lambda x: x.cost)
        self.d_center = d_center

    def solve(self):
        out = False
        while not out:
            for idx, l in enumerate(self.centers):
                if not l.active:
                    continue

                for c in l.cities_primary:
                    # Check the cost improvement by downgrading the center and 
                    # removing the city. self.types is ordered by cost
                    original_t = l.t
                    next_t = None
                    for t in self.types:
                        if t.tid != l.t.tid:
                            ok = l.check_cost_improve(c, t, primary=True)
                            if ok:
                                next_t = t
                                break

                    if next_t is None:
                        # Can not downgrade the center
                        continue
                    else:
                        # Can downgrade the center yay :D
                        # Check if the city can be assigned to another center
                        for l2 in self.centers:
                            if l == l2 or not l2.active:
                                continue
                            try:
                                # TODO: Do more iterations?
                                # Remove the city from the old logistic center
                                # (l) and add it to the new (l2). Update the old
                                # logistic center type
                                l2.add_city_primary(c)
                                print(f"Downgrading center {l.coordinates} from"
                                      f" type {l.t.tid} to {next_t.tid}")
                                print(f"Changing city ({c.coordinates}) primary"
                                      f" center from {l.coordinates} to "
                                      f"{l2.coordinates}")

                                # Make sure PC is updated in cities object
                                for cidx, c2 in enumerate(self.cities):
                                    if c2 == c:
                                        self.cities[cidx].pc = l2

                                self.centers[idx].cities_primary = [
                                    x for x in l.cities_primary if x != c
                                    ]
                                self.centers[idx].t = next_t
                                out = True
                                break

                            except CenterTooFar:
                                continue
                            except CapacityExceeded:
                                continue

            # Same but with secondary cities
            for idx, l in enumerate(self.centers):
                if not l.active:
                    continue

                for c in l.cities_secondary:
                    # Check the cost improvement by downgrading the center and 
                    # removing the city. self.types is ordered by cost
                    original_t = l.t
                    next_t = None
                    for t in self.types:
                        if t.tid != l.t.tid:
                            ok = l.check_cost_improve(c, t, primary=False)
                            if ok:
                                next_t = t
                                break

                    if next_t is None:
                        # Can not downgrade the center
                        continue
                    else:
                        # Can downgrade the center yay :D
                        # Check if the city can be assigned to another center
                        for l2 in self.centers:
                            if l == l2 or not l2.active:
                                continue
                            try:
                                # TODO: Do more iterations?
                                # Remove the city from the old logistic center
                                # (l) and add it to the new (l2). Update the old
                                # logistic center type
                                l2.add_city_secondary(c)
                                print(f"Downgrading center {l.coordinates} from"
                                      f" type {l.t.tid} to {next_t.tid}")
                                print(f"Changing city ({c.coordinates}) secondary"
                                      f" center from {l.coordinates} to "
                                      f"{l2.coordinates}")

                                # Make sure PC is updated in cities object
                                for cidx, c2 in enumerate(self.cities):
                                    if c2 == c:
                                        self.cities[cidx].pc = l2

                                self.centers[idx].cities_secondary = [
                                    x for x in l.cities_secondary if x != c
                                    ]
                                self.centers[idx].t = next_t
                                out = True
                                break

                            except CenterTooFar:
                                continue
                            except CapacityExceeded:
                                continue
