from Engine import Engine
from Chassis import Chassis
from Car import Car
from Truck import Truck
from Motorcycle import Motorcycle


def build_demo_vehicles():
    car_engine = Engine("ENG-CAR-001", 203, 250, "Gasoline")
    car_chassis = Chassis("unibody", 1450)
    car1 = Car("VIN123", "Toyota Camry", 2022, "Blue", 25000, car_engine, car_chassis, 4, "Sedan")

    truck_engine = Engine("ENG-TRK-001", 400, 650, "Gasoline")
    truck_chassis = Chassis("body-on-frame", 2600)
    truck1 = Truck("VIN456", "Ford F-150", 2021, "Black", 40000, truck_engine, truck_chassis, 2000, "4x4")

    bike_engine = Engine("ENG-BIKE-001", 200, 112, "Gasoline")
    bike_chassis = Chassis("unibody", 200)
    bike1 = Motorcycle("VIN789", "Yamaha R1", 2023, "Red", 18000, bike_engine, bike_chassis, 1000, True)

    return [car1, truck1, bike1]


if __name__ == "__main__":
    for vehicle in build_demo_vehicles():
        print("----- Vehicle -----")
        print(vehicle.get_specs())
        print("Selling Price:", vehicle.calculate_selling_price())
        print()
