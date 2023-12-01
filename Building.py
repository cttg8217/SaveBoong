from abc import *
import random
from building_data import data

boong_probability = 0.1


class Building(metaclass=ABCMeta):
    def __init__(self, name, map_pos, type_id, level=1, is_upgrading=False, left_time=0):
        self.data = data[type_id]
        self.name = name
        self.map_pos = map_pos
        self.type_id = type_id
        self.connected_sprite = None
        self.level = level
        self.is_upgrading = is_upgrading
        self.left_time = left_time
        self.is_earthquake = False
        self.graduates = 0

        self.money = 0
        self.boong = 0

    def set_upgrade(self, build_speed):
        self.level += 1
        self.is_upgrading = True
        self.left_time = data[self.type_id]['upgrade_time'][self.level - 1] / build_speed

    def update_second(self):
        if self.is_upgrading:
            self.upgrade_second()
        elif not self.is_earthquake:
            self.action_second()

    def upgrade_second(self):
        print(self.left_time)
        self.left_time -= 1
        if self.left_time <= 0:
            self.is_upgrading = False
            if random.random() < boong_probability:
                self.boong += 1

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

    @property
    def is_available(self):
        if self.is_upgrading or self.is_earthquake:
            return False
        return True

    @property
    def is_max_level(self):
        return self.level == self.data['max_level']

    @property
    def total_price(self):
        total_price = 0
        for i in range(self.level):
            total_price += self.data['upgrade_price'][i]
        return total_price


class TownCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('마을 회관', map_pos, 'town_center', level, is_upgrading, left_time)


class House(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('집', map_pos, 'house', level, is_upgrading, left_time)


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

            new_graduates = self.data['graduates_per_min'][self.level - 1]
            self.graduates += new_graduates


class Library(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('도서관', map_pos, 'library', level, is_upgrading, left_time)


class Shop(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('붕어빵 가게', map_pos, 'shop', level, is_upgrading, left_time)
        self.money = 0
        self.passed_seconds = 0

    def action_second(self):
        new_money = self.data['money_per_min'][self.level - 1] / 60
        self.money += new_money


class Stadium(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('붕어빵 스타디움', map_pos, 'stadium', level, is_upgrading, left_time)
        self.money = 0
        self.passed_seconds = 0

    def action_second(self):
        money_per_min = self.data['money_per_min'][self.level - 1]
        new_money = money_per_min // 60
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

    def start_research(self):
        Laboratory.is_research_in_progress = True
        Laboratory.research_time_left = self.data['research_time']

    def action_second(self):
        if Laboratory.is_research_in_progress:
            Laboratory.research_time_left -= 1

            if Laboratory.research_time_left == 0:
                Laboratory.is_research_in_progress = False

                Laboratory.is_research_done = True


class Factory(Building):
    product_count = 0

    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('공장', map_pos, 'factory', level, is_upgrading, left_time)
        self.is_production_in_progress = False
        self.production_time_left = 0

    def start_production(self):
        price = self.data['manufacture_price']
        self.money -= price
        self.is_production_in_progress = True
        self.production_time_left = self.data['manufacture_time']

    def action_second(self):
        if self.is_production_in_progress:
            self.production_time_left -= 1
            if self.production_time_left <= 0:
                self.is_production_in_progress = False
                Factory.product_count += self.data['manufacture_count']


class WorkCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('일자리 센터', map_pos, 'work_center', level, is_upgrading, left_time)


class ArtCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('예술의 전당', map_pos, 'art_center', level, is_upgrading, left_time)
