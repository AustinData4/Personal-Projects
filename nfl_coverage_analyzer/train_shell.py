import os, json
import numpy as np, pandas as pd, joblib
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
D = "/Users/austincharbonneau/GitHub/AustinData4/nfl_coverage_analyzer/data"
M = "/Users/austincharbonneau/GitHub/AustinData4/nfl_coverage_analyzer/models"
os.makedirs(M, exist_ok=True)
m = pd.read_parquet(os.path.join(D, "coverage_plays.parquet"))
# restrict to real scrimmage plays
m = m[m["play_type"].isin(["pass", "run"]) & m["down"].notna()].copy()
m["rushers"] = m["n_pass_rushers"].fillna(4).clip(0, 8)
m["box"] = m["n_defense_box"].fillna(6).clip(0, 11)
m["blitz"] = (m["n_blitzers"].fillna(0) > 0).astype(int)
# coverage-shell proxy labels from box+rushers+down (documented heuristic)
# Cover-0: 6+ rush / blitz with box>=6; Cover-1: blitz/5rush box 6-7;
# Cover-2: 4 rush box 6-7; Cover-3: 4 rush box 7-8 vs run downs;
# Cover-4/Quarters: 4 rush box<=6 on pass downs; Goal-line: box>=8
import numpy as np
cond = [
    (m["rushers"] >= 6).to_numpy(),
    ((m["rushers"] == 5) & (m["box"] >= 6)).to_numpy(),
    ((m["rushers"] == 4) & (m["box"] >= 7)).to_numpy(),
    ((m["rushers"] == 4) & (m["box"] <= 5) & (m["down"] >= 2)).to_numpy(),
    ((m["rushers"] <= 4) & (m["box"] >= 8)).to_numpy(),
]
labels = ["Cover-0", "Cover-1", "Cover-3", "Quarters", "Goal-line"]
m["shell"] = np.select(cond, labels, default="Cover-2")
print("shell dist:", m["shell"].value_counts(normalize=True).round(3).to_dict())
FEATS = ["box", "rushers", "down", "ydstogo", "yardline_100",
         "shotgun", "is_motion", "is_play_action", "blitz"]
for c in ["shotgun"]:
    m[c] = m[c].fillna(0).astype(float)
for c in ["is_motion", "is_play_action"]:
    m[c] = m[c].fillna(False).astype(int)
m["ydstogo"] = m["ydstogo"].fillna(10)
m["yardline_100"] = m["yardline_100"].fillna(50)
m = m.dropna(subset=FEATS + ["shell", "defteam", "epa"])
tr = m[m["season_x"] <= 2023]
te = m[m["season_x"] >= 2024]
le = LabelEncoder()
clf = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                    subsample=0.9, colsample_bytree=0.8, n_jobs=-1,
                    random_state=42)
clf.fit(tr[FEATS], le.fit_transform(tr["shell"]))
for nm, d in [("train", tr), ("test24+", te)]:
    print(nm, round(float(accuracy_score(le.transform(d["shell"]), clf.predict(d[FEATS]))), 4))
joblib.dump(clf, os.path.join(M, "shell_clf.pkl"))
json.dump({"features": FEATS, "classes": le.classes_.tolist()},
          open(os.path.join(M, "shell_meta.json"), "w"), indent=2)
joblib.dump(le, os.path.join(M, "shell_labels.pkl"))

# team tendencies
t = m.groupby("defteam").agg(plays=("shell", "size"),
                             blitz_rate=("blitz", "mean"),
                             box_avg=("box", "mean"),
                             rush_avg=("rushers", "mean"),
                             epa_allowed=("epa", "mean")).round(3)
for s in le.classes_.tolist():
    t["sh_" + s] = m.groupby("defteam")["shell"].apply(lambda x, s=s: (x == s).mean()).round(3)
t = t.sort_values("blitz_rate", ascending=False)
t.to_csv(os.path.join(D, "team_tendencies.csv"))
print(t.head(12).to_string())
print("saved")
