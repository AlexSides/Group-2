from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout


def money(value: float) -> str:
    return f"${value:,.0f}"


class DashboardMetricCard(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setObjectName("dwMetricCard")
        self.setMinimumHeight(148)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        self.accent = QFrame()
        self.accent.setFixedHeight(6)
        self.accent.setObjectName("dwAccent")
        self.title_label = QLabel(title)
        self.title_label.setObjectName("dwTitle")
        self.value_label = QLabel("--")
        self.value_label.setObjectName("dwValue")
        self.subtitle_label = QLabel("")
        self.subtitle_label.setObjectName("dwSubtitle")
        self.subtitle_label.setWordWrap(True)

        layout.addWidget(self.accent)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)
        layout.addStretch()

    def set_theme(self, accent: str, tint: str):
        self.setStyleSheet(
            f"QFrame#dwMetricCard{{background:{tint}; border:1px solid #E3EAF6; border-radius:22px;}}"
            f"QFrame#dwAccent{{background:{accent}; border:none; border-radius:3px;}}"
        )
        self.value_label.setStyleSheet(f"color:{accent}; font-size:28px; font-weight:900;")


class DashboardProgressRow(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("dwProgressRow")
        self.setMinimumHeight(64)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        top = QHBoxLayout()
        self.label = QLabel("Label")
        self.label.setObjectName("dwRowTitle")
        self.value = QLabel("0")
        self.value.setObjectName("dwRowValue")
        top.addWidget(self.label)
        top.addStretch()
        top.addWidget(self.value)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(10)
        self.caption = QLabel("0% of inventory")
        self.caption.setObjectName("dwSubtitle")

        layout.addLayout(top)
        layout.addWidget(self.bar)
        layout.addWidget(self.caption)

    def set_data(self, label: str, count: int, percent: int, color: str):
        self.label.setText(label)
        self.value.setText(str(count))
        self.caption.setText(f"{percent}% of inventory")
        self.bar.setValue(max(0, min(100, percent)))
        self.bar.setStyleSheet(
            f"QProgressBar{{background:#EEF2F8; border:none; border-radius:5px;}}"
            f"QProgressBar::chunk{{background:{color}; border-radius:5px;}}"
        )


class DashboardActionRow(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("dwActionRow")
        self.setMinimumHeight(58)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        self.dot = QLabel("●")
        self.dot.setObjectName("dwActionDot")
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self.title = QLabel("Title")
        self.title.setObjectName("dwRowTitle")
        self.subtitle = QLabel("Subtitle")
        self.subtitle.setObjectName("dwSubtitle")
        self.subtitle.setWordWrap(True)
        text_col.addWidget(self.title)
        text_col.addWidget(self.subtitle)

        self.trailing = QLabel("")
        self.trailing.setObjectName("dwRowValue")

        layout.addWidget(self.dot)
        layout.addLayout(text_col, 1)
        layout.addWidget(self.trailing)

    def set_data(self, title: str, subtitle: str, trailing: str, color: str):
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.trailing.setText(trailing)
        self.dot.setStyleSheet(f"color:{color}; font-size:16px; font-weight:900;")


class DashboardLotRow(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("dwLotRow")
        self.setMinimumHeight(92)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        top = QHBoxLayout()
        self.title = QLabel("Lot")
        self.title.setObjectName("dwRowTitle")
        self.value = QLabel("$0")
        self.value.setObjectName("dwRowValue")
        top.addWidget(self.title)
        top.addStretch()
        top.addWidget(self.value)

        self.meta = QLabel("")
        self.meta.setObjectName("dwSubtitle")
        self.meta.setWordWrap(True)
        self.blockers = QLabel("")
        self.blockers.setObjectName("dwSubtitle")
        self.blockers.setWordWrap(True)
        self.occupancy = QProgressBar()
        self.occupancy.setRange(0, 100)
        self.occupancy.setTextVisible(False)
        self.occupancy.setFixedHeight(10)
        self.ready = QProgressBar()
        self.ready.setRange(0, 100)
        self.ready.setTextVisible(False)
        self.ready.setFixedHeight(10)
        self.captions = QLabel("")
        self.captions.setObjectName("dwSubtitle")

        layout.addLayout(top)
        layout.addWidget(self.meta)
        layout.addWidget(self.blockers)
        layout.addWidget(self.occupancy)
        layout.addWidget(self.ready)
        layout.addWidget(self.captions)

    def set_data(self, row: dict):
        self.title.setText(f"{row['name']} • {row['units']} units")
        self.value.setText(money(row['value']))
        self.meta.setText(f"{row['city']} • {row['manager']} • {row['avg_days']:.0f} avg days • {row['aged_units']} aged")
        self.blockers.setText(f"{row.get('status_summary', '')}  •  {row.get('type_summary', '')}")
        self.captions.setText(f"Occupancy {row['occupancy_percent']}%  •  Ready {row['ready_percent']}%")
        self.occupancy.setValue(max(0, min(100, row['occupancy_percent'])))
        self.ready.setValue(max(0, min(100, row['ready_percent'])))
        self.occupancy.setStyleSheet("QProgressBar{background:#EEF2F8; border:none; border-radius:5px;} QProgressBar::chunk{background:#4F46E5; border-radius:5px;}")
        self.ready.setStyleSheet("QProgressBar{background:#EEF2F8; border:none; border-radius:5px;} QProgressBar::chunk{background:#22C55E; border-radius:5px;}")


class DashboardMarginRow(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("dwMarginRow")
        self.setMinimumHeight(58)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        self.dot = QLabel("●")
        self.dot.setStyleSheet("color:#22C55E; font-size:16px; font-weight:900;")
        self.title = QLabel("Vehicle")
        self.title.setObjectName("dwRowTitle")
        self.subtitle = QLabel("")
        self.subtitle.setObjectName("dwSubtitle")
        self.value = QLabel("$0")
        self.value.setObjectName("dwRowValue")

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.addWidget(self.title)
        text_col.addWidget(self.subtitle)

        layout.addWidget(self.dot)
        layout.addLayout(text_col, 1)
        layout.addWidget(self.value)

    def set_data(self, title: str, subtitle: str, value: float):
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.value.setText(money(value))
