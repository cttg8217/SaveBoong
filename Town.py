import Building
from building_data import data


class Town:
    def __init__(self, name, building_list, population=0, money=0, boong=0):
        self.name = name
        self.building_list = building_list
        self.is_building = {
            (x, y): False for x in range(-13, 13) for y in range(-13, 13)
        }
        self.building_map = {}

        for building in self.building_list:
            self.is_building[building.map_pos] = True
            self.building_map[building.map_pos] = building

        self.total_happiness = 0
        self.max_population = 0
        self.population = population
        self.money = money
        self.boong = boong

    def update_second(self):
        for building in self.building_list:
            building.update_second()

        total_happiness = 0
        max_population = 0
        for building in self.building_list:
            total_happiness += building.total_happiness
            max_population += building.max_population

        self.total_happiness = total_happiness
        self.max_population = max_population
        print(self.total_happiness, self.max_population)
