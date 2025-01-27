import json
import os

import cv2
import numpy as np

# Define epsilon for comparison
EPSILON = 1e-2


def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception:
        print("file not found")
        return None


def compare_values(val1, val2, epsilon=EPSILON):
    """Compare two values with a given epsilon."""
    return np.abs(val1 - val2) < epsilon


def find_matching_state(order, states, start_idx):
    """
    Find the first state index where the order is successfully carried out,
    starting from start_idx.
    """
    order_type = order["order_type"]
    order_value = order.get("order_value", [])

    for idx in range(start_idx - 1, len(states)):
        idx = max(0, idx)
        state = states[idx]

        if order_type == "MOVE_XY":
            if (len(order_value) == 2 and
                compare_values(order_value[0], state["x_norm"]) and
                compare_values(order_value[1], state["y_norm"])):
                return idx

        elif order_type == "MOVE_Z":
            if len(order_value) == 1 and compare_values(order_value[0], state["z_norm"]):
                return idx

        elif order_type == "GRIPPER_OPEN":
            # Match with claw_norm close to 1.0
            if compare_values(1.0, state["claw_norm"]):
                return idx

        elif order_type == "GRIPPER_CLOSE":
            # Match with claw_norm close to 0.21/0.24/0.25/0.30
            if (compare_values(0.30, state["claw_norm"]) or
                compare_values(0.25, state["claw_norm"]) or
                compare_values(0.24, state["claw_norm"]) or
                compare_values(0.21, state["claw_norm"])):
                return idx

    return None


def get_total_video_frames(video_dir_path):
    """
    Return the total number of frames across all .mp4 files
    in the specified directory. We sum them so that code
    treats multiple .mp4 as concatenated in time.
    """
    sum_frames = 0
    if not os.path.exists(video_dir_path):
        return 0
    for f in sorted(os.listdir(video_dir_path)):
        if f.endswith(".mp4"):
            cap = cv2.VideoCapture(os.path.join(video_dir_path, f))
            sum_frames += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
    return sum_frames


def compute_final_order_from_matches(matching_states):
    """
    Mimics the logic in save_results to figure out the final 'current_order'
    after all matched orders have been applied. Returns that as a dict.
    """
    if not matching_states:
        # If nothing matched, fallback to some default
        return {
            "x_norm": 0.0,
            "y_norm": 0.7,
            "z_norm": 1.0,
            "rotation": 0.0,
            "claw_norm": 0.0
        }

    # Start from the first state's values
    _, _, first_state = matching_states[0]
    current_order = {
        "x_norm": first_state.get("x_norm", 0.0),
        "y_norm": first_state.get("y_norm", 0.0),
        "z_norm": first_state.get("z_norm", 0.0),
        "rotation": first_state.get("rotation", 0.0),
        "claw_norm": first_state.get("claw_norm", 0.0),
    }

    for (order, _, _) in matching_states:
        # If there's no "order_type", it's a special pair (like final),
        # skip it so we don't re-apply final pair logic
        if isinstance(order, dict) and "order_type" in order:
            if order["order_type"] == "MOVE_XY":
                current_order["x_norm"] = order["order_value"][0]
                current_order["y_norm"] = order["order_value"][1]
            elif order["order_type"] == "MOVE_Z":
                current_order["z_norm"] = order["order_value"][0]
            elif order["order_type"] == "GRIPPER_OPEN":
                current_order["claw_norm"] = 1.0
            elif order["order_type"] == "GRIPPER_CLOSE":
                current_order["claw_norm"] = 0.21

    return current_order


