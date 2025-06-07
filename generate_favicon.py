import base64
from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon(size):
    # Create a new image with a white background
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a blue circle
    circle_color = (0, 123, 255)  # Bootstrap primary blue
    draw.ellipse([2, 2, size-2, size-2], fill=circle_color)
    
    # Add text "SMS" in white
    try:
        font = ImageFont.truetype("arial.ttf", size//2)
    except:
        font = ImageFont.load_default()
    
    text = "SMS"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    return image

def main():
    # Create static/image directory if it doesn't exist
    os.makedirs('static/image', exist_ok=True)
    
    # Generate favicon.ico (32x32)
    favicon = create_favicon(32)
    favicon.save('static/image/favicon.ico', format='ICO')
    print('Created favicon.ico')

if __name__ == '__main__':
    main() 