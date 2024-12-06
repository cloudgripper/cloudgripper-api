import json
import os

import cv2
import numpy as np

# Define epsilon for comparison
EPSILON = 1e-2
FRAME_LAG = 1


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
    """Find the first state where the order is successfully carried out, starting from start_idx."""
    order_type = order["order_type"]
    order_value = order.get("order_value", [])

    for idx in range(start_idx, len(states)):

        state = states[idx]

        if order_type == "MOVE_XY":
            if len(order_value) == 2 and (
                compare_values(order_value[0], state["x_norm"])
                and compare_values(order_value[1], state["y_norm"])
            ):
                return idx

        elif order_type == "MOVE_Z":
            if len(order_value) == 1 and compare_values(
                order_value[0], state["z_norm"]
            ):
                return idx

        elif order_type == "GRIPPER_OPEN":
            # Match with claw_norm close to 1.0
            if compare_values(1.0, state["claw_norm"]):
                return idx

        elif order_type == "GRIPPER_CLOSE":
            # Match with claw_norm close to 0.21
            if compare_values(0.24, state["claw_norm"]) or compare_values(0.21, state["claw_norm"]):
                return idx

    return None


def process_task(task_dir):
    """Process each task directory."""
    states_file = os.path.join(task_dir, "states.json")
    orders_file = os.path.join(task_dir, "orders.json")

    # Load data
    states = load_json(states_file)
    orders = load_json(orders_file)

    if states is None or orders is None:
        return None

    matching_states = []
    last_matched_index = None

    # TODO if x/y values of first state is within epsilon of second state, add first state to matching states. Otherwise, add the second state
    # In both cases, their matching order should be the first order

    epsilon = 1e-4 

    if len(states) >= 2:
        first_state, second_state = states[0], states[1]
        
        if (
            abs(first_state['x_norm'] - second_state['x_norm']) < epsilon and
            abs(first_state['y_norm'] - second_state['y_norm']) < epsilon
        ):
            matching_states.append((orders[0], 0, first_state))
        else:
            matching_states.append((orders[0], 1, second_state))

    for order in orders:
        match_index = find_matching_state(
            order,
            states,
            last_matched_index + 1 if last_matched_index is not None else 0,
        )
        if match_index is not None:
            #  if last_matched_index is not None and match_index == last_matched_index + 1:
                # Skip this match as it is consecutive to the last one
                # continue
            matching_states.append(
                (order, match_index, states[match_index])
            )  # Store order, index, and state
            last_matched_index = match_index
        else:
            break  # If an order can't be matched, stop further processing

    return matching_states


