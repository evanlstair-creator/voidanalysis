# Netlify Deployment Guide

## 🚀 Your Dashboard is Ready!

Everything you need is in the **`upload/`** folder.

## Quick Deploy (30 seconds)

### Step 1: Open Netlify Drop
Go to: **https://app.netlify.com/drop**

### Step 2: Drag & Drop
Drag the entire **`upload`** folder onto the page

### Step 3: Done!
You'll get a live URL like: `https://amazing-name-12345.netlify.app`

**No account needed!** Share the URL immediately.

## What You're Deploying

```
upload/
├── index.html (570 KB)    ← Your interactive dashboard
└── README.txt             ← Deployment instructions
```

The dashboard includes:
- ✅ Interactive Google Map
- ✅ Distance ring filters (1-5 miles)
- ✅ Retailers found vs missing tables
- ✅ CSV & PDF export
- ✅ Search/filter functionality
- ✅ Mobile responsive design

## Current Dashboard Details

**Location:** McKinney, TX
**Coordinates:** 33.423248658058945, -96.5887672571626
**Radius:** 5 miles
**Retailers Found:** 60
**Matched:** 7
**Missing (Voids):** 8,569

## Easy Deployment Options

### Option 1: No Account (Quickest)
```
1. Visit: https://app.netlify.com/drop
2. Drag 'upload' folder
3. Get random URL
4. Share immediately
```

**Pros:** Instant, no signup
**Cons:** Random URL, expires after inactivity

### Option 2: Free Account (Best)
```
1. Sign up: https://www.netlify.com
2. New Site → Deploy manually
3. Drag 'upload' folder
4. Customize URL to: yourproject.netlify.app
```

**Pros:** Custom URL, doesn't expire, analytics
**Cons:** Requires free account (1 minute signup)

### Option 3: Command Line (Advanced)
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd upload
netlify deploy --prod
```

**Pros:** Scriptable, can automate
**Cons:** Requires Node.js

## Creating Multiple Dashboards

Want to deploy dashboards for multiple locations?

### Step 1: Create Multiple Reports
```bash
# Los Angeles
python interactive_void_report.py
# Enter: 34.0522, -118.2437

# New York
python interactive_void_report.py
# Enter: 40.7128, -74.0060

# Chicago
python interactive_void_report.py
# Enter: 41.8781, -87.6298
```

### Step 2: Generate HTML Dashboards
```bash
python generate_html_report.py
```

### Step 3: Create Multi-Page Site
```bash
# Copy dashboards to upload folder
cp outputs/void_report_20260113_193048.html upload/los_angeles.html
cp outputs/void_report_20260113_193102.html upload/new_york.html
cp outputs/void_report_20260113_193115.html upload/chicago.html
```

### Step 4: Create Index Page
Create `upload/index.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Retail Void Analysis - All Markets</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        h1 { color: #667eea; }
        .location {
            background: #f7fafc;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        a {
            color: #667eea;
            text-decoration: none;
            font-size: 1.2em;
            font-weight: 600;
        }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>🗺️ Retail Void Analysis Reports</h1>
    <p>Select a market to view the interactive dashboard:</p>

    <div class="location">
        <a href="los_angeles.html">Los Angeles, CA</a>
        <p>Downtown LA • 5 Mile Radius • 487 Retailers Found</p>
    </div>

    <div class="location">
        <a href="new_york.html">New York, NY</a>
        <p>Manhattan • 5 Mile Radius • 892 Retailers Found</p>
    </div>

    <div class="location">
        <a href="chicago.html">Chicago, IL</a>
        <p>Downtown Chicago • 5 Mile Radius • 634 Retailers Found</p>
    </div>
</body>
</html>
```

### Step 5: Deploy All
Drag the entire `upload` folder to Netlify!

## Automated Workflow

Use the helper script to automatically prepare for deployment:

```bash
# Generate report
python interactive_void_report.py

# Create HTML dashboard
python generate_html_report.py

# Prepare for Netlify (copies to upload folder)
python prepare_for_netlify.py

# Deploy!
# Drag upload folder to https://app.netlify.com/drop
```

## Custom Domain

Want to use your own domain? (e.g., `voidanalysis.yourcompany.com`)

1. Deploy to Netlify (with account)
2. Go to Site Settings → Domain Management
3. Add custom domain
4. Update DNS records (Netlify provides instructions)
5. Done! SSL certificate auto-generated

## URL Structure Examples

**Single Dashboard:**
```
https://retail-void-analysis.netlify.app/
  └── Interactive dashboard for one location
```

**Multiple Dashboards:**
```
https://retail-void-analysis.netlify.app/
  ├── index.html (landing page)
  ├── los_angeles.html
  ├── new_york.html
  └── chicago.html
```

## Sharing with Clients

### Email Template
```
Hi [Client],

I've created an interactive retail void analysis for [Location].

View it here: https://your-site.netlify.app

The dashboard shows:
- Interactive map with all retailers in the trade area
- Filter by 1-5 mile radius rings
- List of retailers present vs missing (voids)
- Export to CSV or PDF

Let me know if you have any questions!

Best,
[Your Name]
```

### What They'll See
1. Professional, clean interface
2. Google Map with their location
3. Distance ring selector
4. Tables of found/missing retailers
5. Export buttons for their own analysis

## Updating Your Dashboard

To update with new data:

1. Generate new report:
   ```bash
   python interactive_void_report.py
   ```

2. Create new HTML:
   ```bash
   python generate_html_report.py
   ```

3. Copy to upload folder:
   ```bash
   python prepare_for_netlify.py
   ```

4. Re-deploy to Netlify:
   - Drag `upload` folder again, OR
   - In Netlify dashboard: Deploys → Drag and drop

## Troubleshooting

**Dashboard doesn't load:**
- Check browser console for errors
- Ensure Google Maps API key is valid
- Try different browser

**Map shows gray area:**
- API key may have referrer restrictions
- See API_KEY_SETUP.md to fix

**Slow loading:**
- Normal for first load (570 KB HTML)
- Subsequent loads are cached
- Consider splitting into multiple pages if >1 MB

**Can't export CSV:**
- Enable pop-ups in browser
- Try different browser
- Use "Save As" on the table

## Cost

**Netlify Free Tier:**
- 100 GB bandwidth/month
- 300 build minutes/month
- Unlimited sites
- Free SSL certificates
- **Perfect for this use case!**

Typical usage: ~0.6 MB per view = ~166,000 views/month free

## Support

Need help?
- [HTML_DASHBOARD_README.md](HTML_DASHBOARD_README.md) - Dashboard features
- [START_HERE.md](START_HERE.md) - Getting started
- Netlify Docs: https://docs.netlify.com

---

## Ready to Deploy?

```bash
# 1. Open Netlify Drop
open https://app.netlify.com/drop

# 2. Open upload folder
open upload/

# 3. Drag upload folder to Netlify
#    Get your live URL!
```

**That's it! 🎉**
