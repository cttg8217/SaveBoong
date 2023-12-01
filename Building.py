from abc import *
import random
from building_data import data  # 건물에 대한 모든 수치값은 이 파일에 하드코딩 해두었다.

# 건축 도중 붕어빵을 획득할 확률
boong_probability = 0.15


# 마을 내의 건물을 위한 추상 클래스
class Building(metaclass=ABCMeta):
    def __init__(self, name, map_pos, type_id, level=1, is_upgrading=False, left_time=0, is_earthquake=False):
        self.data = data[type_id]  # 데이터 파일에서 자신의 데이터만을 취한다.
        self.name = name  # 건물의 화면상 이름
        self.map_pos = map_pos  # 건물의 맵 위 위치
        self.type_id = type_id  # 건물의 게임상 아이디
        self.level = level  # 건물의 레벨
        self.is_upgrading = is_upgrading  # 현재 업그레이드 중 여부
        self.left_time = left_time  # 업그레이드 남은 시간
        self.is_earthquake = is_earthquake  # 지진이 지나갔는지 여부
        self.graduates = 0  # 졸업생 수(학교에서 사용)

        self.money = 0  # 건물의 돈
        self.boong = 0  # 건물이 발견한 붕어빵

    # 건물 자신의 업그레이드를 실행한다. build_speed: 마을의 생산력 증가 효과에 의한 생산 시간 단축 비율
    def set_upgrade(self, build_speed):
        self.level += 1
        self.is_upgrading = True
        self.left_time = data[self.type_id]['upgrade_time'][self.level - 1] / build_speed

    # 매 초마다 실행되는 건물의 메서드. 1초 경과마다 건물의 작동을 제어한다.
    def update_second(self):
        if self.is_upgrading:
            self.upgrade_second()
        elif not self.is_earthquake:
            self.action_second()

    # 업그레이드를 1초 진행시킨다.
    def upgrade_second(self):
        print(self.left_time)
        self.left_time -= 1
        if self.left_time <= 0:
            self.is_upgrading = False
            if random.random() < boong_probability: # 완료 시 일정 확률로 붕어빵을 얻는다.
                self.boong += 1

    # 건물에서 1초 경과마다 호출되는 함수이다. Building 클래스를 상속한 후 건물마다 오버라이딩해서 사용한다.
    def action_second(self):
        pass

    # 건물이 주는 전체 행복도를 자신의 데이터를 참조해 반환한다.
    @property  # property 데코레이터: 메서드를 인스턴스 변수처럼 참조할 수 있도록 한다.
    def total_happiness(self):
        if not self.is_upgrading:
            return self.data['total_happiness'][self.level - 1]
        return 0

    # 건물의 수용 가능 인원을 자신의 데이터를 참조해 반환한다.
    @property
    def max_population(self):
        if not self.is_upgrading and 'max_population' in self.data.keys():
            return self.data['max_population'][self.level - 1]
        return 0

    # 건물이 업그레이드 중이거나 지진이 지나갔으면 사용이 불가능하기 때문에 사용 가능한지를 반환한다.
    @property
    def is_available(self):
        if self.is_upgrading or self.is_earthquake:
            return False
        return True

    # 건물이 최대 레벨인지를 반환한다.
    @property
    def is_max_level(self):
        return self.level == self.data['max_level']

    # 건물의 설립부터 현재 레벨까지 업그레이드 가격을 모두 더한 전체 가격
    @property
    def total_price(self):
        total_price = 0
        for i in range(self.level):
            total_price += self.data['upgrade_price'][i]
        return total_price


# 마을 회관 건물
class TownCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('마을 회관', map_pos, 'town_center', level, is_upgrading, left_time, is_earthquake)


