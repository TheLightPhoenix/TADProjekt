from shapely.geometry.polygon import Polygon
import pygame
from constants import *
import path_algorithm


class Object:

    DEBUG = False

    def __init__(self, obj_id, x_pos=0, y_pos=0, length=10, width=10):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.length = length
        self.width = width
        self.object_id = obj_id

    def move_down(self):
        if check_if_position_is_valid(self.x_pos, self.y_pos + 1):
            self.y_pos = self.y_pos + 1
        elif Object.DEBUG:
            print('Size of the map is to small. Object cannot be moved')

    def move_up(self):
        if check_if_position_is_valid(self.x_pos, self.y_pos - 1):
            self.y_pos = self.y_pos - 1
        elif Object.DEBUG:
            print('Size of the map is to small. Object cannot be moved')

    def move_right(self):
        if check_if_position_is_valid(self.x_pos + 1, self.y_pos):
            self.x_pos = self.x_pos + 1
        elif Object.DEBUG:
            print('Size of the map is to small. Object cannot be moved')

    def move_left(self):
        if check_if_position_is_valid(self.x_pos - 1, self.y_pos):
            self.x_pos = self.x_pos - 1
        elif Object.DEBUG:
            print('Size of the map is to small. Object cannot be moved')

    def draw(self, screen):
            pass


class Shelf(Object):
    def __init__(self, obj_id, x_pos=13, y_pos=200, status=StatusesRack.CAN_BE_MOVED, length=25, width=25):
        Object.__init__(self, obj_id, x_pos, y_pos, length, width)
        self.status = status

        self.products = []

        self.shelf = Polygon([(self.x_pos - self.length / 2, self.y_pos - self.width / 2),
                              (self.x_pos - self.length / 2, self.y_pos + self.width / 2),
                              (self.x_pos + self.length / 2, self.y_pos + self.width / 2),
                              (self.x_pos + self.length / 2, self.y_pos - self.width / 2)])

    def get_position(self):
        return [self.x_pos, self.y_pos]

    def draw(self, screen):
        pygame.draw.polygon(screen, constants.get('shelf_color'),
                            [(xx, yy) for xx, yy in zip([self.x_pos, self.x_pos, self.x_pos+25, self.x_pos+25],
                                                        [self.y_pos, self.y_pos+25, self.y_pos+25, self.y_pos])])


class UnloadPoint:
    def __init__(self, x_pos, y_pos, length=40, width=40):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.length = length
        self.width = width

        self.item = Polygon([(self.x_pos - self.length / 2, self.y_pos - self.width / 2),
                              (self.x_pos - self.length / 2, self.y_pos + self.width / 2),
                              (self.x_pos + self.length / 2, self.y_pos + self.width / 2),
                              (self.x_pos + self.length / 2, self.y_pos - self.width / 2)])

    def draw(self, screen):
        x, y = self.item.exterior.xy
        pygame.draw.polygon(screen, constants.get('unload_point_color'), [(xx, yy) for xx, yy in zip(x, y)])

    def get_position(self):
        return [self.x_pos, self.y_pos]


class ChargingPoint(Object):
    def __init__(self, obj_id, x_pos=0, y_pos=0, length=40, width=40):
        Object.__init__(self, obj_id, x_pos, y_pos, length, width)
        self.status = StatusesChargingPoint.FREE
        self.item = Polygon([(self.x_pos - self.length / 2, self.y_pos - self.width / 2),
                            (self.x_pos - self.length / 2, self.y_pos + self.width / 2),
                            (self.x_pos + self.length / 2, self.y_pos + self.width / 2),
                            (self.x_pos + self.length / 2, self.y_pos - self.width / 2)])

    def draw(self, screen):
        x, y = self.item.exterior.xy
        pygame.draw.polygon(screen, constants.get('charging_point_color'), [(xx, yy) for xx, yy in zip(x, y)])

# We need to overwrite functions responsible for movement
    def move_forward(self):
        print('Charging point cannot be moved')
        pass

    def move_back(self):
        print('Charging point cannot be moved')
        pass

    def move_left(self):
        print('Charging point cannot be moved')
        pass

    def move_right(self):
        print('Charging point cannot be moved')
        pass

    def charge(self, robot):
        robot.set_status(StatusesRobot.CHARGING)
        robot.power_left = constants.get('max_level')  # max level


class Order:
    def __init__(self, obj_id, size, robot, shelves_with_products, unload_point):
        self.obj_id = obj_id
        self.nb_of_items = size
        self.robot_used_curr = robot
        self.shelves_prod = shelves_with_products
        self.unload_point = unload_point

    def remove_order(self):
        self.robot_used_curr.set_status(StatusesRobot.FREE)
        del self

    def update(self, shelves, robots):
        # If robot came to destination and was going to unload point take items for order and put shelf back for now with bo putting back
        if (self.robot_used_curr.status == StatusesRobot.IN_DESTINATION and
                self.robot_used_curr.earlier_status == StatusesRobot.GOING_TO_UNLOAD_POINT):
            self.shelves_prod.pop(0)
            # All shelves taken delete order if not take the next one
            if not self.shelves_prod:
                self.remove_order()
            else:
                act_pos = self.robot_used_curr.get_position()
                shelf_pos = self.shelves_prod[0].get_position()
                path = path_algorithm.find_path(act_pos, shelf_pos, robots, shelves)
                self.robot_used_curr.go_to_take_shelf(path, shelf_pos)

        # If robot is in destination and was going to collect shelf, navigate robot to unload point
        elif (self.robot_used_curr.status == StatusesRobot.IN_DESTINATION and
                self.robot_used_curr.earlier_status == StatusesRobot.GOING_TO_COLLECT_SHELF):
            self.robot_used_curr.shelf_held = self.shelves_prod[0]
            act_pos = self.robot_used_curr.get_position()
            path = path_algorithm.find_path(act_pos, self.unload_point.get_position(), robots, shelves)
            self.robot_used_curr.go_unload(self.unload_point.get_position(), path)

        # If robot is in starting point make it to bring the first shelf
        elif (self.robot_used_curr.status == StatusesRobot.IN_DESTINATION and
              self.robot_used_curr.earlier_status == StatusesRobot.BUSY) or\
             (self.robot_used_curr.status == StatusesRobot.BUSY and
              self.robot_used_curr.earlier_status == StatusesRobot.FREE):
            act_pos = self.robot_used_curr.get_position()
            shelf_pos = self.shelves_prod[0].get_position()
            path = path_algorithm.find_path(act_pos, shelf_pos, robots, shelves)
            self.robot_used_curr.go_to_take_shelf(path, shelf_pos)

        elif not self.shelves_prod:
            self.remove_order()
        else:
            print ('No action')


