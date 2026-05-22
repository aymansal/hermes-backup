#!/usr/bin/env bash
set -euo pipefail

# Hermes Shadow System restore helper.
# Run on a fresh Ubuntu VPS after cloning this private repo.

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SRC_DIR="$HERMES_HOME/hermes-agent"

mkdir -p "$HERMES_HOME"

if ! command -v git >/dev/null 2>&1; then
  sudo apt-get update && sudo apt-get install -y git curl python3 python3-venv
fi

if [ ! -d "$SRC_DIR/.git" ]; then
  mkdir -p "$(dirname "$SRC_DIR")"
  cp -a "$BACKUP_DIR/source/hermes-agent" "$SRC_DIR"
else
  echo "Source exists at $SRC_DIR; not overwriting."
fi

cp -a "$BACKUP_DIR/skills/user-skills" "$HERMES_HOME/skills" 2>/dev/null || true
cp -a "$BACKUP_DIR/config/SOUL.md" "$HERMES_HOME/SOUL.md" 2>/dev/null || true
cp -a "$BACKUP_DIR/config/OPERATOR_PROFILE.md" "$HERMES_HOME/OPERATOR_PROFILE.md" 2>/dev/null || true
cp -a "$BACKUP_DIR/config/config.yaml" "$HERMES_HOME/config.yaml" 2>/dev/null || true
cp -a "$BACKUP_DIR/state/memory_store.db" "$HERMES_HOME/memory_store.db" 2>/dev/null || true
cp -a "$BACKUP_DIR/state/kanban.db" "$HERMES_HOME/kanban.db" 2>/dev/null || true
cp -a "$BACKUP_DIR/state/cron" "$HERMES_HOME/cron" 2>/dev/null || true

if [ ! -f "$HERMES_HOME/.env" ] && [ -f "$BACKUP_DIR/secrets/env.template" ]; then
  cp "$BACKUP_DIR/secrets/env.template" "$HERMES_HOME/.env"
  chmod 600 "$HERMES_HOME/.env"
  echo "Created $HERMES_HOME/.env from template. Fill Access Keys before starting Hermes."
fi

mkdir -p "$HOME/.config/systemd/user"
cp -a "$BACKUP_DIR/systemd"/*.service "$HOME/.config/systemd/user/" 2>/dev/null || true
cp -a "$BACKUP_DIR/systemd"/*.timer "$HOME/.config/systemd/user/" 2>/dev/null || true
systemctl --user daemon-reload 2>/dev/null || true

echo "Restore files placed. Next: fill ~/.hermes/.env, run hermes doctor, then resummon services."
