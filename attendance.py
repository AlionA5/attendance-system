import tkinter as Tk
from tkinter import *
from tkinter import messagebox, ttk 
from datetime import date
import traceback
import sqlite3


DB_FILE = "attendance.db"

#database connection
def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    #students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            subject_grade TEXT,
            today_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    #attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            attendance_date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

#function of adding students
def add_student():
    try:
        name = entry_name.get()
        surname = entry_surname.get()
        subject_grade = entry_subject_grade.get()

        if not name or not surname or not subject_grade:
            messagebox.showerror("All boxes should be filled in.")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, surname, subject_grade) VALUES (?, ?, ?)",
                       (name, surname, subject_grade))
        conn.commit()
        conn.close()
        messagebox.showinfo("Student was added succesfully.")
        entry_name.delete(0, END)
        entry_surname.delete(0, END)
        entry_subject_grade.delete(0, END)
        load_students()
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Error", str(e))

#delete student function
def delete_student(student_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()
        load_students()
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Error", str(e))

#mark attendance function
def mark_attendance():
    selected=tree.focus()
    if not selected:
        messagebox.showerror("No student is selected.")
        return
    values=tree.item(selected, 'values')
    student_id=values[0]
    status=combo_status.get()
    if not status:
        messagebox.showerror("Attendance must be marked.")
        return
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        "INSERT INTO attendance (student_id, attendance_date, status) VALUES (?, ?, ?)",
        (student_id, date.today(), status))
    conn.commit()
    conn.close()
    messagebox.showinfo("Attendance was succesfully marked.")
    
#load students into a list
def load_students():
    try:
        for row in tree.get_children():
            tree.delete(row)
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("select* from students")
        rows=cursor.fetchall()
        for r in rows:
            tree.insert("", END, values=r)
        conn.close()
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Error", str(e))

#show attendance
def view_attendance():  
    win=Toplevel(root)
    win.title("Attendance system")
    tree=ttk.Treeview(win, columns=("Name", "Second name", "Grade","Status", "Date"), show='headings')
    tree.heading("Name", text="Name")
    tree.heading("Second name", text="Second name")
    tree.heading("Grade", text="Grade")
    tree.heading("Status", text="Status")
    tree.heading("Date", text="Date")
    tree.pack(fill="both", expand=True)

    conn=get_connection()
    cursor=conn.cursor()
    today = date.today()
    cursor.execute("""
        SELECT s.name, s.surname, s.subject_grade, a.status, a.attendance_date
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND a.attendance_date = ?
    """, (today,))
    rows=cursor.fetchall()
    for r in rows:
        tree.insert("", END, values=r)
    conn.close()

def on_delete_student():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("No studernt is selected.")
        return
    student_id = int(tree.item(selected, "values")[0])
    delete_student(student_id)
    load_students()

#gui
root = Tk()
root.title("Attendance system")
root.geometry("1800x1200")
root.configure(bg="#6fa4ee")

#parametre studentov
frame1 = LabelFrame(root, text="Add student", padx=10, pady=10, bg="#78b298")
frame1.pack(fill="x", expand="yes", padx=20, pady=10)

Label(frame1, text="Name:").grid(row=0, column=0, padx=5, pady=5)
entry_name = Entry(frame1)
entry_name.grid(row=0, column=1, padx=5, pady=5)

Label(frame1, text="Second name:").grid(row=1, column=0, padx=5, pady=5)
entry_surname = Entry(frame1)
entry_surname.grid(row=1, column=1, padx=5, pady=5)

Label(frame1, text="Grade:").grid(row=2, column=0, padx=5, pady=5)
entry_subject_grade = Entry(frame1)
entry_subject_grade.grid(row=2, column=1, padx=5, pady=5)

Label(frame1, text="Todays date:").grid(row=3, column=0, padx=5, pady=5)
today_str = date.today().strftime("%Y-%m-%d")
Label(frame1, text=today_str).grid(row=3, column=1, padx=5, pady=5)

Button(frame1, text="Add", command=add_student).grid(row=4, column=0, padx=20, pady=5)

#dochadzka
frame3 = LabelFrame(root, text="Attendance", padx=10, pady=10, bg="#9e99e9")
frame3.pack(fill="x", expand="yes", padx=10, pady=5)

Label(frame3, text="Status:").grid(row=0, column=0, padx=5)
combo_status=ttk.Combobox(frame3, values=["Present", "Absent"])
combo_status.grid(row=0, column=1, padx=5)

Button(frame3, text="Save attendance", command=mark_attendance).grid(row=0, column=2, padx=10)
Button(frame3, text="Show attendance", command=view_attendance).grid(row=0, column=3, padx=10)

#zoznam studentov
frame2 = LabelFrame(root, text="Students list", padx=10, pady=10, bg="#e999d9")
frame2.pack(fill="both", expand="yes", padx=20, pady=10)

tree=ttk.Treeview(frame2, columns=("Number", "Name", "Second name", "Grade", "Date"), show='headings')
tree.heading("Number", text="Number")
tree.heading("Name", text="Name")
tree.heading("Second name", text="Second name")
tree.heading("Grade", text="Grade")
tree.heading("Date", text="Date")   
tree.pack(fill="both", expand=True)
style = ttk.Style()
style.configure("Treeview",
                background="#e999d9",
                foreground="black",
                rowheight=25,
                fieldbackground="#e999d9")
style.map('Treeview', background=[('selected', '#0d6efd')])

Button(frame2, text="Delete student:", command=on_delete_student).pack(pady=5)

init_db()
root.mainloop()