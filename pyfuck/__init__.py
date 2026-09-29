"""Pyfuck —— 只用 13 个字符写任意 Python 程序。

字符集：``+ t r a v e l s [ ] ' ( )``

对外只暴露四件事：把字符串/源码编码成 13 字符表达式，外加自检与统计。

    >>> import pyfuck
    >>> code = pyfuck.encode_program('print("hi")')
    >>> set(code) <= pyfuck.ALPHABET
    True
"""

from __future__ import annotations

from .encoder import (
    ALPHABET,
    EncodeError,
    EncodeResult,
    build_str,
    encode_program,
    encode_string,
    encode_with_stats,
    needs_print,
    selfcheck,
)

__version__ = "1.0.0"

__all__ = [
    "ALPHABET",
    "EncodeError",
    "EncodeResult",
    "build_str",
    "encode_program",
    "encode_string",
    "encode_with_stats",
    "needs_print",
    "selfcheck",
    "__version__",
]
