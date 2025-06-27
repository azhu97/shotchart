from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
import matplotlib.pyplot as plt
import numpy as np

def get_player_id(name):
    player_list = players.find_players_by_full_name(name)
    if not player_list:
        return None
    return player_list[0]['id']

def fetch_shot_data(player_id):
    response = shotchartdetail.ShotChartDetail(
        team_id=0,
        player_id=player_id,
        season_type_all_star='Regular Season',
        season_nullable='2023-24'
    )
    return response.get_data_frames()[0]

def plot_shot_chart(df, player_name):
    plt.figure(figsize=(6.5, 5.5))

    # Plot made/missed shots
    plt.scatter(df['LOC_X'], df['LOC_Y'], c=df['SHOT_MADE_FLAG'], cmap='coolwarm', alpha=0.7)

    # Draw 3-point arc
    arc = np.linspace(-np.pi / 2, np.pi / 2, 300)
    radius = 237.5  # 23.75 feet * 12 inches
    x_arc = radius * np.cos(arc)
    y_arc = radius * np.sin(arc)

    plt.plot(x_arc, y_arc, color='black')

    # Draw corner 3 lines
    plt.plot([-220, -220], [-47.5, 92], color='black')  # left corner
    plt.plot([220, 220], [-47.5, 92], color='black')   # right corner

    plt.title(f"{player_name}'s Shot Chart (2023-24)")
    plt.xlim(-250, 250)
    plt.ylim(-50, 470)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.axis(False)
    plt.show()

def main():
    print("🏀 NBA Shot Chart Viewer")
    print("'exit' to quit.\n")

    while True:
        name = input("Enter NBA player's full name: ")
        if name.lower() in ('exit', 'quit', 'q'):
            print("Goodbye!")
            break

        player_id = get_player_id(name)
        if not player_id:
            print("❌ Player not found. Try again.\n")
            continue

        print("Fetching shot data...")
        df = fetch_shot_data(player_id)

        if df.empty:
            print("No shot data found for this player.\n")
            continue

        print(f"Displaying {name}'s shot chart...")
        plot_shot_chart(df, name)
        print()  # Add blank line before next prompt

if __name__ == "__main__":
    main()