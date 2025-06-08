import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import requests
import time
import re
import pickle
import pycountry
import streamlit as st

def show_plot(fig):
    try:
        # Only works when running inside Streamlit
        import streamlit as st
        st.pyplot(fig)
    except:
        # Fallback to standard display
        fig.show() if hasattr(fig, "show") else plt.show()

def download_monthly_games(username, year, months, save_folder):
    os.makedirs(save_folder, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}  # <- Add this line
    for month in months:
        file_name = f"{year}-{month:02d}.json"
        file_path = os.path.join(save_folder, file_name)
        if os.path.exists(file_path):
            print(f"🟡 Already exists: {file_name}")
            continue
        url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
        res = requests.get(url, headers=headers)  # <- Use headers here
        if res.status_code == 200:
            with open(file_path, "w") as f:
                json.dump(res.json(), f)
            print(f"✅ Downloaded: {file_name}")
        else:
            print(f"❌ Failed to fetch: {file_name} (status {res.status_code})")
        time.sleep(0.2)


def get_country(username):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(f"https://api.chess.com/pub/player/{username}", headers=headers, timeout=5)
        if res.status_code == 200:
            player_data = res.json()
            if "country" in player_data:
                return player_data["country"].split("/")[-1]
        return "unknown"
    except Exception as e:
        print(f"Error fetching country for {username}: {e}")
        return "unknown"

