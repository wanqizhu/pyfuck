from pyfuck import encode_code, encode_string


def test(code: str):
    print(f"\n----- TEST ------")
    print(f"==> Original:          {code}")

    encoded_code = encode_code(code)
    print(f"==> Encoded:           {encoded_code}")

    encoded_string = encode_string(code)
    encoded_string_value = eval(encoded_string)
    print(f"==> Encoded to string: {encoded_string_value}")
    assert encoded_string_value == code, f"Code string didn't equal: {encoded_string_value} != {code}"

    alphabet = set("exc'=()%+")
    assert all([c in alphabet for c in set(encoded_code)]), "Used illegal chars in encoded coded"


test('\x00\x01\x02')
test('12')
test('print("Hello, world!")')
test("'hi'a")
test('(lambda x: x**2)(5+3)')

test('''

def f(x):
    return x * 4
y = f(5)
print(y)

''')

test("@")
