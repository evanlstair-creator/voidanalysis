"""
Generate interactive HTML dashboard from void report data - BROKER EDITION
Built specifically for commercial real estate brokers doing tenant placement.
"""

import csv
import json
from datetime import datetime
from typing import List, Dict
import os
from collections import defaultdict


class BrokerHTMLReportGenerator:
    """Generate broker-focused interactive HTML reports from void analysis data."""

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
                        'business_status': row.get('business_status', 'UNKNOWN'),
                        'place_id': row.get('place_id', '')
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

    def get_category_stats(self):
        """Calculate category statistics for found vs missing."""
        found_categories = defaultdict(int)
        missing_categories = defaultdict(int)

        # Count found categories
        for retailer in self.retailers_found:
            if retailer['matched_retailer']:
                category = self.retailer_categories.get(retailer['matched_retailer'], 'Unknown')
                found_categories[category] += 1

        # Count missing categories
        for retailer_name in self.retailers_missing:
            category = self.retailer_categories.get(retailer_name, 'Unknown')
            missing_categories[category] += 1

        return dict(found_categories), dict(missing_categories)

    def generate_html(self, output_path: str):
        """Generate the broker-focused interactive HTML dashboard."""
        self.load_data()

        # Get category statistics
        found_categories, missing_categories = self.get_category_stats()

        # Get all unique categories
        all_categories = sorted(set(list(found_categories.keys()) + list(missing_categories.keys())))

        # Get matched and unmatched retailers
        matched_retailers = [r for r in self.retailers_found if r['matched_retailer']]
        unmatched_retailers = [r for r in self.retailers_found if not r['matched_retailer']]

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tenant Placement Void Analysis</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={self.google_api_key}&libraries=geometry,places"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
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
            background: linear-gradient(135deg, #2c5282 0%, #2d3748 100%);
            color: white;
            padding: 1.5rem 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 1.8rem;
            margin-bottom: 0.3rem;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 1rem;
        }}

        .header .tagline {{
            color: #90cdf4;
            font-weight: 600;
            margin-top: 0.3rem;
        }}

        .container {{
            max-width: 1600px;
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
            color: #2c5282;
            font-size: 1.2rem;
        }}

        .radius-filters {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }}

        .radius-btn {{
            padding: 0.6rem 1.2rem;
            border: 2px solid #2c5282;
            background: white;
            color: #2c5282;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.3s;
        }}

        .radius-btn:hover {{
            background: #2c5282;
            color: white;
            transform: translateY(-2px);
        }}

        .radius-btn.active {{
            background: #2c5282;
            color: white;
        }}

        .export-buttons {{
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }}

        .export-btn {{
            padding: 0.6rem 1.2rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95rem;
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
            height: 600px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #2c5282;
        }}

        .stat-card h3 {{
            color: #718096;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}

        .stat-card .value {{
            font-size: 2.2rem;
            font-weight: 700;
            color: #2c5282;
        }}

        .two-column-layout {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }}

        .section {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .section.full-width {{
            margin-bottom: 2rem;
        }}

        .section h2 {{
            color: #2d3748;
            margin-bottom: 1.5rem;
            font-size: 1.4rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .section h2 i {{
            color: #2c5282;
        }}

        .category-filter {{
            margin-bottom: 1.5rem;
        }}

        .category-filter label {{
            display: block;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }}

        .category-filter select {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            background: white;
            cursor: pointer;
            transition: border-color 0.3s;
        }}

        .category-filter select:focus {{
            outline: none;
            border-color: #2c5282;
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
            padding: 0.85rem;
            text-align: left;
            font-weight: 600;
            color: #4a5568;
            border-bottom: 2px solid #e2e8f0;
            font-size: 0.9rem;
        }}

        .retailer-table td {{
            padding: 0.85rem;
            border-bottom: 1px solid #e2e8f0;
            font-size: 0.9rem;
        }}

        .retailer-table tbody tr:hover {{
            background: #f7fafc;
            cursor: pointer;
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

        .status-badge.opportunity {{
            background: #fef5e7;
            color: #7c4a00;
        }}

        .distance-badge {{
            background: #e6fffa;
            color: #234e52;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .category-badge {{
            background: #ebf8ff;
            color: #2c5282;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 500;
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
            border-color: #2c5282;
        }}

        .filter-info {{
            background: #ebf8ff;
            border-left: 4px solid #4299e1;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            font-size: 0.95rem;
        }}

        .filter-info strong {{
            color: #2c5282;
        }}

        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 1rem;
        }}

        .insights-box {{
            background: #fef5e7;
            border-left: 4px solid #ed8936;
            padding: 1rem;
            border-radius: 4px;
            margin-top: 1rem;
        }}

        .insights-box h3 {{
            color: #7c4a00;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }}

        .insights-box ul {{
            margin-left: 1.5rem;
            color: #7c4a00;
        }}

        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.7);
        }}

        .modal-content {{
            background-color: white;
            margin: 5% auto;
            padding: 2rem;
            border-radius: 12px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}

        .close:hover {{
            color: black;
        }}

        .modal-header {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 1rem;
            margin-bottom: 1rem;
        }}

        .modal-header h2 {{
            color: #2c5282;
            margin: 0;
        }}

        .modal-section {{
            margin: 1.5rem 0;
        }}

        .modal-section h3 {{
            color: #2d3748;
            font-size: 1.1rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .modal-section p {{
            color: #4a5568;
            margin: 0.5rem 0;
            line-height: 1.6;
        }}

        .modal-section .label {{
            font-weight: 600;
            color: #2d3748;
            min-width: 120px;
            display: inline-block;
        }}

        @media print {{
            .controls, .export-buttons {{
                display: none;
            }}
        }}

        @media (max-width: 1200px) {{
            .two-column-layout {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 768px) {{
            .radius-filters {{
                flex-direction: column;
            }}

            .radius-btn {{
                width: 100%;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1><i class="fas fa-store"></i> Tenant Placement Void Analysis</h1>
            <p class="tagline">Commercial Real Estate • Site Selection • Tenant Mix Optimization</p>
            <p>Trade Area Analysis | Generated {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
    </div>

    <div class="container">
        <!-- Controls -->
        <div class="controls">
            <h2><i class="fas fa-sliders-h"></i> Distance Filter</h2>
            <div class="radius-filters">
                <button class="radius-btn" data-radius="1">1 Mile</button>
                <button class="radius-btn" data-radius="2">2 Miles</button>
                <button class="radius-btn" data-radius="3">3 Miles</button>
                <button class="radius-btn" data-radius="4">4 Miles</button>
                <button class="radius-btn active" data-radius="5">5 Miles</button>
            </div>

            <div class="export-buttons">
                <button class="export-btn csv" onclick="exportToCSV()">
                    <i class="fas fa-file-csv"></i> Export CSV
                </button>
                <button class="export-btn pdf" onclick="window.print()">
                    <i class="fas fa-file-pdf"></i> Print/PDF
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
                <p style="color: #718096; margin-top: 0.3rem; font-size: 0.9rem;">miles</p>
            </div>
            <div class="stat-card">
                <h3>Businesses Found</h3>
                <div class="value" id="statTotal">{len(self.retailers_found)}</div>
            </div>
            <div class="stat-card">
                <h3>Matched Retailers</h3>
                <div class="value" id="statMatched" style="color: #48bb78;">{len(matched_retailers)}</div>
            </div>
            <div class="stat-card">
                <h3>Tenant Opportunities</h3>
                <div class="value" id="statMissing" style="color: #ed8936;">{len(self.retailers_missing)}</div>
            </div>
        </div>

        <!-- Two Column Layout: Charts -->
        <div class="two-column-layout">
            <!-- Category Distribution -->
            <div class="section">
                <h2><i class="fas fa-chart-bar"></i> Missing Categories</h2>
                <div class="chart-container">
                    <canvas id="missingCategoriesChart"></canvas>
                </div>
                <div class="insights-box" id="categoryInsights">
                    <!-- Populated by JavaScript -->
                </div>
            </div>

            <!-- Found vs Missing Comparison -->
            <div class="section">
                <h2><i class="fas fa-balance-scale"></i> Category Mix Analysis</h2>
                <div class="chart-container">
                    <canvas id="comparisonChart"></canvas>
                </div>
                <div class="insights-box" id="mixInsights">
                    <!-- Populated by JavaScript -->
                </div>
            </div>
        </div>

        <!-- Retailers Found (Table) -->
        <div class="section full-width">
            <h2><i class="fas fa-map-marker-alt"></i> Current Tenants & Competition</h2>
            <div class="filter-info" id="foundFilterInfo">
                Showing all retailers within <strong>5 miles</strong>
            </div>
            <input type="text" id="searchFound" class="search-box" placeholder="Search current tenants...">
            <div style="overflow-x: auto;">
                <table class="retailer-table">
                    <thead>
                        <tr>
                            <th>Business Name</th>
                            <th>Chain Match</th>
                            <th>Distance</th>
                            <th>Address</th>
                            <th>Rating</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody id="foundRetailersTable">
                        <!-- Populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Missing Retailers (Table with Category Filter) -->
        <div class="section full-width">
            <h2><i class="fas fa-bullseye"></i> Tenant Opportunities (Voids)</h2>

            <div class="category-filter">
                <label for="categorySelect">
                    <i class="fas fa-filter"></i> Filter by Category
                </label>
                <select id="categorySelect">
                    <option value="all">All Categories</option>
                    <!-- Populated by JavaScript -->
                </select>
            </div>

            <div class="filter-info" id="missingFilterInfo">
                Showing <strong id="missingCount">{len(self.retailers_missing)}</strong> tenant opportunities
            </div>

            <input type="text" id="searchMissing" class="search-box" placeholder="Search tenant opportunities...">

            <div style="overflow-x: auto;">
                <table class="retailer-table">
                    <thead>
                        <tr>
                            <th>Retailer Name</th>
                            <th>Category</th>
                            <th>Opportunity</th>
                        </tr>
                    </thead>
                    <tbody id="missingRetailersTable">
                        <!-- Populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Modal for Retailer Details -->
    <div id="retailerModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modalBody">
                <!-- Populated by JavaScript -->
            </div>
        </div>
    </div>

    <script>
        // Data
        const retailersFound = {json.dumps(self.retailers_found)};
        const retailersMissing = {json.dumps(self.retailers_missing)};
        const retailerCategories = {json.dumps(self.retailer_categories)};
        const foundCategories = {json.dumps(found_categories)};
        const missingCategories = {json.dumps(missing_categories)};
        const centerLat = {self.center_lat or 0};
        const centerLon = {self.center_lon or 0};

        let map;
        let markers = [];
        let circles = [];
        let currentRadius = 5;
        let currentCategory = 'all';
        let missingCategoriesChart, comparisonChart;

        // Initialize charts
        function initCharts() {{
            // Missing Categories Chart
            const missingCtx = document.getElementById('missingCategoriesChart').getContext('2d');
            const missingData = Object.entries(missingCategories)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10);

            missingCategoriesChart = new Chart(missingCtx, {{
                type: 'bar',
                data: {{
                    labels: missingData.map(d => d[0]),
                    datasets: [{{
                        label: 'Missing Retailers',
                        data: missingData.map(d => d[1]),
                        backgroundColor: '#ed8936',
                        borderColor: '#dd6b20',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {{
                        legend: {{ display: false }},
                        title: {{
                            display: true,
                            text: 'Top 10 Missing Categories'
                        }}
                    }},
                    scales: {{
                        x: {{
                            beginAtZero: true,
                            ticks: {{ precision: 0 }}
                        }}
                    }}
                }}
            }});

            // Comparison Chart
            const comparisonCtx = document.getElementById('comparisonChart').getContext('2d');
            const allCategories = Array.from(new Set([
                ...Object.keys(foundCategories),
                ...Object.keys(missingCategories)
            ])).sort().slice(0, 10);

            comparisonChart = new Chart(comparisonCtx, {{
                type: 'bar',
                data: {{
                    labels: allCategories,
                    datasets: [
                        {{
                            label: 'Currently Present',
                            data: allCategories.map(cat => foundCategories[cat] || 0),
                            backgroundColor: '#48bb78',
                            borderColor: '#38a169',
                            borderWidth: 2
                        }},
                        {{
                            label: 'Missing (Opportunities)',
                            data: allCategories.map(cat => missingCategories[cat] || 0),
                            backgroundColor: '#ed8936',
                            borderColor: '#dd6b20',
                            borderWidth: 2
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'top'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{ precision: 0 }}
                        }}
                    }}
                }}
            }});

            // Generate insights
            updateInsights();
        }}

        function updateInsights() {{
            // Category insights
            const topMissing = Object.entries(missingCategories)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 3);

            document.getElementById('categoryInsights').innerHTML = `
                <h3><i class="fas fa-lightbulb"></i> Key Insights</h3>
                <ul>
                    ${{topMissing.map(([cat, count]) =>
                        `<li><strong>${{cat}}</strong>: ${{count}} potential tenants</li>`
                    ).join('')}}
                </ul>
            `;

            // Mix insights
            const underserved = Object.entries(missingCategories)
                .filter(([cat, missCount]) => {{
                    const foundCount = foundCategories[cat] || 0;
                    return missCount > foundCount * 2;
                }})
                .slice(0, 3);

            document.getElementById('mixInsights').innerHTML = `
                <h3><i class="fas fa-exclamation-triangle"></i> Underserved Categories</h3>
                <ul>
                    ${{underserved.length > 0 ?
                        underserved.map(([cat, count]) =>
                            `<li><strong>${{cat}}</strong>: High demand, low supply</li>`
                        ).join('')
                        : '<li>Market appears balanced across major categories</li>'
                    }}
                </ul>
            `;
        }}

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

            // Add shopping center marker
            new google.maps.Marker({{
                position: center,
                map: map,
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 12,
                    fillColor: '#ed8936',
                    fillOpacity: 1,
                    strokeColor: 'white',
                    strokeWeight: 3
                }},
                title: 'Shopping Center / Analysis Point',
                label: {{
                    text: 'SC',
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: 'bold'
                }}
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
                fillColor: '#2c5282',
                fillOpacity: 0.1,
                strokeColor: '#2c5282',
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
                            scale: isMatched ? 8 : 6,
                            fillColor: isMatched ? '#48bb78' : '#cbd5e0',
                            fillOpacity: isMatched ? 1 : 0.7,
                            strokeColor: 'white',
                            strokeWeight: 2
                        }},
                        title: retailer.name
                    }});

                    // Click to show details modal
                    marker.addListener('click', () => {{
                        showRetailerDetails(retailer);
                    }});

                    markers.push(marker);
                }}
            }});

            // Fit bounds to circle
            map.fitBounds(circle.getBounds());
        }}

        // Show retailer details modal
        function showRetailerDetails(retailer) {{
            const modal = document.getElementById('retailerModal');
            const modalBody = document.getElementById('modalBody');

            const category = retailer.matched_retailer ?
                retailerCategories[retailer.matched_retailer] || 'Unknown' :
                'Not in target list';

            modalBody.innerHTML = `
                <div class="modal-header">
                    <h2>${{retailer.name}}</h2>
                </div>

                ${{retailer.matched_retailer ? `
                <div class="modal-section">
                    <h3><i class="fas fa-check-circle" style="color: #48bb78;"></i> Chain Match</h3>
                    <p><span class="label">Matched To:</span> ${{retailer.matched_retailer}}</p>
                    <p><span class="label">Category:</span> <span class="category-badge">${{category}}</span></p>
                    <p><span class="label">Match Score:</span> ${{retailer.match_score.toFixed(1)}}%</p>
                </div>
                ` : ''}}

                <div class="modal-section">
                    <h3><i class="fas fa-map-marker-alt"></i> Location</h3>
                    <p><span class="label">Address:</span> ${{retailer.address}}</p>
                    <p><span class="label">Distance:</span> <span class="distance-badge">${{retailer.distance_miles.toFixed(2)}} mi</span></p>
                    <p><span class="label">Coordinates:</span> ${{retailer.latitude.toFixed(6)}}, ${{retailer.longitude.toFixed(6)}}</p>
                </div>

                <div class="modal-section">
                    <h3><i class="fas fa-star"></i> Google Data</h3>
                    <p><span class="label">Rating:</span> ${{retailer.rating ? retailer.rating + ' ⭐' : 'No rating'}}</p>
                    <p><span class="label">Reviews:</span> ${{retailer.user_ratings_total || 0}} reviews</p>
                    <p><span class="label">Status:</span> ${{retailer.business_status}}</p>
                    <p><span class="label">Place ID:</span> <code style="font-size: 0.85rem; background: #f7fafc; padding: 0.25rem 0.5rem; border-radius: 4px;">${{retailer.place_id}}</code></p>
                </div>

                <div class="modal-section">
                    <h3><i class="fas fa-tags"></i> Google Types</h3>
                    <p>${{retailer.types.split(', ').map(type =>
                        `<span class="category-badge" style="margin: 0.25rem;">${{type}}</span>`
                    ).join('')}}</p>
                </div>

                <div class="modal-section">
                    <p style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; color: #718096; font-size: 0.9rem;">
                        <i class="fas fa-info-circle"></i> <strong>Broker Note:</strong>
                        ${{retailer.matched_retailer ?
                            `This location may impact tenant interest for ${{retailer.matched_retailer}} (${{retailer.distance_miles.toFixed(2)}} miles away).` :
                            'This business is not in your target retailer list.'
                        }}
                    </p>
                </div>
            `;

            modal.style.display = 'block';
        }}

        // Close modal
        document.querySelector('.close').onclick = function() {{
            document.getElementById('retailerModal').style.display = 'none';
        }}

        window.onclick = function(event) {{
            const modal = document.getElementById('retailerModal');
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }}

        // Update tables
        function updateTables(radiusMiles) {{
            currentRadius = radiusMiles;

            // Filter found retailers
            const foundFiltered = retailersFound.filter(r => r.distance_miles <= radiusMiles);

            // Update found retailers table
            const foundTable = document.getElementById('foundRetailersTable');
            foundTable.innerHTML = foundFiltered.map(r => `
                <tr onclick="showRetailerDetails(${{JSON.stringify(r).replace(/"/g, '&quot;')}})">
                    <td><strong>${{r.name}}</strong></td>
                    <td>${{r.matched_retailer || '<span style="color: #a0aec0;">Not matched</span>'}}</td>
                    <td><span class="distance-badge">${{r.distance_miles.toFixed(2)}} mi</span></td>
                    <td>${{r.address}}</td>
                    <td>${{r.rating ? r.rating + ' ⭐' : '-'}}</td>
                    <td><button style="padding: 0.25rem 0.75rem; border: 1px solid #2c5282; background: white; color: #2c5282; border-radius: 4px; cursor: pointer; font-size: 0.85rem;">View</button></td>
                </tr>
            `).join('');

            // Update stats
            const matchedCount = foundFiltered.filter(r => r.matched_retailer).length;
            document.getElementById('statRadius').textContent = radiusMiles;
            document.getElementById('statTotal').textContent = foundFiltered.length;
            document.getElementById('statMatched').textContent = matchedCount;

            // Update filter info
            document.getElementById('foundFilterInfo').innerHTML =
                `Showing <strong>${{foundFiltered.length}}</strong> businesses within <strong>${{radiusMiles}} mile${{radiusMiles > 1 ? 's' : ''}}</strong>`;

            // Update missing retailers
            filterMissingRetailers();
        }}

        // Populate and filter missing retailers
        function filterMissingRetailers() {{
            const missingTable = document.getElementById('missingRetailersTable');
            const searchTerm = document.getElementById('searchMissing').value.toLowerCase();

            let filtered = retailersMissing.filter(name => {{
                const category = retailerCategories[name] || 'Unknown';
                const matchesCategory = currentCategory === 'all' || category === currentCategory;
                const matchesSearch = name.toLowerCase().includes(searchTerm) ||
                                    category.toLowerCase().includes(searchTerm);
                return matchesCategory && matchesSearch;
            }});

            missingTable.innerHTML = filtered.map(name => {{
                const category = retailerCategories[name] || 'Unknown';
                return `
                    <tr>
                        <td><strong>${{name}}</strong></td>
                        <td><span class="category-badge">${{category}}</span></td>
                        <td><span class="status-badge opportunity"><i class="fas fa-bullseye"></i> Tenant Opportunity</span></td>
                    </tr>
                `;
            }}).join('');

            // Update count
            document.getElementById('missingCount').textContent = filtered.length;
            document.getElementById('missingFilterInfo').innerHTML =
                `Showing <strong>${{filtered.length}}</strong> tenant opportunities${{currentCategory !== 'all' ? ` in <strong>${{currentCategory}}</strong>` : ''}}`;
        }}

        // Populate category dropdown
        function populateCategoryDropdown() {{
            const select = document.getElementById('categorySelect');
            const categories = Object.keys(missingCategories).sort();

            categories.forEach(category => {{
                const option = document.createElement('option');
                option.value = category;
                option.textContent = `${{category}} (${{missingCategories[category]}})`;
                select.appendChild(option);
            }});

            select.addEventListener('change', (e) => {{
                currentCategory = e.target.value;
                filterMissingRetailers();
            }});
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

        document.getElementById('searchMissing').addEventListener('input', () => {{
            filterMissingRetailers();
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

            let csv = 'CURRENT TENANTS\\n';
            csv += 'Business Name,Chain Match,Distance (miles),Address,Rating,Reviews,Status\\n';

            filtered.forEach(r => {{
                csv += `"${{r.name}}","${{r.matched_retailer}}","${{r.distance_miles.toFixed(2)}}","${{r.address}}","${{r.rating || 'N/A'}}","${{r.user_ratings_total}}","${{r.business_status}}"\\n`;
            }});

            csv += '\\n\\nTENANT OPPORTUNITIES\\n';
            csv += 'Retailer Name,Category\\n';

            const filteredMissing = currentCategory === 'all' ?
                retailersMissing :
                retailersMissing.filter(name => retailerCategories[name] === currentCategory);

            filteredMissing.forEach(name => {{
                const category = retailerCategories[name] || 'Unknown';
                csv += `"${{name}}","${{category}}"\\n`;
            }});

            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tenant_placement_analysis_${{currentRadius}}mi_${{new Date().toISOString().split('T')[0]}}.csv`;
            a.click();
        }}

        // Initialize
        google.maps.event.addDomListener(window, 'load', () => {{
            initMap();
            updateTables(5);
            populateCategoryDropdown();
            filterMissingRetailers();
            initCharts();
        }});
    </script>
</body>
</html>"""

        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Broker-focused HTML dashboard generated: {output_path}")


def main():
    """Main function to generate HTML report from latest CSV."""
    import glob
    import argparse

    parser = argparse.ArgumentParser(description='Generate broker-focused HTML dashboard')
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
        base_name = os.path.basename(args.csv).replace('.csv', '_broker.html')
        args.output = f'outputs/{base_name}'

    generator = BrokerHTMLReportGenerator(args.csv, args.api_key)
    generator.generate_html(args.output)

    print(f"\n✓ Broker-focused dashboard created: {args.output}")
    print(f"\nFeatures:")
    print("  ✓ Category filter dropdown")
    print("  ✓ Missing categories bar chart")
    print("  ✓ Category mix comparison chart")
    print("  ✓ Detailed retailer modals with all Google data")
    print("  ✓ Broker-focused insights")
    print(f"\nTo view: open {args.output}")


if __name__ == '__main__':
    main()
