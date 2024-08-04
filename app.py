import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class EmployeeTimeTracker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Employee Time Tracker")
        self.geometry("900x600")

        self.employees = []
        self.load_employees()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tabview.add("Add Employee")
        self.tabview.add("Check In/Out")
        self.tabview.add("View Activities")

        self.setup_add_employee_tab()
        self.setup_check_in_out_tab()
        self.setup_view_activities_tab()

    def load_employees(self):
        try:
            with open("employees.csv", "r") as file:
                reader = csv.reader(file)
                self.employees = list(reader)
        except FileNotFoundError:
            pass

    def save_employees(self):
        with open("employees.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(self.employees)

    def setup_add_employee_tab(self):
        tab = self.tabview.tab("Add Employee")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(tab, text="Add New Employee", font=("Arial", 20)).grid(row=0, column=0, pady=20)
        
        self.name_entry = ctk.CTkEntry(tab, placeholder_text="Enter employee name")
        self.name_entry.grid(row=1, column=0, padx=20, pady=10)

        add_button = ctk.CTkButton(tab, text="Add Employee", command=self.add_employee)
        add_button.grid(row=2, column=0, padx=20, pady=10)

        self.add_status_label = ctk.CTkLabel(tab, text="")
        self.add_status_label.grid(row=3, column=0, pady=10)

    def setup_check_in_out_tab(self):
        tab = self.tabview.tab("Check In/Out")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(tab, text="Check In/Out", font=("Arial", 20)).grid(row=0, column=0, pady=20)

        self.employee_combobox = ctk.CTkComboBox(tab, values=[emp[0] for emp in self.employees])
        self.employee_combobox.grid(row=1, column=0, padx=20, pady=10)

        button_frame = ctk.CTkFrame(tab)
        button_frame.grid(row=2, column=0, padx=20, pady=10)

        ctk.CTkButton(button_frame, text="Clock In", command=self.clock_in).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Clock Out", command=self.clock_out).pack(side="left", padx=5)

        self.check_status_label = ctk.CTkLabel(tab, text="")
        self.check_status_label.grid(row=3, column=0, pady=10)

    def setup_view_activities_tab(self):
        tab = self.tabview.tab("View Activities")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tab, text="Employee Activities", font=("Arial", 20)).grid(row=0, column=0, pady=20)
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.employee_filter = ctk.CTkComboBox(filter_frame, values=["All Employees"] + [emp[0] for emp in self.employees])
        self.employee_filter.set("All Employees")
        self.employee_filter.pack(side="left", padx=(0, 10))

        self.date_filter = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD")
        self.date_filter.pack(side="left", padx=(0, 10))

        filter_button = ctk.CTkButton(filter_frame, text="Filter", command=self.apply_filter)
        filter_button.pack(side="left")


        
        # Create a frame to hold the Treeview
        tree_frame = ctk.CTkFrame(tab)
        tree_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Create Treeview widget
        self.activity_tree = ttk.Treeview(tree_frame, columns=("Employee", "Action", "Timestamp"), show="headings")
        self.activity_tree.heading("Employee", text="Employee")
        self.activity_tree.heading("Action", text="Action")
        self.activity_tree.heading("Timestamp", text="Timestamp")
        self.activity_tree.column("Employee", width=150)
        self.activity_tree.column("Action", width=100)
        self.activity_tree.column("Timestamp", width=200)
        self.activity_tree.grid(row=0, column=0, sticky="nsew")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.activity_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.activity_tree.configure(yscrollcommand=scrollbar.set)

        self.update_activities()
    
    def apply_filter(self):
        employee = self.employee_filter.get()
        date = self.date_filter.get().strip()
        
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        for emp in self.employees:
            if employee == "All Employees" or employee == emp[0]:
                for activity in emp[1:]:
                    action, timestamp = activity.split(": ")
                    if not date or date in timestamp:
                        self.activity_tree.insert("", "end", values=(emp[0], action, timestamp))
    
    def add_employee(self):
        name = self.name_entry.get().strip()
        if name and name not in [employee[0] for employee in self.employees]:
            self.employees.append([name])
            self.save_employees()
            self.name_entry.delete(0, 'end')
            self.add_status_label.configure(text=f"Added: {name}")
            self.employee_filter.configure(values=["All Employees"] + [emp[0] for emp in self.employees])
            self.update_employee_combobox()
            self.update_activities()
        else:
            self.add_status_label.configure(text="Invalid name or employee already exists")

    def clock_in(self):
        name = self.employee_combobox.get()
        if name:
            for employee in self.employees:
                if employee[0] == name:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    employee.append(f"In: {timestamp}")
                    self.save_employees()
                    self.check_status_label.configure(text=f"{name} clocked in at {timestamp}")
                    self.update_activities()
                    break
        else:
            self.check_status_label.configure(text="Please select an employee")

    def clock_out(self):
        name = self.employee_combobox.get()
        if name:
            for employee in self.employees:
                if employee[0] == name:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    employee.append(f"Out: {timestamp}")
                    self.save_employees()
                    self.check_status_label.configure(text=f"{name} clocked out at {timestamp}")
                    self.update_activities()
                    break
        else:
            self.check_status_label.configure(text="Please select an employee")

    def update_employee_combobox(self):
        self.employee_combobox.configure(values=[emp[0] for emp in self.employees])

    def update_activities(self):
        self.employee_filter.configure(values=["All Employees"] + [emp[0] for emp in self.employees])
        self.apply_filter()

if __name__ == "__main__":
    app = EmployeeTimeTracker()
    app.mainloop()