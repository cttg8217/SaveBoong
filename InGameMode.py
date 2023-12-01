import pygame
from abc import *
from building_data import data
from math import ceil
import Building


# 빌딩 옵션 선택 화면, 미션 확인 화면 등 각종 게임 내 화면 상태의 부모 클래스가 되는 인게임 상의 모드 클래스.
class InGameMode(metaclass=ABCMeta):
    def __init__(self, game):
        self.game = game
        self.sprite_group = pygame.sprite.Group()  # 해당 모드에서 표시해야 하는 스프라이트 그룹

    @abstractmethod
    def handle_event(self, event):  # 이벤트가 왔을 때 처리하는 방식. 이벤트 처리 후 표시할 다음 화면을 return 한다. ex) 맵 보는 모드에서 건물을 누르면 건물 건설 모드로 이동.
        pass

    def update(self):  # 화면이 실시간으로 바뀌여야 한다면 update를 사용한다.
        pass


class InGameModeController:  # InGameMode들을 연결시켜주는 클래스.
    def __init__(self, game):
        self.game = game
        self.in_game_mode = MapView(game)  # 현재의 모드

    def handle_event(self, event):  # 이벤트를 받으면 현재 모드에서 handle시키고, 반환값을 다음 in_game_mode로 설정한다.
        next_in_game_mode = self.in_game_mode.handle_event(event)
        self.in_game_mode = next_in_game_mode

    def update(self):  # town의 popup_list는 화면에 띄울 팝업을 queue처럼 관리한다. 만약 맵을 보는 기본 화면이고 popup이 있다면 하나씩 빼서 보여준다.
        if isinstance(self.in_game_mode, MapView):
            if len(self.game.town.popup_list) != 0:
                popup_name = self.game.town.popup_list.pop(0)
                self.in_game_mode = PopupScreen(self.game, popup_name)

    def sprite_group(self):
        return self.in_game_mode.sprite_group


# 가장 기본적인, 맵을 보는 화면 클래스
class MapView(InGameMode):
    def __init__(self, game):
        super().__init__(game)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 미션 버튼 클릭 --> 미션 화면으로 이동
            if self.game.mission_button_rect.collidepoint(event.pos):
                return Missions(self.game)

            # 고양이 클릭 --> 붕어빵을 주는 사건 처리
            if self.game.town.cat_show and self.game.cat_rect.collidepoint(event.pos):
                self.game.town.cat_show = False
                self.game.town.cat_left_time = 60

                if self.game.town.boong > 0:
                    self.game.town.boong -= 1
                    self.game.town.cat_boong += 1
                    return PopupScreen(self.game, 'give_boong')
                else:
                    return PopupScreen(self.game, 'no_boong')

            building_sprite_clicked = self.game.get_building_clicked()
            if building_sprite_clicked is None:
                tile_clicked = self.game.get_tile_clicked()
                print(tile_clicked.map_pos)
                # 빈 타일 클릭 시 빈 타일 옵션 화면으로 이동
                if tile_clicked is not None:
                    tile_clicked.is_selected = True

                    map_pos = tile_clicked.map_pos
                    return EmptyTileOptions(self.game, map_pos)
            else:
                # 빌딩 클릭시 빌딩 관련 옵션 화면으로 이동
                return BuildingOptions(self.game, building_sprite_clicked.building)

        return self


# 빈 타일의 옵션
class EmptyTileOptions(InGameMode):
    def __init__(self, game, map_pos):
        super().__init__(game)
        self.map_pos = map_pos
        # 해당 타일에 건물을 지을 수 있다면 옵션에 추가
        if self.game.town.buildable[map_pos]:
            option_names = ['build']
        else:
            option_names = []

        # 인게임 메뉴 클래스를 이용해 메뉴바 생성
        self.sprite_group = InGameMenu(option_names, game.screen_width, game.screen_height)

    # 없어질 때 선택 해재
    def __del__(self):
        self.game.tile_sprite_dict[self.map_pos].is_selected = False

    def update(self):
        self.game.tile_sprite_dict[self.map_pos].is_selected = True

    # 화면 클릭시: 아무데나 다른데 클릭 -> 기본화면으로 돌아감, 건설 버튼 클릭 -> 건설 화면
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            item_selected = self.sprite_group.get_item_selected()

            if item_selected is None:
                return MapView(self.game)
            elif item_selected == 'build':
                return Build(self.game, self.map_pos)

        return self


