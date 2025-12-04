"""
Utility functions for loading static assets (CSS and JavaScript)

Functions to load CSS and JavaScript files and format them for Gradio.
"""
import os
from pathlib import Path


def get_static_dir() -> Path:
    """Get the path to the static directory"""
    # Get the directory where this file is located
    current_dir = Path(__file__).parent.parent
    static_dir = current_dir / "static"
    return static_dir


def load_css(file_name: str = "styles.css") -> str:
    """
    Load CSS file and wrap it in <style> tags for Gradio
    
    Args:
        file_name: Name of the CSS file (default: "styles.css")
    
    Returns:
        HTML string with CSS wrapped in <style> tags
    """
    static_dir = get_static_dir()
    css_path = static_dir / file_name
    
    if not css_path.exists():
        raise FileNotFoundError(f"CSS file not found: {css_path}")
    
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    return f"<style>\n{css_content}\n</style>"


def load_js(file_name: str = "scripts.js") -> str:
    """
    Load JavaScript file and wrap it in <script> tags for Gradio
    
    Args:
        file_name: Name of the JavaScript file (default: "scripts.js")
    
    Returns:
        HTML string with JavaScript wrapped in <script> tags
    """
    static_dir = get_static_dir()
    js_path = static_dir / file_name
    
    if not js_path.exists():
        raise FileNotFoundError(f"JavaScript file not found: {js_path}")
    
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    return f"<script>\n{js_content}\n</script>"


def load_static_assets(css_file: str = "styles.css", js_file: str = "scripts.js") -> str:
    """
    Load both CSS and JavaScript files and combine them for Gradio
    
    Args:
        css_file: Name of the CSS file (default: "styles.css")
        js_file: Name of the JavaScript file (default: "scripts.js")
    
    Returns:
        Combined HTML string with CSS and JavaScript
    """
    css_html = load_css(css_file)
    js_html = load_js(js_file)
    return f"{css_html}\n{js_html}"
