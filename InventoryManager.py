class InventoryManager:
    """Manages the inventory of vehicles."""
    def __init__(self):
        self.inventory = {}  # Store vehicles with VIN as key and vehicle object as value

    def add_vehicle(self, vehicle_object):
        # Only add the vehicle if it has a 'vin' attribute
        if hasattr(vehicle_object, "vin"):
            self.inventory[vehicle_object.vin] = vehicle_object
        else:
            raise AttributeError("Vehicle object must have a 'vin' attribute.")

    def remove_vehicle(self, vin):
        # Remove the vehicle only if the VIN exists in the inventory
        if vin in self.inventory:
            del self.inventory[vin]
            print(f"Vehicle with VIN {vin} removed from inventory.")
        else:
            print(f"Vehicle with VIN {vin} not found.")

    def get_vehicle(self, vin):
        # Return the vehicle object if found, otherwise return None
        return self.inventory.get(vin, None)

    def search_by_model(self, model_name):
        results = []

        # Check every vehicle in the inventory for a matching model name
        for vehicle in self.inventory.values():
            # hasattr check ensures we only try to access 'model' if it exists, preventing errors
            if hasattr(vehicle, "model") and vehicle.model.lower() == model_name.lower():
                results.append(vehicle)

        return results