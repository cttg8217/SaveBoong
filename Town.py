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

            self.money += building.money
            building.money = 0

            self.boong += building.boong
            building.boong = 0

        self.total_happiness = total_happiness
        self.max_population = max_population
        print(self.total_happiness, self.max_population)

    def build(self, map_pos, building_name):
        build_price = data[building_name]['upgrade_price'][0]
        build_time = data[building_name]['upgrade_time'][0]
        class_name = data[building_name]['class_name']
        self.money -= build_price

        new_building = eval(f'Building.{class_name}')(map_pos, left_time=build_time)

        self.building_list.append(new_building)
        self.building_map[map_pos] = new_building
        self.is_building[map_pos] = True

        return new_building

    @property
    def happiness(self):
        return self.total_happiness // self.population
