"""
Backend API server for retail void analysis
- Runs void analysis on demand
- Saves all Google Places data to SQLite database (deduplicated by place_id)
- Returns results to frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os
from void_report import VoidReportGenerator

try:
    from google_sheets_sync import GoogleSheetsDB
except Exception:
    GoogleSheetsDB = None

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Configuration
DATABASE_PATH = 'retail_places_database.db'
RETAILER_LIST_PATH = 'list of retailers_cleaned.csv'
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', 'AIzaSyA85pSu9Naza2sf1YTjq82D3v7UFtt8I80')
GOOGLE_SHEET_ID = os.environ.get(
    'GOOGLE_SHEET_ID',
    '1at4Q1ZlPMz8WDzpVHKDHYm-46843zGllE9Jf432W570'
)
GOOGLE_SHEETS_CREDENTIALS = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')

SHEETS_DB = None


def init_google_sheets():
    """Initialize Google Sheets integration if credentials are available."""
    global SHEETS_DB

    has_json = bool(os.environ.get('GOOGLE_SHEETS_CREDENTIALS_JSON'))
    has_path = bool(GOOGLE_SHEETS_CREDENTIALS)
    print(f"ℹ️  Google Sheets creds json set: {has_json}, path set: {has_path}")

    if not GoogleSheetsDB:
        print("ℹ️  Google Sheets integration not available (missing dependencies).")
        return

    if not GOOGLE_SHEETS_CREDENTIALS:
        print("ℹ️  Google Sheets integration disabled (GOOGLE_SHEETS_CREDENTIALS not set).")
        return

    try:
        SHEETS_DB = GoogleSheetsDB(GOOGLE_SHEET_ID, GOOGLE_SHEETS_CREDENTIALS)
        print(f"✅ Google Sheets sync enabled: {GOOGLE_SHEET_ID}")
    except Exception as exc:
        print(f"⚠️  Google Sheets sync error: {exc}")
        SHEETS_DB = None


def ensure_google_sheets():
    """Lazy-init Google Sheets in case env vars were set after startup."""
    if SHEETS_DB is None:
        init_google_sheets()
    return SHEETS_DB


def init_database():
    """Initialize SQLite database with schema."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create places table (stores all Google Places data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS places (
            place_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            latitude REAL,
            longitude REAL,
            types TEXT,
            rating REAL,
            user_ratings_total INTEGER,
            business_status TEXT,
            price_level INTEGER,
            phone_number TEXT,
            website TEXT,
            first_seen_date TEXT NOT NULL,
            last_seen_date TEXT NOT NULL,
            times_seen INTEGER DEFAULT 1
        )
    ''')

    # Create matched_retailers table (tracks chain matches)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matched_retailers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_id TEXT NOT NULL,
            matched_chain TEXT NOT NULL,
            match_score REAL NOT NULL,
            match_date TEXT NOT NULL,
            FOREIGN KEY (place_id) REFERENCES places(place_id)
        )
    ''')

    # Create searches table (tracks all searches run)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            radius_miles REAL NOT NULL,
            search_date TEXT NOT NULL,
            total_places_found INTEGER,
            matched_chains INTEGER,
            api_calls_used INTEGER
        )
    ''')

    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_place_name ON places(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_place_location ON places(latitude, longitude)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_matched_chain ON matched_retailers(matched_chain)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_location ON searches(latitude, longitude)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def save_place_to_database(place_info: dict, matched_retailer: str = None, match_score: float = None):
    """
    Save or update place in database.

    Args:
        place_info: Dictionary with place data
        matched_retailer: Matched chain name (if any)
        match_score: Match confidence score (if any)
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    place_id = place_info['place_id']
    current_date = datetime.now().isoformat()

    # Check if place already exists
    cursor.execute('SELECT times_seen FROM places WHERE place_id = ?', (place_id,))
    existing = cursor.fetchone()

    if existing:
        # Update existing place (increment times_seen, update last_seen_date)
        cursor.execute('''
            UPDATE places
            SET last_seen_date = ?,
                times_seen = times_seen + 1,
                rating = ?,
                user_ratings_total = ?,
                business_status = ?
            WHERE place_id = ?
        ''', (
            current_date,
            place_info.get('rating'),
            place_info.get('user_ratings_total'),
            place_info.get('business_status'),
            place_id
        ))
    else:
        # Insert new place
        # Convert types to string if it's a list
        types_str = place_info.get('types', '')
        if isinstance(types_str, list):
            types_str = ', '.join(types_str)

        cursor.execute('''
            INSERT INTO places (
                place_id, name, address, latitude, longitude,
                types, rating, user_ratings_total, business_status,
                first_seen_date, last_seen_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            place_id,
            place_info['name'],
            place_info.get('address', ''),
            place_info['latitude'],
            place_info['longitude'],
            types_str,
            place_info.get('rating'),
            place_info.get('user_ratings_total'),
            place_info.get('business_status', 'UNKNOWN'),
            current_date,
            current_date
        ))

    # If matched to a chain, save the match
    if matched_retailer:
        cursor.execute('''
            INSERT INTO matched_retailers (place_id, matched_chain, match_score, match_date)
            VALUES (?, ?, ?, ?)
        ''', (place_id, matched_retailer, match_score, current_date))

    conn.commit()
    conn.close()


