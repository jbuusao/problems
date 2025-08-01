def solution(numbers):
    result = Set()
    for number in numbers:
        if number % 2 == 0:
            result.add(number)