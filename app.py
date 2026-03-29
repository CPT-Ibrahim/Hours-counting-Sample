import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import defaultdict
import json
import os
import sys
import subprocess
from io import BytesIO
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas

# ── Constants ─────────────────────────────────────────────────────────────────
RECEIPT_WIDTH  = 3.15 * inch
RECEIPT_HEIGHT = 9 * inch
SUMATRA_PATH   = r"C:\SumatraPDF\SumatraPDF.exe"
TEMP_DIR       = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")

employee_names = ["Ahmad", "Ibraheem", "Hamza", "Zein", "Mohammad", "Suha", "Tasnem", "Saeb"]

# ── Shared state ──────────────────────────────────────────────────────────────
employee_data = defaultdict(list)
timers = {}

# ── File paths ────────────────────────────────────────────────────────────────
# FIX: Two nearly identical functions merged into one
def get_file_path(filename):
    base = os.path.expanduser("~") if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    return os.path.join(base, filename)

DATA_FILE   = get_file_path("employee_data.json")
TIMERS_FILE = get_file_path("timers.json")

# ── Save / Load ───────────────────────────────────────────────────────────────
# FIX: Removed debug print() statements from all four functions

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(employee_data, f)

def save_timers():
    with open(TIMERS_FILE, "w") as f:
        json.dump({name: t.strftime("%Y-%m-%d %H:%M:%S") if t else None for name, t in timers.items()}, f)

def load_data():
    global employee_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            employee_data = defaultdict(list, json.load(f))

def load_timers():
    global timers
    if os.path.exists(TIMERS_FILE):
        with open(TIMERS_FILE, "r") as f:
            raw = json.load(f)
        timers = {name: datetime.strptime(t, "%Y-%m-%d %H:%M:%S") if t else None for name, t in raw.items()}

# ── Timers ────────────────────────────────────────────────────────────────────
# FIX: Removed redundant null-checks (defaultdict handles missing keys automatically)

def start_timer(employee):
    if timers.get(employee) is not None:
        messagebox.showwarning("Warning", f"Timer already running for {employee}.")
        return
    timers[employee] = datetime.now()
    save_timers()
    update_treeview()
    messagebox.showinfo("Info", f"Timer started for {employee}.")

def stop_timer(employee):
    if timers.get(employee) is None:
        messagebox.showwarning("Warning", f"No running timer for {employee}.")
        return

    start_time   = timers[employee]
    end_time     = datetime.now()
    hours_worked = (end_time - start_time).total_seconds() / 3600

    employee_data[employee].append({
        "start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end":   end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "hours": round(hours_worked, 2)
    })
    timers[employee] = None
    save_data()
    save_timers()
    update_treeview()
    print_receipt(employee, start_time, end_time, hours_worked)
    messagebox.showinfo("Info", f"Timer stopped for {employee}. Hours worked: {round(hours_worked, 2)}")

# ── PDF printing ──────────────────────────────────────────────────────────────
# FIX: Duplicated SumatraPDF printing block extracted into one helper

