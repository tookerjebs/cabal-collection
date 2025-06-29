# Collection tab UI

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import mouse
from data.collection_data import get_collection_buttons
from automation.collection_automation import CollectionAutomation

class CollectionTab:
    def __init__(self, parent_frame, main_window):
        """Initialize the Collection tab"""
        self.parent_frame = parent_frame
        self.main_window = main_window

        # Automation components
        self.automation = CollectionAutomation(
            main_window.game_connector,
            main_window.update_status
        )

        # UI state variables
        self.button_coord_vars = {}
        self.areas_defined = {
            'collection_tabs': False,
            'dungeon_list': False,
            'collection_items': False
        }
        
        # Create UI
        self.create_ui()
        
        # Set default delay multiplier
        self.automation.set_delay_multiplier(1.0)

    def create_ui(self):
        """Create the collection UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instructions = (
            "COLLECTION AUTO-FILL STEPS:\n"
            "1) Define detection areas for red dots (Collection Tabs, Dungeon List, Items)\n"
            "2) Set coordinates for action buttons (Auto Refill, Register, Yes)\n"
            "3) Set coordinates for pagination buttons (Page 2, 3, 4, Arrow Right)\n"
            "4) Press 'Start' - automation will scan for red dots and auto-fill collections!\n\n"
            "The tool will detect red dots, navigate through all pages, and scroll through items automatically."
        )
        instruction_label = ttk.Label(main_frame, text=instructions, font=("Arial", 9))
        instruction_label.pack(pady=(0, 10))

        # Red Dot Detection Areas Section
        area_frame = ttk.LabelFrame(main_frame, text="Red Dot Detection Areas", padding="5")
        area_frame.pack(fill=tk.X, pady=(0, 10))

        # Collection tabs area
        tabs_area_frame = ttk.Frame(area_frame)
        tabs_area_frame.pack(fill=tk.X, pady=2)
        ttk.Button(tabs_area_frame, text="Define Collection Tabs Area", 
                  command=self.define_collection_tabs_area).pack(side=tk.LEFT)
        ttk.Label(tabs_area_frame, text="Area containing Dungeon, World, Special, Boss tabs", 
                 font=("Arial", 8)).pack(side=tk.LEFT, padx=(10, 0))
        self.tabs_area_status = ttk.Label(tabs_area_frame, text="❌ Not defined", foreground="red")
        self.tabs_area_status.pack(side=tk.RIGHT)

        # Dungeon list area
        dungeon_area_frame = ttk.Frame(area_frame)
        dungeon_area_frame.pack(fill=tk.X, pady=2)
        ttk.Button(dungeon_area_frame, text="Define Dungeon List Area", 
                  command=self.define_dungeon_list_area).pack(side=tk.LEFT)
        ttk.Label(dungeon_area_frame, text="Area containing dungeon/world/special/boss entries", 
                 font=("Arial", 8)).pack(side=tk.LEFT, padx=(10, 0))
        self.dungeon_area_status = ttk.Label(dungeon_area_frame, text="❌ Not defined", foreground="red")
        self.dungeon_area_status.pack(side=tk.RIGHT)

        # Collection items area
        items_area_frame = ttk.Frame(area_frame)
        items_area_frame.pack(fill=tk.X, pady=2)
        ttk.Button(items_area_frame, text="Define Collection Items Area", 
                  command=self.define_collection_items_area).pack(side=tk.LEFT)
        ttk.Label(items_area_frame, text="Area containing collection materials/items", 
                 font=("Arial", 8)).pack(side=tk.LEFT, padx=(10, 0))
        self.items_area_status = ttk.Label(items_area_frame, text="❌ Not defined", foreground="red")
        self.items_area_status.pack(side=tk.RIGHT)

        # Action Button Coordinates Section
        button_coord_frame = ttk.LabelFrame(main_frame, text="Action Button Coordinates", padding="5")
        button_coord_frame.pack(fill=tk.X, pady=(0, 10))

        # Create coordinate setting for each action button
        collection_buttons = get_collection_buttons()
        for button_key, button_name in collection_buttons.items():
            button_frame = ttk.Frame(button_coord_frame)
            button_frame.pack(fill=tk.X, pady=2)

            ttk.Label(button_frame, text=f"{button_name} Button:").pack(side=tk.LEFT)
            
            coord_var = tk.StringVar(value="Not set")
            self.button_coord_vars[button_key] = coord_var
            ttk.Label(button_frame, textvariable=coord_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Button(button_frame, text=f"Set {button_name}", 
                      command=lambda k=button_key, n=button_name: self.set_button_coordinate(k, n)).pack(side=tk.RIGHT)

        # Pagination Button Coordinates Section
        pagination_coord_frame = ttk.LabelFrame(main_frame, text="Pagination Button Coordinates", padding="5")
        pagination_coord_frame.pack(fill=tk.X, pady=(0, 10))

        # Create coordinate setting for each pagination button
        pagination_buttons = {
            "page_2": "Page 2", 
            "page_3": "Page 3",
            "page_4": "Page 4",
            "arrow_right": "Arrow Right"
        }
        
        for button_key, button_name in pagination_buttons.items():
            button_frame = ttk.Frame(pagination_coord_frame)
            button_frame.pack(fill=tk.X, pady=2)

            ttk.Label(button_frame, text=f"{button_name} Button:").pack(side=tk.LEFT)
            
            coord_var = tk.StringVar(value="Not set")
            self.button_coord_vars[button_key] = coord_var
            ttk.Label(button_frame, textvariable=coord_var, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
            
            ttk.Button(button_frame, text=f"Set {button_name}", 
                      command=lambda k=button_key, n=button_name: self.set_pagination_coordinate(k, n)).pack(side=tk.RIGHT)

        # Speed Settings Section
        speed_frame = ttk.LabelFrame(main_frame, text="Speed Settings", padding="5")
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Delay multiplier setting
        delay_frame = ttk.Frame(speed_frame)
        delay_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(delay_frame, text="Delay Multiplier:").pack(side=tk.LEFT)
        
        self.delay_var = tk.DoubleVar(value=1.0)  # Default 1.0x speed
        delay_spinbox = ttk.Spinbox(delay_frame, from_=0.0, to=5.0, increment=0.1, 
                                   textvariable=self.delay_var, width=8,
                                   command=self.update_delay_multiplier)
        delay_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        # Speed presets
        ttk.Button(delay_frame, text="Ultra Fast (0x)", 
                  command=lambda: self.set_delay_preset(0.0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(delay_frame, text="Fast (0.5x)", 
                  command=lambda: self.set_delay_preset(0.5)).pack(side=tk.LEFT, padx=2)
        ttk.Button(delay_frame, text="Normal (1x)", 
                  command=lambda: self.set_delay_preset(1.0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(delay_frame, text="Safe (2x)", 
                  command=lambda: self.set_delay_preset(2.0)).pack(side=tk.LEFT, padx=2)
        
        # Speed info
        speed_info = ttk.Label(speed_frame, 
                              text="0 = Ultra fast (no delays), 1 = Normal speed, 2+ = Slower/safer", 
                              font=("Arial", 8), foreground="gray")
        speed_info.pack(pady=(5, 0))

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_start = ttk.Button(control_frame, text="Start Collection Automation", 
                                   command=self.start_automation, style="Accent.TButton")
        self.btn_start.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_stop = ttk.Button(control_frame, text="Stop", command=self.stop_automation)
        self.btn_stop.pack(side=tk.LEFT)

    def define_collection_tabs_area(self):
        """Define the area containing all collection tabs"""
        def area_callback(area):
            """Callback when area is selected"""
            self.automation.set_collection_tabs_area(area)
            self.areas_defined['collection_tabs'] = True
            self.tabs_area_status.config(text="✅ Defined", foreground="green")
            self.main_window.update_status(f"Collection tabs area defined: {area}")

        # Use the shared area selector
        if not hasattr(self.main_window, 'area_selector'):
            from core.area_selector import AreaSelector
            self.main_window.area_selector = AreaSelector(self.main_window.root, area_callback)
        else:
            self.main_window.area_selector.callback = area_callback

        self.main_window.area_selector.select_area()

    def define_dungeon_list_area(self):
        """Define the area containing dungeon/world/special/boss list entries"""
        def area_callback(area):
            """Callback when area is selected"""
            self.automation.set_dungeon_list_area(area)
            self.areas_defined['dungeon_list'] = True
            self.dungeon_area_status.config(text="✅ Defined", foreground="green")
            self.main_window.update_status(f"Dungeon list area defined: {area}")

        # Use the shared area selector
        if not hasattr(self.main_window, 'area_selector'):
            from core.area_selector import AreaSelector
            self.main_window.area_selector = AreaSelector(self.main_window.root, area_callback)
        else:
            self.main_window.area_selector.callback = area_callback

        self.main_window.area_selector.select_area()

    def define_collection_items_area(self):
        """Define the area containing collection materials/items"""
        def area_callback(area):
            """Callback when area is selected"""
            self.automation.set_collection_items_area(area)
            self.areas_defined['collection_items'] = True
            self.items_area_status.config(text="✅ Defined", foreground="green")
            self.main_window.update_status(f"Collection items area defined: {area}")

        # Use the shared area selector
        if not hasattr(self.main_window, 'area_selector'):
            from core.area_selector import AreaSelector
            self.main_window.area_selector = AreaSelector(self.main_window.root, area_callback)
        else:
            self.main_window.area_selector.callback = area_callback

        self.main_window.area_selector.select_area()

    def set_button_coordinate(self, button_key, button_name):
        """Set coordinates for an action button"""
        # Connect to game if needed
        if not self.main_window.game_connector.is_connected():
            if not self.main_window.game_connector.connect_to_game():
                messagebox.showerror("Error", "Could not connect to the game window. Make sure the game is running.")
                return

        messagebox.showinfo(
            "Instruction",
            f"Click on the '{button_name}' button in the game window.\n"
            "The coordinates will be captured automatically."
        )

        # Change cursor to indicate click mode
        self.main_window.root.config(cursor="crosshair")

        def capture_click():
            """Capture the mouse click coordinates"""
            try:
                # Wait for mouse click
                mouse.wait(button='left')
                x, y = mouse.get_position()

                # Convert to window-relative coordinates
                rel_x, rel_y, success = self.main_window.game_connector.convert_to_window_coords(x, y)

                if success:
                    # Set coordinates in automation based on button type
                    if button_key == "auto_refill":
                        self.automation.set_auto_refill_button((rel_x, rel_y))
                    elif button_key == "register":
                        self.automation.set_register_button((rel_x, rel_y))
                    elif button_key == "yes":
                        self.automation.set_yes_button((rel_x, rel_y))
                    
                    self.button_coord_vars[button_key].set(f"({rel_x}, {rel_y})")
                    self.main_window.update_status(f"{button_name} button coordinates set at ({rel_x}, {rel_y})")
                else:
                    messagebox.showerror("Error", "Failed to convert coordinates")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to capture click: {str(e)}")
            finally:
                # Reset cursor
                self.main_window.root.config(cursor="")

        # Start capture in thread
        threading.Thread(target=capture_click, daemon=True).start()

    def set_pagination_coordinate(self, button_key, button_name):
        """Set coordinates for a pagination button"""
        # Connect to game if needed
        if not self.main_window.game_connector.is_connected():
            if not self.main_window.game_connector.connect_to_game():
                messagebox.showerror("Error", "Could not connect to the game window. Make sure the game is running.")
                return

        messagebox.showinfo(
            "Instruction",
            f"Click on the '{button_name}' button in the game window.\n"
            "The coordinates will be captured automatically."
        )

        # Change cursor to indicate click mode
        self.main_window.root.config(cursor="crosshair")

        def capture_click():
            """Capture the mouse click coordinates"""
            try:
                # Wait for mouse click
                mouse.wait(button='left')
                x, y = mouse.get_position()

                # Convert to window-relative coordinates
                rel_x, rel_y, success = self.main_window.game_connector.convert_to_window_coords(x, y)

                if success:
                    # Set coordinates in automation based on button type
                    if button_key == "page_2":
                        self.automation.set_page_2_button((rel_x, rel_y))
                    elif button_key == "page_3":
                        self.automation.set_page_3_button((rel_x, rel_y))
                    elif button_key == "page_4":
                        self.automation.set_page_4_button((rel_x, rel_y))
                    elif button_key == "arrow_right":
                        self.automation.set_arrow_right_button((rel_x, rel_y))
                    
                    self.button_coord_vars[button_key].set(f"({rel_x}, {rel_y})")
                    self.main_window.update_status(f"{button_name} button coordinates set at ({rel_x}, {rel_y})")
                else:
                    messagebox.showerror("Error", "Failed to convert coordinates")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to capture click: {str(e)}")
            finally:
                # Reset cursor
                self.main_window.root.config(cursor="")

        # Start capture in thread
        threading.Thread(target=capture_click, daemon=True).start()

    def update_delay_multiplier(self):
        """Update the delay multiplier in automation"""
        multiplier = self.delay_var.get()
        self.automation.set_delay_multiplier(multiplier)
        self.main_window.update_status(f"Delay multiplier set to {multiplier}x")

    def set_delay_preset(self, multiplier):
        """Set delay multiplier to a preset value"""
        self.delay_var.set(multiplier)
        self.automation.set_delay_multiplier(multiplier)
        speed_names = {0.0: "Ultra Fast", 0.5: "Fast", 1.0: "Normal", 2.0: "Safe"}
        speed_name = speed_names.get(multiplier, f"{multiplier}x")
        self.main_window.update_status(f"Speed set to {speed_name} ({multiplier}x)")

    def start_automation(self):
        """Start the collection automation"""
        # Check if automation is already running
        if self.main_window.is_automation_running():
            messagebox.showwarning("Already Running", "Collection automation is already running!")
            return

        # Start automation
        if self.automation.start():
            self.main_window.set_automation_running(True)
            
            # Update UI state
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")

    def stop_automation(self):
        """Stop the collection automation"""
        self.automation.stop()
        
        # Clear running state
        self.main_window.set_automation_running(False)
        
        # Update UI state
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    def emergency_stop(self):
        """Emergency stop the automation"""
        self.automation.emergency_stop()
        
        # Update UI state
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")