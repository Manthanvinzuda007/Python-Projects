# By - Manthan Vinzuda 
import tkinter as tk
import math
import time

class MechanicalClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Mechanical Clock")
        self.canvas = tk.Canvas(root, width=400, height=400, bg='#1a1a1a', highlightthickness=0)
        self.canvas.pack()
        
        # Clock settings
        self.center_x = 200
        self.center_y = 200
        self.radius = 150
        
        self.update_clock()

    def draw_gear(self):
        """Draws a decorative gear-like outer rim"""
        for i in range(0, 360, 10):
            angle = math.radians(i)
            x_outer = self.center_x + (self.radius + 10) * math.cos(angle)
            y_outer = self.center_y + (self.radius + 10) * math.sin(angle)
            self.canvas.create_line(self.center_x, self.center_y, x_outer, y_outer, fill='#333333', width=2)
            
        self.canvas.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                                self.center_x + self.radius, self.center_y + self.radius,
                                outline='#d4af37', width=4) # Gold rim

    def update_clock(self):
        self.canvas.delete("all")
        self.draw_gear()
        
        # Get current time
        now = time.localtime()
        hr = now.tm_hour % 12
        mn = now.tm_min
        sc = now.tm_sec

        # Calculate angles (adjusted by -90 degrees because 0 rad is at 3 o'clock)
        # Formula: Angle = (Unit/Total_Units * 2 * PI) - PI/2
        sec_angle = (sc / 60) * 2 * math.pi - math.pi / 2
        min_angle = (mn / 60) * 2 * math.pi - math.pi / 2
        hour_angle = ((hr + mn / 60) / 12) * 2 * math.pi - math.pi / 2

        # Draw Hands
        self.create_hand(hour_angle, self.radius * 0.5, '#ffffff', 6)  # Hour
        self.create_hand(min_angle, self.radius * 0.8, '#cccccc', 4)   # Minute
        self.create_hand(sec_angle, self.radius * 0.9, '#ff4500', 2)   # Second

        # Center pin
        self.canvas.create_oval(self.center_x-5, self.center_y-5, self.center_x+5, self.center_y+5, fill='#d4af37')

        # Refresh every 1000ms (1 second)
        self.root.after(1000, self.update_clock)

    def create_hand(self, angle, length, color, width):
        x = self.center_x + length * math.cos(angle)
        y = self.center_y + length * math.sin(angle)
        self.canvas.create_line(self.center_x, self.center_y, x, y, fill=color, width=width, capstyle='round')

if __name__ == "__main__":
    root = tk.Tk()
    clock = MechanicalClock(root)
    root.mainloop()
                                                                                                                                # Created By Manthan Vinzuda....

