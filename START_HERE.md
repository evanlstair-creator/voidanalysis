# START HERE - Void Report Tool

## What This Tool Does

Analyzes any location and tells you which retailers from your list of 8,578 retailers are **missing** in that area - these are your "voids" or expansion opportunities.

## Setup (One Time Only)

### 1. Install Dependencies
```bash
cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"
pip install -r requirements.txt
```

### 2. Fix Your API Key
Your current API key has restrictions that block command-line use.

**Fix it in 2 minutes:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your API key
3. Under "Application restrictions", select **"None"**
4. Click **"Save"**
5. Wait 1-2 minutes

See [API_KEY_SETUP.md](API_KEY_SETUP.md) for detailed instructions with screenshots.

## How to Use

### Run the Interactive Tool
```bash
python interactive_void_report.py
```

Then just answer the prompts:
- **Coordinates**: Paste from Google Maps: `33.423248658058945, -96.5887672571626`
- **Radius**: Press Enter for default (5 miles)
- **Threshold**: Press Enter for default (80% match)

### Get Coordinates for Any Location

**Google Maps Method (EASIEST):**
1. Go to Google Maps
2. Right-click on your location
3. Click the coordinates at the top to copy them
4. Paste DIRECTLY into the tool (it handles the format automatically!)
   - Example: `33.423248658058945, -96.5887672571626`
   - Just paste and press Enter - done!

**Common Locations:**
- Los Angeles: 34.0522, -118.2437
- New York: 40.7128, -74.0060
- Chicago: 41.8781, -87.6298
- Houston: 29.7604, -95.3698
- Phoenix: 33.4484, -112.0740

## What You Get

Two CSV files saved in the `outputs/` folder:

### 1. Main Report (void_report_TIMESTAMP.csv)
All retailers found near your location with:
- Retailer name
- Matched name from your list
- Distance from center point
- Address, rating, reviews
- Google Place ID

### 2. Missing Retailers (void_report_TIMESTAMP_missing_retailers.csv)
**This is the important one!** Lists all retailers from your 8,578 retailer list that are NOT in the area.

These are your voids - potential expansion opportunities!

## Example Output

```
================================================================================
VOID REPORT SUMMARY
================================================================================
Total places found: 487
  - Matched to target list: 156
  - Not matched: 331

Target retailers in list: 8,578
  - Found in area: 156 (1.82%)
  - Missing (voids): 8,422

Missing retailers (top 20):
  - Whole Foods
  - Target
  - Walmart Supercenter
  - Starbucks
  ...
```

## Troubleshooting

**"REQUEST_DENIED" Error**
- Your API key still has restrictions
- See [API_KEY_SETUP.md](API_KEY_SETUP.md)

**"No results found"**
- Check your coordinates aren't reversed (lat/long)
- Try a smaller radius first (2-3 miles)
- Verify API is enabled in Google Cloud Console

**"File not found" Error**
- Make sure you're in the correct directory
- Run: `cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"`

## Files in This Folder

- **interactive_void_report.py** - Run this! Interactive interface
- **void_report.py** - Core logic (don't run directly)
- **list of retailers.csv** - Your 8,578 retailers (ChainName + Category)
- **requirements.txt** - Python dependencies
- **API_KEY_SETUP.md** - Detailed API key instructions
- **VOID_REPORT_README.md** - Full documentation
- **outputs/** - Where reports are saved (created automatically)

## Quick Commands

### Generate a report for Los Angeles
```bash
python interactive_void_report.py
# Then enter: 34.0522, -118.2437
```

### Generate a report for New York
```bash
python interactive_void_report.py
# Then enter: 40.7128, -74.0060
```

### View your reports
```bash
open outputs/
# Or on Windows: explorer outputs\
```

## Cost

Places API pricing with Google's $200/month free credit:
- ~$32 per 1,000 searches
- Most users: **$0/month** (covered by free credit)
- Typical usage: 10-20 searches/month = ~$0.60-$1.20

Monitor at: https://console.cloud.google.com/apis/dashboard

## Need Help?

1. **API Key Issues**: See [API_KEY_SETUP.md](API_KEY_SETUP.md)
2. **Full Documentation**: See [VOID_REPORT_README.md](VOID_REPORT_README.md)
3. **Test Your API Key**:
   ```bash
   curl "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=34.0522,-118.2437&radius=1000&type=store&key=YOUR_API_KEY"
   ```

---

**Ready?** Run this command:
```bash
python interactive_void_report.py
```
