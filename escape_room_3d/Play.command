#!/bin/bash
# Escape Room 3D — Mac launcher. Double-click to play.
# Serves this folder on localhost, then opens it in your default browser.
cd "$(dirname "$0")"
PORT=8000
# free the port if a previous run is still hanging around
lsof -ti tcp:$PORT | xargs kill -9 2>/dev/null
(sleep 1 && open "http://localhost:$PORT/index.html") &
echo "Escape Room 3D running at http://localhost:$PORT"
echo "Close this window to stop the server."
python3 -m http.server $PORT
