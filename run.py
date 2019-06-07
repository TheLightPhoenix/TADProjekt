from robot import Robot
from environment import *
import path_algorithm
import pygame


pos = constants.get('robot_base')

if __name__ == '__main__':
    rob = [Robot(1, pos[0], pos[1]), Robot(2, pos[0], pos[1]+50), Robot(3, pos[0], pos[1]+100)]
    env = []
    for i in range(1,5):
        for j in range(1,8):
            env.append(Shelf((i*8+j), 50*i, 50*j))


    charging_points = [ChargingPoint(1, 700, 30), ChargingPoint(2, 700, 120), ChargingPoint(4, 700, 220), ChargingPoint(5, 700, 320)]
    unload_points = [UnloadPoint(40, 550), UnloadPoint(140, 550), UnloadPoint(240, 550), UnloadPoint(340, 550), UnloadPoint(440, 550)]
    pygame.init()
    pygame.display.set_caption("Symulacja")
    window_width = 800
    window_height = 600
    screen = pygame.display.set_mode((window_width, window_height))

    v = 0.5
    exit = False
    dir = [v, 0]
    dir1 = [v, 0]
    dir2 = [0, v]
    rob[0].set_destination(100, 120)
    rob[1].set_destination(200, 220)
    rob[2].set_destination(300, 320)

    iterations_counter = 0

    while not exit:
        iterations_counter = iterations_counter + 1
        if iterations_counter == 1000000:
            iterations_counter = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True

        screen.fill(constants.get('screen_color'))
        for x in rob:
            x.update()
            x.draw(screen)
        for x in env:
            x.draw(screen)
        for x in charging_points:
            x.draw(screen)
        for x in unload_points:
            x.draw(screen)
        if not rob[0].in_move:
            rob[0].get_shelf(env[4])
            rob[0].set_destination(300,50)
        env[0].move_down()
        pygame.display.flip()

        if iterations_counter % 10 == 0:
            for r in rob:
                x_from = r.get_position()
                new_path = path_algorithm.find_path(x_from, r.destination, rob, env)
                if new_path:
                    r.path = new_path

    pygame.quit()

