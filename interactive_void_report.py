"""
Interactive Void Report Generator

Simple command-line interface to generate void reports.
Just enter coordinates and let it run!
"""

import os
from datetime import datetime
from void_report import VoidReportGenerator


def get_float_input(prompt: str, default: float = None) -> float:
    """Get validated float input from user."""
    while True:
        try:
            user_input = input(prompt)
            if not user_input and default is not None:
                return default
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_int_input(prompt: str, default: int = None, min_val: int = None, max_val: int = None) -> int:
    """Get validated integer input from user."""
    while True:
        try:
            user_input = input(prompt)
            if not user_input and default is not None:
                return default
            value = int(user_input)
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def main():
    """Run interactive void report generator."""
    print("="*80)
    print("INTERACTIVE VOID REPORT GENERATOR")
    print("="*80)
    print()

    # API Key
    print("Google Places API Key")
    print("-" * 40)
    default_api_key = os.environ.get('GOOGLE_PLACES_API_KEY', 'AIzaSyA85pSu9Naza2sf1YTjq82D3v7UFtt8I80')
    api_key = input(f"API Key (press Enter to use default): ").strip()
    if not api_key:
        api_key = default_api_key
        print(f"Using default API key: {api_key[:20]}...")
    print()

    # Retailer List
    print("Retailer List")
    print("-" * 40)
    default_retailer_list = "list of retailers.csv"
    retailer_list = input(f"Retailer list file (press Enter for '{default_retailer_list}'): ").strip()
    if not retailer_list:
        retailer_list = default_retailer_list
    print(f"Using: {retailer_list}")
    print()

    # Check if file exists
    if not os.path.exists(retailer_list):
        print(f"ERROR: File not found: {retailer_list}")
        return

    # Location coordinates
    print("Location Coordinates")
    print("-" * 40)
    print("Enter the center point for your search:")
    print("You can either:")
    print("  1. Paste both coordinates together: '33.423248658058945, -96.5887672571626'")
    print("  2. Enter latitude and longitude separately")
    print()

    # Try to get coordinates in one line first
    coords_input = input("Coordinates (lat, lon) or just latitude: ").strip()

    # Check if they pasted both coordinates together
    if ',' in coords_input:
        try:
            parts = coords_input.split(',')
            latitude = float(parts[0].strip())
            longitude = float(parts[1].strip())
            print(f"✓ Parsed coordinates: {latitude}, {longitude}")
        except (ValueError, IndexError):
            print("Error parsing coordinates. Please enter latitude:")
            latitude = get_float_input("Latitude: ")
            longitude = get_float_input("Longitude: ")
    else:
        # They only entered latitude, ask for longitude
        try:
            latitude = float(coords_input)
            longitude = get_float_input("Longitude: ")
        except ValueError:
            print("Invalid latitude. Please try again.")
            latitude = get_float_input("Latitude: ")
            longitude = get_float_input("Longitude: ")

    print()

    # Search parameters
    print("Search Parameters")
    print("-" * 40)
    radius = get_float_input("Radius in miles (default 5.0): ", default=5.0)
    threshold = get_int_input("Match threshold 0-100 (default 80): ", default=80, min_val=0, max_val=100)
    print()

    # Output location
    print("Output Files")
    print("-" * 40)

    # Create outputs folder if it doesn't exist
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created '{output_dir}' folder for reports")

    # Generate timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_output = f"{output_dir}/void_report_{timestamp}.csv"

    output_file = input(f"Output file (press Enter for '{default_output}'): ").strip()
    if not output_file:
        output_file = default_output

    print(f"Output will be saved to: {output_file}")
    print()

    # Confirmation
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Location: ({latitude}, {longitude})")
    print(f"Radius: {radius} miles")
    print(f"Match threshold: {threshold}%")
    print(f"Output: {output_file}")
    print("="*80)
    print()

    confirm = input("Generate report? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    print()
    print("Starting report generation...")
    print()

    try:
        # Create generator
        generator = VoidReportGenerator(api_key, retailer_list)

        # Generate report
        stats = generator.generate_void_report(
            latitude=latitude,
            longitude=longitude,
            radius_miles=radius,
            match_threshold=threshold,
            output_file=output_file
        )

        print()
        print("="*80)
        print("SUCCESS!")
        print("="*80)
        print(f"Report saved to: {output_file}")
        print(f"Missing retailers saved to: {output_file.replace('.csv', '_missing_retailers.csv')}")
        print()
        print("You can now open these files in Excel or any CSV viewer.")
        print("="*80)

    except Exception as e:
        print()
        print("="*80)
        print("ERROR")
        print("="*80)
        print(f"An error occurred: {str(e)}")
        print()
        print("Common issues:")
        print("1. API Key restrictions - Check Google Cloud Console")
        print("   - Go to APIs & Services > Credentials")
        print("   - Edit your API key")
        print("   - Remove HTTP referrer restrictions (or add 'None' restriction)")
        print()
        print("2. API not enabled - Enable Places API in Google Cloud Console")
        print("3. Billing not set up - Places API requires a billing account")
        print("="*80)


if __name__ == "__main__":
    main()
