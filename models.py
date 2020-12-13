import math
import io
import copy

def distance(a, b):
    return math.sqrt(math.pow((a[0] - b[0]), 2) + math.pow((a[1] - b[1]), 2))

# ---- EXCEPTIONS ------
class CapacityExceeded(Exception):
    pass

class CenterTooFar(Exception):
    pass

class CenterTooClose(Exception):
    pass

class AlreadyPrimaryCenter(Exception):
    pass

class Infeasible(Exception):
    pass

# ---- MODELS ----
class City:
    def __init__(self, x, y, population):
        self.x = x
        self.y = y
        self.population = population
        # Primary center
        self.pc = None
        self.sc = None

    @property
    def coordinates(self):
        return (self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class LogisticCenterLocation:
    def __init__(self, x, y, t=None):
        self.x = x
        self.y = y
        self.t = t
        self.cities_primary = []
        self.cities_secondary = []
        # Indicates if there's an actual logistic center or not
        self.active = False

    @property
    def cost(self):
        return self.t.cost

    @property
    def coordinates(self):
        return (self.x, self.y)

    @property
    def curr_load(self):
        return sum([x.population for x in self.cities_primary]) \
               + 0.1 * sum([x.population for x in self.cities_secondary])

    def activate(self, locations, d_center):
        for l in locations:
            if l.active and (distance(self.coordinates, l.coordinates) < d_center):
                raise CenterTooClose

        self.active = True

    def next_load_with_city_primary(self, city):
        return sum(
            [x.population for x in self.cities_primary] + [city.population]
            ) + 0.1 * sum([x.population for x in self.cities_secondary])

    def next_load_without_city_primary(self, city):
        return sum(
            [x.population for x in self.cities_primary]) - city.population \
             + 0.1 * sum([x.population for x in self.cities_secondary])

    def next_load_with_city_secondary(self, city):
        return sum([x.population for x in self.cities_primary]) + 0.1 * sum(
                        [x.population for x in self.cities_secondary] 
                        + [city.population]
                        )

    def next_load_without_city_secondary(self, city):
        return sum([x.population for x in self.cities_primary]) \
               + 0.1 * sum([x.population for x in self.cities_secondary]) \
                        - city.population

    def is_primary(self, x, y):
        for c in self.cities_primary:
            if c.x == x and c.y == y:
                return True
        return False

    def is_secondary(self, x, y):
        for c in self.cities_secondary:
            if c.x == x and c.y == y:
                return True
        return False

    def check_city_primary(self, city):
        if (distance(self.coordinates, city.coordinates) > self.t.working_d):
            raise CenterTooFar
        if (self.next_load_with_city_primary(city) > self.t.cap):
            raise CapacityExceeded
        return True

    def check_city_secondary(self, city):
        if self.is_primary(city.x, city.y):
            raise AlreadyPrimaryCenter
        if (distance(self.coordinates, city.coordinates) > 3*self.t.working_d):
            raise CenterTooFar
        if (self.next_load_with_city_secondary(city) > self.t.cap):
            raise CapacityExceeded
        return True

    def add_city_primary(self, city):
        if (distance(self.coordinates, city.coordinates) > self.t.working_d):
            raise CenterTooFar
        if (self.next_load_with_city_primary(city) > self.t.cap):
            raise CapacityExceeded
        self.cities_primary.append(city)
        city.pc = self

    def add_city_secondary(self, city):
        if self.is_primary(city.x, city.y):
            raise AlreadyPrimaryCenter
        if (distance(self.coordinates, city.coordinates) > 3*self.t.working_d):
            raise CenterTooFar
        if (self.next_load_with_city_secondary(city) > self.t.cap):
            raise CapacityExceeded
        self.cities_secondary.append(city)
        city.sc = self

    def check_cost_improve(self, city, t, primary=True):
        # Check if cost can be improve by removing city and assigning the center
        # to type t.
        if primary:
            next_load = self.next_load_without_city_primary(city)
        else:
            next_load = self.next_load_without_city_secondary(city)

        if t.cost < self.t.cost and t.cap >= next_load:
            # Center can be downgraded without the city
            return True
        return False

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class LogisticCenterType:
    def __init__(self, tid, cap, working_d, cost):
        self.tid = tid
        self.cap = cap
        self.working_d = working_d
        self.cost = cost

    def __eq__(self, other):
        return self.tid == other.tid

class Solution:
    def __init__(self, cities, centers, types):
        self.cities = copy.deepcopy(cities)
        self.centers = copy.deepcopy(centers)
        self.types = copy.deepcopy(types)

    @property
    def cost(self):
        total_cost = 0
        for l in centers:
            if l.active:
                total_cost += l.cost
        return total_cost

    def __str__(self):
        str_buf = io.StringIO()
        for idx, c in enumerate(self.cities):
            str_buf.write(f"City {idx} {c.x, c.y}:\n")
            str_buf.write(f"\tPrimary center: ({c.pc.x}, {c.pc.y}) of type "
                          f"{c.pc.t.tid}\n")
            str_buf.write(f"\tSecondary center: ({c.sc.x}, {c.sc.y}) of type "
                          f"{c.sc.t.tid}\n")

        total_cost = 0
        for idx, l in enumerate(self.centers):
            if l.active:
                str_buf.write(
                    f"Location {idx}, has a center of type {l.t.tid}.\n"
                    )
                total_cost += l.cost
        str_buf.write(f"Total cost: {total_cost}\n")
        return str_buf.getvalue()
