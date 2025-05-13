import pandas as pd
import requests
import time

# --- Load postcode database ---
postcode_df = pd.read_csv("support_data/ukpostcodes.csv")
postcode_df["postcode"] = postcode_df["postcode"].str.replace(" ", "").str.upper()

# --- Geo cache to avoid repeated lookups ---
geo_cache = {}

# --- Function: Get coordinates from Nominatim API ---
def get_lat_long(location):
    if location in geo_cache:
        return geo_cache[location]

    try:
        response = requests.get("https://nominatim.openstreetmap.org/search", params={
            "q": location,
            "format": "json",
            "limit": 1
        }, headers={"User-Agent": "GeoLookupApp/1.0"})
        response.raise_for_status()
        data = response.json()

        if data:
            lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
            geo_cache[location] = (lat, lon)
            time.sleep(1)
            return lat, lon
    except Exception as e:
        print(f"⚠️ Error fetching location '{location}': {e}")

    return None, None

# --- Function: Get coordinates from local postcode CSV ---
def get_lat_long_offline(postcode):
    postcode = postcode.replace(" ", "").upper()
    match = postcode_df[postcode_df["postcode"] == postcode]
    if not match.empty:
        return match["latitude"].values[0], match["longitude"].values[0]
    return None, None

# --- Function: Add missing coordinates to DataFrame ---
def add_lat_long_if_missing(df, location_column):
    latitudes, longitudes = [], []

    for idx, row in df.iterrows():
        lat = row.get("latitude", None)
        lon = row.get("longitude", None)

        if pd.notna(lat) and pd.notna(lon):
            latitudes.append(lat)
            longitudes.append(lon)
            continue

        location = str(row[location_column])
        print(f"🌍 Getting lat/lon for [{idx+1}/{len(df)}]: {location}")

        if any(char.isdigit() for char in location):  # Likely a postcode
            lat, lon = get_lat_long_offline(location)
            if lat and lon:
                print(f"✅ Found in postcode DB: ({lat}, {lon})")
        else:
            lat, lon = get_lat_long(location)
            if lat and lon:
                print(f"✅ Fetched from Nominatim: ({lat}, {lon})")
            else:
                print("⚠️ Location not found")

        latitudes.append(lat)
        longitudes.append(lon)

    df["latitude"] = latitudes
    df["longitude"] = longitudes
    return df
