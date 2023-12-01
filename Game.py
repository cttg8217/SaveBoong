import pygame
import Town
import Building
import MapSprites
import InGameMode
import Mission
import pickle
clock = pygame.time.Clock()

#  화면 중심, 화면 배율 위치 리스트. 화살표를 통해 화면 중심, 배율이 이 값들 사이에서 이동한다.
screen_center_dx_levels = [-200, -100, 0, 100, 200]
screen_center_dy_levels = [-200, -100, 0, 100, 200]
scale_levels = [0.6, 0.8, 1.0, 1.2, 1.4]

# 화면 크기
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

# 로고, 새 게임 버튼
logo_image = pygame.image.load('image/logo.png')
new_game_button_image = pygame.image.load('image/new_game_button.png')

bring_button_image = pygame.image.load('image/bring_button.png')


# 게임 관리와 화면 출력 관련된 것을 담당하는 클래스이다.
class Game:
    def __init__(self):
        # 여기서 None으로 설정된 변수들은 이후에 setup 함수들에서 설정되고 거기에서 설명한다.
        self.cat_rect = None
        self.cat_img = None
        self.mission_list = None
        self.mission_success_cnt = None
        self.mission_button_rect = None
        self.mission_button_image = None
        self.save_button_image = None
        self.save_button_rect = None
        self.tile_sprite_group = None
        self.building_sprite_group = None
        self.data_sprite_list = None
        self.tile_sprite_dict = None
        self.building_sprite_dict = None
        self.town = None
        self.in_game_mode_controller = None
        self.screen_center_dx_level = None
        self.screen_center_dy_level = None
        self.scale_level = None
        self.running = None
        self.screen = None

        # pygame 초기화
        pygame.init()
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.previous_second = 0
        self.font = pygame.font.Font('./fonts/CookieRun Regular.otf', 30)

    # 게임 프로그램을 실행시키는 메서드
    def play(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('구제의 붕어빵')
        self.running = True
        self.main_menu()
        self.main_game()
        pygame.quit()

    # 메인 게임 (마을 운영)을 실행시키는 메서드
    def main_game(self):
        # 음악 재생
        mixer = pygame.mixer.Sound('./music.mp3')
        mixer.play(-1)

        # 화면 중심, 배율 레벨 설정
        self.screen_center_dx_level = 2
        self.screen_center_dy_level = 2
        self.scale_level = 2
        # 게임과 마을과의 상호작용을 담당한다.
        self.in_game_mode_controller = InGameMode.InGameModeController(self)

        # 각종 스프라이트, 이미지 설정하고 위치 조정 등
        self.setup_map_sprites()
        self.setup_data()
        self.setup_menu_buttons()
        self.setup_missions()
        self.setup_cat()

        # 메인 루프, 게임 시작
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.handle_map_movement(event)  # 게임 화면 이동 처리
                self.in_game_mode_controller.handle_event(event)  # 게임 내 상호작용 처리

            # 마을 업데이트, 각종 스프라이트 업데이트와 렌더링
            self.town_update()
            self.update_missions()

            self.screen.fill('white')

            self.render_map_sprites()
            self.render_data()
            self.render_menu()

            self.render_cat()

            self.in_game_mode_controller.update()

            in_game_mode_group = self.in_game_mode_controller.sprite_group()
            in_game_mode_group.draw(self.screen)

            pygame.display.flip()
            clock.tick(15)

        pygame.quit()

    # 본격적 게임 시작 전 메인 메뉴
    def main_menu(self):
        logo_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        new_game_button_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        bring_button_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 - 100)

        logo_rect = logo_image.get_rect()  # 로고
        logo_rect.center = logo_pos

        new_game_button_rect = new_game_button_image.get_rect()  # 새로운 게임 버튼
        new_game_button_rect.center = new_game_button_pos

        bring_button_rect = bring_button_image.get_rect()
        bring_button_rect.center = bring_button_pos

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if new_game_button_rect.collidepoint(*mouse_pos):  # 새 게임 누르면 해당 메서드(시작 화면 종료)
                        self.town = Town.Town([Building.TownCenter((0, 0), is_upgrading=False),
                                               Building.School((2, 0), is_upgrading=False, is_earthquake=True),
                                               Building.Shop((1, 0), is_upgrading=False)],
                                              population=20, money=200)
                        return

                    if bring_button_rect.collidepoint(*mouse_pos):
                        with open('saved.obj', 'rb') as file:
                            self.town = pickle.load(file)
                        return

            self.screen.fill('#9DE19F')
            self.screen.blit(logo_image, logo_rect)
            self.screen.blit(new_game_button_image, new_game_button_rect)
            self.screen.blit(bring_button_image, bring_button_rect)

            pygame.display.flip()

            clock.tick(30)

    # 게임 화면 이동 처리
    def handle_map_movement(self, event):
        if event.type == pygame.KEYDOWN:
            # 상하좌우 이동 설정(화살표)
            if event.key == pygame.K_UP:
                if self.screen_center_dy_level < len(screen_center_dy_levels) - 1:
                    self.screen_center_dy_level += 1

            elif event.key == pygame.K_DOWN:
                if self.screen_center_dy_level > 0:
                    self.screen_center_dy_level -= 1

            elif event.key == pygame.K_LEFT:
                if self.screen_center_dx_level < len(screen_center_dx_levels) - 1:
                    self.screen_center_dx_level += 1

            elif event.key == pygame.K_RIGHT:
                if self.screen_center_dx_level > 0:
                    self.screen_center_dx_level -= 1

            # 확대, 축소 설정(+/- 키)
            elif event.key == pygame.K_EQUALS:
                if self.scale_level < len(scale_levels) - 1:
                    self.scale_level += 1

            elif event.key == pygame.K_MINUS:
                if self.scale_level > 0:
                    self.scale_level -= 1

    @property
    def screen_center_pos(self):  # 각종 이동을 고려한 현재의 맵 중앙(0,0)의 화면 상 위치를 반환.
        screen_center_x = SCREEN_WIDTH // 2 + screen_center_dx_levels[self.screen_center_dx_level]
        screen_center_y = SCREEN_HEIGHT // 2 + screen_center_dy_levels[self.screen_center_dy_level]
        return screen_center_x, screen_center_y

    @property
    def scale(self):  # 현재의 배율
        scale = scale_levels[self.scale_level]
        return scale

    def get_building_clicked(self):  # 현재 화면에서 클릭된 건물을 반환한다. 없으면 None
        # 해당 group 에 건물이 위부터 아래 순서로 저장됨. 클릭 확인의 우선순위는 아래부터 위가 돼야 하므로 reverse를 함
        for building_sprite in reversed(self.building_sprite_group.sprites()):
            if building_sprite.is_mouse_over():
                return building_sprite

        # 건물 자체가 아니라, 해당 건물의 바닥을 눌러도 인식됨.
        for building in self.town.building_list:
            map_pos = building.map_pos
            tile_sprite = self.tile_sprite_dict[map_pos]
            if tile_sprite.is_mouse_over():
                return self.building_sprite_dict[map_pos]

        return None

    # 선택된 타일(건물이 없는 곳)을 반환
    def get_tile_clicked(self):
        tile_sprite_dict = self.tile_sprite_dict
        is_building = self.town.is_building  # (x, y) 형태의 맵상 위치를 key로 하여, 해당 위치에 건물이 있는지를 value로 하는 dict.
        for map_pos in tile_sprite_dict.keys():
            tile_sprite = tile_sprite_dict[map_pos]
            if not is_building[map_pos] and tile_sprite.is_mouse_over():
                return tile_sprite

        return None

    # 마을을 업데이트한다.
    def town_update(self):
        time = pygame.time.get_ticks()
        # 지난 번 호출 시각보다 1초가 지났는지 확인하고 1초가 지났으면 update_second 호출
        if time > self.previous_second + 1000:
            self.previous_second = time
            self.town.update_second()

    # 건물 클래스를 받아 스프라이트를 생성하고 저장
    def add_building_sprite(self, building):
        building_sprite = MapSprites.BuildingSprite(building)
        self.building_sprite_dict[building.map_pos] = building_sprite
        building_sprite.add(self.building_sprite_group)

    # 맵 관련 스프라이트 setup
    def setup_map_sprites(self):
        self.building_sprite_dict = {}
        self.tile_sprite_dict = {}
        self.building_sprite_group = pygame.sprite.LayeredDirty()
        self.tile_sprite_group = pygame.sprite.Group()

        for building in self.town.building_list:
            self.add_building_sprite(building)

        for map_pos in self.town.is_building.keys():
            tile_sprite = MapSprites.TileSprite(map_pos)
            self.tile_sprite_dict[map_pos] = tile_sprite
            tile_sprite.add(self.tile_sprite_group)

    # 맵 스프라이트를 전부 렌더링
    def render_map_sprites(self):
        self.tile_sprite_group.update(screen_center=self.screen_center_pos, scale=self.scale, is_building=self.town.is_building, buildable=self.town.buildable)
        self.tile_sprite_group.draw(self.screen)

        self.building_sprite_group.update(screen_center=self.screen_center_pos, scale=self.scale)
        for building_sprite in self.building_sprite_group:
            self.building_sprite_group.change_layer(building_sprite, building_sprite.rect.y)
        self.building_sprite_group.draw(self.screen)
    
    # 화면에 표시할 데이터를 셋업
    def setup_data(self):
        names = ['money', 'happiness', 'boong', 'population', 'graduates', 'products']
        self.data_sprite_list = []
        for i in range(len(names)):
            new_data_sprite = MapSprites.DataSprite(self.town, names[i], i+1)
            self.data_sprite_list.append(new_data_sprite)
    
    # 화면 표시 데이터를 렌더링.
    def render_data(self):
        for data_sprite in self.data_sprite_list:
            if data_sprite.name == 'graduates' and not self.town.school_exists:  # 졸업생 항목은 학교 존재시에만 표시
                continue

            if data_sprite.name == 'products' and not self.town.is_research_done:  # 장난감 항목은 그것이 연구되었을 시에만 표시
                continue

            data_sprite.update()
            data_sprite.draw(self.screen)
    
    # 미션 화면으로 넘어가는 버튼, 저장 버튼 등 메뉴 셋업
    def setup_menu_buttons(self):
        self.mission_button_image = pygame.image.load('./image/buttons/mission.png')
        self.mission_button_rect = self.mission_button_image.get_rect(midleft=(260, 75))

        self.save_button_image = pygame.image.load('./image/buttons/save.png')
        self.save_button_rect = self.mission_button_image.get_rect(midleft=(260, 165))
    
    # 메뉴 렌더링
    def render_menu(self):
        self.screen.blit(self.mission_button_image, self.mission_button_rect)
        self.screen.blit(self.save_button_image, self.save_button_rect)
    
    # Mission 파일에 있는 미션 목록으로부터 미션들을 생성해서 저장
    def setup_missions(self):
        self.mission_success_cnt = 0
        self.mission_list = []
        for i in range(len(Mission.check_func_list)):
            self.mission_list.append(Mission.Mission(self.town, Mission.check_func_list[i]))
    
    # 미션 완료 여부 업데이트, 새 미션이 완료되었다면 팝업으로 띄운다.
    def update_missions(self):
        new_mission_success_cnt = 0
        for mission in self.mission_list:
            if mission.is_done:
                new_mission_success_cnt += 1

        if new_mission_success_cnt > self.mission_success_cnt:
            self.town.popup_list.append('mission_done')

        self.mission_success_cnt = new_mission_success_cnt
    
    # 고양이 이미지 셋업
    def setup_cat(self):
        base_image = pygame.image.load('./image/cat.png')
        self.cat_img = pygame.transform.smoothscale_by(base_image, .3)
        self.cat_rect = self.cat_img.get_rect(bottomleft=(self.screen_width-100, self.screen_height))
    
    # 고양이 이미지 렌더
    def render_cat(self):
        if self.town.cat_show:
            self.screen.blit(self.cat_img, self.cat_rect)
