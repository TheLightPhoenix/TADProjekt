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

    exit = False
    points1 = [[400, 500], [200, 50], [300, 50], [100, 450], [40, 550]]
    points2 = [[400, 500], [200, 100], [300, 50], [100, 450], [140, 550]]
    points3 = [[400, 500], [200, 150], [300, 50], [200, 450], [240, 550]]
    i_points1 = 0
    i_points2 = 0
    i_points3 = 0
    rob[0].set_destination(points1[i_points1][0], points1[i_points1][1])
    rob[1].set_destination(points2[i_points2][0], points2[i_points2][1])
    rob[2].set_destination(points3[i_points3][0], points3[i_points3][1])
    iterations_counter = 0

    algorithm = True
    while not exit:
        iterations_counter = iterations_counter + 1
        if iterations_counter == 1000000:
            iterations_counter = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True

        screen.fill(constants.get('screen_color'))
        for x in charging_points:
            x.draw(screen)
        for x in unload_points:
            x.draw(screen)
        for x in rob:
            x.update()
            x.draw(screen)
        for x in env:
            x.update()
            x.draw(screen)

        if algorithm:
            if iterations_counter % 10 == 0:
                for r in rob:
                    x_from = r.get_position()
                    new_path = path_algorithm.find_path(x_from, points1[2], rob, env)
                    if new_path:
                        r.path = new_path
        else:
            if not rob[0].in_move:
                i_points1 += 1
                if i_points1 > 4:
                    i_points1 = 4
                if i_points1 == 2:
                    rob[0].get_shelf(env[21])
                rob[0].set_destination(points1[i_points1][0], points1[i_points1][1])

            if not rob[1].in_move:
                i_points2 += 1
                if i_points2 > 4:
                    i_points2 = 4
                if i_points2 == 2:
                    rob[1].get_shelf(env[22])
                rob[1].set_destination(points2[i_points2][0], points2[i_points2][1])

            if not rob[2].in_move:
                i_points3 += 1
                if i_points3 > 4:
                    i_points3 = 4
                if i_points3 == 2:
                    rob[2].get_shelf(env[23])
                rob[2].set_destination(points3[i_points3][0], points3[i_points3][1])

        pygame.display.flip()

    pygame.quit()

