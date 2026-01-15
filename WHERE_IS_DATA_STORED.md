# 📍 Where is Google Places Data Stored?

## Current Setup (Local)

### 1. SQLite Database (`retail_places_database.db`)
**Location:** `/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool/retail_places_database.db`

**What's Stored:**
- Every place from Google Places API
- Automatically deduplicated by `place_id`
- Retailer matches
- Search history
- First seen / last seen dates
- Times seen count

**When It Saves:**
Every time you click "Run Analysis":
1. Backend fetches from Google Places API
2. Processes the data
3. **Saves everything to SQLite database**
4. Returns results to dashboard
5. Database grows over time

**Example:**
```
Run 1: Find 96 places → Save all 96 to database
Run 2: Find 150 places → Save 150 (some might be duplicates, auto-handled)
Database now has: ~200+ unique places
```

### 2. In-Memory Only (Browser)
**What's NOT Saved:**
- The dashboard itself doesn't save anything
- When you close the browser, dashboard data is gone
- But the database still has everything!

## Netlify Deployment Options

### Option A: Static Only (No Database) ❌ Not Recommended

**What You Deploy:**
- Just `interactive_dashboard.html`
- No backend
- No database

**What Happens:**
- Dashboard loads but can't run analysis
- No connection to backend
- **Data is NOT saved**
- Error: "Backend server not found"

**Good For:**
- Viewing pre-generated reports only
- Demonstrations with static data

### Option B: Full Stack (With Database) ✅ **RECOMMENDED**

**Architecture:**
```
Netlify (Frontend)     →    Backend API (Cloud)    →    PostgreSQL (Cloud Database)
HTML Dashboard              Python Flask               Persistent Storage
```

**What You Deploy:**

**1. Frontend to Netlify:**
- `interactive_dashboard.html`
- Free hosting

**2. Backend to Render/Railway/Heroku:**
- `api_server.py`
- `void_report.py`
- `requirements.txt`
- Free tier available

**3. Database:**
- PostgreSQL on Render/Railway/Heroku
- Or ElephantSQL (free tier)
- Or Supabase (free tier)

**What Happens:**
- ✅ Dashboard works from anywhere
- ✅ All data saved to cloud database
- ✅ Accessible by your whole team
- ✅ Data persists forever
- ✅ Build comprehensive database over time

## How Data Flows

### Current (Local) Flow:
```
1. You open: interactive_dashboard.html (in browser)
2. Enter coordinates
3. Dashboard calls: http://localhost:5002/api/analyze
4. Backend:
   - Calls Google Places API
   - Gets retailers
   - SAVES to local SQLite database
   - Returns results
5. Dashboard displays results
6. Database: retail_places_database.db has new data
```

### Future (Cloud) Flow:
```
1. Anyone opens: https://yoursite.netlify.app
2. Enter coordinates
3. Dashboard calls: https://your-api.railway.app/api/analyze
4. Cloud Backend:
   - Calls Google Places API
   - Gets retailers
   - SAVES to cloud PostgreSQL database
   - Returns results
5. Dashboard displays results
6. Database: Cloud PostgreSQL has new data (accessible from anywhere)
```

## Database Schema (What's Stored)

### `places` Table
Every business found by Google Places API:
```sql
CREATE TABLE places (
    place_id TEXT PRIMARY KEY,         -- Google's unique ID
    name TEXT,                         -- Business name
    address TEXT,                      -- Full address
    latitude REAL,                     -- GPS
    longitude REAL,                    -- GPS
    types TEXT,                        -- Google categories
    rating REAL,                       -- 1-5 stars
    user_ratings_total INTEGER,        -- Review count
    business_status TEXT,              -- OPERATIONAL, CLOSED, etc.
    first_seen_date TEXT,              -- When first discovered
    last_seen_date TEXT,               -- Most recent sighting
    times_seen INTEGER                 -- How many searches found it
);
```

