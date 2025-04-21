# 🖥️ Activity Tracker Web App

A full-stack application for tracking desktop activity, assigning custom tags to applications, managing session data, and reviewing detailed usage analytics. Built with **Python (Flask)** on the backend and **React** on the frontend.

---

## ✨ Features

### 🔍 Activity Tracking
- Tracks the currently active window on the user's system
- Records start and end times of each active window
- Splits records across hour boundaries for accurate hourly summaries

### 📸 Screenshot Capture
- Periodic screenshots captured at configurable intervals
- Saved locally to the disk

### 📊 Statistics Dashboard
- View total time spent per application per day
- View time breakdown per hour
- See grouped sessions by application, including duration of each

### 🏷️ Tag Manager
- Assign tags (e.g., `work`, `break`, `meeting`) to each unique application
- Filter and aggregate time based on tags
- Set minimum duration filters to ignore short-lived activities
- Collapsible tag sections for better UI organization

### 🧹 Cleanup Tools
- Merge/group applications under a unified label
- Remove unused or outdated application entries from tag list
- Zebra-striped UI for better readability

---

## 🧠 Technologies Used

- **Backend**: Python, Flask
- **Frontend**: React
- **System Access**: `win32gui` (for window tracking), `PIL.ImageGrab` (for screenshots)
- **Data Format**: JSON (`activity_log.json` for tracking, `tags.json` for tags)

---

## 🚀 How It Works

### Tracking & Screenshot
- Two background threads run:
  - One checks the active window every second
  - One captures a screenshot at a set interval (e.g., every 60 seconds)

- When a window changes:
  - The previous window's session is ended
  - Its duration is split into separate records for each hour it spans
  - Data is stored under date + hour in `activity_log.json`

### Frontend App
- React frontend communicates with Flask backend via API
- Users can:
  - View usage stats for each application and hour
  - Assign tags and manage them
  - Toggle visibility of sections
  - Filter minimum durations for cleaner analytics

---

## 🔐 API Endpoints (Flask)

| Endpoint               | Method | Description                                  |
|------------------------|--------|----------------------------------------------|
| `/api/activity`        | GET    | Returns all recorded activity                |
| `/api/tags`            | GET    | Returns current tags for applications        |
| `/api/tags`            | POST   | Updates or adds a tag for an application     |
| `/api/tags/rename`     | POST   | Replaces selected applications' tags         |
| `/api/tags/delete`     | POST   | Deletes selected applications from tag list  |

---

## 📁 Data Format Example

### `activity_log.json`

```json
{
  "2025-04-19": {
    "11:00": [
      {
        "window": "TPProject – main.py",
        "start_time": "11:58:43",
        "end_time": "11:59:59"
      }
    ],
    "12:00": [
      {
        "window": "TPProject – main.py",
        "start_time": "12:00:00",
        "end_time": "12:03:20"
      }
    ]
  }
}
