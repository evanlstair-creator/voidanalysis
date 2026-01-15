"""
Generate interactive HTML dashboard from void report data.
Creates a beautiful, professional report for real estate audiences.
"""

import csv
import json
from datetime import datetime
from typing import List, Dict
import os


class HTMLReportGenerator:
    """Generate interactive HTML reports from void analysis data."""

    def __init__(self, csv_report_path: str, google_api_key: str, retailer_list_path: str = "list of retailers_cleaned.csv"):
        """
        Initialize the HTML report generator.

        Args:
            csv_report_path: Path to the void report CSV
            google_api_key: Google Maps API key
            retailer_list_path: Path to master retailer list with categories
        """
        self.csv_report_path = csv_report_path
        self.google_api_key = google_api_key
        self.retailer_list_path = retailer_list_path
        self.retailers_found = []
        self.retailers_missing = []
        self.retailer_categories = {}
        self.center_lat = None
        self.center_lon = None
        self.max_radius = 5.0

    def load_data(self):
        """Load data from CSV files."""
        # Load retailer categories
        if os.path.exists(self.retailer_list_path):
            with open(self.retailer_list_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.retailer_categories[row['ChainName']] = row['PrimaryCategory']

        # Load found retailers
        with open(self.csv_report_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['name']:
                    self.retailers_found.append({
                        'name': row['name'],
                        'matched_retailer': row.get('matched_retailer', ''),
                        'match_score': float(row.get('match_score', 0)) if row.get('match_score') else 0,
                        'distance_miles': float(row['distance_miles']) if row.get('distance_miles') else 0,
                        'address': row.get('address', ''),
                        'latitude': float(row['latitude']) if row.get('latitude') else 0,
                        'longitude': float(row['longitude']) if row.get('longitude') else 0,
                        'types': row.get('types', ''),
                        'rating': float(row.get('rating', 0)) if row.get('rating') else None,
                        'user_ratings_total': int(row.get('user_ratings_total', 0)) if row.get('user_ratings_total') else 0,
                    })

        # Get center coordinates from first retailer
        if self.retailers_found:
            # Calculate center as average of all found retailers
            lats = [r['latitude'] for r in self.retailers_found if r['latitude']]
            lons = [r['longitude'] for r in self.retailers_found if r['longitude']]
            if lats and lons:
                self.center_lat = sum(lats) / len(lats)
                self.center_lon = sum(lons) / len(lons)

        # Load missing retailers
        missing_path = self.csv_report_path.replace('.csv', '_missing_retailers.csv')
        if os.path.exists(missing_path):
            with open(missing_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('missing_retailer'):
                        self.retailers_missing.append(row['missing_retailer'])

    def generate_html(self, output_path: str):
        """Generate the interactive HTML dashboard."""
        self.load_data()

        # Get matched and unmatched retailers
        matched_retailers = [r for r in self.retailers_found if r['matched_retailer']]
        unmatched_retailers = [r for r in self.retailers_found if not r['matched_retailer']]

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retail Void Analysis Report</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={self.google_api_key}&libraries=geometry"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            color: #2d3748;
            line-height: 1.6;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .controls {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}

        .controls h2 {{
            margin-bottom: 1rem;
            color: #667eea;
            font-size: 1.3rem;
        }}

        .radius-filters {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }}

        .radius-btn {{
            padding: 0.75rem 1.5rem;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s;
        }}

        .radius-btn:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}

        .radius-btn.active {{
            background: #667eea;
            color: white;
        }}

        .export-buttons {{
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }}

        .export-btn {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .export-btn.csv {{
            background: #48bb78;
            color: white;
        }}

        .export-btn.pdf {{
            background: #ed8936;
            color: white;
        }}

        .export-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}

        .map-container {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}

        #map {{
            width: 100%;
            height: 500px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}

        .stat-card h3 {{
            color: #718096;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}

        .stat-card .value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
        }}

        .section {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}

        .section h2 {{
            color: #2d3748;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .section h2 i {{
            color: #667eea;
        }}

        .retailer-table {{
            width: 100%;
            border-collapse: collapse;
            overflow: hidden;
        }}

        .retailer-table thead {{
            background: #f7fafc;
        }}

        .retailer-table th {{
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
        }}

        .retailer-table td {{
            padding: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }}

        .retailer-table tbody tr:hover {{
            background: #f7fafc;
        }}

        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .status-badge.found {{
            background: #c6f6d5;
            color: #22543d;
        }}

        .status-badge.missing {{
            background: #fed7d7;
            color: #742a2a;
        }}

        .distance-badge {{
            background: #e6fffa;
            color: #234e52;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .match-score {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .match-score.high {{
            background: #c6f6d5;
            color: #22543d;
        }}

        .match-score.medium {{
            background: #fef5e7;
            color: #7c4a00;
        }}

        .search-box {{
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            margin-bottom: 1rem;
            transition: border-color 0.3s;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .filter-info {{
            background: #ebf8ff;
            border-left: 4px solid #4299e1;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
        }}

        .filter-info strong {{
            color: #2c5282;
        }}

        @media print {{
            .controls, .export-buttons {{
                display: none;
            }}
        }}

        @media (max-width: 768px) {{
            .radius-filters {{
                flex-direction: column;
            }}

            .radius-btn {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1><i class="fas fa-map-marked-alt"></i> Retail Void Analysis Report</h1>
            <p>Trade Area Analysis | Generated {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
    </div>

    <div class="container">
        <!-- Controls -->
        <div class="controls">
            <h2><i class="fas fa-sliders-h"></i> Distance Filter</h2>
            <div class="radius-filters">
                <button class="radius-btn" data-radius="1">1 Mile Radius</button>
                <button class="radius-btn" data-radius="2">2 Mile Radius</button>
                <button class="radius-btn" data-radius="3">3 Mile Radius</button>
                <button class="radius-btn" data-radius="4">4 Mile Radius</button>
                <button class="radius-btn active" data-radius="5">5 Mile Radius</button>
            </div>

            <div class="export-buttons">
                <button class="export-btn csv" onclick="exportToCSV()">
                    <i class="fas fa-file-csv"></i> Export CSV
                </button>
                <button class="export-btn pdf" onclick="exportToPDF()">
                    <i class="fas fa-file-pdf"></i> Export PDF
                </button>
            </div>
        </div>

        <!-- Map -->
        <div class="map-container">
            <div id="map"></div>
        </div>

        <!-- Statistics -->
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <h3>Search Radius</h3>
                <div class="value" id="statRadius">{self.max_radius}</div>
                <p style="color: #718096; margin-top: 0.5rem;">miles</p>
            </div>
            <div class="stat-card">
                <h3>Total Places Found</h3>
                <div class="value" id="statTotal">{len(self.retailers_found)}</div>
            </div>
            <div class="stat-card">
                <h3>Matched Retailers</h3>
                <div class="value" id="statMatched" style="color: #48bb78;">{len(matched_retailers)}</div>
            </div>
            <div class="stat-card">
                <h3>Missing Retailers</h3>
                <div class="value" id="statMissing" style="color: #f56565;">{len(self.retailers_missing)}</div>
            </div>
        </div>

        <!-- Retailers Found -->
        <div class="section" id="retailersFoundSection">
            <h2><i class="fas fa-check-circle"></i> Retailers Present in Trade Area</h2>
            <div class="filter-info" id="foundFilterInfo">
                Showing all retailers within <strong>5 miles</strong>
            </div>
            <input type="text" id="searchFound" class="search-box" placeholder="Search retailers...">
            <div style="overflow-x: auto;">
                <table class="retailer-table">
                    <thead>
                        <tr>
                            <th>Retailer Name</th>
                            <th>Matched To</th>
                            <th>Match Score</th>
                            <th>Distance</th>
                            <th>Address</th>
                            <th>Rating</th>
                        </tr>
                    </thead>
                    <tbody id="foundRetailersTable">
                        <!-- Populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Missing Retailers -->
        <div class="section" id="missingRetailersSection">
            <h2><i class="fas fa-times-circle"></i> Missing Retailers (Voids)</h2>
            <div class="filter-info" id="missingFilterInfo">
                Showing retailers NOT found within <strong>5 miles</strong>
            </div>
            <input type="text" id="searchMissing" class="search-box" placeholder="Search missing retailers...">
            <div style="overflow-x: auto;">
                <table class="retailer-table">
                    <thead>
                        <tr>
                            <th>Retailer Name</th>
                            <th>Category</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="missingRetailersTable">
                        <!-- Populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Data
        const retailersFound = {json.dumps(self.retailers_found)};
        const retailersMissing = {json.dumps(self.retailers_missing)};
        const retailerCategories = {json.dumps(self.retailer_categories)};
        const centerLat = {self.center_lat or 0};
        const centerLon = {self.center_lon or 0};

        let map;
        let markers = [];
        let circles = [];
        let currentRadius = 5;

        // Initialize map
        function initMap() {{
            const center = {{ lat: centerLat, lng: centerLon }};

            map = new google.maps.Map(document.getElementById('map'), {{
                center: center,
                zoom: 12,
                styles: [
                    {{
                        featureType: "poi",
                        elementType: "labels",
                        stylers: [{{ visibility: "off" }}]
                    }}
                ]
            }});

            // Add center marker
            new google.maps.Marker({{
                position: center,
                map: map,
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 10,
                    fillColor: '#667eea',
                    fillOpacity: 1,
                    strokeColor: 'white',
                    strokeWeight: 3
                }},
                title: 'Search Center'
            }});

            updateMap(5);
        }}

        // Update map with current radius
        function updateMap(radiusMiles) {{
            // Clear existing circles and markers
            circles.forEach(c => c.setMap(null));
            markers.forEach(m => m.setMap(null));
            circles = [];
            markers = [];

            const center = {{ lat: centerLat, lng: centerLon }};
            const radiusMeters = radiusMiles * 1609.34;

            // Add radius circle
            const circle = new google.maps.Circle({{
                map: map,
                center: center,
                radius: radiusMeters,
                fillColor: '#667eea',
                fillOpacity: 0.1,
                strokeColor: '#667eea',
                strokeOpacity: 0.8,
                strokeWeight: 2
            }});
            circles.push(circle);

            // Filter retailers by distance
            const filtered = retailersFound.filter(r => r.distance_miles <= radiusMiles);

            // Add markers for retailers
            filtered.forEach(retailer => {{
                if (retailer.latitude && retailer.longitude) {{
                    const isMatched = retailer.matched_retailer !== '';

                    const marker = new google.maps.Marker({{
                        position: {{ lat: retailer.latitude, lng: retailer.longitude }},
                        map: map,
                        icon: {{
                            path: google.maps.SymbolPath.CIRCLE,
                            scale: 7,
                            fillColor: isMatched ? '#48bb78' : '#cbd5e0',
                            fillOpacity: 1,
                            strokeColor: 'white',
                            strokeWeight: 2
                        }},
                        title: retailer.name
                    }});

                    const infoWindow = new google.maps.InfoWindow({{
                        content: `
                            <div style="padding: 0.5rem;">
                                <h3 style="margin: 0 0 0.5rem 0; color: #2d3748;">${{retailer.name}}</h3>
                                ${{retailer.matched_retailer ? `<p style="margin: 0.25rem 0;"><strong>Matched:</strong> ${{retailer.matched_retailer}}</p>` : ''}}
                                <p style="margin: 0.25rem 0;"><strong>Distance:</strong> ${{retailer.distance_miles.toFixed(2)}} mi</p>
                                <p style="margin: 0.25rem 0;"><strong>Address:</strong> ${{retailer.address}}</p>
                                ${{retailer.rating ? `<p style="margin: 0.25rem 0;"><strong>Rating:</strong> ${{retailer.rating}} ⭐</p>` : ''}}
                            </div>
                        `
                    }});

                    marker.addListener('click', () => {{
                        infoWindow.open(map, marker);
                    }});

                    markers.push(marker);
                }}
            }});

            // Fit bounds to circle
            map.fitBounds(circle.getBounds());
        }}

        // Update tables
        function updateTables(radiusMiles) {{
            currentRadius = radiusMiles;

            // Filter found retailers
            const foundFiltered = retailersFound.filter(r => r.distance_miles <= radiusMiles);

            // Update found retailers table
            const foundTable = document.getElementById('foundRetailersTable');
            foundTable.innerHTML = foundFiltered.map(r => `
                <tr>
                    <td><strong>${{r.name}}</strong></td>
                    <td>${{r.matched_retailer || '<span style="color: #a0aec0;">Not matched</span>'}}</td>
                    <td>
                        ${{r.match_score > 0 ?
                            `<span class="match-score ${{r.match_score >= 90 ? 'high' : 'medium'}}">${{r.match_score.toFixed(0)}}%</span>`
                            : '-'
                        }}
                    </td>
                    <td><span class="distance-badge">${{r.distance_miles.toFixed(2)}} mi</span></td>
                    <td>${{r.address}}</td>
                    <td>${{r.rating ? r.rating + ' ⭐' : '-'}}</td>
                </tr>
            `).join('');

            // Update stats
            const matchedCount = foundFiltered.filter(r => r.matched_retailer).length;
            document.getElementById('statRadius').textContent = radiusMiles;
            document.getElementById('statTotal').textContent = foundFiltered.length;
            document.getElementById('statMatched').textContent = matchedCount;

            // Update filter info
            document.getElementById('foundFilterInfo').innerHTML =
                `Showing <strong>${{foundFiltered.length}}</strong> retailers within <strong>${{radiusMiles}} mile${{radiusMiles > 1 ? 's' : ''}}</strong>`;
            document.getElementById('missingFilterInfo').innerHTML =
                `Showing <strong>${{retailersMissing.length}}</strong> retailers NOT found within <strong>${{radiusMiles}} mile${{radiusMiles > 1 ? 's' : ''}}</strong>`;
        }}

        // Populate missing retailers table
        function populateMissingTable() {{
            const missingTable = document.getElementById('missingRetailersTable');
            missingTable.innerHTML = retailersMissing.map(name => {{
                const category = retailerCategories[name] || 'Unknown';
                return `
                    <tr>
                        <td><strong>${{name}}</strong></td>
                        <td><span style="color: #718096;">${{category}}</span></td>
                        <td><span class="status-badge missing"><i class="fas fa-times-circle"></i> Not Found</span></td>
                    </tr>
                `;
            }}).join('');
        }}

        // Search functionality
        document.getElementById('searchFound').addEventListener('input', (e) => {{
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#foundRetailersTable tr');

            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            }});
        }});

        document.getElementById('searchMissing').addEventListener('input', (e) => {{
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#missingRetailersTable tr');

            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            }});
        }});

        // Radius filter buttons
        document.querySelectorAll('.radius-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const radius = parseFloat(btn.dataset.radius);

                // Update active state
                document.querySelectorAll('.radius-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Update map and tables
                updateMap(radius);
                updateTables(radius);
            }});
        }});

        // Export to CSV
        function exportToCSV() {{
            const filtered = retailersFound.filter(r => r.distance_miles <= currentRadius);

            let csv = 'Retailer Name,Matched To,Match Score,Distance (miles),Address,Rating\\n';

            filtered.forEach(r => {{
                csv += `"${{r.name}}","${{r.matched_retailer}}","${{r.match_score.toFixed(1)}}","${{r.distance_miles.toFixed(2)}}","${{r.address}}","${{r.rating || 'N/A'}}"\\n`;
            }});

            csv += '\\n\\nMissing Retailers\\n';
            csv += 'Retailer Name,Category,Status\\n';
            retailersMissing.forEach(name => {{
                const category = retailerCategories[name] || 'Unknown';
                csv += `"${{name}}","${{category}}","Not Found"\\n`;
            }});

            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `retail_void_analysis_${{currentRadius}}mi_${{new Date().toISOString().split('T')[0]}}.csv`;
            a.click();
        }}

        // Export to PDF
        function exportToPDF() {{
            window.print();
        }}

        // Initialize
        google.maps.event.addDomListener(window, 'load', () => {{
            initMap();
            updateTables(5);
            populateMissingTable();
        }});
    </script>
