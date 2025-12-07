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
    result_table_without_prompt: gr.Textbox
    copy_button: gr.Button


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
    
    with gr.Row():
        copy_button = gr.Button(
            "📋 複製",
            variant="secondary",
            size="sm",
            scale=0,
            min_width=80,
            elem_classes=["copy-button"]
        )
    
    # Visible textbox showing result without prompt
    result_table = gr.Textbox(
        label="",
        lines=1,
        visible=True,
        interactive=False,
        show_label=False,
        container=False,
        elem_classes=["result-table-hidden"],
    )
    
    # Hidden textbox for result without prompt (used for copying)
    # This will be hidden via CSS
    result_table_without_prompt = gr.Textbox(
        label="",
        lines=40,
        max_lines=60,
        interactive=True,
        elem_classes=["result-table"],
        show_label=False,
        # container=True
    )

    # Add JavaScript to handle copy functionality
    copy_button.click(
        fn=None,
        inputs=[result_table],
        js="""
        function(text) {
            if (!text || text.trim() === '') {
                return [];
            }
            
            // Function to update button appearance
            function updateButton(button, success) {
                if (!button) return;
                const originalText = button.textContent || button.innerText;
                if (success) {
                    button.textContent = '✓ 已複製';
                    button.style.backgroundColor = '#4caf50';
                    button.style.color = '#ffffff';
                    setTimeout(function() {
                        button.textContent = originalText;
                        button.style.backgroundColor = '';
                        button.style.color = '';
                    }, 2000);
                }
            }
            
            // Find the copy button element
            const buttons = document.querySelectorAll('button');
            let copyBtn = null;
            for (let btn of buttons) {
                if (btn.textContent && (btn.textContent.includes('📋 複製') || btn.textContent.includes('複製'))) {
                    copyBtn = btn;
                    break;
                }
            }
            
            // Copy to clipboard
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function() {
                    updateButton(copyBtn, true);
                }).catch(function(err) {
                    console.error('Failed to copy text: ', err);
                    // Fallback method
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    textArea.style.position = 'fixed';
                    textArea.style.left = '-9999px';
                    textArea.style.top = '-9999px';
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    try {
                        const successful = document.execCommand('copy');
                        if (successful) {
                            updateButton(copyBtn, true);
                        }
                    } catch (err) {
                        console.error('Fallback copy failed: ', err);
                    }
                    document.body.removeChild(textArea);
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-9999px';
                textArea.style.top = '-9999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    const successful = document.execCommand('copy');
                    if (successful) {
                        updateButton(copyBtn, true);
                    }
                } catch (err) {
                    console.error('Copy failed: ', err);
                }
                document.body.removeChild(textArea);
            }
            
            return [];
        }
        """
    )
    
    return ResultDisplay(
        result_table=result_table, 
        result_table_without_prompt=result_table_without_prompt,
        copy_button=copy_button
    )

