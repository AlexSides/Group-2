from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHeaderView,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QSpinBox,
    QDoubleSpinBox,
    QStackedWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from InventoryManager import InventoryManager
from LocationManager import Location, LocationManager
from SampleData import seed_inventory
from Vehicle import Vehicle
from DashboardAnalytics import DashboardAnalytics
from DashboardWidgets import (
    DashboardActionRow,
    DashboardLotRow,
    DashboardMarginRow,
    DashboardMetricCard,
    DashboardProgressRow,
)


STATUSES = [
    "Acquired",
    "Inspection",
    "Repair Needed",
    "Detailing",
    "Photo Pending",
    "Needs Info Added",
    "Ready for Sale",
    "Reserved",
    "Sold",
]

TABLE_COLUMNS = [
    "Photo",
    "Stock ID",
    "Year",
    "Make",
    "Model",
    "Type",
    "Mileage",
    "List Price",
    "Market Value",
    "Margin",
    "Days",
    "Status",
    "Location",
]

LOT_COLUMNS = [
    "Stock ID",
    "Vehicle",
    "Status",
    "List Price",
    "Days",
    "Photos",
]


def money(value: float) -> str:
    return f"${value:,.0f}"


def status_color(status: str) -> str:
    mapping = {
        "Ready for Sale": "#2E9E6F",
        "Needs Info Added": "#4F46E5",
        "Photo Pending": "#F59E0B",
        "Inspection": "#D97706",
        "Repair Needed": "#DC2626",
        "Reserved": "#2563EB",
        "Sold": "#6B7280",
        "Detailing": "#0EA5A4",
        "Acquired": "#8B5CF6",
    }
    return mapping.get(status, "#64748B")


class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "--", subtitle: str = ""):
        super().__init__()
        self.setObjectName("metricCard")
        self.setMinimumHeight(128)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        self.accent = QFrame()
        self.accent.setObjectName("metricAccent")
        self.accent.setFixedHeight(6)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setMinimumHeight(22)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("metricValue")
        self.value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.value_label.setMinimumHeight(42)
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("cardSubtitle")
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setMinimumHeight(22)

        layout.addWidget(self.accent)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)
        layout.addStretch()

    def set_theme(self, accent: str, tint: str = "#FFFFFF"):
        self.setStyleSheet(
            f"QFrame#metricCard{{background:{tint}; border:1px solid #E3EAF6; border-radius:24px;}}"
            f"QFrame#metricAccent{{background:{accent}; border:none; border-radius:3px;}}"
        )
        self.value_label.setStyleSheet(f"color:{accent}; font-size:28px; font-weight:900;")


class Panel(QFrame):
    def __init__(self, title: str, subtitle: str = ""):
        super().__init__()
        self.setObjectName("panel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)
        title_label = QLabel(title)
        title_label.setMinimumHeight(28)
        title_label.setObjectName("panelTitle")
        layout.addWidget(title_label)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("softText")
            subtitle_label.setWordWrap(True)
            subtitle_label.setMinimumHeight(22)
            layout.addWidget(subtitle_label)
        self.body = QVBoxLayout()
        self.body.setSpacing(12)
        layout.addLayout(self.body)


class ProgressInsightRow(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("progressInsightRow")
        self.setMinimumHeight(86)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        self.name_label = QLabel("Label")
        self.name_label.setObjectName("progressLabel")
        self.name_label.setMinimumHeight(20)
        self.count_label = QLabel("0")
        self.count_label.setObjectName("progressCount")
        top.addWidget(self.name_label)
        top.addStretch()
        top.addWidget(self.count_label)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(10)

        self.percent_label = QLabel("0% of inventory")
        self.percent_label.setObjectName("softText")

        layout.addLayout(top)
        layout.addWidget(self.bar)
        layout.addWidget(self.percent_label)

    def set_data(self, label: str, count: int, percent: int, color: str):
        self.name_label.setText(label)
        self.count_label.setText(str(count))
        self.bar.setValue(max(0, min(100, percent)))
        self.percent_label.setText(f"{percent}% of inventory")
        self.bar.setStyleSheet(
            f"QProgressBar{{background:#EEF2F8; border:none; border-radius:5px;}}"
            f"QProgressBar::chunk{{background:{color}; border-radius:5px;}}"
        )


class LotHealthCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("lotHealthCard")
        self.setMinimumHeight(168)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        self.title_label = QLabel("Lot")
        self.title_label.setObjectName("lotHealthTitle")
        self.title_label.setMinimumHeight(24)
        self.meta_label = QLabel("City • Manager")
        self.meta_label.setObjectName("softText")

        self.value_label = QLabel("$0")
        self.value_label.setObjectName("lotHealthValue")
        self.stats_label = QLabel("0 units • 0 avg days • 0 aged")
        self.stats_label.setObjectName("bodyText")

        self.occupancy_bar = QProgressBar()
        self.occupancy_bar.setRange(0, 100)
        self.occupancy_bar.setTextVisible(False)
        self.occupancy_bar.setFixedHeight(10)

        self.ready_bar = QProgressBar()
        self.ready_bar.setRange(0, 100)
        self.ready_bar.setTextVisible(False)
        self.ready_bar.setFixedHeight(10)

        self.occupancy_caption = QLabel("Occupancy")
        self.occupancy_caption.setObjectName("softText")
        self.ready_caption = QLabel("Ready Rate")
        self.ready_caption.setObjectName("softText")

        layout.addWidget(self.title_label)
        layout.addWidget(self.meta_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.occupancy_caption)
        layout.addWidget(self.occupancy_bar)
        layout.addWidget(self.ready_caption)
        layout.addWidget(self.ready_bar)

    def set_data(self, data: dict):
        self.title_label.setText(data["name"])
        self.meta_label.setText(f"{data['city']} • {data['manager']}")
        self.value_label.setText(money(data['value']))
        self.stats_label.setText(f"{data['units']} units • {data['avg_days']:.0f} avg days • {data['aged_units']} aged")
        self.occupancy_caption.setText(f"Occupancy {data['occupancy_percent']}%")
        self.ready_caption.setText(f"Ready Rate {data['ready_percent']}%")
        self.occupancy_bar.setValue(max(0, min(100, data['occupancy_percent'])))
        self.ready_bar.setValue(max(0, min(100, data['ready_percent'])))
        self.occupancy_bar.setStyleSheet("QProgressBar{background:#EEF2F8; border:none; border-radius:5px;} QProgressBar::chunk{background:#4F46E5; border-radius:5px;}")
        self.ready_bar.setStyleSheet("QProgressBar{background:#EEF2F8; border:none; border-radius:5px;} QProgressBar::chunk{background:#22C55E; border-radius:5px;}")


class InsightCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("insightCard")
        self.setMinimumHeight(108)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        self.badge = QLabel("●")
        self.badge.setObjectName("insightBadge")
        self.value_label = QLabel("")
        self.value_label.setObjectName("insightValue")
        top.addWidget(self.badge)
        top.addStretch()
        top.addWidget(self.value_label)

        self.title_label = QLabel("Title")
        self.title_label.setObjectName("insightTitle")
        self.title_label.setMinimumHeight(22)
        self.subtitle_label = QLabel("Subtitle")
        self.subtitle_label.setObjectName("softText")
        self.subtitle_label.setWordWrap(True)

        layout.addLayout(top)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)

    def set_data(self, title: str, subtitle: str, value: str, color: str):
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)
        self.value_label.setText(value)
        self.badge.setStyleSheet(f"color:{color}; font-size:16px; font-weight:900;")


class StatusChip(QLabel):
    def __init__(self):
        super().__init__("—")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(32)
        self.update_status("Acquired")

    def update_status(self, status: str):
        self.setText(status)
        self.setStyleSheet(
            f"background:{status_color(status)}; color:white; border:none; border-radius:16px; padding:6px 14px; font-weight:700;"
        )


class LocationCard(QFrame):
    def __init__(self, location: Location, callback):
        super().__init__()
        self.location = location
        self.callback = callback
        self.selected = False
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("lotCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        self.title = QLabel(location.name)
        self.title.setObjectName("lotTitle")
        self.meta = QLabel(f"{location.city} • Manager: {location.manager_name}")
        self.meta.setObjectName("softText")
        self.stats = QLabel("")
        self.stats.setObjectName("lotStats")
        self.stats.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.meta)
        layout.addWidget(self.stats)
        layout.addStretch()
        self.refresh_style()

    def mousePressEvent(self, event):
        self.callback(self.location.location_id)
        super().mousePressEvent(event)

    def set_summary(self, lines: list[str]):
        self.stats.setText("\n".join(lines))

    def set_selected(self, selected: bool):
        self.selected = selected
        self.refresh_style()

    def refresh_style(self):
        if self.selected:
            self.setStyleSheet("#lotCard {background:#EEF2FF; border:2px solid #6366F1; border-radius:22px;}")
        else:
            self.setStyleSheet("#lotCard {background:white; border:1px solid #E3EAF6; border-radius:22px;}")


