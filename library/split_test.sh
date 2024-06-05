#!/bin/bash
​
# Change to the "robotCR18" directory
cd /proj/berzelius-2023-54/users/x_shuji/OccluManip/Foam/Quadruple/20230906/robotCR23
​
# Create the "Test" directory and its subdirectories
mkdir -p Test/Position Test/Video Test/Bottom_Video
​
# Get the last video number
last_video_num=$(ls Position/ | grep -oE '[0-9]+' | sort -n | tail -1)
echo $(ls Position/ | grep -oE '[0-9]+' | sort -n | tail -1)
​
# Given a starting video number
video_num=6410  # Replace with your desired starting video number
​
# Loop through the video numbers and move the corresponding files
while [ $video_num -le $last_video_num ]; do
    mv Position/video_${video_num}.txt Test/Position/
    mv Video/video_${video_num}.mp4 Test/Video/
    mv Bottom_Video/video_${video_num}.mp4 Test/Bottom_Video/
    
    # Increment video_num for the next iteration
    video_num=$((video_num + 1))
done
​
# Go back to the previous directory
cd -