from abc import *
import random


class Building(metaclass=ABCMeta):
    def __init__(self, name, map_pos, type_id, level=1, is_upgrading=True, left_time=0):
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
        if self.left_time == 0:
            self.is_upgrading = False

    @abstractmethod
    def action_second(self):
        pass


class Hospital(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('병원', map_pos, 'hospital', level, is_upgrading, left_time)

    def action_second(self):
        pass


class School(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('학교', map_pos, 'school', level, is_upgrading, left_time)
        self.passed_seconds = 0
        self.graduates = 0
        self.productivity_increase = 0

    def action_second(self):
        self.passed_seconds += 1
        if self.passed_seconds == 60:
            self.passed_seconds = 0

            new_graduates = data['School']['graduate_per_min'][self.level - 1]
            self.graduates += new_graduates

        self.productivity_increase = data['School']['productivity_increase'][self.level - 1]


class House(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('집', map_pos, 'house', level, is_upgrading, left_time)
        self.max_population = data['House']['population'][self.level - 1]

    def action_second(self):
        self.max_population = data['House']['population'][self.level - 1]


class Library(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('도서관', map_pos, 'library', level, is_upgrading, left_time)
        self.build_speed_increase = data['Library']['build_speed_increase'][self.level - 1]

    def action_second(self):
        self.build_speed_increase = data['Library']['build_speed_increase'][self.level - 1]


class Shop(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('붕어빵 가게', map_pos, 'shop', level, is_upgrading, left_time)
        self.money = 0
        self.boong = 0
        self.passed_seconds = 0

    def action_second(self):
        new_money = data['Shop']['money'][self.level - 1]
        new_boong = data['Shop']['boong'][self.level - 1]

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
        new_money = data['Stadium']['money'][self.level - 1]

        self.passed_seconds += 1
        if self.passed_seconds == 60:
            self.passed_seconds = 0

            self.money += new_money


class Park(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('공원', map_pos, 'park', level, is_upgrading, left_time)

    def action_second(self):
        pass


class WeatherCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('기상청', map_pos, 'weather_center', level, is_upgrading, left_time)
        self.reduce_repair_cost = data['weather_center']['repair_cost_reduction'][self.level - 1]

    def action_second(self):
        self.reduce_repair_cost = data['weather_center']['repair_cost_reduction'][self.level - 1]
        pass


class Laboratory(Building):
    is_research_done = {
        'toy': False
    }
    is_research_in_progress = {
        'toy': False
    }
    research_time_left = {
        'toy': 0
    }

    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('연구소', map_pos, 'laboratory', level, is_upgrading, left_time)

    def start_research(self, item):
        Laboratory.is_research_in_progress[item] = True
        Laboratory.research_time_left[item] = data['Laboratory']['research_time'][item]

    def action_second(self):
        for item in Laboratory.is_research_in_progress.keys():
            if Laboratory.is_research_in_progress[item]:
                Laboratory.research_time_left[item] -= 1

                if Laboratory.research_time_left[item] == 0:
                    Laboratory.is_research_in_progress[item] = False

                    if random.random() < data['Laboratory']['research_probability']:
                        Laboratory.is_research_done[item] = True


class Factory(Building):
    #TODO: Fix
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('공장', map_pos, 'factory', level, is_upgrading, left_time)
        self.toys = 0
        self.cost_of_toy = 100
        self.new_toys = 10
        self.production_time_toy = 30
        self.production_in_progress_toy = False

    def start_production_toy(self):
        self.production_in_progress_toy = True

    def action_second(self):
        if self.production_in_progress_toy == True:
            self.passed_seconds += 1
            if self.passed_seconds == self.production_time_toy:
                self.passed_seconds = 0
                self.production_in_progress_toy = False

                self.toys += self.new_toys


# research_toy가 True이면 돈을 지불 가능, 돈을 지불한 후 부터 30초동안 장난감 10개를 만들어내는 코드


data = {
    'Hospital': {
        'max_level': 4,
        'upgrade_price': [500, 600, 700, 800],
        'upgrade_time': [60, 90, 180, 240],
        'total_happiness': [25, 50, 100, 200],
    },
    'School': {
        'max_level': 2,
        'upgrade_price': [500, 1000],
        'upgrade_time': [90, 180],
        'total_happiness': [200, 400],
        'productivity_increase': [0.1, 0.2],
        'graduate_per_min': [10, 20],
    },
    'House': {
        'max_level': 4,
        'upgrade_price': [200, 400, 1200, 3000],
        'upgrade_time': [5, 10, 30, 60],
        'total_happiness': [50, 150, 400, 1500],
        'population': [5, 15, 30, 100]
    },
    'Library': {
        'max_level': 2,
        'upgrade_price': [1200, 1600],
        'upgrade_time': [180, 240],
        'total_happiness': [],
        'build_speed_increase': [0.1, 0.2]
    },
    'Shop': {
        'max_level': 4,
        'upgrade_price': [50, 100, 250, 1000],
        'upgrade_time': [10, 20, 40, 70],
        'total_happiness': [],
        'money': [20, 40, 60, 80],
        'boong': [0, 1, 3, 5]
    },
    'Stadium': {
        'max_level': 1,
        'upgrade_price': [5000],
        'upgrade_time': [300],
        'total_happiness': [],
        'money': [200]
    },
    'Park': {
        'max_level': 2,
        'upgrading_price': [2000, 3000],
        'upgrading_time': [30, 40],
        'total_happiness': []
    },
    'weather_center': {
        'max_level': 2,
        'upgrading_price': [3000, 4000],
        'upgrading_time': [150, 210],
        'total_happiness': [],
        'repair_cost_reduction': [0.05, 0.15]
    },
    'Laboratory': {
        'max_level': 1,
        'upgrading_price': [1750],
        'upgrading_time': [240],
        'total_happiness': [],
        'research_time': {
            'toy': 30,
        },
        'research_cost': {
            'toy': 1000,
        },
        'research_probability': {
            'toy': 0.3,
        }
    },
    'Factory': {
        'max_level': 1,
        'upgrading_price': [2000],
        'upgrading_time': [120],
        'total_happiness': []
    }
}
