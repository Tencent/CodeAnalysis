#!/usr/bin/env bash

case $1 in
  -h|--help)
    echo $'usage: docker-stop\n\nStops Docker (Docker.app) on macOS.'    
    exit 0
    ;;
esac
(( $# )) && { echo "ARGUMENT ERROR: Unexpected argument(s) specified. Use -h for help." >&2; exit 2; }

[[ $(uname) == 'Darwin' ]] || { echo "This function only runs on macOS." >&2; exit 2; }

echo "-- Quitting Docker.app, if running..."

osascript - <<'EOF' || exit
tell application "Docker"
  if it is running then quit it
end tell
EOF

echo "-- Docker is stopped."
echo "Caveat: Restarting it too quickly can cause errors."
