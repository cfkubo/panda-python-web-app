import random
import math


def interpolate_points(start, end, steps):
    """Interpolate points between start and end with a given number of steps."""
    latitudes = [start[0] + i * (end[0] - start[0]) / (steps - 1) for i in range(steps)]
    longitudes = [start[1] + i * (end[1] - start[1]) / (steps - 1) for i in range(steps)]
    return list(zip(latitudes, longitudes))

def simulate_movement(start, end, steps):
    """Simulate car movement from start to end."""
    points = interpolate_points(start, end, steps)
    # Add a bit of randomness to simulate real-world movement
    noisy_points = [(lat + random.uniform(-0.001, 0.001), lon + random.uniform(-0.001, 0.001)) for lat, lon in points]
    return noisy_points

# Define start and end coordinates
start_coordinate = (40.7128, -74.0060)  # Example: New York City
end_coordinate = (34.0522, -118.2437)    # Example: Los Angeles

# Number of steps or intermediate points
num_steps = 10

# Generate and print the simulated GPS coordinates
path = simulate_movement(start_coordinate, end_coordinate, num_steps)

print("Simulated GPS Coordinates:")
for idx, (latitude, longitude) in enumerate(path):
    print(f"Step {idx + 1}: Latitude = {latitude}, Longitude = {longitude}")
