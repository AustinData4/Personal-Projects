# 4th-Down Decision Model (neural net + dashboard)
- Data: 41,779 4th downs 2016-2025 from nflverse PBP; 39,366 after
  dropping no_play/kneel. Labels: go (7,057) / fg (9,790) / punt (22,519).
- Model: sklearn MLPClassifier(64,32), 10 features (yardline, to-go,
  score diff, qtr, time left, timeouts, WP, goal-to-go, home).
  Train acc 0.912, test 2024+ acc 0.881.
- Dashboard overlays empirical league go-conversion table
  (data/go_success_table.csv) + FG distance math on top of the
  mimic-coach probabilities.
## Run
pip install -r requirements.txt
python build_fourth.py && python train_fourth2.py
streamlit run app.py
