from models import City, LogisticCenterLocation, LogisticCenterType

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
    LogisticCenterType(1, 18, 2, 50),
    LogisticCenterType(2, 14, 4, 45),
    LogisticCenterType(3, 5, 7, 15)
]

d_center = 1.2
