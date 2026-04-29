import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inventory_app.services.sample_data import build_seed_vehicles


def build_demo_vehicles():
    vehicles = build_seed_vehicles(PROJECT_ROOT / "images")
    return vehicles[:3]


if __name__ == "__main__":
    for vehicle in build_demo_vehicles():
        print("----- Vehicle -----")
        print(f"{vehicle.stock_id}: {vehicle.year} {vehicle.make} {vehicle.model}")
        print("Type:", vehicle.vehicle_type)
        print("Expected Margin:", vehicle.expected_margin())
        print("Selling Price:", vehicle.calculate_selling_price())
        print()
