
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os
import sys
import subprocess
from io import BytesIO
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
import re

# Initialize data structures
employee_data = defaultdict(list)
timers = {}
employee_names = ["Ahmad", "Ibraheem", "Hamza", "Zein", "Mohammad", "Suha", "Tasnem", "Saeb"] 

def main():
  
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Notification", "This app is a sample version to show how the app works, in order to run all the functions, you must download Sumatra PDF, and set its path to C:\SumatraPDF\SumatraPDF.exe , the app will automatically create JSON files in order to save records, for full modified version contact +972536660641 ")
    root.destroy()
if __name__ == "__main__":
    main()


def get_data_file_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.expanduser("~"), "employee_data.json")
    else:
        return os.path.join(os.path.dirname(__file__), "employee_data.json")

def get_timers_file_path():
    if getattr(sys, 'frozen', False):
       
        return os.path.join(os.path.expanduser("~"), "timers.json")
    else:
       
        return os.path.join(os.path.dirname(__file__), "timers.json")

DATA_FILE = get_data_file_path()
TIMERS_FILE = get_timers_file_path()

def save_data():
    print(f"Saving data to: {DATA_FILE}")  
    with open(DATA_FILE, "w") as file:
        json.dump(employee_data, file)

def save_timers():
    print(f"Saving timers to: {TIMERS_FILE}")  
    with open(TIMERS_FILE, "w") as file:
        json.dump({name: time.strftime("%Y-%m-%d %H:%M:%S") if time else None for name, time in timers.items()}, file)

def load_data():
    global employee_data
    print(f"Loading data from: {DATA_FILE}") 
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            employee_data = json.load(file)
    else:
        print(f"File not found: {DATA_FILE}") 

def load_timers():
    global timers
    print(f"Loading timers from: {TIMERS_FILE}")  
    if os.path.exists(TIMERS_FILE):
        with open(TIMERS_FILE, "r") as file:
            timers_data = json.load(file)
            timers = {name: datetime.strptime(time, "%Y-%m-%d %H:%M:%S") if time else None for name, time in timers_data.items()}
    else:
        print(f"File not found: {TIMERS_FILE}")  # Debug print

def start_timer(employee):
    if employee not in employee_data:
        employee_data[employee] = []
    if employee in timers and timers[employee] is not None:
        messagebox.showwarning("Warning", f"Timer already running for {employee}.")
        return
    timers[employee] = datetime.now()
    save_timers()  # Save the timer state immediately
    update_treeview()
    messagebox.showinfo("Info", f"Timer started for {employee}.")

def stop_timer(employee):
    if employee not in employee_data:
        employee_data[employee] = []
    if employee not in timers or timers[employee] is None:
        messagebox.showwarning("Warning", f"No running timer for {employee}.")
        return
    
    start_time = timers[employee]
    end_time = datetime.now()
    duration = end_time - start_time
    hours_worked = duration.total_seconds() / 3600
    
    employee_data[employee].append({
        "start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "hours": round(hours_worked, 2)
    })
    timers[employee] = None
    save_data()
    save_timers()  # Save the timer state after clocking out
    update_treeview()

    # Print receipt with clock-in and clock-out details
    print_receipt(employee, start_time, end_time, hours_worked)

    messagebox.showinfo("Info", f"Timer stopped for {employee}. Hours worked: {round(hours_worked, 2)}")

