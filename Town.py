import Building
from building_data import data
import random

earthquake_probability = 0.1
earthquake_time = 60


class Town:
    def __init__(self, name, building_list, population=0, money=0, boong=0):
        self.name = name
        self.building_list = building_list
        self.is_building = {
            (x, y): False for x in range(-13, 13) for y in range(-13, 13)
        }
        self.buildable = {
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

        self.earthquake_left_time = earthquake_time
        self.earthquake_checked = True
        self.earthquake_harm = False

        self.popup_list = []

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

            if building.boong > 0:
                self.popup_list.append('find_boong')
            self.boong += building.boong
            building.boong = 0

        self.total_happiness = total_happiness
        self.max_population = max_population

        self.earthquake_left_time -= 1
        if self.earthquake_left_time <= 0:
            self.earthquake_left_time = earthquake_time
            self.earthquake()

        self.buildable_area_check()

    def buildable_area_check(self):
        for building in self.building_list:
            if 'house_range' not in building.data.keys():
                continue
            house_range = building.data['house_range'][building.level-1]
            center_x, center_y = building.map_pos
            for d_x in range(-house_range, house_range+1):
                for d_y in range(-house_range+abs(d_x), house_range-abs(d_x)+1):
                    map_pos = (center_x+d_x, center_y+d_y)
                    self.buildable[map_pos] = True

    def build(self, map_pos, building_name):
        build_price = data[building_name]['upgrade_price'][0]
        build_time = data[building_name]['upgrade_time'][0]
        class_name = data[building_name]['class_name']
        self.money -= build_price

        new_building = eval(f'Building.{class_name}')(map_pos, level=1, is_upgrading=True, left_time=build_time)

        self.building_list.append(new_building)
        self.building_map[map_pos] = new_building
        self.is_building[map_pos] = True

        return new_building

    @property
    def happiness(self):
        return self.total_happiness // self.population

    def earthquake(self):
        earthquake_harm = False
        for building in self.building_list:
            if building.is_upgrading:
                continue
            if building.type_id == 'town_center':
                continue
            if random.random() < earthquake_probability:
                building.is_earthquake = True
                earthquake_harm = True

        if earthquake_harm:
            self.popup_list.append('earthquake_fix')
        else:
            self.popup_list.append('earthquake_safe')

