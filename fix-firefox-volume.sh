#!/bin/bash

# Fix firefox volume up to 100% again

pactl set-sink-input-volume $(
  pactl-list | awk -f <(cat <<'EOF'
/^Sink Input/ {n=$3}
/application.name = "Firefox"/ {print substr(n,2); exit}
EOF
)) 100%