def print_receipt(employee, start_time, end_time, hours_worked):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(3.15 * inch, 9 * inch))  # Receipt paper size
        width, height = 3.15 * inch, 9 * inch
        
        c.setFont("Helvetica", 8)
        c.drawString(0.1 * inch, height - 0.5 * inch, f"Work Hours Report for {employee}")
        c.drawString(0.1 * inch, height - 0.8 * inch, f"Clock In: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(0.1 * inch, height - 1.1 * inch, f"Clock Out: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(0.1 * inch, height - 1.4 * inch, f"Hours Worked: {round(hours_worked, 2)}")
        
        c.drawString(0.1 * inch, height - 2 * inch, "---------------------------------")
        c.drawString(0.1 * inch, height - 2.2 * inch, "DON'T LOSE THIS PAPER")
        c.drawString(0.1 * inch, height - 2.4 * inch, "Maka Market")
        
        c.save()

        buffer.seek(0)
        pdf_data = buffer.getvalue()
        temp_pdf_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "receipt.pdf")
        
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_data)
        
        # Use SumatraPDF to print the PDF
        sumatra_path = r"C:\SumatraPDF\SumatraPDF.exe"  # Adjust this path to where SumatraPDF is installed
        if not os.path.exists(sumatra_path):
            messagebox.showerror("Error", "SumatraPDF not found. Please install it or check the path.")
            return

        subprocess.run([sumatra_path, "-print-to-default", temp_pdf_path])

    except Exception as e:
        print(f"Failed to print receipt: {e}")
        messagebox.showerror("Error", f"Failed to print receipt: {e}")
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)  # Clean up temp file

def show_history(employee):
    history_window = tk.Toplevel(root)
    history_window.title(f"History for {employee}")

    # Create search engine for date and time
    search_frame = tk.Frame(history_window)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Search (MM-DD):").pack(side=tk.LEFT, padx=5)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    search_button = tk.Button(search_frame, text="Search", command=lambda: search_records(employee, search_entry.get(), history_text))
    search_button.pack(side=tk.LEFT, padx=5)

    history_text = tk.Text(history_window, wrap=tk.WORD, height=15, width=80)
    history_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    pdf_button = tk.Button(history_window, text="Print Report", command=lambda: print_filtered_report(employee, search_entry.get()))
    pdf_button.pack(pady=10)

    # Initialize with all records
    search_records(employee, "", history_text)

def search_records(employee, month_day, history_text):
    if employee not in employee_data or not employee_data[employee]:
        history_text.delete(1.0, tk.END)
        history_text.insert(tk.END, "No records for this employee.")
        return

    try:
        if month_day:
            if '-' in month_day:
                search_month, search_day = month_day.split('-')
                search_month = int(search_month)
                search_day = int(search_day)
            else:
                search_month = int(month_day)
                search_day = None
        else:
            search_month = search_day = None
    except ValueError:
        messagebox.showerror("Input Error", "Invalid date format. Use MM-DD or MM.")
        return

    total_hours = 0
    history_lines = []

    for entry in employee_data[employee]:
        entry_start = datetime.strptime(entry['start'], "%Y-%m-%d %H:%M:%S")
        if (search_month is None or entry_start.month == search_month) and (search_day is None or entry_start.day == search_day):
            entry_end = datetime.strptime(entry['end'], "%Y-%m-%d %H:%M:%S")
            hours = entry['hours']
            total_hours += hours
            history_lines.append(f"Start: {entry_start}, End: {entry_end}, Hours: {hours}")

    history_lines.append(f"\nTotal Hours: {round(total_hours, 2)}")
    history_text.delete(1.0, tk.END)
    history_text.insert(tk.END, "\n".join(history_lines))

