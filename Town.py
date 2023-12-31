import Building
from building_data import data
import random

# 지진 발생 확률, 주기
earthquake_probability = 0.1
earthquake_time = 60


# 마을 클래스
class Town:
    def __init__(self, building_list, population=0, money=0, boong=0):
        self.building_list = building_list
        self.is_building = {  # (x, y) 위치별 건물 있는지 확인
            (x, y): False for x in range(-13, 13) for y in range(-13, 13)
        }
        self.buildable = {  # (x, y) 위치별 건설 가능한 지 확인
            (x, y): False for x in range(-13, 13) for y in range(-13, 13)
        }
        self.building_map = {}
        self.school_exists = False

        for building in self.building_list:  # 빌딩별로 is_building, building_map 설정
            self.is_building[building.map_pos] = True
            self.building_map[building.map_pos] = building
            if isinstance(building, Building.School):
                self.school_exists = True

        # 마을 관련 데이터 변수들
        self.total_happiness = 0
        self.max_population = 0
        self.population = population
        self.money = money
        self.boong = boong
        self.cat_boong = 0
        self.graduates = 0

        self.earthquake_left_time = earthquake_time
        self.earthquake_checked = True

        self.popup_list = []

        self.productivity = 1
        self.build_speed = 1
        self.repair_price_ratio = 1

        self.is_research_done = False

        self.cat_left_time = 90
        self.cat_show = False

    # 1초마다 실행되는 메서드.
    def update_second(self):
        for building in self.building_list:  # 건물마다 update 돌림.
            building.update_second()

        if Building.Laboratory.is_research_in_progress:  # 연구소 연구 처리
            Building.Laboratory.research_second()

        if not self.is_research_done and Building.Laboratory.is_research_done:
            self.is_research_done = True
            self.popup_list.append('research_success')

        total_happiness = 0
        max_population = 0

        productivity = 1
        build_speed = 1
        repair_price = 1
        # 데이터 변수 합산, 생산력, 건설 속도, 수리 비용 감소 효과 고려
        for building in self.building_list:
            total_happiness += building.total_happiness
            max_population += building.max_population

            self.money += building.money * self.productivity
            building.money = 0

            self.boong += building.boong
            building.boong = 0

            self.graduates += building.graduates
            building.graduates = 0

            if building.is_upgrading:
                effect_level = building.level - 1
            else:
                effect_level = building.level
            if effect_level > 0:
                if 'productivity_increase' in building.data.keys():
                    productivity += building.data['productivity_increase'][effect_level-1]

                if 'build_speed_increase' in building.data.keys():
                    build_speed += building.data['build_speed_increase'][effect_level-1]

                if 'repair_price_reduction' in building.data.keys():
                    repair_price -= building.data['repair_price_reduction'][effect_level-1]
                    if repair_price <= 0:
                        repair_price = 0

        self.total_happiness = total_happiness
        self.max_population = max_population
        
        self.change_population()

        self.productivity = productivity
        self.build_speed = build_speed
        self.repair_price_ratio = repair_price
        
        # 지진 효과 발생
        self.earthquake_left_time -= 1
        if self.earthquake_left_time <= 0:
            self.earthquake_left_time = earthquake_time
            self.earthquake()
        
        # 건설 가능 범위 업데이트
        self.buildable_area_check()
        
        # 고양이 보임 관련 업데이트
        self.cat_left_time -= 1
        if self.cat_left_time == 0:
            self.cat_show = True
    
    # 건설 범위를 넓혀주는 건물들에 대해 범위 확인, dict에 저장.
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
    
    # 특정한 건물을 특정 위치에 건설.
    def build(self, map_pos, building_name):
        # 가격, 시간 등 계산
        build_price = data[building_name]['upgrade_price'][0]
        build_time = data[building_name]['upgrade_time'][0] / self.build_speed
        class_name = data[building_name]['class_name']
        self.money -= build_price
        
        # eval을 이용해 이름으로부터 클래스 생성
        new_building = eval(f'Building.{class_name}')(map_pos, level=1, is_upgrading=True, left_time=build_time)

        self.building_list.append(new_building)
        self.building_map[map_pos] = new_building
        self.is_building[map_pos] = True

        if isinstance(new_building, Building.School):
            self.school_exists = True

        return new_building
    
    # 행복도 = 전체 행복도 / 인구
    @property
    def happiness(self):
        return self.total_happiness // self.population

    # 지진 발생시키기. 
    def earthquake(self):
        earthquake_harm = False #지진이 피해를 줬는지 기록.
        for building in self.building_list:
            if building.is_upgrading:
                continue
            if building.type_id in ['town_center', 'weather_center']:
                continue
            if random.random() < earthquake_probability:
                building.is_earthquake = True
                earthquake_harm = True
        
        # 지진 관련 팝업 띄움
        if earthquake_harm:
            self.popup_list.append('earthquake_fix')
        else:
            self.popup_list.append('earthquake_safe')
    
    # 빌딩 업그레이드
    def upgrade_building(self, building):
        self.money -= building.data['upgrade_price'][building.level]
        building.set_upgrade(self.build_speed)
    
    # 빌딩 수리
    def repair_building(self, building):
        repair_cost = self.repair_price_ratio * building.total_price / 5
        self.money -= repair_cost
        building.is_earthquake = False
 
    # 행복도에 따라 인구 변화
    def change_population(self):
        if self.happiness < 10:
            min_d_population = -100
        elif self.happiness < 20:
            min_d_population = -50
        elif 61 < self.happiness < 85:
            min_d_population = 100
        elif 85 <= self.happiness:
            min_d_population = 200
        else:
            min_d_population = 0

        self.population += min_d_population / 60
        self.population = min(self.population, self.max_population)

    # 공장 제작 물품 개수
    @property
    def products(self):
        return Building.Factory.product_count
