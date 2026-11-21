import os
import pandas as pd
RAW = "/Users/austincharbonneau/GitHub/AustinData4/nfl_4th_down/data/raw"
OUT = "/Users/austincharbonneau/GitHub/AustinData4/nfl_4th_down/data"
os.makedirs(OUT, exist_ok=True)
frames = []
for s in range(2016, 2026):
    df = pd.read_parquet(os.path.join(RAW, "pbp_%d.parquet" % s))
    keep = [c for c in ["game_id", "season", "week", "posteam", "defteam",
                        "home_team", "away_team", "qtr", "down", "ydstogo",
                        "yardline_100", "goal_to_go", "play_type",
                        "score_differential", "game_seconds_remaining",
                        "posteam_timeouts_remaining",
                        "defteam_timeouts_remaining", "wp", "epa", "success",
                        "fourth_down_converted", "fourth_down_failed",
                        "field_goal_result", "punt_attempt"] if c in df.columns]
    frames.append(df[[c for c in keep]][df["down"] == 4])
    print("4th", s, (df["down"] == 4).sum())
fd = pd.concat(frames, ignore_index=True)
print("cols:", [c for c in fd.columns])
print("play types:", fd["play_type"].value_counts().to_dict())
fd.to_parquet(os.path.join(OUT, "fourth_all.parquet"), index=False)
print("saved", len(fd))
