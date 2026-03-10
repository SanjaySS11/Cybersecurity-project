import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests

from admin_dashboard import AdminDashboard
from teacher_dashboard import TeacherDashboard

def center_window(win, width, height):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

class StudentDashboard(tk.Frame): 
    def __init__(self, root, token):
        super().__init__(root)
        self.root = root
        self.token = token
        self.root.title("Student Dashboard")
        center_window(self.root, 800, 400)
        self.pack(fill=tk.BOTH, expand=True)

        tk.Label(self, text="Enter Your Student ID:", font=("Arial", 12)).pack(pady=10)
        self.id_entry = tk.Entry(self, font=("Arial", 12))
        self.id_entry.pack(pady=5)

        tk.Button(self, text="View My Info", font=("Arial", 12), command=self.fetch_student_data).pack(pady=10)

        self.info_frame = tk.Frame(self)
        self.info_frame.pack(pady=20, fill=tk.BOTH, expand=True)

    def fetch_student_data(self):
        student_id = self.id_entry.get().strip()
        if not student_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid student ID")
            return

        url = f"http://127.0.0.1:5000/students/{student_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(url, headers=headers, timeout=5)
            data = response.json()

            for widget in self.info_frame.winfo_children():
                widget.destroy()

            if response.status_code == 200:
                info_text = (
                    f"ID: {data['id']}\n"
                    f"Name: {data['name']}\n"
                    f"Marks: {data['marks']}\n"
                    f"Fee Status: {data['fee_status']}\n"
                    f"Enrollment Year: {data['enrollment_year']}\n"
                    f"Course: {data['course']}"
                )
                tk.Label(self.info_frame, text=info_text, font=("Arial", 12), justify="left").pack()
            else:
                messagebox.showinfo("Info", data.get("error", "No data found."))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Could not connect to server.\n{str(e)}")

class Landing_page(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("Home Page")
        center_window(self.root, 800, 600)
        self.pack(fill=tk.BOTH, expand=True)

        try:
            self.bg_image = Image.open("backgroundimg.jpg")
            self.bg_image = self.bg_image.resize((800, 600))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = tk.Label(self, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as error:
            print("Background image not found:", error)
            self.root.configure(bg="lightblue")

        button_frame = tk.Frame(self, bg="#ffffff", relief=tk.RIDGE, borderwidth=2)
        button_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(button_frame, text="Login As", font=("Arial", 24, "bold"), bg="#ffffff").grid(row=0, column=0, pady=(20, 10), padx=30)

        tk.Button(button_frame, text="Admin", font=("Arial", 18), width=20, command=self.login_admin).grid(row=1, column=0, pady=10, padx=30)
        tk.Button(button_frame, text="Teacher", font=("Arial", 18), width=20, command=self.login_teacher).grid(row=2, column=0, pady=10, padx=30)
        tk.Button(button_frame, text="Student", font=("Arial", 18), width=20, command=self.login_student).grid(row=3, column=0, pady=(10, 20), padx=30)

    def login_admin(self):
        self.open_login_window("admin")

    def login_teacher(self):
        self.open_login_window("teacher")

    def login_student(self):
        self.open_login_window("student")

    def open_login_window(self, role):
        login_win = tk.Toplevel(self.root)
        center_window(login_win, 400, 300)
        LoginWindow(login_win, role)

class LoginWindow(tk.Frame):
    def __init__(self, root, role):
        super().__init__(root)
        self.root = root
        self.role = role
        self.root.title(f"{role.title()} Login")
        self.pack(fill=tk.BOTH, expand=True)

        login_frame = tk.Frame(self, bg="#f2f2f2", relief=tk.RIDGE, borderwidth=2)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=350, height=300)

        tk.Label(login_frame, text=f"{role.title()} Login", font=("Arial", 18, "bold"), bg="#f2f2f2").pack(pady=10)
        tk.Label(login_frame, text="Username:", bg="#f2f2f2").pack(pady=(10, 0))
        self.username_entry = tk.Entry(login_frame, font=("Arial", 14))
        self.username_entry.pack()
        tk.Label(login_frame, text="Password:", bg="#f2f2f2").pack(pady=(10, 0))
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 14))
        self.password_entry.pack()
        tk.Button(
            login_frame,
            text="Login",
            font=("Arial", 14, "bold"),
            height=2,
            bg="#4CAF50",
            fg="white",
            command=self.authenticate
        ).pack(pady=18, fill=tk.X, padx=40)

    def authenticate(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        payload = {"username": username, "password": password, "role": self.role}

        try:
            response = requests.post("http://127.0.0.1:5000/login", json=payload, timeout=5)
            result = response.json()
            if result.get("success"):
                token = result["token"]
                self.root.destroy()
                dash_board = tk.Toplevel()
                if self.role == "admin":
                    center_window(dash_board, 800, 600)
                    AdminDashboard(dash_board, token)
                elif self.role == "teacher":
                    center_window(dash_board, 800, 500)
                    TeacherDashboard(dash_board, token)
                elif self.role == "student":
                    center_window(dash_board, 800, 400)
                    StudentDashboard(dash_board, token)
            else:
                messagebox.showerror("Login Failed", result.get("message", "Invalid login"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server.\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    Landing_page(root)
    root.mainloop()
