import tkinter as tk
from tkinter import messagebox
import pyautogui
import pytesseract
import time
import re
import os
import datetime
import sys

from tkinter import ttk
import threading
from pywinauto import Application
import win32gui
import win32con
import mouse
import keyboard

base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
tesseract_path = os.path.join(base_path, "Tesseract", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = tesseract_path


class GameConnector:
    def __init__(self, status_callback=None):
        """
        Initialize the game connector for direct window clicking
        """
        self.game_window = None
        self.status_callback = status_callback

    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)

    def connect_to_game(self):
        """
        Connect to the game window by class name (most reliable method)
        Returns: bool: True if connection successful, False otherwise
        """
        try:
            app = Application()
            app.connect(class_name="D3D Window")

            # Get all D3D Windows and find the one that's likely the game
            windows = app.windows(class_name="D3D Window")

            # If there's only one D3D Window, use it
            if len(windows) == 1:
                self.game_window = windows[0]
            # If there are multiple, try to find the right one
            elif len(windows) > 1:
                # First try to find one with game-related keywords in the title
                for window in windows:
                    window_text = window.window_text().lower()
                    if any(keyword in window_text for keyword in ["stellar", "game", "cabal"]):
                        self.game_window = window
                        break
                # If that fails, use the first visible one
                else:
                    for window in windows:
                        if window.is_visible():
                            self.game_window = window
                            break
                    # If all else fails, use the first one
                    else:
                        self.game_window = windows[0]
            else:
                raise Exception("No D3D Window found")

            # Verify connection
            if self.game_window.is_visible() and self.game_window.is_enabled():
                return True
            else:
                raise Exception("Found window but it's not visible or enabled")

        except Exception as e:
            self.update_status(f"Could not connect to the game. Make sure it's running. Error: {str(e)}")
            return False

    def click_at_position(self, coords, adjust_for_client_area=True):
        """
        Click at the specified coordinates in the game window using direct Windows messages
        This method sends clicks directly without moving the mouse cursor

        Args:
            coords: Tuple of (x, y) coordinates relative to the window
            adjust_for_client_area: Whether to adjust coordinates for client area (title bar offset)
        """
        if not self.game_window:
            return False

        try:
            # If we need to adjust for client area (title bar and borders)
            if adjust_for_client_area:
                # Get the offset between window and client area
                offset = self.get_window_client_offset()

                if offset:
                    # Adjust the coordinates by subtracting the offset
                    # This converts window coordinates to client coordinates
                    adjusted_coords = (coords[0] - offset[0], coords[1] - offset[1])
                    self.game_window.click(coords=adjusted_coords)
                    return True

            # If no adjustment needed or offset couldn't be determined
            self.game_window.click(coords=coords)
            return True
        except Exception as e:
            self.update_status(f"Click failed: {str(e)}")
            return False

    def get_window_rect(self):
        """Get the rectangle of the game window"""
        if not self.game_window:
            return None
        try:
            return self.game_window.rectangle()
        except Exception:
            return None

    def get_client_rect(self):
        """
        Get the client rectangle of the game window.
        This is the area inside the window borders and title bar.
        """
        if not self.game_window:
            return None
        try:
            # Get the window handle
            hwnd = self.game_window.handle

            # Get client rectangle in client coordinates (0,0 is top-left of client area)
            client_rect = win32gui.GetClientRect(hwnd)

            # Convert client coordinates (0,0) to screen coordinates
            client_pos = win32gui.ClientToScreen(hwnd, (0, 0))

            # Return as (left, top, right, bottom) tuple
            return (
                client_pos[0],
                client_pos[1],
                client_pos[0] + client_rect[2],
                client_pos[1] + client_rect[3]
            )
        except Exception as e:
            self.update_status(f"Failed to get client rect: {str(e)}")
            return None

    def get_window_client_offset(self):
        """
        Calculate the offset between window coordinates and client coordinates.
        Returns (offset_x, offset_y) tuple or None if not available.
        """
        if not self.game_window:
            return None

        try:
            # Get window and client rectangles
            window_rect = self.get_window_rect()
            client_rect = self.get_client_rect()

            if not window_rect or not client_rect:
                return None

            # Calculate offsets
            offset_x = client_rect[0] - window_rect.left
            offset_y = client_rect[1] - window_rect.top

            return (offset_x, offset_y)
        except Exception as e:
            self.update_status(f"Failed to calculate window-client offset: {str(e)}")
            return None

    def convert_to_window_coords(self, screen_x, screen_y):
        """Convert screen coordinates to window-relative coordinates"""
        if not self.game_window:
            return (screen_x, screen_y, False)

        try:
            rect = self.game_window.rectangle()
            rel_x = screen_x - rect.left
            rel_y = screen_y - rect.top
            return (rel_x, rel_y, True)
        except Exception:
            return (screen_x, screen_y, False)

    def is_connected(self):
        """Check if connected to game window"""
        return self.game_window is not None