### `matched_retailers` Table
Which places matched which chains:
```sql
CREATE TABLE matched_retailers (
    id INTEGER PRIMARY KEY,
    place_id TEXT,                     -- Links to places table
    matched_chain TEXT,                -- Chain name from CSV
    match_score REAL,                  -- Fuzzy match confidence
    match_date TEXT                    -- When matched
);
```

### `searches` Table
History of all analyses run:
```sql
CREATE TABLE searches (
    id INTEGER PRIMARY KEY,
    latitude REAL,                     -- Search location
    longitude REAL,
    radius_miles REAL,
    search_date TEXT,
    total_places_found INTEGER,
    matched_chains INTEGER,
    api_calls_used INTEGER             -- For cost tracking
);
```

## Current Database Location

**Mac:**
```bash
/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool/retail_places_database.db
```

**View the database:**
```bash
cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"

# Open in DB Browser
open retail_places_database.db

# Or query with SQLite
sqlite3 retail_places_database.db
> SELECT COUNT(*) FROM places;
> SELECT * FROM places LIMIT 5;
> .quit
```

## What Gets Saved After Each Search

**Example: Search McKinney, TX (5 mile radius)**

**Google API Returns:**
- 96 unique retailers

**Backend Saves to Database:**
1. **96 rows in `places` table** (or updates if already exist)
   - Each with full Google data
   - Deduplicated by `place_id`

2. **14 rows in `matched_retailers` table**
   - Only the places that matched your chain list

3. **1 row in `searches` table**
   - Metadata about this search

**Database Size Growth:**
- After 1 search: ~100 places
- After 10 searches: ~500-800 places (some overlap)
- After 100 searches: ~5,000-8,000 places
- After 1,000 searches: ~50,000-80,000 places

**File Size:**
- 1,000 places: ~500 KB
- 10,000 places: ~5 MB
- 100,000 places: ~50 MB

Very efficient!

## Netlify Deployment Strategy

### For Now (Testing):
Keep running locally:
```bash
python api_server.py  # Backend
open interactive_dashboard.html  # Frontend
```
Data saves to local SQLite.

### For Production:

**Step 1: Deploy Backend to Railway** (Free)
1. Create account: https://railway.app
2. New Project → Deploy from GitHub
3. Add environment variables:
   - `GOOGLE_API_KEY`
   - `DATABASE_URL` (Railway provides PostgreSQL)
4. Deploy!
5. Get URL: `https://your-app.railway.app`

**Step 2: Update Frontend**
Change API URL in `interactive_dashboard.html`:
```javascript
// OLD (local)
const portsToTry = [5000, 5001, ...];

// NEW (cloud)
const API_BASE_URL = 'https://your-app.railway.app';
```

**Step 3: Deploy Frontend to Netlify**
1. Drag `interactive_dashboard.html` to Netlify Drop
2. Get URL: `https://vista-void-analysis.netlify.app`
3. Share with anyone!

### Migration Path

**Phase 1: Local (Current)**
- Frontend: Local HTML file
- Backend: Local Python (localhost:5002)
- Database: Local SQLite
- **Good for:** Testing, development

**Phase 2: Hybrid**
- Frontend: Netlify (public URL)
- Backend: Still local
- Database: Still local SQLite
- **Good for:** Sharing dashboard, you run backend when needed

**Phase 3: Full Cloud (Recommended)**
- Frontend: Netlify
- Backend: Railway/Render
- Database: PostgreSQL (cloud)
- **Good for:** Production, team access, always available

## Summary

**Where Data Is Stored Now:**
```
📁 retail_places_database.db (SQLite)
├── places (all Google Places data)
├── matched_retailers (chain matches)
└── searches (search history)
```

**Where Data Will Be Stored on Netlify:**

**Option A (Static):** Nowhere - dashboard can't save ❌

**Option B (Full Stack):** Cloud PostgreSQL database ✅
- Same schema
- Accessible from anywhere
- Persistent forever
- Backed up automatically

**Recommendation:** Deploy full stack so data builds over time and is accessible to your whole team!

Want me to create a deployment guide?
