from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .vehicle import Vehicle


@dataclass
class Car(Vehicle):
    num_doors: int = 4
    body_type: str = "Sedan"
    drivetrain: str = "FWD"

    def calculate_selling_price(self) -> float:
        return round(max(self.list_price, self.total_investment() * 1.12), 2)

    def subclass_dict(self) -> Dict[str, Any]:
        return {
            "num_doors": self.num_doors,
            "body_type": self.body_type,
            "drivetrain": self.drivetrain,
        }

    def subclass_detail_fields(self) -> Dict[str, Any]:
        return {
            "Doors": self.num_doors,
            "Body Type": self.body_type,
            "Drivetrain": self.drivetrain,
        }
