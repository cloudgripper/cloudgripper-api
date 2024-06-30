import json
import os


def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def merge_robot_data(states, orders):
    orders_sorted = sorted(orders, key=lambda x: x["time"])
    merged_data = []

    for state in states:
        state_time = state["time"]
        latest_order = None
        for order in orders_sorted:
            if order["time"] <= state_time:
                latest_order = order
            else:
                break
        merged_entry = state.copy()
        if latest_order:
            merged_entry["latest_order"] = latest_order
        merged_data.append(merged_entry)

    return merged_data


def process_directory(base_path, task_number):
    task_path = os.path.join(base_path, str(task_number), "task")
    states_file = os.path.join(task_path, "states.json")
    orders_file = os.path.join(task_path, "orders.json")
    output_file = os.path.join(task_path, "merged_robot_data.json")

    if os.path.exists(states_file) and os.path.exists(orders_file):
        robot_states = load_json(states_file)
        robot_orders = load_json(orders_file)

        merged_data = merge_robot_data(robot_states, robot_orders)

        save_json(output_file, merged_data)

        print(f"Merged data saved to {output_file}")
    else:
        print(f"states.json or orders.json not found in {task_path}")


if __name__ == "__main__":
    base_path = "stack_from_scratch/recorded_data"
    start_range = 1
    end_range = 36  # Specify the end range as per your requirements

    for task_number in range(start_range, end_range + 1):
        process_directory(base_path, task_number)
