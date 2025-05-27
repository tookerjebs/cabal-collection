# Arrival Skill tab UI
# Ported from arrival_skill_ocr/ui.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import mouse
import re
from data.arrival_data import get_offensive_skills, get_defensive_skills, get_stat_variations
from automation.arrival_automation import ArrivalAutomation

class ArrivalTab:
    def __init__(self, parent_frame, main_window):
        """Initialize the Arrival Skill tab"""
        self.parent_frame = parent_frame
        self.main_window = main_window

        # Automation components
        self.automation = ArrivalAutomation(
            main_window.game_connector,
            main_window.ocr_engine,
            main_window.update_status
        )

        # UI state
        self.area = None
        self.apply_button_coords = None
        self.change_button_coords = None

        # Create UI
        self.create_ui()

    def create_ui(self):
        """Create the arrival skill UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instructions = (
            "STEPS:\n"
            "1) Set Apply and Change button coordinates\n"
            "2) Define OCR area for stat detection\n"
            "3) Select desired offensive and/or defensive stats\n"
            "4) Press 'Start' - automation will begin!"
        )
        instruction_label = ttk.Label(main_frame, text=instructions, font=("Arial", 9))
        instruction_label.pack(pady=(0, 10))

        # Button coordinates section
        coord_frame = ttk.LabelFrame(main_frame, text="Button Coordinates", padding="5")
        coord_frame.pack(fill=tk.X, pady=(0, 10))

        # Apply button coordinates
        apply_frame = ttk.Frame(coord_frame)
        apply_frame.pack(fill=tk.X, pady=2)

        ttk.Label(apply_frame, text="Apply Button:").pack(side=tk.LEFT)
        self.apply_coord_var = tk.StringVar(value="Not set")
        ttk.Label(apply_frame, textvariable=self.apply_coord_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(apply_frame, text="Set Apply Button", command=self.set_apply_button).pack(side=tk.RIGHT)

        # Change button coordinates
        change_frame = ttk.Frame(coord_frame)
        change_frame.pack(fill=tk.X, pady=2)

        ttk.Label(change_frame, text="Change Button:").pack(side=tk.LEFT)
        self.change_coord_var = tk.StringVar(value="Not set")
        ttk.Label(change_frame, textvariable=self.change_coord_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(change_frame, text="Set Change Button", command=self.set_change_button).pack(side=tk.RIGHT)

        # Area definition
        area_frame = ttk.Frame(main_frame)
        area_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_define_area = ttk.Button(area_frame, text="Define OCR Area", command=self.define_area)
        self.btn_define_area.pack()

        # Stat selection section
        stats_frame = ttk.LabelFrame(main_frame, text="Desired Stats", padding="5")
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # Offensive stat selection
        off_frame = ttk.Frame(stats_frame)
        off_frame.pack(fill=tk.X, pady=2)

        ttk.Label(off_frame, text="Offensive Stat:").pack(side=tk.LEFT)
        self.off_stat = tk.StringVar()

        offensive_skills = [""] + get_offensive_skills()  # Add empty option
        self.off_stat_dropdown = ttk.Combobox(off_frame, textvariable=self.off_stat, values=offensive_skills, state="readonly", width=20)
        self.off_stat_dropdown.pack(side=tk.LEFT, padx=(5, 0))
        self.off_stat_dropdown.bind("<<ComboboxSelected>>", self.update_off_variations)

        ttk.Label(off_frame, text="Min Value:").pack(side=tk.LEFT, padx=(10, 0))
        self.off_var = tk.StringVar()
        self.off_var_dropdown = ttk.Combobox(off_frame, textvariable=self.off_var, state="readonly", width=8)
        self.off_var_dropdown.pack(side=tk.LEFT, padx=(5, 0))

        # Defensive stat selection
        def_frame = ttk.Frame(stats_frame)
        def_frame.pack(fill=tk.X, pady=2)

        ttk.Label(def_frame, text="Defensive Stat:").pack(side=tk.LEFT)
        self.def_stat = tk.StringVar()

        defensive_skills = [""] + get_defensive_skills()  # Add empty option
        self.def_stat_dropdown = ttk.Combobox(def_frame, textvariable=self.def_stat, values=defensive_skills, state="readonly", width=20)
        self.def_stat_dropdown.pack(side=tk.LEFT, padx=(5, 0))
        self.def_stat_dropdown.bind("<<ComboboxSelected>>", self.update_def_variations)

        ttk.Label(def_frame, text="Min Value:").pack(side=tk.LEFT, padx=(10, 0))
        self.def_var = tk.StringVar()
        self.def_var_dropdown = ttk.Combobox(def_frame, textvariable=self.def_var, state="readonly", width=8)
        self.def_var_dropdown.pack(side=tk.LEFT, padx=(5, 0))

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_start = ttk.Button(control_frame, text="Start", command=self.start_automation, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_stop = ttk.Button(control_frame, text="Stop", command=self.stop_automation, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)

    def set_apply_button(self):
        """Set the apply button coordinates"""
        # Connect to game if needed
        if not self.main_window.game_connector.is_connected():
            if not self.main_window.game_connector.connect_to_game():
                messagebox.showerror("Error", "Could not connect to the game window. Make sure the game is running.")
                return

        messagebox.showinfo(
            "Instruction",
            "Click on the 'Apply' button in the game window.\n"
            "The coordinates will be captured automatically."
        )

        # Change cursor to indicate click mode
        self.main_window.root.config(cursor="crosshair")

        def capture_click():
            """Capture the mouse click coordinates"""
            try:
                # Wait for mouse click (exactly as in main.py)
                mouse.wait(button='left')
                x, y = mouse.get_position()

                # Convert to window-relative coordinates
                rel_x, rel_y, success = self.main_window.game_connector.convert_to_window_coords(x, y)

                if success:
                    self.apply_button_coords = (rel_x, rel_y)
                    self.automation.set_apply_button(self.apply_button_coords)
                    self.apply_coord_var.set(f"({rel_x}, {rel_y})")
                    self.main_window.update_status(f"Apply button set at ({rel_x}, {rel_y})")
                else:
                    messagebox.showerror("Error", "Failed to convert coordinates")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to capture click: {str(e)}")
            finally:
                # Reset cursor
                self.main_window.root.config(cursor="")

        # Start capture in thread
        threading.Thread(target=capture_click, daemon=True).start()

    def set_change_button(self):
        """Set the change button coordinates"""
        # Connect to game if needed
        if not self.main_window.game_connector.is_connected():
            if not self.main_window.game_connector.connect_to_game():
                messagebox.showerror("Error", "Could not connect to the game window. Make sure the game is running.")
                return

        messagebox.showinfo(
            "Instruction",
            "Click on the 'Change' button in the game window.\n"
            "The coordinates will be captured automatically."
        )

        # Change cursor to indicate click mode
        self.main_window.root.config(cursor="crosshair")

        def capture_click():
            """Capture the mouse click coordinates"""
            try:
                # Wait for mouse click (exactly as in main.py)
                mouse.wait(button='left')
                x, y = mouse.get_position()

                # Convert to window-relative coordinates
                rel_x, rel_y, success = self.main_window.game_connector.convert_to_window_coords(x, y)

                if success:
                    self.change_button_coords = (rel_x, rel_y)
                    self.automation.set_change_button(self.change_button_coords)
                    self.change_coord_var.set(f"({rel_x}, {rel_y})")
                    self.main_window.update_status(f"Change button set at ({rel_x}, {rel_y})")
                else:
                    messagebox.showerror("Error", "Failed to convert coordinates")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to capture click: {str(e)}")
            finally:
                # Reset cursor
                self.main_window.root.config(cursor="")

        # Start capture in thread
        threading.Thread(target=capture_click, daemon=True).start()

    def define_area(self):
        """Define the OCR area using the shared area selector"""
        def area_callback(area):
            """Callback when area is selected"""
            self.area = area
            self.automation.set_area(area)
            self.btn_start.config(state=tk.NORMAL)
            self.main_window.update_status(f"OCR area defined: {area}")

        # Use the shared area selector
        if not hasattr(self.main_window, 'area_selector'):
            from core.area_selector import AreaSelector
            self.main_window.area_selector = AreaSelector(self.main_window.root, area_callback)
        else:
            self.main_window.area_selector.callback = area_callback

        self.main_window.area_selector.select_area()

    def update_off_variations(self, event=None):
        """Update the offensive stat variations dropdown based on selected stat"""
        selected_stat = self.off_stat.get()
        if selected_stat:
            variations = get_stat_variations(selected_stat)
            self.off_var_dropdown['values'] = variations
            if variations:
                self.off_var.set(variations[0])  # Select first variation by default
        else:
            self.off_var_dropdown['values'] = []
            self.off_var.set("")

    def update_def_variations(self, event=None):
        """Update the defensive stat variations dropdown based on selected stat"""
        selected_stat = self.def_stat.get()
        if selected_stat:
            variations = get_stat_variations(selected_stat)
            self.def_var_dropdown['values'] = variations
            if variations:
                self.def_var.set(variations[0])  # Select first variation by default
        else:
            self.def_var_dropdown['values'] = []
            self.def_var.set("")

    def start_automation(self):
        """Start the arrival skill automation"""
        # Check if another tool is running
        if not self.main_window.set_running_tool("Arrival Skill"):
            return

        # Check if at least one stat is specified
        if not self.off_stat.get() and not self.def_stat.get():
            messagebox.showerror("Error", "Please specify at least one stat to look for.")
            self.main_window.clear_running_tool()
            return

        # Prepare desired stats
        desired_stats = {
            'offensive': [],
            'defensive': []
        }

        # Add offensive stat if specified
        stat_name = self.off_stat.get()
        if stat_name:
            variation = self.off_var.get()
            if not variation:
                messagebox.showerror("Error", f"Please select a minimum value for {stat_name}.")
                self.main_window.clear_running_tool()
                return

            # Extract numeric value from the variation
            value_match = re.search(r'(\d+)', variation)
            if value_match:
                off_val = int(value_match.group(1))
                desired_stats['offensive'].append((stat_name, off_val, variation))
                self.main_window.update_status(f"Looking for {stat_name} with minimum value {variation}")

        # Add defensive stat if specified
        stat_name = self.def_stat.get()
        if stat_name:
            variation = self.def_var.get()
            if not variation:
                messagebox.showerror("Error", f"Please select a minimum value for {stat_name}.")
                self.main_window.clear_running_tool()
                return

            # Extract numeric value from the variation
            value_match = re.search(r'(\d+)', variation)
            if value_match:
                def_val = int(value_match.group(1))
                desired_stats['defensive'].append((stat_name, def_val, variation))
                self.main_window.update_status(f"Looking for {stat_name} with minimum value {variation}")

        # Start automation
        if self.automation.start(desired_stats):
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.main_window.update_status("Arrival skill automation started")
        else:
            self.main_window.clear_running_tool()

    def stop_automation(self):
        """Stop the arrival skill automation"""
        self.automation.stop()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.main_window.clear_running_tool()
        self.main_window.update_status("Arrival skill automation stopped")

    def emergency_stop(self):
        """Emergency stop the automation"""
        self.automation.emergency_stop()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.main_window.clear_running_tool()
