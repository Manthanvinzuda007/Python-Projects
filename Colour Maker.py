import tkinter as tk
import random

def generate_color():
    # Generate a random hex color code
    letters = "0123456789ABCDEF"
    color = "#" + "".join(random.choice(letters) for i in range(6))
    
    # Update UI
    root.configure(bg=color)
    color_label.config(text=color, bg=color)
    title_label.config(bg=color)
    
    # Logic to keep text readable (Dark vs Light)
    # If the color is too bright, make text black; if dark, make text white
    if sum(int(color[i:i+2], 16) for i in (1, 3, 5)) > 400:
        color_label.config(fg="black")
    else:
        color_label.config(fg="white")

# 1. Setup Window
root = tk.Tk()
root.title("Vinzuda Color Studio")
root.geometry("400x400")
root.configure(bg="#2c3e50")

# 2. UI Elements
title_label = tk.Label(root, text="Color Inspiration", font=("Arial", 16, "bold"), 
                       bg="#2c3e50", fg="white")
title_label.pack(pady=30)

color_label = tk.Label(root, text="#2C3E50", font=("Courier", 30, "bold"), 
                       bg="#2c3e50", fg="white")
color_label.pack(pady=20)

# 3. The Action Button
gen_button = tk.Button(root, text="Generate New Color", font=("Arial", 12),
                       padx=20, pady=10, command=generate_color)
gen_button.pack(pady=40)

root.mainloop()
                                                                                                         # Created By Manthan Vinzuda....
