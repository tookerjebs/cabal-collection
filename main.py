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
        self.root = root
        self.root.title("Stellar OCR Demo")

        self.root.attributes("-topmost", True)

        self.overlay_window = None
        self.area = None
        self.area_start = None
        self.area_end = None
        self.click_counter = 0
        self.listener = None
        self.running = False

        self.log_file_path = self.create_log_file()
        self.log_info(f"Application start - log saved in: {self.log_file_path}")

        label_info = tk.Label(
            root,
            text=(
                "STEPS:\n"
                "1) Press 'Define area'\n"
                "2) Press & hold LMB, drag across to the opposite corner,\n"
                "   then release LMB.\n"
                "3) Type in phrase1 (Penetration) and phrase2 (15)\n"
                "4) Press 'Start' and place mouse cursor\n"
                "   on 'Imprint' button in the game.\n"
            )
        )
        label_info.pack(pady=5)

        frame_phrases = tk.Frame(root)
        frame_phrases.pack(pady=5)

        label_phrase1 = tk.Label(frame_phrases, text="Phrase 1 (Penetration):")
        label_phrase1.grid(row=0, column=0, padx=5, sticky="e")

        self.entry_phrase1 = tk.Entry(frame_phrases, width=25)
        self.entry_phrase1.grid(row=0, column=1, padx=5)

        label_phrase2 = tk.Label(frame_phrases, text="Phrase 2 (15):")
        label_phrase2.grid(row=1, column=0, padx=5, sticky="e")

        vcmd = (root.register(self.validate_digits), '%P')
        self.entry_phrase2 = tk.Entry(
            frame_phrases, width=25,
            validate='key', validatecommand=vcmd,
            state="normal"
        )
        self.entry_phrase2.grid(row=1, column=1, padx=5)

        self.enable_phrase2_var = tk.BooleanVar(value=True)
        self.check_phrase2 = tk.Checkbutton(
            frame_phrases,
            text="Enable phrase2",
            variable=self.enable_phrase2_var,
            command=self.toggle_phrase2
        )
        self.check_phrase2.grid(row=1, column=2, padx=5, sticky="w")

        self.btn_define_area = tk.Button(root, text="Define area", command=self.define_area)
        self.btn_define_area.pack(pady=5)

        self.btn_start = tk.Button(root, text="Start", command=self.start, state=tk.DISABLED)
        self.btn_start.pack(pady=5)

        self.btn_stop = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED)
        self.btn_stop.pack(pady=5)

    @staticmethod
    def validate_digits(new_value):
        return new_value.isdigit()


    def toggle_phrase2(self):
        if self.enable_phrase2_var.get():
            self.entry_phrase2.config(state="normal")
        else:
            self.entry_phrase2.config(state="disabled")

    @staticmethod
    def create_log_file():
        """
        Creates directory stellarlink_logs in user home directory and
        returns path to new log file in that dir.
        If file exists, appends _v2, _v3, etc.
        """
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
        """
        Adds a line with timestamp to the log file.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] INFO: {message}\n"
        with open(self.log_file_path, mode="a", encoding="utf-8") as f:
            f.write(line)

    def log_error(self, exception):
        """
        Logs an error (exception) with a timestamp.
        """
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
                        self.calculate_area()
                        self.listener.stop()
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

        raw_phrase1 = self.entry_phrase1.get().strip()
        if self.enable_phrase2_var.get():
            raw_phrase2 = self.entry_phrase2.get().strip()
        else:
            raw_phrase2 = ""

        self.phrase1 = re.sub(r"\s+", "", raw_phrase1).lower()
        self.phrase2 = re.sub(r"\s+", "", raw_phrase2).lower()

        if not self.phrase1:
            messagebox.showwarning("Missing phrases", "You have to input phrase1!")
            return

        self.log_info(f"Start OCR - phrase1={self.phrase1}, phrase2={self.phrase2} (enabled={self.enable_phrase2_var.get()})")

        self.running = True
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_start.config(state=tk.DISABLED)
        self.root.after(100, self.loop_ocr)

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
        if not self.running:
            return

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

            # Sprawdzamy wszystkie liczby:
            numbers_found = re.findall(r"\d+", text)
            if len(numbers_found) > 1:
                messagebox.showinfo("Multiple numbers", "Found more than one number - stopping.\n"
                                                        "Make sure that you've defined area correctly.")
                self.log_info("More than one number found in text. Stopping.")
                self.stop()
                return

            found_phrase1 = (self.phrase1 in text) if self.phrase1 else False

            found_phrase2 = False
            if self.phrase2:
                if self.phrase2.isdigit():
                    p2_int = int(self.phrase2)
                    found_phrase2 = self.numeric_compare(p2_int, text)
                else:
                    found_phrase2 = (self.phrase2 in text)

            # -------------------------
            # Logic
            # -------------------------
            # 1) both found
            if found_phrase1 and self.enable_phrase2_var.get() and found_phrase2:
                messagebox.showinfo("Found it!", "Hopefully that's what you have been looking for")
                self.log_info("Both found - finish")
                self.stop()

            # 2) phrase2 off - phrase1 found
            elif found_phrase1 and not self.enable_phrase2_var.get():
                messagebox.showinfo("Found it!", "Phrase1 found, phrase2 disabled.")
                self.log_info("Phrase1 found - finish (phrase2 disabled).")
                self.stop()

            # 3) Only one of the phrases found
            elif (found_phrase1 and self.enable_phrase2_var.get() and not found_phrase2) or \
                 (found_phrase2 and not found_phrase1):
                self.log_info(f"One found, text={text} -> Another attempt.")
                time.sleep(1)
                time.sleep(0.3)
                self.root.after(100, self.loop_ocr)
            else:
                pyautogui.click(button='left')
                time.sleep(1)
                pyautogui.click(button='left')
                time.sleep(0.3)
                self.root.after(100, self.loop_ocr)

        except Exception as e:
            self.log_error(e)
            messagebox.showerror("Error", f"An error occurred:\n{e}")
            self.stop()


def main():
    root = tk.Tk()
    app = StellarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
