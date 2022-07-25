#/usr/bin/python3

def encode_digit(n: int) -> str:
    assert n >= 0, "n must be positive"
    if n == 0:
        return "((()=='')+(()==''))"
    elif n == 1:
        return "((()=='')+(()==()))"
    else:
        return "(" + "+".join(["(()==())"]*n) + ")"

def encode_string(s: str) -> str:
    return "+".join([f"'%c'%{encode_digit(ord(c))}" for c in s])

def encode_code(s: str) -> str:
    return f"exec({encode_string(s)})"
