from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.animation import FuncAnimation

def get_player_data(name):
    player_list = players.find_players_by_full_name(name)
    if not player_list:
        return None, None
    if len(player_list) > 1:
        print(f"Multiple players found for '{name}':")
        for idx, p in enumerate(player_list, 1):
            print(f"  {idx}. {p['full_name']} (ID: {p['id']})")
        try:
            choice = int(input("Select the player by number: "))
            player = player_list[choice - 1]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return None, None
    else:
        player = player_list[0]
    full_name = f"{player['first_name']} {player['last_name']}"
    return player['id'], full_name

def normalize_season(season):
    # Accept '2021-2022' or '2021-22' and convert to '2021-22'
    match = re.match(r"(\d{4})-(\d{2,4})", season)
    if match:
        start, end = match.groups()
        if len(end) == 4:
            end = end[2:]
        return f"{start}-{end}"
    return season

def fetch_shot_data(player_id, season):
    try:
        response = shotchartdetail.ShotChartDetail(
            team_id=0,
            player_id=player_id,
            season_type_all_star='Regular Season',
            season_nullable=season
        )
        df = response.get_data_frames()[0]
        if 'SHOT_MADE_FLAG' in df.columns:
            print('DEBUG: Unique SHOT_MADE_FLAG values:', df['SHOT_MADE_FLAG'].unique())
        return df
    except Exception as e:
        print(f"Error fetching shot data: {e}")
        return None

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

def get_shot_area(x, y):
    # Standard NBA court area definitions
    if abs(x) <= 40 and y <= 80:
        return 'Restricted Area'
    elif abs(x) <= 80 and 80 < y <= 190:
        return 'In the Paint (Non-RA)'
    elif x < -220 and y <= 140:
        return 'Left Corner 3'
    elif x > 220 and y <= 140:
        return 'Right Corner 3'
    elif abs(x) <= 220 and y > 237.5:
        return 'Above the Break 3'
    elif abs(x) > 220 and y > 140:
        return 'Other 3s'
    elif abs(x) <= 220 and 190 < y < 400:
        return 'Mid-Range'
    else:
        return 'Other'

def compute_area_stats(df):
    if df is None or df.empty:
        return {}
    df = df.copy()
    df['AREA'] = df.apply(lambda row: get_shot_area(row['LOC_X'], row['LOC_Y']), axis=1)
    stats = {}
    for area in df['AREA'].unique():
        area_df = df[df['AREA'] == area]
        total = len(area_df)
        stats[area] = {'total': total}
    return stats

def print_area_stats(stats, player_name):
    print(f"\nShot Area Stats for {player_name}:")
    print(f"{'Area':<25}{'Total':>8}")
    for area, s in stats.items():
        print(f"{area:<25}{s['total']:>8}")

def annotate_area_stats(ax, stats):
    # Place stats at approximate area locations
    area_coords = {
        'Restricted Area': (0, 40),
        'In the Paint (Non-RA)': (0, 130),
        'Left Corner 3': (-230, 30),
        'Right Corner 3': (230, 30),
        'Above the Break 3': (0, 350),
        'Other 3s': (230, 200),
        'Mid-Range': (0, 250),
        'Other': (0, 450)
    }
    for area, coord in area_coords.items():
        if area in stats:
            s = stats[area]
            text = f"{s['total']}"
            ax.text(coord[0], coord[1], text, ha='center', va='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

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

    # Compute and annotate area stats
    stats = compute_area_stats(df)
    annotate_area_stats(ax, stats)
    plt.show()
    print_area_stats(stats, player_name)

def plot_comparison_shot_chart(df1, player_name1, df2, player_name2, season):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    stats1 = compute_area_stats(df1)
    stats2 = compute_area_stats(df2)

    for ax, df, player_name, stats in zip(axes, [df1, df2], [player_name1, player_name2], [stats1, stats2]):
        ax.scatter(df['LOC_X'], df['LOC_Y'],
                   c=df['SHOT_MADE_FLAG'],
                   cmap='coolwarm', alpha=0.7)
        draw_three_point_line(ax)
        draw_paint(ax)
        ax.set_xlim(-250, 250)
        ax.set_ylim(-50, 470)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"{player_name}\n({season})")
        annotate_area_stats(ax, stats)

    plt.suptitle(f"Shot Chart Comparison: {player_name1} vs {player_name2} ({season})")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
    print_area_stats(stats1, player_name1)
    print_area_stats(stats2, player_name2)

