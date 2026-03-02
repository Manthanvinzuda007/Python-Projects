# Createdd By Manthan Vinzuda 
import turtle
import math
import time

# --- Configuration ---
WIDTH, HEIGHT = 900, 800
BASE_SIZE = 120
MAX_DEPTH = 10
BG_COLOR = "black"
LINE_COLOR_BASE = "white"
ANIMATION_DELAY = 0.01  # Delay between edges for "growth" feel

def get_color(depth):
    """Calculates color gradient from white to green based on recursion depth."""
    # Scale from depth 0 (White) to MAX_DEPTH (Bright Green)
    ratio = depth / MAX_DEPTH
    r = int(255 * (1 - ratio))
    g = 255
    b = int(255 * (1 - ratio))
    return (r / 255, g / 255, b / 255)

def draw_square(t, x, y, size, angle, depth):
    """
    Draws a square outline starting from (x, y) at a specific angle.
    Draws edge-by-edge to simulate growth.
    """
    t.penup()
    t.goto(x, y)
    t.setheading(angle)
    t.color(get_color(depth))
    t.pensize(max(1, MAX_DEPTH - depth))
    t.pendown()

    # Store vertices for the next level calculation
    # We need the top-left corner and the peak of the triangle
    # vertex[0] = bottom-left (x, y)
    # vertex[1] = top-left
    # vertex[2] = top-right
    # vertex[3] = bottom-right
    
    vertices = []
    
    for i in range(4):
        t.forward(size)
        vertices.append(t.pos())
        t.left(90)
        
    # To match the "growth" feel, we update the screen after the square is finished
    turtle.update()
    time.sleep(ANIMATION_DELAY)
    
    return vertices

def draw_pythagoras_tree(t, x, y, size, angle, depth):
    """
    Recursive function to generate the tree.
    Follows: left_size = size * cos(45), right_size = size * sin(45)
    """
    if depth > MAX_DEPTH or size < 2:
        return

    # 1. Draw the current square (the "trunk" or parent branch)
    # Returns the corners of the square
    # v[0]: BL, v[1]: BR, v[2]: TR, v[3]: TL
    v = draw_square(t, x, y, size, angle, depth)
    
    # Top edge vertices for the triangle base
    # In turtle, after drawing 4 sides:
    # side 1: (x,y) -> (x+S, y) [if angle 0]
    # side 2: -> (x+S, y+S)
    # side 3: -> (x, y+S)
    # side 4: -> (x, y)
    
    # Let's use more explicit vertex naming for clarity:
    # v[0] is bottom-right, v[1] is top-right, v[2] is top-left, v[3] is bottom-left
    # depending on the loop. Let's re-calculate manually for 100% precision.
    
    # Top-left corner of the parent square
    tl_x = x + size * math.cos(math.radians(angle + 90))
    tl_y = y + size * math.sin(math.radians(angle + 90))
    
    # Construction angle (45 degrees as requested)
    branch_angle = 45
    rad_angle = math.radians(branch_angle)
    
    # Pythagorean sizes
    size_l = size * math.cos(rad_angle)
    size_r = size * math.sin(rad_angle)
    
    # 2. Calculate the "Peak" of the triangle sitting on the top edge
    # The peak is the point where the two child squares meet.
    # It is located (size_l) distance away from the top-left corner at (angle + 45)
    peak_x = tl_x + size_l * math.cos(math.radians(angle + branch_angle))
    peak_y = tl_y + size_l * math.sin(math.radians(angle + branch_angle))
    
    # 3. Recursive calls
    # Left Child: Starts at Top-Left, rotated left by 45 degrees
    draw_pythagoras_tree(t, tl_x, tl_y, size_l, angle + branch_angle, depth + 1)
    
    # Right Child: Starts at the Peak, rotated right by 45 degrees (angle - 45)
    # The square is drawn "up" from its base, so its base angle is angle - 45
    draw_pythagoras_tree(t, peak_x, peak_y, size_r, angle + branch_angle - 90, depth + 1)

def main():
    # Screen setup
    screen = turtle.Screen()
    screen.setup(WIDTH, HEIGHT)
    screen.bgcolor(BG_COLOR)
    screen.title("Mathematical Pythagoras Tree - Engineering Visualization")
    screen.tracer(0) # Disable automatic animation for manual control

    # Turtle setup
    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    
    # Initial parameters
    start_x = -BASE_SIZE / 2
    start_y = -HEIGHT / 2 + 50
    
    # Start the recursive drawing
    draw_pythagoras_tree(t, start_x, start_y, BASE_SIZE, 0, 0)
    
    # Final update to ensure everything is rendered
    screen.update()
    screen.mainloop()

if __name__ == "__main__":
    main()
