# A logistics company manages several climate controlled units for storing various items. They have received a set of orders each specifying a required storage temperature.
# Design an algorithm to determine how many of these items need to be stored at a temperature below zero.

def count_below_zero(orders):
    count = 0
    
    for order in orders:
        if order < 0:  # Check if the order requires a temperature below zero
            count += 1
    
    return count

# Example usage:
if __name__ == "__main__":
    orders = [-5, 10, -3, 0, 2, -1, 4]
    result = count_below_zero(orders)
    print("Orders requiring storage below zero:", result)
# Output should be:
# Orders requiring storage below zero: 3
