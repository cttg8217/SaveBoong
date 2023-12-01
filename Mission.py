import Building


class Mission:
    def __init__(self, town, is_done_func):
        self.town = town
        self.is_done_func = is_done_func

    @property
    def is_done(self):
        return self.is_done_func(self.town)


def check_cat_boong(town):
    return True


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


check_func_list = [check_cat_boong, stadium_exists, research_done, check_toys, work_center_exists, art_center_exists, check_graduates]
