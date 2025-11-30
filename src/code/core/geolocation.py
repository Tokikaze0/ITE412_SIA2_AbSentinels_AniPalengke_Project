import requests

def get_coordinates(address):
    """
    Converts an address string to (latitude, longitude) using OpenStreetMap Nominatim API.
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "AniPalengke/1.0 (anipalengke@example.com)" # Required by Nominatim
    }

    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            return None
    except Exception as e:
        print(f"Geocoding request failed: {e}")
        return None

def get_address_from_coordinates(lat, lng):
    """
    Converts (latitude, longitude) to a human-readable address using OpenStreetMap Nominatim API.
    """
    base_url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lng,
        "format": "json"
    }
    headers = {
        "User-Agent": "AniPalengke/1.0 (anipalengke@example.com)" # Required by Nominatim
    }

    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data and 'display_name' in data:
            return data['display_name']
        return None
    except Exception:
        return None
