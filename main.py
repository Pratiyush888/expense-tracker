import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

# Connect to SQLite database
def connect_to_sqlite():
    conn = sqlite3.connect('expenses.db')
    return conn

# Create users table
def create_users_table(conn):
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()

# Create expenses table
def create_expenses_table(conn):
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            amount REAL,
            date TEXT,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()

# Register a new user
def register_user(username, password):
    conn = connect_to_sqlite()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful! You can now log in.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")
    finally:
        conn.close()

# Authenticate user
def authenticate_user(username, password):
    conn = connect_to_sqlite()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# Add expense to database
def add_expense(user_id, category, amount, date, description):
    conn = connect_to_sqlite()
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO expenses (user_id, category, amount, date, description) 
        VALUES (?, ?, ?, ?, ?) 
    ''', (user_id, category, amount, date, description))
    conn.commit()
    conn.close()

# View expenses for a user
def get_expenses(user_id):
    conn = connect_to_sqlite()
    cursor = conn.cursor()
    cursor.execute('SELECT id, category, amount, date, description FROM expenses WHERE user_id = ?', (user_id,))
    expenses = cursor.fetchall()
    conn.close()
    return expenses

# Delete all expenses for a user
def delete_all_expenses(user_id):
    conn = connect_to_sqlite()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# Delete a specific expense
def delete_expense(user_id, expense_id):
    conn = connect_to_sqlite()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE user_id = ? AND id = ?', (user_id, expense_id))
    conn.commit()
    conn.close()

# Export data to CSV
def export_data_to_csv():
    conn = connect_to_sqlite()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()
    conn.close()

    if expenses:
        with open('expenses_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'User ID', 'Category', 'Amount', 'Date', 'Description'])
            writer.writerows(expenses)
        messagebox.showinfo("Success", "Data exported successfully!")
    else:
        messagebox.showwarning("No Data", "No data available to export.")

# Show Pie Chart - Generates and displays the pie chart
def show_pie_chart():
    # Clear any existing pie chart
    for widget in pie_chart_frame.winfo_children():
        widget.destroy()

    # Fetch data for the pie chart
    expenses = get_expenses(current_user_id)
    categories = {}
    for expense in expenses:
        category = expense[1]
        amount = expense[2]
        categories[category] = categories.get(category, 0) + amount

    # Plot Pie chart if data is available
    if categories:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle

        canvas = FigureCanvasTkAgg(fig, master=pie_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# GUI Functions
def show_login_page():
    for widget in root.winfo_children():
        widget.destroy()

    login_frame = tk.Frame(root, bg="#E1F5FE")
    login_frame.pack(pady=20)

    tk.Label(login_frame, text="Username:", bg="#E1F5FE", font=('Helvetica', 12)).grid(row=0, column=0, padx=10, pady=5)
    tk.Label(login_frame, text="Password:", bg="#E1F5FE", font=('Helvetica', 12)).grid(row=1, column=0, padx=10, pady=5)

    username_entry = tk.Entry(login_frame, width=30, font=('Helvetica', 12))
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    password_entry = tk.Entry(login_frame, width=30, show="*", font=('Helvetica', 12))
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()
        global current_user_id
        current_user_id = authenticate_user(username, password)
        if current_user_id:
            show_main_page()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def handle_register():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            register_user(username, password)
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    tk.Button(login_frame, text="Login", command=handle_login, bg="#4CAF50", fg="white", font=('Helvetica', 12), relief="flat").grid(row=2, column=0, padx=10, pady=10)
    tk.Button(login_frame, text="Register", command=handle_register, bg="#FF9800", fg="white", font=('Helvetica', 12), relief="flat").grid(row=2, column=1, padx=10, pady=10)

def show_main_page():
    for widget in root.winfo_children():
        widget.destroy()

    main_frame = tk.Frame(root, bg="#E1F5FE")
    main_frame.pack(pady=20, fill=tk.BOTH, expand=True)

    global pie_chart_frame
    pie_chart_frame = tk.Frame(root, bg="#FFFFFF")
    pie_chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tk.Label(main_frame, text="Category:", bg="#E1F5FE", font=('Helvetica', 12)).grid(row=0, column=0, padx=10, pady=5)
    tk.Label(main_frame, text="Amount:", bg="#E1F5FE", font=('Helvetica', 12)).grid(row=1, column=0, padx=10, pady=5)
    tk.Label(main_frame, text="Date (YYYY-MM-DD):", bg="#E1F5FE", font=('Helvetica', 12)).grid(row=2, column=0, padx=10, pady=5)
    tk.Label(main_frame, text="Description:", bg="#E1F5FE", font=('Helvetica', 12)).grid(row=3, column=0, padx=10, pady=5)
    tk.Label(main_frame, text="Expense ID (to delete):", bg="#E1F5FE", font=('Helvetica', 12)).grid(row=4, column=0, padx=10, pady=5)

    category_var = StringVar(value="Food")
    tk.OptionMenu(main_frame, category_var, "Food", "Clothes", "Travel", "Entertainment", "Bills", "Other").grid(row=0, column=1, padx=10, pady=5)

    entry_amount = tk.Entry(main_frame, width=30, font=('Helvetica', 12))
    entry_amount.grid(row=1, column=1, padx=10, pady=5)

    entry_date = tk.Entry(main_frame, width=30, font=('Helvetica', 12))
    entry_date.grid(row=2, column=1, padx=10, pady=5)

    entry_description = tk.Entry(main_frame, width=30, font=('Helvetica', 12))
    entry_description.grid(row=3, column=1, padx=10, pady=5)

    entry_expense_id = tk.Entry(main_frame, width=30, font=('Helvetica', 12))
    entry_expense_id.grid(row=4, column=1, padx=10, pady=5)

    # Add Expense
    def add_expense_from_gui():
        category = category_var.get()
        amount = entry_amount.get()
        date = entry_date.get()
        description = entry_description.get()

        if category and amount and date:
            try:
                add_expense(current_user_id, category, float(amount), date, description)
                messagebox.showinfo("Success", "Expense added successfully!")
                entry_amount.delete(0, tk.END)
                entry_date.delete(0, tk.END)
                entry_description.delete(0, tk.END)
                view_expenses()  # Refresh the expense list
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount!")

    tk.Button(main_frame, text="Add Expense", command=add_expense_from_gui, bg="#4CAF50", fg="white", font=('Helvetica', 12), relief="flat").grid(row=5, column=0, padx=10, pady=10)

    # View Expenses
    def view_expenses():
        expenses = get_expenses(current_user_id)
        expenses_listbox.delete(0, tk.END)
        for expense in expenses:
            expenses_listbox.insert(
                tk.END, f"ID: {expense[0]}, Category: {expense[1]}, Amount: {expense[2]}, Date: {expense[3]}, Description: {expense[4]}"
            )

    tk.Button(main_frame, text="View Expenses", command=view_expenses, bg="#03A9F4", fg="white", font=('Helvetica', 12), relief="flat").grid(row=6, column=0, padx=10, pady=10)

    # Show Pie Chart
    tk.Button(main_frame, text="Show Pie Chart", command=show_pie_chart, bg="#9C27B0", fg="white", font=('Helvetica', 12), relief="flat").grid(row=6, column=1, padx=10, pady=10)

    # Export Data to CSV
    tk.Button(main_frame, text="Export Data", command=export_data_to_csv, bg="#FFC107", fg="white", font=('Helvetica', 12), relief="flat").grid(row=7, column=0, padx=10, pady=10)

    # Expenses Listbox
    expenses_listbox = tk.Listbox(main_frame, width=80, height=10, font=('Helvetica', 12))
    expenses_listbox.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    # Delete Expense
    def delete_expense_from_gui():
        expense_id = entry_expense_id.get()
        if expense_id:
            delete_expense(current_user_id, int(expense_id))
            messagebox.showinfo("Success", "Expense deleted successfully!")
            view_expenses()

    tk.Button(main_frame, text="Delete Expense", command=delete_expense_from_gui, bg="#FF5722", fg="white", font=('Helvetica', 12), relief="flat").grid(row=9, column=0, padx=10, pady=10)

    # Clear All Expenses
    def clear_all_expenses():
        delete_all_expenses(current_user_id)
        messagebox.showinfo("Success", "All expenses cleared!")
        view_expenses()

    tk.Button(main_frame, text="Clear All Expenses", command=clear_all_expenses, bg="#D32F2F", fg="white", font=('Helvetica', 12), relief="flat").grid(row=9, column=1, padx=10, pady=10)

# Initialize SQLite database
conn = connect_to_sqlite()
create_users_table(conn)
create_expenses_table(conn)
conn.close()

# Create the main application window
root = tk.Tk()
root.geometry("800x600")
root.title("Expense Tracker")

current_user_id = None

show_login_page()

root.mainloop()
