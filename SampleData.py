from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from Car import Car
from Chassis import Chassis
from Engine import Engine
from InventoryManager import InventoryManager
from LocationManager import Location, LocationManager
from Motorcycle import Motorcycle
from Truck import Truck

STATUSES = [
    "Ready for Sale",
    "Inspection",
    "Repair Needed",
    "Detailing",
    "Photo Pending",
    "Needs Info Added",
    "Reserved",
    "Sold",
]


def ensure_locations(location_manager: LocationManager) -> None:
    for location in [
        Location("AUS", "Austin Lot", "Austin", "100 Main St", "Elena Cruz", 80, notes="Sedans and premium motorcycles."),
        Location("DAL", "Dallas Lot", "Dallas", "220 Market Ave", "Marcus Hill", 70, notes="Truck-heavy, higher throughput location."),
        Location("HOU", "Houston Lot", "Houston", "54 Bayou Dr", "Tanya Brooks", 60, notes="Utility inventory and aged-unit cleanup."),
    ]:
        location_manager.add_location(location)


def _days(days_ago: int) -> str:
    return (date.today() - timedelta(days=days_ago)).isoformat()


def _engine(serial: str, horsepower: int, torque: int, fuel: str = "Gasoline") -> Engine:
    return Engine(serial, horsepower, torque, fuel)


def _photo(paths: dict[str, list[str]], key: str) -> list[str]:
    return list(paths.get(key, []))


