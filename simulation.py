from robot import *
from constants import *
from environment import *
from path_algorithm import *

# number of orders collecting == number of unload points


def create_orders(nb_of_orders, robots, shelves, unload_points):
    orders = []
    # create orders with random parameters
    for i in range(nb_of_orders):
        size = np.random.randint(1, constants.get('max_order_size'))
        shelves_list = []
        robots_list = []
        robots_nb = np.random.randint(1,constants.get('max_robots'))
        for j in range(size):
            shelves_list.append(shelves[np.random.randint(0, len(shelves))])
        for j in range(robots_nb):
            robots_list.append(robots[np.random.randint(0, len(robots))])
        tmp = Order(i+1, size, None, shelves_list, unload_points[0])
        orders.append(tmp)
    return orders


class Simulation:
    def __init__(self, robots, shelves, charging_points, unload_points, orders):
        self.robots = robots
        self.shelves = shelves
        self.charging_points = charging_points
        self.unload_points = unload_points
        self.orders = orders
        self.orders_maintained = []

    def update(self):
        if len(self.orders_maintained) < len(self.unload_points):
            ret = self.find_free_robot(orders[0])
            if ret == StatusesOrder.FREE_ROBOT_FOUND:
                self.orders_maintained.append(orders[0])
                self.orders.pop(0)
        for i in self.robots:
            i.path = path_algorithm.find_path([i.x_pos, i.y_pos], i.destination, i, self.shelves)
            i.update()
        for i in self.orders_maintained:
            i.update()

    def find_free_robot(self, order):
        for i in self.robots:
            if i.status == StatusesRobot.FREE:
                order.robot_used_curr = i
                return StatusesOrder.FREE_ROBOT_FOUND
        return StatusesOrder.NO_FREE_ROBOTS

env = []
for i in range(1, 5):
    for j in range(1, 8):
        env.append(Shelf((i*8+j), 50*i, 50*j))
orders = create_orders(40, env)
