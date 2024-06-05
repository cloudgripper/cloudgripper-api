#!/bin/bash

# Path to the directory containing videos
video_dir="/proj/berzelius-2023-54/users/x_shuji/OccluManip/Foam/Quadruple/20230906/robotCR23/Test/"

dir1="$video_dir""Video"
dir2="$video_dir""Bottom_Video"

# Loop through all video files in the directory
for video_file in "$dir1"/*.mp4; do
    # Get the number of frames using ffprobe
    num_frames=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 "$video_file")

    # Check if the number of frames is less than 50
    if [ "$num_frames" -lt 50 ]; then
        echo "Video $video_file in $dir1 has less than 50 frames."
    fi
done

for video_file in "$dir2"/*.mp4; do
    # Get the number of frames using ffprobe
    num_frames=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 "$video_file")

    # Check if the number of frames is less than 50
    if [ "$num_frames" -lt 50 ]; then
        echo "Video $video_file in $dir2 has less than 50 frames."
    fi
done

