#!/usr/bin/env python
"""
Entry point script to run the Gradio UI

This script can be run directly from the project root:
    python run_gradio_ui.py
"""

from gradio_ui.ui_builder import create_ui

if __name__ == "__main__":
    demo = create_ui()
    demo.launch()