class OverlayWindow(tk.Toplevel):
    def __init__(self, master, x, y, w, h, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.config(bg="black")
        self.attributes("-transparentcolor", "black")

        self.geometry(f"{w}x{h}+{x}+{y}")

        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_rectangle(
            0, 0, w, h,
            outline="red",
            width=2,
            fill=""
        )

    def close_overlay(self):
        self.destroy()


class StellarApp:
    def __init__(self, root):
        root.geometry("520x500")  # Increased height for new button
        self.delay_ms = 500
        self.ping_ms = 50
        self.root = root
        self.root.title("Stellar OCR - v1 (with Direct Clicking)")

        self.root.attributes("-topmost", True)

        self.overlay_window = None
        self.area = None
        self.running = False

        self.wrong_read_counter = 0
        self.loop_in_progress = False

        # Game connector for direct clicking
        self.game_connector = GameConnector(self.log_info)
        self.imprint_button_coords = None

        self.exceptions_for_penetration = [
            "ignore",
            "cancel"
        ]

        self.log_file_path = self.create_log_file()
        self.log_info(f"Application start - log saved in: {self.log_file_path}")

        # Set up emergency kill switch (ESC key)
        keyboard.add_hotkey('esc', self.emergency_stop)

        label_info = tk.Label(
            root,
            text=(
                "STEPS:\n"
                "1) Press 'Set Imprint Button' and click on the Imprint button in game\n"
                "2) Press 'Define area' and select the OCR area\n"
                "3) Select Option name from available options\n"
                "4) Type in minimum value or disable it\n"
                "5) Press 'Start' - clicks will be sent directly to the game!\n"
            )
        )
        label_info.pack(pady=5)

        # Button coordinate setup section
        frame_coords = tk.Frame(root)
        frame_coords.pack(pady=5)

        self.imprint_coord_var = tk.StringVar(value="Not set")
        label_imprint_coord = tk.Label(frame_coords, text="Imprint Button:")
        label_imprint_coord.grid(row=0, column=0, sticky="e", padx=5)

        label_coord_display = tk.Label(frame_coords, textvariable=self.imprint_coord_var, fg="blue")
        label_coord_display.grid(row=0, column=1, sticky="w", padx=5)

        self.btn_set_imprint = tk.Button(frame_coords, text="Set Imprint Button", command=self.set_imprint_button)
        self.btn_set_imprint.grid(row=0, column=2, padx=5)

        frame_phrases = tk.Frame(root)
        frame_phrases.pack(pady=5)

        label_optionName = tk.Label(frame_phrases, text="Option name")
        label_optionName.grid(row=0, column=0, padx=5, sticky="e")

        self.optionName_options = [
            "PVE Penetration",
            "PVE Critical DMG",
            "All Attack UP",
            "Penetration",
            "Critical DMG.",
            "Ignore Accuracy"
        ]

        self.combo_optionName = ttk.Combobox(
            frame_phrases,
            values=self.optionName_options,
            state="readonly",
            width=22
        )
        self.combo_optionName.current(0)
        self.combo_optionName.grid(row=0, column=1, padx=5)

        label_optionMinValue = tk.Label(frame_phrases, text="Option min value:")
        label_optionMinValue.grid(row=1, column=0, padx=5, sticky="e")

        vcmd_optionMinValue = (root.register(self.validate_digits), '%P')
        self.entry_optionMinValue = tk.Entry(
            frame_phrases, width=25,
            validate='key', validatecommand=vcmd_optionMinValue,
            state="normal"
        )
        self.entry_optionMinValue.grid(row=1, column=1, padx=5)

        self.enable_optionMinValue_var = tk.BooleanVar(value=True)
        self.check_optionMinValue = tk.Checkbutton(
            frame_phrases,
            text="Enable min value",
            variable=self.enable_optionMinValue_var,
            command=self.toggle_optionMinValue
        )
        self.check_optionMinValue.grid(row=1, column=2, padx=5, sticky="w")

        label_ms = tk.Label(frame_phrases, text="MS (Ping):")
        label_ms.grid(row=2, column=0, padx=5, sticky="e")

        vcmd_ms = (root.register(self.validate_digits), '%P')
        self.entry_ms = tk.Entry(
            frame_phrases, width=25,
            validate='key', validatecommand=vcmd_ms,
            state="normal"
        )
        self.entry_ms.insert(0, "50")
        self.entry_ms.grid(row=2, column=1, padx=5)

        self.btn_define_area = tk.Button(root, text="Define area", command=self.define_area)
        self.btn_define_area.pack(pady=5)

        self.btn_start = tk.Button(root, text="Start", command=self.start, state=tk.DISABLED)
        self.btn_start.pack(pady=5)

        self.btn_stop = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED)
        self.btn_stop.pack(pady=5)

        # Emergency stop info
        emergency_label = tk.Label(root, text="🚨 Emergency Stop: Press ESC key anytime",
                                  fg="red", font=("Arial", 9, "bold"))
        emergency_label.pack(pady=2)

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    @staticmethod
    def validate_digits(new_value):
        return new_value.isdigit() or new_value == ""

    def toggle_optionMinValue(self):
        if self.enable_optionMinValue_var.get():
            self.entry_optionMinValue.config(state="normal")
        else:
            self.entry_optionMinValue.config(state="disabled")

    def set_imprint_button(self):
        """Record the coordinates of the Imprint button in the game"""
        self.log_info("Setting up Imprint button coordinates...")

        # Connect to game if needed
        if not self.game_connector.is_connected():
            if not self.game_connector.connect_to_game():
                messagebox.showerror("Error", "Could not connect to the game window. Make sure the game is running.")
                return

        messagebox.showinfo(
            "Instruction",
            "Click on the 'Imprint' button in the game window.\n"
            "The coordinates will be captured automatically."
        )

        self.root.config(cursor="crosshair")  # Change cursor to indicate click mode

        # Function to capture mouse click
        def capture_click():
            # Wait for next mouse click
            mouse.wait(button='left')

            # Get mouse position
            x, y = mouse.get_position()

            # Get game window position and convert to window-relative coordinates
            rel_x, rel_y, success = self.game_connector.convert_to_window_coords(x, y)

            if success:
                # Store coordinates
                self.imprint_button_coords = (rel_x, rel_y)
                self.imprint_coord_var.set(f"({rel_x}, {rel_y})")

                self.log_info(f"Imprint button set at: ({rel_x}, {rel_y})")
                messagebox.showinfo("Success", f"Imprint button coordinates set: ({rel_x}, {rel_y})")
            else:
                self.log_info("Failed to get game window position")
                messagebox.showerror("Error", "Failed to get game window position")

            # Reset cursor
            self.root.config(cursor="")

        # Start the capture in a thread so it doesn't block the UI
        thread = threading.Thread(target=capture_click, daemon=True)
        thread.start()

    @staticmethod
    def create_log_file():
        home_dir = os.path.expanduser("~")
        log_dir = os.path.join(home_dir, "stellarlink_logs")
        os.makedirs(log_dir, exist_ok=True)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_name = f"{now_str}.txt"
        log_path = os.path.join(log_dir, base_name)

        version = 2
        while os.path.exists(log_path):
            log_path = os.path.join(log_dir, f"{now_str}_v{version}.txt")
            version += 1

        return log_path

    def log_info(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] INFO: {message}\n"
        with open(self.log_file_path, mode="a", encoding="utf-8") as f:
            f.write(line)

    def log_error(self, exception):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] ERROR: {type(exception).__name__} - {str(exception)}\n"
        with open(self.log_file_path, mode="a", encoding="utf-8") as f:
            f.write(line)

    def define_area(self):
        """Allow user to select a region of the screen with visual feedback"""
        # Close any existing overlay
        if hasattr(self, "overlay_window") and self.overlay_window is not None:
            self.overlay_window.close_overlay()
            self.overlay_window = None

        # Create a fullscreen transparent overlay
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.2)
        overlay.attributes('-topmost', True)
        overlay.configure(bg='grey')

        # Variables for selection
        start_x, start_y = 0, 0
        rect = None

        # Handle mouse events
        def on_press(event):
            nonlocal start_x, start_y, rect
            start_x, start_y = event.x, event.y
            rect = tk.Canvas(overlay, bg='red', height=1, width=1)
            rect.place(x=start_x, y=start_y)

        def on_drag(event):
            nonlocal rect, start_x, start_y
            width = abs(event.x - start_x)
            height = abs(event.y - start_y)
            x = min(start_x, event.x)
            y = min(start_y, event.y)
            rect.place(x=x, y=y, width=width, height=height)

        def on_release(event):
            left = min(start_x, event.x)
            top = min(start_y, event.y)
            right = max(start_x, event.x)
            bottom = max(start_y, event.y)
            width = right - left
            height = bottom - top

            # Validate area dimensions
            if width <= 0 or height <= 0:
                messagebox.showerror("Error", "Invalid area selection (width or height <= 0).")
                self.log_info("Area definition error - zero or negative dimension.")
                overlay.destroy()
                return

            # Store the area in the format expected by pyautogui.screenshot
            self.area = (left, top, width, height)
            self.log_info(f"Defined area: {self.area}")

            # Enable the start button
            self.btn_start.config(state=tk.NORMAL)

            # Create the visual overlay to show the selected area
            self.overlay_window = OverlayWindow(self.root, left, top, width, height)

            messagebox.showinfo("Success", f"Area defined: ({left}, {top}, {width}, {height})")
            overlay.destroy()

        # Bind events
        overlay.bind("<ButtonPress-1>", on_press)
        overlay.bind("<B1-Motion>", on_drag)
        overlay.bind("<ButtonRelease-1>", on_release)
        overlay.bind("<Escape>", lambda _: overlay.destroy())

        # Show instruction
        messagebox.showinfo(
            "Area Selection",
            "Click and drag to select the OCR area.\n"
            "Press ESC to cancel."
        )



    def start(self):
        if not self.area:
            messagebox.showwarning("Missing area definition", "Fix area definition first!")
            return

        if not self.imprint_button_coords:
            messagebox.showwarning("Missing button coordinates", "Please set the Imprint button coordinates first!")
            return

        # Connect to game if not already connected
        if not self.game_connector.is_connected():
            if not self.game_connector.connect_to_game():
                messagebox.showerror("Error", "Could not connect to the game window. Make sure the game is running.")
                return

        raw_optionName = self.combo_optionName.get().strip()
        if self.enable_optionMinValue_var.get():
            raw_optionMinValue = self.entry_optionMinValue.get().strip()
        else:
            raw_optionMinValue = ""

        self.optionName = re.sub(r"\s+", "", raw_optionName).lower()
        self.optionMinValue = re.sub(r"\s+", "", raw_optionMinValue).lower()

        try:
            self.ping_ms = int(self.entry_ms.get().strip() or 50)
        except ValueError:
            self.ping_ms = 50

        self.delay_ms = 800 + self.ping_ms  # Give OCR more time to process after clicks

        self.log_info(f"Start OCR - optionName={self.optionName}, optionMinValue={self.optionMinValue} (enabled={self.enable_optionMinValue_var.get()})")

        self.running = True
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_start.config(state=tk.DISABLED)
        self.root.after(3000, self.loop_ocr)

    def stop(self):
        self.running = False
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_start.config(state=tk.NORMAL)
        self.log_info("Stop OCR - end of loop.")

    def emergency_stop(self):
        """Emergency stop triggered by ESC key"""
        if self.running:
            self.stop()
            self.log_info("🚨 EMERGENCY STOP - ESC key pressed!")
            # Bring window to front
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)

    @staticmethod
    def numeric_compare(optionMinValue_int, text):
        numbers_found = re.findall(r"\d+", text)
        for num_str in numbers_found:
            val = int(num_str)
            if val >= optionMinValue_int:
                return True
        return False

    def loop_ocr(self):
        if self.loop_in_progress:
            self.log_info("loop_ocr called but loop_in_progress is True - skipping re-entrance.")
            return

        if not self.running:
            return

        self.loop_in_progress = True

        try:
            x, y, w, h = self.area
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            text = pytesseract.image_to_string(screenshot)

            text = re.sub(r"\s+", "", text).lower()
            text = re.sub(r'([A-Za-z]+)4(\d)', r'\1+\2', text)

            if "stellarforce4" in text:
                text = text.replace("stellarforce4", "stellarforce+")

            self.log_info(f"OCR text: {text}")
            print(text)

            numbers_found = re.findall(r"\d+", text)
            print("self.wrong_read_counter:", self.wrong_read_counter)
            if len(numbers_found) != 1:
                self.wrong_read_counter += 1
                if self.wrong_read_counter > 2:
                    messagebox.showinfo(
                        "Error",
                        "Found wrong amount of numbers - stopping.\n"
                        "Make sure that you've defined area correctly, please restart application"
                    )
                    self.log_info("More than one (or zero) numbers found in text. Stopping.")
                    self.stop()
                    self.loop_in_progress = False
                    return
                else:
                    self.loop_in_progress = False
                    self.root.after(700 + self.ping_ms, self.loop_ocr)  # Slightly longer delay for wrong reads
                    return

            self.wrong_read_counter = 0

            found_optionName = False
            if self.optionName:
                if self.optionName in text:
                    if self.optionName == "penetration":
                        if any(exc in text for exc in self.exceptions_for_penetration):
                            self.log_info("Found 'penetration' but ignoring special exception phrase.")
                        else:
                            found_optionName = True
                    else:
                        found_optionName = True

            found_optionMinValue = False
            if self.optionMinValue:
                if self.optionMinValue.isdigit():
                    p2_int = int(self.optionMinValue)
                    found_optionMinValue = self.numeric_compare(p2_int, text)
                else:
                    found_optionMinValue = (self.optionMinValue in text)

            if found_optionName and self.enable_optionMinValue_var.get() and found_optionMinValue:
                messagebox.showinfo("Found it!", "Hopefully that's what you have been looking for")
                self.log_info("Both found - finish")
                self.stop()
            elif found_optionName and not self.enable_optionMinValue_var.get():
                messagebox.showinfo("Found it!", "Option found, minimum value disabled.")
                self.log_info("Option found - finish (minimum value disabled).")
                self.stop()
            else:
                # Use direct window clicking instead of pyautogui
                self.game_connector.click_at_position(self.imprint_button_coords)

                # Wait between clicks - balance between speed and OCR accuracy
                time.sleep(0.3 + (self.ping_ms / 1000))  # Give UI time to update between clicks

                self.game_connector.click_at_position(self.imprint_button_coords)

                self.loop_in_progress = False
                self.root.after(self.delay_ms, self.loop_ocr)
                return

        except Exception as e:
            self.log_error(e)
            messagebox.showerror("Error", f"An error occurred:\n{e}")
            self.stop()

        self.loop_in_progress = False

    def on_closing(self):
        """Clean up when closing the application"""
        keyboard.unhook_all()  # Remove all keyboard hooks
        self.root.destroy()


def main():
    root = tk.Tk()
    app = StellarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
