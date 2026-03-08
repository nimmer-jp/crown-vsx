from PIL import Image, ImageDraw

# Create a 256x256 image
size = 256
img = Image.new('RGBA', (size, size), (40, 44, 52, 255)) # Dark gray background

draw = ImageDraw.Draw(img)

# Draw a crown shape (banana yellow color)
# A simple 3-point or 5-point crown
points = [
    (30, 80),      # left top point
    (60, 180),     # left inner bottom
    (128, 50),     # center top point
    (196, 180),    # right inner bottom
    (226, 80),     # right top point
    (210, 200),    # right bottom corner
    (46, 200),     # left bottom corner
]

# Better 5-point crown shape
points = [
    (40, 80),      # left peak
    (80, 130),     # left valley
    (128, 50),     # center peak
    (176, 130),    # right valley
    (216, 80),     # right peak
    (200, 190),    # right base
    (56, 190)      # left base
]

draw.polygon(points, fill=(255, 225, 53, 255)) # Banana yellow

# Draw a base line for the crown
draw.rectangle([(50, 200), (206, 215)], fill=(255, 225, 53, 255), radius=5 if hasattr(draw, 'rounded_rectangle') else 0)

# Save the image
img.save('icon.png')
print("icon.png generated.")
