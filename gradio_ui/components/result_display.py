"""
Result display component for the Gradio UI

This module contains the result display component that shows divination results.
"""

from dataclasses import dataclass

import gradio as gr


@dataclass
class ResultDisplay:
    """Components for displaying divination results"""
    result_table: gr.Textbox


def create_result_display() -> ResultDisplay:
    """
    Create the result display component
    
    Returns:
        ResultDisplay containing the result table component
    """
    gr.Markdown("### 詳細排盤表", elem_classes=["section-header"])
    gr.Markdown(
        "<p style='color: #868e96; font-size: 13px; margin-top: -8px; margin-bottom: 16px;'>排盤結果將顯示在下方</p>",
        elem_classes=["text-muted"]
    )
    
    result_table = gr.Textbox(
        label="",
        lines=40,
        max_lines=60,
        interactive=True,
        elem_classes=["result-table"],
        container=True
    )
    
    return ResultDisplay(result_table=result_table)

