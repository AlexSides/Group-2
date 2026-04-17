import tkinter as tk
from tkinter import messagebox
from datetime import datetime


# ============================================================
# Car Inventory Management System GUI
# ------------------------------------------------------------
# Main Tkinter frontend shell for the inventory interface.
# Contains:
# - sidebar navigation
# - home dashboard
# - recent file preview behavior
# - placeholder backend actions
# ============================================================


class ToolTip:
    """Simple tooltip for Tkinter widgets."""

    # --------------------------------------------------------
    # Setup
    # Stores widget references and binds hover events.
    # --------------------------------------------------------
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    # --------------------------------------------------------
    # Display tooltip
    # Creates a small floating tooltip near the widget.
    # --------------------------------------------------------
    def show_tooltip(self, event=None):
        if self.tip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + 30

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            bg="#111827",
            fg="white",
            relief="solid",
            bd=1,
            font=("Arial", 10),
            padx=8,
            pady=4
        )
        label.pack()

    # --------------------------------------------------------
    # Hide tooltip
    # Removes the tooltip when the cursor leaves the widget.
    # --------------------------------------------------------
    def hide_tooltip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class InventoryApp(tk.Tk):
    """Frontend GUI shell for the Car Inventory Management System."""

    # ========================================================
    # Application setup
    # --------------------------------------------------------
    # Initializes the main window, UI state trackers,
    # and builds the base layout.
    #
    # Future integration:
    # - replace placeholder data with real inventory/session data
    # ========================================================
    def __init__(self):
        super().__init__()

        self.title("Car Inventory Management System")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg="#f4f6f8")
        self.resizable(True, True)

        self.selected_recent_file_card = None
        self.selected_recent_file_icon_label = None
        self.selected_recent_file_name_label = None
        self.selected_recent_file_name = None

        self.recent_canvas = None
        self.recent_press_x = 0
        self.recent_dragging = False
        self.pending_recent_click = None

        self.preview_title_label = None
        self.preview_text = None

        self.session_value_label = None
        self.summary_value_label = None

        self._build_layout()

    # ========================================================
    # Base layout
    # --------------------------------------------------------
    # Creates the persistent sidebar and main content area.
    # ========================================================
    def _build_layout(self):
        self.sidebar = tk.Frame(self, bg="#1f2937", width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self, bg="#f4f6f8")
        self.content.pack(side="right", fill="both", expand=True)

        title = tk.Label(
            self.sidebar,
            text="Car Inventory\nSystem",
            font=("Arial", 20, "bold"),
            bg="#1f2937",
            fg="white",
            justify="center"
        )
        title.pack(pady=(18, 14))

        button_frame = tk.Frame(self.sidebar, bg="#1f2937")
        button_frame.pack(fill="x", padx=16, pady=4)

        button_data = [
            ("Home", self.show_home),
            ("Add Vehicle", self.show_add_vehicle),
            ("Search", self.show_search_inventory),
            ("Locations", self.show_locations),
        ]

        for text, command in button_data:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=("Arial", 12, "bold"),
                bg="#374151",
                fg="white",
                activebackground="#4b5563",
                activeforeground="white",
                relief="flat",
                bd=0,
                anchor="w",
                padx=18,
                height=2,
                cursor="hand2"
            )
            btn.pack(fill="x", pady=7)

        self.show_home()

    # ========================================================
    # Clear active page
    # --------------------------------------------------------
    # Removes current page widgets and resets temporary state.
    # ========================================================
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        self.selected_recent_file_card = None
        self.selected_recent_file_icon_label = None
        self.selected_recent_file_name_label = None
        self.selected_recent_file_name = None

        self.recent_canvas = None
        self.recent_press_x = 0
        self.recent_dragging = False
        self.pending_recent_click = None

        self.preview_title_label = None
        self.preview_text = None
        self.session_value_label = None
        self.summary_value_label = None

    # ========================================================
    # Reusable vertical scroll region
    # --------------------------------------------------------
    # Builds a scrollable canvas + inner frame combination.
    # Used for pages that may grow beyond the window height.
    # ========================================================
    def make_vertical_scroll_region(self, parent, bg="#f4f6f8"):
        outer = tk.Frame(parent, bg=bg)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)

        inner = tk.Frame(canvas, bg=bg)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def update_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def resize_inner(event):
            canvas.itemconfigure(window_id, width=event.width)

        inner.bind("<Configure>", update_scrollregion)
        canvas.bind("<Configure>", resize_inner)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._bind_vertical_mousewheel(canvas)

        return outer, canvas, inner

    # --------------------------------------------------------
    # Vertical scroll bindings
    # Connects mousewheel events to vertical canvas scrolling.
    # --------------------------------------------------------
    def _bind_vertical_mousewheel(self, widget):
        widget.bind("<MouseWheel>", lambda e: self._on_vertical_mousewheel(e, widget))
        widget.bind("<Button-4>", lambda e: widget.yview_scroll(-1, "units"))
        widget.bind("<Button-5>", lambda e: widget.yview_scroll(1, "units"))

    # --------------------------------------------------------
    # Vertical scroll handler
    # --------------------------------------------------------
    def _on_vertical_mousewheel(self, event, widget):
        if event.delta > 0:
            widget.yview_scroll(-1, "units")
        elif event.delta < 0:
            widget.yview_scroll(1, "units")

    # ========================================================
    # Header toolbar
    # --------------------------------------------------------
    # Creates the home-page action buttons.
    #
    # Future integration:
    # - connect load/save/report to actual file operations
    # ========================================================
    def build_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg="#b7c3d1")
        toolbar.pack(side="left", anchor="w", padx=8, pady=6)

        icon_style = {
            "font": ("Segoe UI Emoji", 9),
            "bg": "#374151",
            "fg": "white",
            "activebackground": "#4b5563",
            "activeforeground": "white",
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 0,
            "cursor": "hand2",
            "width": 4,
            "height": 1
        }

        load_btn = tk.Button(toolbar, text="📂", command=self.load_placeholder, **icon_style)
        save_btn = tk.Button(toolbar, text="💾", command=self.save_placeholder, **icon_style)
        report_btn = tk.Button(toolbar, text="📋", command=self.report_placeholder, **icon_style)

        load_btn.pack(side="left", padx=(0, 2))
        save_btn.pack(side="left", padx=(0, 2))
        report_btn.pack(side="left")

        ToolTip(load_btn, "Load Inventory")
        ToolTip(save_btn, "Save Inventory")
        ToolTip(report_btn, "View Report")

    # ========================================================
    # Recent file strip scrolling
    # --------------------------------------------------------
    # Handles horizontal scrolling for the recent files area.
    # ========================================================
    def _bind_recent_horizontal_scroll(self, widget):
        widget.bind("<Shift-MouseWheel>", self._on_recent_shift_mousewheel)
        widget.bind("<MouseWheel>", self._on_recent_touchpad_mousewheel)
        widget.bind("<Button-4>", lambda e: self._scroll_recent(-1))
        widget.bind("<Button-5>", lambda e: self._scroll_recent(1))

    def _on_recent_shift_mousewheel(self, event):
        if event.delta > 0:
            self._scroll_recent(-1)
        elif event.delta < 0:
            self._scroll_recent(1)
        return "break"

    def _on_recent_touchpad_mousewheel(self, event):
        if getattr(event, "state", 0):
            if event.delta > 0:
                self._scroll_recent(-1)
            elif event.delta < 0:
                self._scroll_recent(1)
            return "break"

    def _scroll_recent(self, amount):
        if self.recent_canvas is not None:
            self.recent_canvas.xview_scroll(amount, "units")

    # ========================================================
    # Recent file selection and drag behavior
    # --------------------------------------------------------
    # Keeps recent files responsive for:
    # - click to select
    # - drag to scroll
    # - double-click placeholder open
    #
    # Change made:
    # - dragging works across the whole recent area, not just cards
    # ========================================================
    def _recent_area_press(self, event):
        self.recent_press_x = event.x_root
        self.recent_dragging = False

    def _recent_area_drag(self, event):
        if self.recent_canvas is None:
            return

        dx = event.x_root - self.recent_press_x
        if abs(dx) > 2:
            self.recent_dragging = True
            self.recent_canvas.xview_scroll(int(-dx / 8), "units")
            self.recent_press_x = event.x_root

    def _recent_card_press(self, event, file_name, card, icon_label, name_label):
        self.recent_press_x = event.x_root
        self.recent_dragging = False
        self.pending_recent_click = (file_name, card, icon_label, name_label)

    def _recent_card_release(self, event):
        if not self.pending_recent_click:
            return

        file_name, card, icon_label, name_label = self.pending_recent_click
        if not self.recent_dragging:
            self.select_recent_file(card, icon_label, name_label, file_name)
            self.show_file_preview(file_name)
            self.update_home_info(file_name)

        self.pending_recent_click = None
        self.recent_dragging = False

    def _recent_card_double_click(self, event, file_name):
        self.open_recent_file_placeholder(file_name)
        return "break"

    # --------------------------------------------------------
    # Highlight active recent file card
    # --------------------------------------------------------
    def select_recent_file(self, card, icon_label, name_label, file_name):
        default_bg = "#d1d5db"
        selected_bg = "#93a8bf"

        if self.selected_recent_file_card is not None:
            self.selected_recent_file_card.config(bg=default_bg)
        if self.selected_recent_file_icon_label is not None:
            self.selected_recent_file_icon_label.config(bg=default_bg)
        if self.selected_recent_file_name_label is not None:
            self.selected_recent_file_name_label.config(bg=default_bg)

        card.config(bg=selected_bg)
        icon_label.config(bg=selected_bg)
        name_label.config(bg=selected_bg)

        self.selected_recent_file_card = card
        self.selected_recent_file_icon_label = icon_label
        self.selected_recent_file_name_label = name_label
        self.selected_recent_file_name = file_name

    # --------------------------------------------------------
    # Build one recent file card
    # --------------------------------------------------------
    def create_recent_file_card(self, parent, file_name):
        card = tk.Frame(
            parent,
            bg="#d1d5db",
            width=145,
            height=82,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        card.pack(side="left", padx=(0, 10))
        card.pack_propagate(False)

        icon_label = tk.Label(
            card,
            text="📄",
            font=("Arial", 16),
            bg="#d1d5db",
            fg="#374151",
            cursor="hand2"
        )
        icon_label.pack(anchor="w", padx=10, pady=(10, 2))

        name_label = tk.Label(
            card,
            text=file_name,
            font=("Arial", 10, "bold"),
            bg="#d1d5db",
            fg="#111827",
            anchor="w",
            justify="left",
            wraplength=120,
            cursor="hand2"
        )
        name_label.pack(fill="x", padx=10)

        for widget in (card, icon_label, name_label):
            widget.bind(
                "<ButtonPress-1>",
                lambda e, fn=file_name, c=card, i=icon_label, n=name_label:
                self._recent_card_press(e, fn, c, i, n)
            )
            widget.bind("<B1-Motion>", self._recent_area_drag)
            widget.bind("<ButtonRelease-1>", self._recent_card_release)
            widget.bind(
                "<Double-Button-1>",
                lambda e, fn=file_name: self._recent_card_double_click(e, fn)
            )
            self._bind_recent_horizontal_scroll(widget)

        return card

    # ========================================================
    # Preview and summary updates
    # --------------------------------------------------------
    # Updates the right-side preview area and left-side info cards.
    #
    # Future integration:
    # - load real file contents
    # - show actual vehicle/location/save metadata
    # ========================================================
    def show_file_preview(self, file_name):
        """Show preview text in the large open white area."""
        if self.preview_title_label is not None:
            self.preview_title_label.config(text=f"Preview: {file_name}")

        if self.preview_text is not None:
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(
                "1.0",
                f"{file_name}\n\n"
                "Preview window\n"
                "-------------------------\n\n"
                "This is a fake preview area for the selected recent file.\n"
                "Later, this can show real file details, notes, metadata,\n"
                "or a short file summary."
            )

    def update_home_info(self, file_name):
        """Update Session and Summary cards from selected test file."""
        current_date = datetime.now().strftime("%B %d, %Y")

        if self.session_value_label is not None:
            self.session_value_label.config(text=file_name)

        if self.summary_value_label is not None:
            self.summary_value_label.config(
                text=f"Vehicles: 0\nLocations: Austin\nLast Save: {current_date}"
            )

    # ========================================================
    # Home page
    # --------------------------------------------------------
    # Main dashboard view.
    # Includes:
    # - header toolbar
    # - session panel
    # - summary panel
    # - preview area
    # - recent files strip
    #
    # Change made:
    # - header stays above session/summary
    # - recent files stay docked at the bottom
    # ========================================================
    def show_home(self):
        self.clear_content()

        home_container = tk.Frame(self.content, bg="#f4f6f8")
        home_container.pack(fill="both", expand=True)

        header_panel = tk.Frame(home_container, bg="#b7c3d1", height=44)
        header_panel.pack(fill="x", side="top")
        header_panel.pack_propagate(False)
        self.build_toolbar(header_panel)

        body = tk.Frame(home_container, bg="#f4f6f8")
        body.pack(fill="both", expand=True)

        left_panel = tk.Frame(body, bg="#e5e7eb", width=280)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(body, bg="#f4f6f8")
        right_panel.pack(side="right", fill="both", expand=True)

        left_inner = tk.Frame(left_panel, bg="#e5e7eb")
        left_inner.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(
            left_inner,
            text="Session",
            font=("Arial", 14, "bold"),
            bg="#e5e7eb",
            fg="#111827",
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        session_card = tk.Frame(left_inner, bg="white", relief="flat", bd=0)
        session_card.pack(fill="x", pady=(0, 12))

        self.session_value_label = tk.Label(
            session_card,
            text="No inventory loaded",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#111827",
            anchor="w",
            padx=12,
            pady=12
        )
        self.session_value_label.pack(fill="x")

        tk.Label(
            left_inner,
            text="Summary",
            font=("Arial", 14, "bold"),
            bg="#e5e7eb",
            fg="#111827",
            anchor="w"
        ).pack(fill="x", pady=(8, 10))

        summary_card = tk.Frame(left_inner, bg="white", relief="flat", bd=0)
        summary_card.pack(fill="x")

        self.summary_value_label = tk.Label(
            summary_card,
            text="Vehicles: --\nLocations: --\nLast Save: --",
            font=("Arial", 11),
            justify="left",
            bg="white",
            fg="#374151",
            anchor="w",
            padx=12,
            pady=12
        )
        self.summary_value_label.pack(fill="x")

        preview_wrapper = tk.Frame(right_panel, bg="#f4f6f8")
        preview_wrapper.pack(fill="both", expand=True, padx=16, pady=(16, 8))

        self.preview_title_label = tk.Label(
            preview_wrapper,
            text="Preview: No file selected",
            font=("Arial", 14, "bold"),
            bg="#f4f6f8",
            fg="#111827",
            anchor="w"
        )
        self.preview_title_label.pack(anchor="w", pady=(0, 10))

        self.preview_text = tk.Text(
            preview_wrapper,
            font=("Arial", 11),
            bg="white",
            fg="#111827",
            relief="solid",
            bd=1,
            wrap="word"
        )
        self.preview_text.pack(fill="both", expand=True)
        self.preview_text.insert("1.0", "Select a recent file to preview it here.")

        recent_wrapper = tk.Frame(right_panel, bg="#f4f6f8")
        recent_wrapper.pack(fill="x", side="bottom", anchor="sw", padx=16, pady=(0, 16))

        tk.Label(
            recent_wrapper,
            text="Recent Files",
            font=("Arial", 14, "bold"),
            bg="#f4f6f8",
            fg="#111827",
            anchor="w"
        ).pack(anchor="w", pady=(0, 10))

        recent_outer = tk.Frame(recent_wrapper, bg="#f4f6f8")
        recent_outer.pack(fill="x")

        self.recent_canvas = tk.Canvas(
            recent_outer,
            bg="#f4f6f8",
            highlightthickness=0,
            bd=0,
            height=95
        )
        self.recent_canvas.pack(side="top", fill="x", expand=True)

        recent_scroll_x = tk.Scrollbar(
            recent_outer,
            orient="horizontal",
            command=self.recent_canvas.xview
        )
        recent_scroll_x.pack(side="bottom", fill="x")

        self.recent_canvas.configure(xscrollcommand=recent_scroll_x.set)

        recent_row = tk.Frame(self.recent_canvas, bg="#f4f6f8")
        recent_window = self.recent_canvas.create_window((0, 0), window=recent_row, anchor="nw")

        def update_recent_scroll(event=None):
            self.recent_canvas.configure(scrollregion=self.recent_canvas.bbox("all"))

        def resize_recent_window(event):
            row_req_width = recent_row.winfo_reqwidth()
            self.recent_canvas.itemconfigure(recent_window, width=row_req_width)

        recent_row.bind("<Configure>", update_recent_scroll)
        self.recent_canvas.bind("<Configure>", resize_recent_window)

        for widget in (self.recent_canvas, recent_row, recent_outer, recent_wrapper):
            widget.bind("<ButtonPress-1>", self._recent_area_press)
            widget.bind("<B1-Motion>", self._recent_area_drag)
            self._bind_recent_horizontal_scroll(widget)

        fake_files = [
            "yard_a.json",
            "inventory_backup.csv",
            "april_report.json",
            "warehouse_2.csv",
            "fleet_test.json",
            "north_lot_export.csv",
            "march_snapshot.json",
            "vehicle_log_backup.csv"
        ]

        for file_name in fake_files:
            self.create_recent_file_card(recent_row, file_name)

    # ========================================================
    # Secondary pages
    # --------------------------------------------------------
    # Placeholder pages until real forms and data views are added.
    # ========================================================
    def show_add_vehicle(self):
        self.clear_content()

        _, _, scrollable = self.make_vertical_scroll_region(self.content, bg="#f4f6f8")

        frame = tk.Frame(scrollable, bg="#f4f6f8")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        tk.Label(
            frame,
            text="Add Vehicle",
            font=("Arial", 22, "bold"),
            bg="#f4f6f8",
            fg="#111827"
        ).pack(pady=(10, 18))

        tk.Label(
            frame,
            text="Vehicle entry form will go here.",
            font=("Arial", 13),
            bg="#f4f6f8",
            fg="#4b5563"
        ).pack(pady=10)

        spacer = tk.Frame(frame, bg="#f4f6f8", height=700)
        spacer.pack(fill="x")

    def show_search_inventory(self):
        self.clear_content()

        _, _, scrollable = self.make_vertical_scroll_region(self.content, bg="#f4f6f8")

        frame = tk.Frame(scrollable, bg="#f4f6f8")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        tk.Label(
            frame,
            text="Search Inventory",
            font=("Arial", 22, "bold"),
            bg="#f4f6f8",
            fg="#111827"
        ).pack(pady=(10, 18))

        tk.Label(
            frame,
            text="Search tools and result display will go here.",
            font=("Arial", 13),
            bg="#f4f6f8",
            fg="#4b5563"
        ).pack(pady=10)

        spacer = tk.Frame(frame, bg="#f4f6f8", height=700)
        spacer.pack(fill="x")

    def show_locations(self):
        self.clear_content()

        _, _, scrollable = self.make_vertical_scroll_region(self.content, bg="#f4f6f8")

        frame = tk.Frame(scrollable, bg="#f4f6f8")
        frame.pack(fill="both", expand=True, padx=24, pady=24)

        tk.Label(
            frame,
            text="Locations",
            font=("Arial", 22, "bold"),
            bg="#f4f6f8",
            fg="#111827"
        ).pack(pady=(10, 18))

        tk.Label(
            frame,
            text="Warehouse, yard, or dealership locations will go here.",
            font=("Arial", 13),
            bg="#f4f6f8",
            fg="#4b5563"
        ).pack(pady=10)

        spacer = tk.Frame(frame, bg="#f4f6f8", height=700)
        spacer.pack(fill="x")

    # ========================================================
    # Placeholder actions
    # --------------------------------------------------------
    # Temporary message boxes until backend functions exist.
    # ========================================================
    def save_placeholder(self):
        messagebox.showinfo("Save", "Save button works. Backend not connected yet.")

    def load_placeholder(self):
        messagebox.showinfo("Load", "Load button works. Backend not connected yet.")

    def report_placeholder(self):
        messagebox.showinfo("Report", "Report button works. Backend not connected yet.")

    def open_recent_file_placeholder(self, file_name):
        messagebox.showerror("Recent File", f'"{file_name}" does not exist yet.')


# ============================================================
# Program entry point
# ------------------------------------------------------------
# Runs the app when this file is executed directly.
# ============================================================
if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
