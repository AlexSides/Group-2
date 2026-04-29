from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .vehicle import Vehicle


@dataclass
class Motorcycle(Vehicle):
    engine_displacement_cc: int = 0
    is_sport_bike: bool = False
    bike_type: str = "Standard"

    def calculate_selling_price(self) -> float:
        multiplier = 1.14 if self.is_sport_bike else 1.09
        return round(max(self.list_price, self.total_investment() * multiplier), 2)

    def subclass_dict(self) -> Dict[str, Any]:
        return {
            "engine_displacement_cc": self.engine_displacement_cc,
            "is_sport_bike": self.is_sport_bike,
            "bike_type": self.bike_type,
        }

    def subclass_detail_fields(self) -> Dict[str, Any]:
        return {
            "Engine (cc)": self.engine_displacement_cc,
            "Sport Bike": self.is_sport_bike,
            "Bike Type": self.bike_type,
        }
