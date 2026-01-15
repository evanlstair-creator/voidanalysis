# 🎯 Vista Site Selection - Interactive Dashboard Usage Guide

## ✨ Features Implemented

### 1. **Vista Branding**
- Primary color: #B63A3A (Vista Red)
- Black and white accents
- Professional gradient headers
- Sticky navigation bar

### 2. **Smart Coordinate Input**
- Paste coordinates like: `33.4233994297814, -96.58878795317332`
- Auto-fills latitude and longitude fields
- Supports manual entry

### 3. **Auto Port Detection**
- Backend automatically finds available port (5000-5009)
- Frontend discovers backend automatically
- No manual configuration needed

### 4. **Interactive Tables**
- **Sortable Columns**: Click any header to sort
  - Business Name
  - Matched Chain
  - Distance (mi)
  - Address
  - Rating
  - Category
- Visual indicators (▲ ▼) show sort direction
- Smooth animations on hover

### 5. **Complete Retailer List**
- Shows ALL missing retailers (not limited to 100)
- Category filter dropdown
- Live count: "Showing X of Y retailers"

### 6. **Excel Export**
- Downloads multi-sheet workbook with:
  - **Summary**: Search details and stats
  - **Retailers Found**: All businesses with details
  - **Tenant Opportunities**: ALL missing chains
  - **Category Mix**: Google category breakdown
- Filename includes timestamp
- Broker-friendly format

### 7. **Interactive Map**
- Google Maps integration
- Search center marked in Vista red
- Color-coded markers:
  - 🟢 Green: Matched retailers
  - 🟡 Yellow: Unmatched businesses
- Click markers for detailed info windows

### 8. **Database Storage**
- SQLite database stores all Google Places data
- Deduplicates by place_id
- Tracks first_seen, last_seen, times_seen
- Permanent history of all searches

## 🚀 How to Use

### Step 1: Start Backend Server

```bash
cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"
python3 api_server.py
```

**Expected Output:**
```
================================================================================
🚀 RETAIL VOID ANALYSIS API SERVER
================================================================================
Database: retail_places_database.db
Retailer list: list of retailers_cleaned.csv

Endpoints:
  POST /api/analyze - Run void analysis
  GET  /api/database/stats - Get database statistics
  GET  /api/health - Health check

✅ Server running on http://localhost:5000
================================================================================
```

### Step 2: Open Dashboard

Simply open [interactive_dashboard.html](interactive_dashboard.html) in your browser.

The dashboard will automatically:
1. Find the backend server (checks ports 5000-5009)
2. Display connection status in console
3. Ready to run analysis!

### Step 3: Run Analysis

**Option A: Paste Coordinates**
1. Copy coordinates from Google Maps (right-click → coordinates)
   - Format: `33.4233994297814, -96.58878795317332`
2. Paste into "Coordinates" field
3. Latitude and longitude auto-fill!

**Option B: Manual Entry**
1. Enter latitude
2. Enter longitude
3. Set radius (1-10 miles)

**Then:**
4. Click "RUN ANALYSIS" button
5. Wait for spinner (typically 10-30 seconds)
6. Results appear with stats, map, and tables!

### Step 4: Interact with Data

**Sort Tables:**
- Click any column header to sort
- Click again to reverse sort order
- Visual indicators (▲ ▼) show current sort

**Filter Missing Retailers:**
- Use category dropdown
- Shows count: "Showing X of Y retailers"

**Explore Map:**
- Click markers for detailed info
- Zoom and pan as needed
- Vista red marker = search center
- Green = matched chains
- Yellow = unmatched businesses

**Export to Excel:**
1. Click "Export to Excel" button (top right)
2. Downloads instantly
3. Filename: `Vista_Void_Analysis_2026-01-13T12-30-45.xlsx`
4. Open in Excel/Google Sheets
5. Share with brokers!

## 📊 Understanding Results

### Stats Cards
- **Total Places Found**: All businesses from Google Places API
- **Matched Chains**: Target retailers found in area
- **Tenant Opportunities**: Missing chains (potential voids)
- **Coverage**: % of target retailers present

### Retailers Found Table
- All businesses within radius
- Shows matched chain if recognized
- Distance from search center
- Rating and address
- Status badge (Matched/Unmatched)

### Category Mix Analysis
- Based on Google's business types
- Shows actual retail composition
- Percentage breakdown
- Sortable by count or category

### Tenant Opportunities Table
- ALL missing chains (complete list!)
- Filter by category
- Sorted alphabetically by default
- Click "Category" to group by type

## 💡 Tips & Tricks

### Finding Coordinates
1. Go to Google Maps
2. Right-click on location
3. Click the coordinates (top of menu)
4. Paste into dashboard!

### Best Radius Settings
- **1-3 miles**: Immediate trade area
- **3-5 miles**: Primary market
- **5-10 miles**: Regional analysis

### Database Growth
- Every search adds to database
- Deduplicates automatically
- Track changes over time
- Use `/api/database/stats` to see totals

### Excel Export Usage
- Share "Tenant Opportunities" sheet with brokers
- "Retailers Found" shows competition
- "Category Mix" reveals market composition
- "Summary" provides quick overview

## 🔧 Troubleshooting

### "Backend server not found"
- Make sure `python3 api_server.py` is running
- Check console (F12) for port detection logs
- Backend shows health check attempts in logs

### "Connection error"
- Restart backend server
- Refresh browser page
- Check firewall settings

### No results showing
- Verify coordinates are valid
- Check radius (must be 1-10 miles)
- Look for error messages in red status box
- Check backend terminal for error logs

### Excel export not working
- Make sure results are loaded first
- Button only appears after analysis runs
- Check browser allows downloads

### Map not loading
- Verify Google Maps API key is valid
- Check browser console (F12) for errors
- Make sure "Maps JavaScript API" is enabled

## 📈 Database Files

All data stored in:
```
retail_places_database.db
```

**Tables:**
- `places`: All Google Places data
- `matched_retailers`: Chain matches
- `searches`: Search history

**View stats:**
```bash
curl http://localhost:5000/api/database/stats
```

## 🎨 Design Features

- **Vista Red (#B63A3A)**: Primary brand color
- **Gradient Headers**: Modern, professional look
- **Hover Effects**: Interactive feedback
- **Smooth Animations**: Polished user experience
- **Responsive Design**: Works on all screen sizes
- **Clean Typography**: Easy to read
- **Card-based Layout**: Organized information
- **Professional Tables**: Striped rows, sortable headers

## 🚀 Next Steps

This is a **complete, production-ready dashboard** with:
- ✅ All features implemented
- ✅ Vista branding applied
- ✅ Maximally interactive
- ✅ Maximally creative
- ✅ Database storage
- ✅ Excel export
- ✅ Sortable tables
- ✅ Complete retailer list
- ✅ Category filtering
- ✅ Auto port detection
- ✅ Coordinate paste

**Ready to use for real estate analysis!**

---

**Questions or Issues?**
Check the backend terminal for detailed logs.
Browser console (F12) shows frontend errors.
All data is saved to `retail_places_database.db`.

**Enjoy analyzing retail voids!** 🎯
