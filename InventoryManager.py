from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Iterable, List

from Car import Car
from Truck import Truck
from Motorcycle import Motorcycle
from Vehicle import Vehicle
from Engine import Engine
from Chassis import Chassis


STATUS_READY = "Ready for Sale"


class InventoryManager:
    def __init__(self) -> None:
        self.inventory: Dict[str, Vehicle] = {}

    def add_vehicle(self, vehicle: Vehicle) -> None:
        self.inventory[vehicle.vin] = vehicle

    def remove_vehicle(self, vin: str) -> None:
        self.inventory.pop(vin, None)

    def get_vehicle(self, vin: str) -> Vehicle | None:
        return self.inventory.get(vin)

    def all_vehicles(self) -> list[Vehicle]:
        return list(self.inventory.values())

    def filter_by_location(self, location_id: str) -> list[Vehicle]:
        return [v for v in self.inventory.values() if v.location_id == location_id]

    def filter_by_status(self, status: str) -> list[Vehicle]:
        return [v for v in self.inventory.values() if v.status == status]

    def filter_by_type(self, vehicle_type: str) -> list[Vehicle]:
        return [v for v in self.inventory.values() if v.vehicle_type == vehicle_type]

    def location_status_breakdown(self, location_id: str) -> Dict[str, int]:
        return self.vehicle_counts_by_status(self.filter_by_location(location_id))

    def location_type_breakdown(self, location_id: str) -> Dict[str, int]:
        return self.vehicle_counts_by_type(self.filter_by_location(location_id))

    def action_item_vehicles(self, limit: int = 5, location_id: str | None = None) -> list[Vehicle]:
        vehicles = self.filter_by_location(location_id) if location_id else self.all_vehicles()

        def score(vehicle: Vehicle) -> int:
            total = 0
            if vehicle.days_on_lot() >= 90:
                total += 5
            elif vehicle.days_on_lot() >= 60:
                total += 3
            if vehicle.status in {"Inspection", "Repair Needed", "Detailing", "Photo Pending", "Needs Info Added"}:
                total += 3
            if not vehicle.photo_paths:
                total += 2
            if vehicle.market_gap() < 0:
                total += 1
            return total

        ranked = sorted(vehicles, key=lambda v: (score(v), v.days_on_lot(), -v.expected_margin()), reverse=True)
        return [vehicle for vehicle in ranked if score(vehicle) > 0][:limit]

    def search(self, text: str) -> list[Vehicle]:
        needle = text.strip().lower()
        if not needle:
            return self.all_vehicles()
        fields = ("stock_id", "vin", "make", "model", "trim", "location_id", "status")
        results: list[Vehicle] = []
        for vehicle in self.inventory.values():
            haystack = " ".join(str(getattr(vehicle, field, "")).lower() for field in fields)
            if needle in haystack:
                results.append(vehicle)
        return results

    def vehicle_counts_by_type(self, vehicles: Iterable[Vehicle] | None = None) -> Dict[str, int]:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        counts: Dict[str, int] = {}
        for vehicle in records:
            counts[vehicle.vehicle_type] = counts.get(vehicle.vehicle_type, 0) + 1
        return counts

    def vehicle_counts_by_status(self, vehicles: Iterable[Vehicle] | None = None) -> Dict[str, int]:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        counts: Dict[str, int] = {}
        for vehicle in records:
            counts[vehicle.status] = counts.get(vehicle.status, 0) + 1
        return counts

    def total_units(self, vehicles: Iterable[Vehicle] | None = None) -> int:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return len(records)

    def total_acquisition_cost(self, vehicles: Iterable[Vehicle] | None = None) -> float:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return sum(v.acquisition_cost for v in records)

    def total_reconditioning_cost(self, vehicles: Iterable[Vehicle] | None = None) -> float:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return sum(v.reconditioning_cost for v in records)

    def total_investment(self, vehicles: Iterable[Vehicle] | None = None) -> float:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return sum(v.total_investment() for v in records)

    def total_list_value(self, vehicles: Iterable[Vehicle] | None = None) -> float:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return sum(v.list_price for v in records)

    def total_market_value(self, vehicles: Iterable[Vehicle] | None = None) -> float:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return sum(v.estimated_market_value for v in records)

    def expected_gross_profit(self, vehicles: Iterable[Vehicle] | None = None) -> float:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return sum(v.expected_margin() for v in records)

    def total_depreciation_exposure(self, vehicles: Iterable[Vehicle] | None = None) -> float:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return sum(v.depreciation_value for v in records)

    def average_days_on_lot(self, vehicles: Iterable[Vehicle] | None = None) -> float:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        if not records:
            return 0.0
        return sum(v.days_on_lot() for v in records) / len(records)

    def aged_units(self, min_days: int = 60, vehicles: Iterable[Vehicle] | None = None) -> list[Vehicle]:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return [v for v in records if v.days_on_lot() >= min_days]

    def ready_for_sale_percent(self, vehicles: Iterable[Vehicle] | None = None) -> float:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        if not records:
            return 0.0
        ready = sum(1 for v in records if v.status == STATUS_READY)
        return (ready / len(records)) * 100

    def photo_missing_count(self, vehicles: Iterable[Vehicle] | None = None) -> int:
        records = list(vehicles) if vehicles is not None else self.all_vehicles()
        return sum(1 for v in records if not v.photo_paths)

    def location_metrics(self, location_id: str) -> Dict[str, Any]:
        vehicles = self.filter_by_location(location_id)
        return {
            "vehicle_count": self.total_units(vehicles),
            "location_list_value": self.total_list_value(vehicles),
            "location_market_value": self.total_market_value(vehicles),
            "location_expected_margin": self.expected_gross_profit(vehicles),
            "avg_days_on_lot": self.average_days_on_lot(vehicles),
            "ready_units": round(self.ready_for_sale_percent(vehicles) * self.total_units(vehicles) / 100),
            "aged_units": len(self.aged_units(60, vehicles)),
            "photo_missing_count": self.photo_missing_count(vehicles),
        }

    def company_metrics(self) -> Dict[str, Any]:
        vehicles = self.all_vehicles()
        return {
            "total_units": self.total_units(vehicles),
            "total_acquisition_cost": self.total_acquisition_cost(vehicles),
            "total_reconditioning_cost": self.total_reconditioning_cost(vehicles),
            "total_investment": self.total_investment(vehicles),
            "total_list_value": self.total_list_value(vehicles),
            "total_market_value": self.total_market_value(vehicles),
            "expected_gross_profit": self.expected_gross_profit(vehicles),
            "average_days_on_lot": self.average_days_on_lot(vehicles),
            "aged_units_60": len(self.aged_units(60, vehicles)),
            "ready_for_sale_percent": self.ready_for_sale_percent(vehicles),
            "photo_missing_count": self.photo_missing_count(vehicles),
            "total_depreciation_exposure": self.total_depreciation_exposure(vehicles),
        }

    def transfer_vehicle(self, vin: str, new_location_id: str) -> bool:
        vehicle = self.get_vehicle(vin)
        if not vehicle:
            return False
        vehicle.location_id = new_location_id
        return True

    def to_list(self) -> List[Dict[str, Any]]:
        return [vehicle.base_dict() for vehicle in self.all_vehicles()]

    def save_to_json(self, filepath: str | Path) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(self.to_list(), handle, indent=2)

    def load_from_json(self, filepath: str | Path) -> None:
        path = Path(filepath)
        if not path.exists():
            return
        with path.open("r", encoding="utf-8") as handle:
            records = json.load(handle)
        self.inventory = {}
        for record in records:
            vehicle = self._vehicle_from_dict(record)
            self.add_vehicle(vehicle)

    def _vehicle_from_dict(self, record: Dict[str, Any]) -> Vehicle:
        class_name = record.pop("class_name")
        engine = Engine.from_dict(record.pop("engine"))
        chassis = Chassis.from_dict(record.pop("chassis"))
        record["engine"] = engine
        record["chassis"] = chassis
        mapping = {
            "Car": Car,
            "Truck": Truck,
            "Motorcycle": Motorcycle,
        }
        cls = mapping[class_name]
        return cls(**record)
