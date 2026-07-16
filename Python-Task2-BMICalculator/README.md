# 🧮 BMI Calculator — Oasis Infobyte Internship (Task 2)

> A dual-tier Python application that calculates Body Mass Index (BMI), classifies it into WHO health categories, and visualizes user trends over time.

---

## 📌 Project Overview

This project is part of the **Python Programming** track for the Oasis Infobyte Internship. It includes two complete implementations:

- **Beginner Tier** — A command-line interface (CLI) tool that accepts weight and height inputs, validates them, calculates BMI, and displays the health category.
- **Advanced Tier** — A full-featured GUI application built with `tkinter` that supports **multi-user profiles**, **SQLite database persistence**, **colour-coded results**, and a **BMI trend graph** using `matplotlib`.

Both tiers share the same core BMI calculation logic, making this a scalable and well-structured project.

---

## 🚀 Features

### ✅ Beginner Tier (CLI)

- Prompt user for **weight (kg)** and **height (m)** via the command line.
- Calculate BMI using the formula: `BMI = weight / (height²)`.
- Classify results into standard categories:
  - Underweight (< 18.5)
  - Normal (18.5 – 24.9)
  - Overweight (25 – 29.9)
  - Obese (≥ 30)
- Display BMI rounded to **2 decimal places** along with the category.
- Input validation that rejects non-numeric and negative values with clear error messages.
- Option to calculate repeatedly without restarting the program.

### ✅ Advanced Tier (GUI + Database)

- **Tkinter GUI** with labeled input fields for Name, Weight, and Height.
- **"Calculate" button** that computes BMI instantly.
- **Colour-coded results**:
  - 🔵 Underweight — Blue
  - 🟢 Normal — Green
  - 🟠 Overweight — Orange
  - 🔴 Obese — Red
- **Multi-user support** — each named user has their own history.
- **SQLite database** (`bmi_records.db`) to store every record permanently.
- **History viewer** (Treeview) showing all past entries for the current user.
- **BMI Trend Graph** using `matplotlib` — plots a line chart of BMI over time.
- Graceful error handling for database read/write failures (no crashes).

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 |
| GUI Framework | `tkinter` (built-in) |
| Data Visualization | `matplotlib` |
| Database | `sqlite3` (built-in) |
| Data Persistence | SQLite |
| CLI | Standard `input()` / `print()` |

---

## 📦 Dependencies

All required libraries come pre-installed with Python, except `matplotlib`.

### Install Matplotlib

Open your terminal/command prompt and run:

```bash
pip install matplotlib
✅ No other external libraries are required.

🏃 How to Run
1. Clone or Download the Project
Ensure all three Python files are in the same folder:

bmi_calculator_beginner.py

bmi_calculator_advanced.py

bmi_db_utils.py

2. Run the Beginner CLI Version
bash
python bmi_calculator_beginner.py
3. Run the Advanced GUI Version
bash
python bmi_calculator_advanced.py
📊 BMI Categories (WHO Standard)
The Body Mass Index (BMI) is calculated using the formula:


BMI = weight (kg) / height (m)²
Once calculated, the BMI value falls into one of the following standard categories:

BMI Range	Category	Health Implication
< 18.5	Underweight	May indicate malnutrition, eating disorders, or other health conditions.
18.5 – 24.9	Normal weight	Healthy weight range — associated with lowest risk of chronic diseases.
25.0 – 29.9	Overweight	Increased risk of heart disease, diabetes, and hypertension.
≥ 30.0	Obese	High risk of severe health complications, including cardiovascular diseases and type 2 diabetes.
Note: BMI is a screening tool and does not directly measure body fat. Factors such as age, gender, muscle mass, and ethnicity may influence interpretation. Always consult a healthcare professional for a complete health assessment.

📁 Folder Structure

OIBSIP/
└── Python-Task2-BMICalculator/
    ├── bmi_calculator_beginner.py   # CLI version (Beginner Tier)
    ├── bmi_calculator_advanced.py   # GUI version (Advanced Tier)
    ├── bmi_db_utils.py              # Database utilities (SQLite)
    ├── bmi_records.db               # (Auto-generated) SQLite database
    ├── README.md                    # This file
    └── screenshot.png               #screenshot 
    Demo (BMI calculaor)             #Demo Video (uploaded on linkedin)