def _send_to_printer(buffer, temp_filename):
    temp_path = os.path.join(TEMP_DIR, temp_filename)
    try:
        with open(temp_path, "wb") as f:
            f.write(buffer.getvalue())
        if not os.path.exists(SUMATRA_PATH):
            messagebox.showerror("Error", "SumatraPDF not found. Please install it or check the path.")
            return
        subprocess.run([SUMATRA_PATH, "-print-to-default", temp_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to print: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def print_receipt(employee, start_time, end_time, hours_worked):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(RECEIPT_WIDTH, RECEIPT_HEIGHT))
    h = RECEIPT_HEIGHT
    # FIX: Removed unused 'width' variable

    c.setFont("Helvetica", 8)
    c.drawString(0.1 * inch, h - 0.5 * inch, f"Work Hours Report for {employee}")
    c.drawString(0.1 * inch, h - 0.8 * inch, f"Clock In:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(0.1 * inch, h - 1.1 * inch, f"Clock Out: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(0.1 * inch, h - 1.4 * inch, f"Hours Worked: {round(hours_worked, 2)}")
    c.drawString(0.1 * inch, h - 2.0 * inch, "---------------------------------")
    c.drawString(0.1 * inch, h - 2.2 * inch, "DON'T LOSE THIS PAPER")
    c.drawString(0.1 * inch, h - 2.4 * inch, "Maka Market")
    c.save()

    _send_to_printer(buffer, "receipt.pdf")

def print_filtered_report(employee, month_day):
    try:
        if '-' in month_day:
            search_month, search_day = (int(p) for p in month_day.split('-'))
        elif month_day:
            search_month, search_day = int(month_day), None
        else:
            search_month = search_day = None
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Use MM or MM-DD.")
        return

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(RECEIPT_WIDTH, RECEIPT_HEIGHT))
    h = RECEIPT_HEIGHT
    # FIX: Removed unused 'width' variable

    c.setFont("Helvetica", 8)
    c.drawString(0.1 * inch, h - 0.5 * inch, f"Work Hours Report for {employee}")

    total_hours = 0
    y = h - 1.0 * inch

    for entry in employee_data.get(employee, []):
        entry_start = datetime.strptime(entry['start'], "%Y-%m-%d %H:%M:%S")
        month_match = (search_month is None or entry_start.month == search_month)
        day_match   = (search_day   is None or entry_start.day   == search_day)
        if not (month_match and day_match):
            continue

        entry_end = datetime.strptime(entry['end'], "%Y-%m-%d %H:%M:%S")
        hours = entry['hours']
        total_hours += hours
        c.drawString(0.1 * inch, y, f"Start: {entry_start}  End: {entry_end}  Hours: {hours}")
        y -= 0.2 * inch
        if y < 0.5 * inch:
            c.showPage()
            c.setFont("Helvetica", 8)
            y = h - 0.5 * inch

    c.drawString(0.1 * inch, y,              f"Total Hours: {round(total_hours, 2)}")
    c.drawString(0.1 * inch, y - 0.2 * inch, "---------------------------------")
    c.drawString(0.1 * inch, y - 0.4 * inch, "DON'T LOSE THIS PAPER")
    c.drawString(0.1 * inch, y - 0.6 * inch, "Maka Market")
    c.save()

    _send_to_printer(buffer, "filtered_report.pdf")

# ── History window ────────────────────────────────────────────────────────────

def search_records(employee, month_day, history_text):
    records = employee_data.get(employee, [])
    if not records:
        history_text.delete(1.0, tk.END)
        history_text.insert(tk.END, "No records for this employee.")
        return

    try:
        if '-' in month_day:
            search_month, search_day = (int(p) for p in month_day.split('-'))
        elif month_day:
            search_month, search_day = int(month_day), None
        else:
            search_month = search_day = None
    except ValueError:
        messagebox.showerror("Input Error", "Invalid date format. Use MM-DD or MM.")
        return

    total_hours = 0
    lines = []

    for entry in records:
        entry_start = datetime.strptime(entry['start'], "%Y-%m-%d %H:%M:%S")
        month_match = (search_month is None or entry_start.month == search_month)
        day_match   = (search_day   is None or entry_start.day   == search_day)
        if not (month_match and day_match):
            continue

        entry_end = datetime.strptime(entry['end'], "%Y-%m-%d %H:%M:%S")
        hours = entry['hours']
        total_hours += hours
        lines.append(f"Start: {entry_start}  |  End: {entry_end}  |  Hours: {hours}")

    lines.append(f"\nTotal Hours: {round(total_hours, 2)}")
    history_text.delete(1.0, tk.END)
    history_text.insert(tk.END, "\n".join(lines))

def show_history(employee):
    win = tk.Toplevel(root)
    win.title(f"History — {employee}")

    search_frame = tk.Frame(win)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Search (MM or MM-DD):").pack(side=tk.LEFT, padx=5)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    history_text = tk.Text(win, wrap=tk.WORD, height=15, width=80)
    history_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    tk.Button(search_frame, text="Search",
              command=lambda: search_records(employee, search_entry.get(), history_text)
              ).pack(side=tk.LEFT, padx=5)

    tk.Button(win, text="Print Report",
              command=lambda: print_filtered_report(employee, search_entry.get())
              ).pack(pady=10)

    search_records(employee, "", history_text)

# ── Main window ───────────────────────────────────────────────────────────────

def update_treeview():
    now = datetime.now()
    for row in tree.get_children():
        tree.delete(row)
    for name in employee_names:
        t = timers.get(name)
        if t is not None:
            elapsed = now - t
            elapsed_str = (f"{elapsed.seconds // 3600:02}:"
                           f"{(elapsed.seconds // 60) % 60:02}:"
                           f"{elapsed.seconds % 60:02}")
            tree.insert("", tk.END, values=(name, "Online", elapsed_str))
        else:
            tree.insert("", tk.END, values=(name, "Offline", ""))
    root.after(1000, update_treeview)

def on_select(event):
    selected = tree.selection()
    if not selected:
        return
    name = tree.item(selected[0])["values"][0]
    clock_in_button.config( command=lambda: start_timer(name))
    clock_out_button.config(command=lambda: stop_timer(name))
    view_button.config(     command=lambda: show_history(name))

# ── App entry point ───────────────────────────────────────────────────────────
# FIX: The original main() / if __name__ guard was broken — the real app code
# ran at module level regardless. Now everything is properly inside main().

def main():
    global root, tree, clock_in_button, clock_out_button, view_button

    # Disclaimer popup
    splash = tk.Tk()
    splash.withdraw()
    messagebox.showinfo(
        "Notice",
        "This is a sample version.\n\n"
        "To enable printing install SumatraPDF at:\n"
        "C:\\SumatraPDF\\SumatraPDF.exe\n\n"
        "The app saves records as JSON files automatically.\n"
        "For the full version contact: +972536660641"
    )
    splash.destroy()

    # Load saved data
    load_data()
    load_timers()

    # Build main window
    root = tk.Tk()
    root.title("Employee Time Tracker")

    w, h = 800, 600
    x = (root.winfo_screenwidth()  // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.resizable(True, True)

    tree = ttk.Treeview(root, columns=("Name", "Status", "Clock In Time"), show="headings")
    tree.heading("Name",          text="Name")
    tree.heading("Status",        text="Status")
    tree.heading("Clock In Time", text="Clock In Time")
    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    clock_in_button  = tk.Button(button_frame, text="Clock In")
    clock_out_button = tk.Button(button_frame, text="Clock Out")
    view_button      = tk.Button(button_frame, text="View History")

    clock_in_button.pack( side=tk.LEFT, padx=5)
    clock_out_button.pack(side=tk.LEFT, padx=5)
    view_button.pack(     side=tk.LEFT, padx=5)

    footer = tk.Frame(root)
    footer.pack(side='bottom', fill='x', padx=10, pady=5)
    tk.Label(footer, text="Made by Ibraheem Amro\nContact: 0536660641",
             anchor='w', font=("Helvetica", 8)).pack(side='left')
    tk.Label(footer, text="Not Registered Version",
             anchor='e', font=("Helvetica", 8)).pack(side='right')

    tree.bind("<ButtonRelease-1>", on_select)
    update_treeview()
    root.mainloop()

if __name__ == "__main__":
    main()
