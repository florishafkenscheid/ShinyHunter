from PIL import ImageGrab, Image
import win32gui




class Screenshotter:
    def __init__(self):
        self.window_rect = 0
        self.left = 0
        self.top = 0
        self.right = 0
        self.bottom = 0
    

    def _get_window_rect(self, window_title):
        """Get the coordinates of the Emulator window."""
        def callback(hwnd, win_rect):
            if win32gui.GetWindowText(hwnd).__contains__(window_title):
                rect = win32gui.GetWindowRect(hwnd)
                win_rect.append(rect)
        win_rect = []
        win32gui.EnumWindows(callback, win_rect)
        self.left, self.top, self.right, self.bottom = win_rect[0] if win_rect else None
    
    def _poke_screenshot(self):
        """
        screenshot_left = right - 300
        screenshot_top = top
        screenshot_right = right
        screenshot_bottom = top + 300
        """
        return ImageGrab.grab(bbox=(self.right-300, self.top, self.right, self.top+300))
    
    def _emu_screenshot(self, pokemon, count):
        screenshot = ImageGrab.grab(bbox=(self.left, self.top, self.right, self.bottom))
        screenshot.save(f"screenshots/{pokemon}-{count}.png")

        return f"screenshots/{pokemon}-{count}.png"
