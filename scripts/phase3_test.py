import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inventory_app.models.location_manager import LocationManager
from inventory_app.services.inventory_manager import InventoryManager
from inventory_app.services.sample_data import seed_inventory


def main():
    inventory_manager = InventoryManager()
    location_manager = LocationManager()
    inventory_path = PROJECT_ROOT / "inventory.json"
    images_path = PROJECT_ROOT / "images"

    seed_inventory(inventory_manager, location_manager, images_path)

    inventory_manager.save_to_json(inventory_path)
    print("Inventory saved to inventory.json")

    inventory_manager.load_from_json(inventory_path)
    print("Inventory loaded from inventory.json")

    inventory_manager.generate_performance_report()


if __name__ == "__main__":
    main()
