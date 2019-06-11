from robot import *
from constants import *
from environment import *
from path_algorithm import *
from math import ceil

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
        unload = unload_points[np.random.randint(0, len(unload_points))]
        tmp = Order(i+1, size, None, shelves_list, unload)
        orders.append(tmp)
    return orders


def iter_to_sec(curr_iteration, robot_radius):
    # Robot.Radius = 15, real robot has radius = 0,45
    # And in 1 iteration robot moves by 1 pixel, real robot moves 1,3 m/s
    # so: 30 px=0,9 m  -> 1px = 0,03 m -> 1,3 m/s = 43,(3) px/s -> 1 second = ab. 43 iteration
    one_px = 0.9/(2*robot_radius)
    iter_per_sec = int(1.3/one_px)
    return int(curr_iteration/iter_per_sec)


class Simulation:
    def __init__(self, robots, shelves, charging_points, unload_points, orders):
        self.robots = robots
        self.shelves = shelves
        self.charging_points = charging_points
        self.unload_points = unload_points
        self.orders = orders
        self.orders_maintained = []

    def update(self):
        print(len(self.orders_maintained))
        print(len(self.orders))
        '''
        for i in self.shelves:
            if i.status == StatusesRack.CAN_BE_MOVED and i.base_pos != i.get_position():
                for j in self.robots:
                    if j.status == StatusesRobot.FREE or j.status == StatusesRobot.DONE:
                        path = path_algorithm.find_path(j.get_position(), i.base_pos, self.robots, self.shelves)
                        j.put_shelf_back(path, i)
        '''
        for i in rob:
            print(i.status)
            if i.status == StatusesRobot.FREE and i.shelf_held is not None:
                path = path_algorithm.find_path(i.get_position(), i.shelf_held.base_pos, self.robots, self.shelves)
                i.put_shelf_back(path, i.shelf_held)
        for i in self.robots:
            i.path = path_algorithm.find_path([i.x_pos, i.y_pos], i.destination, self.robots, self.shelves)
            i.update(self.charging_points)
        for i in range(len(self.orders_maintained)):
            self.orders_maintained[i].update(self.shelves, self.robots)
        for i in range(len(self.orders_maintained)):
            if i == len(self.orders_maintained):
                i = i-1
            if not self.orders_maintained[i].shelves_prod:
                self.orders_maintained.pop(i)
                i = i-1
            if i < len(self.orders_maintained) and len(self.orders_maintained)>0:
                if self.orders_maintained[i].robot_used_curr.status == StatusesRobot.FREE or \
                        self.orders_maintained[i].robot_used_curr.status == StatusesRobot.DONE:
                    print(self.orders_maintained[i].shelves_prod)
                    act_pos = self.orders_maintained[i].robot_used_curr.get_position()
                    shelf_pos = self.orders_maintained[i].shelves_prod[0].get_position()
                    path = path_algorithm.find_path(act_pos, shelf_pos, self.robots, self.shelves)
                    self.orders_maintained[i].robot_used_curr.go_to_take_shelf(path, shelf_pos)
        if self.orders:
            if len(self.orders_maintained) < len(self.unload_points):

                ret = self.find_free_robot(self.orders[0])
                if ret == StatusesOrder.FREE_ROBOT_FOUND:
                    self.orders[0].robot_used_curr.earlier_status = self.orders[0].robot_used_curr.status
                    self.orders[0].robot_used_curr.status = StatusesRobot.BUSY
                    self.orders_maintained.append(self.orders[0])
                    self.orders.pop(0)

        if not self.orders:
            for i in self.robots:
                if i.status == StatusesRobot.FREE or i.status == StatusesRobot.DONE or i.status == StatusesRobot.IN_DESTINATION:
                    if i.shelf_held is None:
                        i.set_destination(700, 500)
                        i.set_status(StatusesRobot.DONE)
                        i.path = path_algorithm.find_path(i.get_position(), i.destination, self.robots, self.shelves)
                    else:
                        path = path_algorithm.find_path(i.get_position(), i.shelf_held.base_pos, self.robots, self.shelves)
                        i.set_status(StatusesRobot.PUTTING_SHELF_BACK)
                        i.put_shelf_back(path, i.shelf_held)
                        if i.status == StatusesRobot.PUTTING_SHELF_BACK and i.get_position() == i.shelf_held.base_pos :
                            i.shelf_held = None


    def find_free_robot(self, order):
        for i in self.robots:
            if i.status == StatusesRobot.FREE:
                order.robot_used_curr = i
                return StatusesOrder.FREE_ROBOT_FOUND
        return StatusesOrder.NO_FREE_ROBOTS


pos = constants.get('robot_base')

if __name__ == '__main__':

    window_width = constants['map_width']
    window_height = constants['map_length']

    rob = []

    for i in range(0, 5):
        for j in range(0, 5):
            rob.append(Robot(i*j, pos[0]+i*32, pos[1]+j*32))


    env = []
    max_i = 3;
    max_j = 5;
    for nb_groups_rows in range (0, 3):
        for nb_groups_cols in range(0, 12):
            for i in range(1, max_i):
                for j in range(1, max_j):
                    env.append(Shelf((i*8+j), 30*i+nb_groups_cols*max_i*30, 30*j+nb_groups_rows*max_j*30))

    # Compute number of charging points needed for the robots.
    # Every robot needs to be charged 5 min per hour (5min of charging and 1 minut to switch the robot)
    nb_char_points = ceil((len(rob)*6)/60)
    charging_points= []
    for i in range(0, nb_char_points):
        charging_points.append(ChargingPoint(i, window_width - 25, (i+1)*50))

    unload_points = []
    for i in range(1, 8):
        unload_points.append(UnloadPoint(i*60, window_height - 50))
    # unload_points = [UnloadPoint(40, 550), UnloadPoint(140, 550), UnloadPoint(240, 550), UnloadPoint(340, 550), UnloadPoint(440, 550)]
    orders = create_orders(len(rob)*2, rob, env, unload_points)
    uncharged_robots = rob;
    pygame.init()
    pygame.display.set_caption("Symulacja")

    screen = pygame.display.set_mode((window_width, window_height))

    v = 0.5
    exit = False

    iterations_counter = 0
    simulation = Simulation(rob, env, charging_points, unload_points, orders)

    font = pygame.font.SysFont('Arial', 24)


    while not exit:
        iterations_counter = iterations_counter + 1
        sec_counter = iter_to_sec(iterations_counter, rob[0].radius)
        if iterations_counter == 1000000000:
            iterations_counter = 0



        # if event object type is QUIT
        # then quitting the pygame
        # and program both.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True
        simulation.update()
        screen.fill(constants.get('screen_color'))

        for x in rob:
            x.draw(screen)
        for x in env:
            x.draw(screen)
            x.update()
        for x in charging_points:
            x.draw(screen)
        for x in unload_points:
            x.draw(screen)

        charging_management(uncharged_robots, charging_points, int(sec_counter/10))


        if not simulation.orders and not simulation.orders_maintained:
            print('All orders has been maintained!')
            pygame.display.flip()
            pygame.quit()
            for i in rob:
                path = path_algorithm.find_path(i.get_position(), [700, 500], simulation.robots, simulation.shelves)
                i.go_home(path)


        # Print the current iteration:
        text = font.render('Time: {} sec'.format(sec_counter), True, constants['font_color'])
        textRect = text.get_rect()
        textRect.center = (window_width - 100, 28)
        screen.blit(text, textRect)

        pygame.display.flip()
    pygame.quit()
