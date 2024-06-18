import argparse
import os
import threading
import time

import numpy as np
from autograsper import Autograsper, RobotActivity
from recording import Recorder

prev_robot_activity = RobotActivity.STARTUP
curr_robot_activity = RobotActivity.STARTUP

state_lock = threading.Lock()
shared_state = RobotActivity.STARTUP
recorder_thread = None
recorder = None


def get_new_session_id(base_dir):
    max_id = 0
    if os.path.exists(base_dir):
        for dir_name in os.listdir(base_dir):
            if dir_name.isdigit():
                session_id = int(dir_name)
                if session_id > max_id:
                    max_id = session_id
    return max_id + 1


def run_autograsper(autograsper):
    autograsper.run_grasping()


def setup_recorder(output_dir, robot_idx):
    session_id = "test"
    m, d = (
        np.array(
            [
                [505.24537524391866, 0.0, 324.5096286632362],
                [0.0, 505.6456651337437, 233.54118730278543],
                [0.0, 0.0, 1.0],
            ]
        ),
        np.array(
            [
                -0.07727407195057368,
                -0.047989733519315944,
                0.12157420705123315,
                -0.09667542135039282,
            ]
        ),
    )

    token = os.getenv("ROBOT_TOKEN", "default_token")
    if token == "default_token":
        raise ValueError("ROBOT_TOKEN environment variable not set")

    return Recorder(session_id, output_dir, m, d, token, robot_idx)


def run_recorder(recorder):
    recorder.record(start_new_video_every=30)


def state_monitor(autograsper):
    global shared_state
    while True:
        with state_lock:
            if shared_state != autograsper.state:
                shared_state = autograsper.state
                if shared_state == RobotActivity.FINISHED:
                    break
        time.sleep(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Robot Controller")
    parser.add_argument("--robot_idx", type=str, required=True, help="Robot index")

    args = parser.parse_args()
    robot_idx = args.robot_idx
    script_dir = os.path.dirname(os.path.abspath(__file__))

    def create_new_data_point():
        recorded_data_dir = os.path.join(script_dir, "recorded_data")
        new_session_id = get_new_session_id(recorded_data_dir)
        new_session_dir = os.path.join(recorded_data_dir, str(new_session_id))
        os.makedirs(new_session_dir, exist_ok=True)

        task_dir = os.path.join(new_session_dir, "task")
        restore_dir = os.path.join(new_session_dir, "restore")
        os.makedirs(task_dir, exist_ok=True)
        os.makedirs(restore_dir, exist_ok=True)

        return new_session_dir, task_dir, restore_dir

    # Create initial data point with "task" subfolder
    session_dir, task_dir, restore_dir = create_new_data_point()
    args = argparse.Namespace(robot_idx=robot_idx, output_dir=task_dir)
    autograsper = Autograsper(args, task_dir)

    recorder = setup_recorder(task_dir, robot_idx)

    # Run Autograsper and Recorder in parallel
    autograsper_thread = threading.Thread(target=run_autograsper, args=(autograsper,))
    recorder_thread = threading.Thread(target=run_recorder, args=(recorder,))
    monitor_thread = threading.Thread(target=state_monitor, args=(autograsper,))

    autograsper_thread.start()
    recorder_thread.start()
    monitor_thread.start()

    while True:
        with state_lock:
            if shared_state != prev_robot_activity:
                print("State change detected:", prev_robot_activity, "->", shared_state)

                if prev_robot_activity is not RobotActivity.STARTUP:
                    recorder.write_final_image()

                if shared_state == RobotActivity.ACTIVE:
                    # Create a new data point for task
                    session_dir, task_dir, restore_dir = create_new_data_point()
                    autograsper.output_dir = task_dir
                    recorder.start_new_recording(task_dir)
                elif shared_state == RobotActivity.RESETTING:
                    autograsper.output_dir = restore_dir
                    recorder.start_new_recording(restore_dir)

                prev_robot_activity = shared_state

            if shared_state == RobotActivity.FINISHED:
                if recorder is not None:
                    recorder.stop()  # Ensure recorder is stopped when finished
                    time.sleep(1)
                    recorder_thread.join()  # Ensure the recorder thread has finished
                break

    print("Final robot activity:", prev_robot_activity)

    autograsper_thread.join()
    monitor_thread.join()
