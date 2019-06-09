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
            ret = self.find_free_robot(self.orders[0])
            if ret == StatusesOrder.FREE_ROBOT_FOUND:
                self.orders[0].robot_used_curr.earlier_status = self.orders[0].robot_used_curr.status
                self.orders[0].robot_used_curr.status = StatusesRobot.BUSY
                self.orders_maintained.append(self.orders[0])
                self.orders.pop(0)
        for i in self.robots:
            i.path = path_algorithm.find_path([i.x_pos, i.y_pos], i.destination, self.robots, self.shelves)
            i.update(self.charging_points)
        for i in self.orders_maintained:
            i.update(self.shelves, self.robots)

    def find_free_robot(self, order):
        for i in self.robots:
            if i.status == StatusesRobot.FREE:
                order.robot_used_curr = i
                return StatusesOrder.FREE_ROBOT_FOUND
        return StatusesOrder.NO_FREE_ROBOTS


pos = constants.get('robot_base')

if __name__ == '__main__':
    rob = [Robot(1, pos[0], pos[1]), Robot(2, pos[0], pos[1]+50), Robot(3, pos[0], pos[1]+100)]
    env = []
    for i in range(1,5):
        for j in range(1,8):
            env.append(Shelf((i*8+j), 50*i, 50*j))

    charging_points = [ChargingPoint(1, 700, 30), ChargingPoint(2, 700, 120), ChargingPoint(4, 700, 220), ChargingPoint(5, 700, 320)]
    unload_points = [UnloadPoint(40, 550), UnloadPoint(140, 550), UnloadPoint(240, 550), UnloadPoint(340, 550), UnloadPoint(440, 550)]
    orders = create_orders(100, rob, env, unload_points)
    pygame.init()
    pygame.display.set_caption("Symulacja")
    window_width = 800
    window_height = 600
    screen = pygame.display.set_mode((window_width, window_height))

    v = 0.5
    exit = False

    iterations_counter = 0
    simulation = Simulation(rob, env, charging_points, unload_points, orders)
    while not exit:
        iterations_counter = iterations_counter + 1
        if iterations_counter == 1000000000:
            iterations_counter = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True
        screen.fill(constants.get('screen_color'))
        for x in rob:
            x.draw(screen)
        for x in env:
            x.draw(screen)
        for x in charging_points:
            x.draw(screen)
        for x in unload_points:
            x.draw(screen)
        simulation.update()
        if not simulation.orders and not simulation.orders_maintained:
            pygame.display.quit()

        pygame.display.flip()
    pygame.quit()
