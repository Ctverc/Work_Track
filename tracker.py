import time
import json
import datetime
import threading
import win32gui
import os
from PIL import ImageGrab

LOG_FILE = "activity_log.json"
SCREENSHOT_DIR = "screenshots"

is_tracking = False
is_screenshotting = False
screenshot_interval = 60

def get_active_window_title():
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd) or "Unknown Window"
    except Exception:
        return "Unknown Window"

def get_date_and_hour(dt):
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:00")

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_log(log):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4, ensure_ascii=False)

def track_active_windows_loop():
    global is_tracking
    log_data = load_log()
    current_window = None
    start_time = None

    while is_tracking:
        active_window = get_active_window_title()
        now = datetime.datetime.now()

        if active_window != current_window:
            if current_window:
                if current_window and start_time:
                    try:
                        today = datetime.date.today()
                        start_dt = datetime.datetime.strptime(start_time, "%H:%M:%S").replace(
                            year=today.year, month=today.month, day=today.day
                        )
                        end_dt = now
                        split_and_save_record(log_data, current_window, start_dt, end_dt)
                    except ValueError as e:
                        print("Chyba při převodu času:", e)

                    save_log(log_data)

            current_window = active_window
            start_time = now.strftime("%H:%M:%S")

        time.sleep(1)

def screenshot_loop():
    global is_screenshotting, screenshot_interval
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    while is_screenshotting:
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        hour_str = now.strftime("%H00")

        folder_path = os.path.join(SCREENSHOT_DIR, date_str, hour_str)
        os.makedirs(folder_path, exist_ok=True)

        filename = now.strftime("%Y-%m-%d_%H-%M-%S.png")
        path = os.path.join(folder_path, filename)

        screenshot = ImageGrab.grab()
        screenshot.save(path)
        print(f"[✓] Screenshot uložen: {path}")
        time.sleep(screenshot_interval)

def split_and_save_record(log_data, window, start_dt, end_dt):
    while start_dt < end_dt:
        next_hour = (start_dt + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        segment_end = min(end_dt, next_hour - datetime.timedelta(seconds=1))

        date_key, hour_key = get_date_and_hour(start_dt)
        log_data.setdefault(date_key, {}).setdefault(hour_key, []).append({
            "window": window,
            "start_time": start_dt.strftime("%H:%M:%S"),
            "end_time": segment_end.strftime("%H:%M:%S")
        })

        start_dt = segment_end + datetime.timedelta(seconds=1)