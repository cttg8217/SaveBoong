import pygame
from os import listdir

building_images = {}
building_image_dir = './image/buildings/'
for image_path in listdir(building_image_dir):
    type_id = image_path[:-4]
    image = pygame.image.load(building_image_dir + image_path)
    building_images[type_id] = image


class Sprite:
    def __init__(self, image, **kwargs):
        self.image = image
        self.rect = image.get_rect(**kwargs)

    def is_mouse_over(self):
        mask = pygame.mask.from_surface(self.image)
        mouse_pos = pygame.mouse.get_pos()
        rel_pos = mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y
        return self.rect.collidepoint(*mouse_pos) and mask.get_at(rel_pos)


class AnimatedSprite:
    def __init__(self, image_list, **kwargs):
        self.sprites = []
        for image in image_list:
            sprite = Sprite(image, **kwargs)
            self.sprites.append(sprite)

        self.index = 0

    def update(self):
        self.index += 1
        self.index %= len(self.sprites)

    def is_mouse_over_mask(self):
        return self.current_sprite().is_mouse_over()

    def is_mouse_over_rect(self):
        mouse_pos = pygame.mouse.get_pos()
        rect = self.current_sprite().rect
        return rect.collidepoint(*mouse_pos)

    def current_sprite(self):
        return self.sprites[self.index]

