import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
from tqdm import tqdm


def combine_videos(input_directory, output_file):
    # Get list of video files in the input directory
    video_files = sorted(
        [
            f
            for f in os.listdir(input_directory)
            if f.endswith(".mp4")
            and "_" in f
            and f.split("_")[1].split(".")[0].isdigit()
        ],
        key=lambda x: int(x.split("_")[1].split(".")[0]),
    )

    # Load video clips
    clips = []
    for f in tqdm(video_files, desc="Loading video files"):
        try:
            clip = VideoFileClip(os.path.join(input_directory, f))
            clips.append(clip)
        except Exception as e:
            print(f"Error loading {f}: {e}")

    # Check if there are clips to concatenate
    if not clips:
        raise ValueError(f"No valid video clips found in {input_directory}")

    # Concatenate video clips
    combined_clip = concatenate_videoclips(clips)

    # Write the combined video to a file
    combined_clip.write_videofile(output_file, codec="libx264")

    return combined_clip


def split_video(clip, frame_size, output_directory):
    total_duration = clip.duration  # Total duration in seconds
    fps = clip.fps

    total_frames = int(total_duration * fps)  # Calculate total frames
    start_frame = 0
    part = 0

    while start_frame < total_frames:
        end_frame = min(start_frame + frame_size, total_frames)

        # Calculate start and end times in seconds
        start_time = start_frame / fps
        end_time = end_frame / fps

        subclip = clip.subclip(start_time, end_time)
        output_file = os.path.join(output_directory, f"part_{part}.mp4")
        subclip.write_videofile(output_file, codec="libx264")

        start_frame = end_frame
        part += 1


def cleanup_files(input_directory):
    # Delete old video_x files and the combined.mp4 file
    for f in os.listdir(input_directory):
        if f.endswith(".mp4") and (f.startswith("video_") or f == "combined.mp4"):
            os.remove(os.path.join(input_directory, f))

    # Rename part_x.mp4 files to video_x.mp4 files
    for part_file in os.listdir(input_directory):
        if part_file.startswith("part_") and part_file.endswith(".mp4"):
            part_number = part_file.split("_")[1].split(".")[0]
            new_name = f"video_{part_number}.mp4"
            os.rename(
                os.path.join(input_directory, part_file),
                os.path.join(input_directory, new_name),
            )


def main():
    for x in range(1, 206):
        input_directory = f"stack_from_scratch/recorded_data/{x}/task/Bottom_Video/"  # Directory containing input MP4 files

        # Check if the input directory exists
        if not os.path.exists(input_directory):
            print(f"Directory {input_directory} does not exist. Skipping...")
            continue

        output_combined_file = os.path.join(
            input_directory, "combined.mp4"
        )  # Path for the combined video file
        output_directory = input_directory
        frame_size = 30  # Fixed frame size for each split part

        try:
            print(f"Processing directory: {input_directory}")
            # Combine videos
            combined_clip = combine_videos(input_directory, output_combined_file)

            print(f"Splitting combined video: {output_combined_file}")
            # Split combined video
            split_video(combined_clip, frame_size, output_directory)

            # Close the combined clip to release resources
            combined_clip.close()

            # Cleanup files
            print(f"Cleaning up files in directory: {input_directory}")
            cleanup_files(input_directory)

            print(f"Finished processing directory: {input_directory}")
        except Exception as e:
            print(f"Error processing directory {input_directory}: {e}")


if __name__ == "__main__":
    main()
