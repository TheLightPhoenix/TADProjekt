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

    def set_status(self, new_status):
        if new_status == self.status:
            pass
        else:
            self.earlier_status = self.status
            self.status = new_status

    def update_status(self):
        if self.get_position() == self.destination:
            self.set_status(StatusesRobot.IN_DESTINATION)
        elif self.status == StatusesRobot.IN_DESTINATION and self.earlier_status == StatusesRobot.FREE:
            self.set_status(StatusesRobot.FREE)

    def update(self, charging_points):
        if self.status == StatusesRobot.PUTTING_SHELF_BACK and self.shelf_held is None:
            self.status = StatusesRobot.DONE
        if self.destination == (0,0):
            self.destination = constants.get('robot_base')
            self.status = StatusesRobot.FREE
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

        self.update_status()
        self.update_power(charging_points)

    def get_position(self):
        return [self.x_pos, self.y_pos]

    def get_shelf(self, shelf):
        if shelf.status != StatusesRack.CANNOT_BE_MOVED:
            self.shelf_held = shelf
            self.shelf_held.status = StatusesRack.CANNOT_BE_MOVED
        else:
            print('Shelf cannot be moved')

    def update_power(self, charging_points):
        self.power_left = self.power_left # here we need to sub sth
        if self.power_left < constants.get('battery_low'):
            print('Battery of robot %d low', self.object_id)
            if self.status == StatusesRobot.FREE:
                self.go_charging(charging_points)

    def go_charging(self, charging_point):
        # for point in charging_points:
        if charging_point.status == StatusesChargingPoint.FREE:
            self.set_destination(charging_point.x_pos, charging_point.y_pos)
            self.set_status(StatusesRobot.GOING_TO_CHARGING_POINT)
        else:
            pass

    def go_unload(self, unloading_point_pos, new_path):
        self.shelf_held.update_previous_location(self.destination)
        print('UNLOAD')
        print(unloading_point_pos)
        self.set_destination(unloading_point_pos[0], unloading_point_pos[1])
        self.path = new_path
        self.set_status(StatusesRobot.GOING_TO_UNLOAD_POINT)

    def go_to_take_shelf(self, new_path, shelf_pos):
        print('SHELF')
        print(shelf_pos)
        self.set_destination(shelf_pos[0], shelf_pos[1])
        self.path = new_path
        self.set_status(StatusesRobot.GOING_TO_COLLECT_SHELF)

    def put_shelf_back(self, new_path, shelf):
        # Set status, find place for shelf, put it back

        self.set_status(StatusesRobot.PUTTING_SHELF_BACK)
        self.set_destination(shelf.prev_location[0], shelf.prev_location[1])
        self.path = new_path

    def go_home(self, path):
        self.set_status(StatusesRobot.DONE)
        self.set_destination(700, 500)
        self.path = path
