import picar_4wd as fc
import time as time
import math
import numpy as np

speed = 5
reduced_speed = 2

# Ultrasonic
ANGLE_RANGE = 180
STEP = 4 #18
us_step = STEP
angle_distance = [0,0]
current_angle = 0
max_angle = ANGLE_RANGE/2
min_angle = -ANGLE_RANGE/2
scan_list = []
angle_list = []

errors = []


#exec(compile(open("/home/pi/examples/lite/examples/object_detection/raspberry_pi/detect.py", "rb").read(), "/home/pi/examples/lite/examples/object_detection/raspberry_pi/detect.py", "exec"))

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
            if distance != -2 and distance < 50:
                x_coor = distance * math.sin(math.radians(angle))
                y_coor = distance * math.cos(math.radians(angle))
                list_x.append(x_coor)
                list_y.append(y_coor)

        list_xy = list(zip(list_x, list_y))
        return list_xy

def create_coor_map():
    while True:
        object_coor = get_object_coordinates()
        if not object_coor:
            continue
        print(object_coor)

        object_map = np.zeros((36,36), dtype=int)
        np.set_printoptions(threshold=4000)
        y_start = np.int(len(object_map))
        x_start = np.int(np.ceil(len(object_map[0]) / 2))

        for index, tuple in enumerate(object_coor):
            x_c = tuple[0]
            y_c = tuple[1]
            x_index = np.int(x_start - (np.ceil((x_c / 4))))
            y_index = np.int(y_start - (np.ceil((y_c / 4))))
            print("x: ", x_index, " -- y: ", y_index)
            object_map[y_index, x_index] = 1
            object_map[0,10] = 9
        return object_map

def main():

    while True:
        object_map = create_coor_map()
        print(object_map)


if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()