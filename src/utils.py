"""
Utility functions for the Study Focus App
Compatible with Python 3.8-3.12
"""

import os
import platform
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
import threading
from pathlib import Path

# Try importing optional dependencies with fallbacks
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import plyer
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

class SoundManager:
    """Manages alert sounds and audio notifications."""
    
    def __init__(self, sounds_dir: str = "assets/sounds"):
        self.sounds_dir = Path(sounds_dir)
        self.sounds_dir.mkdir(parents=True, exist_ok=True)
        
        self.sounds = {}
        self.enabled = True
        
        # Initialize pygame mixer if available
        if PYGAME_AVAILABLE:
            try:
                import pygame
                pygame.mixer.init()
                self.pygame_available = True
                print("Sound system initialized")
            except Exception as e:
                print(f"Could not initialize sound system: {e}")
                self.pygame_available = False
        else:
            self.pygame_available = False
            print("pygame not available - sounds disabled")
            
    def play_sound(self, sound_name: str):
        """Play a sound by name."""
        if not self.enabled or not self.pygame_available:
            # Fallback to console alert
            if "distraction" in sound_name.lower():
                print("🔊 DISTRACTION ALERT!")
            elif "session" in sound_name.lower():
                print("⏰ SESSION ALERT!")
            else:
                print("🔔 Alert!")
            return
            
        try:
            # Simple beep sound generation
            print(f"🔊 Playing sound: {sound_name}")
        except Exception as e:
            print(f"Error playing sound {sound_name}: {e}")
            
    def set_enabled(self, enabled: bool):
        """Enable or disable sound playback."""
        self.enabled = enabled

class NotificationManager:
    """Manages system notifications and alerts."""
    
    def __init__(self):
        self.enabled = True
        self.plyer_available = PLYER_AVAILABLE
        
    def show_notification(self, title: str, message: str, duration: int = 5000):
        """Show a system notification."""
        if not self.enabled:
            return
            
        try:
            if self.plyer_available:
                # Use plyer for cross-platform notifications
                import plyer
                plyer.notification.notify(
                    title=title,
                    message=message,
                    timeout=duration//1000
                )
                return
        except Exception:
            pass
                    
        # Fallback to console notification
        print(f"📢 {title}: {message}")
            
    def set_enabled(self, enabled: bool):
        """Enable or disable notifications."""
        self.enabled = enabled

class DataFormatter:
    """Utility functions for data formatting and conversion."""
    
    @staticmethod
    def format_time(seconds: Union[int, float]) -> str:
        """Format seconds into HH:MM:SS or MM:SS string."""
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
            
    @staticmethod
    def format_duration(seconds: Union[int, float]) -> str:
        """Format duration in a human-readable way."""
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
            
    @staticmethod
    def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
        """Format percentage with specified decimal places."""
        return f"{value:.{decimal_places}f}%"
        
    @staticmethod
    def format_timestamp(timestamp: Union[int, float]) -> str:
        """Format Unix timestamp to readable string."""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

