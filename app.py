"""
Hugging Face Spaces / Deployment Entry Point

This file serves as the entry point for Hugging Face Spaces and other cloud deployments.
It's a simple wrapper around the main Gradio UI.
"""

from gradio_ui.ui_builder import create_ui

# Create the Gradio interface
demo = create_ui()

# Launch with public access (for Hugging Face Spaces)
if __name__ == "__main__":
    demo.launch()

