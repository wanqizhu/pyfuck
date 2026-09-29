"""端到端测试：真的把生成结果写盘、用子进程运行、比对输出。

    python -m unittest tests.test_end_to_end -v
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pyfuck
from pyfuck import encoder as pe

PYTHON = sys.executable or "python"
ROOT = Path(__file__).resolve().parent.parent

# 子进程一律跑在 UTF-8 模式下。
# GitHub 的 Windows runner 控制台是 cp1252，而用例里有 print 中文/emoji 的源码：
# 那时编码后的程序和原始源码会"一起"崩（纯 Python 也一样崩），属于控制台代码页问题，
# 不是编码器的问题。让两边都跑在 UTF-8 下，比较才有意义。
# PYTHONIOENCODING 显式覆盖，防止外部环境已设置成别的编码。
UTF8_ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}

# (名字, 源码)：期望输出由"原始源码自己跑一遍"给出，避免手写转义出错
CASES: list[tuple[str, str]] = [
    ("hello", 'print("Hello, world!")'),
    ("quotes", "print('it\\'s \"ok\"')"),
    ("digits", "print(0, 1, 10, 9876543210)"),
    ("unicode", 'print("你好，世界🌍")'),
    ("tabs", "print('a\\tb')"),
    ("backslash", "print(repr('\\\\'))"),
    (
        "fizzbuzz",
        "for i in range(1, 16):\n"
        "    if i % 15 == 0:\n"
        "        print('FizzBuzz')\n"
        "    elif i % 3 == 0:\n"
        "        print('Fizz')\n"
        "    elif i % 5 == 0:\n"
        "        print('Buzz')\n"
        "    else:\n"
        "        print(i)\n",
    ),
    (
        "def",
        "def fib(n):\n"
        "    a, b = 0, 1\n"
        "    for _ in range(n):\n"
        "        a, b = b, a + b\n"
        "    return a\n"
        "print([fib(i) for i in range(10)])\n",
    ),
    ("import", "import math\nprint(math.isqrt(2026))\n"),
    (
        "classes",
        "class A:\n"
        "    def __init__(self, v):\n"
        "        self.v = v\n"
        "    def __repr__(self):\n"
        "        return f'A({self.v})'\n"
        "print(A(3), {k: v for k, v in [('a', 1)]})\n",
    ),
]


def _run_file(path: Path, timeout: float = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=UTF8_ENV,
        timeout=timeout,
    )


class TestEncodedProgramsRun(unittest.TestCase):
    """编码后的程序必须与原始程序 stdout 完全一致。"""

    def test_matches_original(self):
        with tempfile.TemporaryDirectory(prefix="pyfuck_e2e_") as tmp:
            tmpdir = Path(tmp)
            for name, src in CASES:
                with self.subTest(case=name):
                    code = pe.encode_program(src)
                    self.assertLessEqual(set(code), pyfuck.ALPHABET)

                    encoded = tmpdir / f"{name}.py"
                    encoded.write_text(code, encoding="utf-8")
                    got = _run_file(encoded)
                    self.assertEqual(got.returncode, 0, got.stderr)

                    reference = tmpdir / f"{name}_ref.py"
                    reference.write_text(src, encoding="utf-8")
                    want = _run_file(reference, timeout=60)
                    self.assertEqual(want.returncode, 0, want.stderr)

                    self.assertEqual(got.stdout, want.stdout)

    def test_auto_print_semantics(self):
        cases = [
            ("1 + 1", True, "2\n"),
            ('"hi"', True, "hi\n"),
            ('print("hi")', True, "hi\n"),  # 不能多出一个 None
            ("x = 1 + 1", True, ""),
            ("1 + 1", False, ""),
        ]
        with tempfile.TemporaryDirectory(prefix="pyfuck_ap_") as tmp:
            tmpdir = Path(tmp)
            for i, (src, auto_print, expected) in enumerate(cases):
                with self.subTest(src=src, auto_print=auto_print):
                    code = pe.encode_program(src, auto_print=auto_print)
                    path = tmpdir / f"ap{i}.py"
                    path.write_text(code, encoding="utf-8")
                    got = _run_file(path)
                    self.assertEqual(got.returncode, 0, got.stderr)
                    self.assertEqual(got.stdout, expected)

    def test_large_source(self):
        """大源码：确认平衡括号拼接不会把编译器递归打穿。"""
        src = "".join(f"x{i} = {i}\n" for i in range(1500)) + "print(x1499)\n"
        code = pe.encode_program(src)
        compile(code, "<pyfuck>", "exec")
        with tempfile.TemporaryDirectory(prefix="pyfuck_big_") as tmp:
            path = Path(tmp) / "big.py"
            path.write_text(code, encoding="utf-8")
            got = _run_file(path, timeout=300)
        self.assertEqual(got.returncode, 0, got.stderr[-2000:])
        self.assertEqual(got.stdout.strip(), "1499")


class TestCli(unittest.TestCase):
    @staticmethod
    def _cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [PYTHON, "-m", "pyfuck", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            input=input_text,
            cwd=ROOT,
            env=UTF8_ENV,
            timeout=180,
        )

    def test_code_snippet_to_stdout(self):
        proc = self._cli("-c", "print('hi')")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        code = proc.stdout.strip()
        self.assertLessEqual(set(code), pyfuck.ALPHABET)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cli.py"
            path.write_text(code, encoding="utf-8")
            self.assertEqual(_run_file(path).stdout, "hi\n")

    def test_stdin(self):
        proc = self._cli(input_text="print(1 + 1)")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertLessEqual(set(proc.stdout.strip()), pyfuck.ALPHABET)

    def test_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.py"
            proc = self._cli("-c", "print(2)", "-o", str(out), "--stats")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("源码", proc.stderr)
            self.assertTrue(out.exists())
            self.assertEqual(_run_file(out).stdout, "2\n")

    def test_run_flag(self):
        proc = self._cli("-c", "print('ran')", "--run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ran", proc.stdout)
        self.assertIn("[--run]", proc.stderr)

    def test_conflicting_args(self):
        proc = self._cli("-c", "print(1)", "some_file.py")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("不能同时使用", proc.stderr)

    def test_empty_source(self):
        proc = self._cli("-c", "   ")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("编码失败", proc.stderr)

    def test_help_and_version(self):
        self.assertEqual(self._cli("-h").returncode, 0)
        version = self._cli("--version")
        self.assertEqual(version.returncode, 0)
        self.assertIn("pyfuck", version.stdout)

    def test_encode_legacy_script(self):
        """能编码仓库里那份 144 行的原始脚本（不带 --run）。"""
        proc = self._cli(str(ROOT / "legacy" / "pyfuck.py"), "--no-check")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertLessEqual(set(proc.stdout.strip()), pyfuck.ALPHABET)


class TestCliOnNonUtf8Console(unittest.TestCase):
    """回归：中文提示在非 UTF-8 控制台下不能把 CLI 打崩。

    GitHub 的 Windows runner 上 stdout 是 cp1252，之前 `-h` 会直接
    UnicodeEncodeError，stderr 的中文则被转义成 \\uXXXX 乱码。
    """

    @staticmethod
    def _cli(*args: str) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if k != "PYTHONUTF8"}
        env["PYTHONIOENCODING"] = "cp1252"  # 模拟 Windows 英文默认控制台
        return subprocess.run(
            [PYTHON, "-m", "pyfuck", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=ROOT,
            env=env,
            timeout=180,
        )

    def test_help(self):
        proc = self._cli("-h")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("把 Python 源码编码成", proc.stdout)
        self.assertIn("示例", proc.stdout)

    def test_stats_on_stderr(self):
        proc = self._cli("-c", "print(2)", "--stats")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("源码", proc.stderr)  # 不能被转义成 \u6e90\u7801
        self.assertLessEqual(set(proc.stdout.strip()), pyfuck.ALPHABET)  # 输出本体仍是纯 ASCII

    def test_error_message(self):
        proc = self._cli("-c", "   ")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("编码失败", proc.stderr)


class TestWeb(unittest.TestCase):
    """用 Flask 测试客户端跑，不起真实端口。"""

    @classmethod
    def setUpClass(cls):
        try:
            from pyfuck.web import app
        except ImportError as exc:  # pragma: no cover
            raise unittest.SkipTest(f"未安装 Flask：{exc}") from exc
        app.config.update(TESTING=True)
        cls.client = app.test_client()

    def test_index(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("Pyfuck", html)
        self.assertIn("开始混淆", html)

    def test_encode_post(self):
        resp = self.client.post("/", data={"source": 'print("hi")', "auto_print": "on"})
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("字符集校验", html)
        self.assertIn("通过", html)

    def test_empty_source_shows_error(self):
        resp = self.client.post("/", data={"source": "   "})
        self.assertIn("源码不能为空", resp.get_data(as_text=True))

    def test_download_is_attachment(self):
        resp = self.client.post("/download", data={"source": 'print("hi")'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("attachment", resp.headers["Content-Disposition"])
        code = resp.get_data(as_text=True)
        self.assertLessEqual(set(code), pyfuck.ALPHABET)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dl.py"
            path.write_text(code, encoding="utf-8")
            self.assertEqual(_run_file(path).stdout, "hi\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
