# Main tabbed window for the Unified Game Automation Tool
# Title: "Stellar and Arrival Skill Automation"

import tkinter as tk
from tkinter import ttk
import keyboard
from core.game_connector import GameConnector
from core.ocr_engine import OCREngine
from ui.stellar_tab import StellarTab
from ui.arrival_tab import ArrivalTab

class MainWindow:
    def __init__(self):
        """Initialize the main tabbed window"""
        self.root = tk.Tk()
        self.root.title("Stellar and Arrival Skill Automation")
        self.root.geometry("600x700")
        self.root.attributes("-topmost", True)

        # Track which tool is currently running (mutual exclusion)
        self.current_running_tool = None

        # Initialize status variable first
        self.status_var = tk.StringVar(value="Initializing...")

        # Shared components (after status_var is created)
        self.game_connector = GameConnector(self.update_status)
        self.ocr_engine = OCREngine(self.update_status)

        # Set up emergency kill switch (ESC key)
        keyboard.add_hotkey('esc', self.emergency_stop)

        # Create UI
        self.create_ui()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_ui(self):
        """Create the main UI with tabs"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Auto-connect to game and show status
        self.auto_connect_to_game()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Create tab frames
        arrival_frame = ttk.Frame(self.notebook)
        stellar_frame = ttk.Frame(self.notebook)

        # Add tabs to notebook (Arrival Skill first)
        self.notebook.add(arrival_frame, text="Arrival Skill")
        self.notebook.add(stellar_frame, text="Stellar System")

        # Create tab instances
        self.arrival_tab = ArrivalTab(arrival_frame, self)
        self.stellar_tab = StellarTab(stellar_frame, self)

        # Status display
        status_display_frame = ttk.Frame(main_frame)
        status_display_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(status_display_frame, text="Status:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.status_var.set("Ready")  # Update existing status_var instead of creating new one
        self.status_label = ttk.Label(status_display_frame, textvariable=self.status_var, font=("Arial", 9))
        self.status_label.pack(anchor=tk.W, pady=(2, 0))

        # Emergency stop info
        emergency_frame = ttk.Frame(main_frame)
        emergency_frame.pack(fill=tk.X, pady=(5, 0))
        emergency_label = ttk.Label(emergency_frame, text="🚨 Emergency Stop: Press ESC key anytime",
                                   foreground="red", font=("Arial", 9, "bold"))
        emergency_label.pack(anchor=tk.W)

    def auto_connect_to_game(self):
        """Automatically connect to the game and show connection status"""
        if self.game_connector.connect_to_game():
            # Get game window info for display
            window_rect = self.game_connector.get_window_rect()
            if window_rect:
                window_info = f"Connected to game window ({window_rect.width}x{window_rect.height})"
            else:
                window_info = "Connected to game window"
            self.update_status(window_info)
        else:
            self.update_status("⚠️ Game not found - make sure the game is running before starting automation")

    def update_status(self, message):
        """Update the status display"""
        self.status_var.set(message)
        print(f"Status: {message}")  # Also print to console for debugging

    def set_running_tool(self, tool_name):
        """Set which tool is currently running (mutual exclusion)"""
        if self.current_running_tool is not None and self.current_running_tool != tool_name:
            self.update_status(f"Cannot start {tool_name}: {self.current_running_tool} is already running")
            return False

        self.current_running_tool = tool_name
        return True

    def clear_running_tool(self):
        """Clear the currently running tool"""
        self.current_running_tool = None

    def emergency_stop(self):
        """Emergency stop triggered by ESC key"""
        if self.current_running_tool:
            self.update_status(f"🚨 EMERGENCY STOP - {self.current_running_tool} stopped!")

            # Stop whichever tool is running
            if self.current_running_tool == "Stellar System":
                self.stellar_tab.emergency_stop()
            elif self.current_running_tool == "Arrival Skill":
                self.arrival_tab.emergency_stop()

            self.clear_running_tool()

            # Bring window to front
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)

    def on_closing(self):
        """Clean up when closing the application"""
        keyboard.unhook_all()  # Remove all keyboard hooks
        self.root.destroy()

    def run(self):
        """Start the application"""
        self.root.mainloop()
