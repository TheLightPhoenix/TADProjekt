from shapely.geometry.polygon import Polygon
import pygame
from constants import *
import path_algorithm


class Object:

    DEBUG = False

    def __init__(self, obj_id, x_pos, y_pos, length=10, width=10):
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
        self.prev_location = [x_pos, y_pos]
        self.base_pos = [x_pos, y_pos]
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

    def update_previous_location(self, loc):
        self.prev_location = loc

    def update(self):
        if self.base_pos == self.get_position():
            self.status = StatusesRack.CAN_BE_MOVED


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
            act_pos = self.robot_used_curr.get_position()
            path = path_algorithm.find_path(act_pos, self.robot_used_curr.shelf_held.prev_location, robots, shelves)
            self.robot_used_curr.put_shelf_back(path, self.robot_used_curr.shelf_held)

        elif (self.robot_used_curr.status == StatusesRobot.IN_DESTINATION and
              self.robot_used_curr.earlier_status == StatusesRobot.PUTTING_SHELF_BACK):
                if self.robot_used_curr.shelf_held is not None:
                    self.robot_used_curr.shelf_held.status = StatusesRack.CAN_BE_MOVED
                self.robot_used_curr.shelf_held = None
                if not self.shelves_prod:

                    self.robot_used_curr.set_destination(constants.get('robot_base')[0], constants.get('robot_base')[1])
                    self.remove_order()

                else:

                    act_pos = self.robot_used_curr.get_position()
                    if self.shelves_prod[0].status != StatusesRack.CANNOT_BE_MOVED:
                        shelf_pos = self.shelves_prod[0].get_position()
                        path = path_algorithm.find_path(act_pos, shelf_pos, robots, shelves)
                        self.robot_used_curr.go_to_take_shelf(path, shelf_pos)
                    elif len(self.shelves_prod) > 1:
                        for i in range(len(self.shelves_prod)):
                            if self.shelves_prod[i] and self.shelves_prod[i].status == StatusesRack.CAN_BE_MOVED:
                                tmp = self.shelves_prod[0]
                                self.shelves_prod[0] = self.shelves_prod[i]
                                self.shelves_prod[i] = tmp
                                shelf_pos = self.shelves_prod[0].get_position()
                                path = path_algorithm.find_path(act_pos, shelf_pos, robots, shelves)
                                self.robot_used_curr.go_to_take_shelf(path, shelf_pos)

        # If robot is in destination and was going to collect shelf, navigate robot to unload point
        elif (self.robot_used_curr.status == StatusesRobot.IN_DESTINATION and
                self.robot_used_curr.earlier_status == StatusesRobot.GOING_TO_COLLECT_SHELF):

            self.robot_used_curr.get_shelf(self.shelves_prod[0])
            if self.robot_used_curr.shelf_held is not None:
                act_pos = self.robot_used_curr.get_position()
                path = path_algorithm.find_path(act_pos, self.unload_point.get_position(), robots, shelves)
                self.robot_used_curr.go_unload(self.unload_point.get_position(), path)

        # If robot is in starting point make it to bring the first shelf
        elif (self.robot_used_curr.status == StatusesRobot.IN_DESTINATION and
              self.robot_used_curr.earlier_status == StatusesRobot.BUSY) or\
             (self.robot_used_curr.status == StatusesRobot.BUSY and
              self.robot_used_curr.earlier_status == StatusesRobot.FREE):

            act_pos = self.robot_used_curr.get_position()
            if self.shelves_prod:
                if self.shelves_prod[0].status != StatusesRack.CANNOT_BE_MOVED:
                    shelf_pos = self.shelves_prod[0].get_position()
                    print (shelf_pos)
                    path = path_algorithm.find_path(act_pos, shelf_pos, robots, shelves)
                    self.robot_used_curr.go_to_take_shelf(path, shelf_pos)
                elif len(self.shelves_prod) > 1:
                    for i in range(len(self.shelves_prod)):
                        if self.shelves_prod[i] and self.shelves_prod[i].status == StatusesRack.CAN_BE_MOVED:
                            tmp = self.shelves_prod[0]
                            self.shelves_prod[0] = self.shelves_prod[i]
                            self.shelves_prod[i] = tmp
                            shelf_pos = self.shelves_prod[0].get_position()
                            path = path_algorithm.find_path(act_pos, shelf_pos, robots, shelves)
                            self.robot_used_curr.go_to_take_shelf(path, shelf_pos)

            else:

                self.remove_order()
                self.robot_used_curr.set_destination(constants.get('robot_base')[0], constants.get('robot_base')[1])



def charging_management(uncharged_robots, charging_points, minut):

    curr_to_load = len(charging_points)* int(minut/6)
    for i, ch_point in enumerate(charging_points):
        if curr_to_load + i < len(uncharged_robots):
            curr_rob = uncharged_robots[curr_to_load + i]
            if curr_rob.shelf_held is  None:
                curr_rob.set_status(StatusesRobot.CHARGING)
                curr_rob.set_destination(ch_point.x_pos, ch_point.y_pos)
                ch_point.status = StatusesChargingPoint.BUSY
        elif curr_to_load + i >= len(charging_points):
            uncharged_robots[curr_to_load - len(charging_points) + i].set_status(StatusesRobot.FREE)
            ch_point.status = StatusesChargingPoint.FREE



    # if minut % 6 == 0:
    #     i = 0
    #     for j, unchar_r in enumerate(uncharged_robots):
    #         if i < len(charging_points):
    #             if unchar_r.status == StatusesRobot.FREE:
    #                 unchar_r.go_charging(charging_points[i])
    #                 i = i+1
    #                 uncharged_robots_tmp = uncharged_robots[:j]
    #                 if j+1 < len(uncharged_robots):
    #                     uncharged_robots_tmp.extend(uncharged_robots[j+1:])
    #                 else:
    #                     pass
    #                 uncharged_robots = uncharged_robots_tmp
    #             else:
    #                 pass
    #         else:
    #             pass
    #
    # else:
    #     for r in uncharged_robots