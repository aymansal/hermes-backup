#!/usr/bin/env bash
# Restore Ayman's Hermes recovery vault.
# Recommended for a new VPS: run this script in default full-clone mode.
# It restores the source/dashboard snapshot, memory/skills/config, then installs the hermes CLI launcher.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
ASSUME_YES=0
DRY_RUN=0
MODE="full"  # full | knowledge
SKIP_PACKAGES=0
SKIP_SYSTEMD=1
INSTALL_HERMES=1

usage() {
  cat <<'EOF'
Hermes Restore Script — Shadow System Recovery

Recommended friend-clone flow:
  1. Run: bash scripts/restore.sh --yes
  2. Run: hermes login --provider openai-codex
  3. Run: hermes
  4. Ask Hermes to configure Telegram interactively. Paste secrets only when Hermes asks.

Usage:
  bash scripts/restore.sh [options]

Options:
  --full            Restore source/dashboard snapshot plus brain/persona/skills/memory/config. Default.
  --knowledge-only  Restore brain/persona/skills/memory/config only. Does NOT overwrite source/dashboard.
  --yes             Do not ask before restoring.
  --dry-run         Show what would be restored, but do not write files.
  --with-packages   Install base apt packages. Default in --full mode.
  --with-systemd    Restore systemd user units. Off by default; useful only for exact recovery.
  --no-install-hermes  Do not install/reinstall the global hermes CLI launcher.
  -h, --help        Show this help.

Default full restores:
  - ~/.hermes/hermes-agent source snapshot, including the customized dashboard build/code
  - ~/.hermes/config.yaml and persona/profile files
  - ~/.hermes/skills
  - ~/.hermes/memory_store.db, kanban.db, cron definitions
  - ~/.hermes/.env template only if .env does not exist
  - global hermes CLI launcher, installed from the restored source snapshot

Never restored:
  - secret values
  - ~/.hermes/auth.json / OAuth tokens
  - existing ~/.hermes/.env values
EOF
}

log() { printf '\033[1;34m[restore]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[fail]\033[0m %s\n' "$*" >&2; exit 1; }
run() {
  if [ "$DRY_RUN" = 1 ]; then
    printf '[dry-run] %q ' "$@"; printf '\n'
  else
    "$@"
  fi
}

install_hermes_cli() {
  if [ "$INSTALL_HERMES" != 1 ]; then
    return 0
  fi

  if [ "$MODE" = "knowledge" ] && command -v hermes >/dev/null 2>&1; then
    log "Hermes CLI already found: $(command -v hermes)"
    return 0
  fi

  if [ "$MODE" = "full" ]; then
    [ -f "$HERMES_HOME/hermes-agent/scripts/install.sh" ] || fail "Restored source is missing scripts/install.sh; cannot install Hermes CLI."
    log "Installing global hermes CLI launcher from restored source snapshot."
    run bash "$HERMES_HOME/hermes-agent/scripts/install.sh" --skip-setup --dir "$HERMES_HOME/hermes-agent" --hermes-home "$HERMES_HOME"
  else
    log "Hermes CLI missing; installing official Hermes first for knowledge-only restore."
    if [ "$DRY_RUN" = 1 ]; then
      printf '[dry-run] curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash -s -- --skip-setup --hermes-home %q\n' "$HERMES_HOME"
    else
      curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash -s -- --skip-setup --hermes-home "$HERMES_HOME"
    fi
  fi

  if [ "$DRY_RUN" = 1 ]; then
    log "Dry-run: skipped post-install PATH verification."
    return 0
  fi

  export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
  command -v hermes >/dev/null 2>&1 || fail "Hermes CLI install finished, but 'hermes' is still not on PATH. Try: source ~/.bashrc && export PATH=\"$HOME/.local/bin:/usr/local/bin:\$PATH\""
  log "Hermes CLI ready: $(command -v hermes)"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --knowledge-only) MODE="knowledge"; SKIP_PACKAGES=1; SKIP_SYSTEMD=1 ;;
    --full) MODE="full"; SKIP_PACKAGES=0 ;;
    --yes) ASSUME_YES=1 ;;
    --dry-run) DRY_RUN=1 ;;
    --with-packages) SKIP_PACKAGES=0 ;;
    --with-systemd) SKIP_SYSTEMD=0 ;;
    --no-install-hermes) INSTALL_HERMES=0 ;;
    -h|--help) usage; exit 0 ;;
    *) fail "Unknown option: $1" ;;
  esac
  shift
done

[ -d "$ROOT" ] || fail "Cannot find restore root."
[ -d "$ROOT/config" ] || fail "Missing config/ directory. Run this from the cloned hermes-backup repo."

log "Restore root: $ROOT"
log "Hermes home:  $HERMES_HOME"
log "Mode:         $MODE"
log "Install CLI:  $INSTALL_HERMES"

if [ "$ASSUME_YES" != 1 ] && [ "$DRY_RUN" != 1 ]; then
  cat <<EOF
This will restore Hermes knowledge into:
  $HERMES_HOME

