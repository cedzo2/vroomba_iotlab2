import picar_4wd as fc
import time as time
import math
import numpy as np
import heapq

speed = 5
reduced_speed = 2

ANGLE_RANGE = 180
STEP = 4 #18
us_step = STEP
angle_distance = [0,0]
current_angle = 0
max_angle = ANGLE_RANGE/2
min_angle = -ANGLE_RANGE/2
scan_list = []
angle_list = []
object_nodes = []
GridLocation = tuple[int,int]

errors = []

class Node():
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __repr__(self):
        return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

    def __lt__(self, other):
        return self.f < other.f

    def __gt__(self, other):
        return self.f > other.f

def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]

def perform_a_star(coor_map, start, end):
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    open_list = []
    closed_list = []

    heapq.heapify(open_list)
    heapq.heappush(open_list, start_node)

    outer_iterations = 0
    max_iterations = (len(coor_map[0]) * len(coor_map) // 2)

    neighbors = ((1, 0), (0, 1), (-1, 0),(0, -1),)

    while len(open_list) > 0:

        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        if current_node == end_node:
            return return_path(current_node)

        children = []

        for new_position in neighbors:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            if node_position[0] > (len(coor_map) - 1) or node_position[0] < 0 or node_position[1] > (len(coor_map[len(coor_map) - 1]) - 1) or node_position[1] < 0:
                continue

            if coor_map[node_position[0]][node_position[1]] != 0:
                continue

            new_node = Node(current_node, node_position)
            children.append(new_node)

        for child in children:
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) + (child.position[1] - end_node.position[1]))
            child.f = child.g + child.h

            if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                continue

            heapq.heappush(open_list, child)

    print("couldn't find a path")
    return None


def scan_distance():
    global scan_list, current_angle, us_step, angle_list
    current_angle += us_step
    if current_angle >= max_angle:
        current_angle = max_angle
        us_step = -STEP
    elif current_angle <= min_angle:
        current_angle = min_angle
        us_step = STEP
    status = fc.get_distance_at(current_angle)

    scan_list.append(status)
    angle_list.append(current_angle)
    if current_angle == min_angle or current_angle == max_angle:
        if us_step < 0:
            # print("reverse")
            scan_list.reverse()
            angle_list = [element * -1 for element in angle_list]
        # print(scan_list)
        tmp = scan_list.copy()
        tmp2 = angle_list.copy()
        dist_angle = list(zip(tmp, tmp2))
        scan_list = []
        angle_list = []
        print(dist_angle)
        return dist_angle
    else:
        return False

def get_object_coordinates():
    while True:
        distance_angle = scan_distance()
        if not distance_angle:
            continue

        list_x = []
        list_y = []
        for index, tuple in enumerate(distance_angle):
            distance = tuple[0]
            angle = tuple[1]
            if distance != -2 and distance < 65:
                x_coor = distance * math.sin(math.radians(angle))
                y_coor = distance * math.cos(math.radians(angle))
                list_x.append(x_coor)
                list_y.append(y_coor)

        list_xy = list(zip(list_x, list_y))
        return list_xy

def find_object_nodes(position, orientation):
    object_map = np.zeros((36,36), dtype=int)
    while True:
        object_coor = get_object_coordinates()
        if not object_coor:
            continue
        print(object_coor)

        np.set_printoptions(threshold=4000)
        y_start = np.int(len(object_map))
        x_start = np.int(np.ceil(len(object_map[0]) / 2))

        x_list = []
        y_list = []

        if orientation == "forward":
            for index, tuple in enumerate(object_coor):
                x_c = tuple[0]
                y_c = tuple[1]
                x_index = np.int(position[0] - (np.ceil((x_c / 4))))
                y_index = np.int(position[1] - (np.ceil((y_c / 4))))
                print("x: ", x_index, " -- y: ", y_index)
                if y_index < len(object_map) and x_index < len(object_map[0]):
                    object_map[y_index, x_index] = 1
                    x_list.append(x_index)
                    y_list.append(y_index)
                    object_nodes.append([x_index, y_index])

        if orientation == "left":
            for index, tuple in enumerate(object_coor):
                x_c = tuple[0]
                y_c = tuple[1]
                x_index = np.int(position[0] - (np.ceil((y_c / 4))))
                y_index = np.int(position[1] + (np.ceil((x_c / 4))))
                print("x: ", x_index, " -- y: ", y_index)
                if y_index < len(object_map) and x_index < len(object_map[0]):
                    object_map[y_index, x_index] = 1
                    x_list.append(x_index)
                    y_list.append(y_index)
                    object_nodes.append([x_index, y_index])

        if orientation == "right":
            for index, tuple in enumerate(object_coor):
                x_c = tuple[0]
                y_c = tuple[1]
                x_index = np.int(position[0] + (np.ceil((y_c / 4))))
                y_index = np.int(position[1] - (np.ceil((x_c / 4))))
                print("x: ", x_index, " -- y: ", y_index)
                if y_index < len(object_map) and x_index < len(object_map[0]):
                    object_map[y_index, x_index] = 1
                    x_list.append(x_index)
                    y_list.append(y_index)
                    object_nodes.append([x_index, y_index])

        if orientation == "backward":
            for index, tuple in enumerate(object_coor):
                x_c = tuple[0]
                y_c = tuple[1]
                x_index = np.int(position[0] + (np.ceil((x_c / 4))))
                y_index = np.int(position[1] + (np.ceil((y_c / 4))))
                print("x: ", x_index, " -- y: ", y_index)
                if y_index < len(object_map) and x_index < len(object_map[0]):
                    object_map[y_index, x_index] = 1
                    x_list.append(x_index)
                    y_list.append(y_index)
                    object_nodes.append([x_index, y_index])

        return object_nodes

