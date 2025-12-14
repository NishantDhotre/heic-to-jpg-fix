import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from converter_core import process_file_generator, format_time, get_file_list

# Setup appearance
ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HEIC to JPG Converter")
        self.geometry("700x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Spacer

        # Variables
        self.source_path = ctk.StringVar()
        self.dest_path = ctk.StringVar()
        self.is_running = False

        # Header
        self.header_label = ctk.CTkLabel(self, text="📸 HEIC to JPG Converter", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=20)

        # File Selection Frame
        self.frame_files = ctk.CTkFrame(self)
        self.frame_files.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frame_files.grid_columnconfigure(1, weight=1)

        # Source
        self.btn_source = ctk.CTkButton(self.frame_files, text="Select Source Folder", command=self.select_source)
        self.btn_source.grid(row=0, column=0, padx=10, pady=10)
        self.entry_source = ctk.CTkEntry(self.frame_files, textvariable=self.source_path, placeholder_text="Path to raw photos...")
        self.entry_source.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Destination (Optional)
        self.btn_dest = ctk.CTkButton(self.frame_files, text="Select Dest Folder", command=self.select_dest, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_dest.grid(row=1, column=0, padx=10, pady=10)
        self.entry_dest = ctk.CTkEntry(self.frame_files, textvariable=self.dest_path, placeholder_text="Optional (Defaults to 'converted' folder)")
        self.entry_dest.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Info Label
        self.info_label = ctk.CTkLabel(self, text="Ready to process.", text_color="gray")
        self.info_label.grid(row=2, column=0, padx=20, pady=(10, 0))

        # Progress
        self.progressbar = ctk.CTkProgressBar(self)
        self.progressbar.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.progressbar.set(0)

        # Stats Area
        self.textbox = ctk.CTkTextbox(self, height=150)
        self.textbox.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox.insert("0.0", "Logs will appear here...\n")

        # Action Buttons
        self.btn_start = ctk.CTkButton(self, text="START CONVERSION", command=self.start_thread, height=50, font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_start.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

        # Attempt to auto-detect 'raw' folder
        if os.path.exists('raw'):
            self.source_path.set(os.path.abspath('raw'))
            self.update_info()

    def select_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_path.set(folder)
            self.update_info()

    def select_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_path.set(folder)

    def update_info(self):
        src = self.source_path.get()
        if os.path.isdir(src):
            files = get_file_list(src)
            self.info_label.configure(text=f"Found {len(files)} files in selected folder.")
        else:
            self.info_label.configure(text="Invalid source folder.")

    def start_thread(self):
        if self.is_running:
            return
        if not self.source_path.get():
            messagebox.showerror("Error", "Please select a source folder.")
            return

        self.is_running = True
        self.btn_start.configure(state="disabled", text="PROCESSING...")
        self.textbox.delete("0.0", "end")
        
        thread = threading.Thread(target=self.run_process)
        thread.start()

    def run_process(self):
        source = self.source_path.get()
        dest = self.dest_path.get()
        
        if not dest:
            dest = os.path.join(source, "converted")

        gen = process_file_generator(source, dest)
        
        for filename, stats in gen:
            # Update GUI from thread
            progress = stats.processed / stats.total_files if stats.total_files > 0 else 0
            self.progressbar.set(progress)
            
            # Update text log every few files or important events
            log_msg = f"Processed: {filename} ({stats.processed}/{stats.total_files})\n"
            self.textbox.insert("end", log_msg)
            self.textbox.see("end")
            
            # Simple header update
            self.info_label.configure(text=f"Processing... {int(progress*100)}%")

        # Finish
        formatted_time = format_time(stats.elapsed)
        summary = f"\n✅ DONE!\nTime: {formatted_time}\nConverted: {stats.converted}\nCopied: {stats.copied}\nFailed: {stats.failed}\n"
        self.textbox.insert("end", summary)
        self.info_label.configure(text="Processing Complete.")
        self.btn_start.configure(state="normal", text="START CONVERSION")
        self.is_running = False
        self.progressbar.set(1)

if __name__ == "__main__":
    app = App()
    app.mainloop()
