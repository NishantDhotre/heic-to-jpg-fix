import os
import argparse
import time
from tqdm import tqdm
from colorama import init, Fore, Style
from converter_core import process_file_generator, format_time, get_file_list

# Initialize colorama
init(autoreset=True)

def print_header():
    print("\n" + "="*60)
    print(f"{Fore.CYAN}{Style.BRIGHT}   📸  HEIC TO JPG CONVERSION DASHBOARD  📸{Style.RESET_ALL}")
    print("="*60 + "\n")

def print_summary(stats):
    formatted_time = format_time(stats.elapsed)
    print("\n" + "="*60)
    print(f"{Fore.GREEN}{Style.BRIGHT}   ✅  PROCESSING COMPLETE  ✅{Style.RESET_ALL}")
    print("="*60)
    print(f" ⏱️  {Fore.YELLOW}Time Elapsed:{Style.RESET_ALL}   {formatted_time}")
    print(f" 📂 {Fore.YELLOW}Total Files:{Style.RESET_ALL}    {stats.total_files}")
    print("-" * 30)
    print(f" 🔄 {Fore.CYAN}Converted (HEIC):{Style.RESET_ALL} {stats.converted}")
    print(f" 📋 {Fore.BLUE}Copied (Media):{Style.RESET_ALL}   {stats.copied}")
    
    if stats.failed > 0:
        print(f" ❌ {Fore.RED}Failed:{Style.RESET_ALL}           {stats.failed}")
    else:
        print(f" ❌ {Fore.RED}Failed:{Style.RESET_ALL}           0")
    print("="*60 + "\n")

def get_directories():
    parser = argparse.ArgumentParser(description="Convert HEIC photos to JPG.")
    parser.add_argument("--input", "-i", type=str, help="Input directory containing photos")
    parser.add_argument("--output", "-o", type=str, help="Output directory for converted photos")
    args = parser.parse_args()

    source_dir = args.input
    dest_dir = args.output

    if not source_dir:
        if os.path.exists('raw'):
            source_dir = 'raw'
        else:
            print_header()
            print(f"{Fore.YELLOW}Default 'raw' folder not found.{Style.RESET_ALL}")
            while not source_dir or not os.path.exists(source_dir):
                source_dir = input(f"{Fore.CYAN}Please enter the path to your photos: {Style.RESET_ALL}").strip().strip('"').strip("'")
                if not os.path.exists(source_dir):
                    print(f"{Fore.RED}Error: Directory not found. Try again.{Style.RESET_ALL}")

    if not dest_dir:
        if source_dir == 'raw':
             dest_dir = 'converted'
        else:
             dest_dir = os.path.join(source_dir, 'converted')

    return source_dir, dest_dir

def run_cli():
    source_dir, dest_dir = get_directories()
    
    # Check if files exist before starting generator
    files_check = get_file_list(source_dir)
    if not files_check:
         print(f"{Fore.RED}No files found in source directory!{Style.RESET_ALL}")
         return

    print_header()
    print(f"Using Source:      {Fore.YELLOW}{os.path.abspath(source_dir)}{Style.RESET_ALL}")
    print(f"Using Destination: {Fore.YELLOW}{os.path.abspath(dest_dir)}{Style.RESET_ALL}")
    print(f"Total Files:       {len(files_check)}\n")

    # Run generator
    gen = process_file_generator(source_dir, dest_dir)
    
    # We need to initialize pbar after we know total, which the generator calculates, 
    # but for CLI we usually want the pbar immediately. 
    # Helper: get stats object from first yield or pre-calculate?
    # Actually, let's just use the file check len for pbar total.
    
    total = len(files_check)
    last_stats = None

    with tqdm(total=total, unit="file", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
        for filename, stats in gen:
            last_stats = stats
            desc_name = (filename[:25] + '..') if len(filename) > 25 else filename
            pbar.set_description(f"Processing {desc_name}")
            pbar.update(1)

    if last_stats:
        print_summary(last_stats)

if __name__ == "__main__":
    try:
        run_cli()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Process cancelled by user.{Style.RESET_ALL}")
    except Exception as e:
         print(f"\n{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.CYAN}Press Enter to exit...{Style.RESET_ALL}")
