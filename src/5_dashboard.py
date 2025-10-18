import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px


# Load and Combine Data

@st.cache_data
def load_data():
    conn = sqlite3.connect('db/batting_pitching.db')
    tables = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table';", conn)
    table_names = tables['name'].tolist()

    dfs = []
    for t in table_names:
        if not (t.startswith('batting_') or t.startswith('pitching_')):
            continue

        parts = t.split('_')
        category = parts[0]  # batting or pitching
        year = parts[1] if len(parts) > 1 else 'Unknown'
        league = parts[2] if len(parts) > 2 else 'Unknown'

        try:
            temp_df = pd.read_sql_query(
                f"SELECT *, '{year}' AS year, '{league}' AS league, '{category}' AS category FROM {t}", conn)
            dfs.append(temp_df)
        except Exception as e:
            print(f"Skipping {t}: {e}")

    conn.close()
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        # Ensure numeric conversion for Value column
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        return df
    else:
        return pd.DataFrame()


df = load_data()


# Streamlit UI
st.set_page_config(page_title="MLB Stats Dashboard", layout="wide")
st.title("⚾ MLB Batting & Pitching Dashboard")
st.write("Explore MLB data interactively by league, year, and statistic type.")

if df.empty:
    st.error("No data found. Please check your database connection and tables.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
category = st.sidebar.radio("Select Category:", ["batting", "pitching"])
year = st.sidebar.selectbox("Select Year:", sorted(df['year'].unique()))
league = st.sidebar.selectbox("Select League:", sorted(df['league'].unique()))

filtered_df = df[(df['category'] == category) &
                 (df['year'] == year) &
                 (df['league'] == league)]

# Handle missing or invalid data
if filtered_df.empty:
    st.warning("No data available for this selection.")
    st.stop()


# Visualization 1: Top Players by Value
st.subheader(f"Top Players ({category.title()}) in {league} {year}")
top_players = filtered_df.nlargest(10, 'Value')

fig1 = px.bar(top_players, x='Name', y='Value', color='Team',
              title=f"Top Players - {category.title()} ({league} {year})",
              labels={'Value': 'Stat Value', 'Name': 'Player'})
st.plotly_chart(fig1, use_container_width=True)


# Visualization 2: League Average by Statistic
st.subheader(f"Average Value per Statistic in {league} {year}")
league_avg = filtered_df.groupby('Statistic')['Value'].mean().reset_index()
fig2 = px.bar(league_avg, x='Statistic', y='Value', color='Statistic',
              title=f"Average {category.title()} Stats in {league} {year}")
st.plotly_chart(fig2, use_container_width=True)


# Visualization 3: League Comparison Over Time
st.subheader("League Comparison Over 2023–2024")

# Select which statistic to compare between AL and NL
stat_choice = st.selectbox(
    "Select Statistic for Comparison:",
    sorted(df['Statistic'].dropna().unique())
)

# Filter only that statistic and category
league_trend = df[(df['Statistic'] == stat_choice) &
                  (df['category'] == category)]

# Group by league and year to calculate mean values
league_trend_summary = league_trend.groupby(
    ['year', 'league']
)['Value'].mean().reset_index()

if league_trend_summary.empty:
    st.warning("No data available for this statistic.")
else:
    fig3 = px.line(
        league_trend_summary,
        x='year',
        y='Value',
        color='league',
        markers=True,
        title=f"{category.title()} – {stat_choice} Trend (AL vs NL)",
        labels={'Value': 'Average Value', 'year': 'Year'}
    )
    fig3.update_xaxes(tickvals=[2023, 2024])
    st.plotly_chart(fig3, use_container_width=True)