def animate_shot_chart(df, player_name, season):
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    draw_three_point_line(ax)
    draw_paint(ax)
    ax.set_xlim(-250, 250)
    ax.set_ylim(-50, 470)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f"{player_name}'s Shot Chart ({season})")
    stats = compute_area_stats(df)
    annotate_area_stats(ax, stats)
    scat = ax.scatter([], [], c=[], cmap='coolwarm', alpha=0.7)
    shots = df.sort_values('GAME_EVENT_ID' if 'GAME_EVENT_ID' in df.columns else df.index)
    x = shots['LOC_X'].values
    y = shots['LOC_Y'].values
    c = shots['SHOT_MADE_FLAG'].values
    total_shots = len(x)
    counter_text = ax.text(0.98, 0.02, '', transform=ax.transAxes, ha='right', va='bottom', fontsize=12, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    def init():
        scat.set_offsets(np.empty((0, 2)))
        scat.set_array(np.array([]))
        counter_text.set_text('')
        return scat, counter_text
    def update(frame):
        offsets = np.column_stack((x[:frame+1], y[:frame+1]))
        scat.set_offsets(offsets)
        scat.set_array(c[:frame+1])
        counter_text.set_text(f"Shot {frame+1} / {total_shots}")
        return scat, counter_text
    anim = FuncAnimation(fig, update, frames=total_shots, init_func=init, blit=True, interval=40, repeat=False)
    plt.show()
    print_area_stats(stats, player_name)

def animate_comparison_shot_chart(df1, player_name1, df2, player_name2, season):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, df, player_name in zip(axes, [df1, df2], [player_name1, player_name2]):
        draw_three_point_line(ax)
        draw_paint(ax)
        ax.set_xlim(-250, 250)
        ax.set_ylim(-50, 470)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"{player_name}\n({season})")
    stats1 = compute_area_stats(df1)
    stats2 = compute_area_stats(df2)
    annotate_area_stats(axes[0], stats1)
    annotate_area_stats(axes[1], stats2)
    shots1 = df1.sort_values('GAME_EVENT_ID' if 'GAME_EVENT_ID' in df1.columns else df1.index)
    shots2 = df2.sort_values('GAME_EVENT_ID' if 'GAME_EVENT_ID' in df2.columns else df2.index)
    x1, y1, c1 = shots1['LOC_X'].values, shots1['LOC_Y'].values, shots1['SHOT_MADE_FLAG'].values
    x2, y2, c2 = shots2['LOC_X'].values, shots2['LOC_Y'].values, shots2['SHOT_MADE_FLAG'].values
    total1, total2 = len(x1), len(x2)
    scat1 = axes[0].scatter([], [], c=[], cmap='coolwarm', alpha=0.7)
    scat2 = axes[1].scatter([], [], c=[], cmap='coolwarm', alpha=0.7)
    counter_text1 = axes[0].text(0.98, 0.02, '', transform=axes[0].transAxes, ha='right', va='bottom', fontsize=12, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    counter_text2 = axes[1].text(0.98, 0.02, '', transform=axes[1].transAxes, ha='right', va='bottom', fontsize=12, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    max_frames = max(total1, total2)
    def init():
        scat1.set_offsets(np.empty((0, 2)))
        scat1.set_array(np.array([]))
        scat2.set_offsets(np.empty((0, 2)))
        scat2.set_array(np.array([]))
        counter_text1.set_text('')
        counter_text2.set_text('')
        return scat1, scat2, counter_text1, counter_text2
    def update(frame):
        if frame < total1:
            offsets1 = np.column_stack((x1[:frame+1], y1[:frame+1]))
            scat1.set_offsets(offsets1)
            scat1.set_array(c1[:frame+1])
            counter_text1.set_text(f"Shot {frame+1} / {total1}")
        else:
            counter_text1.set_text(f"Shot {total1} / {total1}")
        if frame < total2:
            offsets2 = np.column_stack((x2[:frame+1], y2[:frame+1]))
            scat2.set_offsets(offsets2)
            scat2.set_array(c2[:frame+1])
            counter_text2.set_text(f"Shot {frame+1} / {total2}")
        else:
            counter_text2.set_text(f"Shot {total2} / {total2}")
        return scat1, scat2, counter_text1, counter_text2
    anim = FuncAnimation(fig, update, frames=max_frames, init_func=init, blit=True, interval=40, repeat=False)
    plt.show()
    print_area_stats(stats1, player_name1)
    print_area_stats(stats2, player_name2)

def main():
    print("\U0001F3C0 NBA Shot Chart Viewer")
    print("Type 'exit' to quit.\n")

    while True:
        print("Select mode:")
        print("1. Single player shot chart")
        print("2. Compare two players")
        mode = input("Enter 1 or 2: ").strip()
        if mode.lower() in ('exit', 'quit', 'q'):
            print("Goodbye!")
            break
        if mode not in ('1', '2'):
            print("Invalid option. Try again.\n")
            continue

        season = input("Enter season (e.g. 2023-24) [press Enter for default]: ").strip()
        if not season:
            season = '2023-24'
        season = normalize_season(season)

        animate = input("Would you like to see an animation of the shots? (y/n): ").strip().lower() == 'y'

        if mode == '1':
            name = input("Enter NBA player's full name: ")
            if name.lower() in ('exit', 'quit', 'q'):
                print("Goodbye!")
                break
            player_id, full_name = get_player_data(name)
            if not player_id:
                print("\u274C Player not found. Try again.\n")
                continue
            print(f"Fetching shot data for {full_name} ({season})...")
            df = fetch_shot_data(player_id, season)
            if df is None or df.empty:
                print("No shot data found for this player or an error occurred.\n")
                continue
            print(f"Displaying {full_name}'s shot chart...")
            if animate:
                animate_shot_chart(df, full_name, season)
            else:
                plot_shot_chart(df, full_name, season)
            print()
        else:
            name1 = input("Enter first NBA player's full name: ")
            if name1.lower() in ('exit', 'quit', 'q'):
                print("Goodbye!")
                break
            player_id1, full_name1 = get_player_data(name1)
            if not player_id1:
                print("\u274C First player not found. Try again.\n")
                continue
            name2 = input("Enter second NBA player's full name: ")
            if name2.lower() in ('exit', 'quit', 'q'):
                print("Goodbye!")
                break
            player_id2, full_name2 = get_player_data(name2)
            if not player_id2:
                print("\u274C Second player not found. Try again.\n")
                continue
            print(f"Fetching shot data for {full_name1} and {full_name2} ({season})...")
            df1 = fetch_shot_data(player_id1, season)
            df2 = fetch_shot_data(player_id2, season)
            if df1 is None or df1.empty or df2 is None or df2.empty:
                print("No shot data found for one or both players or an error occurred.\n")
                continue
            print(f"Displaying shot chart comparison: {full_name1} vs {full_name2}...")
            if animate:
                animate_comparison_shot_chart(df1, full_name1, df2, full_name2, season)
            else:
                plot_comparison_shot_chart(df1, full_name1, df2, full_name2, season)
            print()

if __name__ == "__main__":
    main()
