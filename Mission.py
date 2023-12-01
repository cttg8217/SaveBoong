import Building


# 미션 클래스
class Mission:
    def __init__(self, town, is_done_func):
        self.town = town
        self.is_done_func = is_done_func  # town을 받아 그 town이 조건을 충족시키는지 확인하는 함수를 인스턴스 변수로 가지고 있다.

    @property
    def is_done(self): # 해당 미션 완료 여부 체크
        return self.is_done_func(self.town)


# 각종 미션을 위한 함수들

def check_cat_boong(town):
    if town.cat_boong >= 10:
        return True
    return False


def stadium_exists(town):
    for building in town.building_list:
        if isinstance(building, Building.Stadium):
            return True
    return False


def research_done(town):
    return town.is_research_done


def check_toys(town):
    return town.products >= 50


def work_center_exists(town):
    for building in town.building_list:
        if isinstance(building, Building.WorkCenter):
            return True
    return False


def art_center_exists(town):
    for building in town.building_list:
        if isinstance(building, Building.ArtCenter):
            return True
    return False


def check_graduates(town):
    return town.graduates >= 500


# 위에서 만든 함수들의 리스트.
check_func_list = [check_cat_boong, stadium_exists, research_done, check_toys, work_center_exists, art_center_exists, check_graduates]
