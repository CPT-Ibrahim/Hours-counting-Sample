# Employee Time Tracker

A desktop app for tracking employee work hours. Built with Python and tkinter.
Employees can clock in and out, and the app saves all records automatically and prints receipts.

---

## What It Does

- Clock employees in and out with a single click
- Shows a live timer for every employee that is currently clocked in
- Saves all work sessions automatically to a JSON file on your computer
- Prints a receipt instantly when an employee clocks out
- Lets you view and search an employee's full history by month or date
- Lets you print a filtered report for any employee

---

## Requirements

- Python 3.8 or newer → https://www.python.org/downloads/
- reportlab library → install by running:

      pip install reportlab

- SumatraPDF (only needed for printing) → install it at exactly this path:

      C:\SumatraPDF\SumatraPDF.exe

  Download: https://www.sumatrapdfreader.org/download-free-pdf-viewer

---

## How to Run
( you can use the EXE file instead )
1. Make sure Python is installed
2. Install reportlab:

       pip install reportlab

3. Run the app:

       python app.py

---

## How to Use

**Clocking In**
1. Click on an employee's name in the list
2. Click the "Clock In" button
3. Their status will change to Online and a live timer will start

**Clocking Out**
1. Click on the employee's name
2. Click the "Clock Out" button
3. A receipt will be printed automatically showing the session details

**Viewing History**
1. Click on an employee's name
2. Click "View History"
3. A window will open showing all their past sessions
4. You can search by month (MM) or by exact date (MM-DD)
5. Click "Print Report" to print the filtered results

---

## Files in This Project

| File | What it does |
|---|---|
| app.py | The entire application |
| requirements.txt | Full list of everything needed to run the app |
| employee_data.json | Created automatically — stores all work session records |
| timers.json | Created automatically — stores who is currently clocked in |

> `employee_data.json` and `timers.json` are created the first time you run the app.
> Do not delete them or all records will be lost.

---

## Employees

The following names are loaded into the app by default:

Ahmad, Ibraheem, Hamza, Zein, Mohammad, Suha, Tasnem, Saeb

To add or remove employees, open `app.py` and edit the `employee_names` list near the top of the file.

---

## Notes

- If SumatraPDF is not installed, the app will still run normally but the print buttons will show an error
- The app window can be resized freely
- Records are never deleted automatically — the JSON files keep growing as sessions are added

---

## Contact

For the full registered version contact: +972536660641

Made by Ibraheem Amro
