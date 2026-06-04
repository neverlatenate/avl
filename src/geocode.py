import urllib.request
import urllib.parse
import json
import time
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

locations = [
    {"title": "Thomas Wolfe Memorial house (facing the hotel)", "address": "52 N Market St, Asheville, NC 28801"},
    {"title": "Urban trail marker: Thomas Wolfe's neighborhood (1900-1924)", "address": "52 N Market St, Asheville, NC 28801"},
    {"title": "Chicken Alley (1930-1950)", "address": "8 Chicken Aly, Asheville, NC 28801"},
    {"title": "Asheville Showcase (1960s)", "address": "57-59 Broadway St, Asheville, NC 28801"},
    {"title": "Moogseum", "address": "56 Broadway St, Asheville, NC 28801"},
    {"title": "Mellow Mushroom", "address": "50 Broadway St, Asheville, NC 28801"},
    {"title": "Blomberg Annex to Asheville Community Theatre (ACT) (1923)", "address": "35 E Walnut St, Asheville, NC 28801"},
    {"title": "Asheville Community Theatre (ACT) (1940-PRESENT)", "address": "35 E Walnut St, Asheville, NC 28801"},
    {"title": "Finklesteins Pawn Shop (1903-PRESENT)", "address": "21 Broadway St, Asheville, NC 28801"},
    {"title": "Black Mountain College Tribute Wall (1933-1957)", "address": "5 W Walnut St, Asheville, NC 28801"},
    {"title": "Vanderbilt Shirt Factory (1950s)", "address": "65 W Walnut St, Asheville, NC 28801"},
    {"title": "Tops for Shoes (1950s-PRESENT)", "address": "27 N Lexington Ave, Asheville, NC 28801"},
    {"title": "Coleman Zageir and the Man's Store (1922-1962)", "address": "22 Patton Ave, Asheville, NC 28801"},
    {"title": "S and W Cafeteria (1929-1974)", "address": "56 Patton Ave, Asheville, NC 28801"},
    {"title": "Flatiron building", "address": "20 Battery Park Ave, Asheville, NC 28801"},
    {"title": "Pollock Crest", "address": "39 Patton Ave, Asheville, NC 28801"},
    {"title": "Earth Guild", "address": "33 Haywood St, Asheville, NC 28801"},
    {"title": "Urban Trail Marker to shoppers (1880-1990)", "address": "55 Haywood St, Asheville, NC 28801"},
    {"title": "Fine Arts theater (optional) (1947-1960s)", "address": "36 Biltmore Ave, Asheville, NC 28801"}
]

cache = {}

for loc in locations:
    address = loc['address']
    if address in cache:
        loc['lat'] = cache[address]['lat']
        loc['lng'] = cache[address]['lng']
        continue

    query = urllib.parse.quote(address)
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            if data:
                lat = float(data[0]['lat'])
                lng = float(data[0]['lon'])
                loc['lat'] = lat
                loc['lng'] = lng
                cache[address] = {'lat': lat, 'lng': lng}
            else:
                loc['lat'] = None
                loc['lng'] = None
                print(f"Failed to geocode: {address}")
    except Exception as e:
        print(f"Error for {address}: {e}")
    time.sleep(1)

print(json.dumps(locations, indent=2))
