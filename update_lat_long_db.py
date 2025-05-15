import pandas as pd
import requests
import time
from sqlalchemy import create_engine, text

# ------------------ CONFIGURATION ------------------

DB_URI = "postgresql://postgres:postgres@localhost:5433/ProyectoDA"  # 🔁 Replace with actual values
TABLE_NAME = "locations"
POSTCODE_CSV = "support_data/ukpostcodes.csv"

# ------------------ Load Postcode Database ------------------

postcode_df = pd.read_csv(POSTCODE_CSV)
postcode_df["postcode"] = postcode_df["postcode"].str.replace(" ", "").str.upper()

# ------------------ Geo Cache & Lookup ------------------

geo_cache = {}

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
            time.sleep(1)  # Respect Nominatim usage policy
            return lat, lon
    except Exception as e:
        print(f"⚠️ Error fetching location '{location}': {e}")

    return None, None

def get_lat_long_offline(postcode):
    postcode = postcode.replace(" ", "").upper()
    match = postcode_df[postcode_df["postcode"] == postcode]
    if not match.empty:
        return match["latitude"].values[0], match["longitude"].values[0]
    return None, None

def add_lat_long_if_missing(df, location_column):
    updated_rows = []

    for idx, row in df.iterrows():
        current_lat = row["latitude"]
        current_lon = row["longitude"]

        if pd.notna(current_lat) and pd.notna(current_lon):
            continue  # Skip rows with both coordinates

        location = f"{str(row[location_column])}, UK"
        print(f"🌍 Getting lat/lon for [{idx+1}/{len(df)}]: {location}")

        if any(char.isdigit() for char in location):  # Looks like a postcode
            lat, lon = get_lat_long_offline(location)
            if lat and lon:
                print(f"✅ Found in postcode DB: ({lat}, {lon})")
        else:
            lat, lon = get_lat_long(location)
            if lat and lon:
                print(f"✅ Fetched from Nominatim: ({lat}, {lon})")
            else:
                print("⚠️ Location not found")

        if lat and lon:
            df.at[idx, "latitude"] = lat
            df.at[idx, "longitude"] = lon
            updated_rows.append((row["location_id"], lat, lon))

    return df, updated_rows

# ------------------ Main Script ------------------

def main():
    print("🔌 Connecting to database...")
    engine = create_engine(DB_URI)

    with engine.begin() as conn:
        print("📥 Loading locations table...")
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)

        print("📍 Finding missing coordinates...")
        df, updates = add_lat_long_if_missing(df, "location_name")

        if not updates:
            print("✅ No updates needed. All coordinates present.")
            return

        print(f"📤 Updating {len(updates)} rows in the database...")
        for loc_id, lat, lon in updates:
            conn.execute(
                text("""
                    UPDATE locations
                    SET latitude = :lat, longitude = :lon
                    WHERE location_id = :loc_id
                """),
                {'lat': lat, 'lon': lon, 'loc_id': loc_id}
            )

        print("✅ Database update complete.")

if __name__ == "__main__":
    main()
