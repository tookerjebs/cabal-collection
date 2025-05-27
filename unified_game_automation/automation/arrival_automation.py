# Arrival skill automation logic
# Ported from arrival_skill_ocr/automation.py

import time
import threading
from tkinter import messagebox
from data.arrival_data import get_offensive_skills, get_defensive_skills, get_base_stat_name

class ArrivalAutomation:
    def __init__(self, game_connector, ocr_engine, status_callback=None):
        """Initialize arrival skill automation"""
        self.game_connector = game_connector
        self.ocr_engine = ocr_engine
        self.status_callback = status_callback

        # Automation state
        self.running = False
        self.apply_button_coords = None
        self.change_button_coords = None
        self.detection_region = None

        # Configuration
        self.area = None

        # Stat tracking
        self.stat_counter = {}
        self.unmapped_ocr_counter = {}

    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)

    def set_area(self, area):
        """Set the OCR area"""
        self.area = area
        self.detection_region = area

    def set_apply_button(self, coords):
        """Set the apply button coordinates"""
        self.apply_button_coords = coords

    def set_change_button(self, coords):
        """Set the change button coordinates"""
        self.change_button_coords = coords

    def start(self, desired_stats=None):
        """Start the arrival automation"""
        # Check if button coordinates are set
        if not self.apply_button_coords or not self.change_button_coords:
            messagebox.showerror("Error", "Please set both Apply and Change button coordinates.")
            return False

        if not self.area:
            messagebox.showwarning("Missing area definition", "Fix area definition first!")
            return False

        # Connect to game if not already connected
        if not self.game_connector.is_connected():
            if not self.game_connector.connect_to_game():
                messagebox.showerror("Error", "Could not connect to the game window. Make sure the game is running.")
                return False

        # Reset counters for new run
        self.stat_counter = {}
        self.unmapped_ocr_counter = {}

        self.update_status("Starting arrival skill automation")

        self.running = True

        # Start automation in thread
        threading.Thread(target=self.reroll_loop, args=(desired_stats,), daemon=True).start()
        return True

    def stop(self):
        """Stop the arrival automation"""
        self.running = False
        self.update_status("Arrival automation stopped")

        # Show summary of stats if we have any
        if self.stat_counter:
            self.show_stats_summary()

    def emergency_stop(self):
        """Emergency stop the automation"""
        if self.running:
            self.stop()
            self.update_status("🚨 EMERGENCY STOP - Arrival automation stopped!")

    def detect_text_in_image(self, image):
        """Detect text in image using Tesseract and parse for arrival skill format"""
        if image is None:
            return {}

        # Extract text using Tesseract
        raw_text = self.ocr_engine.extract_text(image)

        # Print raw OCR text to console for debugging
        print(f"Raw OCR text: {repr(raw_text)}")

        # Fix OCR misreading + as 4 (only when there's no + sign already)
        import re
        cleaned_text = re.sub(r'([A-Za-z\s\.]+)\s4(\d)', r'\1 +\2', raw_text)

        # Fix OCR misreading dots as commas
        cleaned_text = cleaned_text.replace(',', '.')

        # Parse for arrival skill format (dual stats, no "Stellar" text)
        return self.parse_arrival_text(cleaned_text)

    def parse_arrival_text(self, text):
        """
        Parse text for arrival skill format
        Expected format: Two stats with values (no "Stellar" text)
        Example:
        Add. Damage        +45
        HP Absorb Up       +2%

        Special handling for long arrival skill names that get cut off:
        - "Arrival Skill Cool time decreas," -> "Arrival Skill Cool Time decreased."
        - "Arrival Skill Duration" -> "Arrival Skill Duration Increase"
        """
        import re

        current_stats = {}

        # First, handle special cases for arrival skills with truncated names
        current_stats.update(self.handle_arrival_skill_special_cases(text))

        # Split text into lines for normal processing
        lines = text.strip().split('\n')

        # Look for stat patterns in each line
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip lines that are already handled by special cases
            if self.is_arrival_skill_line(line):
                continue

            # Try to match stat patterns: "Stat Name +Value" or "Stat Name Value"
            # Handle both percentage and numeric values
            patterns = [
                r'(.+?)\s*\+(\d+)%',  # "Stat Name +5%"
                r'(.+?)\s*\+(\d+)',   # "Stat Name +45"
                r'(.+?)\s*(\d+)%',    # "Stat Name 5%"
                r'(.+?)\s*(\d+)',     # "Stat Name 45"
            ]

            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    stat_name = match.group(1).strip()
                    value_str = match.group(2).strip()

                    # Clean up stat name
                    stat_name = stat_name.replace('.', '').strip()

                    # Try to match against known stats
                    matched_stat = self.match_stat_name(stat_name)
                    if matched_stat:
                        try:
                            value = int(value_str)
                            current_stats[matched_stat] = value
                        except ValueError:
                            continue
                    else:
                        # Track unmapped stats for summary
                        if '%' in pattern:
                            value_str += '%'
                        unmapped_key = f"{stat_name} +{value_str}"
                        self.unmapped_ocr_counter[unmapped_key] = self.unmapped_ocr_counter.get(unmapped_key, 0) + 1
                    break

        return current_stats

    def handle_arrival_skill_special_cases(self, text):
        """
        Handle special cases for arrival skills with long names that get truncated
        Returns a dictionary of detected arrival skills without values
        """
        special_stats = {}
        text_lower = text.lower()

        # Case 1: Arrival Skill Cool Time decreased
        if ('arrival' in text_lower and 'cool' in text_lower and 'time' in text_lower) or \
           ('arrival skill cool time decreas' in text_lower):
            special_stats["Arrival Skill Cool Time decreased."] = None

        # Case 2: Arrival Skill Duration Increase
        elif ('arrival' in text_lower and 'duration' in text_lower) or \
             ('arrival skill duration' in text_lower):
            special_stats["Arrival Skill Duration Increase"] = None

        return special_stats

    def is_arrival_skill_line(self, line):
        """
        Check if a line contains arrival skill text that should be skipped in normal processing
        """
        line_lower = line.lower()
        return ('arrival' in line_lower and ('cool' in line_lower or 'duration' in line_lower))

    def match_stat_name(self, detected_name):
        """Match detected stat name to known arrival skill stats"""
        from data.arrival_data import get_all_base_stat_names

        detected_lower = detected_name.lower().replace(' ', '').replace('.', '')

        # Try exact matches first
        for known_stat in get_all_base_stat_names():
            known_lower = known_stat.lower().replace(' ', '').replace('.', '')
            if detected_lower == known_lower:
                return known_stat

        # Try partial matches
        for known_stat in get_all_base_stat_names():
            known_lower = known_stat.lower().replace(' ', '').replace('.', '')
            if detected_lower in known_lower or known_lower in detected_lower:
                return known_stat

        return None

    def reroll_loop(self, desired_stats):
        """Main reroll loop for arrival skill automation"""
        self.update_status("▶️ Starting arrival skill automation...")

        iteration_count = 0

        # Pre-compute stat categories
        offensive_base_stats = set(get_base_stat_name(stat) for stat in get_offensive_skills())
        defensive_base_stats = set(get_base_stat_name(stat) for stat in get_defensive_skills())

        # First click the Change button to remove current option
        self.game_connector.click_at_position(self.change_button_coords)
        time.sleep(0.4)

        while self.running:
            iteration_count += 1

            # Click Apply button to apply a new option
            self.game_connector.click_at_position(self.apply_button_coords)
            time.sleep(0.5)  # Wait for game to update

            # Capture screenshot using BitBlt
            screenshot = self.game_connector.capture_area_bitblt(self.area)
            if screenshot is None:
                self.update_status("Failed to capture screen, retrying...")
                time.sleep(0.5)
                continue

            # Detect text in the screenshot
            current_stats = self.detect_text_in_image(screenshot)

            if current_stats:
                # Track stats for summary
                for stat, value in current_stats.items():
                    stat_key = f"{stat} +{value}"
                    self.stat_counter[stat_key] = self.stat_counter.get(stat_key, 0) + 1

                # Log detected stats
                stat_list = [f"{stat}: {value}" for stat, value in current_stats.items()]
                if stat_list:
                    self.update_status(f"Roll #{iteration_count}: " + " | ".join(stat_list))
            else:
                self.update_status(f"Roll #{iteration_count}: No stats detected")

            # Check if we have desired stats
            if self.check_desired_stats(current_stats, desired_stats):
                self.update_status("🎉🎉🎉 SUCCESS! DESIRED STATS FOUND! 🎉🎉🎉")
                self.stop()
                messagebox.showinfo("Success", "Desired stats found! Automation stopped.")
                break

            # If desired stats not found, click the Change button to reroll
            self.game_connector.click_at_position(self.change_button_coords)
            time.sleep(0.4)

    def check_desired_stats(self, current_stats, desired_stats):
        """
        Check if current stats meet the desired criteria for arrival skills
        - If only offensive stat specified: The offensive stat must be found
        - If only defensive stat specified: The defensive stat must be found
        - If both are specified: Both the offensive AND defensive stat must be found
        """
        if not desired_stats:
            return True

        if not desired_stats.get('offensive') and not desired_stats.get('defensive'):
            return True

        # Check if offensive stat matches (if specified)
        off_match = False
        if desired_stats.get('offensive'):
            display_stat_name, min_value, _ = desired_stats['offensive'][0]
            base_stat_name = get_base_stat_name(display_stat_name)

            if base_stat_name in current_stats:
                stat_value = current_stats[base_stat_name]
                if stat_value is None:
                    # Special case: arrival skill detected but value unavailable due to UI collision
                    self.update_status(f"🎉 FOUND: {display_stat_name} detected!")
                    self.update_status(f"⚠️ Note: Cannot verify value due to UI collision - please check manually")
                    self.stop()
                    messagebox.showinfo("Found it!", f"{display_stat_name} detected!\n\nNote: Cannot read value due to UI collision.\nPlease verify the value manually.")
                    return True
                elif stat_value >= min_value:
                    off_match = True
                    self.update_status(f"✅ MATCH: Found {display_stat_name} with value {stat_value} (target: {min_value}+)")
        else:
            off_match = True

        # Check if defensive stat matches (if specified)
        def_match = False
        if desired_stats.get('defensive'):
            display_stat_name, min_value, _ = desired_stats['defensive'][0]
            base_stat_name = get_base_stat_name(display_stat_name)

            if base_stat_name in current_stats:
                stat_value = current_stats[base_stat_name]
                if stat_value is None:
                    # Special case: arrival skill detected but value unavailable due to UI collision
                    self.update_status(f"🎉 FOUND: {display_stat_name} detected!")
                    self.update_status(f"⚠️ Note: Cannot verify value due to UI collision - please check manually")
                    self.stop()
                    messagebox.showinfo("Found it!", f"{display_stat_name} detected!\n\nNote: Cannot read value due to UI collision.\nPlease verify the value manually.")
                    return True
                elif stat_value >= min_value:
                    def_match = True
                    self.update_status(f"✅ MATCH: Found {display_stat_name} with value {stat_value} (target: {min_value}+)")
        else:
            def_match = True

        return off_match and def_match

    def show_stats_summary(self):
        """Show summary of detected stats"""
        self.update_status("")
        self.update_status("SUMMARY OF DETECTED STATS")

        # Separate stats by category
        offensive_base_stats = set(get_base_stat_name(stat) for stat in get_offensive_skills())
        defensive_base_stats = set(get_base_stat_name(stat) for stat in get_defensive_skills())

        # Group stats by category
        offensive_stats = {}
        defensive_stats = {}
        other_stats = {}

        for stat_key, count in self.stat_counter.items():
            # Extract the stat name from the key (format is "stat_name +value")
            parts = stat_key.split("+")
            if len(parts) >= 1:
                stat_name = parts[0].strip()

                # Categorize the stat
                if stat_name in offensive_base_stats:
                    offensive_stats[stat_key] = count
                elif stat_name in defensive_base_stats:
                    defensive_stats[stat_key] = count
                else:
                    other_stats[stat_key] = count

        # Display offensive stats
        if offensive_stats:
            self.update_status("Offensive Stats:")
            for stat_key, count in sorted(offensive_stats.items(), key=lambda x: x[1], reverse=True):
                self.update_status(f"  • {stat_key} × {count}")

        # Display defensive stats
        if defensive_stats:
            self.update_status("Defensive Stats:")
            for stat_key, count in sorted(defensive_stats.items(), key=lambda x: x[1], reverse=True):
                self.update_status(f"  • {stat_key} × {count}")

        # Display other stats
        if other_stats:
            self.update_status("Other Stats:")
            for stat_key, count in sorted(other_stats.items(), key=lambda x: x[1], reverse=True):
                self.update_status(f"  • {stat_key} × {count}")

        # Display unmapped stats (stats detected by OCR but not in our data)
        if self.unmapped_ocr_counter:
            self.update_status("🔍 Unmapped Stats (not in our data):")
            for stat_key, count in sorted(self.unmapped_ocr_counter.items(), key=lambda x: x[1], reverse=True):
                self.update_status(f"  • {stat_key} × {count}")

        # Reset counters for next run
        self.stat_counter = {}
        self.unmapped_ocr_counter = {}
