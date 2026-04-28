from InventoryManager import InventoryManager
from SampleData import seed_inventory
from LocationManager import LocationManager


def main():
    inventory_manager = InventoryManager()
    location_manager = LocationManager()

    seed_inventory(inventory_manager, location_manager, "images")

    inventory_manager.save_to_json("inventory.json")
    print("Inventory saved to inventory.json")

    inventory_manager.load_from_json("inventory.json")
    print("Inventory loaded from inventory.json")

    inventory_manager.generate_performance_report()


if __name__ == "__main__":
    main()