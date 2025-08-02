# Find the first 30 prime numbers using the trial division method

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def first_n_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes

# Example usage:
if __name__ == "__main__":
    n = 30
    prime_numbers = first_n_primes(n)
    print(f"The first {n} prime numbers are: {prime_numbers}")


