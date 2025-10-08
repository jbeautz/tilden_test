#!/bin/bash
# Wrapper script to run data viewer on macOS
cd "$(dirname "$0")"
export PYTHONUNBUFFERED=1
python3 -u data_viewer.py
