"""
BMI Calculator - Advanced Tier
--------------------------------
A tkinter GUI application that:
  - Takes weight/height input through labeled fields and a Calculate button
  - Shows the BMI result with colour-coded feedback based on category
  - Supports multiple named users, each with their own saved history
  - Persists every record to an SQLite database (bmi_records.db)
  - Shows a matplotlib line-chart of a user's BMI trend over time
  - Handles database errors gracefully with on-screen messages
"""

import tkinter as tk          #library for -> GUI 
from tkinter import ttk, messagebox     #tkk -> modern tables 
#message box -> for error 

#for graph
from matplotlib.figure import Figure   
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  #attach with tkinter (show in GUI)

from bmi_calculator_beginner import calculate_bmi, classify_bmi
import bmi_db_utils as db

CATEGORY_COLORS = {
    "Underweight": "#3498db",  # blue
    "Normal weight": "#2ecc71",  # green
    "Overweight": "#f39c12",  # orange
    "Obese": "#e74c3c",  # red
}


class BMIApp(tk.Tk): #window child (new screen)
    def __init__(self):
        super().__init__()  #constructor 
        self.title("BMI Calculator")
        self.geometry("480x560")
        self.resizable(False, False)  #fix size 
        self.configure(bg="#f4f6f7")

        ok, error = db.init_db()
        if not ok:
            messagebox.showerror("Database Error", error)


#build sections 
        self._build_input_section()
        self._build_result_section()
        self._build_history_section()

    # ---------------------------------------------------------------- UI

    def _build_input_section(self):        #Frame is the container to arrange 
        frame = tk.Frame(self, bg="#f4f6f7", padx=20, pady=20)
        frame.pack(fill="x")

        tk.Label(     #text show   
            frame, text="BMI Calculator", font=("Segoe UI", 18, "bold"), bg="#f4f6f7"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(frame, text="Name:", bg="#f4f6f7", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky="w", pady=5
        )

        #user type -> entry
        self.name_entry = tk.Entry(frame, font=("Segoe UI", 10))
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=5)   #grid to set in row and col

        tk.Label(frame, text="Weight (kg):", bg="#f4f6f7", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.weight_entry = tk.Entry(frame, font=("Segoe UI", 10))
        self.weight_entry.grid(row=2, column=1, sticky="ew", pady=5)

        tk.Label(frame, text="Height (m):", bg="#f4f6f7", font=("Segoe UI", 10)).grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.height_entry = tk.Entry(frame, font=("Segoe UI", 10))
        self.height_entry.grid(row=3, column=1, sticky="ew", pady=5)

        frame.columnconfigure(1, weight=1)

        button_frame = tk.Frame(frame, bg="#f4f6f7")
        button_frame.grid(row=4, column=0, columnspan=2, pady=(15, 0), sticky="ew")

        tk.Button(
            button_frame,
            text="Calculate",
            font=("Segoe UI", 10, "bold"),
            bg="#2c3e50",
            fg="white",
            command=self.on_calculate,
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        tk.Button(
            button_frame,
            text="Show Trend Graph",
            font=("Segoe UI", 10, "bold"),
            bg="#34495e",
            fg="white",
            command=self.on_show_graph,
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def _build_result_section(self):
        self.result_label = tk.Label(
            self,
            text="Enter your details above",
            font=("Segoe UI", 14, "bold"),
            bg="#f4f6f7",
            fg="#2c3e50",
            pady=10,
        )
        self.result_label.pack(fill="x")

    def _build_history_section(self):
        frame = tk.Frame(self, padx=20, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="History for this name", font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")

        columns = ("date", "weight", "height", "bmi", "category")

        #TREE VIEW  -> TABLE

        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col, label, width in [
            ("date", "Date", 110),
            ("weight", "Weight", 65),
            ("height", "Height", 65),
            ("bmi", "BMI", 60),
            ("category", "Category", 100),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=(5, 0))

    # ------------------------------------------------------------ actions

    def _read_validated_inputs(self):
       
        name = db.normalize_username(self.name_entry.get())

        if not name:
            messagebox.showerror(
                "Missing Name", "Please enter a name before calculating."
            )
            return None

        
        self.name_entry.delete(0, "end")   #khali the text box
        self.name_entry.insert(0, name)    #bhr do name box ko 

        try:
            weight = float(self.weight_entry.get().strip())  #.get -> is for input 
            height = float(self.height_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Weight and height must be numbers.")
            return None

        if weight <= 0 or height <= 0:
            messagebox.showerror(
                "Invalid Input", "Weight and height must be greater than 0."
            )
            return None

        return name, weight, height

    def on_calculate(self): 
        parsed = self._read_validated_inputs() # agr error he to return 
        if parsed is None:
            return
        name, weight, height = parsed  #3 values ko 3 variable me dal do 

        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)
        color = CATEGORY_COLORS[category]

        self.result_label.configure(text=f"BMI: {bmi:.2f}  —  {category}", fg=color)

        ok, error = db.add_record(name, weight, height, bmi, category)
        if not ok:
            messagebox.showerror("Database Error", error)
            return

        self._refresh_history(name)

    def _refresh_history(self, name: str): # delete , record , store in tree view (table)
        for row in self.tree.get_children():
            self.tree.delete(row)         

        ok, records = db.get_records_for_user(name)
        if not ok:
            messagebox.showerror("Database Error", records)
            return

        for _id, weight, height, bmi, category, date_recorded in records:
            self.tree.insert(
                "",
                "end",
                values=(date_recorded, weight, height, f"{bmi:.2f}", category),
            )

    def on_show_graph(self):
        name = db.normalize_username(self.name_entry.get())
        if not name:
            messagebox.showerror(
                "Missing Name", "Enter a name first, then calculate at least one BMI."
            )
            return

        ok, records = db.get_records_for_user(name)
        if not ok:
            messagebox.showerror("Database Error", records)
            return

        if len(records) < 1:
            messagebox.showinfo("No Data", f"No saved records for '{name}' yet.")
            return

        dates = [r[5] for r in records]
        bmis = [r[3] for r in records]

        graph_window = tk.Toplevel(self)
        graph_window.title(f"BMI Trend — {name}")
        graph_window.geometry("600x450")

        figure = Figure(figsize=(5.5, 4), dpi=100)  # dot per inch more -> ,clear less ->blue
        plot = figure.add_subplot(111) #row,col,plot -> 1 plot
        plot.plot(dates, bmis, marker="o", color="#2c3e50")  # X-> dates , Y -> bmis ,mark with circle 
        plot.set_title(f"BMI Trend for {name}")
        plot.set_xlabel("Date")
        plot.set_ylabel("BMI")
        #rotate for clear view 
        plot.tick_params(axis="x", rotation=45) 
        figure.tight_layout()   #final layout figure 

        canvas = FigureCanvasTkAgg(figure, master=graph_window) #connect figure to tkinter widges 
        canvas.draw()   #draw graph
        canvas.get_tk_widget().pack(fill="both", expand=True)  #window resize graph resize 

#start app 
if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()   #open till user close 