def save_search_to_database(latitude: float, longitude: float, radius: float,
                            total_places: int, matched_chains: int, api_calls: int):
    """Save search metadata to database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO searches (latitude, longitude, radius_miles, search_date,
                            total_places_found, matched_chains, api_calls_used)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (latitude, longitude, radius, datetime.now().isoformat(),
          total_places, matched_chains, api_calls))

    conn.commit()
    conn.close()


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Run void analysis for given coordinates.

    Request body:
    {
        "latitude": 33.423,
        "longitude": -96.588,
        "radius": 5.0
    }

    Returns:
    {
        "stats": {...},
        "retailers_found": [...],
        "retailers_missing": [...]
    }
    """
    try:
        data = request.get_json()

        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        radius = float(data.get('radius', 5.0))

        print(f"\n{'='*80}")
        print(f"API REQUEST: Void Analysis")
        print(f"Coordinates: ({latitude}, {longitude})")
        print(f"Radius: {radius} miles")
        print(f"{'='*80}\n")

        # Initialize void report generator
        generator = VoidReportGenerator(GOOGLE_API_KEY, RETAILER_LIST_PATH)

        # Fetch places from Google (this will handle pagination and multi-type search)
        print("Searching multiple place types...")
        place_types = ['store', 'restaurant', 'cafe', 'shopping_mall', 'supermarket',
                      'clothing_store', 'convenience_store', 'department_store']

        all_places = {}
        api_calls = 0

        for place_type in place_types:
            print(f"  Searching '{place_type}'...")
            type_places = generator.fetch_places_with_pagination(latitude, longitude, radius, place_type)
            api_calls += 3 if len(type_places) == 60 else (2 if len(type_places) > 20 else 1)

            for place in type_places:
                place_id = place.get('place_id')
                if place_id and place_id not in all_places:
                    all_places[place_id] = place

        places = list(all_places.values())
        print(f"\nTotal unique places found: {len(places)}")

        # Process each place and save to database
        retailers_found = []
        matched_retailers_set = set()

        print(f"\nProcessing {len(places)} places...")
        for place in places:
            place_info = generator.extract_place_info(place, latitude, longitude)

            # Only include places within radius
            if place_info['distance_miles'] and place_info['distance_miles'] <= radius:
                # Fuzzy match against retailer list
                place_types_list = place.get('types', [])
                match = generator.fuzzy_match_retailer(place_info['name'], place_types_list, 85)

                matched_retailer = None
                match_score = None

                if match:
                    matched_retailer, match_score = match
                    matched_retailers_set.add(matched_retailer)

                # Save to database (deduplicated by place_id)
                save_place_to_database(place_info, matched_retailer, match_score)

                # Add to results
                retailers_found.append({
                    'name': place_info['name'],
                    'matched_retailer': matched_retailer or '',
                    'match_score': match_score or 0,
                    'distance_miles': place_info['distance_miles'],
                    'address': place_info['address'],
                    'latitude': place_info['latitude'],
                    'longitude': place_info['longitude'],
                    'types': place_info['types'],
                    'rating': place_info['rating'],
                    'user_ratings_total': place_info['user_ratings_total'],
                    'business_status': place_info['business_status'],
                    'place_id': place_info['place_id']
                })

        # Find missing retailers
        missing_retailers = set(generator.target_retailers) - matched_retailers_set

        # Get categories for missing retailers
        retailer_categories = {}
        if os.path.exists(RETAILER_LIST_PATH):
            import csv
            with open(RETAILER_LIST_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    retailer_categories[row['ChainName']] = row['PrimaryCategory']

        retailers_missing = [
            {'name': retailer, 'category': retailer_categories.get(retailer, 'Unknown')}
            for retailer in sorted(missing_retailers)
        ]

        # Save search metadata
        save_search_to_database(latitude, longitude, radius, len(retailers_found),
                               len(matched_retailers_set), api_calls)

        # Calculate stats
        stats = {
            'total_places': len(retailers_found),
            'matched_places': len([r for r in retailers_found if r['matched_retailer']]),
            'unmatched_places': len([r for r in retailers_found if not r['matched_retailer']]),
            'target_retailers': len(generator.target_retailers),
            'retailers_found': len(matched_retailers_set),
            'missing_retailers': len(missing_retailers),
            'coverage_percentage': round(len(matched_retailers_set) / len(generator.target_retailers) * 100, 2) if generator.target_retailers else 0,
            'api_calls_used': api_calls
        }

        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"Total places found: {stats['total_places']}")
        print(f"Matched to target list: {stats['matched_places']}")
        print(f"Target retailers: {stats['target_retailers']}")
        print(f"Found in area: {stats['retailers_found']} ({stats['coverage_percentage']}%)")
        print(f"Missing (voids): {stats['missing_retailers']}")
        print(f"API calls used: {api_calls}")
        print(f"{'='*80}\n")

        if ensure_google_sheets():
            try:
                added_places = SHEETS_DB.save_places(retailers_found)
                SHEETS_DB.save_search({
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius_miles': radius,
                    'total_places': stats['total_places'],
                    'matched_chains': stats['matched_places'],
                    'missing_retailers': stats['missing_retailers'],
                    'coverage_pct': stats['coverage_percentage'],
                    'api_calls_used': stats['api_calls_used']
                })
                print(f"✅ Google Sheets sync: {added_places} new places added")
            except Exception as exc:
                print(f"⚠️  Google Sheets sync failed: {exc}")

        return jsonify({
            'success': True,
            'stats': stats,
            'retailers_found': retailers_found,
            'retailers_missing': retailers_missing
        })

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/database/stats', methods=['GET'])
def database_stats():
    """Get database statistics."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Get total places
        cursor.execute('SELECT COUNT(*) FROM places')
        total_places = cursor.fetchone()[0]

        # Get total searches
        cursor.execute('SELECT COUNT(*) FROM searches')
        total_searches = cursor.fetchone()[0]

        # Get unique chains matched
        cursor.execute('SELECT COUNT(DISTINCT matched_chain) FROM matched_retailers')
        unique_chains = cursor.fetchone()[0]

        # Get most common chains
        cursor.execute('''
            SELECT matched_chain, COUNT(*) as count
            FROM matched_retailers
            GROUP BY matched_chain
            ORDER BY count DESC
            LIMIT 10
        ''')
        top_chains = [{'chain': row[0], 'count': row[1]} for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'total_places': total_places,
            'total_searches': total_searches,
            'unique_chains_found': unique_chains,
            'top_chains': top_chains
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'database': os.path.exists(DATABASE_PATH),
        'retailer_list': os.path.exists(RETAILER_LIST_PATH)
    })


def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port."""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            # Port is in use, try next one
            continue

    raise RuntimeError(f"Could not find available port in range {start_port}-{start_port + max_attempts}")


if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    init_google_sheets()

    # Find available port
    port_env = os.environ.get('PORT')
    port = int(port_env) if port_env else find_available_port(5000)

    print("\n" + "="*80)
    print("🚀 RETAIL VOID ANALYSIS API SERVER")
    print("="*80)
    print(f"Database: {DATABASE_PATH}")
    print(f"Retailer list: {RETAILER_LIST_PATH}")
    print("\nEndpoints:")
    print("  POST /api/analyze - Run void analysis")
    print("  GET  /api/database/stats - Get database statistics")
    print("  GET  /api/health - Health check")
    print(f"\n✅ Server running on http://localhost:{port}")
    print(f"\n⚠️  IMPORTANT: Update the dashboard to use port {port}")
    print(f"   Open interactive_dashboard.html and change:")
    print(f"   fetch('http://localhost:5000/api/analyze')")
    print(f"   to:")
    print(f"   fetch('http://localhost:{port}/api/analyze')")
    print("="*80 + "\n")

    debug = os.environ.get('FLASK_DEBUG') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
