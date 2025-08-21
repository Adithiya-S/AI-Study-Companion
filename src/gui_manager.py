"""
GUI Manager - Main application interface
Compatible with Python 3.8-3.12
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Import our modules
from focus_tracker import FocusTracker
from session_manager import SessionManager  
from study_materials import StudyMaterialsManager
from utils import SoundManager, NotificationManager, DataFormatter, ConfigManager

class StudyFocusGUI:
    """Main GUI application for the Study Focus App."""
    
    def __init__(self):
        # Initialize managers
        self.focus_tracker = FocusTracker()
        self.session_manager = SessionManager()
        self.materials_manager = StudyMaterialsManager()
        self.sound_manager = SoundManager()
        self.notification_manager = NotificationManager()
        self.config_manager = ConfigManager()
        
        # GUI components
        self.root = None
        self.notebook = None
        
        # State
        self.session_active = False
        self.camera_feed_active = False
        
        # Threading
        self.camera_thread = None
        self.gui_update_thread = None
        self.running = False
        
        # Set up callbacks
        self.setup_callbacks()
        
    def setup_callbacks(self):
        """Set up callbacks between components."""
        self.focus_tracker.set_callbacks(
            distraction_callback=self.on_distraction_detected
        )
        
        self.session_manager.set_callbacks(
            session_end_callback=self.on_session_end,
            session_update_callback=self.on_session_update
        )
        
    def initialize_gui(self):
        """Initialize the main GUI window."""
        self.root = tk.Tk()
        self.root.title("Study Focus App - Advanced Eye Tracking Assistant")
        self.root.geometry("1200x800")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Apply theme
        colors = self.config_manager.get_theme_colors()
        self.root.configure(bg=colors["bg"])
        
        # Create main interface
        self.create_main_interface()
        self.create_menu_bar()
        
        # Initialize camera
        if self.focus_tracker.initialize_camera():
            self.show_status("Camera initialized successfully")
        else:
            self.show_status("Warning: Camera not available")
            
        self.running = True
        
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self.start_session)
        file_menu.add_command(label="End Session", command=self.end_session)
        file_menu.add_separator()
        file_menu.add_command(label="Export Report", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_main_interface(self):
        """Create the main tabbed interface."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_focus_tab()
        self.create_materials_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
    def create_focus_tab(self):
        """Create the main focus session tab."""
        focus_frame = ttk.Frame(self.notebook)
        self.notebook.add(focus_frame, text="🎯 Focus Session")
        
        # Left panel - Camera and controls
        left_frame = ttk.Frame(focus_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Camera frame
        camera_frame = ttk.LabelFrame(left_frame, text="Camera Feed", padding="10")
        camera_frame.pack(fill=tk.BOTH, expand=True)
        
        self.camera_label = ttk.Label(camera_frame, text="Camera feed will appear here")
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Focus status
        status_frame = ttk.LabelFrame(left_frame, text="Focus Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.focus_status_label = ttk.Label(status_frame, text="Not tracking", 
                                           font=("Arial", 14, "bold"))
        self.focus_status_label.pack()
        
        self.focus_score_label = ttk.Label(status_frame, text="Focus Score: --")
        self.focus_score_label.pack()
        
        # Right panel - Session controls
        right_frame = ttk.Frame(focus_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)
        
        # Session controls
        session_frame = ttk.LabelFrame(right_frame, text="Session Control", padding="10")
        session_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Timer display
        self.timer_label = ttk.Label(session_frame, text="00:00", 
                                    font=("Arial", 24, "bold"))
        self.timer_label.pack(pady=10)
        
        # Duration setting
        duration_frame = ttk.Frame(session_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(duration_frame, text="Duration (min):").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value=str(self.session_manager.settings["study_duration"]))
        duration_entry = ttk.Entry(duration_frame, textvariable=self.duration_var, width=10)
        duration_entry.pack(side=tk.RIGHT)
        
        # Control buttons
        self.start_button = ttk.Button(session_frame, text="▶ Start Session", 
                                      command=self.start_session)
        self.start_button.pack(fill=tk.X, pady=2)
        
        self.pause_button = ttk.Button(session_frame, text="⏸ Pause", 
                                      command=self.pause_session, state=tk.DISABLED)
        self.pause_button.pack(fill=tk.X, pady=2)
        
        self.end_button = ttk.Button(session_frame, text="⏹ End Session", 
                                    command=self.end_session, state=tk.DISABLED)
        self.end_button.pack(fill=tk.X, pady=2)
        
        # Session stats
        stats_frame = ttk.LabelFrame(right_frame, text="Session Statistics", padding="10")
        stats_frame.pack(fill=tk.X)
        
        self.elapsed_time_label = ttk.Label(stats_frame, text="Elapsed: 0:00")
        self.elapsed_time_label.pack(anchor=tk.W)
        
        self.distraction_count_label = ttk.Label(stats_frame, text="Distractions: 0")
        self.distraction_count_label.pack(anchor=tk.W)
        
    def create_materials_tab(self):
        """Create the study materials tab."""
        materials_frame = ttk.Frame(self.notebook)
        self.notebook.add(materials_frame, text="📚 Study Materials")
        
        # Quick links section
        links_frame = ttk.LabelFrame(materials_frame, text="Quick Links", padding="10")
        links_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Links listbox
        self.links_listbox = tk.Listbox(links_frame)
        self.links_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Populate links
        for link in self.materials_manager.materials["quick_links"]:
            self.links_listbox.insert(tk.END, f"{link['name']} - {link['url']}")
            
        # Links buttons
        links_buttons = ttk.Frame(links_frame)
        links_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(links_buttons, text="Open Link", 
                  command=self.open_selected_link).pack(side=tk.LEFT, padx=5)
        ttk.Button(links_buttons, text="Add Link", 
                  command=self.add_link).pack(side=tk.LEFT, padx=5)
        
        # Study techniques section  
        techniques_frame = ttk.LabelFrame(materials_frame, text="Study Techniques", padding="10")
        techniques_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        techniques_text = tk.Text(techniques_frame, height=10, wrap=tk.WORD)
        techniques_text.pack(fill=tk.BOTH, expand=True)
        
        # Add study techniques
        for technique in self.materials_manager.materials["study_techniques"]:
            techniques_text.insert(tk.END, f"{technique['name']}\n")
            techniques_text.insert(tk.END, f"{technique['description']}\n\n")
            
        techniques_text.config(state=tk.DISABLED)
        
    def create_reports_tab(self):
        """Create the reports and statistics tab."""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📊 Reports")
        
        # Report controls
        controls_frame = ttk.Frame(reports_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Report Period:").pack(side=tk.LEFT)
        
        self.report_period_var = tk.StringVar(value="7")
        period_combo = ttk.Combobox(controls_frame, textvariable=self.report_period_var,
                                   values=["1", "7", "14", "30"], width=10)
        period_combo.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(controls_frame, text="Generate Report", 
                  command=self.generate_report).pack(side=tk.LEFT, padx=10)
        
        # Report display
        self.report_text = tk.Text(reports_frame, wrap=tk.WORD)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Generate initial report
        self.generate_report()
        
    def create_settings_tab(self):
        """Create the settings tab."""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Focus tracking settings
        focus_frame = ttk.LabelFrame(settings_frame, text="Focus Tracking", padding="10")
        focus_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Sensitivity setting
        ttk.Label(focus_frame, text="Detection Sensitivity:").grid(row=0, column=0, sticky=tk.W)
        self.sensitivity_var = tk.StringVar(value=self.config_manager.get("focus_tracking.sensitivity"))
        sensitivity_combo = ttk.Combobox(focus_frame, textvariable=self.sensitivity_var,
                                       values=["low", "medium", "high"])
        sensitivity_combo.grid(row=0, column=1, padx=10, sticky=tk.W)
        
        # Camera settings
        camera_frame = ttk.LabelFrame(settings_frame, text="Camera", padding="10")
        camera_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(camera_frame, text="Camera Index:").grid(row=0, column=0, sticky=tk.W)
        self.camera_index_var = tk.StringVar(value=str(self.config_manager.get("camera.device_index")))
        camera_entry = ttk.Entry(camera_frame, textvariable=self.camera_index_var, width=10)
        camera_entry.grid(row=0, column=1, padx=10, sticky=tk.W)
        
        # Notification settings
        notify_frame = ttk.LabelFrame(settings_frame, text="Notifications", padding="10")
        notify_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.sounds_var = tk.BooleanVar(value=self.config_manager.get("notifications.sounds"))
        ttk.Checkbutton(notify_frame, text="Enable Sounds", variable=self.sounds_var).pack(anchor=tk.W)
        
        self.notifications_var = tk.BooleanVar(value=self.config_manager.get("notifications.enabled"))
        ttk.Checkbutton(notify_frame, text="Show Notifications", variable=self.notifications_var).pack(anchor=tk.W)
        
        # Save settings button
        ttk.Button(settings_frame, text="Save Settings", 
                  command=self.save_settings).pack(pady=20)
        
    # Event handlers
    def start_session(self):
        """Start a study session."""
        if self.session_active:
            return
            
        try:
            duration = int(self.duration_var.get())
            if duration <= 0:
                messagebox.showerror("Invalid Duration", "Duration must be a positive number")
                return
        except ValueError:
            messagebox.showerror("Invalid Duration", "Please enter a valid number")
            return
            
        # Update session manager settings
        self.session_manager.settings["study_duration"] = duration
        
        # Start session
        if self.session_manager.start_session():
            self.session_active = True
            
            # Start focus tracking
            self.focus_tracker.start_tracking()
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.end_button.config(state=tk.NORMAL)
            
            self.show_status(f"Study session started - {duration} minutes")
            
            # Start GUI update thread
            self.start_gui_update_thread()
            
    def pause_session(self):
        """Pause/resume the session."""
        if not self.session_active:
            return
            
        if self.session_manager.paused:
            self.session_manager.resume_session()
            self.pause_button.config(text="⏸ Pause")
            self.show_status("Session resumed")
        else:
            self.session_manager.pause_session()
            self.pause_button.config(text="▶ Resume")
            self.show_status("Session paused")
            
    def end_session(self):
        """End the current session."""
        if not self.session_active:
            return
            
        # End session
        session_data = self.session_manager.end_session()
        self.focus_tracker.stop_tracking()
        
        self.session_active = False
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="⏸ Pause")
        self.end_button.config(state=tk.DISABLED)
        
        self.show_status("Session completed")
        
        # Show session summary
        if session_data:
            self.show_session_summary(session_data)
            
    def on_distraction_detected(self):
        """Handle distraction detection."""
        if self.session_active:
            self.session_manager.log_distraction_event()
            
            if self.sounds_var.get():
                self.sound_manager.play_sound("distraction_alert")
                
            if self.notifications_var.get():
                self.notification_manager.show_notification(
                    "Focus Alert", 
                    "You seem distracted. Return to your studies!"
                )
                
    def on_session_end(self):
        """Handle automatic session end."""
        self.end_session()
        
    def on_session_update(self, status):
        """Handle session status updates."""
        if hasattr(self, 'timer_label'):
            remaining = status.get('remaining_time', 0)
            self.timer_label.config(text=DataFormatter.format_time(remaining))
            
        if hasattr(self, 'elapsed_time_label'):
            elapsed = status.get('elapsed_time', 0)
            self.elapsed_time_label.config(text=f"Elapsed: {DataFormatter.format_time(elapsed)}")
            
        if hasattr(self, 'distraction_count_label'):
            count = status.get('distraction_count', 0)
            self.distraction_count_label.config(text=f"Distractions: {count}")
            
    def start_gui_update_thread(self):
        """Start the GUI update thread."""
        if not self.gui_update_thread or not self.gui_update_thread.is_alive():
            self.gui_update_thread = threading.Thread(target=self.gui_update_loop)
            self.gui_update_thread.daemon = True
            self.gui_update_thread.start()
            
    def gui_update_loop(self):
        """Main GUI update loop."""
        while self.running and self.session_active:
            try:
                # Update focus tracking display
                if self.focus_tracker.camera and self.focus_tracker.is_tracking:
                    frame = self.focus_tracker.process_frame()
                    if frame is not None:
                        # Update focus status
                        focus_data = self.focus_tracker.analyze_focus_level(frame)
                        self.root.after(0, self.update_focus_display, focus_data)
                        
                        # Log focus data
                        self.session_manager.log_focus_event(
                            focus_data['focus_score'], 
                            focus_data['is_focused']
                        )
                        
                time.sleep(0.1)  # Update 10 times per second
                
            except Exception as e:
                print(f"GUI update error: {e}")
                break
                
    def update_focus_display(self, focus_data):
        """Update focus status display."""
        if focus_data['is_focused']:
            self.focus_status_label.config(text="🎯 FOCUSED", foreground="green")
        else:
            self.focus_status_label.config(text="😵 DISTRACTED", foreground="red")
            
        self.focus_score_label.config(text=f"Focus Score: {focus_data['focus_score']:.2f}")
        
    def generate_report(self):
        """Generate productivity report."""
        try:
            days = int(self.report_period_var.get())
            report = self.session_manager.generate_productivity_report(days)
            
            if "error" in report:
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, f"No data available for the last {days} days.")
                return
                
            # Format report
            report_text = f"""PRODUCTIVITY REPORT - Last {days} Days
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 OVERVIEW
Total Sessions: {report['total_sessions']}
Total Study Time: {DataFormatter.format_duration(report['total_study_time'])}
Average Session: {DataFormatter.format_duration(report['average_session_duration'])}
Overall Focus: {report['overall_focus_percentage']:.1f}%
Efficiency: {report['efficiency_percentage']:.1f}%
Total Distractions: {report['total_distractions']}

📅 DAILY BREAKDOWN
"""
            for date, stats in report['daily_stats'].items():
                report_text += f"{date}: {stats['sessions']} sessions, "
                report_text += f"{DataFormatter.format_duration(stats['study_time'])}, "
                report_text += f"{stats['distractions']} distractions\n"
                
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, report_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
            
    def show_session_summary(self, session_data):
        """Show session completion summary."""
        stats = self.focus_tracker.get_session_stats()
        
        summary = f"""Session Completed!

Duration: {DataFormatter.format_time(session_data.get('duration_actual', 0))}
Focus Percentage: {stats.get('focus_percentage', 0):.1f}%
Distractions: {session_data.get('distraction_count', 0)}
Average Focus Score: {stats.get('average_focus_score', 0):.2f}

Great job studying! 🎯"""
        
        messagebox.showinfo("Session Complete", summary)
        
    # Utility methods
    def open_selected_link(self):
        """Open selected quick link."""
        selection = self.links_listbox.curselection()
        if selection:
            index = selection[0]
            link = self.materials_manager.materials["quick_links"][index]
            self.materials_manager.open_quick_link(link["name"])
            
    def add_link(self):
        """Add a new quick link."""
        dialog = AddLinkDialog(self.root)
        if dialog.result:
            name, url, category = dialog.result
            if self.materials_manager.add_quick_link(name, url, category):
                # Refresh links display
                self.links_listbox.delete(0, tk.END)
                for link in self.materials_manager.materials["quick_links"]:
                    self.links_listbox.insert(tk.END, f"{link['name']} - {link['url']}")
                    
    def save_settings(self):
        """Save application settings."""
        # Update configuration
        self.config_manager.set("focus_tracking.sensitivity", self.sensitivity_var.get())
        self.config_manager.set("camera.device_index", int(self.camera_index_var.get()))
        self.config_manager.set("notifications.sounds", self.sounds_var.get())
        self.config_manager.set("notifications.enabled", self.notifications_var.get())
        
        # Update component settings
        self.sound_manager.set_enabled(self.sounds_var.get())
        self.notification_manager.set_enabled(self.notifications_var.get())
        
        messagebox.showinfo("Settings", "Settings saved successfully!")
        
    def export_report(self):
        """Export productivity report to file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                report_content = self.report_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                messagebox.showinfo("Export", f"Report exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report: {e}")
                
    def show_about(self):
        """Show about dialog."""
        about_text = """Study Focus App - Advanced Eye Tracking Assistant

