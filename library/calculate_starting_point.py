import numpy as np

def calculate_starting_point(robot_position):
    x = robot_position[0]
    y = robot_position[1]

    distance_00_01 = np.sqrt((x - 0) ** 2)
    distance_00_10 = np.sqrt((y - 0) ** 2)
    distance_01_11 = np.sqrt((y - 1) ** 2)
    distance_10_11 = np.sqrt((x - 1) ** 2)

    # select the shortest distance and return the name
    if distance_00_01 <= distance_00_10 and distance_00_01 <= distance_01_11 and distance_00_01 <= distance_10_11:
        return np.array([0, y])
    elif distance_00_10 <= distance_00_01 and distance_00_10 <= distance_01_11 and distance_00_10 <= distance_10_11:
        return np.array([x, 0])
    elif distance_01_11 <= distance_00_01 and distance_01_11 <= distance_00_10 and distance_01_11 <= distance_10_11:
        return np.array([x, 1])
    elif distance_10_11 <= distance_00_01 and distance_10_11 <= distance_00_10 and distance_10_11 <= distance_01_11:
        return np.array([1, y])
    else:
        return None

    