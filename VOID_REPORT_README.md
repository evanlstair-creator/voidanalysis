# Google Places API Void Report Generator

This tool helps you identify retail gaps (voids) in a geographic area by comparing retailers found via Google Places API against your target retailer list.

## IMPORTANT: API Key Setup Required

Before running the tool, you need to configure your Google Places API key to work with this application.

**Current Issue:** Your API key has HTTP referrer restrictions that prevent it from being used in command-line tools.

**Quick Fix:** See [API_KEY_SETUP.md](API_KEY_SETUP.md) for detailed instructions on how to:
1. Remove referrer restrictions from your API key, OR
2. Create a new unrestricted API key

This takes ~2 minutes in Google Cloud Console.

## Features

- Fetches all retailers within a specified radius using Google Places API
- Handles pagination automatically to get all results (not just first 20)
- Calculates distances from your center point using Haversine formula
- Fuzzy matches Google Places results against your target retailer list
- Generates two reports:
  - Full report with all retailers found and match status
  - Missing retailers report showing which retailers are NOT in the area (the "voids")

## Requirements

- Python 3.x
- requests
- rapidfuzz (for fuzzy matching)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start (Recommended)

### Interactive Interface - EASIEST METHOD!

Simply run the interactive script and follow the prompts:

```bash
cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"
python interactive_void_report.py
```

The script will ask you for:
1. Latitude and longitude coordinates
2. Search radius (default: 5 miles)
3. Match threshold (default: 80%)
4. Output file location

Reports are automatically saved to the `outputs/` folder with timestamps.

**Example interaction:**
```
Latitude: 34.0522
Longitude: -118.2437
Radius in miles (default 5.0): 5
Match threshold 0-100 (default 80): 80
```

## Advanced Usage

### Method 1: Command Line

```bash
cd /Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/dashboard\ site\ selection\ matrix/data\ fix
source .venv/bin/activate

python scripts/void_report.py \
  --api-key "AIzaSyA85pSu9Naza2sf1YTjq82D3v7UFtt8I80" \
  --retailer-list "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool/list of retailers.csv" \
  --latitude 34.0522 \
  --longitude -118.2437 \
  --radius 5.0 \
  --threshold 80 \
  --output void_report.csv
```

### Method 2: Python Script

Edit and run the example script:

```bash
python scripts/run_void_report_example.py
```

### Method 3: Programmatic

```python
from void_report import VoidReportGenerator

generator = VoidReportGenerator(
    api_key="YOUR_API_KEY",
    retailer_list_path="path/to/retailers.csv"
)

stats = generator.generate_void_report(
    latitude=34.0522,
    longitude=-118.2437,
    radius_miles=5.0,
    match_threshold=80,
    output_file="void_report.csv"
)
```

## Parameters

- `--api-key`: Your Google Places API key
- `--retailer-list`: Path to CSV file with target retailers (must have 'ChainName' or 'name' column)
- `--latitude`: Center point latitude (decimal degrees)
- `--longitude`: Center point longitude (decimal degrees)
- `--radius`: Search radius in miles (default: 5.0)
- `--threshold`: Fuzzy match threshold 0-100 (default: 80, higher = stricter matching)
- `--output`: Output CSV file path (default: void_report.csv)

## Output Files

### 1. Main Report (e.g., void_report.csv)

Contains all retailers found in the area with columns:
- `name`: Retailer name from Google Places
- `matched_retailer`: Matched name from your target list (if found)
- `match_score`: Similarity score 0-100 (if matched)
- `distance_miles`: Distance from center point
- `address`: Street address
- `latitude`, `longitude`: Coordinates
- `types`: Google Places categories
- `rating`: Google rating
- `user_ratings_total`: Number of reviews
- `business_status`: Operating status
- `place_id`: Google Place ID

### 2. Missing Retailers Report (e.g., void_report_missing_retailers.csv)

Lists all retailers from your target list that were NOT found in the area. These are your "voids" - potential opportunities for expansion.

## Examples

### Example 1: Downtown LA (5 mile radius)
```bash
python scripts/void_report.py \
  --api-key "AIzaSyA85pSu9Naza2sf1YTjq82D3v7UFtt8I80" \
  --retailer-list "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool/list of retailers.csv" \
  --latitude 34.0522 \
  --longitude -118.2437 \
  --radius 5.0 \
  --output reports/la_downtown_void_report.csv
```

### Example 2: New York City (3 mile radius, stricter matching)
```bash
python scripts/void_report.py \
  --api-key "AIzaSyA85pSu9Naza2sf1YTjq82D3v7UFtt8I80" \
  --retailer-list "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool/list of retailers.csv" \
  --latitude 40.7128 \
  --longitude -74.0060 \
  --radius 3.0 \
  --threshold 85 \
  --output reports/nyc_void_report.csv
```

## How It Works

1. **Fetch Places**: Queries Google Places API for all stores within radius
   - Makes initial request with location and radius
   - Automatically follows `next_page_token` to get all results
   - Waits appropriate time between pagination requests

2. **Calculate Distances**: Uses Haversine formula to calculate great-circle distances
   - Filters results to ensure they're within the specified radius
   - Sorts results by distance from center point

3. **Fuzzy Matching**: Compares each place against your retailer list
   - Uses rapidfuzz library for efficient fuzzy string matching
   - Returns best match if score >= threshold
   - Handles variations in naming (e.g., "Walmart" matches "Walmart Supercenter")

4. **Generate Reports**:
   - Main report: All places with match status
   - Missing report: Retailers NOT found (voids)
   - Console summary: Statistics and top missing retailers

## Tips

- **Match Threshold**: Start with 80 and adjust based on results
  - Lower (70-75): More matches but may include false positives
  - Higher (85-90): Fewer matches but more accurate

- **Radius**: Google Places API has limits
  - Maximum radius: ~31 miles (50km)
  - For larger areas, run multiple reports and combine

- **API Limits**: Google Places API has usage quotas
  - Check your Google Cloud Console for limits
  - Each search costs 1 request per page (usually 1-3 pages)

- **Place Types**: Currently searches for 'store' type
  - Can be modified in code to search for specific types
  - Options: restaurant, cafe, store, shopping_mall, etc.

## Troubleshooting

**No results returned**:
- Check API key is valid
- Verify coordinates are correct (lat/lon not reversed)
- Try a smaller radius first

**Too many unmatched results**:
- Lower the match threshold
- Check retailer list column names match expected format

**API errors**:
- Check quota in Google Cloud Console
- Verify Places API is enabled
- Check for request limit exceeded

## Output Example

```
================================================================================
VOID REPORT SUMMARY
================================================================================
Total places found: 487
  - Matched to target list: 156
  - Not matched: 331

Target retailers in list: 8,245
  - Found in area: 156 (1.89%)
  - Missing (voids): 8,089

Output files:
  - All places: void_report.csv
  - Missing retailers: void_report_missing_retailers.csv
================================================================================

Missing retailers (top 20):
  - 1-800-Flowers
  - 100 Montaditos Spain
  - 1001 Optical Australia
  ...
```

## Next Steps

After generating reports:
1. Review the missing retailers report for expansion opportunities
2. Analyze matched retailers by distance to understand competition density
3. Use place_id to get more details from Google Places API if needed
4. Export to Excel or BI tool for further analysis
