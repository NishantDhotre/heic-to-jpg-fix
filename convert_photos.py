import os
import shutil
import time
from PIL import Image
from pillow_heif import register_heif_opener
from tqdm import tqdm
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Register HEIC opener
register_heif_opener()

SOURCE_DIR = 'raw'
DEST_DIR = 'converted'

def print_header():
    print("\n" + "="*60)
    print(f"{Fore.CYAN}{Style.BRIGHT}   📸  HEIC TO JPG CONVERSION DASHBOARD  📸{Style.RESET_ALL}")
    print("="*60 + "\n")

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

def print_summary(total, converted, copied, failed, elapsed_time):
    formatted_time = format_time(elapsed_time)
    print("\n" + "="*60)
    print(f"{Fore.GREEN}{Style.BRIGHT}   ✅  PROCESSING COMPLETE  ✅{Style.RESET_ALL}")
    print("="*60)
    print(f" ⏱️  {Fore.YELLOW}Time Elapsed:{Style.RESET_ALL}   {formatted_time}")
    print(f" 📂 {Fore.YELLOW}Total Files:{Style.RESET_ALL}    {total}")
    print("-" * 30)
    print(f" 🔄 {Fore.CYAN}Converted (HEIC):{Style.RESET_ALL} {converted}")
    print(f" 📋 {Fore.BLUE}Copied (Media):{Style.RESET_ALL}   {copied}")
    
    if failed > 0:
        print(f" ❌ {Fore.RED}Failed:{Style.RESET_ALL}           {failed}")
    else:
        print(f" ❌ {Fore.RED}Failed:{Style.RESET_ALL}           0")
    print("="*60 + "\n")

def convert_photos():
    if not os.path.exists(SOURCE_DIR):
        print(f"{Fore.RED}Error: Source directory '{SOURCE_DIR}' does not exist.{Style.RESET_ALL}")
        return

    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    files = [f for f in os.listdir(SOURCE_DIR) if not os.path.isdir(os.path.join(SOURCE_DIR, f))]
    total_files = len(files)
    
    start_time = time.time()
    
    stats = {
        'converted': 0,
        'copied': 0,
        'failed': 0
    }

    print_header()
    print(f"Using Source:      {Fore.YELLOW}{os.path.abspath(SOURCE_DIR)}{Style.RESET_ALL}")
    print(f"Using Destination: {Fore.YELLOW}{os.path.abspath(DEST_DIR)}{Style.RESET_ALL}")
    print(f"Total Files:       {total_files}\n")

    # Progress bar loop
    with tqdm(total=total_files, unit="file", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
        for filename in files:
            file_path = os.path.join(SOURCE_DIR, filename)
            name, ext = os.path.splitext(filename)
            ext_lower = ext.lower()

            # Update description (truncate if too long)
            desc_name = (filename[:25] + '..') if len(filename) > 25 else filename
            pbar.set_description(f"Processing {desc_name}")

            try:
                if ext_lower in ['.heic', '.heif']:
                    image = Image.open(file_path)
                    image = image.convert('RGB')
                    save_path = os.path.join(DEST_DIR, f"{name}.jpg")
                    image.save(save_path, "JPEG", quality=100, subsampling=0)
                    stats['converted'] += 1
                else:
                    shutil.copy2(file_path, os.path.join(DEST_DIR, filename))
                    stats['copied'] += 1
            except Exception as e:
                pbar.write(f"{Fore.RED}Error processing {filename}: {e}{Style.RESET_ALL}")
                stats['failed'] += 1
            
            pbar.update(1)

    elapsed = time.time() - start_time
    print_summary(total_files, stats['converted'], stats['copied'], stats['failed'], elapsed)

if __name__ == "__main__":
    convert_photos()
    input(f"\n{Fore.CYAN}Press Enter to exit...{Style.RESET_ALL}")