Python 3.8-3.12 Compatible Version

Features:
• Real-time eye tracking with MediaPipe
• Focus detection and distraction alerts  
• Study session management
• Productivity analytics
• Study materials and techniques

Built with Python, OpenCV, MediaPipe, and tkinter"""
        
        messagebox.showinfo("About Study Focus App", about_text)
        
    def show_status(self, message):
        """Update status bar."""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            
    def on_closing(self):
        """Handle application closing."""
        if self.session_active:
            if messagebox.askyesno("Session Active", "End current session and exit?"):
                self.end_session()
            else:
                return
                
        self.running = False
        
        # Clean up resources
        self.focus_tracker.cleanup()
        self.session_manager.cleanup()
        
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """Run the application."""
        self.initialize_gui()
        
        # Set close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start main loop
        self.root.mainloop()

class AddLinkDialog:
    """Dialog for adding new quick links."""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Quick Link")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Form fields
        ttk.Label(self.dialog, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="URL:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.url_var, width=30).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.dialog, text="Category:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.category_var = tk.StringVar(value="Custom")
        ttk.Entry(self.dialog, textvariable=self.category_var, width=30).grid(row=2, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", command=self.add_link).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
    def add_link(self):
        """Add the link and close dialog."""
        name = self.name_var.get().strip()
        url = self.url_var.get().strip()
        category = self.category_var.get().strip()
        
        if name and url:
            self.result = (name, url, category)
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Please enter both name and URL")
