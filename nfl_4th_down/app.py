"""Streamlit dashboard: 4th-down decision helper.
Run: streamlit run app.py
Field runs LEFT (own goal) -> RIGHT (opponent goal), like a TV broadcast:
  side = Own 10..50, then Opp 50..10 ... or use midfield.
Model trained on nflverse yardline_100 (distance from OWN goal),
so the UI converts side+line -> yard100 before predicting.
"""
import os
import numpy as np, pandas as pd, joblib, streamlit as st
BASE = os.path.dirname(__file__)
mlp = joblib.load(os.path.join(BASE, "models", "fourth_mlp.pkl"))
sc = joblib.load(os.path.join(BASE, "models", "fourth_scaler.pkl"))
le = joblib.load(os.path.join(BASE, "models", "fourth_labels.pkl"))
gotab = pd.read_csv(os.path.join(BASE, "data", "go_success_table.csv"))
st.set_page_config(page_title="4th Down Decision", layout="wide")
st.title("4th-Down Decision Model (neural net, 2016-2025)")
st.caption("MLP(64,32) trained on 39,366 4th downs. Test acc 0.88. "
           "Recommendation blends typical-coach behavior with empirical go success.")

# ---------- FIELD POSITION: left(own) -> right(opp), 0-50 each side ----------
st.subheader("Ball location  ( own goal line  --- MIDFIELD ---  opponent goal line )")
f1, f2 = st.columns([1, 2])
side = f1.radio("Side of field", ["Own", "Opp"], index=0, horizontal=True)
if side == "Own":
    line = f2.slider("Yard line on OWN side (50 = midfield, 1 = own goal)",
                     1, 50, 35,
                     help="50 is midfield, 1 is your own goal line. Field runs left -> right.")
    yard_label = "Own %d" % line
    yard100 = 50 + line  # to model scale (yards to OPP end zone)
else:
    line = f2.slider("Yard line on OPPONENT side (50 = midfield, 1 = goal to go)",
                     1, 50, 30,
                     help="50 is midfield, 1 is the opponent goal line. Field runs left -> right.")
    yard_label = "Opp %d" % line
    yard100 = line
st.write("Ball on: **%s**  |  %d yards to opponent end zone / %d yards from own goal" % (
    yard_label, yard100, 100 - yard100))

c1, c2, c3 = st.columns(3)
togo = c1.slider("Yards to go", 1, 20, 4)
sdiff = c2.slider("Score differential (offense minus defense)", -28, 28, 0)
qtr = c3.selectbox("Quarter", [1, 2, 3, 4, 5], index=3)
mins = c1.slider("Minutes left in game", 0, 60, 8)
off_to = c2.selectbox("Offense timeouts", [0, 1, 2, 3], index=2)
def_to = c3.selectbox("Defense timeouts", [0, 1, 2, 3], index=2)
wp = c1.slider("Offense win prob (pre-snap est.)", 0.01, 0.99, 0.5)
is_home = c2.checkbox("Offense at home", value=True)
goal = yard100 <= togo
if goal:
    c3.success("Goal-to-go situation")
X = np.array([[yard100, togo, sdiff, qtr, mins * 60, off_to, def_to,
               wp, int(goal), int(is_home)]], dtype=float)
proba = mlp.predict_proba(sc.transform(X))[0]
res = dict(zip(le.classes_, proba))
st.subheader("Model: what NFL coaches typically do here")
st.bar_chart(pd.Series(res))
# analytic overlay
fg_dist = yard100 + 17  # LOS to goal + snap + end zone
fg_make = float(np.clip(0.99 - 0.006 * fg_dist, 0.35, 0.98)) if fg_dist <= 70 else 0.0
d = "1" if togo <= 1 else ("2" if togo == 2 else ("3-4" if togo <= 4 else ("5-7" if togo <= 7 else "8+")))
yb = yard100
f = "redzone" if yb <= 20 else ("opp" if yb <= 50 else ("mid" if yb <= 75 else "own"))
row = gotab[(gotab["dist_bin"] == d) & (gotab["field_bin"] == f)]
go_rate = float(row["mean"].iloc[0]) if len(row) and row["count"].iloc[0] >= 20 else 0.5
rec = max(res, key=res.get)
st.subheader("Recommendation")
st.write("Typical call: **%s** (go %.0f%% / fg %.0f%% / punt %.0f%%)" % (
    rec.upper(), res.get("go", 0) * 100, res.get("fg", 0) * 100, res.get("punt", 0) * 100))
st.write("Ball: **%s** | to go: **%d** | empirical league go-conversion in bucket %s/%s: **%.0f%%**" % (
    yard_label, togo, d, f, go_rate * 100))
st.write("FG distance ~%d yds, est. make prob ~%.0f%%" % (fg_dist, fg_make * 100))
dist_opp = yard100
if dist_opp <= 40 and togo <= 2:
    st.success("Analytics lean: GO - short yardage in plus territory.")
elif dist_opp >= 60 and togo >= 8:
    st.info("Analytics lean: PUNT - deep own territory, long to go.")
elif fg_dist <= 50 and res.get("fg", 0) > 0.3:
    st.info("Analytics lean: FG - high-percentage kick.")

