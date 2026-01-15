"""
Generate interactive HTML dashboard with coordinate input and live search
Connects to backend API for real-time void analysis
"""

import csv
import json
from datetime import datetime
from typing import List, Dict
import os


def generate_interactive_dashboard(google_api_key: str, output_path: str = "interactive_dashboard.html"):
    """
    Generate standalone interactive dashboard with coordinate input.

    Args:
        google_api_key: Google Maps API key
        output_path: Where to save the HTML file
    """

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retail Void Analysis - Interactive Dashboard</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={google_api_key}&libraries=places"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }}

        /* Search Form Section */
        .search-section {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        .search-section h2 {{
            margin-bottom: 20px;
            color: #2c3e50;
            font-size: 1.5rem;
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        .form-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #34495e;
        }}

        .form-group input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e6ed;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }}

        .form-group input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .form-row {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }}

        .paste-hint {{
            font-size: 0.85rem;
            color: #7f8c8d;
            margin-top: 5px;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}

        .btn-primary:disabled {{
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }}

        /* Loading Spinner */
        .spinner {{
            display: none;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        .status-message {{
            margin-top: 15px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }}

        .status-message.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}

        .status-message.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}

        .status-message.info {{
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }}

        /* Results Section */
        #results {{
            display: none;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .stat-card h3 {{
            color: #7f8c8d;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}

        .stat-card .value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }}

        #map {{
            width: 100%;
            height: 600px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .table-section {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}

        .table-section h2 {{
            margin-bottom: 20px;
            color: #2c3e50;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #2c3e50;
            border-bottom: 2px solid #e0e6ed;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e0e6ed;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}

        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Retail Void Analysis Dashboard</h1>
        <p>Interactive tool for commercial real estate tenant placement</p>
    </div>

    <div class="container">
        <!-- Search Form -->
        <div class="search-section">
            <h2>📍 Run Void Analysis</h2>
            <form id="searchForm">
                <div class="form-group">
                    <label for="coordinates">Coordinates (paste from Google Maps)</label>
                    <input type="text" id="coordinates" name="coordinates" placeholder="33.4233994297814, -96.58878795317332">
                    <div class="paste-hint">💡 Paste coordinates with comma: "lat, lng" or enter separately below</div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="latitude">Latitude</label>
                        <input type="text" id="latitude" name="latitude" placeholder="33.423248658058945" required>
                    </div>
                    <div class="form-group">
                        <label for="longitude">Longitude</label>
                        <input type="text" id="longitude" name="longitude" placeholder="-96.5887672571626" required>
                    </div>
                    <div class="form-group">
                        <label for="radius">Radius (miles)</label>
                        <input type="number" id="radius" name="radius" value="5" min="1" max="10" step="0.5" required>
                    </div>
                </div>
                <button type="submit" class="btn-primary" id="searchBtn">
                    🚀 Run Analysis
                </button>
                <div class="spinner" id="spinner"></div>
                <div class="status-message" id="statusMessage"></div>
            </form>
        </div>

        <!-- Results Section -->
        <div id="results">
            <!-- Stats Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Places Found</h3>
                    <div class="value" id="statTotal">0</div>
                </div>
                <div class="stat-card">
                    <h3>Matched Chains</h3>
                    <div class="value" id="statMatched">0</div>
                </div>
                <div class="stat-card">
                    <h3>Tenant Opportunities</h3>
                    <div class="value" id="statMissing">0</div>
                </div>
                <div class="stat-card">
                    <h3>Coverage</h3>
                    <div class="value" id="statCoverage">0%</div>
                </div>
            </div>

            <!-- Map -->
            <div id="map"></div>

            <!-- Retailers Found Table -->
            <div class="table-section">
                <h2>✅ Retailers Found</h2>
                <div style="overflow-x: auto;">
                    <table id="foundTable">
                        <thead>
                            <tr>
                                <th>Business Name</th>
                                <th>Matched Chain</th>
                                <th>Distance</th>
                                <th>Address</th>
                                <th>Rating</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="foundTableBody">
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Google Category Mix Analysis -->
            <div class="table-section">
                <h2>📊 Category Mix Analysis (Google Types)</h2>
                <p style="margin-bottom: 20px; color: #7f8c8d;">
                    Based on Google's classification of businesses in this area. Shows what types of retailers are most common.
                </p>
                <div style="overflow-x: auto;">
                    <table id="categoryTable">
                        <thead>
                            <tr>
                                <th>Google Category</th>
                                <th>Count</th>
                                <th>Percentage</th>
                            </tr>
                        </thead>
                        <tbody id="categoryTableBody">
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Tenant Opportunities Table -->
            <div class="table-section">
                <h2>💰 Tenant Opportunities (Top 100)</h2>
                <div style="overflow-x: auto;">
                    <table id="missingTable">
                        <thead>
                            <tr>
                                <th>Chain Name</th>
                                <th>Category</th>
                            </tr>
                        </thead>
                        <tbody id="missingTableBody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let map;
        let markers = [];
        let API_BASE_URL = null;

        // Auto-discover backend API port on page load
        async function discoverBackendPort() {{
            const portsToTry = [5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009];

            for (const port of portsToTry) {{
                try {{
                    const response = await fetch(`http://localhost:${{port}}/api/health`, {{
                        method: 'GET',
                        signal: AbortSignal.timeout(1000) // 1 second timeout
                    }});

                    if (response.ok) {{
                        const data = await response.json();
                        if (data.status === 'healthy') {{
                            API_BASE_URL = `http://localhost:${{port}}`;
                            console.log(`✅ Found backend server on port ${{port}}`);
                            showStatus(`Connected to backend on port ${{port}}`, 'success');
                            return port;
                        }}
                    }}
                }} catch (error) {{
                    // Port not available or server not responding, continue
                    continue;
                }}
            }}

            showStatus('⚠️ Backend server not found. Please start: python api_server.py', 'error');
            console.error('Could not find backend server on any port');
            return null;
        }}

        // Initialize on page load
        window.addEventListener('DOMContentLoaded', async () => {{
            await discoverBackendPort();

            // Add coordinate paste handler
            document.getElementById('coordinates').addEventListener('input', (e) => {{
                const value = e.target.value.trim();
                if (value.includes(',')) {{
                    const parts = value.split(',').map(p => p.trim());
                    if (parts.length === 2) {{
                        const lat = parseFloat(parts[0]);
                        const lng = parseFloat(parts[1]);
                        if (!isNaN(lat) && !isNaN(lng)) {{
                            document.getElementById('latitude').value = lat;
                            document.getElementById('longitude').value = lng;
                            console.log(`Auto-filled: ${{lat}}, ${{lng}}`);
                        }}
                    }}
                }}
            }});
        }});

        // Initialize map
        function initMap(lat, lng, zoom = 12) {{
            map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: lat, lng: lng }},
                zoom: zoom
            }});

            // Add center marker
            new google.maps.Marker({{
                position: {{ lat: lat, lng: lng }},
                map: map,
                icon: {{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 10,
                    fillColor: '#667eea',
                    fillOpacity: 1,
                    strokeColor: 'white',
                    strokeWeight: 2
                }},
                title: 'Search Center'
            }});
        }}

        // Show status message
        function showStatus(message, type) {{
            const statusEl = document.getElementById('statusMessage');
            statusEl.textContent = message;
            statusEl.className = `status-message ${{type}}`;
            statusEl.style.display = 'block';
        }}

        // Hide status message
        function hideStatus() {{
            document.getElementById('statusMessage').style.display = 'none';
        }}

        // Handle form submission
        document.getElementById('searchForm').addEventListener('submit', async (e) => {{
            e.preventDefault();

            // Check if backend is available
            if (!API_BASE_URL) {{
                showStatus('Backend server not connected. Please start: python api_server.py', 'error');
                return;
            }}

            const latitude = parseFloat(document.getElementById('latitude').value);
            const longitude = parseFloat(document.getElementById('longitude').value);
            const radius = parseFloat(document.getElementById('radius').value);

            // Validate inputs
            if (isNaN(latitude) || isNaN(longitude) || isNaN(radius)) {{
                showStatus('Please enter valid coordinates and radius', 'error');
                return;
            }}

            // Show loading state
            document.getElementById('searchBtn').disabled = true;
            document.getElementById('spinner').style.display = 'block';
            hideStatus();

            try {{
                // Call backend API using discovered URL
                const response = await fetch(`${{API_BASE_URL}}/api/analyze`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        latitude: latitude,
                        longitude: longitude,
                        radius: radius
                    }})
                }});

                if (!response.ok) {{
                    throw new Error(`API error: ${{response.statusText}}`);
                }}

                const data = await response.json();

                // Update UI with results
                displayResults(data, latitude, longitude);

                showStatus('Analysis complete! Scroll down to see results.', 'success');

            }} catch (error) {{
                console.error('Error:', error);
                showStatus(`Error: ${{error.message}}. Make sure the backend server is running.`, 'error');
            }} finally {{
                document.getElementById('searchBtn').disabled = false;
                document.getElementById('spinner').style.display = 'none';
            }}
        }});

        // Display results
        function displayResults(data, centerLat, centerLng) {{
            // Show results section
            document.getElementById('results').style.display = 'block';

            // Update stats
            document.getElementById('statTotal').textContent = data.stats.total_places;
            document.getElementById('statMatched').textContent = data.stats.matched_places;
            document.getElementById('statMissing').textContent = data.stats.missing_retailers;
            document.getElementById('statCoverage').textContent = data.stats.coverage_percentage + '%';

            // Initialize map
            initMap(centerLat, centerLng);

            // Clear previous markers
            markers.forEach(marker => marker.setMap(null));
            markers = [];

            // Add markers for found retailers
            data.retailers_found.forEach(retailer => {{
                const marker = new google.maps.Marker({{
                    position: {{ lat: retailer.latitude, lng: retailer.longitude }},
                    map: map,
                    title: retailer.name,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 6,
                        fillColor: retailer.matched_retailer ? '#28a745' : '#6c757d',
                        fillOpacity: 1,
                        strokeColor: 'white',
                        strokeWeight: 1
                    }}
                }});

                const infoWindow = new google.maps.InfoWindow({{
                    content: `
                        <div style="padding: 10px;">
                            <h3 style="margin: 0 0 10px 0;">${{retailer.name}}</h3>
                            ${{retailer.matched_retailer ? `<p><strong>Matched:</strong> ${{retailer.matched_retailer}} (${{retailer.match_score}}%)</p>` : ''}}
                            <p><strong>Distance:</strong> ${{retailer.distance_miles}} mi</p>
                            <p>${{retailer.address}}</p>
                            ${{retailer.rating ? `<p><strong>Rating:</strong> ${{retailer.rating}} ⭐ (${{retailer.user_ratings_total}} reviews)</p>` : ''}}
                        </div>
                    `
                }});

                marker.addListener('click', () => {{
                    infoWindow.open(map, marker);
                }});

                markers.push(marker);
            }});

            // Populate found retailers table
            const foundTableBody = document.getElementById('foundTableBody');
            foundTableBody.innerHTML = '';
            data.retailers_found.forEach(retailer => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{retailer.name}}</td>
                    <td>${{retailer.matched_retailer ? `<span class="badge badge-success">${{retailer.matched_retailer}}</span>` : '-'}}</td>
                    <td>${{retailer.distance_miles}} mi</td>
                    <td>${{retailer.address}}</td>
                    <td>${{retailer.rating ? `${{retailer.rating}} ⭐ (${{retailer.user_ratings_total}})` : '-'}}</td>
                    <td><span class="badge badge-${{retailer.business_status === 'OPERATIONAL' ? 'success' : 'warning'}}">${{retailer.business_status}}</span></td>
                `;
                foundTableBody.appendChild(row);
            }});

            // Populate Google category mix table
            const categoryTableBody = document.getElementById('categoryTableBody');
            categoryTableBody.innerHTML = '';

            // Count all Google types across all retailers
            const categoryCount = {{}};
            let totalCategories = 0;

            data.retailers_found.forEach(retailer => {{
                if (retailer.types) {{
                    // Types come as comma-separated string or array
                    const types = Array.isArray(retailer.types) ? retailer.types : retailer.types.split(', ');
                    types.forEach(type => {{
                        const cleanType = type.trim();
                        if (cleanType && cleanType !== 'point_of_interest' && cleanType !== 'establishment') {{
                            categoryCount[cleanType] = (categoryCount[cleanType] || 0) + 1;
                            totalCategories++;
                        }}
                    }});
                }}
            }});

            // Sort by count descending
            const sortedCategories = Object.entries(categoryCount)
                .sort((a, b) => b[1] - a[1]);

            // Populate table
            sortedCategories.forEach(([category, count]) => {{
                const percentage = ((count / data.retailers_found.length) * 100).toFixed(1);
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="text-transform: capitalize;">${{category.replace(/_/g, ' ')}}</td>
                    <td><strong>${{count}}</strong></td>
                    <td>${{percentage}}%</td>
                `;
                categoryTableBody.appendChild(row);
            }});

            // Populate missing retailers table (top 100)
            const missingTableBody = document.getElementById('missingTableBody');
            missingTableBody.innerHTML = '';
            data.retailers_missing.slice(0, 100).forEach(retailer => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{retailer.name}}</td>
                    <td>${{retailer.category || 'Unknown'}}</td>
                `;
                missingTableBody.appendChild(row);
            }});

            // Scroll to results
            document.getElementById('results').scrollIntoView({{ behavior: 'smooth' }});
        }}
    </script>
</body>
</html>'''

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Interactive dashboard generated: {output_path}")
    print("\nTo use:")
    print("1. Start the backend server: python api_server.py")
    print(f"2. Open: {output_path}")
    print("3. Enter coordinates and click 'Run Analysis'")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate interactive dashboard')
    parser.add_argument('--api-key', default='AIzaSyA85pSu9Naza2sf1YTjq82D3v7UFtt8I80', help='Google Maps API key')
    parser.add_argument('--output', default='interactive_dashboard.html', help='Output file path')

    args = parser.parse_args()

    generate_interactive_dashboard(args.api_key, args.output)
