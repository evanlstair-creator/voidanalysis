# Interactive HTML Dashboard - Retail Void Analysis

## Overview

Beautiful, professional HTML dashboards for presenting retail void analysis to real estate audiences. Perfect for site selection, market analysis, and identifying expansion opportunities.

## Features

### 🗺️ Interactive Google Map
- Shows search center with prominent marker
- Displays all found retailers as color-coded pins
  - 🟢 Green = Matched to target list
  - ⚪ Gray = Not matched
- Click pins for retailer details (name, match, distance, address, rating)
- Auto-fits to show all retailers within selected radius

### 📊 Dynamic Distance Filtering
- Filter by 1, 2, 3, 4, or 5 mile radius
- Real-time updates to:
  - Map view and radius circle
  - Retailer tables
  - Statistics cards
  - Filter indicators

### 📈 Live Statistics
- Current search radius
- Total places found
- Matched retailers count
- Missing retailers (voids) count

### 🔍 Search & Filter
- Search boxes for both found and missing retailers
- Real-time filtering as you type
- Searches names, addresses, categories

### 📥 Export Options
- **CSV Export**: Download filtered data with all details
- **PDF Export**: Print-friendly dashboard view
- Both exports respect current radius filter

### 📋 Retailer Tables

**Found Retailers Table:**
- Retailer name
- Matched chain (from target list)
- Match confidence score
- Distance from center
- Full address
- Google rating

**Missing Retailers Table:**
- Retailer name
- Business category (from your master list)
- Status indicator
- Sortable and searchable

## How to Generate Dashboard

### Method 1: Automatic (from latest report)
```bash
cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"
python generate_html_report.py
```

### Method 2: From specific CSV
```bash
python generate_html_report.py --csv outputs/void_report_20260113_193048.csv
```

### Method 3: Custom output location
```bash
python generate_html_report.py \
  --csv outputs/void_report_20260113_193048.csv \
  --output my_dashboard.html
```

## Workflow

### 1. Generate Void Report Data
```bash
python interactive_void_report.py
# Enter coordinates, get CSV reports
```

### 2. Create HTML Dashboard
```bash
python generate_html_report.py
# Converts CSV to interactive HTML
```

### 3. Open & Present
```bash
# Open in browser
open outputs/void_report_20260113_193048.html

# Or deploy to Netlify (see below)
```

## Netlify Deployment

### Quick Deploy
1. Drag & drop the HTML file to https://app.netlify.com/drop
2. Get instant live URL to share
3. No account required for testing

### Custom Domain Deploy
1. Create Netlify account (free)
2. New Site from Deploy
3. Upload HTML file
4. Get `yoursite.netlify.app` URL
5. Optional: Add custom domain

### Batch Deploy Multiple Locations
Create an `index.html` that links to multiple reports:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Retail Void Analysis - All Locations</title>
</head>
<body>
    <h1>Market Analysis Reports</h1>
    <ul>
        <li><a href="los_angeles_report.html">Los Angeles, CA</a></li>
        <li><a href="mckinney_tx_report.html">McKinney, TX</a></li>
        <li><a href="chicago_il_report.html">Chicago, IL</a></li>
    </ul>
</body>
</html>
```

Then drag the entire folder to Netlify.

## Customization

### Change Colors
Edit `generate_html_report.py`, find the `<style>` section:
```css
/* Primary brand color */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your brand colors */
background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
```

### Add Logo
In the HTML header section, add:
```html
<div class="header">
    <div class="container">
        <img src="your-logo.png" alt="Logo" style="height: 50px;">
        <h1>Retail Void Analysis Report</h1>
        ...
    </div>
