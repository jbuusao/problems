# A marketplace tracks the sales of various products for each day. Design al algorithm to find the product with the highest sales for each day, ensuring that the results are presented in chronological order. 
# The algorithm should efficiently handle large datasets and provide accurate results.

def highest_sales_per_day(sales_data):
    highest_sales = {}
    
    for day, sales in sales_data.items():
        if sales:  # Check if there are sales for the day
            highest_product = max(sales, key=sales.get)
            highest_sales[day] = highest_product
    
    return highest_sales

# Example usage:
if __name__ == "__main__":
    sales_data = {
        "2023-10-01": {"Product A": 150, "Product B": 200, "Product C": 100},
        "2023-10-02": {"Product A": 300, "Product B": 250, "Product C": 400},
        "2023-10-03": {"Product A": 200, "Product B": 300},
        "2023-10-04": {},
    }
    
    result = highest_sales_per_day(sales_data)
    print("Highest sales per day:", result)
# Output should be:
# Highest sales per day: {'2023-10-01': 'Product B', '2023-10-02': 'Product C', '2023-10-03': 'Product B'}
# Note: The output for '2023-10-04' is not included since there are no sales for that day.

