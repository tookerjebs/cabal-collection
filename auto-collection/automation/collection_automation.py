# Collection automation logic

import time
import threading
import os
import sys
import cv2
import numpy as np
import win32api
import win32con
import win32gui

class CollectionAutomation:
    def __init__(self, game_connector, status_callback=None):
        """Initialize collection automation"""
        self.game_connector = game_connector
        self.status_callback = status_callback

        # Automation state
        self.running = False
        
        # Speed settings
        self.delay_ms = 1000  # Default 1000ms (1 second)
        
        # Action button coordinates for calibration
        self.auto_refill_coords = None
        self.register_coords = None
        self.yes_coords = None
        
        # Pagination button coordinates
        self.page_2_coords = None
        self.page_3_coords = None
        self.page_4_coords = None
        self.arrow_right_coords = None
        
        # Detection areas for red dots
        self.collection_tabs_area = None  # Area containing all collection tabs (Dungeon, World, Special, Boss)
        self.dungeon_list_area = None     # Area containing the dungeon/world/special/boss list entries
        self.collection_items_area = None # Area containing the collection items/materials panel
        
        # Red dot template path and cached template
        self.red_dot_template_path = None
        self.red_dot_template = None
        self.load_red_dot_template_path()

    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)

    def set_delay_ms(self, delay_ms):
        """Set the delay in milliseconds"""
        self.delay_ms = max(0, delay_ms)  # Ensure non-negative

    def delay(self, custom_ms=None):
        """Apply delay (0 = no delay)"""
        delay_to_use = custom_ms if custom_ms is not None else self.delay_ms
        if delay_to_use > 0:
            time.sleep(delay_to_use / 1000.0)  # Convert ms to seconds

    def load_red_dot_template_path(self):
        """Load the path to the red dot template image"""
        try:
            # Check if running as PyInstaller bundle
            if getattr(sys, 'frozen', False):
                # Running as executable - look for red-dot.png in the same directory as the exe
                bundle_dir = os.path.dirname(sys.executable)
                template_path = os.path.join(bundle_dir, "red-dot.png")
            else:
                # Running as script - use relative path
                current_dir = os.path.dirname(os.path.abspath(__file__))
                template_path = os.path.join(current_dir, "..", "data", "red-dot.png")
            
            self.red_dot_template_path = os.path.normpath(template_path)
            
            if not os.path.exists(self.red_dot_template_path):
                self.red_dot_template_path = None
            else:
                # Load and cache the template
                self.red_dot_template = cv2.imread(self.red_dot_template_path, cv2.IMREAD_COLOR)
        except Exception as e:
            self.red_dot_template_path = None
            self.red_dot_template = None

    def find_red_dots_in_area(self, area, confidence=0.9):
        """Find all red dots in the specified area using OpenCV template matching"""
        if not self.red_dot_template_path or self.red_dot_template is None:
            return []
        
        try:
            # Area format: (left, top, width, height)
            left, top, width, height = area
            
            # Capture screenshot of the specific area using game connector
            screenshot_pil = self.game_connector.capture_area_bitblt(area)
            if screenshot_pil is None:
                return []
            
            # Convert PIL image to OpenCV format
            screenshot_cv = cv2.cvtColor(np.array(screenshot_pil), cv2.COLOR_RGB2BGR)
            
            # Use cached template
            template = self.red_dot_template
            
            # Perform template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            
            # Find all matches above the confidence threshold
            locations = np.where(result >= confidence)
            
            # Convert matches to center coordinates (absolute screen coordinates)
            red_dot_positions = []
            template_height, template_width = template.shape[:2]
            
            for pt in zip(*locations[::-1]):  # Switch x and y coordinates
                # Calculate center of the template match
                center_x = left + pt[0] + template_width // 2
                center_y = top + pt[1] + template_height // 2
                red_dot_positions.append((center_x, center_y))
            
            # Remove duplicate detections
            if not red_dot_positions:
                return []
            
            filtered_positions = [red_dot_positions[0]]
            for pos in red_dot_positions[1:]:
                if all((pos[0] - existing[0])**2 + (pos[1] - existing[1])**2 >= 100 
                       for existing in filtered_positions):
                    filtered_positions.append(pos)
            
            return filtered_positions
            
        except Exception as e:
            return []

    def click_at_screen_position(self, x, y):
        """Click at absolute screen coordinates"""
        try:
            win32api.SetCursorPos((int(x), int(y)))
            self.delay()
            
            rel_x, rel_y, success = self.game_connector.convert_to_window_coords(x, y)
            if success:
                self.game_connector.click_at_position((rel_x, rel_y))
                return True
            return False
        except Exception as e:
            return False

    def set_collection_tabs_area(self, area):
        self.collection_tabs_area = area

    def set_dungeon_list_area(self, area):
        self.dungeon_list_area = area

    def set_collection_items_area(self, area):
        self.collection_items_area = area

    def set_auto_refill_button(self, coords):
        self.auto_refill_coords = coords

    def set_register_button(self, coords):
        self.register_coords = coords

    def set_yes_button(self, coords):
        self.yes_coords = coords

    def set_page_2_button(self, coords):
        self.page_2_coords = coords

    def set_page_3_button(self, coords):
        self.page_3_coords = coords

    def set_page_4_button(self, coords):
        self.page_4_coords = coords

    def set_arrow_right_button(self, coords):
        self.arrow_right_coords = coords

    def get_button_screen_coords(self, button_type):
        """Get screen coordinates for any button"""
        coords_map = {
            "auto_refill": self.auto_refill_coords,
            "register": self.register_coords,
            "yes": self.yes_coords,
            "page_2": self.page_2_coords,
            "page_3": self.page_3_coords,
            "page_4": self.page_4_coords,
            "arrow_right": self.arrow_right_coords
        }
        
        coords = coords_map.get(button_type)
        if coords and self.game_connector.is_connected():
            window_rect = self.game_connector.get_window_rect()
            if window_rect:
                return (window_rect.left + coords[0], window_rect.top + coords[1])
        return None

    def scroll_in_item_area(self, direction="down", scroll_amount=5):
        """Scroll in the item area using mouse wheel"""
        if not self.collection_items_area or not self.game_connector.is_connected():
            return False
            
        try:
            area_left, area_top, area_width, area_height = self.collection_items_area
            center_x = area_left + area_width // 2
            center_y = area_top + area_height // 2
            
            window_rect = self.game_connector.get_window_rect()
            if window_rect:
                screen_x = window_rect.left + center_x
                screen_y = window_rect.top + center_y
                
                win32api.SetCursorPos((int(screen_x), int(screen_y)))
                self.delay()
                
                wheel_dist = -scroll_amount if direction == "down" else scroll_amount
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, int(screen_x), int(screen_y), wheel_dist * 120, 0)
                self.delay()
                return True
                
        except Exception as e:
            pass
            
        return False

    def start(self):
        """Start the collection automation"""
        # Check if required areas and coordinates are set
        missing_items = []
        
        if not self.collection_tabs_area:
            missing_items.append("Collection tabs area")
        if not self.dungeon_list_area:
            missing_items.append("Dungeon list area")
        if not self.collection_items_area:
            missing_items.append("Collection items area")
        if not self.auto_refill_coords:
            missing_items.append("Auto Refill button")
        if not self.register_coords:
            missing_items.append("Register button") 
        if not self.yes_coords:
            missing_items.append("Yes button")
        if not self.page_2_coords:
            missing_items.append("Page 2 button")
        if not self.page_3_coords:
            missing_items.append("Page 3 button")
        if not self.page_4_coords:
            missing_items.append("Page 4 button")
        if not self.arrow_right_coords:
            missing_items.append("Arrow Right button")
            
        if missing_items:
            self.update_status(f"❌ Missing setup: {', '.join(missing_items)}")
            return False

        if not self.game_connector.is_connected():
            self.update_status("❌ Not connected to game window")
            return False

        # Start automation in separate thread
        self.running = True
        threading.Thread(target=self._automation_loop, daemon=True).start()
        return True

    def _automation_loop(self):
        """Main automation loop"""
        try:
            self.update_status("Automation started")
            
            while self.running:
                if self.delay_ms > 0:
                    self.update_status("🔍 Scanning collection tabs for red dots...")
                tab_red_dots = self.find_red_dots_in_area(self.collection_tabs_area)
                
                if not tab_red_dots:
                    self.update_status("✓ All collections complete!")
                    break
                
                tab_dot_pos = tab_red_dots[0]
                self.click_at_screen_position(tab_dot_pos[0], tab_dot_pos[1])
                self.delay()
                
                self.process_dungeon_list(tab_dot_pos)
                self.delay()
                
        except Exception as e:
            self.update_status(f"❌ Automation error: {str(e)}")
        finally:
            self.running = False
            self.update_status("Automation stopped")

    def process_dungeon_list(self, original_tab_position):
        """Process all dungeons/entries with red dots in the current tab"""
        current_page = 1
        
        while self.running and self.tab_still_has_red_dot(original_tab_position):
            found_dungeons = self.process_dungeons_on_current_page()
            
            if found_dungeons:
                current_page = 1
            else:
                current_page += 1
                
                if current_page <= 4:
                    coords = self.get_button_screen_coords(f"page_{current_page}")
                    if coords:
                        self.click_at_screen_position(coords[0], coords[1])
                        self.delay()
                else:
                    coords = self.get_button_screen_coords("arrow_right")
                    if coords and self.click_at_screen_position(coords[0], coords[1]):
                        self.delay()
                        current_page = 1
                    else:
                        break

    def process_dungeons_on_current_page(self):
        """Process all dungeons with red dots on the current page"""
        items_processed = False
        
        while self.running:
            dungeon_red_dots = self.find_red_dots_in_area(self.dungeon_list_area)
            if not dungeon_red_dots:
                break
            
            dungeon_dot_pos = dungeon_red_dots[0]
            self.click_at_screen_position(dungeon_dot_pos[0], dungeon_dot_pos[1])
            self.delay()
            
            if self.process_collection_items():
                items_processed = True
            self.delay()
                
        return items_processed

    def tab_still_has_red_dot(self, original_tab_position):
        """Check if the specific tab we clicked still has a red dot"""
        tab_red_dots = self.find_red_dots_in_area(self.collection_tabs_area)
        
        # Check if any red dot is close to our original tab position (within 20 pixels)
        tolerance = 20
        for red_dot_pos in tab_red_dots:
            distance = ((red_dot_pos[0] - original_tab_position[0])**2 + 
                       (red_dot_pos[1] - original_tab_position[1])**2)**0.5
            if distance <= tolerance:
                return True
        
        return False

    def process_collection_items(self):
        """Process all collection items with red dots"""
        items_processed = False
        
        self.scroll_in_item_area(direction="up", scroll_amount=20)
        self.delay()
        
        for position in range(4):
            if not self.running:
                break
            
            if self.process_all_items_at_current_position():
                items_processed = True
            
            if position < 3:
                self.scroll_in_item_area(direction="down", scroll_amount=8)
                self.delay()
                
        return items_processed

    def process_all_items_at_current_position(self):
        """Process items with red dots at the current scroll position"""
        items_processed = False
        
        while self.running:
            item_red_dots = self.find_red_dots_in_area(self.collection_items_area)
            if not item_red_dots:
                break
            
            item_dot_pos = item_red_dots[0]
            self.click_at_screen_position(item_dot_pos[0], item_dot_pos[1])
            self.delay()
            
            if self.execute_button_sequence():
                items_processed = True
            self.delay()
                
        return items_processed

    def execute_button_sequence(self):
        """Execute the button sequence: Auto Refill -> Register -> Yes"""
        if not self.running:
            return False
        
        # Auto Refill
        coords = self.get_button_screen_coords("auto_refill")
        if not coords or not self.click_at_screen_position(coords[0], coords[1]):
            return False
        self.delay()
        
        # Register
        coords = self.get_button_screen_coords("register")
        if not coords or not self.click_at_screen_position(coords[0], coords[1]):
            return False
        self.delay()
        
        # Yes
        coords = self.get_button_screen_coords("yes")
        if not coords or not self.click_at_screen_position(coords[0], coords[1]):
            return False
        self.delay()
        
        return True

    def stop(self):
        """Stop the automation"""
        self.running = False
        self.update_status("Stopping collection automation...")

    def emergency_stop(self):
        """Emergency stop the automation"""
        self.running = False
        self.update_status("🚨 Collection automation emergency stopped!")