</div>
```

### Change Map Style
Find `initMap()` function, modify `styles` array:
```javascript
styles: [
    // Hide POIs
    {
        featureType: "poi",
        elementType: "labels",
        stylers: [{ visibility: "off" }]
    },
    // Add more custom styles
]
```

Browse styles at: https://mapstyle.withgoogle.com/

## Dashboard Components

### Statistics Cards
- Automatically update based on selected radius
- Color-coded (green for matched, red for missing)
- Large, easy-to-read numbers

### Radius Filter Buttons
- Visual feedback (active state)
- Hover effects
- Mobile-responsive (stack on small screens)

### Retailer Tables
- Sortable by clicking headers
- Hover highlighting for readability
- Responsive (horizontal scroll on mobile)

### Map Controls
- Zoom in/out
- Fullscreen mode
- Street view (when available)
- Satellite view toggle

## Browser Compatibility

✅ Chrome/Edge (recommended)
✅ Firefox
✅ Safari
✅ Mobile browsers

Requires JavaScript enabled.

## Performance

- Handles 1000+ retailers smoothly
- Fast filtering and search
- Lazy-loads map tiles
- Optimized for 4G mobile connections

## Use Cases

### Real Estate Site Selection
- Show clients what retailers are present/missing
- Identify expansion opportunities
- Compare multiple trade areas

### Market Analysis Presentations
- Professional, interactive reports
- Export for offline viewing
- Print for physical presentations

### Client Deliverables
- Share via URL (Netlify)
- Email HTML file (opens in any browser)
- Embed in websites/portals

### Internal Analysis
- Quick visual assessment of trade areas
- Compare 1-mile vs 5-mile coverage
- Identify retailer clusters

## Tips for Real Estate Presentations

1. **Start Wide**: Show 5-mile view for context
2. **Zoom In**: Filter to 1-2 miles for immediate trade area
3. **Highlight Voids**: Use missing retailers table to show opportunities
4. **Export Data**: Provide CSV for client's own analysis
5. **Multiple Locations**: Create dashboards for competitive sites

## File Structure

```
outputs/
├── void_report_20260113_193048.csv          # Raw data (found)
├── void_report_20260113_193048_missing...   # Raw data (missing)
└── void_report_20260113_193048.html         # Interactive dashboard ⭐
```

## Example Output

### Statistics Summary
```
Search Radius: 5 miles
Total Places Found: 60
Matched Retailers: 7
Missing Retailers: 8,569
```

### Found Retailers (Sample)
| Retailer | Matched To | Score | Distance | Rating |
|----------|-----------|-------|----------|--------|
| Dollar General | Dollar General | 100% | 0.1 mi | 4.2 ⭐ |
| QuikTrip | QuikTrip | 100% | 0.17 mi | 4.5 ⭐ |
| O'Reilly Auto Parts | O'Reilly Auto Parts | 100% | 0.22 mi | 4.5 ⭐ |

### Missing Retailers (Sample)
| Retailer | Category | Status |
|----------|----------|--------|
| Whole Foods | Grocery | Not Found |
| Target | Discount Stores | Not Found |
| Starbucks | Restaurant - Coffee/Tea | Not Found |

## Troubleshooting

**Map doesn't load:**
- Check Google Maps API key is valid
- Ensure API key has no referrer restrictions
- Check browser console for errors

**No retailers showing:**
- Verify CSV file has data
- Check lat/lon coordinates are correct
- Ensure retailers have valid coordinates

**Export doesn't work:**
- Enable pop-ups for CSV download
- Use print dialog (Ctrl/Cmd+P) for PDF
- Check browser download permissions

**Slow performance:**
- Close other browser tabs
- Try smaller radius filter
- Clear browser cache

## Advanced Features

### Adding Business Intelligence
Modify the HTML to add:
- Trade area demographics
- Competition analysis
- Sales projections
- Heat maps

### Integration with CRM
Export CSV and import to:
- Salesforce
- HubSpot
- Custom CRM systems

### Automated Reports
Create batch script to:
1. Run void analysis for multiple locations
2. Generate HTML dashboards
3. Upload to Netlify via API
4. Email links to stakeholders

## Support

Issues or questions? Check:
- [START_HERE.md](START_HERE.md) - Basic setup
- [VOID_REPORT_README.md](VOID_REPORT_README.md) - CLI tool docs
- [API_KEY_SETUP.md](API_KEY_SETUP.md) - API configuration

## License

For internal use. Powered by Google Maps Platform.

---

**Ready to create your first dashboard?**

```bash
# 1. Run analysis
python interactive_void_report.py

# 2. Generate dashboard
python generate_html_report.py

# 3. Open in browser
open outputs/*.html
```

That's it! 🚀