def print_filtered_report(employee, month_day):
    try:
        if '-' in month_day:
            search_month, search_day = month_day.split('-')
            search_month = int(search_month)
            search_day = int(search_day)
        else:
            search_month = int(month_day)
            search_day = None
    except ValueError:
        messagebox.showerror("Error", "Invalid date format.")
        return

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(3.15 * inch, 9 * inch))  # Receipt paper size
    width, height = 3.15 * inch, 9 * inch
    
    c.setFont("Helvetica", 8)
    c.drawString(0.1 * inch, height - 0.5 * inch, f"Work Hours Report for {employee}")
    
    total_hours = 0
    y = height - 1 * inch
    for entry in employee_data[employee]:
        entry_start = datetime.strptime(entry['start'], "%Y-%m-%d %H:%M:%S")
        if (search_month is None or entry_start.month == search_month) and (search_day is None or entry_start.day == search_day):
            entry_end = datetime.strptime(entry['end'], "%Y-%m-%d %H:%M:%S")
            hours = entry['hours']
            total_hours += hours
            c.drawString(0.1 * inch, y, f"Start: {entry_start}, End: {entry_end}, Hours: {hours}")
            y -= 0.2 * inch
            if y < 0.5 * inch:
                c.showPage()
                c.setFont("Helvetica", 8)
                y = height - 0.5 * inch
    
    c.drawString(0.1 * inch, y, f"Total Hours: {round(total_hours, 2)}")
    c.drawString(0.1 * inch, y - 0.2 * inch, "---------------------------------")
    c.drawString(0.1 * inch, y - 0.4 * inch, "DON'T LOSE THIS PAPER")
    c.drawString(0.1 * inch, y - 0.6 * inch, "Maka Market")
    
    c.save()

    buffer.seek(0)
    pdf_data = buffer.getvalue()
    temp_pdf_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "filtered_report.pdf")
    
    with open(temp_pdf_path, "wb") as f:
        f.write(pdf_data)
    
    # Use SumatraPDF to print the PDF
    sumatra_path = r"C:\SumatraPDF\SumatraPDF.exe"  # Adjust this path to where SumatraPDF is installed
    if not os.path.exists(sumatra_path):
        messagebox.showerror("Error", "SumatraPDF not found. Please install it or check the path.")
        return

    subprocess.run([sumatra_path, "-print-to-default", temp_pdf_path])

def update_treeview():
    now = datetime.now()
    for row in tree.get_children():
        tree.delete(row)
    for name in employee_names:
        if name in timers and timers[name] is not None:
            status = "Online"
            elapsed_time = now - timers[name]
            clock_in_time_str = f"{elapsed_time.seconds // 3600:02}:{(elapsed_time.seconds // 60) % 60:02}:{elapsed_time.seconds % 60:02}"
        else:
            status = "Offline"
            clock_in_time_str = ""
        tree.insert("", tk.END, values=(name, status, clock_in_time_str))
    root.after(1000, update_treeview)  # Update every second

def on_select(event):
    selected_item = tree.selection()
    if not selected_item:
        return
    selected_name = tree.item(selected_item[0])["values"][0]
    clock_in_button.config(command=lambda: start_timer(selected_name))
    clock_out_button.config(command=lambda: stop_timer(selected_name))
    view_button.config(command=lambda: show_history(selected_name))



root = tk.Tk()
root.title("Employee Time Tracker")

# Load employee data and timers
load_data()
load_timers()


# Set default size and center the window on the screen
default_width = 800
default_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (default_width // 2)
y = (screen_height // 2) - (default_height // 2)
root.geometry(f"{default_width}x{default_height}+{x}+{y}")
root.resizable(True, True)

# Add footer labels
footer_frame = tk.Frame(root)
footer_frame.pack(side='bottom', fill='x', padx=10, pady=5)

left_footer = tk.Label(footer_frame, text="Made by Ibraheem Amro\nContact: 0536660641", anchor='w', font=("Helvetica", 8))
left_footer.pack(side='left', anchor='w')

right_footer = tk.Label(footer_frame, text="Not Registered Version", anchor='e', font=("Helvetica", 8))
right_footer.pack(side='right', anchor='e')

tree = ttk.Treeview(root, columns=("Name", "Status", "Clock In Time"), show="headings")
tree.heading("Name", text="Name")
tree.heading("Status", text="Status")
tree.heading("Clock In Time", text="Clock In Time")
tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

clock_in_button = tk.Button(button_frame, text="Clock In")
clock_in_button.pack(side=tk.LEFT, padx=5)

clock_out_button = tk.Button(button_frame, text="Clock Out")
clock_out_button.pack(side=tk.LEFT, padx=5)

view_button = tk.Button(button_frame, text="View")
view_button.pack(side=tk.LEFT, padx=5)

tree.bind("<ButtonRelease-1>", on_select)
update_treeview()
root.mainloop()
