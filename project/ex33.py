numbers = []

def while_func(a,b):
    i=0
    while i<a:
        numbers.append(i)
        i += b
    return print(numbers)
print("Give me a number")
a = int(input('> '))
print("Give me another number")
b = int(input('> '))

while_func(a,b)
