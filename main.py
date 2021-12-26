
import dearpygui.dearpygui as dpg

from application import MainApplication

# Fix blurry text on Windows 10
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Global dpi aware
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor dpi aware
except Exception:
    pass  # Fail when not Windows


dpg.create_context()

app = MainApplication()
app.viewport_config()

dpg.start_dearpygui()
