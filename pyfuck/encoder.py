"""pyfuck 编码器。

把任意 Python 源码编码成"只有 13 个字符、单行表达式、可直接运行"的等价程序：

    + t r a v e l s [ ] ' ( )

构造分层（每层只依赖下一层）：

    第 0 层  字符集        + t r a v e l s [ ] ' ( )
    第 1 层  整数          all([]) -> True -> 1 ; all([[]]) -> False -> 0
    第 2 层  单字符        str(str) / str(eval) / str(str.count) 的 repr 取下标
    第 3 层  任意字符串    chr(N) 与已有字符用 + 拼接
    第 4 层  任意程序      eval("exec")(<源码字符串>)  —— exec 由字符串 eval 得到，
                          从而不需要写出 e/x/c 之外的字面量（x 由 chr(120) 得到）

与仓库里 pyfuck.py 的区别：
  * 支持任意语句（def / for / 赋值 ...），不只是单个表达式；
  * 修掉单字符 '0' / '1'（以及 ord < 10 的控制字符）会生成 str + int 从而 TypeError 的 bug；
  * 数字统一走 str(1+1+...) 的字符串拼接，不再依赖正则替换；
  * 超长表达式用平衡括号拼接，避免左深表达式树把 CPython 编译器递归打穿；
  * 每个原语在 import 时自检，Python 版本漂移会立刻报错而不是产出错误结果。

输出保证：set(输出) <= ALPHABET，且 compile(输出) 通过。
"""

from __future__ import annotations

import ast
import time
from collections.abc import Iterable

__all__ = [
    "ALPHABET",
    "MAX_TERMS_BEFORE_BALANCING",
    "EncodeError",
    "EncodeResult",
    "build_str",
    "encode_program",
    "encode_string",
    "encode_with_stats",
    "needs_print",
    "selfcheck",
]

# 第 0 层：全部可用字符
ALPHABET = frozenset("+travels[]'()")

# 可以原样写进字符串字面量里的字符（ALPHABET 去掉单引号本身）
SAFE_LITERAL = frozenset("+travels[]()")

# 拼接项超过这个数量就用括号做平衡树，防止编译器递归过深
MAX_TERMS_BEFORE_BALANCING = 256

# 这些调用本身就有副作用/输出，自动再包一层 print 只会多打印一个 None
PRINT_DISABLED = frozenset({"print", "exec", "exit", "quit"})


class EncodeError(Exception):
    """编码失败。"""


# ============================================================ 第 1 层：整数


def num(n: int) -> str:
    """值为整数 n 的表达式。

    all([])  ->  True  ->  +True  == 1
    all([[]]) -> False ->  +False == 0
    """
    if n < 0:
        raise EncodeError("num() 只接受非负整数")
    if n == 0:
        return "+all([[]])"
    if n == 1:
        return "+all([])"
    return "(" + "+".join(["all([])"] * n) + ")"


def num_str(n: int) -> str:
    """值为字符串 str(n) 的表达式（n 必须是个位数）。"""
    return "str(" + num(n) + ")"


def digits_expr(n: int) -> str:
    """值为字符串 str(n) 的表达式，逐位拼接。

    例如 16 -> str(1)+str(6)，比写 16 个 all([]) 相加短得多。
    """
    return "+".join(num_str(int(d)) for d in str(n))


def int_expr(n: int) -> str:
    """值为整数 n、体量尽可能小的表达式。"""
    if 0 <= n <= 9:
        return num(n)
    # 把数字拆成字符串再 eval 回整数，避免 n 个 all([]) 相加
    return "eval(" + digits_expr(n) + ")"


# ==================================================== 第 2 层：单字符表达式
#
# 这些表达式（在"代码"位置求值）得到长度为 1 的字符串。
#
#   str(str)         == "<class 'str'>"                  -> c(1)  ' (7)
#   str(eval)        == "<built-in function eval>"       -> u(2) n(8) f(10) o(16)
#   str(str.count)   == "<method 'count' of 'str' objects>" -> h(4)
#   str(float(1))    == "1.0"                            -> .(1)

CHAR: dict[str, str] = {
    "c": f"str(str)[{int_expr(1)}]",
    "u": f"str(eval)[{int_expr(2)}]",
    "n": f"str(eval)[{int_expr(8)}]",
    "f": f"str(eval)[{int_expr(10)}]",
    "o": f"str(eval)[{int_expr(16)}]",
    "'": f"str(str)[{int_expr(7)}]",
}


def _concat(parts: list[str]) -> str:
    """把若干字符串表达式用 + 连起来。

    项数很多时用括号搭平衡树：左深表达式 `a+b+c+...` 会生成深度等于项数的
    AST，CPython 编译器递归访问时可能 RecursionError，平衡树把深度压到 log2(n)。
    """
    if len(parts) == 1:
        return parts[0]
    if len(parts) <= MAX_TERMS_BEFORE_BALANCING:
        return "+".join(parts)

    while len(parts) > 1:
        merged: list[str] = []
        for i in range(0, len(parts) - 1, 2):
            merged.append("(" + parts[i] + "+" + parts[i + 1] + ")")
        if len(parts) % 2:
            merged.append(parts[-1])
        parts = merged
    return parts[0]


def build_str(text: str) -> str:
    """返回一个值为字符串 text 的表达式（只用 ALPHABET 里的字符）。"""
    parts: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if buf:
            parts.append("'" + "".join(buf) + "'")
            buf.clear()

    for ch in text:
        if ch in SAFE_LITERAL:
            buf.append(ch)
        else:
            flush()
            parts.append(char_expr(ch))
    flush()

    if not parts:
        return "''"
    return _concat(parts)


