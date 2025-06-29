# Collection automation logic

import time
import threading
import os
import sys
import cv2
import numpy as np
from tkinter import messagebox
from data.collection_data import get_collection_tabs
from pywinauto import mouse

class CollectionAutomation:
    def __init__(self, game_connector, status_callback=None):
        """Initialize collection automation"""
        self.game_connector = game_connector
        self.status_callback = status_callback

        # Automation state
        self.running = False
        
        # Speed settings
        self.delay_multiplier = 1.0  # Default normal speed
        
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
        
        # Red dot template path
        self.red_dot_template_path = None
        self.load_red_dot_template_path()

    def update_status(self, message):
        """Update status via callback if available"""
        if self.status_callback:
            self.status_callback(message)

    def set_delay_multiplier(self, multiplier):
        """Set the delay multiplier for speed control"""
        self.delay_multiplier = max(0.0, multiplier)  # Ensure non-negative

    def delay(self, base_time):
        """Apply delay with multiplier (0 = no delay)"""
        if self.delay_multiplier > 0:
            time.sleep(base_time * self.delay_multiplier)

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
                print(f"Red dot template not found at: {self.red_dot_template_path}")
        except Exception as e:
            self.red_dot_template_path = None
            print(f"Error loading red dot template: {e}")

    def find_red_dots_in_area(self, area, confidence=0.8):
        """Find all red dots in the specified area using OpenCV template matching"""
        if not self.red_dot_template_path or not os.path.exists(self.red_dot_template_path):
            print(f"Red dot template not available: {self.red_dot_template_path}")
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
            
            # Load the red dot template
            template = cv2.imread(self.red_dot_template_path, cv2.IMREAD_COLOR)
            if template is None:
                return []
            
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
            
            # Remove duplicate detections (if multiple detections are very close)
            filtered_positions = []
            min_distance = 10  # Minimum distance between detections
            
            for pos in red_dot_positions:
                is_duplicate = False
                for existing_pos in filtered_positions:
                    distance = ((pos[0] - existing_pos[0])**2 + (pos[1] - existing_pos[1])**2)**0.5
                    if distance < min_distance:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    filtered_positions.append(pos)
            
            print(f"Found {len(filtered_positions)} red dots in area {area}")
            return filtered_positions
            
        except Exception as e:
            print(f"Error in red dot detection: {e}")
            return []

    def click_at_screen_position(self, x, y):
        """Click at absolute screen coordinates"""
        try:
            # Convert screen coordinates to game window relative coordinates
            rel_x, rel_y, success = self.game_connector.convert_to_window_coords(x, y)
            if success:
                self.game_connector.click_at_position((rel_x, rel_y))
                return True
            else:
                return False
        except Exception as e:
            return False

    def set_collection_tabs_area(self, area):
        """Set the area containing all collection tabs"""
        self.collection_tabs_area = area

    def set_dungeon_list_area(self, area):
        """Set the area containing the dungeon/world/special/boss list entries"""
        self.dungeon_list_area = area

    def set_collection_items_area(self, area):
        """Set the area containing the collection items/materials panel"""
        self.collection_items_area = area

    def set_auto_refill_button(self, coords):
        """Set the auto refill button coordinates"""
        self.auto_refill_coords = coords

    def set_register_button(self, coords):
        """Set the register button coordinates"""
        self.register_coords = coords

    def set_yes_button(self, coords):
        """Set the yes button coordinates"""
        self.yes_coords = coords

    def set_page_2_button(self, coords):
        """Set the page 2 button coordinates"""
        self.page_2_coords = coords

    def set_page_3_button(self, coords):
        """Set the page 3 button coordinates"""
        self.page_3_coords = coords

    def set_page_4_button(self, coords):
        """Set the page 4 button coordinates"""
        self.page_4_coords = coords

    def set_arrow_right_button(self, coords):
        """Set the arrow right button coordinates"""
        self.arrow_right_coords = coords

    def click_action_button(self, button_type, double_click=False):
        """Click one of the action buttons (auto_refill, register, yes) with optional double-click"""
        coords = None
        if button_type == "auto_refill":
            coords = self.auto_refill_coords
        elif button_type == "register":
            coords = self.register_coords
        elif button_type == "yes":
            coords = self.yes_coords
        
        if coords and self.game_connector.is_connected():
            self.game_connector.click_at_position(coords)
            if double_click:
                self.delay(0.1)  # Very short delay between double clicks
                self.game_connector.click_at_position(coords)
            self.delay(0.2)  # Base delay
            return True
        return False

    def click_pagination_button(self, button_type):
        """Click one of the pagination buttons (page_2, page_3, page_4, arrow_right)"""
        coords = None
        if button_type == "page_2":
            coords = self.page_2_coords
        elif button_type == "page_3":
            coords = self.page_3_coords
        elif button_type == "page_4":
            coords = self.page_4_coords
        elif button_type == "arrow_right":
            coords = self.arrow_right_coords
        
        if coords and self.game_connector.is_connected():
            self.game_connector.click_at_position(coords)
            self.delay(0.3)  # Page loading delay
            return True
        return False

    def scroll_in_item_area(self, direction="down", scroll_amount=5):
        """Scroll in the item area using mouse wheel - more powerful scrolling"""
        if not self.collection_items_area or not self.game_connector.is_connected():
            return False
            
        try:
            # Calculate center of the item area for scrolling
            area_left, area_top, area_width, area_height = self.collection_items_area
            center_x = area_left + area_width // 2
            center_y = area_top + area_height // 2
            
            # Convert to screen coordinates
            window_rect = self.game_connector.get_window_rect()
            if window_rect:
                screen_x = window_rect.left + center_x
                screen_y = window_rect.top + center_y
                
                # Perform more powerful mouse scroll
                wheel_dist = -scroll_amount if direction == "down" else scroll_amount
                mouse.scroll(coords=(screen_x, screen_y), wheel_dist=wheel_dist)
                self.delay(0.3)  # Wait for scroll to complete
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
            messagebox.showerror("Missing Setup", 
                               f"Please set: {', '.join(missing_items)}")
            return

        if not self.game_connector.is_connected():
            messagebox.showerror("Error", "Not connected to game window")
            return False

        # Start automation in separate thread
        self.running = True
        threading.Thread(target=self._automation_loop, daemon=True).start()
        return True

    def _automation_loop(self):
        """Main automation loop - systematic workflow"""
        try:
            self.update_status("🚀 Collection automation started")
            
            # Validate areas are configured
            if not self.collection_tabs_area:
                self.update_status("❌ Collection tabs area not configured!")
                return
            if not self.dungeon_list_area:
                self.update_status("❌ Dungeon list area not configured!")
                return
            if not self.collection_items_area:
                self.update_status("❌ Collection items area not configured!")
                return
            
            print(f"Template path: {self.red_dot_template_path}")
            print(f"Collection tabs area: {self.collection_tabs_area}")
            print(f"Dungeon list area: {self.dungeon_list_area}")
            print(f"Collection items area: {self.collection_items_area}")
            
            while self.running:
                # Step 1: Check for red dots in collection tabs area
                self.update_status("🔍 Scanning collection tabs for red dots...")
                tab_red_dots = self.find_red_dots_in_area(self.collection_tabs_area)
                
                if not tab_red_dots:
                    self.update_status("✅ All collections complete!")
                    break
                
                # Process the first red dot found (most efficient)
                tab_dot_pos = tab_red_dots[0]
                
                self.click_at_screen_position(tab_dot_pos[0], tab_dot_pos[1])
                self.delay(0.6)  # Wait for tab to load
                
                # Step 2: Process dungeon list in this tab, passing the original tab position
                self.process_dungeon_list(tab_dot_pos)
                
                # Small delay before checking tabs again
                self.delay(0.3)
                
        except Exception as e:
            self.update_status(f"❌ Automation error: {str(e)}")
        finally:
            self.running = False
            self.update_status("⏹️ Collection automation stopped")

    def process_dungeon_list(self, original_tab_position):
        """Process all dungeons/entries with red dots in the current tab - simplified logic"""
        current_page = 1
        page_group = 0
        
        # Keep processing while the specific tab still has a red dot (indicating more work)
        while self.running and self.tab_still_has_red_dot(original_tab_position):
            # Process dungeons on current page
            found_dungeons = self.process_dungeons_on_current_page()
            
            if found_dungeons:
                # Found and processed dungeons, start over from page 1 (no need to click, it's default)
                current_page = 1
                page_group = 0
            else:
                # No dungeons on this page, try next page
                current_page += 1
                
                if current_page <= 4:
                    # Move to next page in current group
                    self.click_pagination_button(f"page_{current_page}")
                else:
                    # Move to next page group
                    if self.click_pagination_button("arrow_right"):
                        page_group += 1
                        current_page = 1
                    else:
                        break

    def process_dungeons_on_current_page(self):
        """Process all dungeons with red dots on the current page"""
        items_processed = False
        
        # Keep processing until no more red dots are found on this page
        while self.running:
            dungeon_red_dots = self.find_red_dots_in_area(self.dungeon_list_area)
            
            if not dungeon_red_dots:
                break
            
            # Process the first red dot found (most efficient approach)
            dungeon_dot_pos = dungeon_red_dots[0]
            
            self.click_at_screen_position(dungeon_dot_pos[0], dungeon_dot_pos[1])
            self.delay(0.4)  # Wait for items to load
            
            # Process collection items for this dungeon
            if self.process_collection_items():
                items_processed = True
            
            # Small delay before checking the page again
            self.delay(0.3)
                
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
        """Process all collection items with red dots - optimized for speed and coverage"""
        items_processed = False
        
        # First, scroll to top to ensure we start from the beginning
        self.scroll_in_item_area(direction="up", scroll_amount=20)  # Strong scroll to top
        self.delay(0.2)  # Reduced delay
        
        # Use a more efficient approach: fewer, larger scrolls
        scroll_positions = 4  # Check 4 positions to cover the full area
        
        for position in range(scroll_positions):
            if not self.running:
                break
            
            # Process all items at current scroll position
            current_position_had_items = self.process_all_items_at_current_position()
            if current_position_had_items:
                items_processed = True
            
            # Scroll down for next position (except on last position)
            if position < scroll_positions - 1:
                self.scroll_in_item_area(direction="down", scroll_amount=8)  # Larger scroll steps
                self.delay(0.15)  # Minimal delay for scroll to settle
                
        return items_processed

    def process_all_items_at_current_position(self):
        """Process items with red dots at the current scroll position - optimized for speed"""
        items_processed = False
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        # Keep processing until no more red dots are found at this position
        while self.running and iteration < max_iterations:
            iteration += 1
            
            # Re-scan for red dots each time to avoid clicking on items that no longer have red dots
            item_red_dots = self.find_red_dots_in_area(self.collection_items_area)
            
            if not item_red_dots:
                break  # No more red dots at this position
            
            # Process only the first red dot found (most reliable approach)
            item_dot_pos = item_red_dots[0]
            
            self.click_at_screen_position(item_dot_pos[0], item_dot_pos[1])
            self.delay(0.3)  # Wait for Auto Refill button to appear
            
            # Execute the button sequence
            if self.execute_button_sequence():
                items_processed = True
            
            # Very minimal delay before re-scanning for more items
            self.delay(0.05)  # Ultra minimal delay for efficiency
                
        return items_processed

    def execute_button_sequence(self):
        """Execute the button sequence: Auto Refill -> Register -> Yes (optimized for speed)"""
        if not self.running:
            return False
        
        # Click Auto Refill button (single click, longer delay)
        if self.click_action_button("auto_refill"):
            self.delay(0.3)  # Longer delay for Auto Refill processing
        else:
            return False
        
        # Double-click Register button for reliability
        if self.click_action_button("register", double_click=True):
            self.delay(0.05)  # Ultra fast timing
        else:
            return False
        
        # Double-click Yes button for reliability
        if self.click_action_button("yes", double_click=True):
            self.delay(0.15)  # Reduced wait for processing
            return True
        else:
            return False

    def stop(self):
        """Stop the automation"""
        self.running = False
        self.update_status("Stopping collection automation...")

    def emergency_stop(self):
        """Emergency stop the automation"""
        self.running = False
        self.update_status("🚨 Collection automation emergency stopped!")