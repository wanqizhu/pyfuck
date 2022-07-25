# Pyfuck -- Esoteric Python using only **`exc'=()%+`**.

How few distinct characters can we use to write and execute any python program?

~~We can at least do 13! **[(+travels')]**~~  
We can now do it in 9! **`exc'=()%+`** and doesn't include any numbers and only the letters required for "exec"

Inspired by:
- [jsfuck](jsfuck.com)
- [the original pyfuck repo](https://github.com/wanqizhu/pyfuck)
- [this Stackoverflow post](https://codegolf.stackexchange.com/a/110677)

## Usage
```python
import pyfuck
code = pyfuck.encode_code('print("Hello World!")')
```

## Encoding Process
TLDR: To execute any python3 string, we convert it into a sequence of chars converted from ints using the `%c` format string, concatenate and wrap the entire thing in `exec()`

### Obtaining Numbers
First, we notice that `()==()` evaluates to True and `True==()` (or `(()==())==()`) evalutes to False. This allows us to build up the integers using 
```python
0: (((()==())==())+((()==())==())) # False+False,
1: (((()==())==())+(()==())),      # False+True
2: ((()==())+(()==())),            # True+True
3: ((()==())+(()==())+(()==()))    # True+True+True
```

### Obtaining Strings
Once we have any non-negative integer we are able to build the strings using a concatenation of single charater format strings. Ie the byte string '\x00\x01\x02' can be represented by:
```python
'%c'%0 + '%c'%1 + '%c'%2 + '%c'%3
```
When we expand digits and remove spaces we get:
```python
'%c'%(((()==())==())+((()==())==()))+'%c'%(((()==())==())+(()==()))+'%c'%((()==())+(()==()))+'%c'%((()==())+(()==())+(()==()))
```

### Putting it all together
Once we can encode strings we can wrap the string in `exec()` and execute.

To encode the simpliest python3 program '12' the following steps are taken:
1) Convert to a list of chars:  `['1', '2']`
2) Convert to a list of ints:  `[49, 50]`
3) Convert to a concatenation of format strings:  `'%c'%49+'%c'%50`
4) Expand numbers and wrap with `exec()`:
    ```python
    exec('%c'%((()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==()))+'%c'%((()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())+(()==())))
    ```

## Examples
See the [generate_examples.py](./generate_examples.py) file for the original source code
### [hello_world.py](./examples/hello_world.py)
```python
print("Hello World!")
```

### [fizzbuzz.py](./examples/fizzbuzz.py)
```python
for fizzbuzz in range(31):
    if fizzbuzz % 3 == 0 and fizzbuzz % 5 == 0:
        print("fizzbuzz")
    elif fizzbuzz % 3 == 0:
        print("fizz")
    elif fizzbuzz % 5 == 0:
        print("buzz")
    else:
        print(fizzbuzz)
```