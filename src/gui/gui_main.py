# gui/gui_main.py

# System
import os
import sys
import time
import config
import logging

#3d Party
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

#local
from orchestrator import run_reconciliation
from utilities.logging_setup import init_logging, diag
from utilities.path_utils import get_version, get_version_info

# ---------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------
def main():
    # This is correct - set up before GUI launches
    # -----------------------------
    # Optional PyInstaller splash
    # -----------------------------
    # Only attempts splash if frozen

    if getattr(sys, 'frozen', False):
        try:
            import pyi_splash
            pyi_splash.update_text("Loading GUI...")
            time.sleep(1)  # delay in seconds
            pyi_splash.close()
        except Exception:
            pass
        # -----------------------------
        # # Step 1 - read version first
        # -----------------------------

    version = get_version()
    info = get_version_info()

    diag("GUI Main: Starting launch gui")

    # -----------------------------
    # Main Window
    # -----------------------------
    root = tk.Tk()
    root.title(f"Search Documents v{version}")  # ← now root exists
    root.geometry("1100x1000")
    root.resizable(True,
                   True)  # allow resizing
    root.minsize(800, 1000
                 )  # Min size
    root.configure(background="white")

    launch_gui(root, info)

# ---------------------------------------------------------
# GUI BUILDER
# ---------------------------------------------------------
def launch_gui(root, info):
    # -----------------------------
    # Menu Bar
    # -----------------------------
    menubar = tk.Menu(root)

    # -----------------------------
    # About Dialog
    # -----------------------------
    def show_about():
        about_text = (
            f"Search Documents Tool\n\n"
            f"Version:     {info['version']}\n"
            f"Build:       {info['build']}\n"
            f"Author:      {info['author']}\n"
            f"Description: {info['description']}\n"
            f"Release:     {info['release']}\n"
        )
        messagebox.showinfo("About Search Documents", about_text)

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="About", command=show_about)
    menubar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menubar)

    # -----------------------------
    # Tkinter Variables
    # -----------------------------
    folderA_var = tk.StringVar()
    folderB_var = tk.StringVar()
    output_dir_var = tk.StringVar()

    compare_mode_var = tk.StringVar(value="timestamp")

    find_all_var = tk.BooleanVar()
    dryrun_var = tk.BooleanVar(value=True)
    deletematches_var = tk.BooleanVar()
    deletecandidates_var = tk.BooleanVar()
    quarantine_var = tk.BooleanVar(value=True)
    diagnostics_var = tk.BooleanVar(value=False) # Diagnostics

    # -----------------------------
    # Helper: Folder Browsers
    # -----------------------------
    def browse_folderA():
        path = filedialog.askdirectory()
        if path:
            folderA_var.set(path)

    def browse_folderB():
        path = filedialog.askdirectory()
        if path:
            folderB_var.set(path)

    def browse_output_dir():
        path = filedialog.askdirectory()
        if path:
            output_dir_var.set(path)

    # -----------------------------
    # Output Folder
    # -----------------------------
    tk.Label(
        root,
        text="Output Folder:",
        bg="white",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w",
           padx=20)

    output_entry = tk.Entry(root,
                            textvariable=output_dir_var,
                            width=60)
    output_entry.pack(anchor="w",
                      padx=20)

    tk.Button(
        root,
        text="Browse",
        command=browse_output_dir
    ).pack(anchor="w",
           padx=20,
           pady=(0, 20))

    # -----------------------------
    # Folder A
    # -----------------------------
    tk.Label(
        root,
        text="Folder A (Source):",
        bg="white",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w",
           padx=20)

    folderA_entry = tk.Entry(root, textvariable=folderA_var,
                             width=60)
    folderA_entry.pack(anchor="w",
                       padx=20)

    tk.Button(root,
              text="Browse",
              command=lambda: folderA_var.set(filedialog.askdirectory())).pack(anchor="w",
                                                                               padx=20,
                                                                               pady=(0, 10))

    # -----------------------------
    # Folder B
    # -----------------------------
    tk.Label(root,
             text="Folder B (Target):",
             bg="white",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w",
                    padx=20)
    folderB_entry = tk.Entry(root,
                             textvariable=folderB_var,
                             width=60)
    folderB_entry.pack(anchor="w",
                       padx=20)
    tk.Button(root,
              text="Browse",
              command=lambda: folderB_var.set(filedialog.askdirectory())).pack(anchor="w",
                                                                               padx=20,
                                                                               pady=(0, 10)
                )
    ttk.Separator(root, orient="horizontal").pack(fill="x", padx=20, pady=10)
    # -----------------------------
    # Comparison Options
    # -----------------------------
    tk.Label(root,
             text="Comparison Options:",
             bg="white",
             font=("Segoe UI", 10, "bold")).pack(anchor="w",
                                                 padx=20)

    tk.Radiobutton(root,
                   text="Timestamp Comparison(Fastest)",
                   bg="white",
                   variable=compare_mode_var,
                   value="timestamp").pack(anchor="w",
                                           padx=40)
    tk.Radiobutton(root,
                   text="Hash Comparison(Accurate Slower)",
                   bg="white",
                   variable=compare_mode_var,
                   value="hash").pack(anchor="w",
                                      padx=40)
    tk.Radiobutton(root,
                   text="Hash-Only Mode (Accurate Moderate speed)",
                   bg="white",
                   variable=compare_mode_var, value="hashonly").pack(anchor="w",
                                                                     padx=40)

    ttk.Separator(root, orient="horizontal").pack(fill="x", padx=20, pady=10)

    # -----------------------------
    # Find all Files Options
    # -----------------------------
    tk.Label(root,
             text="Find All Files (multiple files is Source location:",
             bg="white",
             font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)

    tk.Checkbutton(root, text="Find All Files",
                   bg="white",
                   variable=find_all_var).pack(anchor="w",
                                             padx=40)

    ttk.Separator(root, orient="horizontal").pack(fill="x", padx=20, pady=10)

    # -----------------------------
    # Cleanup Options
    # -----------------------------
    tk.Label(root,
             text="Cleanup Options:",
             bg="white",
             font=("Segoe UI",
                   10,
                   "bold")).pack(anchor="w", padx=20)

    tk.Checkbutton(root, text="Dry Run (No Changes Made)",
                   bg="white",
                   variable=dryrun_var).pack(anchor="w",
                                             padx=40)

    tk.Checkbutton(root, text="Delete Exact Matches",
                   bg="white",
                   variable=deletematches_var).pack(anchor="w",
                                                    padx=40)

    tk.Checkbutton(root, text="Delete Mismatch Candidates",
                   bg="white",
                   variable=deletecandidates_var).pack(anchor="w",
                                                       padx=40)

    tk.Checkbutton(root, text="Use Quarantine Folder",
                   bg="white",
                   variable=quarantine_var).pack(anchor="w",
                                                 padx=40)

    ttk.Separator(root, orient="horizontal").pack(fill="x", padx=20, pady=10)

    # -----------------------------
    # Output Diagnostics
    # -----------------------------
    tk.Label(
        root,
        text="Output Detail Level:",
        bg="white",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w",
           padx=20)

    tk.Checkbutton(
        root,
        text="Diagnostic Output",
        bg="white",
        variable=diagnostics_var
    ).pack(anchor="w",
           padx=20,
           pady=(10, 10))

    # -----------------------------
    # Status Label
    # -----------------------------
    status_label = tk.Label(root,
                            text="Status: Ready",
                            anchor="w",
                            bg="white",
                            font=("Segoe UI", 10),
                            relief="sunken",
                            borderwidth=1,)
    status_label.pack(fill="x",
                      padx=20,
                      pady=(10, 0))

    def set_status(msg):
        status_label.config(text=f"Status: {msg}")

    # -----------------------------
    # Progress Bar
    # -----------------------------
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root,
                                   variable=progress_var,
                                   maximum=100
                                   )
    progress_bar.pack(fill="x",
                      padx=20,
                      pady=(0, 10))

    def set_progress(value):
        progress_var.set(value)
        root.update_idletasks()

    # -----------------------------
    # Status Callback
    # -----------------------------
    def gui_status_callback(message: str, level="high"):
        include_diag = diagnostics_var.get()
        if level == "detailed" and not include_diag:
            return
        summary_box.insert("end", message + "\n")
        summary_box.see("end")

    # -----------------------------
    # Run Button Handler
    # -----------------------------
    def run_clicked():

        try:
            print(f"Run clicked - FolderA: {folderA_var.get()}")
            print(f"FolderB: {folderB_var.get()}")
            print(f"Output: {output_dir_var.get()}")
        except Exception as e:
            print(f"Early error: {e}")

        folderA = folderA_var.get()
        folderB = folderB_var.get()
        output_dir = output_dir_var.get()
        mode = compare_mode_var.get()

        config.initialize_runtime()

        config.HASH_ONLY_MODE = (mode == "hashonly")
        config.HASH_COMPARE_MODE = (mode == "hash")

        config.FIND_ALL_LOCATIONS_MODE = find_all_var.get()
        config.DRY_RUN = dryrun_var.get()
        config.DELETE_EXACT_MATCHES = deletematches_var.get()
        config.DELETE_CANDIDATES = deletecandidates_var.get()
        config.USE_QUARANTINE = quarantine_var.get()
        config.DIAGNOSTIC_MODE = diagnostics_var.get()

        log_path = init_logging(output_dir, diagnostic=config.DIAGNOSTIC_MODE)
        logging.info(f"GUI Log file created: {log_path}")
        diag("Run button clicked")
        diag(f"FolderA: {folderA}")
        diag(f"FolderB: {folderB}")
        diag(f"Output: {output_dir}")
        diag(f"Mode: {mode}")
        diag(f"Dry Run: {config.DRY_RUN}")
        diag(f"Exact Matches: {config.HASH_ONLY_MODE}")
        diag(f"Delete Candidates: {config.DELETE_CANDIDATES}")
        diag(f"Quarantine: {config.USE_QUARANTINE}")
        diag(f"Find All Files: {config.FIND_ALL_LOCATIONS_MODE}")

        try:
            set_status("Starting comparison...")
            set_progress(0)

            results, summary_text = run_reconciliation(
                folderA,
                folderB,
                output_dir,
                progress_callback=set_progress,
                status_callback=set_status
            )

            summary_box.delete("1.0", tk.END)
            summary_box.insert(tk.END, summary_text)

            set_status("Summary ready.")
            messagebox.showinfo("Done", "Comparison complete. Output files created.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
            logging.error(f"GUI ERROR: {e}")
            diag(f"GUI ERROR: {e}")

    # ---------------------------------------------------------
    # VALIDATION FUNCTION (placed here so it sees all widgets)
    # ---------------------------------------------------------
    def validate_all_paths(*args):
        a = folderA_var.get().strip()
        b = folderB_var.get().strip()
        o = output_dir_var.get().strip()

        validA = os.path.isdir(a)
        validB = os.path.isdir(b)
        validO = os.path.isdir(o)

        folderA_entry.config(bg="white" if validA or not a else "#ffcccc")
        folderB_entry.config(bg="white" if validB or not b else "#ffcccc")
        output_entry.config(bg="white" if validO or not o else "#ffcccc")

        run_button.config(state="normal" if (validA and validB and validO) else "disabled")

    folderA_var.trace_add("write", validate_all_paths)
    folderB_var.trace_add("write", validate_all_paths)
    output_dir_var.trace_add("write", validate_all_paths)



    # ---------------------------------------------------------
    # Bind validation to typing + focus loss
    # ---------------------------------------------------------
    folderA_var.trace_add("write",
                          lambda *args: validate_all_paths())
    folderB_var.trace_add("write",
                          lambda *args: validate_all_paths())
    output_dir_var.trace_add("write",
                             lambda *args: validate_all_paths())

    folderA_entry.bind("<FocusOut>",
                       lambda e: validate_all_paths())
    folderB_entry.bind("<FocusOut>",
                       lambda e: validate_all_paths())
    output_entry.bind("<FocusOut>",
                      lambda e: validate_all_paths())

    # -----------------------------
    # Run Button
    # -----------------------------
    run_button = tk.Button(
        root,
        text="Run Comparison",
        font=("Segoe UI", 11, "bold"),
        width=20,
        command=run_clicked,
        state="disabled"
    )
    run_button.pack(pady=20)

    # -----------------------------
    # Summary Output (MUST come before Run button)
    # -----------------------------
    tk.Label(root,
             text="Summary:",
             bg="white",
             font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)

    summary_frame = tk.Frame(root)
    summary_frame.pack(fill="both",
                       expand=True,
                       padx=20, pady=10)

    scrollbar = tk.Scrollbar(summary_frame)
    scrollbar.pack(side="right",
                   fill="y")

    summary_box = tk.Text(summary_frame,
                          width=80,
                          height=15,
                          yscrollcommand=scrollbar.set)
    summary_box.pack(side="left",
                     fill="both",
                     expand=True)

    scrollbar.config(command=summary_box.yview)


    root.mainloop()

# ---------------------------------------------------------
# ENTRY POINT FOR SCRIPT + EXE
# ---------------------------------------------------------
if __name__ == "__main__":
    main()

