import json

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import tracker
import os
app = Flask(__name__)
CORS(app)

window_thread = None
screenshot_thread = None





TAGS_FILE = "tags.json"

def load_tags():
    if os.path.exists(TAGS_FILE):
        with open(TAGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tags(tags):
    with open(TAGS_FILE, "w", encoding="utf-8") as f:
        json.dump(tags, f, indent=2, ensure_ascii=False)

@app.route("/api/tags", methods=["GET"])
def get_tags():
    return jsonify(load_tags())

@app.route("/api/tags", methods=["POST"])
def update_tag():
    data = request.json  # { "window": "...", "tag": "..." }
    if not data or "window" not in data or "tag" not in data:
        return jsonify({"error": "invalid request"}), 400
    tags = load_tags()
    tags[data["window"]] = data["tag"]
    save_tags(tags)
    return jsonify({"status": "ok"})


@app.route("/api/tags/rename", methods=["POST"])
def rename_tags():
    data = request.json  # {"windows": ["...", "..."], "new_name": "TPProject"}
    if not data or "windows" not in data or "new_name" not in data:
        return jsonify({"error": "invalid request"}), 400

    tags = load_tags()
    for win in data["windows"]:
        tags[win] = data["new_name"]

    save_tags(tags)
    return jsonify({"status": "renamed"})



@app.route("/api/tags/delete", methods=["POST"])
def delete_tags():
    data = request.json  # {"windows": ["...", "..."]}
    if not data or "windows" not in data:
        return jsonify({"error": "invalid request"}), 400

    tags = load_tags()
    for win in data["windows"]:
        tags.pop(win, None)

    save_tags(tags)
    return jsonify({"status": "deleted"})


import os
from flask import request, jsonify

@app.route("/api/open-folder", methods=["POST"])
def open_folder():
    data = request.json
    date = data.get("date")
    hour = data.get("hour")

    if not date or not hour:
        return jsonify({"error": "Missing date or hour"}), 400

    folder_path = os.path.abspath(os.path.join("screenshots", date, hour.replace(":", "") ))
    print("Opening folder:", folder_path)
    if os.path.exists(folder_path):
        try:
            os.startfile(folder_path)
            return jsonify({"status": "opened"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Folder does not exist"}), 404

@app.route("/api/activity")
def get_activity():
    with open("activity_log.json", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify({
        "tracking": tracker.is_tracking,
        "screenshotting": tracker.is_screenshotting,
        "interval": tracker.screenshot_interval
    })

@app.route("/api/start", methods=["POST"])
def start_tracking():
    global window_thread
    if not tracker.is_tracking:
        tracker.is_tracking = True
        window_thread = threading.Thread(target=tracker.track_active_windows_loop, daemon=True)
        window_thread.start()
    return jsonify({"status": "tracking started"})

@app.route("/api/stop", methods=["POST"])
def stop_tracking():
    tracker.is_tracking = False
    return jsonify({"status": "tracking stopped"})

@app.route("/api/screenshot/start", methods=["POST"])
def start_screenshotting():
    global screenshot_thread
    if not tracker.is_screenshotting:
        tracker.is_screenshotting = True
        screenshot_thread = threading.Thread(target=tracker.screenshot_loop, daemon=True)
        screenshot_thread.start()
    return jsonify({"status": "screenshotting started"})

@app.route("/api/screenshot/stop", methods=["POST"])
def stop_screenshotting():
    tracker.is_screenshotting = False
    return jsonify({"status": "screenshotting stopped"})

@app.route("/api/screenshot/interval", methods=["POST"])
def set_interval():
    data = request.json
    new_interval = data.get("interval", 60)
    tracker.screenshot_interval = int(new_interval)
    return jsonify({"status": f"interval set to {new_interval} seconds"})

if __name__ == "__main__":
    app.run(debug=True)
