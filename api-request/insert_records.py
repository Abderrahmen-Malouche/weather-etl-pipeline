from api_request import mock_fetch_data,fetch_data
import psycopg2
from datetime import datetime

def clean_weather_data(raw_json):
    print("Cleaning weather data...")

    try:
        weather = raw_json.get("current", {})
        location = raw_json.get("location", {})

        # ----- 1. Extract & normalize fields -----
        city = location.get("name", "").strip().title() if location.get("name") else None
        temp = weather.get("temperature")
        desc = weather.get("weather_descriptions", ["Unknown"])[0].strip() if weather.get("weather_descriptions") else None
        wind = weather.get("wind_speed")
        time_str = location.get("localtime")
        utc_offset = location.get("utc_offset")

        # ----- 2. Convert numeric fields -----
        try:
            temp = float(temp) if temp is not None else None
        except:
            temp = None

        try:
            wind = float(wind) if wind is not None else None
        except:
            wind = None

        # ----- 3. Parse timestamp properly -----
        try:
           time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        except:
           time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S") if ":" in time_str[14:] else None

        # ----- 4. Basic validation rules -----
        if not city:
            print("⚠️ Cleaning failed: missing city.")
            return None

        if temp is None or not (-90 <= temp <= 60):  # Earth temperature range
            print(f"⚠️ Cleaning warning: Invalid temperature {temp}, skipping row.")
            return None

        if time is None:
            print("⚠️ Cleaning failed: invalid timestamp.")
            return None

        # ----- 5. Build cleaned, validated row -----
        cleaned = {
            "city": city,
            "temperature": temp,
            "weather_description": desc or "Unknown",
            "wind_speed": wind if wind is not None else 0.0,
            "time": time,
            "utc_offset": utc_offset or "+00:00"
        }

        print("✅ Cleaning complete, data validated.")
        return cleaned

    except Exception as e:
        print(f"❌ Error while cleaning data: {e}")
        return None

def connect_to_db():
   print("Connecting to the PostgreSQL database...")
   try:
        conn= psycopg2.connect(
            host="db",
            port=5432,
            dbname="db",
            user="db_user",
            password="db_password"
        )
        print(conn)
        return conn
   except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise
    
def create_table(conn):
    print("Creating weather_data table if not exists...")
    try:
        create_table_query="""
        CREATE SCHEMA IF NOT EXISTS dev;
        CREATE TABLE IF NOT EXISTS dev.raw_weather_data (
        id SERIAL PRIMARY KEY,
        city TEXT,
        temperature FLOAT,
        weather_description TEXT,
        wind_speed FLOAT,
        time TIMESTAMP,
        inserted_at TIMESTAMP DEFAULT NOW(),
        utc_offset TEXT
    );
    """
        cursor=conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        print("Table created successfully or already exists.")
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
        raise




def insert_records(conn, row):
    print("Inserting weather data into the database...")

    insert_query = """
    INSERT INTO dev.raw_weather_data (city, temperature, weather_description, wind_speed, time, utc_offset)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    try:
        cursor = conn.cursor()
        cursor.execute(insert_query, (
            row["city"],
            row["temperature"],
            row["weather_description"],
            row["wind_speed"],
            row["time"],
            row["utc_offset"]
        ))
        conn.commit()
        cursor.close()
        print("✅ Cleaned data inserted (or skipped if duplicate).")

    except psycopg2.Error as e:
        print(f"Error inserting weather data: {e}")
        raise
    
def main():
    try:
        data=fetch_data()
        if data is None:
            print("No data fetched, exiting.")
            return
        cleaned_data=clean_weather_data(data)
        if cleaned_data is None:
            print("Data cleaning failed or data invalid, exiting.")
            return
        conn=connect_to_db()
        create_table(conn)
        insert_records(conn, cleaned_data)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if "conn" in locals():
            conn.close()
            print("Database connection closed.")
        
