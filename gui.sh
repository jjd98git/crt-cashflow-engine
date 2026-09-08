#!/usr/bin/env bash
# Start the GUI (Linux/macOS/Codespaces). On Windows use gui.cmd.
cd "$(dirname "$0")"
exec .venv/bin/python -m streamlit run src/crt/gui/app.py
