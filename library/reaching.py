import numpy as np

def interpolate(start, target, max_length):
    # start = np.array(start)
    # target = np.array(target)
    dist = np.linalg.norm(target - start)
    sin, cos = (target - start) / dist
    if dist <= max_length:
        return target
    else:
        return np.array([start[0]+max_length*sin, start[1]+max_length*cos])

def move_further(start, target, step_length):
    start = np.array(start)
    target = np.array(target)
    dist = np.linalg.norm(target - start)
    sin, cos = (target - start) / dist
    return np.array([target[0] + step_length * sin, target[1] + step_length * cos])

def reaching_policy(start, target, max_length, random=False, max_step=20, MOVE_FURTHER=0.1):
    start = np.array(start)
    target = np.array(target)
    dist = np.linalg.norm(target - start)
    path = start
    step_counter = 0
    while dist > max_length and step_counter < max_step:
        next_pos = interpolate(start, target, max_length)
        if random:
            next_pos = np.clip(next_pos + max_length * np.random.rand(2,), 0, 1)
        path = np.concatenate((path, next_pos), axis=0)
        start = next_pos
        dist = np.linalg.norm(target - start)
        step_counter += 1
    path = np.concatenate((path, target), axis=0)
    if MOVE_FURTHER is not None:
        final_point = move_further(start, target, MOVE_FURTHER)
        path = np.concatenate((path, final_point))
    return path.reshape((-1, 2))