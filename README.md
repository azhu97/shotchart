# 🏀 NBA Shot Chart Viewer

This Python project visualizes NBA player shot data using the [`nba_api`](https://github.com/swar/nba_api). It supports single-player and side-by-side player comparisons with optional animations, detailed area statistics, and a full half-court rendering.

## 📸 Features

- Search and fetch NBA player shot data by name
- Generate shot charts for individual players
- Compare two players' shot distributions
- Animated shot chart playback (shot-by-shot)
- Auto-calculated statistics by shot area:
  - Restricted Area  
  - In the Paint (Non-RA)  
  - Corner 3s  
  - Above the Break 3  
  - Mid-Range  
  - Others

## 📦 Dependencies

Install required packages with:

```bash
pip install nba_api matplotlib numpy
```

## 🛠 Usage

Run the application:

```bash
python your_script_name.py
```

You will be prompted to:

1. Choose between single or comparison mode
2. Enter season (`e.g. 2023-24`)
3. Choose whether to see an animation
4. Input player name(s)

### 🎬 Animation Example

Animated charts display one shot at a time and include a counter.

### 🗺 Area Breakdown Example

```
Shot Area Stats for Stephen Curry:
Area                     Total
Above the Break 3         285
Restricted Area            40
Mid-Range                  32
...
```

## 🧠 How It Works

- Player data is fetched using `nba_api.stats.static.players`
- Shot data is retrieved via `ShotChartDetail` endpoint
- Matplotlib renders the half-court, overlaid with made/missed shots
- Area classification is done by analyzing `LOC_X` and `LOC_Y` coordinates
- Optionally animates shots in sequence using `FuncAnimation`

## 📁 File Structure

This project is contained in a single Python file and contains:

- Data fetching (`get_player_data`, `fetch_shot_data`)
- Visualization (`plot_shot_chart`, `animate_shot_chart`, etc.)
- Utility (`normalize_season`, `compute_area_stats`)
- A CLI `main()` loop

## ⚠️ Notes

- The API may occasionally return errors or rate-limit; retry if needed.
- Only **regular season** data is retrieved by default.

## ✅ Example Players to Try

- `Stephen Curry`
- `LeBron James`
- `Jayson Tatum`
- `Nikola Jokic`