# 집 건물
class House(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('집', map_pos, 'house', level, is_upgrading, left_time, is_earthquake)


# 병원 건물
class Hospital(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('병원', map_pos, 'hospital', level, is_upgrading, left_time, is_earthquake)


# 학교 건물
class School(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('학교', map_pos, 'school', level, is_upgrading, left_time, is_earthquake)
        self.passed_seconds = 0  # 졸업시킬 시간을 정하기 위한 시간 경과 확인 변수
        self.graduates = 0  # 졸업생 수

    def action_second(self):
        self.passed_seconds += 1
        if self.passed_seconds == 60:  # 60초가 지나면 졸업생을 지정된 수만큼 늘린다.
            self.passed_seconds = 0

            new_graduates = self.data['graduates_per_min'][self.level - 1]
            self.graduates += new_graduates


# 도서관 건물
class Library(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('도서관', map_pos, 'library', level, is_upgrading, left_time, is_earthquake)


# 가게 건물
class Shop(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('붕어빵 가게', map_pos, 'shop', level, is_upgrading, left_time, is_earthquake)
        self.money = 0
        self.passed_seconds = 0

    def action_second(self):  # 매초 들어오는 가게의 수입 구현
        new_money = self.data['money_per_min'][self.level - 1] / 60
        self.money += new_money


# 붕어빵 스타디움 건물
class Stadium(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('붕어빵 스타디움', map_pos, 'stadium', level, is_upgrading, left_time, is_earthquake)
        self.money = 0
        self.passed_seconds = 0

    def action_second(self):  # 스타디움의 수익 구현
        money_per_min = self.data['money_per_min'][self.level - 1]
        new_money = money_per_min // 60
        self.money += new_money


# 공원 건물
class Park(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('공원', map_pos, 'park', level, is_upgrading, left_time, is_earthquake)


# 기상청 건물
class WeatherCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('기상청', map_pos, 'weather_center', level, is_upgrading, left_time, is_earthquake)


# 연구소 건물
class Laboratory(Building):
    is_research_done = False  # 연구 진행 여부는 모든 연구소가 공유하고, 클래스 변수로 두었다.
    is_research_in_progress = False
    research_time_left = 0

    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('연구소', map_pos, 'laboratory', level, is_upgrading, left_time, is_earthquake)

    def start_research(self):  # 연구소에서 연구를 시작
        Laboratory.is_research_in_progress = True
        Laboratory.research_time_left = self.data['research_time']

    @staticmethod  # 연구는 연구소별로 하는 것이 아니라 연구소 전체가 동시에 한다. 따라서 static method로 설정했다.
    def research_second():
        if Laboratory.is_research_in_progress:
            Laboratory.research_time_left -= 1

            if Laboratory.research_time_left == 0:  # 시간이 다 지나면 완료로 설정
                Laboratory.is_research_in_progress = False
                Laboratory.is_research_done = True


# 공장 클래스
class Factory(Building):
    product_count = 0

    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('공장', map_pos, 'factory', level, is_upgrading, left_time, is_earthquake)
        self.is_production_in_progress = False  # 생산은 공장별로 되므로 인스턴스 변수이다.
        self.production_time_left = 0

    def start_production(self):  # 장난감 생산 시작
        price = self.data['manufacture_price']
        self.money -= price
        self.is_production_in_progress = True
        self.production_time_left = self.data['manufacture_time']

    def action_second(self):  # 1초마다 장난감 생산 진행
        if self.is_production_in_progress:
            self.production_time_left -= 1
            if self.production_time_left <= 0:  # 생산 완료시 장난감 제품 개수 증가(이 개수는 클래스 변수로 관리)
                self.is_production_in_progress = False
                Factory.product_count += self.data['manufacture_count']


# 일자리 센터
class WorkCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('일자리 센터', map_pos, 'work_center', level, is_upgrading, left_time, is_earthquake)


# 예술의 전당
class ArtCenter(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0, is_earthquake=False):
        super().__init__('예술의 전당', map_pos, 'art_center', level, is_upgrading, left_time, is_earthquake)
