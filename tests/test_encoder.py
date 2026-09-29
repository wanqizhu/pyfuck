"""编码器单元测试（不依赖子进程）。

    python -m unittest tests.test_encoder -v
"""

from __future__ import annotations

import unittest

import pyfuck
from pyfuck import encoder as pe

# 字符串往返探针：控制字符、引号、反斜杠、数字、CJK、emoji 都要过
STRING_PROBES = [
    "",
    "a",
    "'",
    '"',
    "\\",
    "0123456789",
    "\n\r\t\x00\x1f",
    "()[]+travels'",
    "你好，世界🌍 — émoji",
    "".join(chr(i) for i in range(1, 128)),
    "eval('exec')",
    "print('Hello, world!')",
]

PROGRAMS = [
    'print("Hello, world!")',
    "for i in range(3):\n    print(i)\n",
    "x = 1\n",
]


class TestAlphabet(unittest.TestCase):
    def test_alphabet_size(self):
        self.assertEqual(len(pe.ALPHABET), 13)
        self.assertEqual("".join(sorted(pe.ALPHABET)), "'()+[]aelrstv")

    def test_base_char_map(self):
        # 这些原语是整条构造链的根基，一旦 Python 换 repr 就会在这里炸
        pe.selfcheck()


class TestNumbers(unittest.TestCase):
    def test_num(self):
        for i in range(10):
            with self.subTest(i=i):
                self.assertEqual(eval(pe.num(i)), i)
                self.assertLessEqual(set(pe.num(i)), pe.ALPHABET)

    def test_num_rejects_negative(self):
        with self.assertRaises(pe.EncodeError):
            pe.num(-1)

    def test_digits_expr(self):
        self.assertEqual(eval(pe.digits_expr(16)), "16")
        self.assertEqual(eval(pe.digits_expr(0)), "0")
        self.assertEqual(eval(pe.digits_expr(9876543210)), "9876543210")

    def test_int_expr(self):
        for i in (0, 1, 5, 9, 10, 16, 42, 1234):
            with self.subTest(i=i):
                self.assertEqual(eval(pe.int_expr(i)), i)
                self.assertLessEqual(set(pe.int_expr(i)), pe.ALPHABET)


class TestChars(unittest.TestCase):
    def test_char_expr_all_ascii(self):
        for code in range(1, 128):
            ch = chr(code)
            with self.subTest(ch=ch):
                expr = pe.char_expr(ch)
                self.assertLessEqual(set(expr), pe.ALPHABET)
                self.assertEqual(eval(expr), ch)

    def test_char_expr_unicode(self):
        for ch in "中文🌍Ω":
            with self.subTest(ch=ch):
                self.assertEqual(eval(pe.char_expr(ch)), ch)


class TestRoundTrip(unittest.TestCase):
    def test_probes(self):
        for text in STRING_PROBES:
            with self.subTest(text=text[:20]):
                expr = pe.encode_string(text)
                self.assertLessEqual(set(expr), pe.ALPHABET)
                self.assertEqual(eval(expr), text)

    def test_empty_gives_empty_literal(self):
        self.assertEqual(pe.encode_string(""), "''")


class TestProgram(unittest.TestCase):
    def test_charset_and_uniqueness(self):
        for src in PROGRAMS:
            with self.subTest(src=src[:20]):
                code = pe.encode_program(src)
                self.assertLessEqual(set(code), pe.ALPHABET)
                self.assertLessEqual(len(set(code)), 13)

    def test_wraps_exec(self):
        code = pe.encode_program("x = 1")
        self.assertTrue(code.startswith("eval("))
        compile(code, "<pyfuck>", "exec")

    def test_empty_source_rejected(self):
        for bad in ("", "   ", "\n\t "):
            with self.subTest(bad=bad), self.assertRaises(pe.EncodeError):
                pe.encode_program(bad)

    def test_non_str_rejected(self):
        with self.assertRaises(pe.EncodeError):
            pe.encode_program(None)  # type: ignore[arg-type]


class TestAutoPrint(unittest.TestCase):
    def test_needs_print(self):
        self.assertTrue(pe.needs_print("1 + 1"))
        self.assertTrue(pe.needs_print('"hi"'))
        self.assertTrue(pe.needs_print("[1, 2]"))
        self.assertFalse(pe.needs_print('print("hi")'))
        self.assertFalse(pe.needs_print("x = 1"))  # 语句
        self.assertFalse(pe.needs_print("if True:\n    pass"))  # 语句
        self.assertFalse(pe.needs_print("exit(0)"))

    def test_auto_print_wraps_expression(self):
        with_ap = pe.encode_program("1 + 1", auto_print=True)
        without_ap = pe.encode_program("1 + 1", auto_print=False)
        self.assertNotEqual(with_ap, without_ap)

    def test_auto_print_ignores_statements(self):
        self.assertEqual(
            pe.encode_program("x = 1", auto_print=True),
            pe.encode_program("x = 1", auto_print=False),
        )


class TestStats(unittest.TestCase):
    def test_encode_with_stats(self):
        result = pe.encode_with_stats('print("Hello, world!")')
        self.assertTrue(result.charset_ok)
        self.assertEqual(result.source_len, 22)
        self.assertEqual(result.length, len(result.code))
        self.assertGreater(result.ratio, 100)
        self.assertLessEqual(set(result.chars), pe.ALPHABET)
        self.assertGreaterEqual(result.elapsed, 0)

    def test_syntax_check_can_fail(self):
        # check_syntax 走的是 compile，正常源码不该失败
        result = pe.encode_with_stats("1 + 1", check_syntax=True)
        self.assertTrue(result.charset_ok)


class TestPackageSurface(unittest.TestCase):
    def test_public_api(self):
        for name in ("encode_program", "encode_string", "encode_with_stats", "selfcheck", "ALPHABET"):
            self.assertTrue(hasattr(pyfuck, name), name)

    def test_version(self):
        self.assertRegex(pyfuck.__version__, r"^\d+\.\d+\.\d+$")


if __name__ == "__main__":
    unittest.main(verbosity=2)
