import sys
from PySide6.QtWidgets import QApplication
from GUI import InventoryApp


def main() -> None:
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
