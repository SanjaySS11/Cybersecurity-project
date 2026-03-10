import tkinter as tk
from tkinter import simpledialog, messagebox
import requests

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
        center_window(self.root, 500, 300)
        self.pack(fill=tk.BOTH, expand=True)

        dash_frame = tk.Frame(self, bg="#f2f2f2", relief=tk.RIDGE, borderwidth=2)
        dash_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=350, height=200)

        tk.Label(dash_frame, text="Student Dashboard", font=("Arial", 20, "bold"), fg="purple", bg="#f2f2f2").pack(pady=20)
        tk.Button(dash_frame, text="View My Info", font=("Arial", 14), width=25, command=self.view_my_info).pack(pady=10)
        tk.Button(dash_frame, text="Logout", font=("Arial", 14), width=25, bg="red", fg="white", command=self.root.destroy).pack(pady=20)

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def view_my_info(self):
        student_id = simpledialog.askinteger("Student ID", "Enter your Student ID:")
        if student_id:
            try:
                url = f"http://127.0.0.1:5000/students/{student_id}"
                response = requests.get(url, headers=self.get_headers())
                if response.status_code == 200:
                    data = response.json()
                    if "name" in data:
                        self.show_profile(data)
                    else:
                        messagebox.showinfo("No Data", "No student info found for this ID.")
                elif response.status_code == 404:
                    messagebox.showinfo("Not Found", "No student found with this ID.")
                else:
                    messagebox.showerror("Error", f"Server error {response.status_code}: {response.text}")
            except Exception as e:
                messagebox.showerror("Error", f"Error fetching student data.\n{e}")

    def show_profile(self, data):
        profile_win = tk.Toplevel(self.root)
        center_window(profile_win, 400, 300)
        profile_win.title("My Profile")

        info_frame = tk.Frame(profile_win, bg="#f7f7f7")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        fields = {
            "Name": data.get("name", "N/A"),
            "Marks": data.get("marks", "N/A"),
            "Fee Status": data.get("fee_status", "N/A"),
            "Enrollment Year": data.get("enrollment_year", "N/A"),
            "Course": data.get("course", "N/A")
        }

        for idx, (label, value) in enumerate(fields.items()):
            tk.Label(info_frame, text=f"{label}:", font=("Arial", 12, "bold"), anchor="w").grid(row=idx, column=0, sticky="w", pady=5)
            tk.Label(info_frame, text=value, font=("Arial", 12), anchor="w").grid(row=idx, column=1, sticky="w", pady=5)
