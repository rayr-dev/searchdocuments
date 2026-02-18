# Reconciliation Tool — User Guide

The Reconciliation Tool is a fast, reliable utility for comparing two folders of documents and identifying:

- Files that match exactly  
- Files that exist in both folders but differ  
- Files that are missing from one folder  
- Files that appear in multiple locations  

It produces clear Excel, CSV, and text reports and can optionally delete or quarantine duplicate or outdated files.

This guide explains how to run the tool, what each mode does, and how to interpret the results.

---

## 1. What the Tool Does

The Reconciliation Tool compares **Folder A** (the source) to **Folder B** (the target).  
For every file in Folder A, it checks Folder B for:

### ✔ Exact matches  
Same name + same timestamp/size/hash.

### ✔ Mismatches  
Same name but different content or metadata.

### ✔ Missing files  
Files present in A but not in B.

### ✔ Multiple matches  
If the same filename appears in multiple locations in B, the tool can list all of them.

### ✔ Optional cleanup  
You can choose to:

- Delete exact matches  
- Delete mismatch candidates  
- Move files to a quarantine folder  
- Perform a dry‑run (no changes made)

---

## 2. How to Run the Tool

When you launch the EXE, you’ll see a simple interface:

1. Select **Folder A**  
2. Select **Folder B**  
3. Choose your comparison options  
4. Choose your deletion/quarantine options  
5. Click **Run Comparison**

The tool will:

- Scan both folders  
- Compare files  
- Generate Excel, CSV, and text reports  
- Perform optional cleanup actions  

---

## 3. Understanding the Output Files

After running the comparison, the tool creates three output files in the same directory as the EXE:

### 3.1 Excel Report (`comparison.xlsx`)

This is the most user‑friendly output.

It includes:

| Color | Meaning |
|-------|---------|
| **Green** | Exact match |
| **Yellow** | Mismatch |
| **Red** | Missing in Folder B |

Each row shows:

- Status  
- Filename  
- Full path in A  
- Timestamp in A  
- Full path in B  
- Timestamp in B  

If a file appears multiple times in Folder B, each location is listed separately.

---

### 3.2 CSV Report (`comparison.csv`)

A spreadsheet‑friendly version of the same data.  
Useful for importing into Excel, Access, or other systems.

---

### 3.3 Text Report (`comparison.txt`)

A simple, readable summary grouped into:

- Exact Matches  
- Mismatches  
- Missing Files  

---

## 4. Comparison Modes

### 4.1 Timestamp Comparison  
Fastest method.  
Files match if their timestamps are within 1 second.

### 4.2 Size Comparison  
Files match if their sizes are identical.

### 4.3 Hash Comparison  
Files match if their SHA‑256 hash is identical.  
Most accurate, slower.

### 4.4 Hash‑Only Mode  
Ignores timestamps and sizes.  
Uses only SHA‑256 hashing.

### 4.5 Find‑All‑Locations Mode  
If a file appears multiple times in Folder B, all locations are listed.

---

## 5. Deletion and Quarantine Options

### 5.1 Dry‑Run Mode  
No files are deleted or moved.  
Actions are logged only.

### 5.2 Delete Exact Matches  
Removes files from Folder B that match Folder A exactly.

### 5.3 Delete Mismatch Candidates  
Removes files from Folder B that have the same name but different content.

### 5.4 Quarantine Mode  
Instead of deleting files, moves them into a **Quarantine** folder created next to the EXE.

This is the safest cleanup option.

---

## 6. Logs

All deletion or quarantine actions are recorded in:

## File_compare_deletions.logged
This includes:

- Timestamp  
- Action (deleted, quarantined, dry‑run)  
- File path  
- Reason (exact match, mismatch, duplicate)  

---

## 7. System Requirements

- Windows 10 or later  
- Python not required (EXE is standalone)  
- No admin rights needed unless deleting protected files  

---

## 8. Troubleshooting

### “Access Denied” errors  
The file may be locked or require admin permissions.

### Excel report won’t open  
Ensure Excel is installed and not already running in safe mode.

### Quarantine folder not created  
Check that the EXE has permission to write to its directory.

---

## 9. Support

For questions, enhancements, or bug reports, contact the developer or submit an issue in the repository.