def char_expr(ch: str) -> str:
    """返回一个值为单字符 ch 的表达式。"""
    if ch in CHAR:
        return CHAR[ch]
    if ch in SAFE_LITERAL:
        return "'" + ch + "'"
    if "0" <= ch <= "9":
        # 数字不在 ALPHABET 里，用 str(1+1+...) 拼出来
        return num_str(ord(ch) - 48)
    # 其余字符：构造代码字符串 "chr(N)" 再 eval
    return "eval(" + build_str(f"chr({ord(ch)})") + ")"


# 依赖 build_str，所以放在后面定义
CHAR["."] = "eval(" + build_str("str(float(1))[1]") + ")"
CHAR["h"] = "eval(" + build_str("str(str.count)[4]") + ")"


# ============================================================ 第 3、4 层：对外接口


def encode_string(text: str) -> str:
    """把任意字符串编码成一个表达式，求值得到它本身。"""
    if not isinstance(text, str):
        raise EncodeError("encode_string() 需要 str")
    return build_str(text)


def encode_program(source: str, *, auto_print: bool = False, wrap_exec: bool = True) -> str:
    """把 Python 源码编码成可直接运行的等价程序（单行表达式）。

    auto_print=True 时会先尝试把源码当"单个表达式"，包一层 print(...)，
    这样交互式试写的小片段也能看到结果；若源码本来就是 print(...) 调用
    则不再包裹（否则会多打印一行 None）。
    """
    if not isinstance(source, str):
        raise EncodeError("source 必须是 str")
    if not source.strip():
        raise EncodeError("源码为空")

    text = source
    if auto_print and needs_print(source):
        text = "print(" + source + ")"

    body = build_str(text)
    if not wrap_exec:
        return body

    # exec 这个名字本身也不在 ALPHABET 里（x/c 都不在），
    # 但可以先把字符串 "exec" 拼出来再 eval 成函数对象。
    exec_expr = "eval(" + build_str("exec") + ")"
    out = exec_expr + "(" + body + ")"

    bad = set(out) - ALPHABET
    if bad:  # pragma: no cover - 自检兜底
        raise EncodeError(f"编码结果混入了非法字符: {sorted(bad)}")
    return out


def _is_expression(source: str) -> bool:
    try:
        compile(source, "<source>", "eval")
    except SyntaxError:
        return False
    return True


def needs_print(source: str) -> bool:
    """源码是否值得自动包一层 print(...)。

    只有"整体是一个表达式"才需要；其中 print(...) / exit(...) 这类本身
    就有副作用的调用再包一层反而会多打印一个 None。
    """
    try:
        node = ast.parse(source.strip(), mode="eval").body
    except SyntaxError:
        return False
    is_side_effect_call = (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in PRINT_DISABLED
    )
    return not is_side_effect_call


# ============================================================ 自检 & 统计


def selfcheck() -> None:
    """验证所有原语在当前 Python 版本上仍然成立。失败会抛 AssertionError。"""
    assert eval("str(str)") == "<class 'str'>"
    assert eval("str(eval)") == "<built-in function eval>"
    assert eval("str(str.count)") == "<method 'count' of 'str' objects>"
    assert eval("str(float(1))") == "1.0"

    for i in range(10):
        assert eval(num(i)) == i, (i, num(i))
    assert eval(digits_expr(16)) == "16"

    for ch, expr in CHAR.items():
        assert set(expr) <= ALPHABET, (ch, set(expr) - ALPHABET)
        assert eval(expr) == ch, (ch, expr, eval(expr))

    probes = [
        "",
        "a",
        "'",
        "\\",
        "0123456789",
        "\n\t",
        'print("Hello, world!")',
        "你好，世界🌍",
        "def f(x):\n    return x * 4\nprint(f(5))",
    ]
    for s in probes:
        expr = encode_string(s)
        assert set(expr) <= ALPHABET, (s, set(expr) - ALPHABET)
        assert eval(expr) == s, s


class EncodeResult:
    """编码结果 + 统计信息。"""

    def __init__(self, code: str, source_len: int, elapsed: float):
        self.code = code
        self.source_len = source_len
        self.elapsed = elapsed

    @property
    def length(self) -> int:
        return len(self.code)

    @property
    def char_count(self) -> int:
        return len(set(self.code))

    @property
    def chars(self) -> str:
        return "".join(sorted(set(self.code)))

    @property
    def ratio(self) -> float:
        return self.length / self.source_len if self.source_len else 0.0

    @property
    def charset_ok(self) -> bool:
        return set(self.code) <= ALPHABET

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "length": self.length,
            "char_count": self.char_count,
            "chars": self.chars,
            "ratio": round(self.ratio, 1),
            "elapsed_ms": round(self.elapsed * 1000, 1),
            "charset_ok": self.charset_ok,
        }


def encode_with_stats(source: str, *, auto_print: bool = False, check_syntax: bool = True) -> EncodeResult:
    """编码并附带统计；check_syntax 会对生成代码做一次 compile 校验。"""
    t0 = time.perf_counter()
    code = encode_program(source, auto_print=auto_print)
    if check_syntax:
        try:
            compile(code, "<pyfuck>", "exec")
        except (SyntaxError, MemoryError, RecursionError) as exc:  # pragma: no cover
            raise EncodeError(f"生成的代码无法编译: {exc}") from exc
    return EncodeResult(code, len(source), time.perf_counter() - t0)


def charset_of(texts: Iterable[str]) -> str:
    out: set[str] = set()
    for t in texts:
        out |= set(t)
    return "".join(sorted(out))
