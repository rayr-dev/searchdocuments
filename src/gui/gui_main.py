# gui/gui_main.py

#Constants
#TODO: Add constants where necessary

# ---------------------------------------------------------
# Global splash handle (must exist before any function uses it)
# ---------------------------------------------------------
pyi_splash = None

# ---------------------------------------------------------
# Imports with diagnostics
# ---------------------------------------------------------
#System Imports
import os
import sys
import time

#Local imports
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import config
from orchestrator import run_reconciliation
from utilities.logging_setup import init_logging, diag
import logging

# ---------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------
def main():
    launch_gui()

# ---------------------------------------------------------
# GUI BUILDER
# ---------------------------------------------------------
def launch_gui():
    # -----------------------------
    # Optional PyInstaller splash
    # -----------------------------
    # Only attempts splash if frozen

    diag("GUI Main: Starting launch gui")
    logging.info("Logging Info")
    logging.warning("Warning Info")
    logging.error("Error info")
    logging.exception("Exception Info")
    logging.critical("Critical Info")

    if getattr(sys, 'frozen', False):
        try:
            import pyi_splash
            pyi_splash.update_text("Loading GUI...")
            time.sleep(2.0) # delay in seconds
            pyi_splash.close()
        except Exception:
            pass


    # -----------------------------
    # Main Window
    # -----------------------------
    root = tk.Tk()
    root.title("Search Documents Tool")
    root.geometry("900x900")
    root.resizable(False, False)

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
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", padx=20)

    output_entry = tk.Entry(root, textvariable=output_dir_var, width=60)
    output_entry.pack(anchor="w", padx=20)

    tk.Button(
        root,
        text="Browse",
        command=browse_output_dir
    ).pack(anchor="w", padx=20, pady=(0, 20))

    # -----------------------------
    # Folder A
    # -----------------------------
    tk.Label(
        root,
        text="Folder A (Source):",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", padx=20)

    folderA_entry = tk.Entry(root, textvariable=folderA_var, width=60)
    folderA_entry.pack(anchor="w", padx=20)

    tk.Button(root,text="Browse",command=lambda: folderA_var.set(filedialog.askdirectory())).pack(anchor="w", padx=20, pady=(0, 10))

    # -----------------------------
    # Folder B
    # -----------------------------
    tk.Label(root,
             text="Folder B (Target):",
             font=("Segoe UI", 10, "bold")
             ).pack(anchor="w",
                    padx=20)
    folderB_entry = tk.Entry(root,textvariable=folderB_var,width=60)
    folderB_entry.pack(anchor="w",padx=20)
    tk.Button(root,text="Browse",command=lambda: folderB_var.set(filedialog.askdirectory())).pack(anchor="w",padx=20,pady=(0, 10)
                )
    # -----------------------------
    # Comparison Options
    # -----------------------------
    tk.Label(root,
             text="Comparison Options:",
             font=("Segoe UI", 10, "bold")).pack(anchor="w",
                                                 padx=20)

    tk.Radiobutton(root,
                   text="Timestamp Comparison(Fastest)",
                   variable=compare_mode_var,
                   value="timestamp").pack(anchor="w", padx=40)
    tk.Radiobutton(root,
                   text="Hash Comparison(Accurate Slower)",
                   variable=compare_mode_var,
                   value="hash").pack(anchor="w", padx=40)
    tk.Radiobutton(root,
                   text="Hash-Only Mode (Accurate Moderate speed)",
                   variable=compare_mode_var, value="hashonly").pack(anchor="w", padx=40)

    # -----------------------------
    # Find all Files Options
    # -----------------------------
    tk.Label(root, text="Find All Files (multiple files is Source location:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)

    tk.Checkbutton(root, text="Find All Files",
                   variable=find_all_var).pack(anchor="w",
                                             padx=40)

    # -----------------------------
    # Cleanup Options
    # -----------------------------
    tk.Label(root, text="Cleanup Options:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)

    tk.Checkbutton(root, text="Dry Run (No Changes Made)",
                   variable=dryrun_var).pack(anchor="w",
                                             padx=40)

    tk.Checkbutton(root, text="Delete Exact Matches",
                   variable=deletematches_var).pack(anchor="w",
                                                    padx=40)

    tk.Checkbutton(root, text="Delete Mismatch Candidates",
                   variable=deletecandidates_var).pack(anchor="w",
                                                       padx=40)

    tk.Checkbutton(root, text="Use Quarantine Folder",
                   variable=quarantine_var).pack(anchor="w",
                                                 padx=40)

    # -----------------------------
    # Run Button Handler
    # -----------------------------
    def run_clicked():

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

        log_path = init_logging(output_dir, diagnostic=config.DIAGNOSTIC_MODE)
        logging.info(f"GUI Log file created: {log_path}")
        diag("Run button clicked")
        diag(f"FolderA: {folderA}")
        diag(f"FolderB: {folderB}")
        diag(f"Output: {output_dir}")
        diag(f"Mode: {mode}")
        diag(f"Dry Run: {dryrun_var.get()}")
        diag(f"Exact Matches: {deletematches_var.get()}")
        diag(f"Delete Candidates: {deletecandidates_var.get()}")
        diag(f"Quarantive: {quarantine_var.get()}")
        diag(f"Find All Files: {find_all_var.get()}")


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
            diag(f"GUI ERROR: {e}")

        # -----------------------------
        # Run Button (must be AFTER summary_box exists)
        # ---------------------------------------------------------
        # Run Button (must be AFTER validator exists)
        # ---------------------------------------------------------
        run_button = tk.Button(root,
                               text="Run Comparison",
                               font=("Segoe UI", 11, "bold"),
                               width=20,
                               command=run_clicked,
                               state="disabled")  # start disabled
        run_button.pack(pady=20)
    # ---------------------------------------------------------
    # Run Button (must be AFTER validator exists)
    # ---------------------------------------------------------
    run_button=tk.Button(root,text="Run Comparison",font=("Segoe UI",11,"bold"),width=20,command=run_clicked,state="disabled") # start disabled

    run_button.pack(pady=20)

    # ---------------------------------------------------------
    # VALIDATION FUNCTION (placed here so it sees all widgets)
    # ---------------------------------------------------------
    def validate_all_paths():
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
    # Find All Files
    # -----------------------------


    # -----------------------------
    # Status + Progress Bar
    # -----------------------------
    status_var = tk.StringVar(value="Ready")
    tk.Label(root, textvariable=status_var, font=("Segoe UI", 10, "bold"),
             anchor="w").pack(fill="x", padx=20, pady=(10, 0))

    progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
    progress.pack(padx=20, pady=(0, 10))

    def set_status(msg):
        status_var.set(msg)
        root.update_idletasks()

    def set_progress(value, maximum=100):
        progress["maximum"] = maximum
        progress["value"] = value
        root.update_idletasks()

    # -----------------------------
    # Summary Output (MUST come before Run button)
    # -----------------------------
    tk.Label(root, text="Summary:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)

    summary_frame = tk.Frame(root)
    summary_frame.pack(fill="both", expand=True, padx=20, pady=10)

    scrollbar = tk.Scrollbar(summary_frame)
    scrollbar.pack(side="right", fill="y")

    summary_box = tk.Text(summary_frame, width=80, height=15, yscrollcommand=scrollbar.set)
    summary_box.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=summary_box.yview)



    root.mainloop()

# ---------------------------------------------------------
# ENTRY POINT FOR SCRIPT + EXE
# ---------------------------------------------------------
if __name__ == "__main__":
    main()

