# Settings manager for saving/loading configuration
import json
import os
from typing import Dict, Any, Optional, Tuple

class SettingsManager:
    def __init__(self, settings_file: str = "settings.json"):
        """Initialize settings manager"""
        self.settings_file = settings_file
        self.settings = {}
        self.load_settings()
    
    def load_settings(self) -> None:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self._get_default_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self._get_default_settings()
    
    def save_settings(self) -> None:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            "areas": {
                "collection_tabs": None,
                "dungeon_list": None,
                "collection_items": None
            },
            "buttons": {
                "auto_refill": None,
                "register": None,
                "yes": None,
                "page_2": None,
                "page_3": None,
                "page_4": None,
                "arrow_right": None
            },
            "speed": {
                "delay_ms": 1000
            }
        }
    
    def set_area(self, area_name: str, area_coords: Tuple[int, int, int, int]) -> None:
        """Set area coordinates"""
        if "areas" not in self.settings:
            self.settings["areas"] = {}
        self.settings["areas"][area_name] = area_coords
        self.save_settings()
    
    def get_area(self, area_name: str) -> Optional[Tuple[int, int, int, int]]:
        """Get area coordinates"""
        return self.settings.get("areas", {}).get(area_name)
    
    def set_button(self, button_name: str, coords: Tuple[int, int]) -> None:
        """Set button coordinates"""
        if "buttons" not in self.settings:
            self.settings["buttons"] = {}
        self.settings["buttons"][button_name] = coords
        self.save_settings()
    
    def get_button(self, button_name: str) -> Optional[Tuple[int, int]]:
        """Get button coordinates"""
        return self.settings.get("buttons", {}).get(button_name)
    
    def set_delay_ms(self, delay_ms: int) -> None:
        """Set delay in milliseconds"""
        if "speed" not in self.settings:
            self.settings["speed"] = {}
        self.settings["speed"]["delay_ms"] = delay_ms
        self.save_settings()
    
    def get_delay_ms(self) -> int:
        """Get delay in milliseconds"""
        # Handle backward compatibility with old multiplier format
        speed_settings = self.settings.get("speed", {})
        if "delay_ms" in speed_settings:
            return speed_settings["delay_ms"]
        elif "delay_multiplier" in speed_settings:
            # Convert old multiplier to milliseconds (1.0 = 1000ms)
            multiplier = speed_settings["delay_multiplier"]
            return int(multiplier * 1000)
        else:
            return 1000  # Default 1 second
    
    def get_all_areas(self) -> Dict[str, Any]:
        """Get all area settings"""
        return self.settings.get("areas", {})
    
    def get_all_buttons(self) -> Dict[str, Any]:
        """Get all button settings"""
        return self.settings.get("buttons", {})
    
    def is_setup_complete(self) -> bool:
        """Check if basic setup is complete"""
        areas = self.get_all_areas()
        buttons = self.get_all_buttons()
        
        # Check if essential areas are defined
        essential_areas = ["collection_tabs", "dungeon_list", "collection_items"]
        areas_ok = all(areas.get(area) is not None for area in essential_areas)
        
        # Check if essential buttons are defined
        essential_buttons = ["auto_refill", "register", "yes"]
        buttons_ok = all(buttons.get(button) is not None for button in essential_buttons)
        
        return areas_ok and buttons_ok