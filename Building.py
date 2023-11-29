from abc import *
import random
from building_data import data


class Building(metaclass=ABCMeta):
    def __init__(self, name, map_pos, type_id, level=1, is_upgrading=True, left_time=0):
        self.data = data[type_id]
        self.name = name
        self.map_pos = map_pos
        self.type_id = type_id
        self.connected_sprite = None
        self.level = level
        self.is_upgrading = is_upgrading
        self.left_time = left_time

    def set_upgrade(self):
        self.level += 1
        self.is_upgrading = True
        self.left_time = data[self.name]['upgrade_time'][self.level - 1]

    def update_second(self):
        if self.is_upgrading:
            self.upgrade_second()
        else:
            self.action_second()

    def upgrade_second(self):
        self.left_time -= 1
        if self.left_time <= 0:
            self.is_upgrading = False

    def action_second(self):
        pass

    @property
    def total_happiness(self):
        if not self.is_upgrading:
            return self.data['total_happiness'][self.level - 1]
        return 0

    @property
    def max_population(self):
        if not self.is_upgrading and 'max_population' in self.data.keys():
            return self.data['max_population'][self.level - 1]
        return 0


class TownCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('마을 회관', map_pos, 'town_center', level, is_upgrading, left_time)


class Hospital(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('병원', map_pos, 'hospital', level, is_upgrading, left_time)


class School(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('학교', map_pos, 'school', level, is_upgrading, left_time)
        self.passed_seconds = 0
        self.graduates = 0

    def action_second(self):
        self.passed_seconds += 1
        if self.passed_seconds == 60:
            self.passed_seconds = 0

            new_graduates = self.data['graduate_per_min'][self.level - 1]
            self.graduates += new_graduates


class House(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('집', map_pos, 'house', level, is_upgrading, left_time)


class Library(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('도서관', map_pos, 'library', level, is_upgrading, left_time)


class Shop(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('붕어빵 가게', map_pos, 'shop', level, is_upgrading, left_time)
        self.money = 0
        self.boong = 0
        self.passed_seconds = 0

    def action_second(self):
        new_money = self.data['money'][self.level - 1]
        new_boong = self.data['boong'][self.level - 1]

        self.passed_seconds += 1
        if self.passed_seconds == 60:
            self.passed_seconds = 0

            self.money += new_money
            self.boong += new_boong


class Stadium(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('붕어빵 스타디움', map_pos, 'stadium', level, is_upgrading, left_time)
        self.money = 0
        self.passed_seconds = 0

    def action_second(self):
        new_money = self.data['money'][self.level - 1]

        self.passed_seconds += 1
        if self.passed_seconds == 60:
            self.passed_seconds = 0

            self.money += new_money


class Park(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('공원', map_pos, 'park', level, is_upgrading, left_time)


class WeatherCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('기상청', map_pos, 'weather_center', level, is_upgrading, left_time)


class Laboratory(Building):
    is_research_done = False
    is_research_in_progress = False
    research_time_left = 0

    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('연구소', map_pos, 'laboratory', level, is_upgrading, left_time)

    def start_research(self, item):
        Laboratory.is_research_in_progress = True
        Laboratory.research_time_left = self.data['research_time']

    def action_second(self):
        if Laboratory.is_research_in_progress:
            Laboratory.research_time_left -= 1

            if Laboratory.research_time_left == 0:
                Laboratory.is_research_in_progress = False

                if random.random() < self.data['research_probability']:
                    Laboratory.is_research_done = True


class Factory(Building):
    product_count = 0

    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('공장', map_pos, 'factory', level, is_upgrading, left_time)
        self.is_production_in_progress = False
        self.production_time_left = 0

    def start_production_toy(self):
        self.is_production_in_progress = True
        self.production_time_left = self.data['manufacture_time']

    def action_second(self):
        if self.is_production_in_progress:
            self.production_time_left -= 1
            if self.production_time_left <= 0:
                self.is_production_in_progress = False
                Factory.product_count += self.data['manufacture_count']
