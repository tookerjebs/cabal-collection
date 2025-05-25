import tkinter as tk
from tkinter import messagebox
import pyautogui
import pytesseract
import time
import re
import os
import datetime
import sys
from pynput import mouse
from tkinter import ttk

base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
tesseract_path = os.path.join(base_path, "Tesseract", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = tesseract_path


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
        self.phrase1 = None
        self.phrase2 = None
        self.delay_ms = 500
        self.ping_ms = 50
        self.root = root
        self.root.title("Stellar OCR - v1")

        self.root.attributes("-topmost", True)

        self.overlay_window = None
        self.area = None
        self.area_start = None
        self.area_end = None
        self.click_counter = 0
        self.listener = None
        self.running = False

        self.wrong_read_counter = 0
        self.loop_in_progress = False

        self.exceptions_for_penetration = [
            "ignore",
            "cancel"
        ]

        self.log_file_path = self.create_log_file()
        self.log_info(f"Application start - log saved in: {self.log_file_path}")

        label_info = tk.Label(
            root,
            text=(
                "STEPS:\n"
                "1) Press 'Define area'\n"
                "2) Press & hold LMB, drag across to the opposite corner,\n"
                "   then release LMB.\n"
                "3) Select Option name from available options"
                "4) Type in minimum value or disable it\n"
                "4) Press 'Start' and place mouse cursor\n"
                "   on 'Imprint' button in the game.\n"
            )
        )
        label_info.pack(pady=5)

        frame_phrases = tk.Frame(root)
        frame_phrases.pack(pady=5)

        label_phrase1 = tk.Label(frame_phrases, text="Option name")
        label_phrase1.grid(row=0, column=0, padx=5, sticky="e")

        self.phrase1_options = [
            "PVE Penetration",
            "PVE Critical DMG",
            "All Attack UP",
            "Penetration",
            "Critical DMG."
        ]

        self.combo_phrase1 = ttk.Combobox(
            frame_phrases,
            values=self.phrase1_options,
            state="readonly",
            width=22
        )
        self.combo_phrase1.current(0)
        self.combo_phrase1.grid(row=0, column=1, padx=5)

        label_phrase2 = tk.Label(frame_phrases, text="Option min value:")
        label_phrase2.grid(row=1, column=0, padx=5, sticky="e")

        vcmd_phrase2 = (root.register(self.validate_digits), '%P')
        self.entry_phrase2 = tk.Entry(
            frame_phrases, width=25,
            validate='key', validatecommand=vcmd_phrase2,
            state="normal"
        )
        self.entry_phrase2.grid(row=1, column=1, padx=5)

        self.enable_phrase2_var = tk.BooleanVar(value=True)
        self.check_phrase2 = tk.Checkbutton(
            frame_phrases,
            text="Enable min value",
            variable=self.enable_phrase2_var,
            command=self.toggle_phrase2
        )
        self.check_phrase2.grid(row=1, column=2, padx=5, sticky="w")

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

    @staticmethod
    def validate_digits(new_value):
        return new_value.isdigit() or new_value == ""

    def toggle_phrase2(self):
        if self.enable_phrase2_var.get():
            self.entry_phrase2.config(state="normal")
        else:
            self.entry_phrase2.config(state="disabled")

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
        messagebox.showinfo(
            "Instruction",
            "Go to the game screen, press & hold LMB,\n"
            "drag across to the opposite corner, then release."
        )
        self.area_start = None
        self.area_end = None
        self.click_counter = 0

        if hasattr(self, "overlay_window") and self.overlay_window is not None:
            self.overlay_window.close_overlay()
            self.overlay_window = None

        def on_click(x, y, button, pressed):
            if button == mouse.Button.left:
                if pressed:
                    if self.click_counter == 0:
                        self.area_start = (x, y)
                        self.click_counter += 1
                else:
                    if self.click_counter == 1:
                        self.area_end = (x, y)
                        self.listener.stop()
                        self.root.after(10, self.calculate_area)
                        self.click_counter += 1

        self.listener = mouse.Listener(on_click=on_click)
        self.listener.start()

    def calculate_area(self):
        if self.area_start and self.area_end:
            x1, y1 = self.area_start
            x2, y2 = self.area_end
            left = min(x1, x2)
            right = max(x1, x2)
            top = min(y1, y2)
            bottom = max(y1, y2)
            width = right - left
            height = bottom - top

            if width <= 0 or height <= 0:
                messagebox.showerror("Error", "Wrong area definition (width or height <= 0).")
                self.log_info("Area definition error - zero or negative dimension.")
                self.area = None
                return

            self.area = (left, top, width, height)
            messagebox.showinfo("OK", f"Defined area: {self.area}")
            self.log_info(f"Defined area: {self.area}")
            self.btn_start.config(state=tk.NORMAL)

            self.overlay_window = OverlayWindow(self.root, left, top, width, height)

    def start(self):
        if not self.area:
            messagebox.showwarning("Missing area definition", "Fix area definition first!")
            return

        raw_phrase1 = self.combo_phrase1.get().strip()
        if self.enable_phrase2_var.get():
            raw_phrase2 = self.entry_phrase2.get().strip()
        else:
            raw_phrase2 = ""

        self.phrase1 = re.sub(r"\s+", "", raw_phrase1).lower()
        self.phrase2 = re.sub(r"\s+", "", raw_phrase2).lower()

        try:
            self.ping_ms = int(self.entry_ms.get().strip() or 50)
        except ValueError:
            self.ping_ms = 50

        self.delay_ms += self.ping_ms

        self.log_info(f"Start OCR - phrase1={self.phrase1}, phrase2={self.phrase2} (enabled={self.enable_phrase2_var.get()})")

        self.running = True
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_start.config(state=tk.DISABLED)
        self.root.after(3000, self.loop_ocr)

    def stop(self):
        self.running = False
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_start.config(state=tk.NORMAL)
        self.log_info("Stop OCR - end of loop.")

    @staticmethod
    def numeric_compare(phrase2_int, text):
        numbers_found = re.findall(r"\d+", text)
        for num_str in numbers_found:
            val = int(num_str)
            if val >= phrase2_int:
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
                    self.root.after(500 + self.ping_ms, self.loop_ocr)
                    return

            self.wrong_read_counter = 0

            found_phrase1 = False
            if self.phrase1:
                if self.phrase1 in text:
                    if self.phrase1 == "penetration":
                        if any(exc in text for exc in self.exceptions_for_penetration):
                            self.log_info("Found 'penetration' but ignoring special exception phrase.")
                        else:
                            found_phrase1 = True
                    else:
                        found_phrase1 = True

            found_phrase2 = False
            if self.phrase2:
                if self.phrase2.isdigit():
                    p2_int = int(self.phrase2)
                    found_phrase2 = self.numeric_compare(p2_int, text)
                else:
                    found_phrase2 = (self.phrase2 in text)

            if found_phrase1 and self.enable_phrase2_var.get() and found_phrase2:
                messagebox.showinfo("Found it!", "Hopefully that's what you have been looking for")
                self.log_info("Both found - finish")
                self.stop()
            elif found_phrase1 and not self.enable_phrase2_var.get():
                messagebox.showinfo("Found it!", "Phrase1 found, phrase2 disabled.")
                self.log_info("Phrase1 found - finish (phrase2 disabled).")
                self.stop()
            else:
                pyautogui.click(button='left')
                time.sleep(1.5)
                pyautogui.click(button='left')
                self.loop_in_progress = False
                self.root.after(self.delay_ms, self.loop_ocr)
                return

        except Exception as e:
            self.log_error(e)
            messagebox.showerror("Error", f"An error occurred:\n{e}")
            self.stop()

        self.loop_in_progress = False


def main():
    root = tk.Tk()
    app = StellarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
