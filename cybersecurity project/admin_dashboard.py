import tkinter as tk
from tkinter import simpledialog, messagebox
import requests

def center_window(win, width, height):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

class AdminDashboard(tk.Frame):
    def __init__(self, root, token):
        super().__init__(root)
        self.root = root
        self.token = token
        self.root.title("Admin Dashboard")
        center_window(self.root, 800, 700)
        self.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self, bg="#e6f2ff", relief=tk.RIDGE, borderwidth=2)
        btn_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=540, height=660)

        tk.Label(btn_frame, text="Admin Dashboard", font=("Arial", 22, "bold"), fg="navy", bg="#e6f2ff").pack(pady=20)

        # Students Section
        tk.Label(btn_frame, text="Student Management", font=("Arial", 16, "bold"), bg="#e6f2ff", fg="darkgreen").pack(pady=(5, 0))
        tk.Button(btn_frame, text="View All Students", font=("Arial", 13), width=35, command=self.view_students).pack(pady=2)
        tk.Button(btn_frame, text="Add Student", font=("Arial", 13), width=35, command=self.add_student).pack(pady=2)
        tk.Button(btn_frame, text="Update Student", font=("Arial", 13), width=35, command=self.update_student).pack(pady=2)
        tk.Button(btn_frame, text="Delete Student", font=("Arial", 13), width=35, command=self.delete_student).pack(pady=2)

        # Teachers Section
        tk.Label(btn_frame, text="Teacher Management", font=("Arial", 16, "bold"), bg="#e6f2ff", fg="darkblue").pack(pady=(20, 0))
        tk.Button(btn_frame, text="View All Teachers", font=("Arial", 13), width=35, command=self.view_teachers).pack(pady=2)
        tk.Button(btn_frame, text="Add Teacher", font=("Arial", 13), width=35, command=self.add_teacher).pack(pady=2)
        tk.Button(btn_frame, text="Update Teacher", font=("Arial", 13), width=35, command=self.update_teacher).pack(pady=2)
        tk.Button(btn_frame, text="Delete Teacher", font=("Arial", 13), width=35, command=self.delete_teacher).pack(pady=2)

        # Logs and Logout
        tk.Button(btn_frame, text="View Login Logs", font=("Arial", 13), width=35, command=self.view_logs).pack(pady=20)
        tk.Button(btn_frame, text="Logout", font=("Arial", 13), width=35, bg="red", fg="white", command=self.root.destroy).pack()

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    # ---------------- STUDENT FUNCTIONS ----------------
    def view_students(self):
        try:
            r = requests.get("http://127.0.0.1:5000/students", headers=self.get_headers())
            data = r.json()
            if data:
                self.show_table("All Students", data, ["ID", "Name", "Marks", "Fee Status", "Enrollment Year", "Course"])
            else:
                messagebox.showinfo("All Students", "No students found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching students.\n{e}")

    def add_student(self):
        payload = {
            "name": simpledialog.askstring("Name", "Enter student name:"),
            "marks": simpledialog.askinteger("Marks", "Enter marks:"),
            "fee_status": simpledialog.askstring("Fee Status", "Paid/Pending:"),
            "enrollment_year": simpledialog.askstring("Year", "Enter enrollment year:"),
            "course": simpledialog.askstring("Course", "Enter course:")
        }
        if all(payload.values()):
            try:
                r = requests.post("http://127.0.0.1:5000/students", json=payload, headers=self.get_headers())
                messagebox.showinfo("Response", r.json().get("message", "Student added."))
            except Exception as e:
                messagebox.showerror("Error", f"Error adding student.\n{e}")

    def update_student(self):
        student_id = simpledialog.askinteger("ID", "Enter student ID to update:")
        payload = {
            "name": simpledialog.askstring("Name", "Enter new name:"),
            "marks": simpledialog.askinteger("Marks", "Enter new marks:"),
            "fee_status": simpledialog.askstring("Fee Status", "Paid/Pending:"),
            "enrollment_year": simpledialog.askstring("Year", "New enrollment year:"),
            "course": simpledialog.askstring("Course", "New course:")
        }
        if student_id and all(payload.values()):
            try:
                r = requests.put(f"http://127.0.0.1:5000/students/{student_id}", json=payload, headers=self.get_headers())
                messagebox.showinfo("Response", r.json().get("message", "Student updated."))
            except Exception as e:
                messagebox.showerror("Error", f"Error updating student.\n{e}")

    def delete_student(self):
        student_id = simpledialog.askinteger("ID", "Enter student ID to delete:")
        if student_id:
            try:
                r = requests.delete(f"http://127.0.0.1:5000/students/{student_id}", headers=self.get_headers())
                messagebox.showinfo("Response", r.json().get("message", "Student deleted."))
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting student.\n{e}")

    # ---------------- TEACHER FUNCTIONS ----------------
    def view_teachers(self):
        try:
            r = requests.get("http://127.0.0.1:5000/teachers", headers=self.get_headers())
            data = r.json()
            if data:
                self.show_table("All Teachers", data, ["ID", "Name", "Subject", "Salary", "Join Year"])
            else:
                messagebox.showinfo("All Teachers", "No teachers found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching teachers.\n{e}")

    def add_teacher(self):
        payload = {
            "name": simpledialog.askstring("Name", "Enter teacher name:"),
            "subject": simpledialog.askstring("Subject", "Enter subject:"),
            "salary": simpledialog.askfloat("Salary", "Enter salary:"),
            "join_year": simpledialog.askstring("Join Year", "Enter joining year:")
        }
        if all(payload.values()):
            try:
                r = requests.post("http://127.0.0.1:5000/teachers", json=payload, headers=self.get_headers())
                messagebox.showinfo("Response", r.json().get("message", "Teacher added."))
            except Exception as e:
                messagebox.showerror("Error", f"Error adding teacher.\n{e}")

    def update_teacher(self):
        teacher_id = simpledialog.askinteger("ID", "Enter teacher ID to update:")
        payload = {
            "name": simpledialog.askstring("Name", "Enter new name:"),
            "subject": simpledialog.askstring("Subject", "Enter new subject:"),
            "salary": simpledialog.askfloat("Salary", "Enter new salary:"),
            "join_year": simpledialog.askstring("Join Year", "Enter new join year:")
        }
        if teacher_id and all(payload.values()):
            try:
                r = requests.put(f"http://127.0.0.1:5000/teachers/{teacher_id}", json=payload, headers=self.get_headers())
                messagebox.showinfo("Response", r.json().get("message", "Teacher updated."))
            except Exception as e:
                messagebox.showerror("Error", f"Error updating teacher.\n{e}")

    def delete_teacher(self):
        teacher_id = simpledialog.askinteger("ID", "Enter teacher ID to delete:")
        if teacher_id:
            try:
                r = requests.delete(f"http://127.0.0.1:5000/teachers/{teacher_id}", headers=self.get_headers())
                messagebox.showinfo("Response", r.json().get("message", "Teacher deleted."))
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting teacher.\n{e}")

    # ---------------- LOG VIEW ----------------
    def view_logs(self):
        try:
            r = requests.get("http://127.0.0.1:5000/logs", headers=self.get_headers())
            logs = r.json()
            logs_text = "".join(logs) if logs else "No logs found."
            log_win = tk.Toplevel(self.root)
            center_window(log_win, 700, 500)
            log_win.title("Login Logs")
            text = tk.Text(log_win, wrap=tk.WORD, font=("Consolas", 11))
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(tk.END, logs_text)
            text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching logs.\n{e}")

    # ---------------- TABLE DISPLAY ----------------
    def show_table(self, title, data, headers):
        table_win = tk.Toplevel(self.root)
        center_window(table_win, 500, 500)
        table_win.title(title)

        canvas = tk.Canvas(table_win)
        scrollbar_y = tk.Scrollbar(table_win, orient="vertical", command=canvas.yview)
        scrollbar_x = tk.Scrollbar(table_win, orient="horizontal", command=canvas.xview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        for col, header in enumerate(headers):
            tk.Label(scroll_frame, text=header, bg="#d9edf7", font=("Arial", 11, "bold"),
                     borderwidth=1, relief="solid", padx=5, pady=5).grid(row=0, column=col, sticky="nsew")

        for row_index, item in enumerate(data, start=1):
            for col_index, header in enumerate(headers):
                value = item.get(header.lower().replace(" ", "_"), "")
                tk.Label(scroll_frame, text=value, font=("Arial", 10), borderwidth=1, relief="solid",
                         padx=5, pady=3).grid(row=row_index, column=col_index, sticky="nsew")

        for col_index in range(len(headers)):
            scroll_frame.grid_columnconfigure(col_index, weight=1)

