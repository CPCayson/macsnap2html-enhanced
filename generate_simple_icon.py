#!/usr/bin/env python3
"""
Generate a simple folder icon for MacSnap2HTML app
Requires: pip install Pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Create a simple folder-style icon for the app"""
    
    # Create 1024x1024 image with transparent background
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Define colors
    folder_color = (255, 179, 71)  # Orange folder color
    folder_shadow = (200, 140, 55)  # Darker orange for depth
    accent_color = (102, 126, 234)  # Purple accent (matches app theme)
    
    # Draw folder base
    folder_width = int(size * 0.8)
    folder_height = int(size * 0.65)
    folder_x = (size - folder_width) // 2
    folder_y = int(size * 0.25)
    
    # Draw folder shadow
    shadow_offset = 8
    draw.rounded_rectangle(
        [folder_x + shadow_offset, folder_y + shadow_offset, 
         folder_x + folder_width + shadow_offset, folder_y + folder_height + shadow_offset],
        radius=20, fill=folder_shadow
    )
    
    # Draw main folder
    draw.rounded_rectangle(
        [folder_x, folder_y, folder_x + folder_width, folder_y + folder_height],
        radius=20, fill=folder_color
    )
    
    # Draw folder tab
    tab_width = int(folder_width * 0.4)
    tab_height = int(folder_height * 0.15)
    tab_x = folder_x + int(folder_width * 0.1)
    tab_y = folder_y - tab_height // 2
    
    draw.rounded_rectangle(
        [tab_x, tab_y, tab_x + tab_width, tab_y + tab_height],
        radius=8, fill=folder_color
    )
    
    # Add HTML accent
    html_size = int(size * 0.25)
    html_x = folder_x + folder_width - html_size - 20
    html_y = folder_y + 30
    
    # Draw HTML document
    draw.rounded_rectangle(
        [html_x, html_y, html_x + html_size, html_y + int(html_size * 1.3)],
        radius=8, fill='white'
    )
    
    # Add HTML text
    try:
        # Try to load a system font
        font_size = max(16, html_size // 8)
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw "HTML" text
    text = "HTML"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = html_x + (html_size - text_width) // 2
    text_y = html_y + html_size // 2
    
    draw.text((text_x, text_y), text, fill=accent_color, font=font)
    
    # Add some decorative lines on the HTML doc
    line_width = int(html_size * 0.7)
    line_x = html_x + (html_size - line_width) // 2
    line_spacing = font_size + 4
    
    for i in range(3):
        line_y = html_y + html_size + 10 + (i * line_spacing)
        draw.rectangle(
            [line_x, line_y, line_x + line_width, line_y + 2],
            fill=(200, 200, 200)
        )
    
    # Save as PNG first
    img.save('macsnap_icon.png', 'PNG')
    print("Created: macsnap_icon.png")
    
    return 'macsnap_icon.png'

def convert_to_icns(png_path):
    """Convert PNG to ICNS using the previous conversion function"""
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    try:
        original = Image.open(png_path)
        original = original.convert('RGBA')
        
        temp_images = []
        for size in sizes:
            resized = original.resize((size, size), Image.Resampling.LANCZOS)
            temp_images.append(resized)
        
        icns_path = 'app_icon.icns'
        temp_images[0].save(
            icns_path,
            format='ICNS',
            append_images=temp_images[1:],
            sizes=[(size, size) for size in sizes]
        )
        
        print(f"Created: {icns_path}")
        return icns_path
        
    except Exception as e:
        print(f"Error creating ICNS: {e}")
        return None

if __name__ == "__main__":
    # Check if Pillow is installed
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Please install Pillow: pip install Pillow")
        exit(1)
    
    # Create the icon
    png_file = create_app_icon()
    icns_file = convert_to_icns(png_file)
    
    if icns_file:
        print(f"\nIcon files created successfully!")
        print(f"PNG: {png_file}")
        print(f"ICNS: {icns_file}")
        print(f"\nNow rebuild your app with: python setup.py py2app")
    else:
        print("Failed to create ICNS file")