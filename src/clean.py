import pandas as pd
import os

# Input and output folders
input_folder = "data"
output_folder = "data/cleaned"

# Loop through all CSV files in /data
for file_name in os.listdir(input_folder):
    if file_name.endswith(".csv"):
        file_path = os.path.join(input_folder, file_name)
        print(f"Cleaning {file_name}...")

        # Load CSV
        df = pd.read_csv(file_path)

        # Remove duplicate header rows
        df = df[df["Statistic"] != "Statistic"]

        # Drop duplicate rows
        df = df.drop_duplicates()

        # Drop 'Top 25' column if it exists
        if "Top 25" in df.columns:
            df = df.drop(columns=["Top 25"])

        # Rename '#' to 'Value'
        df = df.rename(columns={"#": "Value"})

        # Convert 'Value' to numeric, handle errors (like '.330' or '2.39')
        df["Value"] = (df["Value"].astype(str).str.replace(",", "", regex=False).str.strip())
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

        # Reset index
        df = df.reset_index(drop=True)

        # Save cleaned version
        output_path = os.path.join(output_folder, f"cleaned_{file_name}")
        df.to_csv(output_path, index=False)
        print(f"Saved cleaned file to {output_path}")

print("✅ All files cleaned successfully!")
