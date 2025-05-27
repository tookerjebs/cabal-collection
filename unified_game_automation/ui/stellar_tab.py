# Stellar System tab UI
# Ported from main.py stellar system functionality

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import mouse
from data.stellar_data import get_stellar_options
from automation.stellar_automation import StellarAutomation

class StellarTab:
    def __init__(self, parent_frame, main_window):
        """Initialize the Stellar System tab"""
        self.parent_frame = parent_frame
        self.main_window = main_window

        # Automation components
        self.automation = StellarAutomation(
            main_window.game_connector,
            main_window.ocr_engine,
            main_window.update_status
        )

        # UI state
        self.area = None
        self.imprint_button_coords = None

        # Create UI
        self.create_ui()

    def create_ui(self):
        """Create the stellar system UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instructions = (
            "STEPS:\n"
            "1) Press 'Set Imprint Button' and click on the Imprint button in game\n"
            "2) Press 'Define Area' and select the OCR area\n"
            "3) Select Option name from available options\n"
            "4) Enter minimum value (always enabled)\n"
            "5) Press 'Start' - automation will begin!"
        )
        instruction_label = ttk.Label(main_frame, text=instructions, font=("Arial", 9))
        instruction_label.pack(pady=(0, 10))

        # Button coordinates section
        coord_frame = ttk.LabelFrame(main_frame, text="Button Coordinates", padding="5")
        coord_frame.pack(fill=tk.X, pady=(0, 10))

        # Imprint button coordinates
        imprint_frame = ttk.Frame(coord_frame)
        imprint_frame.pack(fill=tk.X, pady=2)

        ttk.Label(imprint_frame, text="Imprint Button:").pack(side=tk.LEFT)
        self.imprint_coord_var = tk.StringVar(value="Not set")
        ttk.Label(imprint_frame, textvariable=self.imprint_coord_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(imprint_frame, text="Set Imprint Button", command=self.set_imprint_button).pack(side=tk.RIGHT)

        # Option selection section
        option_frame = ttk.LabelFrame(main_frame, text="Option Configuration", padding="5")
        option_frame.pack(fill=tk.X, pady=(0, 10))

        # Option name selection
        name_frame = ttk.Frame(option_frame)
        name_frame.pack(fill=tk.X, pady=2)

        ttk.Label(name_frame, text="Option name:").pack(side=tk.LEFT)
        self.combo_option_name = ttk.Combobox(name_frame, values=get_stellar_options(), state="readonly", width=20)
        self.combo_option_name.pack(side=tk.LEFT, padx=(5, 0))

        # Minimum value (always enabled as per requirements)
        value_frame = ttk.Frame(option_frame)
        value_frame.pack(fill=tk.X, pady=2)

        ttk.Label(value_frame, text="Minimum value:").pack(side=tk.LEFT)
        self.entry_option_min_value = ttk.Entry(value_frame, width=10)
        self.entry_option_min_value.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(value_frame, text="(leave empty to ignore)", font=("Arial", 8), foreground="gray").pack(side=tk.LEFT, padx=(5, 0))

        # Visual effect delay section
        effect_frame = ttk.LabelFrame(main_frame, text="Visual Effect Settings", padding="5")
        effect_frame.pack(fill=tk.X, pady=(0, 10))

        # Explanation text
        explanation_text = (
            "When rerolling, visual effects can interfere with OCR.\n"
            "This delay waits for effects to appear, then clicks the 'close' button to clear them.\n"
            "Adjust timing if effects last longer/shorter on your system."
        )
        explanation_label = ttk.Label(effect_frame, text=explanation_text, font=("Arial", 8), foreground="gray")
        explanation_label.pack(pady=(0, 5))

        # Delay setting
        delay_frame = ttk.Frame(effect_frame)
        delay_frame.pack(fill=tk.X, pady=2)

        ttk.Label(delay_frame, text="Effect clear delay:").pack(side=tk.LEFT)
        self.entry_effect_delay = ttk.Entry(delay_frame, width=8)
        self.entry_effect_delay.pack(side=tk.LEFT, padx=(5, 0))
        self.entry_effect_delay.insert(0, "1000")  # Default 1000ms = 1 second
        ttk.Label(delay_frame, text="ms (1000ms = 1 second)", font=("Arial", 8), foreground="gray").pack(side=tk.LEFT, padx=(5, 0))

        # Area definition
        area_frame = ttk.Frame(main_frame)
        area_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_define_area = ttk.Button(area_frame, text="Define Area", command=self.define_area)
        self.btn_define_area.pack()

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_start = ttk.Button(control_frame, text="Start", command=self.start_automation, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_stop = ttk.Button(control_frame, text="Stop", command=self.stop_automation, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)

    def set_imprint_button(self):
        """Set the imprint button coordinates"""
        # Connect to game if needed
        if not self.main_window.game_connector.is_connected():
            if not self.main_window.game_connector.connect_to_game():
                messagebox.showerror("Error", "Could not connect to the game window. Make sure the game is running.")
                return

        messagebox.showinfo(
            "Instruction",
            "Click on the 'Imprint' button in the game window.\n"
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
                    self.imprint_button_coords = (rel_x, rel_y)
                    self.automation.set_imprint_button(self.imprint_button_coords)
                    self.imprint_coord_var.set(f"({rel_x}, {rel_y})")
                    self.main_window.update_status(f"Imprint button set at ({rel_x}, {rel_y})")
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
            self.main_window.update_status(f"Area defined: {area}")

        # Use the shared area selector
        if not hasattr(self.main_window, 'area_selector'):
            from core.area_selector import AreaSelector
            self.main_window.area_selector = AreaSelector(self.main_window.root, area_callback)
        else:
            self.main_window.area_selector.callback = area_callback

        self.main_window.area_selector.select_area()

    def start_automation(self):
        """Start the stellar automation"""
        # Check if another tool is running
        if not self.main_window.set_running_tool("Stellar System"):
            return

        # Get configuration
        option_name = self.combo_option_name.get().strip()
        option_min_value = self.entry_option_min_value.get().strip()
        effect_delay = self.entry_effect_delay.get().strip()

        if not option_name:
            messagebox.showwarning("Missing Option", "Please select an option name.")
            self.main_window.clear_running_tool()
            return

        # Validate effect delay
        try:
            effect_delay_ms = int(effect_delay) if effect_delay else 1000
            if effect_delay_ms < 0:
                effect_delay_ms = 1000
        except ValueError:
            effect_delay_ms = 1000

        # Set the effect delay in automation
        self.automation.set_effect_delay(effect_delay_ms)

        # Start automation
        if self.automation.start(option_name, option_min_value):
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.main_window.update_status("Stellar automation started")
        else:
            self.main_window.clear_running_tool()

    def stop_automation(self):
        """Stop the stellar automation"""
        self.automation.stop()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.main_window.clear_running_tool()
        self.main_window.update_status("Stellar automation stopped")

    def emergency_stop(self):
        """Emergency stop the automation"""
        self.automation.emergency_stop()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.main_window.clear_running_tool()