Mode: $MODE
Secret files like ~/.hermes/.env and ~/.hermes/auth.json will NOT be overwritten.
EOF
  if [ "$MODE" = "full" ]; then
    warn "FULL mode may move/replace ~/.hermes/hermes-agent, then reinstall the hermes CLI launcher from the restored source."
    if [ "$SKIP_SYSTEMD" = 0 ]; then
      warn "Systemd user units will also be restored because --with-systemd was requested."
    fi
  fi
  read -r -p "Continue? Type YES to proceed: " answer
  [ "$answer" = "YES" ] || fail "Restore cancelled."
fi

if [ "$SKIP_PACKAGES" = 0 ]; then
  if command -v apt-get >/dev/null 2>&1; then
    log "Installing base packages if missing."
    run sudo apt-get update
    run sudo apt-get install -y git curl rsync sqlite3 python3 python3-venv python3-pip build-essential
  else
    warn "apt-get not found; skipping package install."
  fi
fi

log "Creating directories."
run mkdir -p "$HERMES_HOME"

log "Restoring sanitized config/persona/profile files."
run rsync -a "$ROOT/config/" "$HERMES_HOME/"
if [ -f "$HERMES_HOME/_install_method" ] && [ ! -f "$HERMES_HOME/.install_method" ]; then
  run mv "$HERMES_HOME/_install_method" "$HERMES_HOME/.install_method"
fi

if [ -d "$ROOT/skills/user-skills" ]; then
  log "Restoring Skill Runes."
  run mkdir -p "$HERMES_HOME/skills"
  run rsync -a "$ROOT/skills/user-skills/" "$HERMES_HOME/skills/"
fi

if [ -d "$ROOT/state" ]; then
  log "Restoring memory/kanban/cron state."
  run rsync -a "$ROOT/state/" "$HERMES_HOME/"
fi

if [ ! -f "$HERMES_HOME/.env" ]; then
  if [ -f "$ROOT/secrets/env.template" ]; then
    log "Creating ~/.hermes/.env from template. Fill Access Keys later if needed."
    run cp "$ROOT/secrets/env.template" "$HERMES_HOME/.env"
    run chmod 600 "$HERMES_HOME/.env"
  fi
else
  warn "$HERMES_HOME/.env already exists; not overwriting secrets."
fi

if [ "$MODE" = "full" ]; then
  [ -d "$ROOT/source/hermes-agent" ] || fail "Missing source/hermes-agent/ directory for --full mode."
  log "Restoring Hermes source snapshot."
  if [ -d "$HERMES_HOME/hermes-agent" ]; then
    stamp="$(date +%Y%m%d-%H%M%S)"
    warn "Existing hermes-agent directory found; moving to hermes-agent.before-restore-$stamp"
    run mv "$HERMES_HOME/hermes-agent" "$HERMES_HOME/hermes-agent.before-restore-$stamp"
  fi
  run mkdir -p "$HERMES_HOME/hermes-agent"
  run rsync -a "$ROOT/source/hermes-agent/" "$HERMES_HOME/hermes-agent/"
fi

install_hermes_cli

if [ "$SKIP_SYSTEMD" = 0 ] && [ -d "$ROOT/systemd" ]; then
  log "Restoring systemd user units."
  run mkdir -p "$SYSTEMD_USER_DIR"
  run rsync -a "$ROOT/systemd/" "$SYSTEMD_USER_DIR/"
  run systemctl --user daemon-reload || warn "systemctl --user daemon-reload failed; run it manually later."
fi

run chmod 700 "$HERMES_HOME" || true
run chmod 600 "$HERMES_HOME/config.yaml" 2>/dev/null || true
run chmod 600 "$HERMES_HOME/memory_store.db" 2>/dev/null || true
run chmod 600 "$HERMES_HOME/kanban.db" 2>/dev/null || true

log "Restore complete."

if [ "$DRY_RUN" = 1 ]; then
  log "Dry-run complete; skipped hermes doctor."
elif command -v hermes >/dev/null 2>&1; then
  log "Running hermes doctor."
  hermes doctor || warn "hermes doctor reported issues. Usually missing OAuth login or Access Keys."
else
  warn "hermes CLI not found in PATH after restore. Reload shell and check ~/.local/bin or /usr/local/bin."
fi

cat <<'EOF'

Next commands:
  source ~/.bashrc 2>/dev/null || true
  export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
  which hermes
  hermes login --provider openai-codex
  hermes

Inside Hermes, paste this mission:
  Set up Hermes on this VPS using my ChatGPT Codex login as the model provider. Configure Telegram gateway from scratch. Guide me to create a Telegram bot with BotFather, ask me for the token, save it securely in ~/.hermes/.env without printing it back, configure the gateway, set my current Telegram chat as home, start the systemd user service only after I approve, and verify end-to-end.

System note: Hermes body/brain restored according to mode. Secrets/OAuth still need login. BotFather token must be provided by the operator when Hermes asks. No key, no summon.
EOF
