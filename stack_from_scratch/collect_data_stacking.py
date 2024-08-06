import argparse
import logging
import os
import threading
import time
import traceback
from configparser import ConfigParser
from typing import Optional, Tuple

import numpy as np
from autograsper import Autograsper, RobotActivity
from recording import Recorder

from library.rgb_object_tracker import all_objects_are_visible

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATE_LOCK = threading.Lock()
BOTTOM_IMAGE_LOCK = threading.Lock()
ERROR_EVENT = threading.Event()


class SharedState:
    def __init__(self):
        self.state: RobotActivity = RobotActivity.STARTUP
        self.recorder: Optional[Recorder] = None
        self.recorder_thread: Optional[threading.Thread] = None
        self.bottom_image_thread: Optional[threading.Thread] = None


shared_state = SharedState()


def load_config(config_file: str = "stack_from_scratch/config.ini") -> ConfigParser:
    config = ConfigParser()
    config.read(config_file)
    return config


def get_new_session_id(base_dir: str) -> int:
    if not os.path.exists(base_dir):
        return 1
    session_ids = [
        int(dir_name) for dir_name in os.listdir(base_dir) if dir_name.isdigit()
    ]
    return max(session_ids, default=0) + 1


def handle_error(exception: Exception) -> None:
    logger.error(f"Error occurred: {exception}")
    logger.error(traceback.format_exc())
    ERROR_EVENT.set()


def run_autograsper(
    autograsper: Autograsper,
    colors,
    block_heights,
    position_bank,
    stack_position,
    object_size,
) -> None:
    try:
        autograsper.run_grasping(
            colors, block_heights, position_bank, stack_position, object_size
        )
    except Exception as e:
        handle_error(e)


def setup_recorder(output_dir: str, robot_idx: str, config: ConfigParser) -> Recorder:
    session_id = "test"
    camera_matrix = np.array(eval(config["camera"]["m"]))
    distortion_coefficients = np.array(eval(config["camera"]["d"]))
    token = os.getenv("ROBOT_TOKEN")
    if not token:
        raise ValueError("ROBOT_TOKEN environment variable not set")
    return Recorder(
        session_id, output_dir, camera_matrix, distortion_coefficients, token, robot_idx
    )


def run_recorder(recorder: Recorder) -> None:
    try:
        recorder.record()
    except Exception as e:
        handle_error(e)


def monitor_state(autograsper: Autograsper, shared_state: SharedState) -> None:
    try:
        while not ERROR_EVENT.is_set():
            with STATE_LOCK:
                if shared_state.state != autograsper.state:
                    shared_state.state = autograsper.state
                    if shared_state.state == RobotActivity.FINISHED:
                        break
            time.sleep(0.1)
    except Exception as e:
        handle_error(e)


def is_stacking_successful(recorder: Recorder, colors) -> bool:
    return not all_objects_are_visible(colors, recorder.bottom_image, debug=False)


def monitor_bottom_image(recorder: Recorder, autograsper: Autograsper) -> None:
    try:
        while not ERROR_EVENT.is_set():
            if recorder and recorder.bottom_image is not None:
                with BOTTOM_IMAGE_LOCK:
                    autograsper.bottom_image = np.copy(recorder.bottom_image)
            time.sleep(0.1)
    except Exception as e:
        handle_error(e)


def create_new_data_point(script_dir: str) -> Tuple[str, str, str]:
    recorded_data_dir = os.path.join(script_dir, "recorded_data")
    new_session_id = get_new_session_id(recorded_data_dir)
    new_session_dir = os.path.join(recorded_data_dir, str(new_session_id))
    task_dir = os.path.join(new_session_dir, "task")
    restore_dir = os.path.join(new_session_dir, "restore")

    os.makedirs(task_dir, exist_ok=True)
    os.makedirs(restore_dir, exist_ok=True)

    return new_session_dir, task_dir, restore_dir


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Robot Controller")
    parser.add_argument("--robot_idx", type=str, required=True, help="Robot index")
    parser.add_argument(
        "--config",
        type=str,
        default="config.ini",
        help="Path to the configuration file",
    )
    return parser.parse_args()


