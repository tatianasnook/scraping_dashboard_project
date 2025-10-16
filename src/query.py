import sqlite3


def get_connection():
    try:
        return sqlite3.connect("db/batting_pitching.db")
    except sqlite3.Error as e:
        print(f"Error connecting to DB: {e}")
        return None

def show_menu():
    print("\nChoose a query:")
    print("1. Top home run hitters in a league by year")
    print("2. Compare batting statistics between 2023 and 2024")
    print("3. League information summary")
    print("4. Exit")

def home_run_hitter_by_year(conn):
    try:
        year = input("Enter year (2023 or 2024): ").strip()
        league = input("Enter league (AL or NL): ").strip().upper()
        table_name = f"batting_{year}_{league}"

        cursor = conn.execute(f"""
            SELECT Name, Team, Value
            FROM {table_name}
            WHERE Statistic = 'Home Runs'
            ORDER BY Value DESC
            LIMIT 5
        """)
        results = cursor.fetchall()

        if results:
            print(f"\nTop 5 home run hitters in {league} ({year}):")
            for row in results:
                print(f"{row[0]} - {row[1]}: {row[2]}")
        else:
            print("No results found.")
    except Exception as e:
        print(f"Error: {e}")


def compare_batting_years(conn):
    try:
        league = input("Enter league (AL or NL): ").strip().upper()
        table_2023 = f"batting_2023_{league}"
        table_2024 = f"batting_2024_{league}"

        cursor = conn.execute(f"""
            SELECT 
                b23.Statistic,
                ROUND(AVG(b23.Value), 2) AS Avg_2023,
                ROUND(AVG(b24.Value), 2) AS Avg_2024,
                ROUND(AVG(b24.Value) - AVG(b23.Value), 2) AS Change
            FROM {table_2023} AS b23
            JOIN {table_2024} AS b24
              ON b23.Statistic = b24.Statistic
            WHERE b23.Statistic IN ('Home Runs', 'Batting Average', 'RBI')
            GROUP BY b23.Statistic
            ORDER BY Change DESC;
        """)

        results = cursor.fetchall()
        if results:
            print(f"\nBatting Stat Changes ({league}): 2023 → 2024")
            print("-" * 60)
            print(
                f"{'Statistic':20} | {'2023 Avg':10} | {'2024 Avg':10} | {'Change':10}")
            print("-" * 60)
            for row in results:
                stat, avg23, avg24, change = row
                print(f"{stat:20} | {avg23:<10} | {avg24:<10} | {change:<10}")
        else:
            print("No comparable batting data found between 2023 and 2024.")
    except Exception as e:
        print(f"Error: {e}")


def league_info(conn):
    try:
        year = input("Enter year (2023 or 2024): ").strip()
        league = input("Enter league (AL or NL): ").strip().upper()
        table_name = f"batting_{year}_{league}"

        cursor = conn.execute(f"""
            SELECT Team,
                   COUNT(DISTINCT Name) AS Players,
                   ROUND(AVG(Value), 2) AS Avg_Stat
            FROM {table_name}
            WHERE Statistic = 'Home Runs'
            GROUP BY Team
            ORDER BY Avg_Stat DESC
            LIMIT 10
        """)
        results = cursor.fetchall()

        if results:
            print(
                f"\n{league} League Summary ({year}) — Top Teams by Avg Home Runs:")
            for row in results:
                print(f"{row[0]} | Players: {row[1]} | Avg HR: {row[2]}")
        else:
            print("No data found.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    conn = get_connection()
    if not conn:
        return

    try:
        while True:
            show_menu()
            choice = input("Choice: ").strip()

            if choice == "1":
                home_run_hitter_by_year(conn)
            elif choice == "2":
                compare_batting_years(conn)
            elif choice == "3":
                league_info(conn)
            elif choice == "4":
                print("Goodbye.")
                break
            else:
                print("Invalid option. Try again.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