def neighbors(node):
    dirs = [[1,0],[0,1],[-1,0],[0,-1]]
    result = []
    for dir in dirs:
        result.append([node[0] + dir[0], node[1] + dir[1]])
        if neighbor in all_nodes:
            result.append(neighbor)
    return result

def forward_4cm():
    speed4 = fc.Speed(5)
    speed4.start()
    fc.forward(2)
    x = 0
    for i in range(1):
        time.sleep(0.11)
        speed = speed4()
        x += speed * 0.1
    speed4.deinit()
    fc.stop()

def backward_4cm():
    speed4 = fc.Speed(5)
    speed4.start()
    fc.backward(2)
    x = 0
    for i in range(1):
        time.sleep(0.08)
        speed = speed4()
        x += speed * 0.1
    speed4.deinit()
    fc.stop()

def right_90():
    speed4 = fc.Speed(5)
    speed4.start()
    fc.turn_right(40)
    x = 0
    for i in range(1):
        time.sleep(0.7)
        speed = speed4()
        x += speed * 0.1
    speed4.deinit()
    fc.stop()

def left_90():
    speed4 = fc.Speed(5)
    speed4.start()
    fc.turn_left(40)
    x = 0
    for i in range(1):
        time.sleep(0.68)
        speed = speed4()
        x += speed * 0.1
    speed4.deinit()
    fc.stop()

def main():
    object_map = np.zeros((36,36), dtype=int)
    for nodes in object_map[0]:
        object_map[0][nodes] = 1
    all_nodes = []
    for x in range(36):
            for y in range(36):
                all_nodes.append([x,y])
    start = (np.int(np.ceil(len(object_map[0]) / 2)), np.int(len(object_map)))
    position = "forward"
    while True:
        object_nodes = find_object_nodes(start, position)
        print(object_nodes)
        for node in all_nodes:
            if node in object_nodes:
                object_map[node[1]][node[0]] = 1
        print(object_map)
        end = (25, 20)
        path = perform_a_star(object_map, start, end)
        #next_direction1 = (path[1][0] - path[0][0], path[0][1] - path[1][1])
        if len(path) > 5:
            ranger = 6
        else:
            ranger = len(path)
        for check in range(ranger):
                start = path[check]
                if start == end:
                    quit()
                if check + 1 < len(path):
                    direction = (path[check+1][0] - path[check][0], path[check][1] - path[check+1][1])
                if position == "forward":
                    if direction == (-1, 0):
                        left_90()
                        position = "left"
                    if direction == (1, 0):
                        right_90()
                        position = "right"
                    if direction == (0, -1):
                        backward_4cm()
                        position = "forward"
                        break
                    forward_4cm()
                elif position == "left":
                    if direction == (1, 0):
                        backward_4cm()
                        position = "left"
                        break
                    if direction == (0, 1):
                        right_90()
                        position = "forward"
                    if direction == (0, -1):
                        left_90()
                        position = "backward"
                    forward_4cm()
                elif position == "right":
                    if direction == (-1, 0):
                        backward_4cm()
                        position = "right"
                        break
                    if direction == (0, 1):
                        left_90()
                        position = "forward"
                    if direction == (0, -1):
                        right_90()
                        position = "backward"
                    forward_4cm()
                elif position == "backward":
                    if direction == (-1, 0):
                        right_90()
                        position = "left"
                    if direction == (1, 0):
                        left_90()
                        position = "right"
                    if direction == (0, 1):
                        backward_4cm()
                        position = "backward"
                        break
                    forward_4cm()

        print(path)
        print(direction)
        #print(len(all_nodes))



if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()