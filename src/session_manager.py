"""
Session Manager - Study session tracking and data management
Compatible with Python 3.8-3.12
"""

import json
import csv
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import os

class SessionManager:
    """Manages study sessions, timers, and data logging."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.sessions_dir = self.data_dir / "sessions"
        self.preferences_dir = self.data_dir / "preferences"
        
        # Ensure directories exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.preferences_dir.mkdir(parents=True, exist_ok=True)
        
        # Session state
        self.current_session = None
        self.session_active = False
        self.paused = False
        
        # Timer thread
        self.timer_thread = None
        self.stop_timer = False
        
        # Session timing
        self.session_start_time = None
        self.pause_start_time = None
        self.total_pause_time = 0
        
        # Default settings
        self.default_settings = {
            "study_duration": 25,  # minutes
            "break_duration": 5,   # minutes
            "long_break_duration": 15,  # minutes
            "break_interval": 4,   # sessions before long break
            "auto_start_breaks": True,
            "show_notifications": True,
            "play_sounds": True,
            "track_focus": True
        }
        
        # Load user settings
        self.settings = self.load_settings()
        
        # Callbacks
        self.session_end_callback = None
        self.break_reminder_callback = None
        self.session_update_callback = None
        
        # Focus data
        self.focus_events = []
        
    def set_callbacks(self, session_end_callback: Optional[Callable] = None,
                     break_reminder_callback: Optional[Callable] = None,
                     session_update_callback: Optional[Callable] = None):
        """Set callback functions for session events."""
        self.session_end_callback = session_end_callback
        self.break_reminder_callback = break_reminder_callback  
        self.session_update_callback = session_update_callback
        
    def load_settings(self) -> Dict[str, Any]:
        """Load user settings from preferences file."""
        settings_file = self.preferences_dir / "settings.json"
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    settings = self.default_settings.copy()
                    settings.update(loaded_settings)
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return self.default_settings.copy()
        
    def save_settings(self):
        """Save current settings to preferences file."""
        settings_file = self.preferences_dir / "settings.json"
        
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def update_setting(self, key: str, value: Any):
        """Update a setting value."""
        self.settings[key] = value
        self.save_settings()
        
    def start_session(self, session_type: str = "study") -> bool:
        """Start a new study session."""
        if self.session_active:
            return False
            
        self.current_session = {
            "id": self.generate_session_id(),
            "type": session_type,
            "start_time": datetime.now(),
            "end_time": None,
            "duration_planned": self.settings["study_duration"] * 60,  # Convert to seconds
            "duration_actual": 0,
            "focus_data": [],
            "distraction_count": 0,
            "break_count": 0,
            "paused_time": 0,
            "notes": ""
        }
        
        self.session_active = True
        self.session_start_time = time.time()
        self.total_pause_time = 0
        self.focus_events.clear()
        
        # Start timer thread
        self.start_timer_thread()
        
        print(f"Started {session_type} session: {self.current_session['id']}")
        return True
        
    def pause_session(self):
        """Pause the current session."""
        if self.session_active and not self.paused:
            self.paused = True
            self.pause_start_time = time.time()
            print("Session paused")
            
    def resume_session(self):
        """Resume a paused session."""
        if self.session_active and self.paused:
            self.paused = False
            pause_duration = time.time() - self.pause_start_time
            self.total_pause_time += pause_duration
            self.pause_start_time = None
            print("Session resumed")
            
    def end_session(self) -> Dict[str, Any]:
        """End current session and save data."""
        if not self.session_active or not self.current_session:
            return {}
            
        self.session_active = False
        self.stop_timer = True
        
        # Calculate actual duration
        end_time = time.time()
        actual_duration = end_time - self.session_start_time - self.total_pause_time
        
        self.current_session.update({
            "end_time": datetime.now(),
            "duration_actual": actual_duration,
            "paused_time": self.total_pause_time,
            "focus_data": self.focus_events.copy()
        })
        
        # Save session to file
        session_data = self.save_session()
        
        # Reset state
        current_session = self.current_session
        self.current_session = None
        self.session_start_time = None
        
        print(f"Session ended: {current_session['id']}")
        return session_data
        
    def start_break(self, break_type: str = "short") -> bool:
        """Start a break period."""
        if break_type == "short":
            duration = self.settings["break_duration"]
        else:
            duration = self.settings["long_break_duration"]
            
        if self.current_session:
            self.current_session["break_count"] += 1
            
        # Could implement break timer here
        print(f"Started {break_type} break for {duration} minutes")
        return True
        
    def log_focus_event(self, focus_score: float, is_focused: bool):
        """Log a focus tracking event."""
        event = {
            "timestamp": time.time(),
            "focus_score": focus_score,
            "is_focused": is_focused
        }
        
        self.focus_events.append(event)
        
        if self.current_session:
            self.current_session["focus_data"].append(event)
            
    def log_distraction_event(self):
        """Log a distraction event."""
        if self.current_session:
            self.current_session["distraction_count"] += 1
            
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        if not self.session_active or not self.current_session:
            return {"active": False}
            
        current_time = time.time()
        elapsed_time = current_time - self.session_start_time - self.total_pause_time
        
        if self.paused:
            pause_duration = current_time - self.pause_start_time
        else:
            pause_duration = 0
            
        planned_duration = self.current_session["duration_planned"]
        remaining_time = max(0, planned_duration - elapsed_time)
        
        return {
            "active": True,
            "session_id": self.current_session["id"],
            "type": self.current_session["type"],
            "elapsed_time": elapsed_time,
            "remaining_time": remaining_time,
            "planned_duration": planned_duration,
            "paused": self.paused,
            "pause_duration": pause_duration,
            "total_pause_time": self.total_pause_time,
            "distraction_count": self.current_session.get("distraction_count", 0),
            "break_count": self.current_session.get("break_count", 0)
        }
        
    def start_timer_thread(self):
        """Start the session timer thread."""
        self.stop_timer = False
        self.timer_thread = threading.Thread(target=self.timer_loop)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
    def timer_loop(self):
        """Main timer loop running in separate thread."""
        while not self.stop_timer and self.session_active:
            time.sleep(1)
            
            if self.paused:
                continue
                
            status = self.get_session_status()
            
            # Check if session time is up
            if status.get("remaining_time", 0) <= 0:
                if self.session_end_callback:
                    self.session_end_callback()
                break
                
            # Callback for UI updates
            if self.session_update_callback:
                self.session_update_callback(status)
                
    def generate_session_id(self) -> str:
        """Generate unique session identifier."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
        
    def save_session(self) -> Dict[str, Any]:
        """Save current session data to file."""
        if not self.current_session:
            return {}
            
        session_file = self.sessions_dir / f"{self.current_session['id']}.json"
        
        # Convert datetime objects to strings for JSON serialization
        session_data = self.current_session.copy()
        session_data["start_time"] = session_data["start_time"].isoformat()
        if session_data["end_time"]:
            session_data["end_time"] = session_data["end_time"].isoformat()
            
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, default=str, ensure_ascii=False)
                
            # Also save to CSV for easy analysis
            self.save_session_csv(session_data)
            
        except Exception as e:
            print(f"Error saving session: {e}")
            
        return session_data
        
    def save_session_csv(self, session_data: Dict[str, Any]):
        """Save session data to CSV file."""
        csv_file = self.sessions_dir / "sessions_log.csv"
        
        headers = [
            "session_id", "type", "start_time", "end_time",
            "duration_planned", "duration_actual", "paused_time",
            "distraction_count", "break_count", "focus_percentage"
        ]
        
        # Calculate focus percentage
        focus_data = session_data.get("focus_data", [])
        if focus_data:
            focused_events = sum(1 for event in focus_data if event.get("is_focused", False))
            focus_percentage = (focused_events / len(focus_data)) * 100
        else:
            focus_percentage = 0
            
        row_data = [
            session_data["id"],
            session_data["type"],
            session_data["start_time"],
            session_data.get("end_time", ""),
            session_data["duration_planned"],
            session_data["duration_actual"],
            session_data["paused_time"],
            session_data["distraction_count"],
            session_data["break_count"],
            focus_percentage
        ]
        
        try:
            file_exists = csv_file.exists()
            
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                if not file_exists:
                    writer.writerow(headers)
                    
                writer.writerow(row_data)
                
        except Exception as e:
            print(f"Error saving CSV data: {e}")
            
    def load_session_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Load recent session history."""
        sessions = []
        
        try:
            session_files = list(self.sessions_dir.glob("session_*.json"))
            session_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for session_file in session_files[:limit]:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    sessions.append(session_data)
                    
        except Exception as e:
            print(f"Error loading session history: {e}")
            
        return sessions
        
    def generate_productivity_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate productivity report for specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        sessions = self.load_session_history(limit=200)
        
        # Filter recent sessions
        recent_sessions = []
        for session in sessions:
            try:
                start_time = datetime.fromisoformat(session["start_time"])
                if start_time >= cutoff_date:
                    recent_sessions.append(session)
            except (ValueError, KeyError):
                continue
                
        if not recent_sessions:
            return {"error": "No sessions found for the specified period"}
            
        # Calculate statistics
        total_sessions = len(recent_sessions)
        total_study_time = sum(s.get("duration_actual", 0) for s in recent_sessions)
        total_planned_time = sum(s.get("duration_planned", 0) for s in recent_sessions)
        total_distractions = sum(s.get("distraction_count", 0) for s in recent_sessions)
        
        # Calculate focus percentage
        all_focus_data = []
        for session in recent_sessions:
            all_focus_data.extend(session.get("focus_data", []))
            
        if all_focus_data:
            focused_events = sum(1 for event in all_focus_data if event.get("is_focused", False))
            overall_focus_percentage = (focused_events / len(all_focus_data)) * 100
        else:
            overall_focus_percentage = 0
            
        # Daily breakdown
        daily_stats = {}
        for session in recent_sessions:
            try:
                date_str = session["start_time"][:10]  # YYYY-MM-DD
                if date_str not in daily_stats:
                    daily_stats[date_str] = {
                        "sessions": 0,
                        "study_time": 0,
                        "distractions": 0
                    }
                    
                daily_stats[date_str]["sessions"] += 1
                daily_stats[date_str]["study_time"] += session.get("duration_actual", 0)
                daily_stats[date_str]["distractions"] += session.get("distraction_count", 0)
                
            except (KeyError, ValueError):
                continue
        
        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "total_study_time": total_study_time,
            "total_planned_time": total_planned_time,
            "average_session_duration": total_study_time / total_sessions if total_sessions > 0 else 0,
            "overall_focus_percentage": overall_focus_percentage,
            "total_distractions": total_distractions,
            "efficiency_percentage": (total_study_time / total_planned_time * 100) if total_planned_time > 0 else 0,
            "daily_stats": daily_stats
        }
        
    def cleanup(self):
        """Clean up resources."""
        self.stop_timer = True
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(timeout=1)
        print("Session manager cleaned up")
