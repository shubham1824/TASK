import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
import pandas as pd
import csv
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup


class FinanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("800x600")  # Adjusted to full screen size
        self.root.state('zoomed')  # Maximized window
        self.create_database()

        # Load and set background image
        self.bg_image = Image.open("WhatsApp Image 2025-02-12 at 00.29.33_962b961d.jpg")
        self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()),
                                             Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        bg_label = tk.Label(root, image=self.bg_photo)
        bg_label.place(relwidth=1, relheight=1)

        frame = tk.Frame(root)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(frame, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.category_entry = tk.Entry(frame)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Type (Income/Expense):").grid(row=2, column=0, padx=5, pady=5)
        self.type_entry = tk.Entry(frame)
        self.type_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Budget Goal:").grid(row=3, column=0, padx=5, pady=5)
        self.budget_entry = tk.Entry(frame)
        self.budget_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(frame, text="Add Record", command=self.add_record).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        tk.Button(frame, text="View Records", command=self.view_records).grid(row=5, column=0, columnspan=2, padx=5,
                                                                              pady=5)
        tk.Button(frame, text="Generate Report", command=self.generate_report).grid(row=6, column=0, columnspan=2,
                                                                                    padx=5, pady=5)
        tk.Button(frame, text="Export to CSV", command=self.export_to_csv).grid(row=7, column=0, columnspan=2, padx=5,
                                                                                pady=5)
        tk.Button(frame, text="Scrape Data", command=self.scrape_data).grid(row=8, column=0, columnspan=2, padx=5,
                                                                            pady=5)

    def create_database(self):
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                          (id INTEGER PRIMARY KEY, amount REAL, category TEXT, type TEXT)''')
        conn.commit()
        conn.close()

    def add_record(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        trans_type = self.type_entry.get()

        if not amount or not category or not trans_type:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (amount, category, type) VALUES (?, ?, ?)",
                       (amount, category, trans_type))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Record added successfully!")

    def view_records(self):
        conn = sqlite3.connect("finance.db")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()

        record_str = "Records:\n" + df.to_string(index=False)
        messagebox.showinfo("Transaction Records", record_str)

    def generate_report(self):
        conn = sqlite3.connect("finance.db")
        df = pd.read_sql_query(
            "SELECT category, SUM(amount) as total FROM transactions WHERE type='Expense' GROUP BY category", conn)
        conn.close()

        if df.empty:
            messagebox.showinfo("Report", "No expense records found.")
            return

        plt.figure(figsize=(6, 6))
        plt.pie(df['total'], labels=df['category'], autopct='%1.1f%%')
        plt.title("Expense Distribution")
        plt.show()

    def export_to_csv(self):
        conn = sqlite3.connect("finance.db")
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            df.to_csv(filename, index=False)
            messagebox.showinfo("Success", "Data exported successfully!")

    def scrape_data(self):
        url = "https://example.com"  # Replace with actual URL
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        data = []
        for item in soup.find_all("div", class_="data-item"):  # Adjust based on the site structure
            title = item.find("h2").text.strip()
            value = item.find("span", class_="value").text.strip()
            data.append([title, value])

        df = pd.DataFrame(data, columns=["Title", "Value"])
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            df.to_csv(filename, index=False)
            messagebox.showinfo("Success", "Scraped data saved successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTracker(root)
    root.mainloop()
