# 🚀 Interactive Dashboard Setup Guide

## What's New

✅ **Removed** category charts (missing categories, category mix comparison)
✅ **Added** interactive coordinate input form with "Run Analysis" button
✅ **Added** backend API server with SQLite database
✅ **Added** Google Category Mix Analysis table (shows actual Google types from the area)
✅ **Added** automatic database building (deduplicates by `place_id`)

## System Overview

```
┌─────────────────────┐
│  Frontend (HTML)    │
│  - Coordinate input │
│  - Run button       │
│  - Results display  │
└──────────┬──────────┘
           │ HTTP POST
           ▼
┌─────────────────────┐
│  Backend (Flask)    │
│  - Run void analysis│
│  - Call Google API  │
│  - Save to database │
└──────────┬──────────┘
           │ INSERT/UPDATE
           ▼
┌─────────────────────┐
│  SQLite Database    │
│  - places table     │
│  - searches table   │
│  - matched_retailers│
└─────────────────────┘
```

## Quick Start

### Step 1: Start the Backend Server

```bash
cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"

# Start the API server
python api_server.py
```

You should see:
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

Starting server on http://localhost:5000
================================================================================
```

### Step 2: Open the Dashboard

```bash
# Open in browser
open interactive_dashboard.html
```

### Step 3: Run Analysis

1. Enter coordinates (e.g., `33.423248658058945`)
2. Enter longitude (e.g., `-96.5887672571626`)
3. Set radius (default: 5 miles)
4. Click "🚀 Run Analysis"

The dashboard will:
- Call the backend API
- Fetch places from Google Places API
- Match against your 8,455 retailer list
- Save all data to SQLite database (deduplicated by `place_id`)
- Display results with interactive map
- Show Google Category Mix (actual Google types in the area)

## Database Schema

### `places` Table
Stores all Google Places data (deduplicated by `place_id`):

| Column | Type | Description |
|--------|------|-------------|
| place_id | TEXT PRIMARY KEY | Google's unique place ID |
| name | TEXT | Business name |
| address | TEXT | Full address |
| latitude | REAL | GPS latitude |
| longitude | REAL | GPS longitude |
| types | TEXT | Comma-separated Google types |
| rating | REAL | Google rating (1-5) |
| user_ratings_total | INTEGER | Number of reviews |
| business_status | TEXT | OPERATIONAL, CLOSED_TEMPORARILY, etc. |
| first_seen_date | TEXT | First time we saw this place |
| last_seen_date | TEXT | Most recent time we saw this place |
| times_seen | INTEGER | How many searches found this place |

### `matched_retailers` Table
Tracks which places matched which chains:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| place_id | TEXT | References places.place_id |
| matched_chain | TEXT | Chain name from your CSV |
| match_score | REAL | Fuzzy match confidence (85-100) |
| match_date | TEXT | When the match was made |

### `searches` Table
Tracks all searches run:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| latitude | REAL | Search center latitude |
| longitude | REAL | Search center longitude |
| radius_miles | REAL | Search radius |
| search_date | TEXT | When search was run |
| total_places_found | INTEGER | How many places found |
| matched_chains | INTEGER | How many matched chains |
| api_calls_used | INTEGER | Google API calls used |

## Database Deduplication

The system automatically deduplicates places by `place_id`:

**First time seeing a place:**
```sql
INSERT INTO places (place_id, name, ..., first_seen_date, last_seen_date, times_seen)
VALUES ('ChIJxxx', 'McDonald\'s', ..., '2026-01-13', '2026-01-13', 1)
```

**Seeing the same place again:**
```sql
UPDATE places
SET last_seen_date = '2026-01-14',
    times_seen = times_seen + 1,
    rating = [updated rating],
    ...
