# 🚀 Quick Start Guide

## The Easiest Way to Start

### Step 1: Start the Backend

Open Terminal and run:

```bash
cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"
python api_server.py
```

You'll see:
```
================================================================================
🚀 RETAIL VOID ANALYSIS API SERVER
================================================================================
✅ Server running on http://localhost:5001
================================================================================
```

**Note:** The server automatically finds an available port (5000-5009). It will use the first available one.

### Step 2: Open the Dashboard

Simply double-click: `interactive_dashboard.html`

Or from Terminal:
```bash
open interactive_dashboard.html
```

### Step 3: Use It!

The dashboard will **automatically detect** which port the backend is running on!

You'll see a message: **"Connected to backend on port 5001"**

Then:
1. Enter coordinates (e.g., `33.423248658058945`, `-96.5887672571626`)
2. Set radius (e.g., `5` miles)
3. Click **"🚀 Run Analysis"**
4. Wait 30-40 seconds
5. See results!

## What Makes This Easy

✅ **Auto Port Detection**
- Backend finds available port automatically (no conflicts!)
- Frontend auto-discovers the backend (no manual configuration!)
- Just start the server and open the dashboard

✅ **No Configuration Needed**
- No files to edit
- No settings to change
- Works out of the box

✅ **Database Auto-Creates**
- SQLite database created on first run
- Auto-deduplicates by `place_id`
- Builds over time automatically

## Features

### 📊 Google Category Mix Analysis
See what types of businesses Google identifies in the area:
```
Restaurant          32 (33.3%)
Store               28 (29.2%)
Clothing Store      15 (15.6%)
...
```

### 💾 Auto-Building Database
Every search saves:
- All Google Places data
- Matched chains
- Search history
- No duplicates (deduplicated by `place_id`)

### 🗺️ Interactive Map
- Green markers = Matched chains
- Gray markers = Unmatched retailers
- Click markers for details

### 📋 Results Tables
- Retailers Found
- Google Category Mix
- Tenant Opportunities (missing chains)

## Troubleshooting

### Backend won't start
If you see "Address already in use":
```bash
# The server will automatically try ports 5000-5009
# If all are in use, you'll see an error
# Solution: Kill other Flask apps or restart computer
```

### Dashboard says "Backend server not found"
1. Make sure backend is running (`python api_server.py`)
2. Check the terminal - it should say "Server running on http://localhost:XXXX"
3. Try refreshing the dashboard page
4. Check browser console (F12) for errors

### Database errors
```bash
# Delete and recreate
rm retail_places_database.db
python api_server.py
```

## Cost Per Search

- **~$0.50-0.75** per coordinate search
- **$200/month FREE** from Google
- Covers **~300 searches per month** for free

## Files

- `interactive_dashboard.html` - Frontend (double-click to open)
- `api_server.py` - Backend (run in Terminal)
- `retail_places_database.db` - Database (auto-created)
- `list of retailers_cleaned.csv` - 8,455 chains to match

## Example Coordinates

Try these locations:

**McKinney, TX:**
- Latitude: `33.423248658058945`
- Longitude: `-96.5887672571626`
- Radius: `5`

**Dallas, TX (Downtown):**
- Latitude: `32.7767`
- Longitude: `-96.7970`
- Radius: `3`

**Los Angeles, CA (Hollywood):**
- Latitude: `34.0928`
- Longitude: `-118.3287`
- Radius: `5`

## What Happens Behind the Scenes

1. **Backend finds available port** (5000-5009)
2. **Frontend auto-discovers backend** (tries ports 5000-5009)
3. **You enter coordinates**
4. **Frontend sends request to backend**
5. **Backend:**
   - Calls Google Places API (8 place types)
   - Fuzzy matches against 8,455 chains
   - Saves all data to SQLite database
   - Deduplicates by `place_id`
   - Returns results
6. **Frontend displays:**
   - Interactive map
   - Stats cards
   - Google category mix
   - Results tables

## Need Help?

See detailed docs:
- `README_INTERACTIVE.md` - Full guide
- `SETUP_GUIDE.md` - Technical details
- `WHATS_NEW.md` - Recent changes

## Summary

```bash
# Start backend
python api_server.py

# Open dashboard
open interactive_dashboard.html

# That's it! 🎯
```

The system handles everything else automatically!
