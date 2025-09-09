import os
from PIL import Image, UnidentifiedImageError

# Use current folder (".") since images and script are in the same place
source_folder = "."
dest_folder = "converted"

# Make destination folder if needed
os.makedirs(dest_folder, exist_ok=True)

# Convert all JPG/JPEG files in the same folder
for filename in os.listdir(source_folder):
    name, ext = os.path.splitext(filename)
    if ext.lower() in [".jpg", ".jpeg"]:
        try:
            img = Image.open(os.path.join(source_folder, filename))
            img.save(os.path.join(dest_folder, f"{name}.png"), "PNG")
            print(f"Converted: {filename} -> {name}.png")
        except UnidentifiedImageError:
            print(f"Skipping (not a valid image): {filename}")

print("✅ All JPG images converted to PNG successfully!")