def process_task(task_dir):
    """Process each task directory and inject a final (state+frame) at the end (the very last video frame)."""
    states_file = os.path.join(task_dir, "states.json")
    orders_file = os.path.join(task_dir, "orders.json")

    # Load data
    states = load_json(states_file)
    orders = load_json(orders_file)

    if states is None or orders is None:
        return None

    matching_states = []
    last_matched_index = None
    epsilon = 1e-4

    # 1) Get how many frames are in the main 'Video' folder
    video_dir_path = os.path.join(task_dir, "Video")
    total_frames_in_video = get_total_video_frames(video_dir_path)
    # If there's no video or zero count, default to 0
    final_video_frame_index = max(0, total_frames_in_video - 1)

    # 2) Handle the initial "startup" match
    if len(states) >= 2:
        first_state, second_state = states[0], states[1]

        if (
            abs(first_state['x_norm'] - second_state['x_norm']) < epsilon and
            abs(first_state['y_norm'] - second_state['y_norm']) < epsilon
        ):
            first_addition = first_state
        else:
            first_addition = second_state

        # Standardize starting values to cover sensor noise
        first_addition['x_norm'] = 0.0
        first_addition['y_norm'] = 0.7
        first_addition['z_norm'] = 1.0
        first_addition['claw_norm'] = 0.0

        # Insert as if it matched the first order
        matching_states.append((orders[0], 1, first_addition))

    # 3) Match each order to the states
    for order in orders:
        if order["order_type"] == "MOVE_XY":
            # Ensure no negative XY
            order["order_value"] = [max(0,n) for n in order["order_value"]]

        match_index = find_matching_state(
            order,
            states,
            last_matched_index + 1 if last_matched_index is not None else 0,
        )
        if match_index is not None:
            matching_states.append((order, match_index, states[match_index]))
            last_matched_index = match_index
        else:
            # If we can't match but order is GRIPPER_CLOSE, push to last known state
            if order["order_type"] == "GRIPPER_CLOSE" and states:
                matching_states.append((order, len(states)-1, states[-1]))
            else:
                # If an order can't be matched, break out
                break

    # 4) Compute the "final" order from all matched states
    final_order_dict = compute_final_order_from_matches(matching_states)

    # 5) Inject a special final pair: 
    #    ( final_order_dict, final_video_frame_index, final_order_dict )
    #    This ensures the final frame is the absolute last from the video data.
    #    We use the same dict for 'order' and 'state' (no "order_type").
    matching_states.append((final_order_dict, final_video_frame_index, final_order_dict))

    return matching_states


def post_process_results(results):
    """
    Shift orders one index back and remove the first matched entry from the output.
    """
    if len(results) > 1:
        shifted_results = [
            (results[i][0], results[i - 1][1], results[i - 1][2])
            for i in range(1, len(results))
        ]
        return shifted_results
    return results


def save_results(task_dir, results):
    """Save the results to JSON files in the specified formats, rounding values to 2 decimal places."""
    if not results:
        return

    # Initialize current_order with the first state's values
    current_order = {
        "x_norm": results[0][2].get("x_norm", 0),
        "y_norm": results[0][2].get("y_norm", 0),
        "z_norm": results[0][2].get("z_norm", 0),
        "rotation": results[0][2].get("rotation", 0),
        "claw_norm": results[0][2].get("claw_norm", 0),
    }

    combined_output = []
    states_output = []
    orders_output = []

    for order, index, state in results:
        # Detect if this is the special final pair (no "order_type")
        if isinstance(order, dict) and "order_type" not in order:
            # Overwrite the current_order with the final dict
            current_order["x_norm"]    = order["x_norm"]
            current_order["y_norm"]    = order["y_norm"]
            current_order["z_norm"]    = order["z_norm"]
            current_order["rotation"]  = order["rotation"]
            current_order["claw_norm"] = order["claw_norm"]
        else:
            # Normal path for recognized order_type
            if order["order_type"] == "MOVE_XY":
                current_order["x_norm"] = order["order_value"][0]
                current_order["y_norm"] = order["order_value"][1]
            elif order["order_type"] == "MOVE_Z":
                current_order["z_norm"] = order["order_value"][0]
            elif order["order_type"] == "GRIPPER_OPEN":
                current_order["claw_norm"] = 1.0
            elif order["order_type"] == "GRIPPER_CLOSE":
                current_order["claw_norm"] = 0.21

        # Build combined entry
        combined_entry = {
            "state_index": index,
            "x_norm": round(state["x_norm"], 2),
            "y_norm": round(state["y_norm"], 2),
            "z_norm": round(state["z_norm"], 2),
            "rotation": round(state["rotation"], 2),
            "claw_norm": round(state["claw_norm"], 2),
            "order": {
                "x_norm": round(current_order.get("x_norm", 0), 2),
                "y_norm": round(current_order.get("y_norm", 0), 2),
                "z_norm": round(current_order.get("z_norm", 0), 2),
                "rotation": round(current_order.get("rotation", 0), 2),
                "claw_norm": round(current_order.get("claw_norm", 0), 2),
            }
        }

        # Separate state entry
        state_entry = {
            "state_index": index,
            "x_norm": round(state["x_norm"], 2),
            "y_norm": round(state["y_norm"], 2),
            "z_norm": round(state["z_norm"], 2),
            "rotation": round(state["rotation"], 2),
            "claw_norm": round(state["claw_norm"], 2),
        }

        # Separate order entry
        order_entry = {
            "x_norm": round(current_order.get("x_norm", 0), 2),
            "y_norm": round(current_order.get("y_norm", 0), 2),
            "z_norm": round(current_order.get("z_norm", 0), 2),
            "rotation": round(current_order.get("rotation", 0), 2),
            "claw_norm": round(current_order.get("claw_norm", 0), 2),
        }

        combined_output.append(combined_entry)
        states_output.append(state_entry)
        orders_output.append(order_entry)

    # Save combined JSON
    combined_file = os.path.join(task_dir, "extracted_combined.json")
    with open(combined_file, "w") as f:
        json.dump(combined_output, f, indent=4)

    # Save states JSON
    states_file = os.path.join(task_dir, "extracted_states.json")
    with open(states_file, "w") as f:
        json.dump(states_output, f, indent=4)

    # Save orders JSON
    orders_file = os.path.join(task_dir, "extracted_orders.json")
    with open(orders_file, "w") as f:
        json.dump(orders_output, f, indent=4)


