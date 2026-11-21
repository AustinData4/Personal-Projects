"""Streamlit dashboard: defensive coverage + blitz tendencies.
Run: streamlit run app.py
"""
import os
import pandas as pd, joblib, streamlit as st
BASE = os.path.dirname(__file__)
tend = pd.read_csv(os.path.join(BASE, "data", "team_tendencies.csv"), index_col=0)
clf = joblib.load(os.path.join(BASE, "models", "shell_clf.pkl"))
le = joblib.load(os.path.join(BASE, "models", "shell_labels.pkl"))
st.set_page_config(page_title="Coverage Analyzer", layout="wide")
st.title("Defensive Coverage Analyzer (PBP + FTN 2022-2025)")
st.caption("Shells are documented proxies from box + rushers + down "
           "(true pre/post-snap tracking needs Big Data Bowl XY). "
           "FTN data: attribute 'ftndata.com via nflverse'.")
team = st.selectbox("Defense", sorted(tend.index.tolist()))
row = tend.loc[team]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Blitz rate", round(float(row["blitz_rate"]), 3))
c2.metric("Box avg", round(float(row["box_avg"]), 2))
c3.metric("Rush avg", round(float(row["rush_avg"]), 2))
c4.metric("EPA allowed/play", round(float(row["epa_allowed"]), 3))
shell_cols = [c for c in tend.columns if c.startswith("sh_")]
st.subheader("%s shell mix" % team)
st.bar_chart(row[shell_cols].rename(lambda x: x[3:]))
st.subheader("League blitz-rate ranking")
st.dataframe(tend[["plays", "blitz_rate", "box_avg",
                   "rush_avg", "epa_allowed"]].sort_values(
    "blitz_rate", ascending=False), use_container_width=True)
st.subheader("Classify any situation")
a, b, c = st.columns(3)
box = a.slider("Defenders in box", 0, 11, 6)
rush = b.slider("Pass rushers", 0, 8, 4)
down = c.selectbox("Down", [1, 2, 3, 4], index=0)
d, e, f = st.columns(3)
togo = d.slider("Yards to go", 1, 20, 10)
yl = e.slider("Yardline_100 (defense perspective)", 1, 99, 50)
bl = f.checkbox("Blitz flagged", value=False)
import numpy as np
X = np.array([[box, rush, down, togo, yl, 0.0, 0, 0, int(bl)]], dtype=float)
pred = le.inverse_transform(clf.predict(X))[0]
proba = dict(zip(le.classes_, clf.predict_proba(X)[0].round(3)))
st.success("Predicted shell: %s" % pred)
st.write(proba)
