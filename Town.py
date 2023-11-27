import Building


class Town:
    def __init__(self, name, building_list):
        self.name = name
        self.building_list = building_list
        self.is_building = {
            (x, y): False for x in range(-13, 13) for y in range(-13, 13)
        }
        for building in self.building_list:
            self.is_building[building.map_pos] = True

    def update_second(self):
        for building in self.building_list:
            building.update_second()
