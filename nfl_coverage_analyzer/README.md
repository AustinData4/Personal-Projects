# Defensive Coverage Analyzer
- Data: FTN charting 2022-2025 (185k plays, attribute
  'ftndata.com via nflverse') joined to nflverse PBP context
  (96.6% match). Blitz rate overall 13.4%.
- Shells are RULE-BASED PROXIES from box+rushers+down
  (Cover-0/1/2/3, Quarters, Goal-line) — true pre/post-snap
  alignments need Big Data Bowl tracking XY (hook: data/tracking/).
  XGB shell classifier included for the interactive demo
  (note: it re-learns the rule, so acc ~1.0 by construction).
- Team tendencies: data/team_tendencies.csv (blitz rate, box/rush
  avg, EPA allowed, shell mix). Top blitz: MIN 0.250, TB 0.248.
## Run
pip install -r requirements.txt
python build_coverage.py && python train_shell.py
streamlit run app.py
