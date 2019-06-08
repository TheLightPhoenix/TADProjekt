import numpy as np


width = 800
height = 600
robot_size = 40
m_width = int(width/robot_size)
m_height = int(height/robot_size)


def find_path(xy_from, xy_to, robots, shelfs):

    # translate points to unit-size matrix
    x_from, y_from = xy_from
    x_to, y_to = xy_to
    xy_from = int(x_from/robot_size), int(y_from/robot_size)
    xy_to = int(x_to/robot_size), int(y_to/robot_size)

    # check if path is (X -> X)
    if x_from == x_to and y_from == y_to:
        return [xy_from]

    print("Finding path from: " + str(xy_from) + " to: " + str(xy_to))
    matrix = np.zeros((m_width, m_height))
    matrix = place_obstacles(matrix, robots, shelfs)

    path = propagate_path(matrix, xy_from, xy_to)

    print_matrix(matrix, path)

    if path:
        path = translate_back_to_real_sizes(path)

    return path


def translate_back_to_real_sizes(path):
    new_path = []
    for x, y in path:
        new_path.append((x*robot_size, y*robot_size))
    return new_path


def propagate_path(matrix, xy_from, xy_to):
    x, y = xy_from
    x_to, y_to = xy_to
    next_points = [(int(x), int(y))]
    matrix[x, y] = 1
    for iteration in range(1, 100):
        current_iteration_next_points = []
        # mark neighbours as next points
        for point in next_points:
            neighbours = get_neighbours(point)
            accessible_neighbours = find_accessible_neighbours(neighbours, matrix)
            for neighbour in accessible_neighbours:
                nx, ny = neighbour
                matrix[nx, ny] = iteration + 1
                # check if destination is found
                if nx == x_to and ny == y_to:
                    return rollback_path(matrix, (x_to, y_to))
                else:
                    current_iteration_next_points.append(neighbour)

        # replace next points
        next_points = []
        for n in current_iteration_next_points:
            next_points.append(n)

    # print("Path not found!")


def rollback_path(matrix, xy_to):
    path = []
    x_to, y_to = xy_to
    last_iteration = int(matrix[x_to, y_to])
    path.append(xy_to)
    previous_neighbour = xy_to
    for i in range(last_iteration-1):
        previous_neighbour = find_previous_iteration_neighbour(matrix, previous_neighbour)
        path.append(previous_neighbour)

    return reverse(path)


def reverse(path):
    rev_path = []
    for p in range(len(path)):
        rev_path.append(path[len(path) - p - 1])
    return rev_path


def find_previous_iteration_neighbour(matrix, xy):
    neighbours = get_neighbours(xy)
    accessible_neighbours = find_accessible_neighbours(neighbours, matrix, clear=False)
    x, y = xy
    iteration = matrix[x, y]
    for n in accessible_neighbours:
        nx, ny = n
        if matrix[nx, ny] + 1 == iteration:
            return n


def find_accessible_neighbours(neighbours, matrix, clear=True):
    accessible_neighbours = []
    for point in neighbours:
        x, y = point
        if x < 0 or y < 0 or x >= m_width or y >= m_height:
            continue
        if clear:
            if matrix[x, y] == 0:
                accessible_neighbours.append(point)
        else:
            if matrix[x, y] >= 0:
                accessible_neighbours.append(point)
    return accessible_neighbours


def get_neighbours(point):
    # print("Get neighbours")
    # print(point)
    x, y = point
    neighbours = []

    # neighbours.append((x-1, y-1))
    neighbours.append((x, y-1))
    # neighbours.append((x+1, y-1))

    neighbours.append((x-1, y))
    neighbours.append((x+1, y))

    # neighbours.append((x-1, y+1))
    neighbours.append((x, y+1))
    # neighbours.append((x+1, y+1))

    return neighbours


def print_matrix(matrix, path):

    clear_matrix(matrix, path)

    # print(m_width, m_height)
    # print("MATRIX:")
    for w in range(m_width):
        line = " "
        for h in range(m_height):
            if int(matrix[w, h]) == 0 or int(matrix[w, h] == -2):
                line = line + "  ."
            elif int(matrix[w, h]) == -1:
                line = line + "  x"
            else:
                if matrix[w, h] > 9:
                    line = line + " " + str(int(matrix[w, h]))
                else:
                    line = line + "  " + str(int(matrix[w, h]))
        print(line)


def clear_matrix(matrix, path):
    if not path:
        return
    for w in range(m_width):
        for h in range(m_height):
            if matrix[w, h] >= 0:
                matrix[w, h] = -2
    for i in range(len(path)):
        point = path[i]
        x, y = point
        matrix[x, y] = i+1


def place_obstacles(matrix, robots, shelfs):
    for robot in robots:
        robot_x, robot_y = robot.get_position()
        x = int(robot_x/robot_size)
        y = int(robot_y/robot_size)
        matrix[x, y] = -1
    for shelf in shelfs:
        shelf_x, shelf_y = shelf.get_position()
        x = int(shelf_x/robot_size)
        y = int(shelf_y/robot_size)
        matrix[x, y] = -1
    return matrix
