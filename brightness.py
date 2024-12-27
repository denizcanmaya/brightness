import customtkinter as ctk
import screen_brightness_control as sbc
from PIL import Image
import json
import os
from pathlib import Path

class BrightnessControl:
    def __init__(self):
        self.monitors = sbc.list_monitors()
        self.settings_file = Path("brightness_settings.json")
        
        # Theme settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main window setup
        self.root = ctk.CTk()
        self.root.title("Brightness Control")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Main container
        self.container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.header = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 20))
        
        self.title = ctk.CTkLabel(
            self.header,
            text="Brightness Control",
            font=("Helvetica", 24, "bold")
        )
        self.title.pack(side="left")
        
        # Theme toggle
        self.theme_var = ctk.StringVar(value="dark")
        self.theme_button = ctk.CTkSwitch(
            self.header,
            text="Dark Mode",
            command=self.toggle_theme,
            variable=self.theme_var,
            onvalue="dark",
            offvalue="light"
        )
        self.theme_button.pack(side="right")
        
        # Monitor frames
        self.monitor_frames = {}
        for monitor in self.monitors:
            self.create_monitor_frame(monitor)
        
        # Preset buttons
        self.create_preset_buttons()
        
        # Load saved settings
        self.load_settings()

    def create_monitor_frame(self, monitor):
        frame = ctk.CTkFrame(self.container)
        frame.pack(fill="x", pady=10)
        
        # Monitor label with current brightness
        label = ctk.CTkLabel(
            frame,
            text=f"Monitor: {monitor}",
            font=("Helvetica", 14, "bold")
        )
        label.pack(pady=5)
        
        # Brightness slider
        slider = ctk.CTkSlider(
            frame,
            from_=0,
            to=100,
            command=lambda val, m=monitor: self.update_brightness(m, val),
            width=400
        )
        slider.set(sbc.get_brightness(display=monitor)[0])
        slider.pack(pady=10)
        
        # Brightness value label
        value_label = ctk.CTkLabel(
            frame,
            text=f"{int(slider.get())}%",
            font=("Helvetica", 12)
        )
        value_label.pack()
        
        self.monitor_frames[monitor] = {
            "frame": frame,
            "slider": slider,
            "value_label": value_label
        }

    def create_preset_buttons(self):
        presets_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        presets_frame.pack(fill="x", pady=20)
        
        presets = [(25, "Low"), (50, "Medium"), (75, "High"), (100, "Max")]
        
        for value, text in presets:
            btn = ctk.CTkButton(
                presets_frame,
                text=text,
                command=lambda v=value: self.apply_preset(v),
                width=80
            )
            btn.pack(side="left", padx=5, expand=True)

    def update_brightness(self, monitor, value):
        brightness = int(value)
        sbc.set_brightness(brightness, display=monitor)
        self.monitor_frames[monitor]["value_label"].configure(
            text=f"{brightness}%"
        )
        self.save_settings()

    def apply_preset(self, value):
        for monitor in self.monitors:
            self.monitor_frames[monitor]["slider"].set(value)
            self.update_brightness(monitor, value)

    def toggle_theme(self):
        new_mode = self.theme_var.get()
        ctk.set_appearance_mode(new_mode)

    def save_settings(self):
        settings = {
            "theme": self.theme_var.get(),
            "brightness": {
                monitor: int(self.monitor_frames[monitor]["slider"].get())
                for monitor in self.monitors
            }
        }
        with open(self.settings_file, "w") as f:
            json.dump(settings, f)

    def load_settings(self):
        if self.settings_file.exists():
            with open(self.settings_file, "r") as f:
                settings = json.load(f)
                
            # Apply theme
            self.theme_var.set(settings.get("theme", "dark"))
            self.toggle_theme()
            
            # Apply brightness
            saved_brightness = settings.get("brightness", {})
            for monitor, brightness in saved_brightness.items():
                if monitor in self.monitor_frames:
                    self.monitor_frames[monitor]["slider"].set(brightness)
                    self.update_brightness(monitor, brightness)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BrightnessControl()
    app.run()