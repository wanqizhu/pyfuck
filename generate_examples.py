from pyfuck import encode_code


with open('examples/hello_world.py', 'w') as fh:
    fh.write(encode_code('print("Hello World!")'))


with open('examples/fizzbuzz.py', 'w') as fh:
    fh.write(encode_code("""for fizzbuzz in range(31):
    if fizzbuzz % 3 == 0 and fizzbuzz % 5 == 0:
        print("fizzbuzz")
    elif fizzbuzz % 3 == 0:
        print("fizz")
    elif fizzbuzz % 5 == 0:
        print("buzz")
    else:
        print(fizzbuzz)"""))
