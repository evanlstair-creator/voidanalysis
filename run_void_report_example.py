"""
Example script to run the void report generator.
This demonstrates how to use the VoidReportGenerator class programmatically.
"""

from void_report import VoidReportGenerator

# Configuration
GOOGLE_API_KEY = "AIzaSyA85pSu9Naza2sf1YTjq82D3v7UFtt8I80"
RETAILER_LIST = "list of retailers.csv"  # In same directory

# Example coordinates (you can change these)
# These are for downtown Los Angeles
LATITUDE = 34.0522
LONGITUDE = -118.2437
RADIUS_MILES = 5.0

# Fuzzy match threshold (0-100)
# 80 means 80% similarity required to match
MATCH_THRESHOLD = 80

# Output file
OUTPUT_FILE = "void_report_example.csv"


def main():
    """Run the void report generator."""
    print("Starting void report generation...")
    print(f"Searching near: ({LATITUDE}, {LONGITUDE})")
    print(f"Radius: {RADIUS_MILES} miles")
    print(f"Match threshold: {MATCH_THRESHOLD}%")
    print()

    # Create generator instance
    generator = VoidReportGenerator(GOOGLE_API_KEY, RETAILER_LIST)

    # Generate report
    stats = generator.generate_void_report(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        radius_miles=RADIUS_MILES,
        match_threshold=MATCH_THRESHOLD,
        output_file=OUTPUT_FILE
    )

    print("\nReport generation complete!")
    print(f"Check {OUTPUT_FILE} for full results.")


if __name__ == "__main__":
    main()
