import numpy as np

from models import Server

UNCLETOPIA_AUTO_KICK_LATENCY = 150  # Threshold latency in ms
DEBUG_PRINT_PING_DISTANCE_PAIRS = (
    False  # Set to true to print ping-distance pairs to load into a spreadsheet
)

# Servers automatically kick players with a latency higher than
# UNCLETOPIA_AUTO_KICK_LATENCY (150ms at the time of writing)
# Latency is usually proportional to distance
# Since pinging is expensive, we can instead filter by distance
# Automatically determine the max distance filter based on latency (ping)
# We can do this using linear regression


def estimate_max_distance(servers: list[Server]) -> float | None:
    """
    Estimates the max distance at which latency exceeds the auto-kick threshold (150ms).
    Uses linear regression on (distance, ping) pairs.
    """
    # If any server has a negative ping, return None
    if any(server["ping"] < 0 for server in servers):
        return None
    # Extract valid (distance, ping) pairs
    data = [(server["distance"], server["ping"]) for server in servers]

    if len(data) < 2:  # Not enough data to train a model
        return None

    # Convert to NumPy arrays
    distances, latencies = (
        np.array([d[0] for d in data]),
        np.array([d[1] for d in data]),
    )

    # Perform linear regression: Find `a` and `b` in y = ax + b
    A = np.vstack([distances, np.ones(len(distances))]).T
    a: float
    b: float
    a, b = np.linalg.lstsq(A, latencies, rcond=None)[
        0]  # Least squares solution

    # Solve for distance when latency = UNCLETOPIA_AUTO_KICK_LATENCY
    if a == 0:  # Avoid division by zero
        return None

    estimated_distance = (UNCLETOPIA_AUTO_KICK_LATENCY - b) / a

    if DEBUG_PRINT_PING_DISTANCE_PAIRS:
        try:
            with open("debug_ping_distance_pairs.csv", "w") as f:
                _ = f.write("Ping,Distance\n")
                for d, p in data:
                    _ = f.write(f"{p},{d}\n")
        except Exception as e:
            print(f"Error writing ping-distance pairs: {e}")

    return max(0, estimated_distance)  # Ensure it's not negative
