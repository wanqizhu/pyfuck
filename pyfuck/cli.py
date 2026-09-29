"""命令行接口。

    python -m pyfuck -h
    python -m pyfuck legacy/pyfuck.py -o out.py --stats
    python -m pyfuck -c 'print("hi")' --run
    python -m pyfuck --server
"""

from __future__ import annotations

import argparse
import contextlib
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from . import __version__
from . import encoder as pe

EPILOG = """\
示例:
  python -m pyfuck hello.py                  # 编码整个文件到 stdout
  python -m pyfuck hello.py -o hello.fuck.py # 写到文件（内容只有 13 种字符）
  python -m pyfuck -c 'print("hi")' --run    # 编码片段并立刻跑一遍验证
  echo 'print(1)' | python -m pyfuck         # 从 stdin 读源码
  python -m pyfuck --server                  # 启动 Web UI
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m pyfuck",
        description="把 Python 源码编码成只使用 13 个字符的等价程序（可直接运行）",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("source", nargs="?", help="源码文件路径；省略时从 stdin 读取")
    parser.add_argument("-c", "--code", help="直接给出源码片段（不能与 source 同时使用）")
    parser.add_argument("-o", "--output", help="输出文件（默认写到 stdout）")
    parser.add_argument("--auto-print", action="store_true", help="源码若是单个表达式，自动包一层 print(...)")
    parser.add_argument("--stats", action="store_true", help="把体积/耗时统计打到 stderr")
    parser.add_argument("--no-check", action="store_true", help="跳过生成代码的 compile 语法自检")
    parser.add_argument("--run", action="store_true", help="编码后用子进程运行一遍，验证可执行")
    parser.add_argument("--server", action="store_true", help="启动 Web UI（而不是编码）")
    parser.add_argument("--host", default="127.0.0.1", help="Web UI 监听地址，默认 127.0.0.1")
    parser.add_argument("--port", type=int, default=5000, help="Web UI 端口，默认 5000")
    parser.add_argument("--version", action="version", version=f"pyfuck {__version__}")
    return parser


def read_source(args: argparse.Namespace) -> str:
    if args.code is not None:
        return args.code
    if args.source:
        return Path(args.source).read_text(encoding="utf-8")
    if sys.stdin.isatty():
        raise SystemExit("没有源码：请给出文件路径、使用 -c，或从 stdin 管道输入（-h 看示例）")
    return sys.stdin.read()


def _harden_stdio() -> None:
    """把 stdout/stderr 切到 UTF-8，避免中文提示在非 UTF-8 控制台下报错。

    Windows 上 stdout 被重定向/管道时编码跟随 ANSI 代码页（常见 cp1252）：
    stdout 里 print 中文会直接 UnicodeEncodeError，stderr 则会被 Python 默认的
    backslashreplace 转义成 \\uXXXX 乱码。而程序本体输出永远是那 13 个 ASCII
    字符，只有诊断信息含中文，所以统一改成 UTF-8 不影响任何合法输出。
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:  # 被替换成 StringIO 之类时跳过
            continue
        with contextlib.suppress(ValueError, OSError):  # pragma: no cover - 特殊流不支持重配置
            reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    _harden_stdio()
    args = build_parser().parse_args(argv)

    if args.server:
        from .web import run

        run(args.host, args.port)
        return 0

    if args.code is not None and args.source:
        raise SystemExit("-c 与源码文件路径不能同时使用")

    try:
        source = read_source(args)
    except OSError as exc:
        raise SystemExit(f"读取源码失败：{exc}") from exc

    try:
        result = pe.encode_with_stats(
            source, auto_print=args.auto_print, check_syntax=not args.no_check
        )
    except pe.EncodeError as exc:
        raise SystemExit(f"编码失败：{exc}") from exc

    if args.stats:
        print(
            f"源码 {result.source_len} 字符 -> 输出 {result.length} 字符 "
            f"({result.ratio:.0f}x，{result.char_count} 种字符，{result.elapsed * 1000:.1f} ms)",
            file=sys.stderr,
        )

    if args.output:
        Path(args.output).write_text(result.code + "\n", encoding="utf-8")
        print(f"已写入 {args.output}（{result.length} 字符，可直接 python 运行）", file=sys.stderr)
    else:
        print(result.code)

    if args.run:
        return _run_once(result.code)
    return 0


def _run_once(code: str) -> int:
    """把生成的代码落盘并运行，用来看效果（跑的是你自己的源码）。"""
    with tempfile.TemporaryDirectory(prefix="pyfuck_run_") as tmp:
        path = Path(tmp) / "encoded.py"
        path.write_text(code, encoding="utf-8")
        started = time.perf_counter()
        proc = subprocess.run([sys.executable, str(path)], check=False)
        print(
            f"[--run] 退出码 {proc.returncode}，运行耗时 {time.perf_counter() - started:.2f}s",
            file=sys.stderr,
        )
        return proc.returncode


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
