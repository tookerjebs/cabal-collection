# Main window for the Collection Automation Tool

import tkinter as tk
from tkinter import ttk
import keyboard
from core.game_connector import GameConnector
from ui.collection_tab import CollectionTab

class MainWindow:
    def __init__(self):
        """Initialize the main window"""
        self.root = tk.Tk()
        self.root.title("Collection Automation Tool")
        self.root.geometry("400x650")
        self.root.attributes("-topmost", True)

        # Track if automation is currently running
        self.automation_running = False

        # Initialize status variable first
        self.status_var = tk.StringVar(value="Initializing...")

        # Shared components (after status_var is created)
        self.game_connector = GameConnector(self.update_status)

        # Set up emergency kill switch (ESC key)
        keyboard.add_hotkey('esc', self.emergency_stop)

        # Create UI
        self.create_ui()

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_ui(self):
        """Create the main UI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Auto-connect to game and show status
        self.auto_connect_to_game()

        # Create collection tab directly (no notebook needed)
        self.collection_tab = CollectionTab(main_frame, self)

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
        emergency_label = ttk.Label(emergency_frame, text="ESC = Emergency Stop",
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

    def set_automation_running(self, running):
        """Set automation running state"""
        self.automation_running = running

    def is_automation_running(self):
        """Check if automation is currently running"""
        return self.automation_running

    def emergency_stop(self):
        """Emergency stop triggered by ESC key"""
        if self.automation_running:
            self.update_status("EMERGENCY STOP - Automation stopped!")
            self.collection_tab.emergency_stop()
            self.set_automation_running(False)

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
