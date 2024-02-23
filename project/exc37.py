#symbol review
"""
1.

The as keyword creats an alias

relates to import and from keywords

Now with statement:
    simplifies management of common resources like file streams.
    observe following code


A function or class that supports the with statement is knows as a context manager.
A context manager allows you to open and close resources right when you want to.
e.g. open() function 
"""
#wihout using with
file = open('tekst.txt', 'w')
file.write('hello world')
file.close()

#using with
with open('tekst.txt', 'w') as file:
    file.write('hell world2') # no need to close

"""
2.

assert:
If assertion condition true: program continues to run
if condition false; assertion stops the program and gives assertion error (AssertionError)
Syntax:
    assert <condition>
    assert <condition>,<error message>

"""
#example: takes a list and calculate average, can't be empty list
def avg(marks):
    assert len(marks) != 0, "List is empty."
    return sum(marks)/len(marks)
mark1 = []
#running this func with mark returns AssertionError: message          


"""
3.

classes

classes provide a means of bundling data and functionality together.
Creating a new class creates a new type of object, allowing new instances of that type to be made.
Each class instance can have attributes attached to it, can also have methods (defined by its class) for modyfing its state.
"""

"""
4.

continue

explanation own word: skip an iteration when condition is false
"""

#example
for i in 'Python':
    if letter == 'h':
        continue
    print( 'current letter:', i)
#this will print Pyton)

"""
5.

except

if an exception happens (in a try clause), do this:: except ValueError as e: print(e)

try:
  print("Hello")
except:
  print("Something went wrong")
else:
  print("Nothing went wrong")
"""

"""
6.
exec()

This method executes a dynamically created program, which is either a string or a code objext. 
aka run string as python

program = 'a = 5\nb=10\nprint("Sum =", a+b)'
exec(program)
sum = 15
"""

"""
7.

finally block will always be excuted
used in try, except blocks
"""

"""
8.

pass

used as placeholder for future code.
nothing happens.
to avoid error.
"""


"""
9.
raise

raise an error and stop the program if condition == False

ex:
x=-1
if x < 0:
    raise Exception("sorry, no numbers below zero")
"""


"""
10.

Yield

similar to return statement.
slight diff: 

"""