def build_seed_vehicles(images_dir: str | Path):
    images = Path(images_dir)
    photo_sets = {
        "car": [str(images / "sedan.jpg")],
        "truck": [str(images / "truck.jpg")],
        "truck_alt": [p for p in [str(images / "ford_f150_pd.jpg"), str(images / "truck.jpg")] if Path(p).exists()],
        "moto": [str(images / "motorcycle.jpg")],
    }

    vehicles = []
    car_models = [
        ("Toyota", "Camry", "SE", "Blue"), ("Honda", "Accord", "Sport", "White"),
        ("Toyota", "Corolla", "LE", "Silver"), ("Honda", "Civic", "EX", "Black"),
        ("Nissan", "Altima", "SV", "Gray"), ("Jeep", "Wrangler", "Sport", "Green"),
        ("Chevrolet", "Tahoe", "LT", "Pearl White"), ("Hyundai", "Sonata", "SEL", "Red"),
        ("Toyota", "Highlander", "XLE", "Black"), ("Subaru", "Forester", "Premium", "Gray"),
        ("Mazda", "CX-5", "Touring", "Blue"), ("Kia", "Sorento", "EX", "Silver"),
    ]
    truck_models = [
        ("Ford", "F-150", "XLT", "Black"), ("Chevrolet", "Silverado", "LT", "Gray"),
        ("Ram", "1500", "Big Horn", "Blue"), ("Toyota", "Tacoma", "TRD Sport", "Orange"),
        ("GMC", "Sierra 1500", "SLE", "White"), ("Ford", "Ranger", "Lariat", "Gray"),
        ("Nissan", "Frontier", "PRO-4X", "Red"), ("Toyota", "Tundra", "Limited", "White"),
        ("Chevrolet", "Colorado", "Z71", "Sand"), ("GMC", "Canyon", "AT4", "Bronze"),
        ("Ford", "F-150", "Lariat", "Silver"), ("Chevrolet", "Silverado", "RST", "Black"),
    ]
    moto_models = [
        ("Yamaha", "R1", "Base", "Red", True), ("Kawasaki", "Ninja 650", "ABS", "Green", False),
        ("Harley-Davidson", "Street Bob", "114", "Black", False), ("Ducati", "Monster", "937", "Red", True),
        ("BMW", "R 1250 GS", "Adventure", "White", False), ("Honda", "CBR650R", "ABS", "Black", True),
        ("Yamaha", "MT-07", "Base", "Gray", False), ("Suzuki", "GSX-R750", "Base", "Blue", True),
        ("Harley-Davidson", "Iron 883", "Base", "Matte Black", False), ("KTM", "390 Duke", "Base", "Orange", False),
        ("Triumph", "Street Triple", "R", "Silver", True), ("Kawasaki", "Versys 650", "LT", "Green", False),
    ]

    locations = ["AUS", "DAL", "HOU"] * 12
    car_statuses = ["Ready for Sale", "Photo Pending", "Ready for Sale", "Needs Info Added", "Detailing", "Ready for Sale", "Reserved", "Ready for Sale", "Inspection", "Ready for Sale", "Ready for Sale", "Needs Info Added"]
    truck_statuses = ["Ready for Sale", "Inspection", "Ready for Sale", "Needs Info Added", "Repair Needed", "Ready for Sale", "Detailing", "Listed".replace("Listed", "Needs Info Added"), "Photo Pending", "Ready for Sale", "Ready for Sale", "Reserved"]
    moto_statuses = ["Needs Info Added", "Ready for Sale", "Ready for Sale", "Ready for Sale", "Inspection", "Ready for Sale", "Photo Pending", "Detailing", "Ready for Sale", "Ready for Sale", "Needs Info Added", "Ready for Sale"]

    stock = 1
    for i, (make, model, trim, color) in enumerate(car_models):
        loc = locations[i]
        vehicles.append(
            Car(
                stock_id=f"CAR-{stock:03d}", vin=f"VIN-CAR-{stock:03d}", make=make, model=model, trim=trim,
                year=2020 + (i % 4), color=color, mileage=12000 + i * 3100,
                acquisition_cost=16000 + i * 1200, reconditioning_cost=700 + (i % 4) * 250,
                list_price=21000 + i * 1800, estimated_market_value=21300 + i * 1800 + ((i % 3) - 1) * 350,
                location_id=loc, status=car_statuses[i],
                engine=_engine(f"ENG-{stock:03d}", 175 + (i % 4) * 12, 220 + (i % 5) * 18),
                chassis=Chassis("unibody", 1450 + i * 12, "Steel"),
                num_doors=4, body_type="SUV" if model in {"Wrangler", "Tahoe", "Highlander", "Forester", "CX-5", "Sorento"} else "Sedan",
                drivetrain="AWD" if model in {"Wrangler", "Highlander", "Forester", "CX-5", "Sorento"} else "FWD",
                date_acquired=_days(12 + i * 7), depreciation_value=260 + i * 70,
                notes=f"{make} {model} seeded demo vehicle for inventory testing.", photo_paths=_photo(photo_sets, "car"),
            )
        )
        stock += 1

    for i, (make, model, trim, color) in enumerate(truck_models):
        loc = locations[12 + i]
        vehicles.append(
            Truck(
                stock_id=f"TRK-{stock:03d}", vin=f"VIN-TRK-{stock:03d}", make=make, model=model, trim=trim,
                year=2021 + (i % 3), color=color, mileage=9000 + i * 2700,
                acquisition_cost=28500 + i * 1500, reconditioning_cost=1000 + (i % 4) * 320,
                list_price=36000 + i * 2200, estimated_market_value=36400 + i * 2200 + ((i % 3) - 1) * 500,
                location_id=loc, status=truck_statuses[i],
                engine=_engine(f"ENG-{stock:03d}", 285 + (i % 5) * 22, 380 + (i % 5) * 38),
                chassis=Chassis("body-on-frame", 2200 + i * 20, "Steel"),
                payload_capacity_lb=1450 + i * 35, towing_capacity_lb=6800 + i * 390,
                drive_type="4x4" if i % 2 == 0 else "4x2", bed_length="Short" if i % 3 == 0 else "Standard",
                date_acquired=_days(10 + i * 6), depreciation_value=340 + i * 90,
                notes=f"{make} {model} seeded demo truck for lot analysis.", photo_paths=_photo(photo_sets, "truck_alt" if i % 2 == 0 else "truck"),
            )
        )
        stock += 1

    for i, (make, model, trim, color, sport) in enumerate(moto_models):
        loc = locations[24 + i]
        vehicles.append(
            Motorcycle(
                stock_id=f"MOTO-{stock:03d}", vin=f"VIN-MOTO-{stock:03d}", make=make, model=model, trim=trim,
                year=2021 + (i % 3), color=color, mileage=1800 + i * 950,
                acquisition_cost=4800 + i * 700, reconditioning_cost=250 + (i % 3) * 140,
                list_price=6900 + i * 950, estimated_market_value=7100 + i * 950 + ((i % 3) - 1) * 180,
                location_id=loc, status=moto_statuses[i],
                engine=_engine(f"ENG-{stock:03d}", 45 + (i % 5) * 18, 40 + (i % 4) * 14),
                chassis=Chassis("trellis" if sport else "steel frame", 190 + i * 3, "Aluminum" if sport else "Steel"),
                engine_displacement_cc=390 + i * 55, is_sport_bike=sport,
                bike_type="Sport" if sport else "Cruiser" if "Harley" in make else "Touring",
                date_acquired=_days(8 + i * 8), depreciation_value=120 + i * 45,
                notes=f"{make} {model} seeded demo motorcycle for lot analysis.", photo_paths=_photo(photo_sets, "moto"),
            )
        )
        stock += 1

    return vehicles


def seed_inventory(inventory_manager: InventoryManager, location_manager: LocationManager, images_dir: str | Path):
    if inventory_manager.all_vehicles():
        return inventory_manager.all_vehicles()
    ensure_locations(location_manager)
    vehicles = build_seed_vehicles(images_dir)
    for vehicle in vehicles:
        inventory_manager.add_vehicle(vehicle)
    return vehicles
