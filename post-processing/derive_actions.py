import json
import os


# Function to calculate the difference between two states
def calculate_action(current_state, next_state):
    def get_diff(a, b):
        diff = round(b - a, 2)
        return diff if abs(diff) >= 0.001 else 0

    action = {
        "x_norm_diff": get_diff(current_state["x_norm"], next_state["x_norm"]),
        "y_norm_diff": get_diff(current_state["y_norm"], next_state["y_norm"]),
        "z_norm_diff": get_diff(current_state["z_norm"], next_state["z_norm"]),
        "rotation_diff": get_diff(current_state["rotation"], next_state["rotation"]),
        "claw_norm_diff": get_diff(current_state["claw_norm"], next_state["claw_norm"]),
        "z_current_diff": get_diff(
            float(current_state["z_current"]), float(next_state["z_current"])
        ),
        "rotation_current_diff": get_diff(
            float(current_state["rotation_current"]),
            float(next_state["rotation_current"]),
        ),
        "claw_current_diff": get_diff(
            float(current_state["claw_current"]), float(next_state["claw_current"])
        ),
        "time_diff": get_diff(current_state["time"], next_state["time"]),
    }
    return action


def process_states_file(states_file_path):
    with open(states_file_path, "r") as file:
        states = json.load(file)

    actions = []

    for i in range(len(states) - 1):
        current_state = states[i]
        next_state = states[i + 1]
        action = calculate_action(current_state, next_state)
        actions.append(action)

    actions_file_path = os.path.join(os.path.dirname(states_file_path), "actions.json")
    with open(actions_file_path, "w") as file:
        json.dump(actions, file, indent=4)

    print(f"Actions have been written to {actions_file_path}")


def traverse_and_process(root_dir, x_range):
    for x in range(x_range[0], x_range[1] + 1):
        task_dir = os.path.join(
            root_dir, "stack_from_scratch", "recorded_data", str(x), "task"
        )
        states_file_path = os.path.join(task_dir, "states.json")
        if os.path.isfile(states_file_path):
            process_states_file(states_file_path)
        else:
            print(f"File not found: {states_file_path}")


# Define the root directory and range of values for x
root_dir = ""  # Replace with the actual path to the root directory
x_range = (11, 206)  # Replace with the actual range of values for x

# Run the script
traverse_and_process(root_dir, x_range)
