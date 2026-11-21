import os, json
import numpy as np, pandas as pd, joblib
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix
D = "/Users/austincharbonneau/GitHub/AustinData4/nfl_4th_down/data"
M = "/Users/austincharbonneau/GitHub/AustinData4/nfl_4th_down/models"
os.makedirs(M, exist_ok=True)
fd = pd.read_parquet(os.path.join(D, "fourth_all.parquet"))
# decision labels: go = pass/run (excl kneel), punt, fg; drop no_play/kneel
fd = fd[~fd["play_type"].isin(["no_play", "qb_kneel"])].copy()
fd["decision"] = fd["play_type"].map({"pass": "go", "run": "go",
                                      "punt": "punt", "field_goal": "fg"})
fd = fd[fd["decision"].notna()].copy()
fd["yard100"] = fd["yardline_100"].clip(1, 99)
fd["togo"] = fd["ydstogo"].clip(1, 30)
fd["qtr"] = fd["qtr"].fillna(4)
fd["gsr"] = fd["game_seconds_remaining"].fillna(1800)
fd["sdiff"] = fd["score_differential"].fillna(0).clip(-28, 28)
fd["off_to"] = fd["posteam_timeouts_remaining"].fillna(3)
fd["def_to"] = fd["defteam_timeouts_remaining"].fillna(3)
fd["wp"] = fd["wp"].fillna(0.5)
fd["goal"] = fd["goal_to_go"].fillna(0)
fd["is_home"] = (fd["posteam"] == fd["home_team"]).astype(int)
FEATS = ["yard100", "togo", "sdiff", "qtr", "gsr", "off_to",
         "def_to", "wp", "goal", "is_home"]
fd = fd.dropna(subset=FEATS + ["decision"])
print("rows:", len(fd), fd["decision"].value_counts().to_dict())
tr = fd[fd["season"] <= 2023]
te = fd[fd["season"] >= 2024]
sc = StandardScaler().fit(tr[FEATS])
mlp = MLPClassifier(hidden_layer_sizes=(64, 32), activation="relu",
                    alpha=0.001, learning_rate_init=0.001,
                    max_iter=400, early_stopping=True,
                    n_iter_no_change=20, random_state=42, verbose=False)
mlp.fit(sc.transform(tr[FEATS]), tr["decision"])
for nm, d in [("train", tr), ("test24+", te)]:
    p = mlp.predict(sc.transform(d[FEATS]))
    print(nm, "acc:", round(accuracy_score(d["decision"], p), 4))
    print(nm, "cm [go,fg,punt]:")
    print(confusion_matrix(d["decision"], p, labels=["go", "fg", "punt"]))
joblib.dump(mlp, os.path.join(M, "fourth_mlp.pkl"))
joblib.dump(sc, os.path.join(M, "fourth_scaler.pkl"))
json.dump({"features": FEATS, "classes": ["go", "fg", "punt"]},
          open(os.path.join(M, "fourth_meta.json"), "w"), indent=2)
# empirical go-success buckets for dashboard overlay
go = fd[fd["decision"] == "go"].copy()
go["conv"] = ((go["fourth_down_converted"] == 1.0)).astype(int)
go["dist_bin"] = pd.cut(go["togo"], [0, 1, 2, 4, 7, 30],
                        labels=["1", "2", "3-4", "5-7", "8+"])
go["field_bin"] = pd.cut(go["yard100"], [0, 50, 75, 90, 100],
                         labels=["own", "mid", "opp40-25", "redzone"])
tab = go.groupby(["dist_bin", "field_bin"], observed=True)["conv"].agg(["mean", "count"]).reset_index()
tab.to_csv(os.path.join(D, "go_success_table.csv"), index=False)
print(tab.to_string())
print("saved")
