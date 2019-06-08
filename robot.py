from shapely.geometry.point import Point
from shapely.affinity import rotate
import pygame
from environment import *
import path_algorithm


class Robot(Object):
    def __init__(self, obj_id, x_pos, y_pos, radius=15, status=StatusesRobot.FREE, power=constants.get('max_power'), shelf=None):
        Object.__init__(self, obj_id, x_pos, y_pos)
        self.radius = radius
        self.robShape = Point(x_pos, y_pos).buffer(1)
        self.status = status
        self.earlier_status = StatusesRobot.FREE
        self.power_left = power
        self.shelf_held = shelf
        self.destination = [x_pos, y_pos]
        self.path = []
        self.in_move = False

    def draw(self, screen):
        pygame.draw.circle(screen, constants.get('robot_color'), [int(self.x_pos), int(self.y_pos)], self.radius)

    def move_right(self):
        Object.move_right(self)
        if self.shelf_held is not None:
            self.shelf_held.move_right()

    def move_left(self):
        Object.move_left(self)
        if self.shelf_held is not None:
            self.shelf_held.move_left()

    def move_up(self):
        Object.move_up(self)
        if self.shelf_held is not None:
            self.shelf_held.move_up()

    def move_down(self):
        Object.move_down(self)
        if self.shelf_held is not None:
            self.shelf_held.move_down()

    def set_destination(self, x, y):
        self.destination = [x, y]

    def update(self, charging_points):
        self.update_power(charging_points)
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
        elif self.get_position() == self.destination:
            self.status = StatusesRobot.IN_DESTINATION
        if self.status == StatusesRobot.IN_DESTINATION:
            self.destination = self.path[0]
            self.path.pop(0)
            self.status = StatusesRobot.BUSY
        '''else:
            if not self.path:
                self.in_move = False
            else:
                self.destination = self.path[0]
                self.path.pop(0)'''

    def get_position(self):
        return [self.x_pos, self.y_pos]

    def get_shelf(self, shelf):
        if shelf.status != StatusesRack.CANNOT_BE_MOVED:
            self.shelf_held = shelf
        else:
            print('Shelf cannot be moved')

    def update_power(self, charging_points):
        self.power_left = self.power_left-1
        if self.power_left < constants.get('battery_low'):
            print('Battery of robot %d low', self.object_id)
            if self.status == StatusesRobot.FREE:
                self.go_charging(charging_points)

    def go_charging(self, charging_points):
        for point in charging_points:
            if point.status == StatusesChargingPoint.FREE:
                self.set_destination(point.x_pos, point.y_pos)
                self.status = StatusesRobot.CHARGING
            else:
                pass

    def go_unload(self, unloading_point):
        self.set_destination(unloading_point.x_pos, unloading_point.y_pos)
