#import argv from module sys, allows to pass arguments from command into script. argv is the Argument variable, the variable that holds the passed arguments.

from sys import argv

#Unpacks arg so that, rather than holding all the arguments, it gets assigned to variables.

script, filename = argv

#create text object by opening the file, apply read() method to access the content of the text object. everything is considered as a string.

txt = open(filename)

print(f'Here is your file {filename}:')
print(txt.read())

#similar, except for input.
print("Type the filename again:")
file_again = input('> ')

txt_again = open(file_again)

print(txt_again.read())

txt.close()
txt_again.close()
