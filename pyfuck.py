#/usr/bin/python3
import re

base = set("+travels[]'()")


digits = {
    0: '+all([[]])',
    1:  '+all([])',
    2: 'all([])+all([])'
}
for i in range(3, 10):
    digits[i] = digits[i-1] + digits[1]

# use paranthesis in case. Not sure if needed
for i in range(0, 10):
    digits[i] = '(' + digits[i] + ')'

# print(digits)


DICT = {
    # 'a': 'str(str)[' + digits[3] + ']',
    'c': 'str(str)[+all([])]',  # 1
    # 'e': 'str(eval)[eval(str(' + digits[1] + ')+str(' + digits[9] + '))]',
    'f': 'str(eval)[eval(str(' + digits[1] + ')+str(' + digits[0] + '))]', # 10
    'n': 'str(eval)[' + digits[8] + ']',  # 8
    'o': 'str(eval)[eval(str(' + digits[1] + ')+str(' + digits[6] + '))]',
    'u': 'str(eval)[' + digits[2] + ']',
    '\'': 'str(str)[' + digits[7] + ']',
}

# have 'float'  
DICT['.'] = "+".join(["eval('str('", DICT['f'], "'l'", DICT['o'],
            "'at(" + digits[1] + "))[" + digits[1] + "]')"]) #'str(float(1))[1]'

# have str.count
DICT['h'] = "+".join(["eval('str(str'", DICT['.'],
            DICT['c'], DICT['o'], DICT['u'], DICT['n'], "'t)[" + digits[4] + "]')"]) # str(str.count)[4]

## Now we have chr(), we can get every alphanumeric var



# print(DICT)


for i in DICT:
    # print(i, eval(DICT[i]))
    assert i == eval(DICT[i]), (i, DICT[i])

## convery every program into a string, then wrap eval(...) around it

TMP = '\x01'  # substitute out single quotes

def encode(s, with_eval=False):
    new_str = ''
    for c in s:
        # substitute for arbituary characters using chr()
        if not c.isdigit() and c not in base and c not in DICT:
            new_str += "'+eval('chr(" + str(ord(c)) + ")')+'"
        else:
            if c == '\'':
                new_str += "'+" + TMP + "+'"  # fix triple-quote issue
            else:
                new_str += c

    s = "'" + new_str + "'"

    new_str = ''
    for c in s:
        if c in base or c.isdigit() or c == TMP:
            new_str += c
        else:
            # substitute characters in DICT with base characters
            if c in ['.', 'h']:
                new_str += "'+" + DICT[c] + "+'"
            else:
                new_str += "'+eval('" + DICT[c] + "')+'"

    s = new_str
    new_str = ''

    # deal with numbers
    def repl(matchobj):
        i = matchobj.group(0)

        if i == '0':
            return '(+all([[]]))'
        if i == '1':
            return '(+all([]))'
        else:
            return "'+" + "+".join(['str(' + digits[int(j)] + ')' for j in i]) + "+'"

    s = re.sub('\d+', repl, s)

    # sub back in quote
    s = s.replace(TMP, DICT['\''])

    # clear out leading/trailing empty strings
    s = s.replace("+''+", "+")
    if s[:3] == "''+":
        s = s[3:]
    if s[-3:] == "+''":
        s = s[:-3]

    #print(str(eval(s)))
    #print("\n")
    return ("eval(" + s + ")") if with_eval else s


def test(s, verbose=False, with_eval=False):
    print(s)
    s_encoded = encode(s)

    assert set(s_encoded) <= base, set(s)
    assert eval("str("+s_encoded+")") == s, eval("str("+s_encoded+")")

    if verbose:
        print(s_encoded)
    if with_eval:
        print(eval("eval(" + s_encoded + ")"))

    print("Encoding len: ", len(s_encoded), "\n\n")
    return s_encoded


test('print("Hello, world!")', True)
test("'hi'a", True)
test('(lambda x: x**2)(5+3)', with_eval=True)

test('''

def f(x):
    return x * 4
y = f(5)
print(y)

''')


#test('''(lambda __builtin__: (lambda __print, __y, d: [[__print(d.x<d.y<5) for d.y in [(4)]][0] for d.x in [(3)]][0])(__builtin__.__dict__['print'],(lambda f: (lambda x: x(x))(lambda y: f(lambda *args: y(y)(*args)))),type('StateDict',(),__builtin__.__dict__)()))(__import__('__builtin__'))''')