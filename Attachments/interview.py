n = int(input())

for number in range(1, n+1):
    if number % 4 == 0 and number % 6 == 0:
        print('CSESoc Rocks')
    elif number % 4 == 0:
        print('CSESoc')
    elif number % 6 == 0:
        print('Rocks')
    else:
        print(number)
