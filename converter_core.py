import os
import shutil
import time
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIC opener
register_heif_opener()

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.0f}s"

class ConversionStats:
    def __init__(self):
        self.converted = 0
        self.copied = 0
        self.failed = 0
        self.start_time = time.time()
        self.total_files = 0
        self.processed = 0

    @property
    def elapsed(self):
        return time.time() - self.start_time

def get_file_list(source_dir):
    try:
        return [f for f in os.listdir(source_dir) if not os.path.isdir(os.path.join(source_dir, f))]
    except:
        return []

def process_file_generator(source_dir, dest_dir):
    """
    Generator that processes files and yields (current_file_name, stats_object)
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    files = get_file_list(source_dir)
    stats = ConversionStats()
    stats.total_files = len(files)

    for filename in files:
        file_path = os.path.join(source_dir, filename)
        name, ext = os.path.splitext(filename)
        ext_lower = ext.lower()

        try:
            if ext_lower in ['.heic', '.heif']:
                image = Image.open(file_path)
                image = image.convert('RGB')
                save_path = os.path.join(dest_dir, f"{name}.jpg")
                image.save(save_path, "JPEG", quality=100, subsampling=0)
                stats.converted += 1
            else:
                shutil.copy2(file_path, os.path.join(dest_dir, filename))
                stats.copied += 1
        except Exception as e:
            # yield error? For now just count it
            stats.failed += 1
        
        stats.processed += 1
        yield filename, stats

