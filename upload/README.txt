NETLIFY DEPLOYMENT PACKAGE
===========================

This folder contains everything needed to deploy your Retail Void Analysis Dashboard to Netlify.

WHAT'S INCLUDED:
- index.html - Your interactive dashboard (McKinney, TX example)

HOW TO DEPLOY TO NETLIFY:
==========================

OPTION 1: Drag & Drop (Easiest - No Account Needed)
----------------------------------------------------
1. Go to: https://app.netlify.com/drop
2. Drag the entire "upload" folder onto the page
3. Wait 10 seconds
4. Get your live URL: https://[random-name].netlify.app
5. Share with clients!

OPTION 2: With Netlify Account (Custom URL)
--------------------------------------------
1. Sign up at: https://www.netlify.com (free)
2. Click "Add new site" → "Deploy manually"
3. Drag the "upload" folder
4. Get URL: https://yourname.netlify.app
5. Optional: Add custom domain in site settings

OPTION 3: Netlify CLI (Advanced)
---------------------------------
# Install Netlify CLI
npm install -g netlify-cli

# Deploy from this folder
cd upload
netlify deploy

# For production
netlify deploy --prod


TO CREATE NEW DASHBOARDS:
==========================

1. Generate void report:
   cd ..
   python interactive_void_report.py

2. Create HTML dashboard:
   python generate_html_report.py

3. Copy to upload folder:
   cp outputs/void_report_*.html upload/dashboard_[location_name].html

4. Re-deploy to Netlify


EXAMPLE DEPLOYMENT WORKFLOW:
=============================

# Analyze Los Angeles
python interactive_void_report.py
# Enter: 34.0522, -118.2437

# Generate dashboard
python generate_html_report.py

# Copy to upload folder
cp outputs/void_report_*.html upload/los_angeles.html

# Drag upload folder to Netlify
# Share URL with client!


TIPS:
=====
- The HTML file is completely self-contained (no external dependencies except Google Maps)
- Works offline after initial load
- Mobile-friendly and responsive
- No backend server needed
- Free hosting on Netlify


CURRENT DASHBOARD:
==================
Location: McKinney, TX (33.423248658058945, -96.5887672571626)
Radius: 5 miles
Retailers Found: 60
Matched: 7
Missing: 8,569


NEXT STEPS:
===========
1. Open index.html in your browser to preview
2. Deploy to Netlify using one of the options above
3. Share the URL with your real estate clients!


Questions? See:
- ../HTML_DASHBOARD_README.md - Full dashboard documentation
- ../START_HERE.md - Getting started guide
