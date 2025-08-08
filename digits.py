def letter_combinations(digits):
    def combinations(digits):
        digits = [digit for digit in str(digits)]
        out=[]
        def bt(start, end):
            if start == end:
                out.append(digits[:])
            for i in range(start, end):
                digits[start], digits[i] = digits[i], digits[start]
                bt(start+1, end)
                digits[start], digits[i] = digits[i], digits[start]
        bt(0, len(digits))
        out = ["".join(i) for i in out]
        return out



letter_combinations("abc")