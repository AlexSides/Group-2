from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Engine:
    serial_number: str
    horsepower: int
    torque_nm: int
    fuel_type: str
    cylinder_count: int | None = None

    def report_performance(self) -> Dict[str, Any]:
        return {
            "serial_number": self.serial_number,
            "horsepower": self.horsepower,
            "torque_nm": self.torque_nm,
            "fuel_type": self.fuel_type,
            "cylinder_count": self.cylinder_count,
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Engine":
        return cls(**data)
