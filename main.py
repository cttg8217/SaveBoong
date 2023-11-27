import pygame
from Town import Town
import Game
import Building


g = Game.Game()
t = Town('안녕', [Building.Hospital((0, 0), 1),
                Building.Hospital((1, 0), 2),
                Building.Hospital((1, 1), 3),
                Building.Hospital((0, 1), 4)])
g.town = t
g.play()
