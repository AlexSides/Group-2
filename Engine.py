#Component Classes - Engine
class Engine:
    """Represents the engine component of a vehicle."""
    def __init__(self, serial_number, horsepower, torque_nm, fuel_type):
        """Initializes the Engine with its specifications."""
        self.serial_number = serial_number
        self.horsepower = horsepower
        self.torque_nm = torque_nm
        self.fuel_type = fuel_type

    def report_performance(self):
        """Returns a dictionary with the engine's performance metrics."""   
        return{"serial_number": self.serial_number, 
               "horsepower": self.horsepower, 
               "torque_nm": self.torque_nm, 
               "fuel_type": self.fuel_type
               }