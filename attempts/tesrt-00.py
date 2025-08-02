def solution(filename):
    with open(filename, 'rt') as file:
        for line in file:
            yield line.strip()
    print("closed file")

if __name__ == "__main__":
    for line in solution('attempts/tesrt-00.py'):
        print(line.strip())    