class VehicleDialog(QDialog):
    def __init__(self, location_manager: LocationManager, vehicle: Vehicle | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Vehicle" if vehicle else "Add Vehicle")
        self.setModal(True)
        self.resize(720, 760)
        self.location_manager = location_manager
        self.photo_paths: list[str] = list(vehicle.photo_paths) if vehicle else []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(14)

        tabs = QTabWidget()
        outer.addWidget(tabs)

        basic_tab = QWidget()
        basic_form = QFormLayout(basic_tab)
        basic_form.setLabelAlignment(Qt.AlignRight)
        basic_form.setSpacing(12)
        self.type_combo = QComboBox(); self.type_combo.addItems(["Car", "Truck", "Motorcycle"])
        self.stock_id_edit = QLineEdit(); self.vin_edit = QLineEdit(); self.make_edit = QLineEdit(); self.model_edit = QLineEdit(); self.trim_edit = QLineEdit()
        self.year_spin = QSpinBox(); self.year_spin.setRange(1990, 2100)
        self.color_edit = QLineEdit(); self.mileage_spin = QSpinBox(); self.mileage_spin.setRange(0, 2_000_000)
        basic_form.addRow("Type", self.type_combo)
        basic_form.addRow("Stock ID", self.stock_id_edit)
        basic_form.addRow("VIN", self.vin_edit)
        basic_form.addRow("Make", self.make_edit)
        basic_form.addRow("Model", self.model_edit)
        basic_form.addRow("Trim", self.trim_edit)
        basic_form.addRow("Year", self.year_spin)
        basic_form.addRow("Color", self.color_edit)
        basic_form.addRow("Mileage", self.mileage_spin)
        tabs.addTab(basic_tab, "Basic")

        business_tab = QWidget()
        business_form = QFormLayout(business_tab)
        business_form.setLabelAlignment(Qt.AlignRight)
        business_form.setSpacing(12)
        self.location_combo = QComboBox()
        for location in self.location_manager.all_locations():
            self.location_combo.addItem(location.name, location.location_id)
        self.status_combo = QComboBox(); self.status_combo.addItems(STATUSES)
        self.acquisition_spin = QDoubleSpinBox(); self.acquisition_spin.setRange(0, 10_000_000); self.acquisition_spin.setPrefix("$"); self.acquisition_spin.setDecimals(2)
        self.reconditioning_spin = QDoubleSpinBox(); self.reconditioning_spin.setRange(0, 1_000_000); self.reconditioning_spin.setPrefix("$"); self.reconditioning_spin.setDecimals(2)
        self.list_price_spin = QDoubleSpinBox(); self.list_price_spin.setRange(0, 10_000_000); self.list_price_spin.setPrefix("$"); self.list_price_spin.setDecimals(2)
        self.market_value_spin = QDoubleSpinBox(); self.market_value_spin.setRange(0, 10_000_000); self.market_value_spin.setPrefix("$"); self.market_value_spin.setDecimals(2)
        self.depreciation_spin = QDoubleSpinBox(); self.depreciation_spin.setRange(0, 1_000_000); self.depreciation_spin.setPrefix("$"); self.depreciation_spin.setDecimals(2)
        self.days_spin = QSpinBox(); self.days_spin.setRange(0, 3650)
        business_form.addRow("Location", self.location_combo)
        business_form.addRow("Status", self.status_combo)
        business_form.addRow("Acquisition Cost", self.acquisition_spin)
        business_form.addRow("Reconditioning", self.reconditioning_spin)
        business_form.addRow("List Price", self.list_price_spin)
        business_form.addRow("Market Value", self.market_value_spin)
        business_form.addRow("Depreciation", self.depreciation_spin)
        business_form.addRow("Days on Lot", self.days_spin)
        tabs.addTab(business_tab, "Business")

        tech_tab = QWidget()
        tech_form = QFormLayout(tech_tab)
        tech_form.setLabelAlignment(Qt.AlignRight)
        tech_form.setSpacing(12)
        self.engine_serial_edit = QLineEdit(); self.horsepower_spin = QSpinBox(); self.horsepower_spin.setRange(0, 5000)
        self.torque_spin = QSpinBox(); self.torque_spin.setRange(0, 10000)
        self.fuel_combo = QComboBox(); self.fuel_combo.addItems(["Gasoline", "Diesel", "Hybrid", "Electric", "Other"])
        self.chassis_combo = QComboBox(); self.chassis_combo.addItems(["unibody", "body-on-frame", "space frame", "other"])
        self.chassis_weight_spin = QDoubleSpinBox(); self.chassis_weight_spin.setRange(0, 10000); self.chassis_weight_spin.setDecimals(1)
        self.material_edit = QLineEdit()
        self.extra_one_label = QLabel("Doors")
        self.extra_one_widget = QSpinBox(); self.extra_one_widget.setRange(0, 20000)
        self.extra_two_label = QLabel("Body Type")
        self.extra_two_widget = QLineEdit()
        self.extra_three_label = QLabel("Drivetrain")
        self.extra_three_widget = QLineEdit()
        tech_form.addRow("Engine Serial", self.engine_serial_edit)
        tech_form.addRow("Horsepower", self.horsepower_spin)
        tech_form.addRow("Torque (Nm)", self.torque_spin)
        tech_form.addRow("Fuel Type", self.fuel_combo)
        tech_form.addRow("Chassis Type", self.chassis_combo)
        tech_form.addRow("Chassis Weight", self.chassis_weight_spin)
        tech_form.addRow("Material", self.material_edit)
        tech_form.addRow(self.extra_one_label, self.extra_one_widget)
        tech_form.addRow(self.extra_two_label, self.extra_two_widget)
        tech_form.addRow(self.extra_three_label, self.extra_three_widget)
        tabs.addTab(tech_tab, "Technical")

        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        notes_layout.addWidget(QLabel("Photos"))
        photo_row = QHBoxLayout()
        self.photo_line = QLineEdit(); self.photo_line.setReadOnly(True); self.photo_line.setPlaceholderText("No photos selected")
        pick_photos = QPushButton("Select Photos")
        pick_photos.clicked.connect(self.pick_photos)
        photo_row.addWidget(self.photo_line); photo_row.addWidget(pick_photos)
        notes_layout.addLayout(photo_row)
        notes_layout.addWidget(QLabel("Notes"))
        self.notes_edit = QTextEdit(); self.notes_edit.setMinimumHeight(180)
        notes_layout.addWidget(self.notes_edit)
        tabs.addTab(notes_tab, "Photos + Notes")

        button_row = QHBoxLayout()
        button_row.addStretch()
        cancel_btn = QPushButton("Cancel"); cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Vehicle"); save_btn.setObjectName("accentButton"); save_btn.clicked.connect(self.accept)
        button_row.addWidget(cancel_btn); button_row.addWidget(save_btn)
        outer.addLayout(button_row)

        self.type_combo.currentTextChanged.connect(self._update_type_fields)
        self._populate(vehicle)
        self._update_type_fields(self.type_combo.currentText())

    def pick_photos(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Vehicle Photos", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if files:
            self.photo_paths = files
            text = ", ".join(os.path.basename(path) for path in files[:3]) + (" ..." if len(files) > 3 else "")
            self.photo_line.setText(text)

    def _populate(self, vehicle: Vehicle | None):
        self.year_spin.setValue(date.today().year)
        if not vehicle:
            self.days_spin.setValue(0)
            return
        self.type_combo.setCurrentText(vehicle.vehicle_type)
        self.stock_id_edit.setText(vehicle.stock_id)
        self.vin_edit.setText(vehicle.vin)
        self.make_edit.setText(vehicle.make)
        self.model_edit.setText(vehicle.model)
        self.trim_edit.setText(vehicle.trim)
        self.year_spin.setValue(vehicle.year)
        self.color_edit.setText(vehicle.color)
        self.mileage_spin.setValue(vehicle.mileage)
        self.location_combo.setCurrentIndex(max(0, self.location_combo.findData(vehicle.location_id)))
        self.status_combo.setCurrentText(vehicle.status)
        self.acquisition_spin.setValue(vehicle.acquisition_cost)
        self.reconditioning_spin.setValue(vehicle.reconditioning_cost)
        self.list_price_spin.setValue(vehicle.list_price)
        self.market_value_spin.setValue(vehicle.estimated_market_value)
        self.depreciation_spin.setValue(vehicle.depreciation_value)
        self.days_spin.setValue(vehicle.days_on_lot())
        self.engine_serial_edit.setText(vehicle.engine.serial_number)
        self.horsepower_spin.setValue(vehicle.engine.horsepower)
        self.torque_spin.setValue(vehicle.engine.torque_nm)
        self.fuel_combo.setCurrentText(vehicle.engine.fuel_type)
        self.chassis_combo.setCurrentText(vehicle.chassis.chassis_type)
        self.chassis_weight_spin.setValue(float(vehicle.chassis.weight_kg))
        self.material_edit.setText(vehicle.chassis.material or "")
        self.notes_edit.setPlainText(vehicle.notes)
        self.photo_paths = list(vehicle.photo_paths)
        if self.photo_paths:
            text = ", ".join(os.path.basename(path) for path in self.photo_paths[:3]) + (" ..." if len(self.photo_paths) > 3 else "")
            self.photo_line.setText(text)
        if isinstance(vehicle, Car):
            self.extra_one_widget.setValue(vehicle.num_doors)
            self.extra_two_widget.setText(vehicle.body_type)
            self.extra_three_widget.setText(vehicle.drivetrain)
        elif isinstance(vehicle, Truck):
            self.extra_one_widget.setValue(vehicle.payload_capacity_lb)
            self.extra_two_widget.setText(str(vehicle.towing_capacity_lb))
            self.extra_three_widget.setText(vehicle.drive_type)
        elif isinstance(vehicle, Motorcycle):
            self.extra_one_widget.setValue(vehicle.engine_displacement_cc)
            self.extra_two_widget.setText("Yes" if vehicle.is_sport_bike else "No")
            self.extra_three_widget.setText(vehicle.bike_type)

    def _update_type_fields(self, vehicle_type: str):
        if vehicle_type == "Car":
            self.extra_one_label.setText("Doors")
            self.extra_two_label.setText("Body Type")
            self.extra_three_label.setText("Drivetrain")
        elif vehicle_type == "Truck":
            self.extra_one_label.setText("Payload (lb)")
            self.extra_two_label.setText("Towing (lb)")
            self.extra_three_label.setText("Drive Type")
        else:
            self.extra_one_label.setText("Engine CC")
            self.extra_two_label.setText("Sport Bike? (Yes/No)")
            self.extra_three_label.setText("Bike Type")

    def get_vehicle(self) -> Vehicle:
        engine = Engine(
            self.engine_serial_edit.text().strip() or f"ENG-{self.stock_id_edit.text().strip()}",
            self.horsepower_spin.value(),
            self.torque_spin.value(),
            self.fuel_combo.currentText(),
        )
        chassis = Chassis(
            self.chassis_combo.currentText(),
            self.chassis_weight_spin.value(),
            self.material_edit.text().strip() or None,
        )
        common = dict(
            stock_id=self.stock_id_edit.text().strip(),
            vin=self.vin_edit.text().strip(),
            make=self.make_edit.text().strip(),
            model=self.model_edit.text().strip(),
            trim=self.trim_edit.text().strip(),
            year=self.year_spin.value(),
            color=self.color_edit.text().strip(),
            mileage=self.mileage_spin.value(),
            acquisition_cost=self.acquisition_spin.value(),
            reconditioning_cost=self.reconditioning_spin.value(),
            list_price=self.list_price_spin.value(),
            estimated_market_value=self.market_value_spin.value(),
            location_id=self.location_combo.currentData(),
            status=self.status_combo.currentText(),
            engine=engine,
            chassis=chassis,
            notes=self.notes_edit.toPlainText().strip(),
            photo_paths=list(self.photo_paths),
            date_acquired=(date.today() - timedelta(days=self.days_spin.value())).isoformat(),
            depreciation_value=self.depreciation_spin.value(),
        )
        vehicle_type = self.type_combo.currentText()
        if vehicle_type == "Car":
            return Car(**common, num_doors=self.extra_one_widget.value(), body_type=self.extra_two_widget.text().strip() or "Sedan", drivetrain=self.extra_three_widget.text().strip() or "FWD")
        if vehicle_type == "Truck":
            towing = int(float(self.extra_two_widget.text().strip() or "0"))
            return Truck(**common, payload_capacity_lb=self.extra_one_widget.value(), towing_capacity_lb=towing, drive_type=self.extra_three_widget.text().strip() or "4x2")
        sport_text = self.extra_two_widget.text().strip().lower()
        return Motorcycle(**common, engine_displacement_cc=self.extra_one_widget.value(), is_sport_bike=sport_text in {"yes","y","true","1"}, bike_type=self.extra_three_widget.text().strip() or "Standard")


class TransferDialog(QDialog):
    def __init__(self, location_manager: LocationManager, current_location_id: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transfer Vehicle")
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addWidget(QLabel("Move selected vehicle to another lot."))
        self.location_combo = QComboBox()
        for location in location_manager.all_locations():
            self.location_combo.addItem(location.name, location.location_id)
        self.location_combo.setCurrentIndex(max(0, self.location_combo.findData(current_location_id)))
        layout.addWidget(self.location_combo)
        button_row = QHBoxLayout(); button_row.addStretch()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        apply_btn = QPushButton("Transfer"); apply_btn.setObjectName("accentButton"); apply_btn.clicked.connect(self.accept)
        button_row.addWidget(cancel); button_row.addWidget(apply_btn)
        layout.addLayout(button_row)

    def selected_location(self) -> str:
        return self.location_combo.currentData()


class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Car Inventory Management System")
        self.resize(1550, 950)
        self.setMinimumSize(1280, 820)

        self.inventory_manager = InventoryManager()
        self.inventory_manager.load_from_json("inventory.json")
        self.location_manager = LocationManager()
        self.dashboard_analytics = DashboardAnalytics(self.inventory_manager, self.location_manager)
        self.current_page = "Overview"
        self.selected_location_id = "AUS"
        self.selected_vehicle_vin: str | None = None
        self.inventory_hover_vin: str | None = None
        self.images_folder = ""
        self.detail_photo_index = 0
        self.detail_photo_vehicle_vin: str | None = None

        self._seed_data()
        self._build_ui()
        self._apply_styles()
        self.refresh_all_views()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)

    def _seed_data(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(base_dir, "images")
        samples = seed_inventory(self.inventory_manager, self.location_manager, images_dir)
        if samples:
            self.selected_vehicle_vin = samples[0].vin

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_header())
        self.stack = QStackedWidget()
        outer.addWidget(self.stack, 1)
        self.overview_page = self._build_overview_page()
        self.lots_page = self._build_lots_page()
        self.inventory_page = self._build_inventory_page()
        self.vehicle_detail_page = self._build_vehicle_detail_page()
        self.reports_page = self._build_reports_page()
        for page in [self.overview_page, self.lots_page, self.inventory_page, self.vehicle_detail_page, self.reports_page]:
            self.stack.addWidget(page)
        self.set_page("Overview")

    def _build_header(self):
        header = QFrame()
        header.setObjectName("topHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(18)
        brand_col = QVBoxLayout(); brand_col.setSpacing(2)
        brand = QLabel("Car Inventory System"); brand.setObjectName("brandTitle")
        tagline = QLabel("Inventory browser + dedicated vehicle workspace")
        tagline.setObjectName("brandSubtitle")
        brand_col.addWidget(brand); brand_col.addWidget(tagline)
        layout.addLayout(brand_col)
        layout.addSpacing(12)
        self.nav_buttons: dict[str, QPushButton] = {}
        nav_row = QHBoxLayout(); nav_row.setSpacing(10)
        for name in ["Overview", "Lots", "Inventory", "Reports"]:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setObjectName("navButton")
            btn.clicked.connect(lambda checked=False, page=name: self.set_page(page))
            self.nav_buttons[name] = btn
            nav_row.addWidget(btn)
        layout.addLayout(nav_row)
        layout.addStretch()
        self.photos_folder_btn = QPushButton("Load Photos Folder"); self.photos_folder_btn.setObjectName("softButton"); self.photos_folder_btn.clicked.connect(self.choose_images_folder)
        self.save_json_btn = QPushButton("Save Inventory JSON"); self.save_json_btn.setObjectName("accentButton"); self.save_json_btn.clicked.connect(self.save_inventory_json)
        layout.addWidget(self.photos_folder_btn); layout.addWidget(self.save_json_btn)
        return header

    def _page_shell(self, title: str, subtitle: str):
        page = QWidget()
        main = QVBoxLayout(page)
        main.setContentsMargins(26, 22, 26, 24)
        main.setSpacing(16)
        title_label = QLabel(title); title_label.setObjectName("pageTitle")
        subtitle_label = QLabel(subtitle); subtitle_label.setObjectName("pageSubtitle"); subtitle_label.setWordWrap(True)
        main.addWidget(title_label)
        main.addWidget(subtitle_label)
        return page, main

    def _build_overview_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        main = QVBoxLayout(content)
        main.setContentsMargins(26, 22, 26, 24)
        main.setSpacing(16)

        title_label = QLabel("Overview")
        title_label.setObjectName("pageTitle")
        subtitle_label = QLabel("Run the lot from one screen: track the most important KPIs, spot bottlenecks fast, and compare lot health without crowding the page.")
        subtitle_label.setObjectName("pageSubtitle")
        subtitle_label.setWordWrap(True)
        main.addWidget(title_label)
        main.addWidget(subtitle_label)

        self.overview_metrics = {
            "units": DashboardMetricCard("Active Units"),
            "ready": DashboardMetricCard("Front-Line Ready %"),
            "aged": DashboardMetricCard("Aged 60+"),
            "profit": DashboardMetricCard("Expected Gross Profit"),
        }
        metric_themes = {
            "units": ("#2563EB", "#EFF6FF"),
            "ready": ("#14B8A6", "#F0FDFA"),
            "aged": ("#EF4444", "#FEF2F2"),
            "profit": ("#22C55E", "#F0FDF4"),
        }
        metric_grid = QGridLayout()
        metric_grid.setHorizontalSpacing(14)
        metric_grid.setVerticalSpacing(14)
        for idx, key in enumerate(["units", "ready", "aged", "profit"]):
            self.overview_metrics[key].set_theme(*metric_themes[key])
            metric_grid.addWidget(self.overview_metrics[key], 0, idx)
        main.addLayout(metric_grid)

        mid_grid = QGridLayout()
        mid_grid.setHorizontalSpacing(14)
        mid_grid.setVerticalSpacing(14)

        self.action_panel = Panel("Action Board", "What needs attention first today.")
        self.action_container = QVBoxLayout()
        self.action_container.setSpacing(10)
        self.action_panel.body.addLayout(self.action_container)

        self.status_panel = Panel("Workflow Distribution", "How inventory is split across statuses.")
        self.status_container = QVBoxLayout()
        self.status_container.setSpacing(8)
        self.status_panel.body.addLayout(self.status_container)

        self.age_panel = Panel("Inventory Aging", "Which age buckets are growing stale.")
        self.age_container = QVBoxLayout()
        self.age_container.setSpacing(8)
        self.age_panel.body.addLayout(self.age_container)

        mid_grid.addWidget(self.action_panel, 0, 0, 2, 1)
        mid_grid.addWidget(self.status_panel, 0, 1)
        mid_grid.addWidget(self.age_panel, 1, 1)
        mid_grid.setColumnStretch(0, 3)
        mid_grid.setColumnStretch(1, 2)
        main.addLayout(mid_grid)

        self.lot_performance_panel = Panel("Lot Performance", "Compare value, occupancy, readiness, and aging by location.")
        self.lot_cards_container = QVBoxLayout()
        self.lot_cards_container.setSpacing(10)
        self.lot_performance_panel.body.addLayout(self.lot_cards_container)
        main.addWidget(self.lot_performance_panel)

        self.margin_panel = Panel("Action Vehicles", "Vehicles that deserve follow-up because of age, missing info, or workflow blockers.")
        self.margin_container = QVBoxLayout()
        self.margin_container.setSpacing(10)
        self.margin_panel.body.addLayout(self.margin_container)
        main.addWidget(self.margin_panel)

        scroll.setWidget(content)
        outer.addWidget(scroll)
        return page

    def _build_lots_page(self):
        page, main = self._page_shell("Lots", "Use Lots to diagnose each location: what is ready, what is blocking sales, and what the lot is made of.")
        card_row = QHBoxLayout(); card_row.setSpacing(14)
        self.location_cards: dict[str, LocationCard] = {}
        for location in self.location_manager.all_locations():
            card = LocationCard(location, self.select_location)
            self.location_cards[location.location_id] = card
            card_row.addWidget(card)
        main.addLayout(card_row)

        top_grid = QGridLayout(); top_grid.setHorizontalSpacing(14); top_grid.setVerticalSpacing(14)
        self.lot_summary_panel = Panel("Selected Lot Summary", "Big picture for the selected location.")
        self.lot_summary_content = QLabel(); self.lot_summary_content.setObjectName("bodyText"); self.lot_summary_content.setWordWrap(True)
        self.lot_summary_panel.body.addWidget(self.lot_summary_content)

        self.lot_status_panel = Panel("Lot Status Breakdown", "What is helping or holding this location back.")
        self.lot_status_container = QVBoxLayout(); self.lot_status_container.setSpacing(10)
        self.lot_status_panel.body.addLayout(self.lot_status_container)

        self.lot_mix_panel = Panel("Lot Vehicle Mix", "Vehicle makeup and top action vehicles.")
        self.lot_mix_content = QLabel(); self.lot_mix_content.setObjectName("bodyText"); self.lot_mix_content.setWordWrap(True)
        self.lot_mix_panel.body.addWidget(self.lot_mix_content)

        top_grid.addWidget(self.lot_summary_panel, 0, 0)
        top_grid.addWidget(self.lot_status_panel, 0, 1)
        top_grid.addWidget(self.lot_mix_panel, 1, 0, 1, 2)
        main.addLayout(top_grid)

        main.addLayout(self._build_action_toolbar())
        self.lot_table = self._make_table(len(LOT_COLUMNS), LOT_COLUMNS)
        self.lot_table.itemSelectionChanged.connect(lambda: self.handle_table_selection(self.lot_table))
        self.lot_table.itemDoubleClicked.connect(lambda item: self.open_vehicle_detail(item.data(Qt.UserRole)))
        main.addWidget(self.lot_table)
        return page

    def _build_inventory_page(self):
        page, main = self._page_shell("Inventory", "Raw inventory lives here: search, filter, compare, then double-click to open the full vehicle page.")
        filters = QHBoxLayout(); filters.setSpacing(12)
        self.search_edit = QLineEdit(); self.search_edit.setPlaceholderText("Search stock ID, VIN, make, model, status, or location")
        self.search_edit.textChanged.connect(self.refresh_inventory_page)
        self.filter_location = QComboBox(); self.filter_location.addItem("All Locations", "")
        self.filter_status = QComboBox(); self.filter_status.addItem("All Statuses", "")
        self.filter_type = QComboBox(); self.filter_type.addItem("All Types", "")
        for loc in self.location_manager.all_locations():
            self.filter_location.addItem(loc.name, loc.location_id)
        for status in STATUSES:
            self.filter_status.addItem(status, status)
        for vtype in ["Car", "Truck", "Motorcycle"]:
            self.filter_type.addItem(vtype, vtype)
        self.filter_location.currentIndexChanged.connect(self.refresh_inventory_page)
        self.filter_status.currentIndexChanged.connect(self.refresh_inventory_page)
        self.filter_type.currentIndexChanged.connect(self.refresh_inventory_page)
        filters.addWidget(self.search_edit, 3)
        filters.addWidget(self.filter_location, 1)
        filters.addWidget(self.filter_status, 1)
        filters.addWidget(self.filter_type, 1)
        main.addLayout(filters)

        preview_row = QHBoxLayout(); preview_row.setSpacing(16)
        self.inventory_hover_panel = Panel("Row Preview", "Hover or use arrow keys to preview a vehicle before opening it.")
        preview_wrap = QHBoxLayout(); preview_wrap.setSpacing(14)
        self.inventory_hover_image = QLabel("Hover a vehicle row")
        self.inventory_hover_image.setObjectName("hoverPhoto")
        self.inventory_hover_image.setAlignment(Qt.AlignCenter)
        self.inventory_hover_image.setMinimumSize(260, 170)
        self.inventory_hover_image.setMaximumHeight(180)
        preview_text_col = QVBoxLayout(); preview_text_col.setSpacing(8)
        self.inventory_hover_title = QLabel("No preview yet")
        self.inventory_hover_title.setObjectName("detailTitle")
        self.inventory_hover_meta = QLabel("Move your mouse over a table row")
        self.inventory_hover_meta.setObjectName("softText")
        self.inventory_hover_price = QLabel("")
        self.inventory_hover_price.setObjectName("hoverPrice")
        self.inventory_hover_market = QLabel("")
        self.inventory_hover_market.setObjectName("softText")
        preview_text_col.addWidget(self.inventory_hover_title)
        preview_text_col.addWidget(self.inventory_hover_meta)
        preview_text_col.addWidget(self.inventory_hover_price)
        preview_text_col.addWidget(self.inventory_hover_market)
        preview_text_col.addStretch()
        preview_wrap.addWidget(self.inventory_hover_image)
        preview_wrap.addLayout(preview_text_col, 1)
        self.inventory_hover_panel.body.addLayout(preview_wrap)
        preview_row.addWidget(self.inventory_hover_panel, 2)
        preview_row.addLayout(self._build_action_toolbar(), 3)
        main.addLayout(preview_row)

        self.inventory_table = self._make_table(len(TABLE_COLUMNS), TABLE_COLUMNS)
        self.inventory_table.setMouseTracking(True)
        self.inventory_table.itemSelectionChanged.connect(lambda: self.handle_table_selection(self.inventory_table))
        self.inventory_table.itemDoubleClicked.connect(lambda item: self.open_vehicle_detail(item.data(Qt.UserRole)))
        self.inventory_table.cellEntered.connect(self.handle_inventory_hover)
        main.addWidget(self.inventory_table)
        return page

    def _build_vehicle_detail_page(self):
        page, main = self._page_shell("Vehicle Detail", "Dedicated workspace for one vehicle at a time.")
        top_actions = QHBoxLayout(); top_actions.setSpacing(10)
        self.vehicle_back_btn = QPushButton("← Back to Inventory")
        self.vehicle_back_btn.setObjectName("softButton")
        self.vehicle_back_btn.clicked.connect(lambda: self.set_page("Inventory"))
        prev_btn = QPushButton("Previous"); prev_btn.setObjectName("toolbarButton"); prev_btn.clicked.connect(lambda: self.step_vehicle(-1))
        next_btn = QPushButton("Next"); next_btn.setObjectName("toolbarButton"); next_btn.clicked.connect(lambda: self.step_vehicle(1))
        edit_btn = QPushButton("Edit Vehicle"); edit_btn.setObjectName("toolbarButton"); edit_btn.clicked.connect(self.edit_selected_vehicle)
        transfer_btn = QPushButton("Transfer"); transfer_btn.setObjectName("toolbarButton"); transfer_btn.clicked.connect(self.transfer_selected_vehicle)
        upload_btn = QPushButton("Upload Photos"); upload_btn.setObjectName("toolbarButton"); upload_btn.clicked.connect(self.upload_photos_for_selected)
        top_actions.addWidget(self.vehicle_back_btn)
        top_actions.addStretch()
        for btn in [prev_btn, next_btn, edit_btn, transfer_btn, upload_btn]:
            top_actions.addWidget(btn)
        main.addLayout(top_actions)

        hero = QHBoxLayout(); hero.setSpacing(18)
        self.detail_photo_frame = QFrame(); self.detail_photo_frame.setObjectName("heroPhotoFrame")
        photo_layout = QVBoxLayout(self.detail_photo_frame); photo_layout.setContentsMargins(14, 14, 14, 14)
        self.detail_photo = QLabel("No photo loaded")
        self.detail_photo.setObjectName("heroPhoto")
        self.detail_photo.setAlignment(Qt.AlignCenter)
        self.detail_photo.setMinimumHeight(380)
        photo_layout.addWidget(self.detail_photo)
        photo_nav = QHBoxLayout(); photo_nav.setSpacing(10)
        self.detail_photo_prev_btn = QPushButton("← Photo")
        self.detail_photo_prev_btn.setObjectName("toolbarButton")
        self.detail_photo_prev_btn.clicked.connect(lambda: self.step_vehicle_photo(-1))
        self.detail_photo_next_btn = QPushButton("Photo →")
        self.detail_photo_next_btn.setObjectName("toolbarButton")
        self.detail_photo_next_btn.clicked.connect(lambda: self.step_vehicle_photo(1))
        self.detail_photo_counter = QLabel("0 / 0")
        self.detail_photo_counter.setObjectName("softText")
        photo_nav.addWidget(self.detail_photo_prev_btn)
        photo_nav.addStretch()
        photo_nav.addWidget(self.detail_photo_counter)
        photo_nav.addStretch()
        photo_nav.addWidget(self.detail_photo_next_btn)
        photo_layout.addLayout(photo_nav)
        hero.addWidget(self.detail_photo_frame, 3)

        right = QVBoxLayout(); right.setSpacing(14)
        summary_panel = Panel("Vehicle Summary")
        self.detail_title = QLabel("No vehicle selected"); self.detail_title.setObjectName("heroTitle")
        self.detail_meta = QLabel("Select a vehicle from Inventory or Lots")
        self.detail_meta.setObjectName("softText")
        self.detail_status = StatusChip(); self.detail_status.setMaximumWidth(190)
        summary_panel.body.addWidget(self.detail_title)
        summary_panel.body.addWidget(self.detail_meta)
        summary_panel.body.addWidget(self.detail_status)

        metrics_grid = QGridLayout(); metrics_grid.setHorizontalSpacing(10); metrics_grid.setVerticalSpacing(10)
        self.detail_metric_labels = {}
        keys = ["List Price", "Market Value", "Margin", "Days on Lot", "Location", "Mileage"]
        for i, key in enumerate(keys):
            card = QFrame(); card.setObjectName("miniStat")
            card_layout = QVBoxLayout(card); card_layout.setContentsMargins(12, 10, 12, 10)
            key_label = QLabel(key); key_label.setObjectName("miniStatKey")
            value_label = QLabel("—"); value_label.setObjectName("miniStatValue")
            self.detail_metric_labels[key] = value_label
            card_layout.addWidget(key_label); card_layout.addWidget(value_label)
            metrics_grid.addWidget(card, i // 2, i % 2)
        summary_panel.body.addLayout(metrics_grid)
        right.addWidget(summary_panel)
        hero.addLayout(right, 2)
        main.addLayout(hero)

        self.detail_tabs = QTabWidget()
        self.detail_overview = self._make_text_tab()
        self.detail_pricing = self._make_text_tab()
        self.detail_components = self._make_text_tab()
        self.detail_photos = self._make_text_tab()
        self.detail_notes = self._make_text_tab()
        self.detail_tabs.addTab(self.detail_overview, "Overview")
        self.detail_tabs.addTab(self.detail_pricing, "Pricing")
        self.detail_tabs.addTab(self.detail_components, "Components")
        self.detail_tabs.addTab(self.detail_photos, "Photos")
        self.detail_tabs.addTab(self.detail_notes, "Notes")
        main.addWidget(self.detail_tabs)
        return page

    def _make_text_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        label = QLabel("—")
        label.setObjectName("bodyText")
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addStretch()
        tab.content_label = label
        return tab

    def _build_reports_page(self):
        page, main = self._page_shell("Reports", "Keep reports lighter for now until the browsing and detail workflow feels perfect.")
        roadmap = Panel("What comes next")
        label = QLabel(
            "• Aging and depreciation charts\n"
            "• Margin opportunity by lot\n"
            "• Inventory mix over time\n"
            "• Missing photo workflow reports\n"
            "• Transfer history and lot comparisons"
        )
        label.setObjectName("bodyText")
        roadmap.body.addWidget(label)
        main.addWidget(roadmap)
        return page

    def _build_action_toolbar(self):
        row = QHBoxLayout(); row.setSpacing(10)
        label = QLabel("Actions"); label.setObjectName("sectionEyebrow")
        row.addWidget(label); row.addStretch()
        actions = [
            ("Add Vehicle", self.add_vehicle),
            ("Generate Report", self.show_report),
            ("Edit Selected", self.edit_selected_vehicle),
            ("Delete Selected", self.delete_selected_vehicle),
            ("Transfer", self.transfer_selected_vehicle),
            ("Upload Photos", self.upload_photos_for_selected),
        ]
        for text, callback in actions:
            btn = QPushButton(text)
            btn.setObjectName("toolbarButton")
            btn.clicked.connect(callback)
            row.addWidget(btn)
        return row

    def _make_table(self, column_count: int, headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, column_count)
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setMinimumHeight(560)
        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        for i in range(column_count):
            mode = QHeaderView.ResizeToContents if i < min(6, column_count) else QHeaderView.Stretch
            header.setSectionResizeMode(i, mode)
        return table

    def set_page(self, page_name: str):
        pages = {"Overview": 0, "Lots": 1, "Inventory": 2, "VehicleDetail": 3, "Reports": 4}
        self.current_page = page_name
        self.stack.setCurrentIndex(pages[page_name])
        for name, btn in self.nav_buttons.items():
            btn.setChecked(name == page_name)
        if page_name == "VehicleDetail":
            self.refresh_vehicle_detail_page()
        elif page_name == "Overview":
            self.refresh_overview()
        elif page_name == "Inventory":
            self.refresh_inventory_page()
        elif page_name == "Lots":
            self.refresh_lots_page()

    def open_vehicle_detail(self, vin: str | None):
        if not vin:
            return
        self.selected_vehicle_vin = vin
        self.refresh_vehicle_detail_page()
        self.set_page("VehicleDetail")

    def select_location(self, location_id: str):
        self.selected_location_id = location_id
        self.refresh_lots_page()

    def all_vehicles(self) -> list[Vehicle]:
        return self.inventory_manager.all_vehicles()

    def selected_vehicle(self) -> Vehicle | None:
        return self.inventory_manager.get_vehicle(self.selected_vehicle_vin) if self.selected_vehicle_vin else None

    def refresh_all_views(self):
        self.refresh_overview()
        self.refresh_inventory_page()
        self.refresh_lots_page()
        self.refresh_vehicle_detail_page()

    def refresh_overview(self):
        overview = self.dashboard_analytics.build_overview()
        metrics = overview["metrics"]
        self.overview_metrics["units"].value_label.setText(str(metrics["total_units"]))
        self.overview_metrics["units"].subtitle_label.setText("Vehicles currently tracked across all lots")
        self.overview_metrics["ready"].value_label.setText(f"{metrics['ready_percent']:.0f}%")
        self.overview_metrics["ready"].subtitle_label.setText("Units already lot-ready and sellable")
        self.overview_metrics["aged"].value_label.setText(str(metrics["aged_units_60"]))
        self.overview_metrics["aged"].subtitle_label.setText("Vehicles sitting longer than 60 days")
        self.overview_metrics["profit"].value_label.setText(money(metrics["expected_profit"]))
        self.overview_metrics["profit"].subtitle_label.setText("Current expected gross opportunity")

        self.clear_layout(self.action_container)
        for item in overview["attention_units"][:5]:
            row = DashboardActionRow()
            row.set_data(item["title"], item["subtitle"], item.get("location", ""), item["color"])
            self.action_container.addWidget(row)
        self.action_container.addStretch()

        self.clear_layout(self.status_container)
        for row_data in overview["status_rows"][:5]:
            row = DashboardProgressRow()
            row.set_data(row_data["label"], row_data["count"], row_data["percent"], row_data["color"])
            self.status_container.addWidget(row)
        self.status_container.addStretch()

        self.clear_layout(self.age_container)
        for row_data in overview["age_rows"]:
            row = DashboardProgressRow()
            row.set_data(row_data["label"], row_data["count"], row_data["percent"], row_data["color"])
            self.age_container.addWidget(row)
        self.age_container.addStretch()

        self.clear_layout(self.lot_cards_container)
        for row_data in overview["lot_cards"]:
            row = DashboardLotRow()
            row.set_data(row_data)
            self.lot_cards_container.addWidget(row)
        self.lot_cards_container.addStretch()

        self.clear_layout(self.margin_container)
        for item in overview["action_vehicles"]:
            row = DashboardMarginRow()
            row.set_data(item["title"], item["subtitle"], item.get("value", 0))
            self.margin_container.addWidget(row)
        self.margin_container.addStretch()

    def filtered_inventory_vehicles(self) -> list[Vehicle]:
        vehicles = self.inventory_manager.search(self.search_edit.text())
        location_id = self.filter_location.currentData(); status = self.filter_status.currentData(); vehicle_type = self.filter_type.currentData()
        if location_id:
            vehicles = [v for v in vehicles if v.location_id == location_id]
        if status:
            vehicles = [v for v in vehicles if v.status == status]
        if vehicle_type:
            vehicles = [v for v in vehicles if v.vehicle_type == vehicle_type]
        return vehicles

    def refresh_inventory_page(self):
        vehicles = self.filtered_inventory_vehicles()
        self.populate_table(self.inventory_table, vehicles, TABLE_COLUMNS)
        preview_vehicle = self.inventory_manager.get_vehicle(self.inventory_hover_vin) if self.inventory_hover_vin else (self.selected_vehicle() or (vehicles[0] if vehicles else None))
        self.refresh_hover_preview(preview_vehicle)

    def refresh_lots_page(self):
        for location_id, card in self.location_cards.items():
            lm = self.inventory_manager.location_metrics(location_id)
            card.set_selected(location_id == self.selected_location_id)
            card.set_summary([
                f"{lm['vehicle_count']} units",
                f"{money(lm['location_list_value'])} list value",
                f"{lm['avg_days_on_lot']:.0f} avg days",
            ])

        vehicles = self.inventory_manager.filter_by_location(self.selected_location_id)
        self.populate_table(self.lot_table, vehicles, LOT_COLUMNS)
        location = self.location_manager.get_location(self.selected_location_id)
        lm = self.inventory_manager.location_metrics(self.selected_location_id)
        status_breakdown = self.inventory_manager.location_status_breakdown(self.selected_location_id)
        type_breakdown = self.inventory_manager.location_type_breakdown(self.selected_location_id)
        action_items = self.inventory_manager.action_item_vehicles(limit=4, location_id=self.selected_location_id)

        if location:
            lines = [
                f"{location.name} — {location.city}",
                f"Manager: {location.manager_name}",
                f"Address: {location.address}",
                f"Capacity: {location.capacity}",
                "",
                f"Vehicle Count: {lm['vehicle_count']}",
                f"List Value: {money(lm['location_list_value'])}",
                f"Market Value: {money(lm['location_market_value'])}",
                f"Expected Margin: {money(lm['location_expected_margin'])}",
                f"Average Days on Lot: {lm['avg_days_on_lot']:.0f}",
                f"Ready for Sale: {lm['ready_units']}",
                f"Aged Units: {lm['aged_units']}",
                f"Missing Photos: {lm['photo_missing_count']}",
            ]
            self.lot_summary_content.setText("\n".join(lines))

        self.clear_layout(self.lot_status_container)
        status_order = ["Ready for Sale", "Needs Info Added", "Photo Pending", "Inspection", "Detailing", "Repair Needed"]
        total = max(len(vehicles), 1)
        for status in status_order:
            count = status_breakdown.get(status, 0)
            if count:
                row = DashboardProgressRow()
                row.set_data(status, count, int(round((count / total) * 100)), status_color(status))
                self.lot_status_container.addWidget(row)
        self.lot_status_container.addStretch()

        mix_lines = ["Vehicle mix:"]
        for key, value in type_breakdown.items():
            mix_lines.append(f"• {key}: {value}")
        if action_items:
            mix_lines += ["", "Action vehicles:"]
            for vehicle in action_items:
                mix_lines.append(f"• {vehicle.stock_id} — {vehicle.make} {vehicle.model} • {vehicle.status} • {vehicle.days_on_lot()} days")
        self.lot_mix_content.setText("\n".join(mix_lines))

    def refresh_vehicle_detail_page(self):
        vehicle = self.selected_vehicle()
        if not vehicle:
            self.detail_title.setText("No vehicle selected")
            self.detail_meta.setText("Select a vehicle from Inventory or Lots")
            self.detail_status.update_status("Acquired")
            self.detail_photo.setText("No photo loaded")
            self.detail_photo.setPixmap(QPixmap())
            self.detail_photo_counter.setText("0 / 0")
            self.detail_photo_prev_btn.setEnabled(False)
            self.detail_photo_next_btn.setEnabled(False)
            self.detail_photo_vehicle_vin = None
            self.detail_photo_index = 0
            for label in self.detail_metric_labels.values():
                label.setText("—")
            for tab in [self.detail_overview, self.detail_pricing, self.detail_components, self.detail_photos, self.detail_notes]:
                tab.content_label.setText("—")
            return

        if self.detail_photo_vehicle_vin != vehicle.vin:
            self.detail_photo_vehicle_vin = vehicle.vin
            self.detail_photo_index = 0
        self.detail_title.setText(f"{vehicle.year} {vehicle.make} {vehicle.model}")
        self.detail_meta.setText(f"{vehicle.vehicle_type} • {vehicle.stock_id} • {vehicle.vin}")
        self.detail_status.update_status(vehicle.status)
        self.detail_metric_labels["List Price"].setText(money(vehicle.list_price))
        self.detail_metric_labels["Market Value"].setText(money(vehicle.estimated_market_value))
        self.detail_metric_labels["Margin"].setText(money(vehicle.expected_margin()))
        self.detail_metric_labels["Days on Lot"].setText(str(vehicle.days_on_lot()))
        self.detail_metric_labels["Location"].setText(vehicle.location_id)
        self.detail_metric_labels["Mileage"].setText(f"{vehicle.mileage:,}")
        self.detail_overview.content_label.setText(
            f"Year: {vehicle.year}\nMake: {vehicle.make}\nModel: {vehicle.model}\nTrim: {vehicle.trim or '—'}\nColor: {vehicle.color}\n"
            f"Location: {vehicle.location_id}\nStatus: {vehicle.status}\nDays on Lot: {vehicle.days_on_lot()}\nAge Bucket: {vehicle.age_bucket()}"
        )
        self.detail_pricing.content_label.setText(
            f"Acquisition Cost: {money(vehicle.acquisition_cost)}\nReconditioning: {money(vehicle.reconditioning_cost)}\n"
            f"Total Investment: {money(vehicle.total_investment())}\nList Price: {money(vehicle.list_price)}\n"
            f"Estimated Market Value: {money(vehicle.estimated_market_value)}\nExpected Margin: {money(vehicle.expected_margin())}\nDepreciation: {money(vehicle.depreciation_value)}"
        )
        extra = vehicle.subclass_detail_fields()
        self.detail_components.content_label.setText(
            f"Engine Serial: {vehicle.engine.serial_number}\nHorsepower: {vehicle.engine.horsepower}\nTorque: {vehicle.engine.torque_nm}\n"
            f"Fuel Type: {vehicle.engine.fuel_type}\nChassis Type: {vehicle.chassis.chassis_type}\nChassis Weight: {vehicle.chassis.weight_kg}\n"
            f"Load Rating: {vehicle.chassis.get_load_rating()}\n" + "\n".join(f"{k}: {v}" for k, v in extra.items())
        )
        if vehicle.photo_paths:
            self.detail_photos.content_label.setText("\n".join([f"Photo count: {len(vehicle.photo_paths)}", ""] + [f"• {os.path.basename(path)}" for path in vehicle.photo_paths]))
        else:
            self.detail_photos.content_label.setText("No photos linked yet.")
        self.detail_notes.content_label.setText(vehicle.notes or "No notes yet.")
        self.update_detail_photo_display(vehicle)

    def update_detail_photo_display(self, vehicle: Vehicle | None = None):
        vehicle = vehicle or self.selected_vehicle()
        if not vehicle or not vehicle.photo_paths:
            self.detail_photo_counter.setText("0 / 0")
            self.detail_photo_prev_btn.setEnabled(False)
            self.detail_photo_next_btn.setEnabled(False)
            self.set_vehicle_photo(self.detail_photo, "")
            return
        total = len(vehicle.photo_paths)
        self.detail_photo_index = max(0, min(self.detail_photo_index, total - 1))
        self.detail_photo_counter.setText(f"{self.detail_photo_index + 1} / {total}")
        self.detail_photo_prev_btn.setEnabled(total > 1)
        self.detail_photo_next_btn.setEnabled(total > 1)
        self.set_vehicle_photo(self.detail_photo, vehicle.photo_paths[self.detail_photo_index])

    def step_vehicle_photo(self, direction: int):
        vehicle = self.selected_vehicle()
        if not vehicle or len(vehicle.photo_paths) <= 1:
            return
        self.detail_photo_index = (self.detail_photo_index + direction) % len(vehicle.photo_paths)
        self.update_detail_photo_display(vehicle)

    def populate_table(self, table: QTableWidget, vehicles: list[Vehicle], columns: list[str]):
        table.blockSignals(True)
        table.clearContents()
        table.setRowCount(len(vehicles))
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        for row, vehicle in enumerate(vehicles):
            if columns == TABLE_COLUMNS:
                values = {
                    "Photo": "Yes" if vehicle.photo_paths else "No",
                    "Stock ID": vehicle.stock_id,
                    "Year": str(vehicle.year),
                    "Make": vehicle.make,
                    "Model": vehicle.model,
                    "Type": vehicle.vehicle_type,
                    "Mileage": f"{vehicle.mileage:,}",
                    "List Price": money(vehicle.list_price),
                    "Market Value": money(vehicle.estimated_market_value),
                    "Margin": money(vehicle.expected_margin()),
                    "Days": str(vehicle.days_on_lot()),
                    "Status": f"● {vehicle.status}",
                    "Location": vehicle.location_id,
                }
            else:
                values = {
                    "Stock ID": vehicle.stock_id,
                    "Vehicle": f"{vehicle.year} {vehicle.make} {vehicle.model}",
                    "Status": f"● {vehicle.status}",
                    "List Price": money(vehicle.list_price),
                    "Days": str(vehicle.days_on_lot()),
                    "Photos": str(len(vehicle.photo_paths)),
                }
            for col, header in enumerate(columns):
                item = QTableWidgetItem(values.get(header, ""))
                item.setData(Qt.UserRole, vehicle.vin)
                if header == "Status":
                    item.setForeground(QColor(status_color(vehicle.status)))
                    item.setTextAlignment(Qt.AlignCenter)
                elif header in {"List Price", "Market Value", "Margin", "Mileage", "Days", "Photos", "Year"}:
                    item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, item)
        table.blockSignals(False)
        self.restore_table_selection(table)

    def restore_table_selection(self, table: QTableWidget):
        if not self.selected_vehicle_vin:
            if table.rowCount() > 0:
                table.selectRow(0)
            return
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.data(Qt.UserRole) == self.selected_vehicle_vin:
                table.selectRow(row)
                return
        if table.rowCount() > 0:
            table.selectRow(0)

    def handle_table_selection(self, table: QTableWidget):
        selected = table.selectedItems()
        if not selected:
            return
        vin = selected[0].data(Qt.UserRole)
        if not vin:
            return
        self.selected_vehicle_vin = vin
        vehicle = self.inventory_manager.get_vehicle(vin)
        if table is self.inventory_table:
            self.inventory_hover_vin = vin
            self.refresh_hover_preview(vehicle)
        if self.current_page == "VehicleDetail":
            self.refresh_vehicle_detail_page()

    def handle_inventory_hover(self, row: int, column: int):
        item = self.inventory_table.item(row, 0)
        if not item:
            return
        vin = item.data(Qt.UserRole)
        self.inventory_hover_vin = vin
        self.refresh_hover_preview(self.inventory_manager.get_vehicle(vin))

    def refresh_hover_preview(self, vehicle: Vehicle | None):
        if not vehicle:
            self.inventory_hover_title.setText("No preview yet")
            self.inventory_hover_meta.setText("Move your mouse over a table row")
            self.inventory_hover_price.setText("")
            self.inventory_hover_market.setText("")
            self.inventory_hover_image.setPixmap(QPixmap())
            self.inventory_hover_image.setText("Hover a vehicle row")
            return
        self.inventory_hover_title.setText(f"{vehicle.year} {vehicle.make} {vehicle.model}")
        self.inventory_hover_meta.setText(f"{vehicle.stock_id} • {vehicle.location_id} • {vehicle.status}")
        self.inventory_hover_price.setText(f"Pricing: {money(vehicle.list_price)}  •  Margin: {money(vehicle.expected_margin())}")
        self.inventory_hover_market.setText(f"Market value: {money(vehicle.estimated_market_value)}  •  {vehicle.days_on_lot()} days on lot")
        self.set_vehicle_photo(self.inventory_hover_image, vehicle.primary_photo)

    def step_vehicle(self, direction: int):
        vehicles = self.filtered_inventory_vehicles() if self.current_page == "Inventory" else self.all_vehicles()
        if not vehicles or not self.selected_vehicle_vin:
            return
        vins = [v.vin for v in vehicles]
        if self.selected_vehicle_vin not in vins:
            self.selected_vehicle_vin = vins[0]
        idx = vins.index(self.selected_vehicle_vin)
        idx = (idx + direction) % len(vins)
        self.selected_vehicle_vin = vins[idx]
        self.refresh_vehicle_detail_page()

    def set_vehicle_photo(self, label: QLabel, path: str):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(scaled)
                label.setText("")
                return
        label.setPixmap(QPixmap())
        label.setText("No photo loaded")
        
    def show_report(self):
        report = self.inventory_manager.generate_performance_report()

        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Performance Report", report)

    def add_vehicle(self):
        dialog = VehicleDialog(self.location_manager, parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            vehicle = dialog.get_vehicle()
            self.validate_vehicle(vehicle)
            self.inventory_manager.add_vehicle(vehicle)
            self.selected_vehicle_vin = vehicle.vin
            self.selected_location_id = vehicle.location_id
            self.refresh_all_views()
        except Exception as exc:
            QMessageBox.warning(self, "Could not save vehicle", str(exc))


    def edit_selected_vehicle(self):
        vehicle = self.selected_vehicle()
        if not vehicle:
            QMessageBox.information(self, "Edit Vehicle", "Select a vehicle first.")
            return
        old_vin = vehicle.vin
        dialog = VehicleDialog(self.location_manager, vehicle=vehicle, parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            updated = dialog.get_vehicle()
            self.validate_vehicle(updated)
            if updated.vin != old_vin:
                self.inventory_manager.remove_vehicle(old_vin)
            self.inventory_manager.add_vehicle(updated)
            self.selected_vehicle_vin = updated.vin
            self.selected_location_id = updated.location_id
            self.refresh_all_views()
        except Exception as exc:
            QMessageBox.warning(self, "Could not update vehicle", str(exc))

    def delete_selected_vehicle(self):
        vehicle = self.selected_vehicle()
        if not vehicle:
            QMessageBox.information(self, "Delete Vehicle", "Select a vehicle first.")
            return
        reply = QMessageBox.question(self, "Delete Vehicle", f"Delete {vehicle.stock_id} — {vehicle.year} {vehicle.make} {vehicle.model}?")
        if reply != QMessageBox.Yes:
            return
        self.inventory_manager.remove_vehicle(vehicle.vin)
        remaining = self.all_vehicles()
        self.selected_vehicle_vin = remaining[0].vin if remaining else None
        self.refresh_all_views()
        if self.current_page == "VehicleDetail" and self.selected_vehicle_vin is None:
            self.set_page("Inventory")

    def transfer_selected_vehicle(self):
        vehicle = self.selected_vehicle()
        if not vehicle:
            QMessageBox.information(self, "Transfer Vehicle", "Select a vehicle first.")
            return
        dialog = TransferDialog(self.location_manager, vehicle.location_id, parent=self)
        if dialog.exec() != QDialog.Accepted:
            return
        new_location = dialog.selected_location()
        self.inventory_manager.transfer_vehicle(vehicle.vin, new_location)
        self.selected_location_id = new_location
        self.refresh_all_views()

    def upload_photos_for_selected(self):
        vehicle = self.selected_vehicle()
        if not vehicle:
            QMessageBox.information(self, "Upload Photos", "Select a vehicle first.")
            return
        files, _ = QFileDialog.getOpenFileNames(self, "Select Vehicle Photos", self.images_folder or "", "Images (*.png *.jpg *.jpeg *.webp)")
        if not files:
            return
        vehicle.photo_paths = files
        self.refresh_all_views()

    def choose_images_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Images Folder")
        if not folder:
            return
        self.images_folder = folder
        self.try_auto_link_photos(folder)
        self.refresh_all_views()
        QMessageBox.information(self, "Photos Folder Loaded", f"Photos folder set to:\n{folder}")

    def try_auto_link_photos(self, folder: str):
        files = {name.lower(): os.path.join(folder, name) for name in os.listdir(folder)}
        for vehicle in self.all_vehicles():
            candidates = [
                f"{vehicle.stock_id.lower()}.jpg",
                f"{vehicle.stock_id.lower()}.png",
                f"{vehicle.make.lower()}_{vehicle.model.lower().replace(' ', '')}.jpg",
                f"{vehicle.make.lower()}_{vehicle.model.lower().replace(' ', '')}.png",
                f"{vehicle.model.lower().replace(' ', '')}.jpg",
                f"{vehicle.model.lower().replace(' ', '')}.png",
            ]
            for name in candidates:
                if name in files:
                    vehicle.photo_paths = [files[name]]
                    break

    def save_inventory_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Inventory JSON", "inventory_export.json", "JSON Files (*.json)")
        if not path:
            return
        self.inventory_manager.save_to_json(path)
        QMessageBox.information(self, "Inventory Saved", f"Saved inventory to:\n{path}")

    def validate_vehicle(self, vehicle: Vehicle):
        if not vehicle.stock_id:
            raise ValueError("Stock ID is required.")
        if not vehicle.vin:
            raise ValueError("VIN is required.")
        if not vehicle.make or not vehicle.model:
            raise ValueError("Make and model are required.")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_hover_preview(self.inventory_manager.get_vehicle(self.inventory_hover_vin) if self.inventory_hover_vin else self.selected_vehicle())
        self.refresh_vehicle_detail_page()

    def _apply_styles(self):
        self.setStyleSheet(
            """
            QWidget { background: #F6F8FC; color: #16223B; font-family: Segoe UI, Arial, sans-serif; font-size: 14px; }
            QMainWindow { background: #F6F8FC; }
            #topHeader { background: white; border-bottom: 1px solid #E4EBF5; }
            #brandTitle { color: #14213D; font-size: 24px; font-weight: 900; }
            #brandSubtitle { color: #70819A; font-size: 13px; }
            #navButton { background: #F2F5FB; color: #223455; border: 1px solid #E0E7F2; border-radius: 18px; padding: 10px 16px; font-size: 14px; font-weight: 700; }
            #navButton:checked { background: #EEF2FF; color: #3144AA; border: 1px solid #CDD6FF; }
            #navButton:hover { background: #EDF2F9; }
            #softButton, #toolbarButton { background: white; color: #172554; border: 1px solid #DFE6F2; border-radius: 16px; padding: 11px 15px; font-weight: 700; }
            #toolbarButton:hover, #softButton:hover { background: #F8FAFF; }
            #accentButton { background: #4F46E5; color: white; border: none; border-radius: 16px; padding: 11px 15px; font-weight: 800; }
            #accentButton:hover { background: #4338CA; }
            #pageTitle { font-size: 33px; font-weight: 900; color: #132238; }
            #pageSubtitle { color: #64748B; font-size: 15px; }
            #metricCard, #panel { background: white; border: 1px solid #E3EAF6; border-radius: 24px; }
            #cardTitle { color: #6B7C95; font-size: 13px; font-weight: 700; }
            #metricValue { color: #172554; font-size: 28px; font-weight: 900; }
            #cardSubtitle, #softText { color: #71829B; font-size: 13px; }
            #panelTitle { color: #172554; font-size: 20px; font-weight: 800; }
            #sectionEyebrow { color: #4F46E5; font-size: 12px; font-weight: 800; }
            #lotTitle, #detailTitle, #heroTitle { color: #172554; font-size: 20px; font-weight: 850; }
            #bodyText, #lotStats { color: #40526D; font-size: 14px; line-height: 1.45; }
            #hoverPrice { color: #1E3A8A; font-size: 18px; font-weight: 800; }
            #photoLabel, #hoverPhoto { background: #EEF3FB; border-radius: 18px; color: #6E809A; font-size: 16px; font-weight: 700; }
            #heroPhotoFrame { background: white; border: 1px solid #E3EAF6; border-radius: 24px; }
            #heroPhoto { background: #F3F6FC; border-radius: 18px; color: #6E809A; font-size: 18px; font-weight: 700; }
            #miniStat { background: #F8FAFF; border: 1px solid #E4EBF7; border-radius: 18px; }
            #miniStatKey { color: #71829B; font-size: 12px; font-weight: 700; }
            #miniStatValue { color: #172554; font-size: 20px; font-weight: 800; }
            QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox { background: white; border: 1px solid #DCE5F2; border-radius: 16px; padding: 10px 12px; }
            QTabWidget::pane { border: 1px solid #E3EAF6; border-radius: 18px; background: white; top: -1px; }
            QTabBar::tab { background: #EEF2FF; border: 1px solid #D8E1FF; padding: 10px 15px; margin-right: 6px; border-top-left-radius: 14px; border-top-right-radius: 14px; font-weight: 700; color: #32456E; }
            QTabBar::tab:selected { background: white; color: #1E3A8A; }
            QTableWidget { background: white; border: 1px solid #E3EAF6; border-radius: 22px; gridline-color: #EEF2F8; padding: 10px; alternate-background-color: #FAFCFF; }
            QHeaderView::section { background: transparent; color: #6C7E98; border: none; border-bottom: 1px solid #E6EDF8; padding: 12px 10px; font-weight: 800; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #F0F4FB; }
            QTableWidget::item:selected { background: #EEF2FF; color: #14213D; }
            QScrollBar:vertical, QScrollBar:horizontal { background: transparent; border: none; margin: 4px; }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background: #CAD5E7; border-radius: 8px; min-width: 28px; min-height: 28px; }
            QMessageBox QLabel { color: #16223B; }
            """
        )
