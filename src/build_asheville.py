import json
import urllib.parse
import requests
import time
import os
import csv

API_KEY = 'AIzaSyB9_MF2J2Lkb2WhL2-fwwRkfsobBJ0Clps'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'avl.csv')
CACHE_PATH = os.path.join(SCRIPT_DIR, 'geocoded_avl.json')
OUTPUT_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), 'index.html')
MAP_HTML_PATH = os.path.join(SCRIPT_DIR, 'map.html')

def geocode(address):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={API_KEY}'
    try:
        res = requests.get(url, timeout=10).json()
        if res.get('status') == 'OK' and res.get('results'):
            loc = res['results'][0]['geometry']['location']
            return loc['lat'], loc['lng']
    except Exception as e:
        print(f'  Geocode error for {address}: {e}')
    return None, None

def load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r') as f:
                data = json.load(f)
                return {item['name']: (item['lat'], item['lng']) for item in data if item.get('lat') is not None}
        except Exception as e:
            print(f"Error loading cache: {e}")
    return {}

def save_cache(cache_data):
    # Convert cache back to list format to save
    list_data = []
    for idx, (name, (lat, lng)) in enumerate(cache_data.items(), 1):
        list_data.append({
            "number": idx,
            "name": name,
            "address": name, # rough fallback
            "lat": lat,
            "lng": lng
        })
    try:
        with open(CACHE_PATH, 'w') as f:
            json.dump(list_data, f, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")

def main():
    print("Loading walking tour landmarks from CSV...")
    landmarks = []
    
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            landmarks.append({
                "number": int(row['Number']),
                "name": row['Landmark'],
                "address": row['Address'],
                "location_desc": row.get('LocationDesc', ''),
                "question": row.get('Question', ''),
                "answer": row.get('Answer', ''),
                "teachingPoint": row.get('TeachingPoint', ''),
                "image": row.get('Image', '')
            })

    print(f"Loaded {len(landmarks)} landmarks from CSV.")
    cache = load_cache()

    markers = []
    cache_updated = False

    for loc in landmarks:
        name = loc['name']
        address = loc['address']
        num = loc['number']
        
        # Check cache first
        if name in cache:
            lat, lng = cache[name]
            print(f"Found cache for #{num}: {name} ({lat}, {lng})")
        else:
            print(f"Geocoding #{num}: {name}...")
            lat, lng = geocode(address)
            time.sleep(0.15)
            if lat is not None:
                cache[name] = (lat, lng)
                cache_updated = True
                print(f"  Geocoded: {lat}, {lng}")
            else:
                print(f"  Warning: Geocoding failed for {name} ({address})")
        
        markers.append({
            "number": num,
            "name": name,
            "address": address,
            "lat": lat,
            "lng": lng,
            "location_desc": loc.get("location_desc", ""),
            "question": loc.get("question", ""),
            "answer": loc.get("answer", ""),
            "teachingPoint": loc.get("teachingPoint", ""),
            "image": loc.get("image", "")
        })

    if cache_updated:
        # Re-save updated cache with current list of locations
        save_list = []
        for m in markers:
            save_list.append({
                "number": m["number"],
                "name": m["name"],
                "address": m["address"],
                "lat": m["lat"],
                "lng": m["lng"]
            })
        with open(CACHE_PATH, 'w') as f:
            json.dump(save_list, f, indent=2)
        print("Updated geocode cache saved.")

    markers_json = json.dumps(markers, indent=4)

    html_content = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Family Store - Asheville’s Jewish Heritage Walking Tour</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --primary: #1e3a8a;
            --primary-light: #2563eb;
            --accent: #d97706;
            --accent-light: #f59e0b;
            --bg-sidebar: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
            --font-display: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.3);
        }}

        body {{
            margin: 0;
            padding: 0;
            font-family: var(--font-body);
            background-color: #020617;
            color: var(--text-main);
            height: 100vh;
            display: flex;
            overflow: hidden;
        }}

        /* Sidebar Container */
        .sidebar {{
            width: 380px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            height: 100%;
            z-index: 10;
            box-shadow: 4px 0 25px rgba(0, 0, 0, 0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            flex-shrink: 0;
        }}

        .sidebar.collapsed {{
            margin-left: -380px;
        }}

        /* Sidebar Header */
        .sidebar-header {{
            padding: 24px;
            border-bottom: 1px solid var(--border);
            background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
        }}

        .sidebar-header h1 {{
            font-family: var(--font-display);
            font-size: 20px;
            font-weight: 700;
            margin: 0 0 8px 0;
            color: #ffffff;
            letter-spacing: -0.025em;
            line-height: 1.2;
        }}

        .sidebar-header p {{
            font-size: 13px;
            color: var(--text-muted);
            margin: 0;
            line-height: 1.4;
        }}

        .tour-meta {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 14px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .tour-badge {{
            background-color: rgba(217, 119, 6, 0.2);
            color: var(--accent-light);
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid rgba(217, 119, 6, 0.3);
        }}

        .tour-stops-count {{
            color: var(--text-muted);
        }}

        /* Search Filter Container */
        .search-container {{
            padding: 16px 24px;
            border-bottom: 1px solid var(--border);
            background-color: rgba(15, 23, 42, 0.6);
        }}

        .search-wrapper {{
            position: relative;
            display: flex;
            align-items: center;
        }}

        .search-input {{
            width: 100%;
            padding: 10px 14px 10px 38px;
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-main);
            font-family: var(--font-body);
            font-size: 14px;
            outline: none;
            transition: all 0.2s ease;
        }}

        .search-input:focus {{
            border-color: var(--primary-light);
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
            background-color: var(--bg-card-hover);
        }}

        .search-icon {{
            position: absolute;
            left: 12px;
            width: 16px;
            height: 16px;
            fill: var(--text-muted);
            pointer-events: none;
        }}

        /* Landmark List */
        .landmark-list {{
            flex: 1;
            overflow-y: auto;
            padding: 16px 24px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        /* Custom Scrollbar for Sidebar */
        .landmark-list::-webkit-scrollbar {{
            width: 6px;
        }}

        .landmark-list::-webkit-scrollbar-track {{
            background: var(--bg-sidebar);
        }}

        .landmark-list::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 3px;
        }}

        .landmark-list::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}

        /* Landmark Card */
        .landmark-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px 16px 20px 16px; /* Generous bottom padding to give text ample room */
            display: flex;
            align-items: flex-start; /* Align elements to the top so text can expand downward */
            gap: 14px;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            user-select: none;
            position: relative;
            overflow: hidden;
            box-sizing: border-box;
            min-height: 84px; /* Establish a comfortable minimum height */
        }}

        .landmark-card::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background-color: transparent;
            transition: background-color 0.2s ease;
        }}

        .landmark-card:hover {{
            background-color: var(--bg-card-hover);
            transform: translateY(-2px);
            border-color: #475569;
            box-shadow: var(--shadow-lg);
        }}

        .landmark-card.active {{
            background-color: rgba(30, 58, 138, 0.25);
            border-color: rgba(37, 99, 235, 0.5);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}

        .landmark-card.active::before {{
            background-color: var(--accent);
        }}

        /* Badge for Marker Number */
        .landmark-badge {{
            width: 28px;
            height: 28px;
            background-color: var(--primary);
            color: #ffffff;
            font-family: var(--font-display);
            font-weight: 700;
            font-size: 13px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            border: 2px solid rgba(255, 255, 255, 0.1);
            transition: all 0.2s ease;
        }}

        .landmark-card:hover .landmark-badge {{
            background-color: var(--primary-light);
            transform: scale(1.1);
        }}

        .landmark-card.active .landmark-badge {{
            background-color: var(--accent);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: 0 0 8px rgba(217, 119, 6, 0.4);
        }}

        .landmark-info {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            flex: 1; /* Allow text container to take all available width */
            min-width: 0; /* Prevent flex overflow */
            padding-bottom: 2px; /* Extra bottom breathing room for text content */
        }}

        .landmark-name {{
            font-size: 15px;
            font-weight: 600;
            line-height: 1.4;
            color: var(--text-main);
            transition: color 0.2s ease;
            word-wrap: break-word;
            overflow-wrap: break-word;
            display: block;
        }}

        .landmark-card.active .landmark-name {{
            color: #ffffff;
        }}

        .landmark-address {{
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.4;
            word-wrap: break-word;
            overflow-wrap: break-word;
            display: block;
        }}

        /* Main Map Container */
        .map-wrapper {{
            flex: 1;
            position: relative;
            height: 100%;
        }}

        #map {{
            height: 100%;
            width: 100%;
        }}

        /* Sidebar Toggle Button */
        .sidebar-toggle {{
            position: absolute;
            left: 20px;
            top: 20px;
            z-index: 100;
            background-color: var(--bg-sidebar);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: var(--font-display);
            font-weight: 600;
            font-size: 12px;
            box-shadow: var(--shadow-lg);
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .sidebar-toggle:hover {{
            background-color: var(--bg-card-hover);
            border-color: #475569;
            transform: translateY(-1px);
        }}

        /* Beautiful Custom InfoWindow Styles */
        .info-window {{
            padding: 0;
            max-width: 320px;
            font-family: var(--font-body);
            color: #1e293b;
            box-sizing: border-box;
        }}

        .info-window-image {{
            width: 100%;
            height: 160px;
            object-fit: cover;
            border-radius: 8px 8px 0 0;
            margin-bottom: 12px;
            display: block;
        }}

        .info-window-content {{
            padding: 4px 10px 10px 10px;
        }}

        .info-window h3 {{
            margin: 0 0 8px 0;
            font-family: var(--font-display);
            font-size: 17px;
            font-weight: 700;
            color: var(--primary);
            line-height: 1.3;
        }}

        .info-window .address-text {{
            margin: 0 0 10px 0;
            font-size: 13px;
            color: #475569;
            line-height: 1.4;
        }}

        .info-window-details {{
            margin-top: 12px;
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            line-height: 1.4;
            color: #334155;
        }}

        .info-window-qa {{
            margin-bottom: 8px;
            border-bottom: 1px dashed #cbd5e1;
            padding-bottom: 8px;
        }}

        .info-window-q {{
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 4px;
        }}

        .info-window-a {{
            color: #475569;
        }}

        .info-window-tp {{
            font-style: italic;
        }}

        .info-window-tp-title {{
            font-weight: 700;
            color: var(--primary);
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 0.05em;
            margin-bottom: 2px;
            display: block;
        }}

        .info-window-footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid #e2e8f0;
            padding-top: 8px;
            margin-top: 10px;
        }}

        .info-window-badge {{
            background-color: rgba(30, 58, 138, 0.1);
            color: var(--primary);
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
        }}

        .info-window a {{
            color: var(--primary-light);
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: color 0.15s ease;
        }}

        .info-window a:hover {{
            color: var(--primary);
            text-decoration: underline;
        }}

        /* Bottom Detail Panel hidden by default on desktop */
        .detail-panel {{
            display: none;
        }}

        /* Mobile Adjustments */
        @media (max-width: 768px) {{
            body {{
                flex-direction: column-reverse;
            }}

            .sidebar {{
                width: 100%;
                height: 45vh;
                border-right: none;
                border-top: 1px solid var(--border);
            }}

            .sidebar.collapsed {{
                margin-left: 0;
                height: 0;
                overflow: hidden;
            }}

            .map-wrapper {{
                flex: 1;
                height: 55vh;
            }}

            .sidebar-toggle {{
                top: auto;
                bottom: 20px;
                left: 20px;
            }}

            /* Bottom Detail Panel for Mobile styling */
            .detail-panel {{
                display: flex;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: var(--bg-sidebar);
                border-top: 1px solid var(--border);
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                z-index: 1000;
                transform: translateY(100%);
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                max-height: 60vh;
                flex-direction: column;
                box-shadow: 0 -10px 25px rgba(0, 0, 0, 0.5);
                box-sizing: border-box;
            }}

            .detail-panel.active {{
                transform: translateY(0);
            }}

            .detail-header {{
                padding: 12px 20px;
                border-bottom: 1px solid var(--border);
                display: flex;
                align-items: center;
                justify-content: space-between;
                background-color: rgba(15, 23, 42, 0.6);
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }}

            .detail-close {{
                background: none;
                border: none;
                color: var(--text-muted);
                font-size: 28px;
                cursor: pointer;
                padding: 0;
                line-height: 1;
            }}

            .detail-body {{
                padding: 20px;
                overflow-y: auto;
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}

            .detail-body h3 {{
                margin: 0;
                font-family: var(--font-display);
                font-size: 18px;
                font-weight: 700;
                color: #ffffff;
                line-height: 1.3;
            }}

            .detail-address {{
                font-size: 12px;
                color: var(--text-muted);
                margin: 0;
                line-height: 1.4;
            }}

            .detail-description {{
                font-size: 13.5px;
                line-height: 1.5;
                color: var(--text-main);
                margin: 0;
            }}

            .detail-images-wrapper {{
                display: flex;
                flex-direction: column;
                gap: 10px;
                margin: 8px 0;
            }}

            .detail-images-wrapper img {{
                width: 100%;
                border-radius: 8px;
                max-height: 180px;
                object-fit: cover;
                display: block;
            }}

            .detail-footer {{
                padding: 12px 20px;
                border-top: 1px solid var(--border);
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: rgba(15, 23, 42, 0.6);
            }}

            .detail-footer a {{
                color: var(--primary-light);
                text-decoration: none;
                font-size: 13px;
                font-weight: 600;
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }}

            .detail-details {{
                background-color: var(--bg-card);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.5;
                color: var(--text-main);
            }}

            .detail-qa {{
                margin-bottom: 8px;
                border-bottom: 1px dashed var(--border);
                padding-bottom: 8px;
            }}

            .detail-q {{
                font-weight: 700;
                color: var(--accent-light);
                margin-bottom: 4px;
            }}

            .detail-a {{
                color: var(--text-main);
            }}

            .detail-tp {{
                font-style: italic;
                color: var(--text-main);
            }}
        }}
    </style>
</head>

<body>
    <!-- Sidebar Container -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h1>The Family Store</h1>
            <p>Asheville’s Jewish Heritage Walking Tour</p>
            <div class="tour-meta">
                <span class="tour-badge">Walking Tour</span>
                <span class="tour-stops-count" id="stops-counter">{len(landmarks)} Stops</span>
            </div>
        </div>

        <div class="search-container">
            <div class="search-wrapper">
                <svg class="search-icon" viewBox="0 0 24 24">
                    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
                </svg>
                <input type="text" class="search-input" id="search-input" placeholder="Search landmarks or addresses..." autocomplete="off">
            </div>
        </div>

        <div class="landmark-list" id="landmark-list">
            <!-- Dynamically populated via JS -->
        </div>
    </aside>

    <!-- Map Area -->
    <main class="map-wrapper">
        <button class="sidebar-toggle" id="sidebar-toggle">
            <span id="toggle-icon">◀</span>
            <span id="toggle-text">Hide List</span>
        </button>
        <div id="map"></div>
    </main>

    <!-- Bottom Detail Panel for Mobile -->
    <div class="detail-panel" id="detail-panel">
        <div class="detail-header">
            <span class="info-window-badge" id="detail-badge">Stop #1</span>
            <button class="detail-close" id="detail-close">&times;</button>
        </div>
        <div class="detail-body">
            <h3 id="detail-title">Title</h3>
            <p class="detail-address" id="detail-address">Address</p>
            <div class="detail-images-wrapper" id="detail-images"></div>
            <div class="detail-description" id="detail-desc"></div>
        </div>
        <div class="detail-footer">
            <a href="#" id="detail-link" target="_blank">View on Maps ↗</a>
        </div>
    </div>

    <!-- Google Maps API and Application Logic -->
    <script>
        // 24 landmarks geocoded directly from avl.csv & walking tour RTF
        const locations = {markers_json};

        // Clean silver dark-highlighting map styles
        const mapStyles = [
            {{ "elementType": "geometry", "stylers": [{{ "color": "#f5f5f5" }}] }},
            {{ "elementType": "labels.icon", "stylers": [{{ "visibility": "off" }}] }},
            {{ "elementType": "labels.text.fill", "stylers": [{{ "color": "#616161" }}] }},
            {{ "elementType": "labels.text.stroke", "stylers": [{{ "color": "#f5f5f5" }}] }},
            {{ "featureType": "administrative.land_parcel", "elementType": "labels.text.fill", "stylers": [{{ "color": "#bdbdbd" }}] }},
            {{ "featureType": "poi", "elementType": "geometry", "stylers": [{{ "color": "#eeeeee" }}] }},
            {{ "featureType": "poi", "elementType": "labels.text.fill", "stylers": [{{ "color": "#757575" }}] }},
            {{ "featureType": "poi.park", "elementType": "geometry", "stylers": [{{ "color": "#e5e5e5" }}] }},
            {{ "featureType": "poi.park", "elementType": "labels.text.fill", "stylers": [{{ "color": "#9e9e9e" }}] }},
            {{ "featureType": "road", "elementType": "geometry", "stylers": [{{ "color": "#ffffff" }}] }},
            {{ "featureType": "road.arterial", "elementType": "labels.text.fill", "stylers": [{{ "color": "#757575" }}] }},
            {{ "featureType": "road.highway", "elementType": "geometry", "stylers": [{{ "color": "#dadada" }}] }},
            {{ "featureType": "road.highway", "elementType": "labels.text.fill", "stylers": [{{ "color": "#616161" }}] }},
            {{ "featureType": "road.local", "elementType": "labels.text.fill", "stylers": [{{ "color": "#9e9e9e" }}] }},
            {{ "featureType": "transit.line", "elementType": "geometry", "stylers": [{{ "color": "#e5e5e5" }}] }},
            {{ "featureType": "transit.station", "elementType": "geometry", "stylers": [{{ "color": "#eeeeee" }}] }},
            {{ "featureType": "water", "elementType": "geometry", "stylers": [{{ "color": "#c2d1e0" }}] }}, // slightly bluer water
            {{ "featureType": "water", "elementType": "labels.text.fill", "stylers": [{{ "color": "#9e9e9e" }}] }}
        ];

        let map;
        let markers = [];
        let infoWindow;
        let activeMarkerIndex = -1;

        // Custom SVG Pin Symbol Builder
        function getMarkerSymbol(number, isActive) {{
            return {{
                path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z', // Solid teardrop pin
                fillColor: isActive ? '#d97706' : '#1e3a8a', // Gold active vs Deep Navy inactive
                fillOpacity: 1.0,
                strokeColor: '#ffffff',
                strokeWeight: 2,
                scale: isActive ? 1.8 : 1.4,
                anchor: new google.maps.Point(12, 22),
                labelOrigin: new google.maps.Point(12, 9)
            }};
        }}

        // Initialize Google Map
        function initMap() {{
            const mapOptions = {{
                zoom: 15,
                center: {{ lat: 35.5960, lng: -82.5530 }}, // Centered perfectly on downtown Asheville
                styles: mapStyles,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: false,
                zoomControlOptions: {{
                    position: google.maps.ControlPosition.RIGHT_CENTER
                }}
            }};

            map = new google.maps.Map(document.getElementById("map"), mapOptions);
            infoWindow = new google.maps.InfoWindow();

            // Handle when InfoWindow is closed by clicking "X"
            infoWindow.addListener('closeclick', () => {{
                deactivateAll();
            }});

            // Close mobile detail panel or infoWindow on map click
            map.addListener('click', () => {{
                if (window.innerWidth <= 768) {{
                    closeMobilePanel();
                }} else {{
                    infoWindow.close();
                    deactivateAll();
                }}
            }});

            renderSidebarList(locations);
            createMarkers(locations);

            // Fit map to bounds of all locations dynamically
            const bounds = new google.maps.LatLngBounds();
            locations.forEach(loc => {{
                if (loc.lat && loc.lng) {{
                    bounds.extend({{ lat: loc.lat, lng: loc.lng }});
                }}
            }});
            map.fitBounds(bounds);
        }}

        // Create Markers on Map
        function createMarkers(data) {{
            // Clear existing
            markers.forEach(m => m.setMap(null));
            markers = [];

            data.forEach((loc, idx) => {{
                if (!loc.lat || !loc.lng) return;

                const marker = new google.maps.Marker({{
                    position: {{ lat: loc.lat, lng: loc.lng }},
                    title: `${{loc.number}}. ${{loc.name}}`,
                    icon: getMarkerSymbol(loc.number, false),
                    label: {{
                        text: loc.number.toString(),
                        color: '#ffffff',
                        fontSize: '11px',
                        fontWeight: '700',
                        fontFamily: 'Outfit'
                    }},
                    map: map
                }});

                marker.addListener("click", () => {{
                    selectLocation(idx);
                }});

                markers.push(marker);
            }});
        }}

        // Render Sidebar List Cards
        function renderSidebarList(data) {{
            const listContainer = document.getElementById("landmark-list");
            listContainer.innerHTML = "";

            if (data.length === 0) {{
                listContainer.innerHTML = `
                    <div style="text-align: center; padding: 40px 20px; color: var(--text-muted); font-size: 14px;">
                        No matching landmarks found.
                    </div>
                `;
                document.getElementById("stops-counter").innerText = "0 Stops";
                return;
            }}

            document.getElementById("stops-counter").innerText = `${{data.length}} Stop${{data.length === 1 ? '' : 's'}}`;

            data.forEach((loc, index) => {{
                // Find actual index in original locations array
                const originalIndex = locations.findIndex(l => l.number === loc.number);

                const card = document.createElement("div");
                card.className = "landmark-card";
                card.id = `card-${{originalIndex}}`;
                card.innerHTML = `
                    <div class="landmark-badge">${{loc.number}}</div>
                    <div class="landmark-info">
                        <span class="landmark-name">${{loc.name}}</span>
                        <span class="landmark-address">${{loc.address}}</span>
                    </div>
                `;

                card.addEventListener("click", () => {{
                    selectLocation(originalIndex);
                }});

                listContainer.appendChild(card);
            }});
        }}

        // Select and Highlight Location (both list and marker)
        function selectLocation(index) {{
            deactivateAll();

            activeMarkerIndex = index;
            const loc = locations[index];
            const marker = markers[index];

            // 1. Highlight Marker
            if (marker) {{
                marker.setIcon(getMarkerSymbol(loc.number, true));
                marker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
                
                // 2. Open InfoWindow or Mobile Detail Panel
                if (window.innerWidth <= 768) {{
                    infoWindow.close();
                    
                    // Populate Mobile Detail Panel
                    document.getElementById("detail-badge").innerText = `Stop #${{loc.number}}`;
                    document.getElementById("detail-title").innerText = `${{loc.number}}. ${{loc.name}}`;
                    document.getElementById("detail-address").innerText = loc.location_desc || loc.address;
                    
                    // Build Images
                    let imageHtml = "";
                    if (loc.image) {{
                        const imgs = loc.image.split(',');
                        imgs.forEach(img => {{
                            if (img.trim()) {{
                                imageHtml += `<img src="${{img.trim()}}" alt="${{loc.name}}">`;
                            }}
                        }});
                    }}
                    document.getElementById("detail-images").innerHTML = imageHtml;
                    
                    // Build Details/QA/Teaching Point
                    let detailsHtml = "";
                    if (loc.question || loc.teachingPoint) {{
                        detailsHtml += `<div class="detail-details">`;
                        if (loc.question) {{
                            detailsHtml += `
                                <div class="detail-qa">
                                    <div class="detail-q">❓ Q: ${{loc.question}}</div>
                                    <div class="detail-a">💡 A: ${{loc.answer}}</div>
                                </div>
                            `;
                        }}
                        if (loc.teachingPoint) {{
                            detailsHtml += `
                                <div class="detail-tp">
                                    ${{loc.teachingPoint}}
                                </div>
                            `;
                        }}
                        detailsHtml += `</div>`;
                    }}
                    document.getElementById("detail-desc").innerHTML = detailsHtml;
                    
                    // Link
                    document.getElementById("detail-link").href = `https://www.google.com/maps/search/?api=1&query=${{loc.lat}},${{loc.lng}}`;
                    
                    // Show Panel
                    document.getElementById("detail-panel").classList.add("active");
                    
                    // Collapse Sidebar on mobile
                    sidebar.classList.add("collapsed");
                    updateSidebarToggle();
                }} else {{
                    // Open InfoWindow
                    let imageHtml = "";
                    if (loc.image) {{
                        const imgs = loc.image.split(',');
                        imgs.forEach(img => {{
                            if (img.trim()) {{
                                imageHtml += `<img src="${{img.trim()}}" class="info-window-image" alt="${{loc.name}}">`;
                            }}
                        }});
                    }}

                    let detailsHtml = "";
                    if (loc.question || loc.teachingPoint) {{
                        detailsHtml += `<div class="info-window-details">`;
                        if (loc.question) {{
                            detailsHtml += `
                                <div class="info-window-qa">
                                    <div class="info-window-q">❓ Q: ${{loc.question}}</div>
                                    <div class="info-window-a">💡 A: ${{loc.answer}}</div>
                                </div>
                            `;
                        }}
                        if (loc.teachingPoint) {{
                            detailsHtml += `
                                <div class="info-window-tp">
                                    ${{loc.teachingPoint}}
                                </div>
                            `;
                        }}
                        detailsHtml += `</div>`;
                    }}

                    const content = `
                        <div class="info-window">
                            ${{imageHtml}}
                            <div class="info-window-content">
                                <h3>${{loc.number}}. ${{loc.name}}</h3>
                                <p class="address-text">${{loc.location_desc || loc.address}}</p>
                                ${{detailsHtml}}
                                <div class="info-window-footer">
                                    <span class="info-window-badge">Stop #${{loc.number}}</span>
                                    <a href="https://www.google.com/maps/search/?api=1&query=${{loc.lat}},${{loc.lng}}" target="_blank">
                                        View on Maps ↗
                                    </a>
                                </div>
                            </div>
                        </div>
                    `;
                    infoWindow.setContent(content);
                    infoWindow.open(map, marker);
                }}
            }}

            // 3. Pan map smoothly
            map.panTo({{ lat: loc.lat, lng: loc.lng }});
            // minor zoom in if zoomed out
            if (map.getZoom() < 16) {{
                map.setZoom(16);
            }}
            if (window.innerWidth <= 768) {{
                setTimeout(() => {{
                    if (map) map.panBy(0, 120);
                }}, 150);
            }}

            // 4. Highlight Sidebar Card
            const card = document.getElementById(`card-${{index}}`);
            if (card) {{
                card.classList.add("active");
                card.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            }}
        }}

        // Deactivate all highlighted cards and markers
        function deactivateAll() {{
            if (activeMarkerIndex !== -1) {{
                const loc = locations[activeMarkerIndex];
                const marker = markers[activeMarkerIndex];
                if (marker) {{
                    marker.setIcon(getMarkerSymbol(loc.number, false));
                    marker.setZIndex(null);
                }}
                
                const card = document.getElementById(`card-${{activeMarkerIndex}}`);
                if (card) {{
                    card.classList.remove("active");
                }}
            }}
            activeMarkerIndex = -1;
        }}

        // Collapsible Sidebar Setup
        const sidebar = document.getElementById("sidebar");
        const toggleBtn = document.getElementById("sidebar-toggle");
        const toggleIcon = document.getElementById("toggle-icon");
        const toggleText = document.getElementById("toggle-text");

        function updateSidebarToggle() {{
            const isCollapsed = sidebar.classList.contains("collapsed");
            const isMobile = window.innerWidth <= 768;
            if (isMobile) {{
                toggleIcon.innerText = isCollapsed ? "▲" : "▼";
            }} else {{
                toggleIcon.innerText = isCollapsed ? "▶" : "◀";
            }}
            toggleText.innerText = isCollapsed ? "Show List" : "Hide List";
        }}

        function closeMobilePanel() {{
            const panel = document.getElementById("detail-panel");
            if (panel) {{
                panel.classList.remove("active");
            }}
            const sidebarEl = document.getElementById("sidebar");
            if (sidebarEl) {{
                sidebarEl.classList.remove("collapsed");
            }}
            deactivateAll();
            updateSidebarToggle();
            if (map) {{
                setTimeout(() => {{
                    google.maps.event.trigger(map, 'resize');
                }}, 300);
            }}
        }}

        // Close Mobile Panel button listener
        document.getElementById("detail-close").addEventListener("click", () => {{
            closeMobilePanel();
        }});

        toggleBtn.addEventListener("click", () => {{
            const isCollapsed = sidebar.classList.toggle("collapsed");
            updateSidebarToggle();
            
            // If we manually show the list on mobile, close the details panel
            if (!isCollapsed && window.innerWidth <= 768) {{
                const panel = document.getElementById("detail-panel");
                if (panel) {{
                    panel.classList.remove("active");
                }}
            }}
            
            // Trigger maps resize
            if (map) {{
                setTimeout(() => {{
                    google.maps.event.trigger(map, 'resize');
                }}, 300);
            }}
        }});

        window.addEventListener("resize", () => {{
            updateSidebarToggle();
            if (window.innerWidth > 768) {{
                const panel = document.getElementById("detail-panel");
                if (panel) {{
                    panel.classList.remove("active");
                }}
            }}
        }});

        // Initialize state on load
        updateSidebarToggle();

        // Live Search Filtering
        const searchInput = document.getElementById("search-input");
        searchInput.addEventListener("input", (e) => {{
            const query = e.target.value.toLowerCase().trim();
            const filtered = locations.filter(loc => 
                loc.name.toLowerCase().includes(query) || 
                loc.address.toLowerCase().includes(query)
            );
            
            renderSidebarList(filtered);
            
            // Show/hide markers based on match
            locations.forEach((loc, idx) => {{
                const isMatch = filtered.some(f => f.number === loc.number);
                if (markers[idx]) {{
                    markers[idx].setVisible(isMatch);
                }}
            }});
        }});
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}&callback=initMap" async defer></script>
</body>

</html>
"""

    with open(OUTPUT_PATH, 'w') as f:
        f.write(html_content)

    with open(MAP_HTML_PATH, 'w') as f:
        f.write(html_content)

    print(f"Successfully generated index.html and map.html with {len(markers)} markers.")

if __name__ == '__main__':
    main()
