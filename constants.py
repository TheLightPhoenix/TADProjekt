from enum import Enum

# Constant values definitions
constants = dict()
constants['map_width'] = 800
constants['map_length'] = 600
constants['max_power'] = 1000000000000000
constants['robot_color'] = (255, 165, 0)
constants['shelf_color'] = (255, 0, 255)
constants['charging_point_color'] = (0, 128, 0)
constants['unload_point_color'] = (255, 128, 0)
constants['screen_color'] = (255, 255, 255)
constants['robot_base'] = [700, 500]
constants['robot_radius'] = 15
constants['battery_low'] = 10
constants['max_order_size'] = 5
constants['max_robots'] = 2


# Statuses definitions
class StatusesRobot(Enum):
    FREE = 0
    BUSY = 1
    CHARGING = 2
    IN_DESTINATION = 3
    GOING_TO_CHARGING_POINT = 4
    GOING_TO_UNLOAD_POINT = 5
    GOING_TO_COLLECT_SHELF = 6
    PUTTING_SHELF_BACK = 7
    DONE = 8


class StatusesRack(Enum):
    CAN_BE_MOVED = 0
    CANNOT_BE_MOVED = 1


class StatusesChargingPoint(Enum):
    FREE = 0
    BUSY = 1


class StatusesOrder(Enum):
    NO_FREE_ROBOTS = 0
    FREE_ROBOT_FOUND = 1

def check_if_position_is_valid(x_pos, y_pos):
    if (x_pos < constants.get('map_width') and x_pos > 0
        and y_pos > 0 and y_pos < constants.get('map_length')):
        return True
    else:
        return False


def calculate_charging_time(robot):
    power_lack = constants.get('max_level') - robot.power_left
    if power_lack < 50:
        pass
    else:
        pass
