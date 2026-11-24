import os
import subprocess
import time
import pyautogui
from PIL import ImageGrab
from pathlib import Path
from typing import Dict, Any
from config import SCREENSHOTS_DIR

# Safety setup for PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

class DesktopDriver:
    """
    Desktop & OS Control Engine for opening apps, automation keyboard/mouse actions, and taking system screenshots.
    """

    @staticmethod
    def open_application(app_name: str) -> Dict[str, Any]:
        """
        Open local desktop applications on Windows.
        """
        app_name_lower = app_name.lower()
        print(f"[Desktop] Opening application: {app_name}")
        
        common_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "chrome": "start chrome",
            "edge": "start msedge",
            "cmd": "start cmd",
            "powershell": "start powershell",
            "explorer": "explorer.exe",
            "code": "code",
            "vscode": "code"
        }

        try:
            if app_name_lower in common_apps:
                cmd = common_apps[app_name_lower]
                subprocess.Popen(cmd, shell=True)
            else:
                # Try pressing Win key and typing app name
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.write(app_name, interval=0.05)
                time.sleep(0.5)
                pyautogui.press('enter')

            screenshot = DesktopDriver.take_desktop_screenshot("app_opened")
            return {
                "status": "success",
                "message": f"Launched application '{app_name}'",
                "screenshot": screenshot
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def type_keys(text: str) -> Dict[str, Any]:
        """
        Simulate keyboard typing.
        """
        print(f"[Desktop] Typing text: {text}")
        pyautogui.write(text, interval=0.03)
        screenshot = DesktopDriver.take_desktop_screenshot("typed_keys")
        return {"status": "success", "message": f"Typed '{text}'", "screenshot": screenshot}

    @staticmethod
    def press_shortcut(shortcut: str) -> Dict[str, Any]:
        """
        Press hotkeys like 'ctrl+c', 'alt+tab', 'enter', etc.
        """
        print(f"[Desktop] Pressing hotkey: {shortcut}")
        keys = [k.strip().lower() for k in shortcut.split('+')]
        if len(keys) == 1:
            pyautogui.press(keys[0])
        else:
            pyautogui.hotkey(*keys)
        screenshot = DesktopDriver.take_desktop_screenshot("hotkey_pressed")
        return {"status": "success", "message": f"Pressed hotkey '{shortcut}'", "screenshot": screenshot}

    @staticmethod
    def take_desktop_screenshot(name_prefix: str = "desktop") -> str:
        """
        Capture entire desktop screen with fallback for headless/virtual display environments.
        """
        timestamp = int(time.time() * 1000)
        filename = f"{name_prefix}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename
        try:
            img = ImageGrab.grab()
            img.save(filepath)
        except Exception as e:
            print(f"[Desktop Warning] Screen grab failed ({e}). Generating status image.")
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (800, 600), color=(17, 20, 32))
            d = ImageDraw.Draw(img)
            d.text((40, 280), f"Desktop Capture ({name_prefix}) - System Active", fill=(255, 255, 255))
            img.save(filepath)
        return f"/screenshots/{filename}"
