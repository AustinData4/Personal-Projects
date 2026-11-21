import os
import pandas as pd
RAW = "/Users/austincharbonneau/GitHub/AustinData4/nfl_coverage_analyzer/data/raw"
OUT = "/Users/austincharbonneau/GitHub/AustinData4/nfl_coverage_analyzer/data"
os.makedirs(OUT, exist_ok=True)
fl = []
for s in range(2022, 2026):
    fl.append(pd.read_parquet(os.path.join(RAW, "ftn_%d.parquet" % s)))
ftn = pd.concat(fl, ignore_index=True)
print("ftn:", ftn.shape)
print("blitz rate (n_blitzers>0):", (ftn["n_blitzers"] > 0).mean().round(4))
print("rushers dist:", ftn["n_pass_rushers"].value_counts().head(6).to_dict())
# join coverage-relevant context from PBP
pl = []
for s in range(2022, 2026):
    df = pd.read_parquet(os.path.join(RAW, "pbp_%d.parquet" % s))
    keep = [c for c in ["game_id", "play_id", "season", "week", "posteam",
                        "defteam", "down", "ydstogo", "yardline_100",
                        "shotgun", "play_type", "epa", "success",
                        "pass_length", "pass_location"] if c in df.columns]
    pl.append(df[keep])
pbp = pd.concat(pl, ignore_index=True)
print("pbp ctx:", pbp.shape)
pbp["nflverse_play_id"] = pbp["play_id"]
ftn["nflverse_play_id"] = ftn["nflverse_play_id"].astype(int)
m = ftn.merge(pbp, left_on=["nflverse_game_id", "nflverse_play_id"],
              right_on=["game_id", "nflverse_play_id"], how="left")
print("matched:", m["posteam"].notna().mean().round(3), len(m))
m.to_parquet(os.path.join(OUT, "coverage_plays.parquet"), index=False)
print("saved")
