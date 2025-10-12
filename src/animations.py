"""
Animation utilities for modern UI effects
Compatible with Python 3.8-3.12
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Callable, Optional, Dict, Any

class AnimationEngine:
    """Manages animations and transitions."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.active_animations = {}
        self.animation_id_counter = 0
        
    def animate_property(self, widget, property_name: str, start_value, end_value, 
                        duration: int = 300, easing: str = "ease_out", 
                        callback: Optional[Callable] = None):
        """Animate a widget property from start to end value."""
        animation_id = self.animation_id_counter
        self.animation_id_counter += 1
        
        start_time = self.root.tk.call('clock', 'milliseconds')
        
        def step():
            current_time = self.root.tk.call('clock', 'milliseconds')
            elapsed = current_time - start_time
            progress = min(elapsed / duration, 1.0)
            
            # Apply easing function
            eased_progress = self.apply_easing(progress, easing)
            
            # Calculate current value
            if isinstance(start_value, (int, float)):
                current_value = start_value + (end_value - start_value) * eased_progress
            else:
                # For colors
                current_value = self.interpolate_color(start_value, end_value, eased_progress)
            
            # Set property
            try:
                if property_name == "bg" or property_name == "background":
                    widget.configure(bg=current_value)
                elif property_name == "fg" or property_name == "foreground":
                    widget.configure(fg=current_value)
                elif property_name == "width":
                    widget.configure(width=int(current_value))
                elif property_name == "height":
                    widget.configure(height=int(current_value))
            except:
                pass
            
            if progress < 1.0:
                self.active_animations[animation_id] = self.root.after(16, step)  # ~60 FPS
            else:
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if callback:
                    callback()
        
        step()
        
    def apply_easing(self, t: float, easing_type: str) -> float:
        """Apply easing function to progress value."""
        if easing_type == "linear":
            return t
        elif easing_type == "ease_in":
            return t * t
        elif easing_type == "ease_out":
            return 1 - (1 - t) * (1 - t)
        elif easing_type == "ease_in_out":
            return 3 * t * t - 2 * t * t * t
        elif easing_type == "bounce":
            if t < 0.5:
                return 8 * (1 - t) * t * t * t
            else:
                return 1 - 8 * (1 - t) * (1 - t) * (1 - t) * t
        return t
    
    def interpolate_color(self, color1: str, color2: str, progress: float) -> str:
        """Interpolate between two hex colors."""
        # Convert hex to RGB
        c1 = tuple(int(color1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        c2 = tuple(int(color2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Interpolate
        r = int(c1[0] + (c2[0] - c1[0]) * progress)
        g = int(c1[1] + (c2[1] - c1[1]) * progress)
        b = int(c1[2] + (c2[2] - c1[2]) * progress)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def fade_in(self, widget, duration: int = 300, callback: Optional[Callable] = None):
        """Fade in a widget by changing its opacity (simulated with color)."""
        # Tkinter doesn't support true opacity, so we'll use other visual cues
        if callback:
            self.root.after(duration, callback)
    
    def slide_in(self, widget, direction: str = "left", duration: int = 300, 
                 distance: int = 100, callback: Optional[Callable] = None):
        """Slide widget in from specified direction."""
        original_x = widget.winfo_x()
        original_y = widget.winfo_y()
        
        # Set starting position
        if direction == "left":
            start_x = original_x - distance
            start_y = original_y
        elif direction == "right":
            start_x = original_x + distance
            start_y = original_y
        elif direction == "top":
            start_x = original_x
            start_y = original_y - distance
        else:  # bottom
            start_x = original_x
            start_y = original_y + distance
        
        widget.place(x=start_x, y=start_y)
        
        # Animate to original position
        self.animate_position(widget, start_x, start_y, original_x, original_y, 
                            duration, callback)
    
    def animate_position(self, widget, start_x: int, start_y: int, 
                        end_x: int, end_y: int, duration: int = 300,
                        callback: Optional[Callable] = None):
        """Animate widget position."""
        start_time = self.root.tk.call('clock', 'milliseconds')
        
        def step():
            current_time = self.root.tk.call('clock', 'milliseconds')
            elapsed = current_time - start_time
            progress = min(elapsed / duration, 1.0)
            eased_progress = self.apply_easing(progress, "ease_out")
            
            current_x = start_x + (end_x - start_x) * eased_progress
            current_y = start_y + (end_y - start_y) * eased_progress
            
            try:
                widget.place(x=int(current_x), y=int(current_y))
            except:
                return
            
            if progress < 1.0:
                self.root.after(16, step)
            elif callback:
                callback()
        
        step()
    
    def pulse(self, widget, scale: float = 1.1, duration: int = 500):
        """Create a pulse animation effect."""
        # This is a visual effect that can be simulated with highlighting
        original_bg = widget.cget("bg") if hasattr(widget, "cget") else None
        if original_bg:
            # Pulse to lighter color and back
            lighter = self.lighten_color(original_bg, 0.2)
            self.animate_property(widget, "bg", original_bg, lighter, duration // 2)
            self.root.after(duration // 2, 
                          lambda: self.animate_property(widget, "bg", lighter, original_bg, duration // 2))
    
    def lighten_color(self, color: str, factor: float) -> str:
        """Lighten a hex color by a factor."""
        rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return f'#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}'


class CircularProgress(tk.Canvas):
    """Modern circular progress indicator."""
    
    def __init__(self, parent, size: int = 200, line_width: int = 20, 
                 color: str = "#B8956A", bg_color: str = "#3A3027", **kwargs):
        super().__init__(parent, width=size, height=size, 
                        highlightthickness=0, bg=kwargs.get('bg', '#2D2520'), **kwargs)
        
        self.size = size
        self.line_width = line_width
        self.color = color
        self.bg_color = bg_color
        self.progress = 0
        
        # Draw background circle
        padding = 10
        self.bg_arc = self.create_arc(
            padding, padding, size - padding, size - padding,
            start=90, extent=359.99, outline=bg_color, width=line_width,
            style=tk.ARC
        )
        
        # Draw progress arc
        self.progress_arc = self.create_arc(
            padding, padding, size - padding, size - padding,
            start=90, extent=0, outline=color, width=line_width,
            style=tk.ARC
        )
        
        # Center text
        self.text = self.create_text(
            size // 2, size // 2, text="0%", 
            font=("Arial", size // 8, "bold"), fill=color
        )
    
    def set_progress(self, value: float, animated: bool = True):
        """Set progress (0-100)."""
        if animated:
            self.animate_to(value)
        else:
            self.progress = value
            self.update_display()
    
    def animate_to(self, target: float, duration: int = 500):
        """Animate progress to target value."""
        start_value = self.progress
        start_time = self.tk.call('clock', 'milliseconds')
        
        def step():
            current_time = self.tk.call('clock', 'milliseconds')
            elapsed = current_time - start_time
            progress_ratio = min(elapsed / duration, 1.0)
            
            # Ease out
            eased = 1 - (1 - progress_ratio) ** 2
            self.progress = start_value + (target - start_value) * eased
            self.update_display()
            
            if progress_ratio < 1.0:
                self.after(16, step)
        
        step()
    
    def update_display(self):
        """Update the visual display."""
        extent = -(self.progress / 100) * 360
        self.itemconfig(self.progress_arc, extent=extent)
        self.itemconfig(self.text, text=f"{int(self.progress)}%")


class ModernButton(tk.Canvas):
    """Modern button with hover and click animations."""
    
    def __init__(self, parent, text: str, command: Callable, 
                 width: int = 200, height: int = 50,
                 bg_color: str = "#B8956A", text_color: str = "#2D2520",
                 hover_color: str = "#D4A574", **kwargs):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, cursor="hand2", **kwargs)
        
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_pressed = False
        
        # Create rounded rectangle
        self.bg_rect = self.create_rounded_rectangle(
            2, 2, width - 2, height - 2, radius=10, fill=bg_color, outline=""
        )
        
        # Create text
        self.text_item = self.create_text(
            width // 2, height // 2, text=text, 
            font=("Arial", 12, "bold"), fill=text_color
        )
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Create a rounded rectangle."""
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        """Handle mouse enter."""
        self.is_hovered = True
        self.itemconfig(self.bg_rect, fill=self.hover_color)
        self.config(bg=self.master.cget('bg'))
    
    def on_leave(self, event):
        """Handle mouse leave."""
        self.is_hovered = False
        if not self.is_pressed:
            self.itemconfig(self.bg_rect, fill=self.bg_color)
    
    def on_press(self, event):
        """Handle mouse press."""
        self.is_pressed = True
        # Scale down effect
        self.scale(tk.ALL, self.winfo_width() // 2, self.winfo_height() // 2, 0.95, 0.95)
    
    def on_release(self, event):
        """Handle mouse release."""
        self.is_pressed = False
        # Scale back up
        self.scale(tk.ALL, self.winfo_width() // 2, self.winfo_height() // 2, 1/0.95, 1/0.95)
        
        if self.is_hovered:
            self.command()
            self.itemconfig(self.bg_rect, fill=self.hover_color)
        else:
            self.itemconfig(self.bg_rect, fill=self.bg_color)


class ToastNotification:
    """Modern toast notification."""
    
    @staticmethod
    def show(parent, message: str, duration: int = 3000, 
             bg_color: str = "#D4A574", text_color: str = "#2D2520"):
        """Show a toast notification."""
        toast = tk.Toplevel(parent)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        
        # Create label
        label = tk.Label(toast, text=message, bg=bg_color, fg=text_color,
                        font=("Arial", 11), padx=20, pady=12)
        label.pack()
        
        # Position at bottom center
        toast.update_idletasks()
        width = toast.winfo_width()
        height = toast.winfo_height()
        x = (parent.winfo_screenwidth() // 2) - (width // 2)
        y = parent.winfo_screenheight() - height - 100
        toast.geometry(f'+{x}+{y}')
        
        # Fade out and destroy
        def fade_out():
            alpha = 1.0
            def step():
                nonlocal alpha
                alpha -= 0.1
                if alpha > 0:
                    try:
                        toast.attributes('-alpha', alpha)
                        parent.after(50, step)
                    except:
                        pass
                else:
                    try:
                        toast.destroy()
                    except:
                        pass
            step()
        
        parent.after(duration, fade_out)


class StatCard(tk.Frame):
    """Modern statistics card with animation."""
    
    def __init__(self, parent, title: str, value: str = "0", 
                 icon: str = "", bg_color: str = "#3F362E", **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        
        self.title = title
        self.current_value = value
        self.bg_color = bg_color
        
        # Add padding
        self.config(padx=20, pady=20)
        
        # Icon/Title section
        title_frame = tk.Frame(self, bg=bg_color)
        title_frame.pack(fill=tk.X)
        
        if icon:
            icon_label = tk.Label(title_frame, text=icon, bg=bg_color, 
                                 fg="#D4A574", font=("Arial", 24))
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = tk.Label(title_frame, text=title, bg=bg_color,
                              fg="#D4C5B9", font=("Arial", 11))
        title_label.pack(side=tk.LEFT)
        
        # Value section
        self.value_label = tk.Label(self, text=value, bg=bg_color,
                                   fg="#F5EBE0", font=("Arial", 32, "bold"))
        self.value_label.pack(pady=(10, 0))
        
        # Bind hover effect
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        for child in self.winfo_children():
            child.bind("<Enter>", self.on_enter)
            child.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        """Hover effect."""
        self.config(bg="#4A3F35")
        for child in self.winfo_children():
            try:
                child.config(bg="#4A3F35")
            except:
                pass
    
    def on_leave(self, event):
        """Leave hover."""
        self.config(bg=self.bg_color)
        for child in self.winfo_children():
            try:
                child.config(bg=self.bg_color)
            except:
                pass
    
    def update_value(self, new_value: str, animated: bool = True):
        """Update the card value."""
        self.current_value = new_value
        if animated:
            # Simple update with flash effect
            self.value_label.config(fg="#D4A574")
            self.after(200, lambda: self.value_label.config(fg="#F5EBE0"))
        self.value_label.config(text=new_value)
