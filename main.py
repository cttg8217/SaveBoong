import pygame
from Town import Town
import Game
import Building


g = Game.Game()
t = Town('안녕', [Building.Stadium((0, 0), 1),
                Building.School((1, 0), 2),
                Building.Hospital((1, 1), 1, is_upgrading=True, left_time=5),
                Building.Hospital((0, 1), 4)])
g.town = t
g.play()