</body>
</html>"""

        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML report generated: {output_path}")


def main():
    """Main function to generate HTML report from latest CSV."""
    import glob
    import argparse

    parser = argparse.ArgumentParser(description='Generate HTML dashboard from void report')
    parser.add_argument('--csv', help='Path to void report CSV')
    parser.add_argument('--api-key', default='AIzaSyA85pSu9Naza2sf1YTjq82D3v7UFtt8I80', help='Google Maps API key')
    parser.add_argument('--output', help='Output HTML file path')

    args = parser.parse_args()

    # Find latest CSV if not specified
    if not args.csv:
        csv_files = glob.glob('outputs/void_report_*.csv')
        csv_files = [f for f in csv_files if 'missing' not in f]
        if not csv_files:
            print("No void report CSV files found in outputs/")
            return
        args.csv = sorted(csv_files)[-1]
        print(f"Using latest report: {args.csv}")

    if not args.output:
        base_name = os.path.basename(args.csv).replace('.csv', '.html')
        args.output = f'outputs/{base_name}'

    generator = HTMLReportGenerator(args.csv, args.api_key)
    generator.generate_html(args.output)

    print(f"\n✓ HTML dashboard created: {args.output}")
    print(f"\nTo view: Open {args.output} in your browser")
    print(f"To deploy to Netlify: Upload {args.output} and any assets")


if __name__ == '__main__':
    main()
