"""
Modern GUI Manager - Complete UI Redesign with Animations
Compatible with Python 3.8-3.12
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import os
from datetime import datetime
from typing import Optional, Dict, Any
import cv2
from PIL import Image, ImageTk

# Import our modules
from focus_tracker import FocusTracker
from session_manager import SessionManager  
from study_materials import StudyMaterialsManager
from ai_assistant import AIAssistant
from utils import SoundManager, NotificationManager, DataFormatter, ConfigManager
from animations import (AnimationEngine, CircularProgress, ModernButton, 
                        ToastNotification, StatCard)


class ModernStudyFocusGUI:
    """Modern GUI with sidebar navigation and animated components."""
    
    def __init__(self):
        # Initialize managers
        self.focus_tracker = FocusTracker()
        self.session_manager = SessionManager()
        self.materials_manager = StudyMaterialsManager()
        self.ai_assistant = AIAssistant()
        self.sound_manager = SoundManager()
        self.notification_manager = NotificationManager()
        self.config_manager = ConfigManager()
        
        # GUI components
        self.root = None
        self.animation_engine = None
        self.current_view = "dashboard"
        
        # State
        self.session_active = False
        self.camera_feed_active = False
        
        # Threading
        self.camera_thread = None
        self.gui_update_thread = None
        self.running = False
        
        # Theme colors
        self.colors = {}
        
        # View containers
        self.views = {}
        self.sidebar_buttons = {}
        
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
        """Initialize the modern GUI window."""
        self.root = tk.Tk()
        self.root.title("Study Focus - Eye Tracking Assistant")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Get theme colors
        self.colors = self.config_manager.get_theme_colors()
        self.root.configure(bg=self.colors["bg"])
        
        # Initialize animation engine
        self.animation_engine = AnimationEngine(self.root)
        
        # Create main layout
        self.create_modern_layout()
        
        # Initialize camera with config index
        camera_index = self.config_manager.get("camera.device_index", 0)
        if self.focus_tracker.initialize_camera(camera_index):
            self.show_toast("Camera initialized successfully")
        else:
            self.show_toast("Warning: Camera not available")
        
        # Set focus tracking sensitivity from config
        sensitivity = self.config_manager.get("focus_tracking.sensitivity", "medium")
        self.focus_tracker.set_sensitivity(sensitivity)
        
        # Set face outline visibility from config
        show_outline = self.config_manager.get("focus_tracking.show_outline", True)
        self.focus_tracker.set_show_outline(show_outline)
            
        self.running = True
        
    def create_modern_layout(self):
        """Create the modern sidebar + content area layout."""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.create_sidebar(main_container)
        
        # Content area
        self.content_area = tk.Frame(main_container, bg=self.colors["bg"])
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create all views
        self.create_dashboard_view()
        self.create_materials_view()
        self.create_analytics_view()
        self.create_settings_view()
        
        # Show dashboard by default
        self.show_view("dashboard")
        
    def create_sidebar(self, parent):
        """Create modern sidebar navigation."""
        sidebar = tk.Frame(parent, bg=self.colors["bg_secondary"], width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # App title/logo
        title_frame = tk.Frame(sidebar, bg=self.colors["bg_secondary"], height=100)
        title_frame.pack(fill=tk.X, pady=20)
        title_frame.pack_propagate(False)
        
        app_title = tk.Label(title_frame, text="Study Focus", 
                            bg=self.colors["bg_secondary"],
                            fg=self.colors["accent_primary"],
                            font=("Arial", 24, "bold"))
        app_title.pack(pady=10)
        
        subtitle = tk.Label(title_frame, text="Eye Tracking Assistant", 
                           bg=self.colors["bg_secondary"],
                           fg=self.colors["fg_secondary"],
                           font=("Arial", 10))
        subtitle.pack()
        
        # Navigation buttons
        nav_frame = tk.Frame(sidebar, bg=self.colors["bg_secondary"])
        nav_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Study Materials", "materials"),
            ("Analytics", "analytics"),
            ("Settings", "settings")
        ]
        
        for label, view_name in nav_items:
            self.create_nav_button(nav_frame, label, view_name)
        
    def create_nav_button(self, parent, text: str, view_name: str):
        """Create a navigation button."""
        btn_frame = tk.Frame(parent, bg=self.colors["bg_secondary"])
        btn_frame.pack(fill=tk.X, padx=15, pady=5)
        
        is_active = view_name == self.current_view
        bg = self.colors["accent_primary"] if is_active else self.colors["bg_secondary"]
        fg = self.colors["bg"] if is_active else self.colors["fg"]
        
        btn = tk.Label(btn_frame, text=text, bg=bg, fg=fg,
                      font=("Arial", 12, "bold" if is_active else "normal"),
                      cursor="hand2", padx=20, pady=15)
        btn.pack(fill=tk.X)
        
        # Store reference
        self.sidebar_buttons[view_name] = btn
        
        # Bind click
        btn.bind("<Button-1>", lambda e: self.show_view(view_name))
        
        # Hover effect
        if not is_active:
            btn.bind("<Enter>", lambda e: btn.config(bg=self.colors["button_hover"]))
            btn.bind("<Leave>", lambda e: btn.config(bg=self.colors["bg_secondary"]))
    
    def show_view(self, view_name: str):
        """Switch to a different view with animation."""
        if view_name == self.current_view:
            return
        
        # Update sidebar buttons
        for name, btn in self.sidebar_buttons.items():
            if name == view_name:
                btn.config(bg=self.colors["accent_primary"], 
                          fg=self.colors["bg"],
                          font=("Arial", 12, "bold"))
            else:
                btn.config(bg=self.colors["bg_secondary"], 
                          fg=self.colors["fg"],
                          font=("Arial", 12, "normal"))
        
        # Hide all views
        for view in self.views.values():
            view.pack_forget()
        
        # Show selected view
        self.views[view_name].pack(fill=tk.BOTH, expand=True)
        self.current_view = view_name
        
    def create_dashboard_view(self):
        """Create the main dashboard view."""
        dashboard = tk.Frame(self.content_area, bg=self.colors["bg"])
        self.views["dashboard"] = dashboard
        
        # Scrollable container
        canvas = tk.Canvas(dashboard, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(dashboard, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header = tk.Frame(scrollable_frame, bg=self.colors["bg"])
        header.pack(fill=tk.X, padx=40, pady=30)
        
        title = tk.Label(header, text="Dashboard", bg=self.colors["bg"],
                        fg=self.colors["fg"], font=("Arial", 32, "bold"))
        title.pack(side=tk.LEFT)
        
        # Session Status Banner
        self.create_session_control_card(scrollable_frame)
        
        # Stats Cards Row
        stats_container = tk.Frame(scrollable_frame, bg=self.colors["bg"])
        stats_container.pack(fill=tk.X, padx=40, pady=20)
        
        # Create stat cards
        self.stat_sessions = StatCard(stats_container, "Total Sessions", "0",
                                      bg_color=self.colors["card_bg"])
        self.stat_sessions.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.stat_time = StatCard(stats_container, "Study Time", "0h 0m",
                                 bg_color=self.colors["card_bg"])
        self.stat_time.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.stat_focus = StatCard(stats_container, "Focus Score", "0%",
                                  bg_color=self.colors["card_bg"])
        self.stat_focus.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Main content: Two columns
        main_content = tk.Frame(scrollable_frame, bg=self.colors["bg"])
        main_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Left column - Session controls
        left_col = tk.Frame(main_content, bg=self.colors["bg"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        self.create_timer_card(left_col)
        self.create_focus_status_card(left_col)
        
        # Right column - Camera feed
        right_col = tk.Frame(main_content, bg=self.colors["bg"])
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_camera_card(right_col)
        
        # Pack canvas
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update stats
        self.update_dashboard_stats()
        
    def create_session_control_card(self, parent):
        """Create the main session control card."""
        card = tk.Frame(parent, bg=self.colors["card_bg"])
        card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        content = tk.Frame(card, bg=self.colors["card_bg"])
        content.pack(fill=tk.X, padx=30, pady=25)
        
        # Left: Status info
        left = tk.Frame(content, bg=self.colors["card_bg"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.session_status_label = tk.Label(left, text="Ready to Study", 
                                            bg=self.colors["card_bg"],
                                            fg=self.colors["fg"],
                                            font=("Arial", 24, "bold"))
        self.session_status_label.pack(anchor=tk.W)
        
        self.session_subtitle = tk.Label(left, text="Start a new session to begin tracking", 
                                        bg=self.colors["card_bg"],
                                        fg=self.colors["fg_secondary"],
                                        font=("Arial", 12))
        self.session_subtitle.pack(anchor=tk.W, pady=(5, 0))
        
        # Right: Action buttons
        right = tk.Frame(content, bg=self.colors["card_bg"])
        right.pack(side=tk.RIGHT)
        
        self.start_session_btn = ModernButton(right, text="Start Session", 
                                             command=self.start_session,
                                             width=180, height=55,
                                             bg_color=self.colors["accent_primary"],
                                             text_color="#FFFFFF",
                                             hover_color=self.colors["accent_secondary"],
                                             corner_radius=14)
        self.start_session_btn.config(bg=self.colors["card_bg"])
        self.start_session_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_session_btn = ModernButton(right, text="Pause", 
                                             command=self.pause_session,
                                             width=120, height=55,
                                             bg_color="#64748B",
                                             text_color="#FFFFFF",
                                             hover_color="#94A3B8",
                                             corner_radius=14)
        self.pause_session_btn.config(bg=self.colors["card_bg"], state=tk.DISABLED)
        self.pause_session_btn.pack(side=tk.LEFT, padx=5)
        
        self.end_session_btn = ModernButton(right, text="End", 
                                           command=self.end_session,
                                           width=120, height=55,
                                           bg_color=self.colors["accent_danger"],
                                           text_color="#FFFFFF",
                                           hover_color="#DC2626",
                                           corner_radius=14)
        self.end_session_btn.config(bg=self.colors["card_bg"], state=tk.DISABLED)
        self.end_session_btn.pack(side=tk.LEFT, padx=5)
        
    def create_timer_card(self, parent):
        """Create timer display card with circular progress."""
        card = tk.Frame(parent, bg=self.colors["card_bg"])
        card.pack(fill=tk.X, pady=(0, 20))
        
        # Header
        header = tk.Frame(card, bg=self.colors["card_bg"])
        header.pack(fill=tk.X, padx=30, pady=(20, 10))
        
        tk.Label(header, text="Session Timer", bg=self.colors["card_bg"],
                fg=self.colors["fg"], font=("Arial", 18, "bold")).pack(anchor=tk.W)
        
        # Duration setting
        duration_frame = tk.Frame(card, bg=self.colors["card_bg"])
        duration_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(duration_frame, text="Duration (minutes):", bg=self.colors["card_bg"],
                fg=self.colors["fg_secondary"], font=("Arial", 11)).pack(side=tk.LEFT)
        
        self.duration_var = tk.StringVar(value=str(self.session_manager.settings["study_duration"]))
        duration_entry = tk.Entry(duration_frame, textvariable=self.duration_var,
                                 bg=self.colors["input_bg"], fg=self.colors["input_fg"],
                                 font=("Arial", 11), width=8, insertbackground=self.colors["fg"])
        duration_entry.pack(side=tk.LEFT, padx=10)
        
        # Circular progress
        progress_frame = tk.Frame(card, bg=self.colors["card_bg"])
        progress_frame.pack(pady=30)
        
        self.timer_progress = CircularProgress(progress_frame, size=250, line_width=25,
                                              color=self.colors["accent_primary"],
                                              bg_color=self.colors["bg_secondary"])
        self.timer_progress.config(bg=self.colors["card_bg"])
        self.timer_progress.pack()
        
        # Time display overlay
        self.timer_display = tk.Label(card, text="00:00", bg=self.colors["card_bg"],
                                     fg=self.colors["fg"], font=("Arial", 48, "bold"))
        self.timer_display.place(in_=self.timer_progress, relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Session stats
        stats_frame = tk.Frame(card, bg=self.colors["card_bg"])
        stats_frame.pack(fill=tk.X, padx=30, pady=(10, 25))
        
        left_stats = tk.Frame(stats_frame, bg=self.colors["card_bg"])
        left_stats.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.elapsed_label = tk.Label(left_stats, text="Elapsed: 0:00", bg=self.colors["card_bg"],
                                     fg=self.colors["fg_secondary"], font=("Arial", 11))
        self.elapsed_label.pack(anchor=tk.W)
        
        right_stats = tk.Frame(stats_frame, bg=self.colors["card_bg"])
        right_stats.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.distraction_label = tk.Label(right_stats, text="Distractions: 0", 
                                         bg=self.colors["card_bg"],
                                         fg=self.colors["fg_secondary"], font=("Arial", 11))
        self.distraction_label.pack(anchor=tk.E)
        
    def create_focus_status_card(self, parent):
        """Create live focus status indicator."""
        card = tk.Frame(parent, bg=self.colors["card_bg"])
        card.pack(fill=tk.X, pady=(0, 20))
        
        # Header
        header = tk.Frame(card, bg=self.colors["card_bg"])
        header.pack(fill=tk.X, padx=30, pady=(20, 10))
        
        tk.Label(header, text="Focus Status", bg=self.colors["card_bg"],
                fg=self.colors["fg"], font=("Arial", 18, "bold")).pack(anchor=tk.W)
        
        # Status indicator
        status_frame = tk.Frame(card, bg=self.colors["card_bg"])
        status_frame.pack(pady=30)
        
        self.focus_indicator = tk.Canvas(status_frame, width=120, height=120,
                                        bg=self.colors["card_bg"], highlightthickness=0)
        self.focus_indicator.pack()
        
        # Draw circle
        self.focus_circle = self.focus_indicator.create_oval(10, 10, 110, 110,
                                                             fill=self.colors["fg_muted"],
                                                             outline="")
        
        # Status text
        self.focus_status_text = tk.Label(card, text="Not Tracking", bg=self.colors["card_bg"],
                                         fg=self.colors["fg"], font=("Arial", 16, "bold"))
        self.focus_status_text.pack(pady=(10, 20))
        
        # Focus score
        self.focus_score_label = tk.Label(card, text="Focus Score: --", bg=self.colors["card_bg"],
                                         fg=self.colors["fg_secondary"], font=("Arial", 12))
        self.focus_score_label.pack(pady=(0, 25))
        
    def create_camera_card(self, parent):
        """Create camera feed display."""
        card = tk.Frame(parent, bg=self.colors["card_bg"])
        card.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(card, bg=self.colors["card_bg"])
        header.pack(fill=tk.X, padx=30, pady=(20, 10))
        
        tk.Label(header, text="Camera Feed", bg=self.colors["card_bg"],
                fg=self.colors["fg"], font=("Arial", 18, "bold")).pack(anchor=tk.W)
        
        # Camera display
        camera_container = tk.Frame(card, bg=self.colors["bg_secondary"])
        camera_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(10, 25))
        
        self.camera_label = tk.Label(camera_container, text="Camera feed will appear here\nwhen session starts",
                                     bg=self.colors["bg_secondary"], fg=self.colors["fg_muted"],
                                     font=("Arial", 12), justify=tk.CENTER)
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def create_materials_view(self):
        """Create study materials view with AI assistant."""
        materials = tk.Frame(self.content_area, bg=self.colors["bg"])
        self.views["materials"] = materials
        
        # Create notebook for tabs
        notebook = ttk.Notebook(materials)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tab 1: Quick Links
        links_tab = tk.Frame(notebook, bg=self.colors["bg"])
        notebook.add(links_tab, text="Quick Links")
        
        # Header for links tab
        header = tk.Frame(links_tab, bg=self.colors["bg"])
        header.pack(fill=tk.X, padx=40, pady=30)
        
        title = tk.Label(header, text="Study Materials", bg=self.colors["bg"],
                        fg=self.colors["fg"], font=("Arial", 32, "bold"))
        title.pack(side=tk.LEFT)
        
        add_btn = ModernButton(header, text="Add Link", command=self.add_link,
                              width=150, height=45,
                              bg_color=self.colors["accent_primary"],
                              text_color=self.colors["bg"],
                              hover_color=self.colors["accent_secondary"])
        add_btn.config(bg=self.colors["bg"])
        add_btn.pack(side=tk.RIGHT)
        
        # Materials grid
        self.materials_container = tk.Frame(links_tab, bg=self.colors["bg"])
        self.materials_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 30))
        
        self.load_materials()
        
        # Tab 2: AI Assistant
        ai_tab = tk.Frame(notebook, bg=self.colors["bg"])
        notebook.add(ai_tab, text="AI Assistant")
        self.create_ai_assistant_tab(ai_tab)
        
        # Tab 3: Uploaded Materials
        uploads_tab = tk.Frame(notebook, bg=self.colors["bg"])
        notebook.add(uploads_tab, text="My Uploads")
        self.create_uploads_tab(uploads_tab)
        
    def load_materials(self):
        """Load and display study materials as cards."""
        # Clear existing
        for widget in self.materials_container.winfo_children():
            widget.destroy()
        
        # Create grid
        row = 0
        col = 0
        for idx, link in enumerate(self.materials_manager.materials["quick_links"]):
            card = tk.Frame(self.materials_container, bg=self.colors["card_bg"])
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Card content
            content = tk.Frame(card, bg=self.colors["card_bg"])
            content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
            
            name_label = tk.Label(content, text=link['name'], bg=self.colors["card_bg"],
                                 fg=self.colors["fg"], font=("Arial", 14, "bold"),
                                 wraplength=250, justify=tk.LEFT)
            name_label.pack(anchor=tk.W)
            
            url_label = tk.Label(content, text=link['url'], bg=self.colors["card_bg"],
                                fg=self.colors["fg_secondary"], font=("Arial", 10),
                                wraplength=250, justify=tk.LEFT)
            url_label.pack(anchor=tk.W, pady=(5, 15))
            
            open_btn = ModernButton(content, text="Open", 
                                   command=lambda l=link: self.materials_manager.open_quick_link(l["name"]),
                                   width=100, height=35,
                                   bg_color=self.colors["accent_primary"],
                                   text_color=self.colors["bg"])
            open_btn.config(bg=self.colors["card_bg"])
            open_btn.pack(anchor=tk.W)
            
            # Hover effect
            card.bind("<Enter>", lambda e, c=card: c.config(bg=self.colors["button_hover"]))
            card.bind("<Leave>", lambda e, c=card: c.config(bg=self.colors["card_bg"]))
            
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
        
        # Configure grid
        for i in range(3):
            self.materials_container.columnconfigure(i, weight=1, minsize=300)
    
    def create_ai_assistant_tab(self, parent):
        """Create AI assistant interface."""
        # Header
        header = tk.Frame(parent, bg=self.colors["bg"])
        header.pack(fill=tk.X, padx=30, pady=20)
        
        title = tk.Label(header, text="AI Study Assistant", bg=self.colors["bg"],
                        fg=self.colors["fg"], font=("Arial", 28, "bold"))
        title.pack(side=tk.LEFT)
        
        # Button frame for Recent Chats and Clear
        btn_container = tk.Frame(header, bg=self.colors["bg"])
        btn_container.pack(side=tk.RIGHT)
        
        # Recent chats button
        recent_btn = ModernButton(btn_container, text="📜 Recent Chats", 
                                 command=self.show_recent_chats,
                                 width=150, height=40,
                                 bg_color=self.colors["accent_secondary"],
                                 text_color=self.colors["bg"])
        recent_btn.config(bg=self.colors["bg"])
        recent_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear chat button
        clear_btn = ModernButton(btn_container, text="🔄 New Chat", 
                                command=self.start_new_chat,
                                width=120, height=40,
                                bg_color="#64748B",
                                text_color="#FFFFFF",
                                corner_radius=12)
        clear_btn.config(bg=self.colors["bg"])
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Show status indicator if AI not configured
        if not self.ai_assistant.is_configured():
            status_label = tk.Label(header, text="⚠️ AI Not Available", 
                                   bg=self.colors["bg"],
                                   fg="#ff6b6b",
                                   font=("Arial", 11, "italic"))
            status_label.pack(side=tk.RIGHT, padx=10)
        else:
            status_label = tk.Label(header, text="✓ AI Ready", 
                                   bg=self.colors["bg"],
                                   fg="#51cf66",
                                   font=("Arial", 11))
            status_label.pack(side=tk.RIGHT, padx=10)
        
        # Chat container
        chat_container = tk.Frame(parent, bg=self.colors["card_bg"])
        chat_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        # Chat display
        chat_frame = tk.Frame(chat_container, bg=self.colors["card_bg"])
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD,
            bg=self.colors["input_bg"],
            fg=self.colors["input_fg"],
            font=("Arial", 11),
            insertbackground=self.colors["fg"],
            relief=tk.FLAT, padx=15, pady=15,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for styling
        self.chat_display.tag_config("question", foreground=self.colors["accent_primary"], 
                                    font=("Arial", 11, "bold"))
        self.chat_display.tag_config("answer", foreground=self.colors["fg"])
        self.chat_display.tag_config("system", foreground=self.colors["fg_secondary"], 
                                    font=("Arial", 10, "italic"))
        
        # Input area
        input_frame = tk.Frame(chat_container, bg=self.colors["card_bg"])
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Mode selector
        mode_frame = tk.Frame(input_frame, bg=self.colors["card_bg"])
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(mode_frame, text="Mode:", bg=self.colors["card_bg"],
                fg=self.colors["fg"], font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.ai_mode_var = tk.StringVar(value="internet")
        
        internet_rb = tk.Radiobutton(mode_frame, text="🌐 Internet", 
                                    variable=self.ai_mode_var, value="internet",
                                    bg=self.colors["card_bg"], fg=self.colors["fg"],
                                    selectcolor=self.colors["accent_primary"],
                                    font=("Arial", 10))
        internet_rb.pack(side=tk.LEFT, padx=5)
        
        materials_rb = tk.Radiobutton(mode_frame, text="📚 My Materials Only", 
                                     variable=self.ai_mode_var, value="materials",
                                     bg=self.colors["card_bg"], fg=self.colors["fg"],
                                     selectcolor=self.colors["accent_primary"],
                                     font=("Arial", 10))
        materials_rb.pack(side=tk.LEFT, padx=5)
        
        # Question input
        question_frame = tk.Frame(input_frame, bg=self.colors["card_bg"])
        question_frame.pack(fill=tk.X)
        
        self.question_entry = tk.Entry(
            question_frame,
            bg=self.colors["input_bg"],
            fg=self.colors["input_fg"],
            font=("Arial", 11),
            insertbackground=self.colors["fg"],
            relief=tk.FLAT
        )
        self.question_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                                ipady=10, padx=(0, 10))
        self.question_entry.bind("<Return>", lambda e: self.ask_ai_question())
        
        ask_btn = ModernButton(question_frame, text="Ask", 
                              command=self.ask_ai_question,
                              width=100, height=40,
                              bg_color=self.colors["accent_primary"],
                              text_color="#FFFFFF",
                              corner_radius=12)
        ask_btn.config(bg=self.colors["card_bg"])
        ask_btn.pack(side=tk.RIGHT)
        
        # Load chat history
        self.load_chat_history()
    
    def create_uploads_tab(self, parent):
        """Create uploaded materials management interface."""
        # Header
        header = tk.Frame(parent, bg=self.colors["bg"])
        header.pack(fill=tk.X, padx=30, pady=20)
        
        title = tk.Label(header, text="My Study Materials", bg=self.colors["bg"],
                        fg=self.colors["fg"], font=("Arial", 28, "bold"))
        title.pack(side=tk.LEFT)
        
        # Upload button
        upload_btn = ModernButton(header, text="📁 Upload Material", 
                                 command=self.upload_study_material,
                                 width=180, height=45,
                                 bg_color=self.colors["accent_primary"],
                                 text_color="#FFFFFF",
                                 corner_radius=14)
        upload_btn.config(bg=self.colors["bg"])
        upload_btn.pack(side=tk.RIGHT)
        
        # Materials list container
        self.uploads_container = tk.Frame(parent, bg=self.colors["bg"])
        self.uploads_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        # Load uploaded materials
        self.load_uploaded_materials()
    
    def ask_ai_question(self):
        """Send question to AI assistant."""
        question = self.question_entry.get().strip()
        if not question:
            return
        
        if not self.ai_assistant.is_configured():
            messagebox.showerror("AI Not Available", 
                                "AI Assistant is not configured.\n\n"
                                "Please contact the app administrator to set up the API key in the .env file.")
            return
        
        # Clear entry
        self.question_entry.delete(0, tk.END)
        
        # Add question to chat
        self.add_to_chat(f"You: {question}\n", "question")
        
        # Show loading
        self.add_to_chat("AI is thinking...\n", "system")
        
        # Get mode
        mode = self.ai_mode_var.get()
        
        # Process in thread to avoid blocking GUI
        def process_question():
            result = self.ai_assistant.ask_question(question, mode=mode)
            
            # Update GUI from main thread
            self.root.after(0, lambda: self.display_ai_response(result))
        
        thread = threading.Thread(target=process_question, daemon=True)
        thread.start()
    
    def display_ai_response(self, result):
        """Display AI response in chat."""
        # Remove "thinking" message
        self.chat_display.config(state=tk.NORMAL)
        content = self.chat_display.get("1.0", tk.END)
        lines = content.split('\n')
        if lines and "thinking" in lines[-2].lower():
            # Remove last two lines (thinking message + blank line)
            self.chat_display.delete("end-3l", "end-1l")
        
        if result.get("success"):
            answer = result.get("answer", "No response")
            mode_icon = "🌐" if result.get("mode") == "internet" else "📚"
            
            self.add_to_chat(f"{mode_icon} AI: {answer}\n\n", "answer")
            
            # Show info if no information found in materials
            if result.get("mode") == "materials" and not result.get("found_info"):
                self.add_to_chat("💡 Tip: Upload study materials or switch to Internet mode for more information.\n\n", "system")
        else:
            error = result.get("error", "Unknown error")
            self.add_to_chat(f"❌ Error: {error}\n\n", "system")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def add_to_chat(self, text, tag):
        """Add text to chat display with styling."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text, tag)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def load_chat_history(self):
        """Load and display chat history - starts fresh by default."""
        # Clear chat display first
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Start with a fresh chat - no history loaded
        self.ai_assistant.start_new_chat()
        
        # Show welcome message for fresh chat
        self.add_to_chat("Welcome to AI Study Assistant! 👋\n\n", "system")
        self.add_to_chat("You can ask me questions in two modes:\n", "system")
        self.add_to_chat("🌐 Internet Mode: Get answers from the web\n", "system")
        self.add_to_chat("📚 My Materials Mode: Get answers only from your uploaded study materials\n\n", "system")
        self.add_to_chat("💡 Tip: Click '📜 Recent Chats' to view your previous conversations!\n\n", "system")
    
    def start_new_chat(self):
        """Start a completely fresh chat."""
        if messagebox.askyesno("New Chat", "Start a new chat? This will clear the current conversation."):
            self.load_chat_history()
            self.show_toast("Started new chat!")
    
    def show_recent_chats(self):
        """Show popup with recent chat sessions."""
        sessions = self.ai_assistant.get_chat_sessions()
        
        if not sessions:
            messagebox.showinfo("Recent Chats", "No previous chat sessions found.")
            return
        
        # Create popup dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Recent Chat Sessions")
        dialog.geometry("700x500")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header
        header = tk.Frame(dialog, bg=self.colors["bg"])
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text="Recent Chat Sessions", 
                bg=self.colors["bg"], fg=self.colors["fg"],
                font=("Arial", 18, "bold")).pack(side=tk.LEFT)
        
        close_btn = ModernButton(header, text="✕", 
                                command=dialog.destroy,
                                width=40, height=40,
                                bg_color=self.colors["button_bg"],
                                text_color=self.colors["fg"])
        close_btn.config(bg=self.colors["bg"])
        close_btn.pack(side=tk.RIGHT)
        
        # Sessions list with scrollbar
        list_container = tk.Frame(dialog, bg=self.colors["bg"])
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        canvas = tk.Canvas(list_container, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display each session as a card
        for idx, session in enumerate(sessions):
            self.create_session_card(scrollable_frame, session, idx, dialog)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
    
    def create_session_card(self, parent, session, idx, dialog):
        """Create a card for a chat session."""
        card = tk.Frame(parent, bg=self.colors["card_bg"], cursor="hand2")
        card.pack(fill=tk.X, pady=8)
        
        content = tk.Frame(card, bg=self.colors["card_bg"])
        content.pack(fill=tk.X, padx=20, pady=15)
        
        # Session info
        try:
            start_dt = datetime.fromisoformat(session["start_time"])
            date_str = start_dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            date_str = "Unknown date"
        
        # Date and message count
        header = tk.Frame(content, bg=self.colors["card_bg"])
        header.pack(fill=tk.X)
        
        date_label = tk.Label(header, text=date_str,
                             bg=self.colors["card_bg"], fg=self.colors["fg"],
                             font=("Arial", 12, "bold"), anchor=tk.W)
        date_label.pack(side=tk.LEFT)
        
        count_label = tk.Label(header, text=f"{session['message_count']} messages",
                              bg=self.colors["card_bg"], fg=self.colors["fg_secondary"],
                              font=("Arial", 10))
        count_label.pack(side=tk.RIGHT)
        
        # Preview
        preview_label = tk.Label(content, text=session["preview"],
                                bg=self.colors["card_bg"], fg=self.colors["fg_secondary"],
                                font=("Arial", 10), anchor=tk.W, wraplength=600, justify=tk.LEFT)
        preview_label.pack(fill=tk.X, pady=(5, 0))
        
        # Hover effect
        def on_enter(e):
            card.config(bg=self.colors["button_hover"])
            content.config(bg=self.colors["button_hover"])
            header.config(bg=self.colors["button_hover"])
            date_label.config(bg=self.colors["button_hover"])
            count_label.config(bg=self.colors["button_hover"])
            preview_label.config(bg=self.colors["button_hover"])
        
        def on_leave(e):
            card.config(bg=self.colors["card_bg"])
            content.config(bg=self.colors["card_bg"])
            header.config(bg=self.colors["card_bg"])
            date_label.config(bg=self.colors["card_bg"])
            count_label.config(bg=self.colors["card_bg"])
            preview_label.config(bg=self.colors["card_bg"])
        
        def on_click(e):
            self.load_chat_session(session["messages"])
            dialog.destroy()
            self.show_toast(f"Loaded chat from {date_str}")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Button-1>", on_click)
        content.bind("<Button-1>", on_click)
        header.bind("<Button-1>", on_click)
        date_label.bind("<Button-1>", on_click)
        count_label.bind("<Button-1>", on_click)
        preview_label.bind("<Button-1>", on_click)
    
    def load_chat_session(self, messages):
        """Load a specific chat session into the chat display."""
        # Clear chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        
        # Add header
        self.add_to_chat("=== Loaded Previous Chat Session ===\n\n", "system")
        
        # Display all messages from the session
        for item in messages:
            question = item.get("question", "")
            answer = item.get("answer", "")
            mode = item.get("mode", "internet")
            mode_icon = "🌐" if mode == "internet" else "📚"
            
            self.add_to_chat(f"You: {question}\n", "question")
            self.add_to_chat(f"{mode_icon} AI: {answer}\n\n", "answer")
        
        self.add_to_chat("=== End of Previous Session ===\n", "system")
        self.add_to_chat("💡 Continue the conversation or start a new chat!\n\n", "system")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def upload_study_material(self):
        """Upload a new study material file."""
        file_path = filedialog.askopenfilename(
            title="Select Study Material",
            filetypes=[
                ("All Supported", "*.txt *.md *.pdf *.docx *.doc *.pptx *.ppt *.xlsx *.xls *.py *.java *.cpp *.js *.html *.css *.json"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx *.doc"),
                ("PowerPoint", "*.pptx *.ppt"),
                ("Excel Files", "*.xlsx *.xls"),
                ("Text files", "*.txt"),
                ("Markdown", "*.md"),
                ("Code files", "*.py *.java *.cpp *.js *.html *.css *.json"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Ask for title and description
        dialog = tk.Toplevel(self.root)
        dialog.title("Material Details")
        dialog.geometry("400x250")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Title:", bg=self.colors["bg"],
                fg=self.colors["fg"], font=("Arial", 11)).pack(pady=(20, 5), padx=20, anchor=tk.W)
        
        title_entry = tk.Entry(dialog, bg=self.colors["input_bg"],
                              fg=self.colors["input_fg"], font=("Arial", 10))
        title_entry.pack(pady=5, padx=20, fill=tk.X, ipady=5)
        title_entry.insert(0, os.path.basename(file_path))
        
        tk.Label(dialog, text="Description (optional):", bg=self.colors["bg"],
                fg=self.colors["fg"], font=("Arial", 11)).pack(pady=(10, 5), padx=20, anchor=tk.W)
        
        desc_text = tk.Text(dialog, bg=self.colors["input_bg"],
                           fg=self.colors["input_fg"], font=("Arial", 10),
                           height=4)
        desc_text.pack(pady=5, padx=20, fill=tk.X)
        
        def save_upload():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            
            result = self.ai_assistant.upload_study_material(file_path, title, description)
            
            if result.get("success"):
                messagebox.showinfo("Success", "Study material uploaded successfully!")
                dialog.destroy()
                self.load_uploaded_materials()
            else:
                messagebox.showerror("Error", f"Failed to upload: {result.get('error')}")
        
        btn_frame = tk.Frame(dialog, bg=self.colors["bg"])
        btn_frame.pack(pady=20)
        
        save_btn = ModernButton(btn_frame, text="Upload", command=save_upload,
                               width=100, height=35,
                               bg_color=self.colors["accent_primary"],
                               text_color=self.colors["bg"])
        save_btn.config(bg=self.colors["bg"])
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ModernButton(btn_frame, text="Cancel", command=dialog.destroy,
                                 width=100, height=35,
                                 bg_color=self.colors["button_hover"],
                                 text_color=self.colors["fg"])
        cancel_btn.config(bg=self.colors["bg"])
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def load_uploaded_materials(self):
        """Load and display uploaded materials."""
        # Clear existing
        for widget in self.uploads_container.winfo_children():
            widget.destroy()
        
        materials = self.ai_assistant.get_uploaded_materials()
        
        if not materials:
            # Show empty state
            empty_frame = tk.Frame(self.uploads_container, bg=self.colors["card_bg"])
            empty_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(empty_frame, text="📚 No materials uploaded yet",
                    bg=self.colors["card_bg"], fg=self.colors["fg_secondary"],
                    font=("Arial", 16)).pack(expand=True)
            return
        
        # Create scrollable list
        canvas = tk.Canvas(self.uploads_container, bg=self.colors["bg"], 
                          highlightthickness=0)
        scrollbar = tk.Scrollbar(self.uploads_container, orient="vertical", 
                                command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display materials as cards
        for material in materials:
            card = tk.Frame(scrollable_frame, bg=self.colors["card_bg"])
            card.pack(fill=tk.X, padx=10, pady=5)
            
            content = tk.Frame(card, bg=self.colors["card_bg"])
            content.pack(fill=tk.X, padx=20, pady=15)
            
            # Title
            title_label = tk.Label(content, text=material.get("title", "Untitled"),
                                  bg=self.colors["card_bg"], fg=self.colors["fg"],
                                  font=("Arial", 13, "bold"), anchor=tk.W)
            title_label.pack(fill=tk.X)
            
            # Metadata
            word_count = material.get("word_count", 0)
            upload_date = material.get("upload_date", "")
            if upload_date:
                try:
                    date_obj = datetime.fromisoformat(upload_date)
                    upload_date = date_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            meta_text = f"📄 {word_count} words  •  📅 {upload_date}"
            meta_label = tk.Label(content, text=meta_text,
                                 bg=self.colors["card_bg"], fg=self.colors["fg_secondary"],
                                 font=("Arial", 9), anchor=tk.W)
            meta_label.pack(fill=tk.X, pady=(5, 0))
            
            # Description
            if material.get("description"):
                desc_label = tk.Label(content, text=material.get("description"),
                                     bg=self.colors["card_bg"], fg=self.colors["fg_secondary"],
                                     font=("Arial", 10), anchor=tk.W, wraplength=700, justify=tk.LEFT)
                desc_label.pack(fill=tk.X, pady=(5, 10))
            
            # Delete button
            file_id = os.path.basename(material.get("full_path", ""))
            delete_btn = ModernButton(content, text="🗑️ Delete",
                                     command=lambda fid=file_id: self.delete_material(fid),
                                     width=100, height=30,
                                     bg_color="#c44536",
                                     text_color="white")
            delete_btn.config(bg=self.colors["card_bg"])
            delete_btn.pack(anchor=tk.W)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def delete_material(self, file_id):
        """Delete an uploaded material."""
        if messagebox.askyesno("Confirm Delete", 
                              "Are you sure you want to delete this material?"):
            if self.ai_assistant.delete_uploaded_material(file_id):
                self.load_uploaded_materials()
                messagebox.showinfo("Success", "Material deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete material")
        
    def create_analytics_view(self):
        """Create analytics view with charts."""
        analytics = tk.Frame(self.content_area, bg=self.colors["bg"])
        self.views["analytics"] = analytics
        
        # Header
        header = tk.Frame(analytics, bg=self.colors["bg"])
        header.pack(fill=tk.X, padx=40, pady=30)
        
        title = tk.Label(header, text="Analytics", bg=self.colors["bg"],
                        fg=self.colors["fg"], font=("Arial", 32, "bold"))
        title.pack(side=tk.LEFT)
        
        # Period selector
        period_frame = tk.Frame(header, bg=self.colors["bg"])
        period_frame.pack(side=tk.RIGHT)
        
        tk.Label(period_frame, text="Period:", bg=self.colors["bg"],
                fg=self.colors["fg_secondary"], font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        
        self.report_period_var = tk.StringVar(value="7")
        period_options = ["1", "7", "14", "30"]
        for period in period_options:
            btn = tk.Radiobutton(period_frame, text=f"{period} days", 
                               variable=self.report_period_var, value=period,
                               bg=self.colors["bg"], fg=self.colors["fg"],
                               selectcolor=self.colors["accent_primary"],
                               command=self.generate_report)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Report display
        report_card = tk.Frame(analytics, bg=self.colors["card_bg"])
        report_card.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 30))
        
        self.report_text = scrolledtext.ScrolledText(report_card, wrap=tk.WORD,
                                                    bg=self.colors["input_bg"],
                                                    fg=self.colors["input_fg"],
                                                    font=("Consolas", 10),
                                                    insertbackground=self.colors["fg"],
                                                    relief=tk.FLAT, padx=20, pady=20)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Generate initial report
        self.generate_report()
        
    def create_settings_view(self):
        """Create modern settings view."""
        settings = tk.Frame(self.content_area, bg=self.colors["bg"])
        self.views["settings"] = settings
        
        # Header
        header = tk.Frame(settings, bg=self.colors["bg"])
        header.pack(fill=tk.X, padx=40, pady=30)
        
        title = tk.Label(header, text="Settings", bg=self.colors["bg"],
                        fg=self.colors["fg"], font=("Arial", 32, "bold"))
        title.pack(side=tk.LEFT)
        
        # Settings cards
        # Appearance
        self.create_setting_card(settings, "Appearance", [
            ("Theme Mode", "combobox", "theme.mode", ["light", "dark"])
        ])
        
        # Focus Tracking
        self.create_setting_card(settings, "Focus Tracking", [
            ("Sensitivity", "combobox", "focus_tracking.sensitivity", ["low", "medium", "high"]),
            ("Show Face Outline", "checkbox", "focus_tracking.show_outline", None)
        ])
        
        # Camera
        self.create_setting_card(settings, "Camera", [
            ("Device Index", "entry", "camera.device_index", None)
        ])
        
        # Notifications
        self.create_setting_card(settings, "Notifications", [
            ("Enable Sounds", "checkbox", "notifications.sounds", None),
            ("Show Notifications", "checkbox", "notifications.enabled", None)
        ])
        
        # Save button
        save_frame = tk.Frame(settings, bg=self.colors["bg"])
        save_frame.pack(fill=tk.X, padx=40, pady=30)
        
        save_btn = ModernButton(save_frame, text="Save Settings", 
                               command=self.save_settings,
                               width=200, height=55,
                               bg_color=self.colors["accent_primary"],
                               text_color=self.colors["bg"],
                               hover_color=self.colors["accent_secondary"])
        save_btn.config(bg=self.colors["bg"])
        save_btn.pack()
        
    def create_setting_card(self, parent, title: str, settings_list: list):
        """Create a settings card."""
        card = tk.Frame(parent, bg=self.colors["card_bg"])
        card.pack(fill=tk.X, padx=40, pady=(0, 20))
        
        # Header
        header = tk.Frame(card, bg=self.colors["card_bg"])
        header.pack(fill=tk.X, padx=30, pady=(20, 10))
        
        tk.Label(header, text=title, bg=self.colors["card_bg"],
                fg=self.colors["fg"], font=("Arial", 16, "bold")).pack(anchor=tk.W)
        
        # Settings
        for label, widget_type, config_key, values in settings_list:
            row = tk.Frame(card, bg=self.colors["card_bg"])
            row.pack(fill=tk.X, padx=30, pady=10)
            
            tk.Label(row, text=label, bg=self.colors["card_bg"],
                    fg=self.colors["fg_secondary"], font=("Arial", 11)).pack(side=tk.LEFT)
            
            if widget_type == "combobox":
                var = tk.StringVar(value=str(self.config_manager.get(config_key)))
                combo = ttk.Combobox(row, textvariable=var, values=values,
                                    state="readonly", width=15)
                combo.pack(side=tk.RIGHT)
                setattr(self, f"setting_{config_key.replace('.', '_')}", var)
            elif widget_type == "entry":
                var = tk.StringVar(value=str(self.config_manager.get(config_key)))
                entry = tk.Entry(row, textvariable=var, bg=self.colors["input_bg"],
                               fg=self.colors["input_fg"], width=15,
                               insertbackground=self.colors["fg"])
                entry.pack(side=tk.RIGHT)
                setattr(self, f"setting_{config_key.replace('.', '_')}", var)
            elif widget_type == "checkbox":
                var = tk.BooleanVar(value=self.config_manager.get(config_key))
                check = tk.Checkbutton(row, variable=var, bg=self.colors["card_bg"],
                                      fg=self.colors["fg"], selectcolor=self.colors["input_bg"])
                check.pack(side=tk.RIGHT)
                setattr(self, f"setting_{config_key.replace('.', '_')}", var)
        
        # Bottom padding
        tk.Frame(card, bg=self.colors["card_bg"], height=15).pack()
        
    # Event handlers and methods
    def start_session(self):
        """Start a study session."""
        if self.session_active:
            return
            
        try:
            duration = int(self.duration_var.get())
            if duration <= 0:
                self.show_toast("Duration must be positive")
                return
        except ValueError:
            self.show_toast("Please enter a valid duration")
            return
            
        self.session_manager.settings["study_duration"] = duration
        
        if self.session_manager.start_session():
            self.session_active = True
            self.focus_tracker.start_tracking()
            
            # Update UI
            self.session_status_label.config(text="Session Active")
            self.session_subtitle.config(text=f"Stay focused for {duration} minutes")
            self.start_session_btn.config(state=tk.DISABLED)
            self.pause_session_btn.config(state=tk.NORMAL)
            self.end_session_btn.config(state=tk.NORMAL)
            
            self.show_toast(f"Session started - {duration} minutes")
            self.start_gui_update_thread()
            
    def pause_session(self):
        """Pause/resume session."""
        if not self.session_active:
            return
            
        if self.session_manager.paused:
            self.session_manager.resume_session()
            self.pause_session_btn.configure(text="Pause")
            self.show_toast("Session resumed")
        else:
            self.session_manager.pause_session()
            self.pause_session_btn.configure(text="Resume")
            self.show_toast("Session paused")
            
    def end_session(self):
        """End the current session."""
        if not self.session_active:
            return
            
        session_data = self.session_manager.end_session()
        self.focus_tracker.stop_tracking()
        self.session_active = False
        
        # Update UI
        self.session_status_label.config(text="Session Complete")
        self.session_subtitle.config(text="Great work! Ready for another session?")
        self.start_session_btn.config(state=tk.NORMAL)
        self.pause_session_btn.config(state=tk.DISABLED, text="Pause")
        self.end_session_btn.config(state=tk.DISABLED)
        
        # Reset displays
        self.timer_progress.set_progress(0, animated=True)
        self.timer_display.config(text="00:00")
        
        self.show_toast("Session completed!")
        
        if session_data:
            self.show_session_summary(session_data)
        
        self.update_dashboard_stats()
        
    def on_distraction_detected(self):
        """Handle distraction detection."""
        if self.session_active:
            self.session_manager.log_distraction_event()
            
            # Pulse focus indicator
            if hasattr(self, 'focus_indicator'):
                self.animation_engine.pulse(self.focus_indicator)
            
            if self.config_manager.get("notifications.sounds"):
                self.sound_manager.play_sound("distraction_alert")
                
            if self.config_manager.get("notifications.enabled"):
                self.notification_manager.show_notification(
                    "Focus Alert", 
                    "You seem distracted. Return to your studies!"
                )
                
    def on_session_end(self):
        """Handle automatic session end."""
        self.end_session()
        
    def on_session_update(self, status):
        """Handle session status updates."""
        if hasattr(self, 'timer_display'):
            remaining = status.get('remaining_time', 0)
            self.timer_display.config(text=DataFormatter.format_time(remaining))
            
            # Update circular progress
            total_duration = self.session_manager.settings["study_duration"] * 60
            if total_duration > 0:
                progress = ((total_duration - remaining) / total_duration) * 100
                self.timer_progress.set_progress(progress, animated=False)
            
        if hasattr(self, 'elapsed_label'):
            elapsed = status.get('elapsed_time', 0)
            self.elapsed_label.config(text=f"Elapsed: {DataFormatter.format_time(elapsed)}")
            
        if hasattr(self, 'distraction_label'):
            count = status.get('distraction_count', 0)
            self.distraction_label.config(text=f"Distractions: {count}")
            
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
                if self.focus_tracker.camera and self.focus_tracker.is_tracking:
                    frame, focus_data = self.focus_tracker.process_frame()
                    if frame is not None and focus_data is not None:
                        self.root.after(0, self.update_focus_display, focus_data)
                        self.root.after(0, self.update_camera_feed, frame)
                        
                        self.session_manager.log_focus_event(
                            focus_data['focus_score'], 
                            focus_data['is_focused']
                        )
                        
                time.sleep(0.1)
                
            except Exception as e:
                print(f"GUI update error: {e}")
                import traceback
                traceback.print_exc()
                break
                
    def update_focus_display(self, focus_data):
        """Update focus status display."""
        if focus_data['is_focused']:
            self.focus_status_text.config(text="Focused", 
                                         fg=self.colors["status_focused"])
            self.focus_indicator.itemconfig(self.focus_circle, 
                                           fill=self.colors["status_focused"])
        else:
            self.focus_status_text.config(text="Distracted", 
                                         fg=self.colors["status_distracted"])
            self.focus_indicator.itemconfig(self.focus_circle, 
                                           fill=self.colors["status_distracted"])
            
        self.focus_score_label.config(text=f"Focus Score: {focus_data['focus_score']:.2f}")
        
    def update_camera_feed(self, frame):
        """Update camera feed display."""
        try:
            if frame is not None and hasattr(self, 'camera_label'):
                # Convert from BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize frame to fit in the display area
                display_height = 400
                aspect_ratio = frame.shape[1] / frame.shape[0]
                display_width = int(display_height * aspect_ratio)
                
                frame_resized = cv2.resize(frame_rgb, (display_width, display_height))
                
                # Convert to PIL Image
                img = Image.fromarray(frame_resized)
                
                # Convert to ImageTk
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update label
                self.camera_label.configure(image=imgtk, text="")
                self.camera_label.image = imgtk  # Keep a reference
                
        except Exception:
            pass  # Suppress frequent frame errors for perf
        
    def update_dashboard_stats(self):
        """Update dashboard statistics."""
        try:
            report = self.session_manager.generate_productivity_report(7)
            
            if "error" not in report:
                self.stat_sessions.update_value(str(report['total_sessions']), animated=True)
                self.stat_time.update_value(DataFormatter.format_duration(report['total_study_time']), animated=True)
                self.stat_focus.update_value(f"{report['overall_focus_percentage']:.1f}%", animated=True)
        except:
            pass
            
    def generate_report(self):
        """Generate productivity report."""
        try:
            days = int(self.report_period_var.get())
            report = self.session_manager.generate_productivity_report(days)
            
            if "error" in report:
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(tk.END, f"No data available for the last {days} days.")
                return
                
            report_text = f"""PRODUCTIVITY REPORT - Last {days} Days
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW
========
Total Sessions: {report['total_sessions']}
Total Study Time: {DataFormatter.format_duration(report['total_study_time'])}
Average Session: {DataFormatter.format_duration(report['average_session_duration'])}
Overall Focus: {report['overall_focus_percentage']:.1f}%
Efficiency: {report['efficiency_percentage']:.1f}%
Total Distractions: {report['total_distractions']}

DAILY BREAKDOWN
===============
"""
            for date, stats in report['daily_stats'].items():
                report_text += f"{date}: {stats['sessions']} sessions, "
                report_text += f"{DataFormatter.format_duration(stats['study_time'])}, "
                report_text += f"{stats['distractions']} distractions\n"
                
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, report_text)
            
        except Exception as e:
            self.show_toast(f"Failed to generate report: {e}")
            
    def show_session_summary(self, session_data):
        """Show session completion summary."""
        stats = self.focus_tracker.get_session_stats()
        
        summary = f"""Session Completed!

Duration: {DataFormatter.format_time(session_data.get('duration_actual', 0))}
Focus Percentage: {stats.get('focus_percentage', 0):.1f}%
Distractions: {session_data.get('distraction_count', 0)}
Average Focus Score: {stats.get('average_focus_score', 0):.2f}

Great job studying!"""
        
        messagebox.showinfo("Session Complete", summary)
        
    def add_link(self):
        """Add a new study material."""
        dialog = AddLinkDialog(self.root, self.colors)
        if dialog.result:
            name, url, category = dialog.result
            if self.materials_manager.add_quick_link(name, url, category):
                self.load_materials()
                self.show_toast("Material added successfully")
                
    def save_settings(self):
        """Save application settings."""
        try:
            # Get old values to check for changes
            old_camera_index = self.config_manager.get("camera.device_index", 0)
            new_camera_index = int(self.setting_camera_device_index.get())
            old_theme = self.config_manager.get("theme.mode")
            new_theme = self.setting_theme_mode.get()
            
            # Get sensitivity setting
            new_sensitivity = self.setting_focus_tracking_sensitivity.get()
            
            # Get face outline setting
            show_outline = self.setting_focus_tracking_show_outline.get()
            
            # Save all settings
            self.config_manager.set("theme.mode", new_theme)
            self.config_manager.set("focus_tracking.sensitivity", new_sensitivity)
            self.config_manager.set("focus_tracking.show_outline", show_outline)
            self.config_manager.set("camera.device_index", new_camera_index)
            self.config_manager.set("notifications.sounds", self.setting_notifications_sounds.get())
            self.config_manager.set("notifications.enabled", self.setting_notifications_enabled.get())
            
            self.sound_manager.set_enabled(self.setting_notifications_sounds.get())
            self.notification_manager.set_enabled(self.setting_notifications_enabled.get())
            
            # Apply sensitivity change
            self.focus_tracker.set_sensitivity(new_sensitivity)
            
            # Apply face outline setting
            self.focus_tracker.set_show_outline(show_outline)
            
            # Apply theme change immediately
            if old_theme != new_theme:
                self.show_toast(f"Switching to {new_theme} mode...")
                self.root.after(100, self.apply_theme_change)
            
            # Reinitialize camera if index changed
            if old_camera_index != new_camera_index:
                if self.session_active:
                    self.show_toast("Please end current session to change camera")
                else:
                    self.show_toast("Reinitializing camera...")
                    if self.focus_tracker.initialize_camera(new_camera_index):
                        self.show_toast(f"Camera {new_camera_index} initialized successfully!")
                    else:
                        self.show_toast(f"Failed to initialize camera {new_camera_index}")
                        # Revert to old camera index
                        self.config_manager.set("camera.device_index", old_camera_index)
                        self.focus_tracker.initialize_camera(old_camera_index)
            elif old_theme == new_theme:
                # Only show this message if theme didn't change
                self.show_toast("Settings saved successfully!")
                
        except Exception as e:
            self.show_toast(f"Error saving settings: {e}")
            
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        current_mode = self.config_manager.get("theme.mode")
        new_mode = "dark" if current_mode == "light" else "light"
        
        self.config_manager.set("theme.mode", new_mode)
        self.show_toast(f"Switching to {new_mode} mode...")
        self.root.after(100, self.apply_theme_change)
    
    def apply_theme_change(self):
        """Apply theme change to all UI elements without restarting."""
        # Get new theme colors
        self.colors = self.config_manager.get_theme_colors()
        
        # Update root window
        self.root.configure(bg=self.colors["bg"])
        
        # Update all views
        for view in self.views.values():
            self.update_widget_theme(view)
        
        # Update content area
        if hasattr(self, 'content_area'):
            self.content_area.configure(bg=self.colors["bg"])
        
        # Update sidebar buttons
        for name, btn in self.sidebar_buttons.items():
            if name == self.current_view:
                btn.config(bg=self.colors["accent_primary"], 
                          fg=self.colors["bg"])
            else:
                btn.config(bg=self.colors["bg_secondary"], 
                          fg=self.colors["fg"])
        
        # Update specific widgets that need manual refresh
        self.update_special_widgets()
        
        current_mode = self.config_manager.get("theme.mode")
        self.show_toast(f"✓ {current_mode.capitalize()} mode applied!")
    
    def update_widget_theme(self, widget):
        """Recursively update theme for a widget and its children."""
        try:
            # Get widget type
            widget_class = widget.winfo_class()
            
            # Update based on widget type
            if widget_class == 'Frame':
                current_bg = str(widget.cget('bg'))
                # Map old colors to new colors
                if '#' in current_bg or current_bg in ['SystemButtonFace', 'white', 'black']:
                    # Determine which background to use based on context
                    if hasattr(widget, '_card_widget'):
                        widget.configure(bg=self.colors["card_bg"])
                    elif hasattr(widget, '_secondary_bg'):
                        widget.configure(bg=self.colors["bg_secondary"])
                    else:
                        widget.configure(bg=self.colors["bg"])
            
            elif widget_class == 'Label':
                current_bg = str(widget.cget('bg'))
                current_fg = str(widget.cget('fg'))
                
                # Update background
                if '#' in current_bg:
                    if 'card' in current_bg or 'Card' in str(widget):
                        widget.configure(bg=self.colors["card_bg"])
                    elif 'secondary' in current_bg:
                        widget.configure(bg=self.colors["bg_secondary"])
                    else:
                        widget.configure(bg=self.colors["bg"])
                
                # Update foreground based on current color role
                if '#' in current_fg:
                    # Try to determine if it's a primary, secondary, or accent color
                    if 'accent' in str(widget.cget('font')) or 'bold' in str(widget.cget('font')):
                        widget.configure(fg=self.colors["fg"])
                    else:
                        widget.configure(fg=self.colors["fg_secondary"])
            
            elif widget_class in ['Entry', 'Text']:
                widget.configure(
                    bg=self.colors["input_bg"],
                    fg=self.colors["input_fg"],
                    insertbackground=self.colors["fg"]
                )
            
            elif widget_class == 'Canvas':
                widget.configure(bg=self.colors["bg"])
            
            elif widget_class == 'Button':
                widget.configure(
                    bg=self.colors["button_bg"],
                    fg=self.colors["button_fg"]
                )
            
            # Recursively update children
            for child in widget.winfo_children():
                self.update_widget_theme(child)
                
        except Exception as e:
            # Skip widgets that don't support theme updates
            pass
    
    def update_special_widgets(self):
        """Update special widgets that need manual configuration."""
        try:
            # Update chat display
            if hasattr(self, 'chat_display'):
                self.chat_display.configure(
                    bg=self.colors["input_bg"],
                    fg=self.colors["input_fg"]
                )
                # Update tags
                self.chat_display.tag_config("question", 
                                           foreground=self.colors["accent_primary"])
                self.chat_display.tag_config("answer", 
                                           foreground=self.colors["fg"])
                self.chat_display.tag_config("system", 
                                           foreground=self.colors["fg_secondary"])
            
            # Update report text
            if hasattr(self, 'report_text'):
                self.report_text.configure(
                    bg=self.colors["input_bg"],
                    fg=self.colors["input_fg"]
                )
            
            # Update camera label
            if hasattr(self, 'camera_label'):
                self.camera_label.configure(
                    bg=self.colors["bg_secondary"],
                    fg=self.colors["fg_muted"]
                )
            
            # Update focus indicator
            if hasattr(self, 'focus_indicator'):
                self.focus_indicator.configure(bg=self.colors["card_bg"])
            
            # Update session labels
            if hasattr(self, 'session_status_label'):
                self.session_status_label.configure(
                    bg=self.colors["card_bg"],
                    fg=self.colors["fg"]
                )
            
            if hasattr(self, 'session_subtitle'):
                self.session_subtitle.configure(
                    bg=self.colors["card_bg"],
                    fg=self.colors["fg_secondary"]
                )
            
            # Update timer display
            if hasattr(self, 'timer_display'):
                self.timer_display.configure(
                    bg=self.colors["card_bg"],
                    fg=self.colors["fg"]
                )
            
            # Update circular progress colors
            if hasattr(self, 'timer_progress'):
                self.timer_progress.color = self.colors["accent_primary"]
                self.timer_progress.bg_color = self.colors["bg_secondary"]
                self.timer_progress.update_display()
            
            # Update ModernButton colors (they need special handling)
            self.update_modern_buttons()
            
        except Exception as e:
            print(f"Error updating special widgets: {e}")
    
    def update_modern_buttons(self):
        """Update all ModernButton instances."""
        # This method updates buttons by finding them in the widget tree
        def update_buttons_recursive(widget):
            try:
                if isinstance(widget, ModernButton):
                    # Determine semantic role from current fill color
                    fill = None
                    try:
                        # Attempt to read internal bg polygon fill
                        fill = widget.itemcget(widget._bg_item, 'fill')
                    except Exception:
                        pass
                    # Map old fill to new theme colors (basic heuristic)
                    if fill in ["#6366F1", self.colors.get("accent_primary")]:
                        widget.set_colors(self.colors["accent_primary"], self.colors["bg"], self.colors["accent_secondary"])
                    elif fill in ["#EF4444", self.colors.get("accent_danger")]:
                        widget.set_colors(self.colors["accent_danger"], "#FFFFFF", "#DC2626")
                    elif fill in ["#64748B"]:
                        # Muted button (pause/resume)
                        widget.set_colors("#64748B" if self.config_manager.get("theme.mode") == "light" else "#475569", "#FFFFFF", "#94A3B8")
                    else:
                        # Default card background style button
                        widget.set_colors(self.colors["accent_primary"], self.colors["bg"], self.colors["accent_secondary"])
                    # Ensure canvas bg matches surrounding card
                    widget.configure(bg=self.colors["card_bg"])
                
                for child in widget.winfo_children():
                    update_buttons_recursive(child)
            except:
                pass
        
        if hasattr(self, 'content_area'):
            update_buttons_recursive(self.content_area)
        
    def show_toast(self, message: str):
        """Show toast notification."""
        ToastNotification.show(self.root, message, bg_color=self.colors["accent_primary"],
                             text_color=self.colors["bg"])
        
    def on_closing(self):
        """Handle application closing."""
        if self.session_active:
            if messagebox.askyesno("Session Active", "End current session and exit?"):
                self.end_session()
            else:
                return
                
        self.running = False
        self.focus_tracker.cleanup()
        self.session_manager.cleanup()
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """Run the application."""
        self.initialize_gui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


class AddLinkDialog:
    """Modern dialog for adding study materials."""
    
    def __init__(self, parent, colors):
        self.result = None
        self.colors = colors
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Study Material")
        self.dialog.geometry("450x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=colors["bg"])
        
        # Content
        content = tk.Frame(self.dialog, bg=colors["bg"])
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        tk.Label(content, text="Add New Material", bg=colors["bg"],
                fg=colors["fg"], font=("Arial", 18, "bold")).pack(pady=(0, 20))
        
        # Name field
        tk.Label(content, text="Name:", bg=colors["bg"],
                fg=colors["fg_secondary"], font=("Arial", 11)).pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        tk.Entry(content, textvariable=self.name_var, bg=colors["input_bg"],
                fg=colors["input_fg"], font=("Arial", 11),
                insertbackground=colors["fg"]).pack(fill=tk.X, pady=(5, 15))
        
        # URL field
        tk.Label(content, text="URL:", bg=colors["bg"],
                fg=colors["fg_secondary"], font=("Arial", 11)).pack(anchor=tk.W)
        self.url_var = tk.StringVar()
        tk.Entry(content, textvariable=self.url_var, bg=colors["input_bg"],
                fg=colors["input_fg"], font=("Arial", 11),
                insertbackground=colors["fg"]).pack(fill=tk.X, pady=(5, 15))
        
        # Category field
        tk.Label(content, text="Category:", bg=colors["bg"],
                fg=colors["fg_secondary"], font=("Arial", 11)).pack(anchor=tk.W)
        self.category_var = tk.StringVar(value="Custom")
        tk.Entry(content, textvariable=self.category_var, bg=colors["input_bg"],
                fg=colors["input_fg"], font=("Arial", 11),
                insertbackground=colors["fg"]).pack(fill=tk.X, pady=(5, 20))
        
        # Buttons
        button_frame = tk.Frame(content, bg=colors["bg"])
        button_frame.pack(fill=tk.X)
        
        add_btn = ModernButton(button_frame, text="Add", command=self.add_link,
                              width=100, height=45,
                              bg_color=colors["accent_primary"],
                              text_color=colors["bg"])
        add_btn.config(bg=colors["bg"])
        add_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ModernButton(button_frame, text="Cancel", command=self.dialog.destroy,
                                 width=100, height=45,
                                 bg_color=colors["button_bg"],
                                 text_color=colors["fg"])
        cancel_btn.config(bg=colors["bg"])
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
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