def post_process_results(results):
    """Shift orders one index back and remove the first order and last state."""
    if len(results) > 1:
        # Shift orders back by one index
        shifted_results = [
            (results[i][0], results[i - 1][1], results[i - 1][2])
            for i in range(1, len(results))
        ]

        # Remove the first order and last state
        #shifted_results.pop()  # Remove the last element (last state)
        return shifted_results
    return results  # If results length is 1 or less, return as is



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
        # Update current_order with order values where applicable
        if order["order_type"] == "MOVE_XY":
            current_order["x_norm"] = order["order_value"][0]
            current_order["y_norm"] = order["order_value"][1]
        elif order["order_type"] == "MOVE_Z":
            current_order["z_norm"] = order["order_value"][0]
        elif order["order_type"] == "GRIPPER_OPEN":
            current_order["claw_norm"] = 1.0
        elif order["order_type"] == "GRIPPER_CLOSE":
            current_order["claw_norm"] = 0.21

        # Create the combined entry with both the state and the updated order
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

        # Create separate state and order entries
        state_entry = {
            "state_index": index,
            "x_norm": round(state["x_norm"], 2),
            "y_norm": round(state["y_norm"], 2),
            "z_norm": round(state["z_norm"], 2),
            "rotation": round(state["rotation"], 2),
            "claw_norm": round(state["claw_norm"], 2),
        }

        order_entry = {
            "x_norm": round(current_order.get("x_norm", 0), 2),
            "y_norm": round(current_order.get("y_norm", 0), 2),
            "z_norm": round(current_order.get("z_norm", 0), 2),
            "rotation": round(current_order.get("rotation", 0), 2),
            "claw_norm": round(current_order.get("claw_norm", 0), 2),
        }

        # Add entries to outputs
        combined_output.append(combined_entry)
        states_output.append(state_entry)
        orders_output.append(order_entry)

    # Save the combined data
    combined_file = os.path.join(task_dir, "extracted_combined.json")
    with open(combined_file, "w") as f:
        json.dump(combined_output, f, indent=4)

    # Save the states data
    states_file = os.path.join(task_dir, "extracted_states.json")
    with open(states_file, "w") as f:
        json.dump(states_output, f, indent=4)

    # Save the orders data
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
    """Extract the frames corresponding to the states and save them as a new video and individual images."""
    video_files = sorted(
        [f for f in os.listdir(os.path.join(task_dir, video_dir)) if f.endswith(".mp4")]
    )
    video_file_paths = [os.path.join(task_dir, video_dir, f) for f in video_files]

    cap = None
    frame_list = []

    total_frames = 0
    frames_per_video = []

    # Directory to save individual frames
    frames_output_dir = os.path.join(task_dir, f"extracted_frames_{video_dir}")
    os.makedirs(frames_output_dir, exist_ok=True)

    # Calculate the total number of frames per video and overall total frames
    for video_path in video_file_paths:
        cap = cv2.VideoCapture(video_path)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_per_video.append(frames)
        total_frames += frames
        cap.release()
    
    print("frames in video:", total_frames)

    # Determine the frame from which each state should be extracted
    for idx, (_, frame_index, _) in enumerate(results):
        # Adjust frame index to be x frames behind
        adjusted_frame_index = max(0, frame_index - FRAME_LAG)

        cumulative_frames = 0
        for i, frames in enumerate(frames_per_video):
            if adjusted_frame_index < cumulative_frames + frames:
                relative_frame_index = adjusted_frame_index - cumulative_frames
                video_path = video_file_paths[i]

                cap = cv2.VideoCapture(video_path)
                cap.set(cv2.CAP_PROP_POS_FRAMES, relative_frame_index)
                ret, frame = cap.read()
                if ret:
                    frame_list.append(frame)
                    # Save individual frames
                    frame_filename = os.path.join(
                        frames_output_dir, f"frame_{idx:04d}.{frame_format}"
                    )
                    cv2.imwrite(frame_filename, frame)
                cap.release()
                break
            cumulative_frames += frames

    # Save the frames into a new video
    if frame_list:
        height, width, _ = frame_list[0].shape
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        output_path = os.path.join(task_dir, output_video)
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))

        for frame in frame_list:
            out.write(frame)

        out.release()


def main(root_dir):
    """Main function to iterate over all tasks in detected directories."""
    base_dir = os.path.join(root_dir, "autograsper", "recorded_data")

    # Detect directories named with integers and ensure task subdirectory exists
    task_dirs = [
        os.path.join(base_dir, d, "task")
        for d in sorted(os.listdir(base_dir), key=lambda x: int(x) if x.isdigit() else float('inf'))
        if d.isdigit() and os.path.isdir(os.path.join(base_dir, d, "task"))
    ]

    # Process each detected task directory
    for task_dir in task_dirs:
        print(f"Processing {task_dir}...")

        matching_states = process_task(task_dir)
        if matching_states is None:
            continue
        # post_processed_results = matching_states # post_process_results(matching_states)
        post_processed_results = post_process_results(matching_states)
        save_results(task_dir, post_processed_results)

        # Extract frames and save video for both Video and Bottom_Video directories
        extract_frames_and_save_video(
            task_dir,
            post_processed_results,
            video_dir="Video",
            output_video="extracted_states_video.mp4",
        )
        extract_frames_and_save_video(
            task_dir,
            post_processed_results,
            video_dir="Bottom_Video",
            output_video="extracted_states_bottom_video.mp4",
        )


if __name__ == "__main__":
    root_dir = "."
    main(root_dir)
