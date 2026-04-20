#Component Classes - Chassis
class Chassis:
    """Represents the chassis component of a vehicle."""
    def __init__(self,chassis_type, weight_kg):
        self.chassis_type = chassis_type
        self.weight_kg = weight_kg

    def get_load_rating(self): # Load rating is determined by chassis type and weight
        """Determines the load rating based on chassis type and weight."""
        if self.chassis_type.lower() == "body-on-frame":
            if self.weight_kg < 2000:
                return "Medium Load"
            else: 
                return "Heavy Load"
        elif self.chassis_type.lower() == "unibody":
            if self.weight_kg < 1500:
                return "Light Load"
            else:
                return "Medium Load"
        else: # Fallback for unknown chassis types
            return "Unknown Load Rating"