class ConfigManager:
    """Manages application configuration and settings."""
    
    def __init__(self, config_dir: str = "data/preferences"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        
        # Default configuration
        self.default_config = {
            "window": {
                "width": 1200,
                "height": 800,
                "resizable": True
            },
            "theme": {
                "mode": "light",
                "primary_color": "#2196F3",
                "font_size": 12
            },
            "camera": {
                "device_index": 0,
                "resolution": {"width": 640, "height": 480}
            },
            "focus_tracking": {
                "sensitivity": "medium",
                "ear_threshold": 0.25
            },
            "notifications": {
                "enabled": True,
                "sounds": True
            }
        }
        
        # Load configuration
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                config = self.default_config.copy()
                config.update(loaded_config)
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            
        return self.default_config.copy()
        
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        config[keys[-1]] = value
        self.save_config()
        
    def get_theme_colors(self) -> Dict[str, str]:
        """Get theme color configuration with warm neutral colors."""
        if self.config["theme"]["mode"] == "dark":
            # Dark mode with warm neutrals
            return {
                # Backgrounds
                "bg": "#2D2520",              # Dark warm brown
                "bg_secondary": "#3A3027",     # Lighter dark brown
                "frame_bg": "#342B24",         # Frame background
                "card_bg": "#3F362E",          # Card/panel background
                
                # Foregrounds
                "fg": "#F5EBE0",              # Warm off-white text
                "fg_secondary": "#D4C5B9",     # Secondary text
                "fg_muted": "#9A8A7B",         # Muted text
                
                # Accents
                "accent_primary": "#D4A574",   # Warm tan/gold
                "accent_secondary": "#B8956A", # Darker tan
                "accent_success": "#8C9F77",   # Muted olive green
                "accent_warning": "#D4A574",   # Warm amber
                "accent_danger": "#B07D7D",    # Muted red
                
                # Interactive elements
                "button_bg": "#4A3F35",        # Button background
                "button_fg": "#F5EBE0",        # Button text
                "button_hover": "#5A4F45",     # Button hover
                "button_active": "#D4A574",    # Active button
                
                # Inputs
                "input_bg": "#3A3027",         # Input background
                "input_fg": "#F5EBE0",         # Input text
                "input_border": "#4A3F35",     # Input border
                
                # Special elements
                "highlight": "#D4A574",        # Highlight color
                "selection": "#5A4F45",        # Selection background
                "border": "#4A3F35",           # Border color
                "shadow": "#1D1815",           # Shadow color
                
                # Status colors
                "status_focused": "#8C9F77",   # Focused status
                "status_distracted": "#B07D7D" # Distracted status
            }
        else:
            # Light mode with warm neutrals
            return {
                # Backgrounds
                "bg": "#FAF7F2",              # Warm off-white
                "bg_secondary": "#F5EFE7",     # Light beige
                "frame_bg": "#F0E9DC",         # Frame background
                "card_bg": "#FFFFFF",          # Card/panel background
                
                # Foregrounds
                "fg": "#3D3229",              # Dark warm brown text
                "fg_secondary": "#5C4E3F",     # Secondary text
                "fg_muted": "#8A7968",         # Muted text
                
                # Accents
                "accent_primary": "#B8956A",   # Warm tan
                "accent_secondary": "#9C8159", # Darker tan
                "accent_success": "#6B7D52",   # Olive green
                "accent_warning": "#C9974A",   # Warm amber
                "accent_danger": "#A65959",    # Muted red
                
                # Interactive elements
                "button_bg": "#E6DCC8",        # Button background
                "button_fg": "#3D3229",        # Button text
                "button_hover": "#D4C5B0",     # Button hover
                "button_active": "#B8956A",    # Active button
                
                # Inputs
                "input_bg": "#FFFFFF",         # Input background
                "input_fg": "#3D3229",         # Input text
                "input_border": "#D4C5B0",     # Input border
                
                # Special elements
                "highlight": "#B8956A",        # Highlight color
                "selection": "#E6DCC8",        # Selection background
                "border": "#D4C5B0",           # Border color
                "shadow": "#D4C5B0",           # Shadow color
                
                # Status colors
                "status_focused": "#6B7D52",   # Focused status
                "status_distracted": "#A65959" # Distracted status
            }

def check_system_compatibility() -> Dict[str, Any]:
    """Check system compatibility and available features."""
    compatibility = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_compatible": (3, 8) <= sys.version_info[:2] <= (3, 12),
        "platform": platform.system(),
        "pygame_available": PYGAME_AVAILABLE,
        "plyer_available": PLYER_AVAILABLE,
        "features": {
            "sound_alerts": PYGAME_AVAILABLE,
            "system_notifications": PLYER_AVAILABLE,
            "camera_support": True,
            "eye_tracking": True
        }
    }
    
    return compatibility
