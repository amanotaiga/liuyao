"""
Main entry point for the Gradio UI

This module provides a simple entry point to launch the Gradio interface.
It imports and launches the UI created by ui_builder.
"""

import sys
from pathlib import Path

# Handle both direct execution and module import
# When run directly (python main.py), we need to adjust imports
if __name__ == "__main__":
    # Add parent directory to path so we can import gradio_ui as a package
    current_file = Path(__file__).resolve()
    gradio_ui_dir = current_file.parent
    project_root = gradio_ui_dir.parent
    
    # Add project root to path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Use absolute imports when run directly
    from gradio_ui.ui_builder import create_ui
else:
    # Use relative imports when imported as module
    from .ui_builder import create_ui


def main():
    """Main entry point to launch the Gradio UI"""
    demo = create_ui()
    demo.launch()


if __name__ == "__main__":
    main()

