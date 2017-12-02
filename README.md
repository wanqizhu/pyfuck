Pyfuck -- Esoteric Python using only **[(+travels')]**.
=========

How few distinct characters can we use to simulate any python program?

We can at least do 13! **[(+travels')]**

My initial hope is to avoid all alphanumeric characters. Unfortunately, because python has strong-typing (as opposde to javascript), we cannot implicitly cast between e.g. integers and strings. This means that, as far as I could figure out, there's no way to call a function or get a string without using some alhpanumeric character to start with.

Luckily, we can still avoid all numbers, and only use 7 letters to enable `eval` and `str`, which allows we'll construct everything else.

Inspired by [jsfuck](jsfuck.com).



Encoding Process
----------------------

To evaluate any python expression, we can turn it into a string and call `eval()`. Because we can decompose the string arbituarily (break up each character and rebuilding with `+`), our main idea is to use our small set of characters and map to an arbituary character, which then enables us to execute arbituarily complex python code.


First, we notice that `+True` converts the boolean into the integer 1, and `+False` gives 0. This allows us to build up the integers:

```python
digits = {
    0: '+all([[]])',
    1:  '+all([])',
    2: 'all([])+all([])'  # 1 + 1
    # and so forth
}
```

With integers, we can take advantage of string indexing to get individual characters. In particular, calling `str` on an object/function gives its definition/docstrings, from which we can pick out individual characters.

```python
# python 3; slightly different str(...) in python2
str(str)
"<class 'str'>"

str(eval)
'<built-in function eval>'
```

For example, `str(str)[1]` gives `c`. This gives us the following characters:

```python
{
    'c': 'str(str)[+all([])]',                                              # str(str)[1]
    'f': 'str(eval)[eval(str(' + digits[1] + ')+str(' + digits[0] + '))]',  # str(eval)[10]
    'n': 'str(eval)[' + digits[8] + ']',                                    # str(eval)[8]
    'o': 'str(eval)[eval(str(' + digits[1] + ')+str(' + digits[6] + '))]',  # str(eval)[16]
    'u': 'str(eval)[' + digits[2] + ']'.                                    # str(eval)[2]
}

```

where digits[i] is the string representation of the number i from above. Note how to get 10 or larger numbers, we use string concatination on each digit, so we don't need a million copies of `'+all([])'` to form large numbers.

This allows us to build more complex characters, using additional docstrings:

```python
{
  # str(float(1))[1]
  # eval('str(' + 'f' + 'l' + 'o' + 'at(' + '1' + '))[' + '1' + ']')
  '.': "+".join(["eval('str('", DICT['f'], "'l'", DICT['o'],
                 "'at(" + digits[1] + "))[" + digits[1] + "]')"])

  # str(str.count)[4]
  'h': "+".join(["eval('str(str'", DICT['.'],
                 DICT['c'], DICT['o'], DICT['u'], DICT['n'], "'t)[" + digits[4] + "]')"])
}
```

We use `+` to build up the string we want, and then wraps it around in eval to get the desired character.


Now, we have the characters `chr` and access to any integer, so we can simply call `chr()` to get any ascii character! Bingo.

```python
>>> chr(119) + chr(111) + chr(119)
'wow'
```



Writing the actual encoding function turned out to be a pain. Quotation nesting / use of eval(...) / repeated substitution was really messy to encode. Alas, it seem to work now!


See [source code](pyfuck.py) for full details!



Examples
--------

# Encoding arbituary characters

```python
'@' = chr(64)
    = eval('c'                + 'h'                                   + 'r(' + '64' + ')')
    = eval(str(str)[+all([])] + str(str.count)[4]                     + 'r(' + str(6) + str(4) + ')')
    = ...                     + eval('str(str' + '.' + 'count)[4]')   + 'r(' + str((1+1+1+1+1+1)+str((1+1+1+1)+')')
    
    = ...                     # substituting expression for '.', 'c', 'o', 'u', 'n'; substituing +all([]) for 1


    = eval(''+eval('str(str)[+all([])]')      # 'c' 
                                              # 'h' = str(str.count)[4]

             +eval('str(str'                                              # str(str
                                                                          # '.' = str(float(1)[1])

                    +eval('str('                                                          # str(
                          +str(eval)[eval(str((+all([])))+str((+all([[]]))))]             # f
                          +'l'                                                            # l
                          +str(eval)[eval(str((+all([])))                                 # o
                                         +str((all([])+all([])+all([])
                                              +all([])+all([])+all([]))))]
                          +'at((+all([]))))[(+all([]))]')                                 # at(1)[1]

                    +str(str)[+all([])]                                   # c 
                                                                          # o = str(eval)[16]
                    +str(eval)[eval(str((+all([])))
                                    +str((all([])+all([])+all([])
                                         +all([])+all([])+all([]))))]
                                                 
                    +str(eval)[(all([])+all([]))]                         # u
                                                               
                    +str(eval)[(all([])+all([])+all([])+all([])           # n
                               +all([])+all([])+all([])+all([]))]
                                                                 
                    +'t)[(all([])+all([])+all([])+all([]))]')             # t)[4]

             +'r('                            # 'r(
              '
             +str((all([])+all([])+all([])    # '6'
                  +all([])+all([])+all([])))
                                              # '4'
             +str((all([])+all([])+all([])+all([])))
             +')'                             # ')'
          )

```


# Hello World

```python
print("Hello, world!")
```

**Encodes into:**



```python
eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])))+')')+'r'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([
]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]')+'t('+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'
at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])))+str((all([])+all([])))+')')+'ell'+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([
])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+a
ll([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+'rl'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((+all([[]])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval
(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+')'

```

```python
# without linebreak
eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])))+')')+'r'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]')+'t('+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])))+str((all([])+all([])))+')')+'ell'+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+'rl'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((+all([[]])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+')'
```

6019 characters, but only 13 unique ones!

Test it yourseslf, and the expressnion above evaluates to`'print("Hello world!)'`! Add eval(...) around it to actually run the command.





TODO
----------------------

* Compatible with python2
* Integrate with https://github.com/csvoss/onelinerizer to execute any python program
* Enable the use of 'exec' instead of 'eval'
* Shorter / more efficient encoding

* REMOVE THE NEED OF `'`  -- this is actually possible!
  - We can globally replace `'` with `str(str)[(all([])+all([])+all([])+all([])+all([])+all([])+all([]))] = str(str)[8]`, for example, and reduce our character set to 12 characters.
* Can we use even fewer characters? What's the limit?


