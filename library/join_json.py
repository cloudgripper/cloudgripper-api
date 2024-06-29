import json


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def save_json(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def find_latest_order(orders, state_time):
    latest_order = None
    for order in orders:
        if order["time"] <= state_time:
            if latest_order is None or order["time"] > latest_order["time"]:
                latest_order = order
    return latest_order


def combine_states_and_orders(states, orders):
    combined_data = []
    for state in states:
        latest_order = find_latest_order(orders, state["time"])
        combined_entry = state.copy()
        if latest_order:
            combined_entry.update(latest_order)
        combined_data.append(combined_entry)
    return combined_data


def main():
    # Load data from files
    robot_states = load_json("states.json")
    robot_orders = load_json("orders.json")

    # Combine states and orders
    combined_data = combine_states_and_orders(robot_states, robot_orders)

    # Save combined data to a new file
    save_json(combined_data, "combined_robot_data.json")

    print("Data combined and saved to 'combined_robot_data.json'")


if __name__ == "__main__":
    main()
