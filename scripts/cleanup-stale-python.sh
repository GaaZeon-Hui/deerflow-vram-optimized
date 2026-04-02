#!/usr/bin/env bash
# cleanup-stale-python.sh - aggressively kill lingering python/uvicorn/langgraph processes inside the container

set -euo pipefail

silent_kill() {
  set +e
  kill -9 "$1" >/dev/null 2>&1
  local rc=$?
  set -e
  return $rc
}

log() {
  printf '[cleanup-stale-python] %s\n' "$*"
}

kill_port() {
  local port="$1"
  if ! command -v ss >/dev/null 2>&1; then
    log "ss(8) not found, skipping port ${port} cleanup"
    return
  fi
  set +e
  local raw
  raw=$(ss -tulpn 2>/dev/null | awk -v port=":${port}" '$0 ~ port { if (match($0, /pid=([0-9]+)/, m)) print m[1] }')
  set -e
  if [ -z "$raw" ]; then
    return
  fi
  local killed=0
  while IFS= read -r pid; do
    if [ -n "$pid" ] && [ "$pid" -ne "$$" ]; then
      silent_kill "$pid"
      killed=1
    fi
  done <<<"$raw"
  if [ "$killed" -eq 1 ]; then
    log "cleared listeners on port ${port}"
  fi
}

kill_pattern() {
  local pattern="$1"
  if command -v pkill >/dev/null 2>&1; then
    set +e
    pkill -9 -f "$pattern" >/dev/null 2>&1
    set -e
  elif command -v pgrep >/dev/null 2>&1; then
    set +e
    local pids_raw
    pids_raw=$(pgrep -f "$pattern" 2>/dev/null)
    set -e
    if [ -z "$pids_raw" ]; then
      return
    fi
    while IFS= read -r pid; do
      if [ -n "$pid" ] && [ "$pid" -ne "$$" ]; then
        silent_kill "$pid"
      fi
    done <<<"$pids_raw"
  fi
}

log "running stale python/uvicorn cleanup"

for port in 2024 8001; do
  kill_port "$port"
done

for pattern in "langgraph dev" "uv run" "uvicorn app.gateway.app:app" "python -m uvicorn" "uvicorn"; do
  kill_pattern "$pattern"
done

log "cleanup finished"
