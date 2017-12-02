Pyfuck -- Python esolang language using only *+travels[]'()*.
=========

How few distinct characters can we use to simulate any python program?

We can at least do 13!

My initial hope is to avoid all alphanumeric characters. Unfortunately, because python has strong-typing (as opposde to javascript), we cannot implicitly cast between e.g. integers and strings. This means that, as far as I could figure out, there's no way to call a function or get a string without using some alhpanumeric character to start with.

Luckily, we can still avoid all numbers, and only use 7 letters to enable `eval` and `str`, from where we'll construct everything.

Inspired by [jsfuck](jsfuck.com).



Encoding Process
----------------------

WIP -- see [source code](pyfuck.py) for now!


TODO
----------------------

* Compatible with python2
* Integrate with https://github.com/csvoss/onelinerizer to execute any python program
* Enable the use of 'exec' instead of 'eval'
* REMOVE THE NEED OF `'`  -- this is actually possible! We can globally replace `'` with `str(str)[(all([])+all([])+all([])+all([])+all([])+all([])+all([]))]`, for example, and reduce our character set to 12 characters.
* Shorter / more efficient encoding


Examples
--------


```python
print("Hello, world!")
```

**Encodes into:**



```python
eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])))+')')+'r'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]')+'t('+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])))+str((all([])+all([])))+')')+'ell'+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+'rl'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((+all([[]])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+')'

```

a total of 6019 characters using only `+travels[]'()` that evaluates to the string `'print("Hello world!)'` (add eval(...) around it to actually print).