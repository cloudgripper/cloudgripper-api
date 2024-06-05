import argparse
import os
import time
import cv2
from client.cloudgripper_client import GripperRobot
from library.bottom_image_preprocessing import rotate
from library.calculate_starting_point import *
from library.calibration import order2movement, undistort, undistort_fisheye
from library.Camera2Robot import *
from library.object_tracking import *
from library.utils import get_undistorted_bottom_image


class Recorder:
    def __init__(self, session_id, output_dir, m, d, token, idx):
        self.stop_flag = False
        self.session_id = session_id
        self.output_dir = output_dir
        self.m = m
        self.d = d
        self.token = token
        self.robot_idx = idx
        self.video_writer_top = None
        self.video_writer_bottom = None
        self.frame_counter = 0
        self.video_counter = 0

    def _start_new_video(self, output_video_dir, output_bottom_video_dir, video_counter, fourcc, image_shape, bottom_image_shape):
        video_filename_top = os.path.join(
            output_video_dir, f"video_{video_counter}.mp4")
        video_writer_top = cv2.VideoWriter(
            video_filename_top, fourcc, 5.0, image_shape)

        video_filename_bottom = os.path.join(
            output_bottom_video_dir, f"video_{video_counter}.mp4")
        video_writer_bottom = cv2.VideoWriter(
            video_filename_bottom, fourcc, 5.0, bottom_image_shape)

        return video_writer_top, video_writer_bottom

    def record(self, start_new_video_every=None):
        print("Recorder started")
        robot = GripperRobot(self.robot_idx, self.token)
        self._initialize_directories()

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.frame_counter = 0
        self.video_counter = 0
        self.video_writer_top = None
        self.video_writer_bottom = None

        while not self.stop_flag:
            print("Recording frame...")
            imageTop, timestampTop = robot.getImageTop()
            bottom_image = get_undistorted_bottom_image(robot, self.m, self.d)

            if start_new_video_every is not None and self.frame_counter % start_new_video_every == 0:
                if self.video_writer_top is not None:
                    self.video_writer_top.release()
                if self.video_writer_bottom is not None:
                    self.video_writer_bottom.release()

                self.video_writer_top, self.video_writer_bottom = self._start_new_video(
                    self.output_video_dir, self.output_bottom_video_dir, self.video_counter, fourcc,
                    (imageTop.shape[1], imageTop.shape[0]
                     ), (bottom_image.shape[1], bottom_image.shape[0])
                )

                self.video_counter += 1
            elif start_new_video_every is None and self.frame_counter == 0:
                self.video_writer_top, self.video_writer_bottom = self._start_new_video(
                    self.output_video_dir, self.output_bottom_video_dir, self.video_counter, fourcc,
                    (imageTop.shape[1], imageTop.shape[0]
                     ), (bottom_image.shape[1], bottom_image.shape[0])
                )

                self.video_counter += 1

            self.video_writer_top.write(imageTop)
            self.video_writer_bottom.write(bottom_image)

            self.frame_counter += 1

            cv2.imshow("ImageBottom_" + self.robot_idx, bottom_image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.stop_flag = True

        print("Stopping video writers")
        # release the video writer
        if self.video_writer_top is not None:
            self.video_writer_top.release()
        if self.video_writer_bottom is not None:
            self.video_writer_bottom.release()

        print("Saving final image")
        # write the final top image
        imageTop, timestampTop = robot.getImageTop()
        cv2.imwrite(os.path.join(self.final_image_dir,
                    f"final_image_{self.video_counter}.jpg"), imageTop)

        cv2.destroyAllWindows()
        print("Recorder stopped")

    def _initialize_directories(self):
        self.output_video_dir = os.path.join(self.output_dir, "Video")
        self.output_bottom_video_dir = os.path.join(
            self.output_dir, "Bottom_Video")
        self.final_image_dir = os.path.join(self.output_dir, "Final_Image")

        os.makedirs(self.output_video_dir, exist_ok=True)
        os.makedirs(self.output_bottom_video_dir, exist_ok=True)
        os.makedirs(self.final_image_dir, exist_ok=True)

    def start_new_recording(self, new_output_dir):
        self.output_dir = new_output_dir
        self._initialize_directories()
        self.frame_counter = 0
        self.video_counter = 0
        self.stop_flag = False
        print(f"Started new recording in directory: {new_output_dir}")

    def stop(self):
        self.stop_flag = True
        print("Stop flag set to True")


# if called as main, run the main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Robot Index")
    parser.add_argument("--robot_idx", type=str,
                        required=True, help="Robot Index")
    parser.add_argument(
        "--output_dir", help="The prefix for the directories", required=True)

    args = parser.parse_args()
    idx = args.robot_idx
    prefix = args.output_dir

    token = os.getenv("ROBOT_TOKEN", "default_token")

    # Note: this might be different for each robot, but generally similar
    m, d = (
        [
            [505.24537524391866, 0.0, 324.5096286632362],
            [0.0, 505.6456651337437, 233.54118730278543],
            [0.0, 0.0, 1.0],
        ],
        [
            [-0.07727407195057368],
            [-0.047989733519315944],
            [0.12157420705123315],
            [-0.09667542135039282],
        ],
    )

    output_dir = prefix
    recorder = Recorder("test", output_dir, m, d, token, idx)
    recorder.record(start_new_video_every=30)