# 빌딩 관련된 옵션들 화면 클래스
class BuildingOptions(InGameMode):
    def __init__(self, game, building):
        super().__init__(game)
        self.building = building
        building_max_level = building.data['max_level']
        label = f'{building.name}({building.level}/{building_max_level}Lv)'
        # 빌딩 이름 화면
        self.building_name_sprite = TextSprite(label, 30, 'black', center=(self.game.screen_width//2, self.game.screen_height * 0.8 - 100))
        self.building_name_sprite.add(self.sprite_group)

        # 건물들마다 특수한 옵션 추가
        option_names = []
        if self.building.is_available:
            if isinstance(self.building, Building.Laboratory):
                if not self.game.town.is_research_done:
                    option_names.append('research')
            if isinstance(self.building, Building.Factory) and self.game.town.is_research_done:
                option_names.append('manufacture')
            if not self.building.is_max_level:
                option_names.append('check_upgrade') #
        if self.building.is_earthquake:
            option_names.append('fix')
        option_names.append('info')

        self.building_options = InGameMenu(option_names, game.screen_width, game.screen_height)
        self.sprite_group.add(self.building_options)

        print([self.sprite_group])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            selected_option = self.building_options.get_item_selected()
            if selected_option is None:
                return MapView(self.game)
            if selected_option == 'info':
                return ShowInfo(self.game, self.building)
            if selected_option == 'fix':
                return FixBuilding(self.game, self.building)
            if selected_option == 'check_upgrade':
                return UpgradeConfirmation(self.game, self.building)
            if selected_option == 'research':
                return ResearchConfirmation(self.game, self.building)
            if selected_option == 'manufacture':
                return ManufactureConfirmation(self.game, self.building)
        return self


class PopupMessage(pygame.sprite.Sprite):
    def __init__(self, game, name, scale=1):
        super().__init__()
        self.game = game
        base_image = pygame.image.load(f'./image/popups/{name}.png')
        self.image = pygame.transform.smoothscale_by(base_image, scale)
        self.rect = self.image.get_rect(center=(game.screen_width // 2, game.screen_height // 2))

    def is_mouse_over(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(*mouse_pos)


class InGameMenuItem(pygame.sprite.Sprite):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        self.image = pygame.image.load(f'./image/buttons/{name}.png')
        self.rect = self.image.get_rect(**kwargs)

    def is_mouse_over(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(*mouse_pos)


class CardViewItem(pygame.sprite.Sprite):
    def __init__(self, name, **kwargs):
        super().__init__()
        self.name = name
        base_image = pygame.image.load(f'./image/cards/{name}.png')
        self.image = pygame.transform.smoothscale_by(base_image, 0.4)
        self.rect = self.image.get_rect(**kwargs)

    def is_mouse_over(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(*mouse_pos)


class CardView(pygame.sprite.Group):
    def __init__(self, names, screen_width, screen_height):
        super().__init__()
        num_items = len(names)
        total_width = (num_items - 1) * 310
        most_left = screen_width // 2 - total_width // 2
        for i in range(num_items):
            x_pos = most_left + 310 * i
            card_view_item = CardViewItem(names[i], center=(x_pos, screen_height * 0.5-50))
            card_view_item.add(self)

    def selected_item(self):
        for card_view_item in self:
            if card_view_item.is_mouse_over():
                return card_view_item.name

        return None


class CostingConfirmButton(pygame.sprite.Sprite):
    def __init__(self, cost, time, **kwargs):
        super().__init__()
        self.name = 'confirm'

        self.image = pygame.image.load('./image/buttons/cost_confirm_base.png')
        self.cost_text = TextSprite(f'돈: {ceil(cost)}', 20, '#733600')
        minutes, seconds = divmod(ceil(time), 60)
        if minutes > 0:
            if seconds == 0:
                self.time_text = TextSprite(f'시간: {minutes}분', 20, '#733600')
            else:
                self.time_text = TextSprite(f'시간: {minutes}분 {seconds}초', 20, '#733600')
        else:
            self.time_text = TextSprite(f'시간: {seconds}초', 20, '#733600')

        self.cost_text.rect.center = (66, 25)
        self.time_text.rect.center = (66, 70)

        self.image.blit(self.cost_text.image, self.cost_text.rect)
        self.image.blit(self.time_text.image, self.time_text.rect)

        self.rect = self.image.get_rect(**kwargs)

    def is_mouse_over(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(*mouse_pos)


class InGameMenu(pygame.sprite.Group):
    def __init__(self, names, screen_width, screen_height, level=0, **kwargs):
        super().__init__()
        confirm_button_exists = ('time' in kwargs.keys())
        num_items = len(names)

        if confirm_button_exists:
            total_width = num_items * 150
        else:
            total_width = (num_items - 1) * 150
        most_left = screen_width // 2 - total_width // 2

        for i in range(num_items):
            x_pos = most_left + 150 * i
            menu_item = InGameMenuItem(names[i], center=(x_pos, screen_height * 0.8 - 145 * level))
            menu_item.add(self)

        if confirm_button_exists:
            x_pos = most_left + 150 * num_items
            menu_item = CostingConfirmButton(kwargs['cost'], kwargs['time'], center=(x_pos, screen_height * 0.8 - 145 * level))
            menu_item.add(self)

    def get_item_selected(self):
        for menu_item in self:
            if menu_item.is_mouse_over():
                return menu_item.name

        return None


class Build(InGameMode):
    def __init__(self, game, map_pos):
        super().__init__(game)
        self.map_pos = map_pos

        sprite_group_0 = InGameMenu(['build_house', 'build_hospital', 'build_library', 'build_school'],
                                    game.screen_width, game.screen_height, level=0)
        sprite_group_1 = InGameMenu(['build_shop', 'build_stadium', 'build_park', 'build_laboratory'],
                                    game.screen_width, game.screen_height, level=1)
        sprite_group_2 = InGameMenu(['build_weather_center', 'build_art_center', 'build_factory'],
                                    game.screen_width, game.screen_height, level=2)
        self.sprite_group.add(sprite_group_0, sprite_group_1, sprite_group_2)

    def __del__(self):
        self.game.tile_sprite_dict[self.map_pos].is_selected = False

    def update(self):
        self.game.tile_sprite_dict[self.map_pos].is_selected = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            item_selected = self.get_item_selected()
            if item_selected is None:
                return MapView(self.game)

            return BuildConfirmation(self.game, self.map_pos, item_selected)

        return self

    def get_item_selected(self):
        for sprite in self.sprite_group:
            if sprite.is_mouse_over():
                return sprite.name[6:]

        return None


class Missions(InGameMode):
    def __init__(self, game):
        super().__init__(game)
        name_group_0 = []
        name_group_1 = []
        for i in [1, 2, 3]:
            mission = game.mission_list[i-1]
            if mission.is_done:
                name_group_0.append(f'mission{i}_done')
            else:
                name_group_0.append(f'mission{i}_not_done')
        for i in [5, 6, 7]:
            mission = game.mission_list[i - 1]
            if mission.is_done:
                name_group_1.append(f'mission{i}_done')
            else:
                name_group_1.append(f'mission{i}_not_done')

        self.sprite_group_0 = InGameMenu(name_group_0, game.screen_width, game.screen_height, level=0)
        self.sprite_group_1 = InGameMenu(name_group_1, game.screen_width, game.screen_height, level=1)

        self.sprite_group.add(self.sprite_group_0, self.sprite_group_1)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            item_selected = self.get_item_selected()
            if item_selected is None:
                return MapView(self.game)

            return MessageScreen(self.game, item_selected)

        return self

    def get_item_selected(self):
        item_selected = self.sprite_group_0.get_item_selected()
        if item_selected is not None:
            return item_selected

        item_selected = self.sprite_group_1.get_item_selected()
        if item_selected is not None:
            return item_selected

        return None


class PopupScreen(InGameMode):
    def __init__(self, game, name, scale=1):
        super().__init__(game)
        self.popup_sprite = PopupMessage(game, name, scale)
        self.popup_sprite.add(self.sprite_group)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            return MapView(self.game)

        return self


class MessageScreen(PopupScreen):
    def __init__(self, game, name):
        super().__init__(game, name, scale=0.35)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return Missions(self.game)
        return self


class CostingConfirmation(InGameMode):
    def __init__(self, game, names, cost, time):
        super().__init__(game)
        self.card_view = CardView(names, self.game.screen_width, self.game.screen_height)
        self.options = InGameMenu([], self.game.screen_width, self.game.screen_height, cost=cost, time=time)

        self.sprite_group.add(self.card_view)
        self.sprite_group.add(self.options)

    def handle_event(self, event):
        return self


class BuildConfirmation(CostingConfirmation):
    def __init__(self, game, map_pos, type_id):
        self.game = game
        self.map_pos = map_pos
        self.type_id = type_id
        card_name = f'{type_id}1_card'

        self.cost = data[type_id]['upgrade_price'][0]
        time = data[type_id]['upgrade_time'][0] / self.game.town.build_speed
        super().__init__(game, [card_name], self.cost, time)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            option_selected = self.options.get_item_selected()
            if option_selected is None:
                return MapView(self.game)
            if self.type_id == 'stadium' and self.game.town.population < 500:
                return PopupScreen(self.game, 'less_people')
            else:
                if self.game.town.money < self.cost:
                    return PopupScreen(self.game, 'less_money')

                new_building = self.game.town.build(self.map_pos, self.type_id)
                self.game.add_building_sprite(new_building)
                return MapView(self.game)

        return self


class UpgradeConfirmation(CostingConfirmation):
    def __init__(self, game, building):
        self.game = game
        self.building = building
        self.type_id = building.type_id
        level = building.level

        self.cost = building.data['upgrade_price'][level]
        time = building.data['upgrade_time'][level] / self.game.town.build_speed

        card_name1 = f'{self.type_id}{level}_card'
        card_name2 = f'{self.type_id}{level+1}_card'

        super().__init__(game, [card_name1, card_name2], self.cost, time)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            option_selected = self.options.get_item_selected()
            if option_selected is None:
                return MapView(self.game)
            else:
                if self.game.town.money < self.cost:
                    return PopupScreen(self.game, 'less_money')

                self.game.town.upgrade_building(self.building)
                return MapView(self.game)

        return self


class ResearchConfirmation(CostingConfirmation):
    def __init__(self, game, building):
        self.game = game
        self.building = building

        self.cost = building.data['research_price']
        time = building.data['research_time']

        super().__init__(game, ['research_card'], self.cost, time)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            item_selected = self.options.get_item_selected()
            if item_selected == 'confirm':
                if self.game.town.money < self.cost:
                    return PopupScreen(self.game, 'less_money')

                self.building.start_research()
                return PopupScreen(self.game, 'research_start')
            else:
                return MapView(self.game)

        return self


class ManufactureConfirmation(CostingConfirmation):
    def __init__(self, game, building):
        self.game = game
        self.building = building

        self.cost = building.data['manufacture_price']
        time = building.data['manufacture_time']

        super().__init__(game, ['manufacture_card'], self.cost, time)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            item_selected = self.options.get_item_selected()
            if item_selected == 'confirm':
                if self.game.town.money < self.cost:
                    return PopupScreen(self.game, 'less_money')

                if self.building.is_production_in_progress:
                    return PopupScreen(self.game, 'already_manufacturing')

                self.building.start_production()
                return PopupScreen(self.game, 'manufacture_start')
            else:
                return MapView(self.game)

        return self


class ShowInfo(InGameMode):
    def __init__(self, game, building):
        super().__init__(game)
        self.building = building
        card_name = f'{building.type_id}{building.level}_card'
        card_view = CardView([card_name], self.game.screen_width, self.game.screen_height)
        self.sprite_group.add(card_view)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            return MapView(self.game)

        return self


class FixBuilding(CostingConfirmation):
    def __init__(self, game, building):
        self.game = game
        self.building = building
        self.cost = self.game.town.repair_price_ratio * building.total_price / 5
        super().__init__(game, [], self.cost, 0)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            selected_item = self.options.get_item_selected()
            if selected_item == 'confirm':
                if self.cost > self.game.town.money:
                    return PopupScreen(self.game, 'less_money')

                else:
                    self.game.town.repair_building(self.building)
                    return MapView(self.game)

        return self


class TextSprite(pygame.sprite.Sprite):
    def __init__(self, text, size, color, **kwargs):
        super().__init__()
        font = pygame.font.Font('./fonts/CookieRun Regular.otf', size)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(**kwargs)