def extract_frames_and_save_video(
    task_dir,
    results,
    video_dir="Video",
    output_video="extracted_states_video.mp4",
    frame_format="jpg",
):
    """Extract frames from the matched state indices and save them to a new video + individual images."""
    video_files = sorted(
        [f for f in os.listdir(os.path.join(task_dir, video_dir)) if f.endswith(".mp4")]
    )
    video_file_paths = [os.path.join(task_dir, video_dir, f) for f in video_files]

    frame_list = []
    total_frames = 0
    frames_per_video = []

    # Directory to save individual frames
    frames_output_dir = os.path.join(task_dir, f"extracted_frames_{video_dir}")
    os.makedirs(frames_output_dir, exist_ok=True)

    # Calculate total number of frames (treat multiple MP4 as concatenated)
    for video_path in video_file_paths:
        cap = cv2.VideoCapture(video_path)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_per_video.append(frames)
        total_frames += frames
        cap.release()

    print(f"[{video_dir}] total frames in video:", total_frames)

    # Determine the frame lag (used only for non-final states)
    if total_frames > 18:
        frame_lag = 1
    elif total_frames > 13:
        frame_lag = 2
    else:
        frame_lag = 3

    # Pull out frames
    for idx, (order, frame_index, _) in enumerate(results):
        # If this is the special final pair (no "order_type"), skip the lag
        if isinstance(order, dict) and ("order_type" not in order):
            adjusted_frame_index = frame_index
        else:
            # Apply the normal lag
            adjusted_frame_index = max(0, frame_index - frame_lag)

        cumulative_frames = 0
        for i, fcount in enumerate(frames_per_video):
            if adjusted_frame_index < cumulative_frames + fcount:
                relative_frame_index = adjusted_frame_index - cumulative_frames
                video_path = video_file_paths[i]

                cap = cv2.VideoCapture(video_path)
                cap.set(cv2.CAP_PROP_POS_FRAMES, relative_frame_index)
                ret, frame = cap.read()
                if ret:
                    frame_list.append(frame)
                    # Save frame as an image
                    frame_filename = os.path.join(
                        frames_output_dir, f"frame_{idx:04d}.{frame_format}"
                    )
                    cv2.imwrite(frame_filename, frame)
                cap.release()
                break
            cumulative_frames += fcount

    # Write extracted frames into a new MP4 video
    if frame_list:
        height, width, _ = frame_list[0].shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_path = os.path.join(task_dir, output_video)
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))

        for frame in frame_list:
            out.write(frame)
        out.release()


def main(root_dir):
    """Main function to iterate over all tasks in numeric subdirectories."""
    base_dir = os.path.join(root_dir, "autograsper", "merged_data")

    # Detect directories named with integers and ensure "task" subdirectory exists
    task_dirs = [
        os.path.join(base_dir, d, "task")
        for d in sorted(
            os.listdir(base_dir), key=lambda x: int(x) if x.isdigit() else float('inf')
        )
        if d.isdigit() and os.path.isdir(os.path.join(base_dir, d, "task"))
    ]

    for task_dir in task_dirs:
        print(f"Processing {task_dir}...")

        # 1) Process the data (includes injecting final-state with last frame)
        matching_states = process_task(task_dir)
        if matching_states is None:
            continue

        # 2) Optionally run post-processing to shift orders
        post_processed_results = post_process_results(matching_states)

        # 3) Save results to extracted_*.json
        save_results(task_dir, post_processed_results)

        # 4) Extract frames and write a video for the "top" camera
        extract_frames_and_save_video(
            task_dir,
            post_processed_results,
            video_dir="Video",
            output_video="extracted_states_video.mp4",
        )

        # 5) Extract frames and write a video for the "bottom" camera
        extract_frames_and_save_video(
            task_dir,
            post_processed_results,
            video_dir="Bottom_Video",
            output_video="extracted_states_bottom_video.mp4",
        )


if __name__ == "__main__":
    root_dir = "."
    main(root_dir)



