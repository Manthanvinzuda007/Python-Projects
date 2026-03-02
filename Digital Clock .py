import tkinter as tk
from time import strftime

def update_time():
    # Get current time and date
    time_string = strftime('%H:%M:%S %p')
    date_string = strftime('%A, %B %d, %Y')
    
    # Update the labels
    time_label.config(text=time_string)
    date_label.config(text=date_string)
    
    # Call this function again after 1000ms (1 second)
    time_label.after(1000, update_time)

# 1. Create Window
root = tk.Tk()
root.title("Vinzuda Brand Clock")
root.geometry("500x300")
root.configure(bg="#1a1a1a")  # Deep dark background

# 2. Brand Label (Logo style)
brand_label = tk.Label(root, text="VINZUDA MANTHAN", font=("Impact", 24), 
                       bg="#1a1a1a", fg="#f1c40f") # Golden color
brand_label.pack(pady=(30, 0))

# 3. Time Display
time_label = tk.Label(root, font=("Helvetica", 48, "bold"), 
                      bg="#1a1a1a", fg="#00d2ff") # Cyan glow
time_label.pack()

# 4. Date Display
date_label = tk.Label(root, font=("Arial", 14), 
                      bg="#1a1a1a", fg="white")
date_label.pack(pady=10)

# Start the clock
update_time()

root.mainloop()
                                                                                                         # Created By Manthan Vinzuda....
