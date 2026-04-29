from __future__ import annotations

from typing import Any, Dict

from .inventory_manager import InventoryManager
from ..models.location_manager import LocationManager
from ..models.vehicle import Vehicle

STATUS_ORDER = [
    "Ready for Sale",
    "Needs Info Added",
    "Photo Pending",
    "Inspection",
    "Detailing",
    "Repair Needed",
    "Reserved",
    "Sold",
    "Acquired",
]

AGE_BUCKET_ORDER = ["0-30", "31-60", "61-90", "90+"]

STATUS_COLORS = {
    "Ready for Sale": "#22C55E",
    "Needs Info Added": "#4F46E5",
    "Photo Pending": "#F59E0B",
    "Inspection": "#F97316",
    "Detailing": "#14B8A6",
    "Repair Needed": "#EF4444",
    "Reserved": "#2563EB",
    "Sold": "#64748B",
    "Acquired": "#8B5CF6",
}

AGE_COLORS = {
    "0-30": "#22C55E",
    "31-60": "#F59E0B",
    "61-90": "#F97316",
    "90+": "#EF4444",
}


class DashboardAnalytics:
    def __init__(self, inventory_manager: InventoryManager, location_manager: LocationManager):
        self.inventory_manager = inventory_manager
        self.location_manager = location_manager

    def build_overview(self) -> Dict[str, Any]:
        vehicles = self.inventory_manager.all_vehicles()
        metrics = self.inventory_manager.company_metrics()
        total_units = max(metrics["total_units"], 1)

        status_counts = self.inventory_manager.vehicle_counts_by_status(vehicles)
        status_rows = [
            {
                "label": status,
                "count": status_counts.get(status, 0),
                "percent": int(round((status_counts.get(status, 0) / total_units) * 100)),
                "color": STATUS_COLORS.get(status, "#64748B"),
            }
            for status in STATUS_ORDER if status_counts.get(status, 0)
        ]

        age_counts = {bucket: 0 for bucket in AGE_BUCKET_ORDER}
        for vehicle in vehicles:
            age_counts[vehicle.age_bucket()] += 1
        age_rows = [
            {
                "label": bucket,
                "count": age_counts[bucket],
                "percent": int(round((age_counts[bucket] / total_units) * 100)) if total_units else 0,
                "color": AGE_COLORS[bucket],
            }
            for bucket in AGE_BUCKET_ORDER
        ]

        lot_cards = []
        for location in self.location_manager.all_locations():
            lot_metrics = self.inventory_manager.location_metrics(location.location_id)
            capacity = max(location.capacity, 1)
            status_breakdown = self.inventory_manager.location_status_breakdown(location.location_id)
            type_breakdown = self.inventory_manager.location_type_breakdown(location.location_id)
            blockers = []
            for key in ["Inspection", "Detailing", "Repair Needed", "Photo Pending", "Needs Info Added"]:
                count = status_breakdown.get(key, 0)
                if count:
                    blockers.append(f"{key}: {count}")
            lot_cards.append({
                "location_id": location.location_id,
                "name": location.name,
                "city": location.city,
                "manager": location.manager_name,
                "units": lot_metrics["vehicle_count"],
                "value": lot_metrics["location_list_value"],
                "avg_days": lot_metrics["avg_days_on_lot"],
                "ready_units": lot_metrics["ready_units"],
                "aged_units": lot_metrics["aged_units"],
                "occupancy_percent": int(round((lot_metrics["vehicle_count"] / capacity) * 100)),
                "ready_percent": int(round((lot_metrics["ready_units"] / max(lot_metrics['vehicle_count'], 1)) * 100)) if lot_metrics["vehicle_count"] else 0,
                "status_summary": " • ".join(blockers[:3]) if blockers else "No blockers currently flagged",
                "type_summary": " • ".join(f"{k}: {v}" for k, v in type_breakdown.items()),
            })

        attention_units = []
        for vehicle in self.inventory_manager.action_item_vehicles(limit=10):
            reasons = []
            if vehicle.days_on_lot() >= 60:
                reasons.append(f"{vehicle.days_on_lot()} days")
            if not vehicle.photo_paths:
                reasons.append("missing photos")
            if vehicle.status in {"Inspection", "Repair Needed", "Photo Pending", "Detailing", "Needs Info Added"}:
                reasons.append(vehicle.status)
            if vehicle.market_gap() < 0:
                reasons.append("priced above market")
            attention_units.append({
                "title": f"{vehicle.stock_id} • {vehicle.make} {vehicle.model}",
                "subtitle": " • ".join(reasons[:3]) or vehicle.status,
                "location": vehicle.location_id,
                "color": self._risk_color(vehicle),
                "value": vehicle.expected_margin(),
            })
        if not attention_units:
            attention_units.append({
                "title": "No urgent vehicle flags",
                "subtitle": "Inventory is currently in a healthy range.",
                "location": "",
                "color": "#22C55E",
                "value": 0,
            })

        return {
            "metrics": {
                "total_units": metrics["total_units"],
                "total_list_value": metrics["total_list_value"],
                "expected_profit": metrics["expected_gross_profit"],
                "ready_percent": metrics["ready_for_sale_percent"],
                "avg_days": metrics["average_days_on_lot"],
                "aged_units_60": metrics["aged_units_60"],
            },
            "status_rows": status_rows,
            "age_rows": age_rows,
            "lot_cards": lot_cards,
            "attention_units": attention_units,
            "action_vehicles": attention_units[:6],
        }

    def _risk_score(self, vehicle: Vehicle) -> int:
        score = 0
        if vehicle.days_on_lot() >= 90:
            score += 5
        elif vehicle.days_on_lot() >= 60:
            score += 3
        if not vehicle.photo_paths:
            score += 2
        if vehicle.status in {"Inspection", "Repair Needed", "Photo Pending", "Detailing", "Needs Info Added"}:
            score += 3
        if vehicle.market_gap() < 0:
            score += 1
        return score

    def _risk_color(self, vehicle: Vehicle) -> str:
        score = self._risk_score(vehicle)
        if score >= 7:
            return "#EF4444"
        if score >= 4:
            return "#F59E0B"
        return "#22C55E"
