from shapely.geometry.point import Point
from shapely.affinity import rotate
import pygame
from environment import *


class Robot(Object):
    def __init__(self, obj_id, x_pos, y_pos, radius=15, status=StatusesRobot.FREE, power=constants.get('max_power'), shelf=Shelf(1)):
        Object.__init__(self, obj_id, x_pos, y_pos)
        self.radius = radius
        self.robShape = Point(x_pos, y_pos).buffer(1)
        self.status = status
        self.power_left = power
        self.shelf_held = shelf
        self.destination = [x_pos, y_pos]
        self.path = []
        self.in_move = False

    def draw(self, screen):
        pygame.draw.circle(screen, constants.get('robot_color'), [int(self.x_pos), int(self.y_pos)], self.radius)

    def move_right(self):
        Object.move_right(self)
        self.shelf_held.move_right()

    def move_left(self):
        Object.move_left(self)
        self.shelf_held.move_left()

    def move_up(self):
        Object.move_up(self)
        self.shelf_held.move_up()

    def move_down(self):
        Object.move_down(self)
        self.shelf_held.move_down()

    def set_destination(self, x, y):
        self.destination = [x,y]

    def update(self):
        if self.y_pos < self.destination[1]:
            self.move_down()
            self.in_move = True
        elif self.y_pos > self.destination[1]:
            self.move_up()
            self.in_move = True
        elif self.x_pos < self.destination[0]:
            self.move_right()
            self.in_move = True
        elif self.x_pos > self.destination[0]:
            self.move_left()
            self.in_move = True
        else:
            if not self.path:
                self.in_move = False
            else:
                self.destination = self.path[0]
                self.path.pop(0)

    def get_position(self):
        return [self.x_pos, self.y_pos]

    def get_shelf(self, shelf):
        self.shelf_held = shelf


