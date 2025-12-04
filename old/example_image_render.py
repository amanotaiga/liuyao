"""
Example: Render Liu Yao Traditional Format Display as Image and HTML

This example demonstrates how to use the new image and HTML rendering features
for the Traditional Format Display.

Requirements:
    - Pillow (for image rendering): pip install Pillow
    - No additional requirements for HTML rendering
"""

from liu_yao import (
    six_yao_divination_from_date,
    format_liu_yao_display,
    format_liu_yao_display_as_image,
    format_liu_yao_display_as_html
)

def main():
    # Example: Create a divination
    hexagram_code = "111111"  # 乾为天
    date_str = "2025/12/01 19:00"
    changing_lines = [1]  # First line is changing
    
    print("Generating Liu Yao divination...")
    yao_list, result_json = six_yao_divination_from_date(
        hexagram_code,
        date_str,
        changing_lines
    )
    
    # Display traditional text format
    print("\n" + "="*70)
    print("Traditional Text Format:")
    print("="*70)
    print(format_liu_yao_display(yao_list, show_shen_sha=True))
    
    # Render as image
    print("\n" + "="*70)
    print("Rendering as Image...")
    print("="*70)
    try:
        # Option 1: Save directly
        format_liu_yao_display_as_image(
            yao_list,
            show_shen_sha=True,
            font_size=18,
            save_path="liu_yao_result.png"
        )
        print("✓ Image saved: liu_yao_result.png")
        
        # Option 2: Get image object and customize
        img = format_liu_yao_display_as_image(
            yao_list,
            show_shen_sha=True,
            font_size=20,
            background_color="white",
            text_color="black"
        )
        if img:
            # You can further manipulate the image here
            # img = img.resize((800, 600))
            img.save("liu_yao_result_custom.png")
            print("✓ Custom image saved: liu_yao_result_custom.png")
    except ImportError:
        print("✗ Pillow not installed. Install with: pip install Pillow")
    except Exception as e:
        print(f"✗ Error rendering image: {e}")
    
    # Render as HTML
    print("\n" + "="*70)
    print("Rendering as HTML...")
    print("="*70)
    try:
        # Traditional style
        html_traditional = format_liu_yao_display_as_html(
            yao_list,
            show_shen_sha=True,
            style="traditional"
        )
        with open("liu_yao_result_traditional.html", "w", encoding="utf-8") as f:
            f.write(html_traditional)
        print("✓ Traditional HTML saved: liu_yao_result_traditional.html")
        
        # Modern style
        html_modern = format_liu_yao_display_as_html(
            yao_list,
            show_shen_sha=True,
            style="modern"
        )
        with open("liu_yao_result_modern.html", "w", encoding="utf-8") as f:
            f.write(html_modern)
        print("✓ Modern HTML saved: liu_yao_result_modern.html")
    except Exception as e:
        print(f"✗ Error rendering HTML: {e}")
    
    print("\n" + "="*70)
    print("Done! Check the generated files.")
    print("="*70)

if __name__ == "__main__":
    main()

