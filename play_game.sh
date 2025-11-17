#!/usr/bin/env bash

# 1) launch the backend
echo "Starting backend…"
uv run src/backend/server.py &

BACKEND_PID=$!
# give it a second to spin up
sleep 1

# 2) open the HTML UI (Linux/Mac)
if command -v xdg-open >/dev/null; then
  xdg-open src/frontend/index_tabbed.html
elif command -v open >/dev/null; then
  open src/frontend/index_tabbed.html
else
  echo "Please open src/frontend/index_tabbed.html in your browser"
fi

# 3) wait on the backend process
wait $BACKEND_PID
