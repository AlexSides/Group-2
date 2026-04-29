from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Chassis:
    chassis_type: str
    weight_kg: float
    material: str | None = None

    def get_load_rating(self) -> str:
        kind = self.chassis_type.strip().lower()
        if kind == "body-on-frame":
            return "Heavy Load" if self.weight_kg >= 2000 else "Medium Load"
        if kind == "unibody":
            return "Medium Load" if self.weight_kg >= 1500 else "Light Load"
        return "Unknown Load Rating"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chassis":
        return cls(**data)