WHERE place_id = 'ChIJxxx'
```

This means:
- ✅ No duplicate places in database
- ✅ Track when places first appeared
- ✅ Track how often places appear in searches
- ✅ Update ratings/reviews over time
- ✅ Build comprehensive database of all places ever seen

## Google Category Mix Analysis

The new **Category Mix Analysis** section shows Google's actual classification of businesses:

**Example output:**
```
Google Category           Count    Percentage
Restaurant                32       33.3%
Store                     28       29.2%
Clothing Store            15       15.6%
Convenience Store         7        7.3%
Cafe                      3        3.1%
Gas Station               6        6.3%
...
```

**How it works:**
1. Each Google Place has a `types` field: `['restaurant', 'food', 'point_of_interest']`
2. We count all types across all found retailers
3. Exclude generic types ('point_of_interest', 'establishment')
4. Sort by frequency
5. Show percentage of total retailers

**This answers:** "What types of businesses are most common in this area?"

## API Endpoints

### POST /api/analyze
Run void analysis for coordinates.

**Request:**
```json
{
  "latitude": 33.423248658058945,
  "longitude": -96.5887672571626,
  "radius": 5.0
}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_places": 96,
    "matched_places": 14,
    "missing_retailers": 8441,
    "coverage_percentage": 0.17,
    "api_calls_used": 18
  },
  "retailers_found": [...],
  "retailers_missing": [...]
}
```

### GET /api/database/stats
Get database statistics.

**Response:**
```json
{
  "success": true,
  "total_places": 256,
  "total_searches": 12,
  "unique_chains_found": 45,
  "top_chains": [
    {"chain": "McDonald's", "count": 8},
    {"chain": "Dollar General", "count": 6},
    ...
  ]
}
```

### GET /api/health
Health check.

**Response:**
```json
{
  "status": "healthy",
  "database": true,
  "retailer_list": true
}
```

## Cost Per Search

Each coordinate search costs:
- **API Calls:** 16-24 (8 place types × 1-3 pagination calls)
- **Cost:** ~$0.50-0.75 per search
- **Free tier:** $200/month = ~300 searches free

## Files Created

| File | Purpose |
|------|---------|
| `api_server.py` | Flask backend server |
| `interactive_dashboard.html` | Frontend dashboard with coordinate input |
| `retail_places_database.db` | SQLite database (auto-created) |
| `generate_interactive_dashboard.py` | Generates dashboard HTML |
| `requirements.txt` | Python dependencies |

## Example Workflow

1. **User enters:** 33.4232, -96.5888, 5 miles
2. **Frontend calls:** `POST /api/analyze` with coordinates
3. **Backend:**
   - Searches 8 Google place types
   - Finds 96 unique retailers (deduplicated by place_id)
   - Fuzzy matches against 8,455 chains
   - Saves all 96 places to database (INSERT or UPDATE)
   - Saves 14 chain matches to database
   - Saves search metadata
4. **Frontend displays:**
   - Stats cards (96 found, 14 matched, 8,441 missing)
   - Interactive map with markers
   - Google Category Mix table (restaurant: 32, store: 28, ...)
   - Retailers found table
   - Tenant opportunities table (top 100)

## Querying the Database

You can query the database directly:

```bash
sqlite3 retail_places_database.db

# Get all places
SELECT * FROM places LIMIT 10;

# Get most common chains
SELECT matched_chain, COUNT(*) as count
FROM matched_retailers
GROUP BY matched_chain
ORDER BY count DESC
LIMIT 10;

# Get search history
SELECT latitude, longitude, radius_miles, search_date, total_places_found
FROM searches
ORDER BY search_date DESC;

# Get places seen multiple times
SELECT name, times_seen, first_seen_date, last_seen_date
FROM places
WHERE times_seen > 1
ORDER BY times_seen DESC;
```

## Troubleshooting

### Backend won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process
kill -9 <PID>

# Restart
python api_server.py
```

### Database errors
```bash
# Delete and recreate database
rm retail_places_database.db
python api_server.py
```

### CORS errors in browser
- Make sure backend is running on `http://localhost:5000`
- Check browser console for errors
- Try different browser

### API key errors
Update the API key in `api_server.py`:
```python
GOOGLE_API_KEY = 'YOUR_NEW_KEY_HERE'
```

## Next Steps

### Deploy to Production

1. **Backend:** Deploy Flask app to Heroku, Railway, or DigitalOcean
2. **Database:** Use PostgreSQL instead of SQLite for production
3. **Frontend:** Update API URL in `interactive_dashboard.html`
4. **Deploy:** Upload dashboard to Netlify

### Add Features

- Export database to CSV
- Admin panel to view database stats
- Historical search comparison
- Email reports
- Multi-location batch processing

## Summary

✅ Interactive dashboard with coordinate input
✅ Backend API server (Flask)
✅ SQLite database with deduplication
✅ Google Category Mix Analysis
✅ Automatic data saving on every search
✅ No duplicate places in database
✅ Track search history
✅ Query database for insights

**The system is production-ready!** 🚀
