#!/usr/bin/env bash
# Fix Docker on Ubuntu and standardize on Docker Compose V2 (docker compose).
#
# Usage:
#   bash infrastructure/scripts/fix-docker.sh
#
# Optional — match how Compose V2 is installed on your machine/server:
#   COMPOSE_PROVIDER=plugin  — docker-compose-plugin (Docker CE / get.docker.com)
#   COMPOSE_PROVIDER=ubuntu  — docker-compose-v2 .deb (Ubuntu archive) [default]
#
# Both provide the same command:  docker compose  (V2, not docker-compose V1)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

COMPOSE_PROVIDER="${COMPOSE_PROVIDER:-ubuntu}"

info() { echo -e "${GREEN}==>${NC} $*"; }
warn() { echo -e "${YELLOW}!!>${NC} $*"; }
err() { echo -e "${RED}ERROR:${NC} $*"; exit 1; }

if [[ "${EUID}" -eq 0 ]]; then
  err "Run as your normal user; the script will use sudo when needed."
fi

info "Target: Docker Engine + Compose V2 (provider: ${COMPOSE_PROVIDER})"

info "Step 1: Repair apt"
sudo dpkg --configure -a || true
sudo apt-get install -f -y

info "Step 2: Remove legacy Compose V1 if present"
sudo apt-get remove -y docker-compose 2>/dev/null || true

info "Step 3: Install Docker Engine"
if ! dpkg -l docker.io 2>/dev/null | grep -q '^ii'; then
  sudo apt-get update
  sudo apt-get install -y docker.io
fi

info "Step 4: Install exactly one Compose V2 provider"
case "${COMPOSE_PROVIDER}" in
  plugin)
    # Same stack as Docker CE on many servers (docker compose plugin)
    sudo apt-get remove -y docker-compose-v2 2>/dev/null || true
    sudo apt-get install -y docker-compose-plugin
    ;;
  ubuntu)
    # Ubuntu docker-compose-v2 package — cannot coexist with docker-compose-plugin
    if dpkg -l docker-compose-plugin 2>/dev/null | grep -q '^ii'; then
      info "Removing docker-compose-plugin (conflicts with docker-compose-v2)"
      sudo apt-get remove -y docker-compose-plugin
    fi
    sudo apt-get install -y docker-compose-v2
    ;;
  *)
    err "Unknown COMPOSE_PROVIDER=${COMPOSE_PROVIDER}. Use 'ubuntu' or 'plugin'."
    ;;
esac

info "Step 5: Enable Docker service"
sudo systemctl enable docker
sudo systemctl start docker

info "Step 6: docker group"
if ! groups "$USER" | grep -q '\bdocker\b'; then
  sudo usermod -aG docker "$USER"
  warn "Added $USER to group 'docker'. Log out/in or run: newgrp docker"
fi

info "Step 7: Use system Docker (not Docker Desktop)"
DOCKER_BIN="/usr/bin/docker"
if [[ -x "${DOCKER_BIN}" ]]; then
  "${DOCKER_BIN}" context use default 2>/dev/null || true
  if [[ ! -S "${HOME}/.docker/desktop/docker.sock" ]] \
    && "${DOCKER_BIN}" context ls -q 2>/dev/null | grep -qx desktop-linux; then
    "${DOCKER_BIN}" context rm desktop-linux -f 2>/dev/null || true
  fi
else
  warn "${DOCKER_BIN} not found"
fi

# Docker Desktop leaves credsStore=desktop; breaks pulls after uninstall
if [[ -f "${HOME}/.docker/config.json" ]] && grep -q '"credsStore".*desktop' "${HOME}/.docker/config.json" 2>/dev/null; then
  info "Removing Docker Desktop credential helper from ~/.docker/config.json"
  python3 -c "
import json, pathlib
p = pathlib.Path.home() / '.docker/config.json'
cfg = json.loads(p.read_text())
cfg.pop('credsStore', None)
cfg.pop('credHelpers', None)
p.write_text(json.dumps(cfg, indent=2) + '\n')
"
fi

info "Step 8: Verify Compose V2"
hash -r 2>/dev/null || true
export PATH="/usr/bin:/bin:${PATH}"

docker_cmd() {
  if groups "$USER" | grep -q '\bdocker\b'; then
    docker "$@"
  elif [[ -S /var/run/docker.sock ]] && [[ -r /var/run/docker.sock ]]; then
    docker "$@"
  elif [[ -S /var/run/docker.sock ]]; then
    sg docker -c "docker $*"
  else
    sudo docker "$@"
  fi
}

if ! systemctl is-active --quiet docker 2>/dev/null; then
  err "Docker service is not running. Run: sudo systemctl start docker"
fi

if ! docker_cmd info >/dev/null 2>&1; then
  if [[ -S /var/run/docker.sock ]] && ! groups "$USER" | grep -q '\bdocker\b'; then
    echo ""
    warn "Docker is running but your user is not in the 'docker' group yet."
    warn "Run ONE of these, then try again:"
    echo "  newgrp docker"
    echo "  # or log out and log back in"
    echo ""
    warn "Quick test (works immediately):"
    echo "  sg docker -c 'docker info'"
    exit 1
  fi
  err "docker info failed. Check: sudo journalctl -u docker -n 50"
fi

if docker_cmd compose version >/dev/null 2>&1; then
  COMPOSE_VER="$(docker_cmd compose version --short 2>/dev/null || docker_cmd compose version | head -1)"
  info "Compose V2 OK: ${COMPOSE_VER}"
  case "${COMPOSE_VER}" in
    2.*|v2.*) ;;
    *)
      warn "Expected Compose 2.x, got: ${COMPOSE_VER}"
      ;;
  esac
else
  err "'docker compose' not available. Re-run with COMPOSE_PROVIDER=plugin or COMPOSE_PROVIDER=ubuntu"
fi

# Reject old V1 hyphenated command if it points to a real v1 binary
if command -v docker-compose >/dev/null 2>&1; then
  if docker-compose version 2>/dev/null | grep -qE 'version 1\.'; then
    warn "docker-compose V1 still on PATH — remove package 'docker-compose' (not needed for this project)"
  fi
fi

echo ""
info "Done. Open a new terminal, then:"
echo "  cd ~/personal/projects/pdfintoword"
echo "  docker compose up --build"
echo ""
info "Context: $(docker_cmd context show 2>/dev/null || echo unknown)"
if ! groups "$USER" | grep -q '\bdocker\b'; then
  warn "Remember: run 'newgrp docker' or log out/in before 'docker compose' without sg/sudo"
fi
