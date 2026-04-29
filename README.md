# Car Inventory Management System - PySide6 Version

## Run
1. Install PySide6:
   `pip install PySide6`
2. Keep the `images/` folder beside the Python files if you want the bundled sample inventory photos.
3. Start the desktop app:
   `python main.py`

## Project structure
```text
inventory_app/
  models/      Vehicle, engine, chassis, location, and vehicle-type classes
  services/    Inventory logic, analytics, and sample-data seeding
  ui/          PySide6 windows and dashboard widgets
scripts/       Utility scripts for report/testing demos
images/        Bundled image assets
main.py        Desktop app entry point
inventory.json Saved inventory snapshot
```

## Current pages
- Overview
- Lots
- Inventory
- Vehicle Detail
- Reports

## Current capabilities
- Load inventory from `inventory.json` at startup
- Seed demo vehicles and lot data when no saved inventory exists
- Add, edit, delete, and transfer vehicles
- Save inventory back to JSON
- Browse metrics, lot health, and vehicle details in the PySide6 UI
- Generate and export a text performance report

## Key backend files
- Vehicle.py
- Car.py
- Truck.py
- Motorcycle.py
- Engine.py
- Chassis.py
- InventoryManager.py
- LocationManager.py

## Good next additions
- CSV import/export
- Editable location management
- Historical transfer log
- More report visualizations
