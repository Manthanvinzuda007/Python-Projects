import functools
import logging

# Setting up a basic logger
logging.basicConfig(level=logging.INFO)

# The Decorator (A function that modifies another function)
def smart_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Attempt to run the original function
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error automatically
            logging.error(f"Error in {func.__name__} with arguments {args}: {e}")
            return "System Error: Action blocked for safety."
    return wrapper

# Application of the Decorator
@smart_error_handler
def divide_numbers(a, b):
    return a / b

@smart_error_handler
def get_user_data(user_id):
    # Simulating a database error
    raise ConnectionError("Database is offline!")

# Main Execution
if __name__ == "__main__":
    print("---System Active ---")
    
    # This would normally crash the program (DivisionByZero)
    result1 = divide_numbers(10, 0)
    print(f"Result 1: {result1}")
    
    # This would normally crash the program (ConnectionError)
    result2 = get_user_data(101)
    print(f"Result 2: {result2}")
                                                                                                                                                     # Created By Manthan Vinzuda....
