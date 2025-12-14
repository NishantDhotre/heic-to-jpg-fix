import os
import shutil
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIC opener
register_heif_opener()

SOURCE_DIR = 'raw'
DEST_DIR = 'converted'

def convert_photos():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory '{SOURCE_DIR}' does not exist.")
        return

    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    files = os.listdir(SOURCE_DIR)
    print(f"Found {len(files)} files in '{SOURCE_DIR}'...")

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        
        if os.path.isdir(file_path):
            continue

        name, ext = os.path.splitext(filename)
        ext_lower = ext.lower()

        if ext_lower in ['.heic', '.heif']:
            print(f"Converting: {filename}")
            try:
                image = Image.open(file_path)
                # Convert to RGB to ensure compatibility
                image = image.convert('RGB')
                save_path = os.path.join(DEST_DIR, f"{name}.jpg")
                # Save with maximum quality and no subsampling to preserve detail
                image.save(save_path, "JPEG", quality=100, subsampling=0)
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")
        else:
            print(f"Copying: {filename}")
            try:
                shutil.copy2(file_path, os.path.join(DEST_DIR, filename))
            except Exception as e:
                print(f"Failed to copy {filename}: {e}")

    print("Processing complete.")

if __name__ == "__main__":
    convert_photos()
