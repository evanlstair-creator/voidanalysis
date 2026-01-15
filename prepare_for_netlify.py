#!/usr/bin/env python3
"""
Prepare latest void report for Netlify deployment.
Automatically copies the latest HTML dashboard to the upload folder.
"""

import os
import glob
import shutil
from datetime import datetime


def prepare_netlify_upload():
    """Prepare upload folder for Netlify deployment."""

    # Paths
    upload_dir = "upload"
    outputs_dir = "outputs"

    # Create upload directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)

    # Find latest HTML dashboard
    html_files = glob.glob(f'{outputs_dir}/void_report_*.html')
    if not html_files:
        print("❌ No HTML dashboards found in outputs/")
        print("\nGenerate one first:")
        print("  python generate_html_report.py")
        return

    latest_html = max(html_files, key=os.path.getmtime)

    # Copy as index.html
    index_path = f'{upload_dir}/index.html'
    shutil.copy2(latest_html, index_path)

    # Get file info
    file_size = os.path.getsize(index_path)
    size_kb = file_size / 1024

    print("=" * 80)
    print("✅ NETLIFY DEPLOYMENT PACKAGE READY!")
    print("=" * 80)
    print()
    print(f"📁 Upload Folder: {os.path.abspath(upload_dir)}/")
    print(f"📄 Dashboard: index.html ({size_kb:.1f} KB)")
    print(f"📊 Source Report: {os.path.basename(latest_html)}")
    print()
    print("=" * 80)
    print("DEPLOY TO NETLIFY - 3 EASY OPTIONS:")
    print("=" * 80)
    print()
    print("🚀 OPTION 1: Drag & Drop (Fastest)")
    print("   1. Go to: https://app.netlify.com/drop")
    print("   2. Drag the 'upload' folder onto the page")
    print("   3. Done! Get your live URL")
    print()
    print("🌐 OPTION 2: With Account (Custom URL)")
    print("   1. Sign up at: https://www.netlify.com")
    print("   2. New site → Deploy manually")
    print("   3. Drag 'upload' folder")
    print("   4. Customize your URL")
    print()
    print("💻 OPTION 3: Command Line")
    print("   cd upload")
    print("   netlify deploy --prod")
    print()
    print("=" * 80)
    print("PREVIEW LOCALLY:")
    print("=" * 80)
    print(f"   open {os.path.abspath(index_path)}")
    print()
    print("=" * 80)
    print("TIP: Create dashboards for multiple locations and deploy them all!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    prepare_netlify_upload()
