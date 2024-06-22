from logging import root
import tkinter as tk
from tkinter import Label, PhotoImage, messagebox
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect('bmi_data.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS bmi_records (
    id INTEGER PRIMARY KEY,
    name TEXT,
    weight REAL,
    height REAL,
    bmi REAL,
    category TEXT,
    date TEXT
)
''')

# Function to calculate BMI
def calculate_bmi(weight, height):
    m=height/100
    bmi = weight / (m**2)
    return round(bmi, 2)

# Function to categorize BMI
def categorize_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"
    
    
###### Creating GUI  #############################

class BMICalculator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("BMI Calculator")
        self.geometry("400x400")
        
        # #two boxes
        # box=PhotoImage(file="Images/box.png")
        # Label(root, image=box).place(x=20,y=100)
        # Label(root,image=box).place(x=240,y=100)

        self.name_label = tk.Label(self, text="Name:")
        self.name_label.pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        self.weight_label = tk.Label(self, text="Weight (kg):")
        self.weight_label.pack()
        self.weight_entry = tk.Entry(self)
        self.weight_entry.pack()

        self.height_label = tk.Label(self, text="Height (cm):")
        self.height_label.pack()
        self.height_entry = tk.Entry(self)
        self.height_entry.pack()

        self.calculate_button = tk.Button(self, text="Calculate BMI", command=self.calculate_bmi)
        self.calculate_button.pack()

        self.result_label = tk.Label(self, text="")
        self.result_label.pack()

        self.view_history_button = tk.Button(self, text="View History", command=self.view_history)
        self.view_history_button.pack()

    def calculate_bmi(self):
        try:
            name = self.name_entry.get()
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())

            if weight <= 0 or height <= 0:
                raise ValueError

            bmi = calculate_bmi(weight, height)
            category = categorize_bmi(bmi)
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("INSERT INTO bmi_records (name, weight, height, bmi, category, date) VALUES (?, ?, ?, ?, ?, ?)", 
                           (name, weight, height, bmi, category, date))
            conn.commit()

            self.result_label.config(text=f"BMI: {bmi}\nCategory: {category}")

        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid weight and height values.")

    def view_history(self):
        cursor.execute("SELECT name, weight, height, bmi, category, date FROM bmi_records")
        records = cursor.fetchall()

        history_window = tk.Toplevel(self)
        history_window.title("BMI History")
        history_window.geometry("600x400")

        for idx, record in enumerate(records):
            record_label = tk.Label(history_window, text=f"{record}")
            record_label.pack()

        plot_button = tk.Button(history_window, text="Plot BMI Trend", command=self.plot_bmi_trend)
        plot_button.pack()

    def plot_bmi_trend(self):
        cursor.execute("SELECT date, bmi FROM bmi_records")
        records = cursor.fetchall()

        dates = [record[0] for record in records]
        bmis = [record[1] for record in records]

        plt.plot(dates, bmis, marker='o')
        plt.xlabel('Date')
        plt.ylabel('BMI')
        plt.title('BMI Trend Over Time')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = BMICalculator()
    app.mainloop()

    conn.close()
