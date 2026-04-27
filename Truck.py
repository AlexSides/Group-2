from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from Vehicle import Vehicle


@dataclass
class Truck(Vehicle):
    payload_capacity_lb: int = 0
    towing_capacity_lb: int = 0
    drive_type: str = "4x2"
    bed_length: str = "Standard"

    def calculate_selling_price(self) -> float:
        bonus = self.payload_capacity_lb * 0.35 + self.towing_capacity_lb * 0.02
        return round(max(self.list_price, self.total_investment() + bonus), 2)

    def subclass_dict(self) -> Dict[str, Any]:
        return {
            "payload_capacity_lb": self.payload_capacity_lb,
            "towing_capacity_lb": self.towing_capacity_lb,
            "drive_type": self.drive_type,
            "bed_length": self.bed_length,
        }

    def subclass_detail_fields(self) -> Dict[str, Any]:
        return {
            "Payload Capacity (lb)": self.payload_capacity_lb,
            "Towing Capacity (lb)": self.towing_capacity_lb,
            "Drive Type": self.drive_type,
            "Bed Length": self.bed_length,
        }
