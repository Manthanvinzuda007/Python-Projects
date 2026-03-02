                                                                                                                                                     # Created By Manthan Vinzuda....
import tkinter as tk
from tkinter import messagebox

def add_task():
    task = entry.get()
    if task != "":
        listbox.insert(tk.END, task)
        entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "You must enter a task!")

def delete_task():
    try:
        selected_task_index = listbox.curselection()[0]
        listbox.delete(selected_task_index)
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to delete!")

# 1. Create the Main Window
root = tk.Tk()
root.title("Vinzuda Task Manager")
root.geometry("400x450")

# 2. UI Layout - The Header
label = tk.Label(root, text="My Tasks", font=("Arial", 18, "bold"))
label.pack(pady=10)

# 3. Input Box
entry = tk.Entry(root, font=("Arial", 14), width=25)
entry.pack(pady=5)

# 4. Buttons (Functional UI)
add_button = tk.Button(root, text="Add Task", width=20, bg="#2ecc71", fg="white", command=add_task)
add_button.pack(pady=5)

delete_button = tk.Button(root, text="Delete Selected", width=20, bg="#e74c3c", fg="white", command=delete_task)
delete_button.pack(pady=5)

# 5. Task List (The Display)
listbox = tk.Listbox(root, font=("Arial", 12), width=40, height=10)
listbox.pack(pady=10, padx=10)

# Start the Application
root.mainloop()
