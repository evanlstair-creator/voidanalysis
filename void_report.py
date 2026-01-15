"""
Google Places API Void Report Generator

This script fetches retailers from Google Places API within a specified radius,
performs fuzzy matching against a target retailer list, and generates a void report
showing which retailers are present/missing in the area.
"""

import requests
import time
import csv
import json
from math import radians, cos, sin, asin, sqrt
from typing import List, Dict, Tuple, Optional
import argparse
import os
import sys
import types

# Avoid pandas import issues in environments with NumPy 2.x.
if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")
    pandas_stub.NA = None
    sys.modules["pandas"] = pandas_stub

from rapidfuzz import fuzz, process


class VoidReportGenerator:
    """Generate void reports using Google Places API."""

    # Convert miles to meters for Google Places API
    MILES_TO_METERS = 1609.34

    def __init__(self, api_key: str, retailer_list_path: str):
        """
        Initialize the void report generator.

        Args:
            api_key: Google Places API key
            retailer_list_path: Path to CSV file with target retailers
        """
        self.api_key = api_key
        self.retailer_list_path = retailer_list_path
        self.target_retailers = self._load_target_retailers()
        self.places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    def _load_target_retailers(self) -> List[str]:
        """Load target retailers from CSV file."""
        retailers = []
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                with open(self.retailer_list_path, 'r', encoding=encoding) as f:
                    return self._parse_retailers(f)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not decode {self.retailer_list_path} with any common encoding")

    def _parse_retailers(self, f) -> List[str]:
        """Parse retailers from file object."""
        retailers = []
        reader = csv.DictReader(f)
        # Check for common column names
        for row in reader:
            # Look for ChainName first (from your CSV), then other common names
            if 'ChainName' in row:
                retailers.append(row['ChainName'].strip())
            elif 'retailer' in row:
                retailers.append(row['retailer'].strip())
            elif 'name' in row:
                retailers.append(row['name'].strip())
            elif 'retailer_name' in row:
                retailers.append(row['retailer_name'].strip())
            else:
                # If column name unknown, take first column
                retailers.append(list(row.values())[0].strip())

        print(f"Loaded {len(retailers)} target retailers")
        return retailers

    def haversine_distance(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """
        Calculate the great circle distance in miles between two points
        on the earth (specified in decimal degrees).

        Args:
            lon1, lat1: Longitude and latitude of point 1
            lon2, lat2: Longitude and latitude of point 2

        Returns:
            Distance in miles
        """
        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        # Radius of earth in miles
        miles = 3956 * c
        return miles

    def fetch_places_with_pagination(
        self,
        latitude: float,
        longitude: float,
        radius_miles: float,
        place_type: str = 'store'
    ) -> List[Dict]:
        """
        Fetch all places from Google Places API, handling pagination.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_miles: Search radius in miles
            place_type: Type of place to search for (default: 'store')

        Returns:
            List of place dictionaries
        """
        all_places = []
        radius_meters = int(radius_miles * self.MILES_TO_METERS)

        # Initial request
        params = {
            'location': f"{latitude},{longitude}",
            'radius': radius_meters,
            'type': place_type,
            'key': self.api_key
        }

        print(f"Fetching places within {radius_miles} miles of ({latitude}, {longitude})...")

        page = 1
        while True:
            response = requests.get(self.places_url, params=params)

            if response.status_code != 200:
                print(f"Error: API returned status code {response.status_code}")
                print(f"Response: {response.text}")
                break

            data = response.json()

            if data.get('status') not in ['OK', 'ZERO_RESULTS']:
                print(f"Error: API returned status {data.get('status')}")
                print(f"Message: {data.get('error_message', 'No error message')}")
                break

            results = data.get('results', [])
            all_places.extend(results)
            print(f"Page {page}: Retrieved {len(results)} places (Total: {len(all_places)})")

            # Check for next page token
            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break

            # Google requires a short delay before using next_page_token
            print("Waiting for next page token to become valid...")
            time.sleep(2)

            # Update params for next page
            params = {
                'pagetoken': next_page_token,
                'key': self.api_key
            }
            page += 1

        print(f"Total places retrieved: {len(all_places)}")
        return all_places

    def extract_place_info(self, place: Dict, center_lat: float, center_lon: float) -> Dict:
        """
        Extract relevant information from a place result.

        Args:
            place: Place dictionary from API
            center_lat: Center point latitude for distance calculation
            center_lon: Center point longitude for distance calculation

        Returns:
            Dictionary with extracted place information
        """
        location = place.get('geometry', {}).get('location', {})
        lat = location.get('lat')
        lon = location.get('lng')

        distance = None
        if lat and lon:
            distance = self.haversine_distance(center_lon, center_lat, lon, lat)

        return {
            'name': place.get('name', ''),
            'place_id': place.get('place_id', ''),
            'address': place.get('vicinity', ''),
            'types': place.get('types', []),
            'latitude': lat,
            'longitude': lon,
            'distance_miles': round(distance, 2) if distance else None,
            'rating': place.get('rating'),
            'user_ratings_total': place.get('user_ratings_total'),
            'business_status': place.get('business_status', 'UNKNOWN')
        }

    def fuzzy_match_retailer(self, place_name: str, place_types: List[str] = None, threshold: int = 85) -> Optional[Tuple[str, int]]:
        """
        Intelligently match a place name against target retailers.
        Uses multiple strategies to avoid false matches like "McDonald's Arabian Peninsula"

        Args:
            place_name: Name of the place from Google Places
            place_types: Google types for the place (e.g., ['restaurant', 'store'])
            threshold: Minimum similarity score (0-100) to consider a match

        Returns:
            Tuple of (matched_retailer, score) or None if no match
        """
        if not self.target_retailers:
            return None

        # Clean the place name - remove common location suffixes
        clean_name = place_name
        # Remove location indicators that interfere with matching
        location_patterns = [
            r'\s+#\d+$',  # " #1234"
            r'\s+-\s+[A-Z][a-z]+\s*[A-Z]*.*$',  # " - Van Alstyne"
            r'\s+[A-Z][a-z]+\s+Store$',  # " Van Alstyne Store"
        ]
        import re
        for pattern in location_patterns:
            clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)

        # Strategy 1: Exact word matching (most reliable)
        # If retailer name appears as complete words in the Google name
        place_words = set(clean_name.lower().split())
        best_match = None
        best_score = 0

        for retailer in self.target_retailers:
            retailer_words = set(retailer.lower().split())

            # Check if all retailer words appear in place name
            if retailer_words.issubset(place_words):
                # Calculate how much extra stuff is in the Google name
                extra_words = len(place_words) - len(retailer_words)
                # Prefer matches with fewer extra words
                score = 100 - (extra_words * 5)  # Penalty for extra words
                if score > best_score:
                    best_score = score
                    best_match = retailer

        # Strategy 2: Partial matching with stricter rules
        if not best_match or best_score < 90:
            # Use token_sort_ratio which is more forgiving of word order
            # but less likely to match unrelated names
            result = process.extractOne(
                clean_name,
                self.target_retailers,
                scorer=fuzz.token_sort_ratio
            )

            if result:
                candidate, candidate_score = result[0], result[1]

                # Additional validation: check if match makes sense
                # Reject if the matched name is much shorter and not actually in the place name
                if candidate_score >= threshold:
                    # Require that the retailer name words actually appear in place name
                    retailer_words = candidate.lower().split()
                    place_lower = clean_name.lower()

                    # Check if key words from retailer appear in place name
                    key_words_present = sum(1 for word in retailer_words if word in place_lower)
                    word_coverage = (key_words_present / len(retailer_words)) * 100

                    if word_coverage >= 80:  # At least 80% of retailer words must appear
                        if candidate_score > best_score:
                            best_score = candidate_score
                            best_match = candidate

        # Final validation: prevent false positives with single-word chains
        if best_match:
            best_match_words = best_match.lower().split()

            # RULE 1: Single-word chains must match exactly or be the first word
            if len(best_match_words) == 1:
                single_word = best_match_words[0]
                place_words_list = clean_name.lower().split()

                # Must be exact match OR first word (brand name position)
                # Examples: "Express" should match "Express" but not "Hibachi Express"
                if single_word not in place_words_list:
                    return None

                # If it appears but not as first word, and place has 2+ words, likely false positive
                if len(place_words_list) >= 2 and place_words_list[0] != single_word:
                    # Exception: if score is perfect (100) and it's the only word
                    if best_score != 100 or len(place_words_list) > 1:
                        return None

            # RULE 2: Prevent substring-only matches (like "Cream" matching "Ice Cream")
            # The matched chain should be a meaningful portion of the name, not just a fragment
            if len(best_match_words) <= 2:
                place_lower = clean_name.lower()
                match_lower = best_match.lower()

                # Check if matched term appears as a standalone phrase boundary
                # "Braum's Ice Cream & Dairy Store" should NOT match just "Cream"
                # But "Cream" by itself should match "Cream"
                if match_lower in place_lower:
                    # Find the position of the match
                    match_pos = place_lower.find(match_lower)
                    match_end = match_pos + len(match_lower)

                    # Check if it's truly standalone (word boundaries)
                    is_start = match_pos == 0 or place_lower[match_pos - 1] in ' -&'
                    is_end = match_end >= len(place_lower) or place_lower[match_end] in ' -&'

                    # If match is in the middle of other words, likely false positive
                    # Unless it's a very short place name (1-2 words total)
                    place_word_count = len(clean_name.split())
                    if place_word_count >= 3 and not (is_start and is_end):
                        # Additional check: is this a suffix match? (e.g., "Cream" at end of "Ice Cream")
                        if match_pos > 0:
                            return None

            # Return if score meets threshold
            if best_score >= threshold:
                return (best_match, best_score)

        return None

    def generate_void_report(
        self,
        latitude: float,
        longitude: float,
        radius_miles: float = 5.0,
        match_threshold: int = 80,
        output_file: str = 'void_report.csv'
    ) -> Dict:
        """
        Generate a complete void report.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_miles: Search radius in miles (default: 5)
            match_threshold: Fuzzy match threshold (default: 80)
            output_file: Output CSV file path

        Returns:
            Dictionary with report statistics
        """
        print("\n" + "="*80)
        print(f"VOID REPORT GENERATION")
        print(f"Center: ({latitude}, {longitude})")
        print(f"Radius: {radius_miles} miles")
        print(f"Match Threshold: {match_threshold}%")
        print("="*80 + "\n")

        # Fetch places using MULTIPLE TYPES to get more than 60 results
        # Google Places API limits to 60 results per type, so we search multiple types
        print("Searching multiple place types to maximize coverage...")
        place_types = ['store', 'restaurant', 'cafe', 'shopping_mall', 'supermarket',
                      'clothing_store', 'convenience_store', 'department_store']

        all_places = {}  # Use dict to deduplicate by place_id

        for place_type in place_types:
            print(f"  Searching '{place_type}'...")
            type_places = self.fetch_places_with_pagination(latitude, longitude, radius_miles, place_type)
            for place in type_places:
                place_id = place.get('place_id')
                if place_id and place_id not in all_places:
                    all_places[place_id] = place

        places = list(all_places.values())
        print(f"\nTotal unique places found: {len(places)} (after deduplication)")

        # Process each place
        matched_places = []
        unmatched_places = []
        matched_retailers = set()

        print(f"\nProcessing {len(places)} places...")
        for place in places:
            place_info = self.extract_place_info(place, latitude, longitude)

            # Only include places within the radius (API sometimes returns extras)
            if place_info['distance_miles'] and place_info['distance_miles'] <= radius_miles:
                # Pass place types to matching function for smarter matching
                place_types_list = place.get('types', [])
                match = self.fuzzy_match_retailer(place_info['name'], place_types_list, match_threshold)

                if match:
                    place_info['matched_retailer'] = match[0]
                    place_info['match_score'] = match[1]
                    matched_places.append(place_info)
                    matched_retailers.add(match[0])
                else:
                    place_info['matched_retailer'] = ''
                    place_info['match_score'] = ''
                    unmatched_places.append(place_info)

        # Find retailers not found in the area (the "voids")
        missing_retailers = set(self.target_retailers) - matched_retailers

        # Write results to CSV
        all_places_processed = matched_places + unmatched_places

        if all_places_processed:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'name', 'matched_retailer', 'match_score', 'distance_miles',
                    'address', 'latitude', 'longitude', 'types', 'rating',
                    'user_ratings_total', 'business_status', 'place_id'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                # Sort by distance
                all_places_processed.sort(key=lambda x: x.get('distance_miles', 999))

                for place in all_places_processed:
                    # Convert types list to string
                    place['types'] = ', '.join(place['types'])
                    writer.writerow(place)

        # Write missing retailers report
        missing_file = output_file.replace('.csv', '_missing_retailers.csv')
        with open(missing_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['missing_retailer'])
            for retailer in sorted(missing_retailers):
                writer.writerow([retailer])

        # Generate summary statistics
        stats = {
            'total_places_found': len(all_places_processed),
            'matched_places': len(matched_places),
            'unmatched_places': len(unmatched_places),
            'target_retailers': len(self.target_retailers),
            'retailers_found': len(matched_retailers),
            'retailers_missing': len(missing_retailers),
            'coverage_percentage': round(len(matched_retailers) / len(self.target_retailers) * 100, 2) if self.target_retailers else 0
        }

        # Print summary
        print("\n" + "="*80)
        print("VOID REPORT SUMMARY")
        print("="*80)
        print(f"Total places found: {stats['total_places_found']}")
        print(f"  - Matched to target list: {stats['matched_places']}")
        print(f"  - Not matched: {stats['unmatched_places']}")
        print()
        print(f"Target retailers in list: {stats['target_retailers']}")
        print(f"  - Found in area: {stats['retailers_found']} ({stats['coverage_percentage']}%)")
        print(f"  - Missing (voids): {stats['retailers_missing']}")
        print()
        print(f"Output files:")
        print(f"  - All places: {output_file}")
        print(f"  - Missing retailers: {missing_file}")
        print("="*80 + "\n")

        if missing_retailers:
            print(f"Missing retailers (top 20):")
            for retailer in sorted(missing_retailers)[:20]:
                print(f"  - {retailer}")
            if len(missing_retailers) > 20:
                print(f"  ... and {len(missing_retailers) - 20} more")

        return stats


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Generate void report using Google Places API'
    )
    parser.add_argument(
        '--api-key',
        required=True,
        help='Google Places API key (or set GOOGLE_PLACES_API_KEY env var)'
    )
    parser.add_argument(
        '--retailer-list',
        required=True,
        help='Path to CSV file with target retailers'
    )
    parser.add_argument(
        '--latitude',
        type=float,
        required=True,
        help='Center point latitude'
    )
    parser.add_argument(
        '--longitude',
        type=float,
        required=True,
        help='Center point longitude'
    )
    parser.add_argument(
        '--radius',
        type=float,
        default=5.0,
        help='Search radius in miles (default: 5.0)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=80,
        help='Fuzzy match threshold 0-100 (default: 80)'
    )
    parser.add_argument(
        '--output',
        default='void_report.csv',
        help='Output CSV file path (default: void_report.csv)'
    )

    args = parser.parse_args()

    # Allow API key from environment variable
    api_key = args.api_key or os.environ.get('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("Error: Google Places API key required")
        return

    # Generate report
    generator = VoidReportGenerator(api_key, args.retailer_list)
    generator.generate_void_report(
        args.latitude,
        args.longitude,
        args.radius,
        args.threshold,
        args.output
    )


if __name__ == '__main__':
    main()
