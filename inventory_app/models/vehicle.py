from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List

from .engine import Engine
from .chassis import Chassis


@dataclass
class Vehicle(ABC):
    stock_id: str
    vin: str
    make: str
    model: str
    year: int
    color: str
    mileage: int
    acquisition_cost: float
    reconditioning_cost: float
    list_price: float
    estimated_market_value: float
    location_id: str
    status: str
    engine: Engine
    chassis: Chassis
    trim: str = ""
    notes: str = ""
    photo_paths: List[str] = field(default_factory=list)
    date_acquired: str = field(default_factory=lambda: date.today().isoformat())
    depreciation_value: float = 0.0

    @property
    def vehicle_type(self) -> str:
        return self.__class__.__name__

    @property
    def primary_photo(self) -> str:
        return self.photo_paths[0] if self.photo_paths else ""

    def add_photo(self, path: str) -> None:
        if path and path not in self.photo_paths:
            self.photo_paths.append(path)

    def total_investment(self) -> float:
        return float(self.acquisition_cost + self.reconditioning_cost)

    def expected_margin(self) -> float:
        return float(self.list_price - self.total_investment())

    def market_gap(self) -> float:
        return float(self.estimated_market_value - self.list_price)

    def days_on_lot(self) -> int:
        try:
            acquired = datetime.fromisoformat(self.date_acquired).date()
        except ValueError:
            return 0
        return max((date.today() - acquired).days, 0)

    def age_bucket(self) -> str:
        days = self.days_on_lot()
        if days <= 30:
            return "0-30"
        if days <= 60:
            return "31-60"
        if days <= 90:
            return "61-90"
        return "90+"

    def base_dict(self) -> Dict[str, Any]:
        return {
            "class_name": self.__class__.__name__,
            "stock_id": self.stock_id,
            "vin": self.vin,
            "make": self.make,
            "model": self.model,
            "trim": self.trim,
            "year": self.year,
            "color": self.color,
            "mileage": self.mileage,
            "acquisition_cost": self.acquisition_cost,
            "reconditioning_cost": self.reconditioning_cost,
            "list_price": self.list_price,
            "estimated_market_value": self.estimated_market_value,
            "location_id": self.location_id,
            "status": self.status,
            "notes": self.notes,
            "photo_paths": list(self.photo_paths),
            "date_acquired": self.date_acquired,
            "depreciation_value": self.depreciation_value,
            "engine": self.engine.to_dict(),
            "chassis": self.chassis.to_dict(),
            **self.subclass_dict(),
        }

    def table_row(self) -> Dict[str, Any]:
        return {
            "Photo": self.primary_photo,
            "Stock ID": self.stock_id,
            "VIN": self.vin,
            "Year": self.year,
            "Make": self.make,
            "Model": self.model,
            "Type": self.vehicle_type,
            "Mileage": self.mileage,
            "Total Investment": self.total_investment(),
            "List Price": self.list_price,
            "Market Value": self.estimated_market_value,
            "Expected Margin": self.expected_margin(),
            "Days on Lot": self.days_on_lot(),
            "Status": self.status,
            "Location": self.location_id,
        }

    def detail_sections(self) -> Dict[str, Dict[str, Any]]:
        return {
            "Basic Info": {
                "Stock ID": self.stock_id,
                "VIN": self.vin,
                "Make": self.make,
                "Model": self.model,
                "Trim": self.trim or "-",
                "Year": self.year,
                "Type": self.vehicle_type,
                "Color": self.color,
                "Mileage": f"{self.mileage:,}",
                "Location": self.location_id,
                "Status": self.status,
            },
            "Pricing": {
                "Acquisition Cost": self.acquisition_cost,
                "Reconditioning Cost": self.reconditioning_cost,
                "Total Investment": self.total_investment(),
                "List Price": self.list_price,
                "Estimated Market Value": self.estimated_market_value,
                "Expected Margin": self.expected_margin(),
                "Depreciation Value": self.depreciation_value,
                "Days on Lot": self.days_on_lot(),
            },
            "Components": {
                "Engine Serial": self.engine.serial_number,
                "Horsepower": self.engine.horsepower,
                "Torque (Nm)": self.engine.torque_nm,
                "Fuel Type": self.engine.fuel_type,
                "Chassis Type": self.chassis.chassis_type,
                "Chassis Weight (kg)": self.chassis.weight_kg,
                "Load Rating": self.chassis.get_load_rating(),
            },
            "Extra": self.subclass_detail_fields(),
        }

    @abstractmethod
    def calculate_selling_price(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def subclass_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def subclass_detail_fields(self) -> Dict[str, Any]:
        raise NotImplementedError
