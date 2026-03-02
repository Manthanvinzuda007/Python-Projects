# The Metaclass (The "Boss" of all classes)
class ForceUppercaseMeta(type):
    # This method runs the MOMENT a new class is defined
    def __new__(cls, name, bases, dct):
        if not name.isupper():
            raise TypeError(f"Safety Error: Class name '{name}' must be ALL CAPS!")
        
        print(f"Metaclass Approval: Class '{name}' created successfully.")
        return super().__new__(cls, name, bases, dct)

# Example 1: This follows the rule
class USER(metaclass=ForceUppercaseMeta):
    def greet(self):
        return "Hello from a valid class!"

# Example 2: This will BREAK the program immediately
try:
    class Customer(metaclass=ForceUppercaseMeta):
        pass
except TypeError as e:
    print(f"Caught by Metaclass: {e}")

# Main Execution
if __name__ == "__main__":
    u = USER()
    print(u.greet())
                                                                                             # Created By Manthan Vinzuda....