def convert_country_code(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        return "Unknown"

def analyze_chess_games_in_folder(folder_path, your_username, year, months, clear_cache=False):
    all_games = []
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            print("Reading:", file)
            with open(os.path.join(folder_path, file), "r") as f:
                data = json.load(f)
                for game in data.get("games", []):
                  # if game.get("time_class") != "rapid":
                  #      continue

                    end_time = pd.to_datetime(game["end_time"], unit='s')

                    white = game.get("white", {}).get("username", "").lower()
                    black = game.get("black", {}).get("username", "").lower()

                    if your_username.lower() == white:
                        player_color = "white"
                        opponent = black
                    elif your_username.lower() == black:
                        player_color = "black"
                        opponent = white
                    else:
                        continue

                    result = game[player_color].get("result", "unknown")

                    opponent_rating = (
                        game.get("white", {}).get("rating")
                        if opponent == game.get("white", {}).get("username", "").lower()
                        else game.get("black", {}).get("rating")
                    )

                    eco = game.get("eco", "")
                    opening_name = game.get("opening", "Unknown")
                    all_games.append({
                        "datetime": end_time,
                        "hour": end_time.hour,
                        "weekday": end_time.day_name(),
                        "month": end_time.month_name(),
                        "opponent": opponent,
                        "result": result,
                        "player_color": player_color,
                    "opening": f"{eco} {opening_name}".strip(),
                    "opponent_rating": opponent_rating
                    })

    df = pd.DataFrame(all_games)
    df = df[df["datetime"].dt.year == year]
    df = df[df["datetime"].dt.month.isin(months)]

    print(f"Total games analyzed: {len(df)}")

    unique_opponents = df["opponent"].dropna().unique()
    print(f"Fetching countries for {len(unique_opponents)} unique opponents...")

    cache_file = "country_cache.pkl"
    if not clear_cache and os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            opponent_country_map = pickle.load(f)
    else:
        opponent_country_map = {}

    for i, opponent in enumerate(unique_opponents):
        if opponent in opponent_country_map:
            continue
        if i % 10 == 0:
            print(f"Progress: {i}/{len(unique_opponents)}")
        opponent_country_map[opponent] = get_country(opponent)
        #time.sleep(0.02)  # faster and safe

    with open(cache_file, "wb") as f:
        pickle.dump(opponent_country_map, f)

    df["country_code"] = df["opponent"].map(opponent_country_map)
    df["country"] = df["country_code"].apply(convert_country_code)
    df["win"] = df["result"].apply(lambda x: 1 if x == "win" else 0)

    return df

def simplify(name):
    name = name.split("/")[-1].replace("-", " ").replace("Unknown", "").strip()
    name = re.sub(r"\d+\.\S+", "", name)
    simple = " ".join(name.split()[:3]).strip()
    return simple if simple else "Other"


def render_all_graphs(df):
    # Required preprocessing
    draw_results = ["draw", "agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient"]
    df["outcome"] = df["result"].apply(
        lambda x: "Win" if x == "win" else "Draw" if x in draw_results else "Loss"
    )

    # Graph 1: Pie chart
    ordered_outcomes = ["Win", "Draw", "Loss"]
    outcome_counts = df["outcome"].value_counts()
    outcome_counts = outcome_counts.reindex(ordered_outcomes)
    results, ax1 = plt.subplots(figsize=(6, 6))
    ax1.pie(outcome_counts.values, labels=outcome_counts.index, autopct="%1.1f%%",
            colors=["#4caf50", "#ffc107", "#f44336"],
            startangle=185.3,
            counterclock=False 
    )
    ax1.set_title("Win vs Draw vs Loss")
    show_plot(results)

    # Graph 2 & 3: Top and bottom 3 openings
    opening_played = df["opening"].value_counts()
    opening_won = df[df["win"] == 1]["opening"].value_counts().reindex(opening_played.index, fill_value=0)
    win_percentage = (opening_won / opening_played * 100).round(1)

    full_opening_summary = pd.DataFrame({
        "Games Played": opening_played,
        "Wins": opening_won,
        "Win %": win_percentage
    })

    filtered = full_opening_summary[full_opening_summary["Games Played"] > 10].sort_values("Win %", ascending=False)
    top_openings = filtered.head(3).copy()
    bottom_openings = filtered.tail(3).copy()

    top_openings.index = top_openings.index.to_series().apply(simplify)
    bottom_openings.index = bottom_openings.index.to_series().apply(simplify)

    for title, data, color in [
        ("Top 3 Openings by Win %", top_openings, "green"),
        ("Bottom 3 Openings by Win %", bottom_openings, "red")
    ]:
        opening, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(data.index, data["Win %"], color=color)
        ax.set_title(title)
        ax.set_ylabel("Win %")
        for bar, (name, row) in zip(bars, data.iterrows()):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{int(row['Wins'])}/{int(row['Games Played'])}\n({row['Win %']}%)",
                    ha="center", fontsize=9)
        plt.xticks(rotation=0)
        plt.ylim(0, 100)
        plt.tight_layout()
        show_plot(opening)

    # Graph 4: Win Rate By Month
    month_stats = df.groupby("month").agg(
        total_games=("win", "count"),
        wins=("win", "sum"))
    month_stats["win_rate"] = month_stats["wins"] / month_stats["total_games"]
    month_order = ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"]
    month_stats = month_stats.reindex(month_order).dropna()

    month = plt.figure(figsize=(10, 5))
    bars = plt.bar(month_stats.index, month_stats["win_rate"], color="teal")
    plt.title("Win Rate by Month")
    plt.ylabel("Win Rate")
    plt.xlabel("Month")
    for bar, wins, games in zip(bars, month_stats["wins"], month_stats["total_games"]):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f"{wins}/{games}\n({bar.get_height()*100:.1f}%)", ha="center", fontsize=9)
    plt.ylim(0, 1.1)
    plt.tight_layout()
    show_plot(month)

    # Graph 5: Top Opponents
    opponent_stats = df.groupby("opponent").agg(
        avg_rating=("opponent_rating", "mean"),
        games=("win", "count"),
        wins=("win", "sum")).reset_index()
    opponent_stats["win_rate"] = opponent_stats["wins"] / opponent_stats["games"]
    top_opponents = opponent_stats.sort_values("games", ascending=False).head(5)
    top_opponents = top_opponents.sort_values("win_rate", ascending=False)

    opponents = plt.figure(figsize=(10, 5))
    bars = plt.bar(top_opponents["opponent"], top_opponents["win_rate"], color="skyblue")
    plt.title("Win Rate vs Top 5 Opponents")
    plt.ylabel("Win Rate")
    plt.xlabel("Opponent")
    for bar, wins, games in zip(bars, top_opponents["wins"], top_opponents["games"]):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                 f"{wins}/{games}\n({bar.get_height()*100:.1f}%)", ha="center", fontsize=9)
    plt.ylim(0, 1.1)
    plt.tight_layout()
    show_plot(opponents)

    # Graph 6: By Hour
    hourly_stats = df.groupby("hour").agg(total_games=("win", "count"), wins=("win", "sum"))
    hourly_stats["win_percent"] = (hourly_stats["wins"] / hourly_stats["total_games"]) * 100

    hour, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(hourly_stats.index, hourly_stats["win_percent"], color="orange")
    ax.set_title("Win Rate by Hour")
    ax.set_ylabel("Win Rate (%)")
    ax.set_xlabel("Hour")
    for bar, (name, row) in zip(bars, hourly_stats.iterrows()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{int(row['wins'])}/{int(row['total_games'])}\n({row['win_percent']:.1f}%)",
                ha="center", fontsize=9)
    ax.set_ylim(0, 100)
    hour.tight_layout()
    show_plot(hour)

    # Graphs 7 & 8: Country stats
    country_stats = df.groupby("country").agg(
        total_games=("win", "count"),
        wins=("win", "sum")).sort_values("total_games", ascending=False)
    country_stats["win_rate"] = (country_stats["wins"] / country_stats["total_games"] * 100).round(1)
    filtered = country_stats[country_stats["total_games"] > 9]

    for title, data, color in [
        ("Top 5 Countries by Win Rate", filtered.sort_values("win_rate", ascending=False).head(5), "green"),
        ("Bottom 5 Countries by Win Rate", filtered.sort_values("win_rate", ascending=True).head(5), "red")
    ]:
        country, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(data.index, data["win_rate"], color=color)
        ax.set_title(f"{title} (min 10 games)")
        ax.set_ylabel("Win Rate (%)")
        ax.set_xlabel("Country")
        ax.set_xticklabels(data.index, rotation=45)
        for bar, (name, row) in zip(bars, data.iterrows()):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{int(row['wins'])}/{int(row['total_games'])}\n({row['win_rate']}%)",
                    ha="center", fontsize=9)
        ax.set_ylim(0, 100)
        country.tight_layout()
        show_plot(country)

