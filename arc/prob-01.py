# You are provided with a sequence of numbers. Develop a method to eliminate all repeated numbers from the sequence, ensuring that the sequence contains only unique numbers whilst preserving the original order.
def eliminate_repeats(sequence):
    seen = set()
    unique_sequence = []
    
    for number in sequence:
        if number not in seen:
            seen.add(number)
            unique_sequence.append(number)
    
    return unique_sequence

# Example usage:
if __name__ == "__main__":
    input_sequence = [1, 2, 2, 3, 4, 4, 5]
    result = eliminate_repeats(input_sequence)
    print("Original sequence:", input_sequence)
    print("Unique sequence:", result)
# Output should be:
# Original sequence: [1, 2, 2, 3, 4, 4, 5]
# Unique sequence: [1, 2, 3, 4, 5]

