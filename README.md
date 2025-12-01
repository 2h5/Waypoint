# Waypoint
A clean, utility-focused Discord bot for routing, maps, translation, and reminders.

---

## 🚀 Features

### 📍 Location Tools

#### Route Planner
Generates a driving route between two locations, shows distance & time, and returns a rendered Mapbox map image.  
Based on the `/route` command.

#### Static Map Snapshot
Returns a map with a pinned location using Mapbox Static Maps.  
Powered by `/staticmap`.

**Internal utilities used:**
- Geocoding via Mapbox Search API (`geocode()`)
- Static map renderer & polyline reducer (`static_map_util()`)
- Duration formatter for readable ETAs (`format_duration()`)

---

### 🌐 Translation
Translate text into any ISO-639 2-letter language using GoogleTranslator.  
See `/translate`.

---

### ⏰ Reminders
Simple time-based reminders using short formats like `10m`, `2h`, or `30s`.  
See `/remindme`.

---

## 🛠️ Commands Overview

### /route
**Description:** Driving route between two places + map  
**Usage:**
```
/route "NYC" "Boston"
```

### /staticmap
**Description:** Static map snapshot of a place  
**Usage:**
```
/staticmap "Eiffel Tower"
```

### /translate
**Description:** Translate text to a target language  
**Usage:**
```
/translate es "good morning"
```

### /remindme
**Description:** Reminder after a duration  
**Usage:**
```
/remindme 10m "Take a break"
```

---

## 📦 Installation

### Requirements
- Python 3.10+
- Discord Bot Token
- Mapbox API Token
- Railway (or any hosting) account if deploying publicly

### Clone the repo
```bash
git clone https://github.com/<your-username>/waypoint.git
cd waypoint
```

### Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🔧 Environment Variables

Waypoint uses a `.env` file.  
Create `.env` in the project root:

```
DISCORD_TOKEN=your_discord_bot_token
MAPBOX_TOKEN=your_mapbox_api_key
```

Mapbox is required for all routing and static map features.

---

## ▶️ Running Waypoint

Start the bot locally:

```bash
python main.py
```

Upon successful login, Waypoint will sync all slash commands automatically.

---

## ☁️ Deploying on Railway

1. Create a new project  
2. Connect your GitHub repo  
3. Add the required environment variables in **Railway → Variables**  
4. Deploy  

Railway will automatically rebuild and start the bot on each push.

---

## 📄 License

Licensed under the MIT License.  
See `LICENSE` for details.