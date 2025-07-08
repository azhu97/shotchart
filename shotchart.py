from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
import matplotlib.pyplot as plt
import numpy as np

def get_player_data(name):
    player_list = players.find_players_by_full_name(name)
    if not player_list:
        return None, None
    player = player_list[0]
    full_name = f"{player['first_name']} {player['last_name']}"
    return player['id'], full_name

def fetch_shot_data(player_id, season):
    response = shotchartdetail.ShotChartDetail(
        team_id=0,
        player_id=player_id,
        season_type_all_star='Regular Season',
        season_nullable=season
    )
    return response.get_data_frames()[0]

def draw_three_point_line(ax):
    radius = 237.5
    arc_angles = np.linspace(-np.pi, np.pi, 500)

    x_arc = radius * np.cos(arc_angles)
    y_arc = radius * np.sin(arc_angles)

    mask = (x_arc >= -220) & (x_arc <= 220) & (y_arc >= 0)
    ax.plot(x_arc[mask], y_arc[mask], color='black', linewidth=2)

    ax.plot([-220, -220], [-47.5, 89], color='black', linewidth=2)
    ax.plot([220, 220], [-47.5, 89], color='black', linewidth=2)

def draw_paint(ax):
    paint_width = 160
    paint_height = 140  # Adjusted so it stays below arc

    ax.plot([-paint_width/2, -paint_width/2], [-47.5, paint_height], color='black', linewidth=2)
    ax.plot([paint_width/2, paint_width/2], [-47.5, paint_height], color='black', linewidth=2)
    ax.plot([-paint_width/2, paint_width/2], [paint_height, paint_height], color='black', linewidth=2)

    # Free throw circle (top half)
    circle_radius = 72
    theta = np.linspace(0, np.pi, 100)
    x = circle_radius * np.cos(theta)
    y = circle_radius * np.sin(theta) + paint_height
    ax.plot(x, y, color='black', linewidth=2)

    # Free throw circle (bottom half, dashed)
    theta = np.linspace(-np.pi, 0, 100)
    x = circle_radius * np.cos(theta)
    y = circle_radius * np.sin(theta) + paint_height
    ax.plot(x, y, color='black', linestyle='dashed', linewidth=1)

    # Backboard
    ax.plot([-30, 30], [-7.5, -7.5], color='black', linewidth=2)

    # Rim
    rim = plt.Circle((0, 0), 7.5, linewidth=1.5, color='orange', fill=False)
    ax.add_patch(rim)

def plot_shot_chart(df, player_name, season):
    fig, ax = plt.subplots(figsize=(6.5, 5.5))

    ax.scatter(df['LOC_X'], df['LOC_Y'],
               c=df['SHOT_MADE_FLAG'],
               cmap='coolwarm', alpha=0.7)

    draw_three_point_line(ax)
    draw_paint(ax)

    ax.set_xlim(-250, 250)
    ax.set_ylim(-50, 470)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f"{player_name}'s Shot Chart ({season})")

    plt.show()

def main():
    print("🏀 NBA Shot Chart Viewer")
    print("Type 'exit' to quit.\n")

    while True:
        name = input("Enter NBA player's full name: ")
        if name.lower() in ('exit', 'quit', 'q'):
            print("Goodbye!")
            break

        player_id, full_name = get_player_data(name)
        if not player_id:
            print("❌ Player not found. Try again.\n")
            continue

        season = input("Enter season (e.g. 2023-24) [press Enter for default]: ").strip()
        if not season:
            season = '2023-24'

        print(f"Fetching shot data for {full_name} ({season})...")
        df = fetch_shot_data(player_id, season)

        if df.empty:
            print("No shot data found for this player.\n")
            continue

        print(f"Displaying {full_name}'s shot chart...")
        plot_shot_chart(df, full_name, season)
        print()

if __name__ == "__main__":
    main()
