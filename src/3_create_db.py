import sqlite3
import pandas as pd
import os

input_folder = "data/cleaned"

# Connect to SQLite
with sqlite3.connect("db/batting_pitching.db") as conn:
    cursor = conn.cursor()

    # Loop through all CSV files in cleaned folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".csv"):
            table_name = file_name.replace("cleaned_", "").replace(".csv", "")
            file_path = os.path.join(input_folder, file_name)
            print(f"Importing {file_name} as table {table_name}...")

            try:
                # Load CSV
                df = pd.read_csv(file_path)

                # Import DataFrame to SQLite
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                print(f"✅ Imported {table_name} successfully.")

            except Exception as e:
                print(f"Failed to import {file_name}: {e}")

print("All CSV files imported into SQLite database successfully!")
