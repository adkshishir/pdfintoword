#!/bin/bash
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH=.
python -m pytest tests/ -v "$@"
