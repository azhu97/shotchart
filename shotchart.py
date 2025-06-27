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

def draw_three_point_line(ax):
    radius = 237.5
    arc_angles = np.linspace(-np.pi, np.pi, 500)  # Full circle, higher resolution

    x_arc = radius * np.cos(arc_angles)
    y_arc = radius * np.sin(arc_angles)

    # Keep only arc segment between x = -220 and 220 AND y >= 0 (top half only)
    mask = (x_arc >= -220) & (x_arc <= 220) & (y_arc >= 0)
    ax.plot(x_arc[mask], y_arc[mask], color='black', linewidth=2)

    # Draw corner 3-point lines from baseline (-47.5") to where arc begins (~89")
    ax.plot([-220, -220], [-47.5, 89], color='black', linewidth=2)
    ax.plot([220, 220], [-47.5, 89], color='black', linewidth=2)


def plot_shot_chart(df, player_name):
    fig, ax = plt.subplots(figsize=(6.5, 5.5))

    # Plot shots: 1 = made (blue), 0 = missed (red)
    scatter = ax.scatter(df['LOC_X'], df['LOC_Y'],
                         c=df['SHOT_MADE_FLAG'],
                         cmap='coolwarm', alpha=0.7)

    draw_three_point_line(ax)

    ax.set_xlim(-250, 250)
    ax.set_ylim(-50, 470)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f"{player_name.title()}'s Shot Chart (2023-24)")

    plt.show()

def main():
    print("🏀 NBA Shot Chart Viewer")
    print("Type 'exit' to quit.\n")

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

        print(f"Displaying {name.title()}'s shot chart...")
        plot_shot_chart(df, name)
        print()

if __name__ == "__main__":
    main()