def run_analysis(username, year, months, clear_cache=False):
    folder = f"chess_games/{username.lower()}"
    download_monthly_games(username, year, months, folder)
    df = analyze_chess_games_in_folder(folder, username, year, months, clear_cache)
    df = df.sort_values("datetime")
    df["month"] = df["datetime"].dt.strftime("%B")
    render_all_graphs(df)

    # Track streak
    current = 0
    best_streak = 0
    best_month = ""
    for _, row in df.iterrows():
        if row["win"] == 1:
            current += 1
            if current > best_streak:
                best_streak = current
                best_month = row["month"]
        else:
            current = 0

    print(f"\nLongest Win Streak: {best_streak} games")
    print(f"It happened in: {best_month}")

    df.to_csv(f"{username.lower()}_full_chess_analysis.csv", index=False)
    print("\nSaved to full_chess_analysis.csv in project folder.")

    draw_results = ["draw", "agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient"]
    df["outcome"] = df["result"].apply(
        lambda x: "Win" if x == "win" else "Draw" if x in draw_results else "Loss"
    )

    print("\n--- Overall Summary ---")
    print(f"Total Games: {len(df)}")
    print(f"Wins: {df['win'].sum()}")
    print(f"Draws: {sum(df['outcome'] == 'Draw')}")
    print(f"Losses: {sum(df['outcome'] == 'Loss')}")
    print(df["result"].value_counts())


if __name__ == "__main__":
    username = input("Enter your Chess.com username: ").strip()
    year = int(input("Enter the year (e.g., 2025): ").strip())
    months = list(map(int, input("Enter months as comma-separated numbers (e.g., 1,2,3): ").split(",")))
    run_analysis(username, year, months)