def initialize(args: argparse.Namespace) -> Tuple[Autograsper, ConfigParser, str]:
    config = load_config()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    autograsper = Autograsper(args, output_dir="")
    return autograsper, config, script_dir


def start_threads(
    autograsper: Autograsper, config: ConfigParser
) -> Tuple[threading.Thread, threading.Thread, list]:
    colors = eval(config["experiment"]["colors"])
    block_heights = np.array(eval(config["experiment"]["block_heights"]))
    position_bank = eval(config["experiment"]["position_bank"])
    stack_position = eval(config["experiment"]["stack_position"])
    object_size = config.getfloat("experiment", "object_size")

    autograsper_thread = threading.Thread(
        target=run_autograsper,
        args=(
            autograsper,
            colors,
            block_heights,
            position_bank,
            stack_position,
            object_size,
        ),
    )
    monitor_thread = threading.Thread(
        target=monitor_state, args=(autograsper, shared_state)
    )

    autograsper_thread.start()
    monitor_thread.start()

    return autograsper_thread, monitor_thread, colors


def handle_state_changes(
    autograsper: Autograsper,
    config: ConfigParser,
    script_dir: str,
    colors,
    args: argparse.Namespace,
) -> None:
    prev_robot_activity = RobotActivity.STARTUP
    session_dir, task_dir, restore_dir = "", "", ""

    while not ERROR_EVENT.is_set():
        with STATE_LOCK:
            if shared_state.state != prev_robot_activity:
                if (
                    prev_robot_activity != RobotActivity.STARTUP
                    and shared_state.recorder
                ):
                    shared_state.recorder.write_final_image()

                if shared_state.state == RobotActivity.ACTIVE:
                    session_dir, task_dir, restore_dir = create_new_data_point(
                        script_dir
                    )
                    autograsper.output_dir = task_dir

                    if not shared_state.recorder:
                        shared_state.recorder = setup_recorder(
                            task_dir, args.robot_idx, config
                        )
                        shared_state.recorder_thread = threading.Thread(
                            target=run_recorder, args=(shared_state.recorder,)
                        )
                        shared_state.recorder_thread.start()
                        shared_state.bottom_image_thread = threading.Thread(
                            target=monitor_bottom_image,
                            args=(shared_state.recorder, autograsper),
                        )
                        shared_state.bottom_image_thread.start()

                    shared_state.recorder.start_new_recording(task_dir)
                    time.sleep(0.5)
                    autograsper.start_flag = True

                elif shared_state.state == RobotActivity.RESETTING:
                    status_message = (
                        "success"
                        if is_stacking_successful(shared_state.recorder, colors)
                        else "fail"
                    )
                    if status_message == "fail":
                        autograsper.failed = True

                    logger.info(status_message)
                    with open(
                        os.path.join(session_dir, "status.txt"), "w"
                    ) as status_file:
                        status_file.write(status_message)

                    autograsper.output_dir = restore_dir
                    shared_state.recorder.start_new_recording(restore_dir)

                prev_robot_activity = shared_state.state

            if shared_state.state == RobotActivity.FINISHED:
                if shared_state.recorder:
                    shared_state.recorder.stop()
                    time.sleep(1)
                    shared_state.recorder_thread.join()
                    shared_state.bottom_image_thread.join()
                break


def cleanup(
    autograsper_thread: threading.Thread, monitor_thread: threading.Thread
) -> None:
    ERROR_EVENT.set()
    autograsper_thread.join()
    monitor_thread.join()
    if shared_state.recorder_thread and shared_state.recorder_thread.is_alive():
        shared_state.recorder_thread.join()
    if shared_state.bottom_image_thread and shared_state.bottom_image_thread.is_alive():
        shared_state.bottom_image_thread.join()


def main():
    args = parse_arguments()
    autograsper, config, script_dir = initialize(args)

    autograsper_thread, monitor_thread, colors = start_threads(autograsper, config)

    try:
        handle_state_changes(autograsper, config, script_dir, colors, args)
    except Exception as e:
        handle_error(e)
    finally:
        cleanup(autograsper_thread, monitor_thread)


if __name__ == "__main__":
    main()
