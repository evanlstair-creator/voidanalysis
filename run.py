#!/usr/bin/env python3
"""
Quick launcher for void report tool.
Just run: python run.py
"""

import subprocess
import sys
import os

# Change to the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("VOID REPORT TOOL - QUICK LAUNCHER")
print("=" * 80)
print()
print("This tool will help you find retail voids (missing retailers) in any area.")
print()
print("TIP: Copy coordinates from Google Maps by right-clicking on a location")
print("     and clicking the coordinates shown at the top.")
print()
print("=" * 80)
print()

# Run the interactive tool
subprocess.run([sys.executable, "interactive_void_report.py"])
