from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, Iterable


@dataclass
class Location:
    location_id: str
    name: str
    city: str
    address: str
    manager_name: str
    capacity: int
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Location":
        return cls(**data)


class LocationManager:
    def __init__(self) -> None:
        self.locations: Dict[str, Location] = {}

    def add_location(self, location: Location) -> None:
        self.locations[location.location_id] = location

    def remove_location(self, location_id: str) -> None:
        self.locations.pop(location_id, None)

    def get_location(self, location_id: str) -> Location | None:
        return self.locations.get(location_id)

    def all_locations(self) -> list[Location]:
        return list(self.locations.values())

    def to_list(self) -> list[Dict[str, Any]]:
        return [location.to_dict() for location in self.all_locations()]

    def load_list(self, records: Iterable[Dict[str, Any]]) -> None:
        self.locations = {}
        for record in records:
            self.add_location(Location.from_dict(record))
