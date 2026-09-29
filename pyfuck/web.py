"""Pyfuck Web：输入 Python 源码，输出只使用 13 个字符的等价混淆代码。

启动：
    python app.py            （根目录启动脚本）
    python -m pyfuck --server
"""

from __future__ import annotations

from flask import Flask, Response, render_template, request

from . import encoder as pe

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024  # 请求体上限，防手滑

# 源码长度上限：输出约为源码的 250~400 倍，2 万字符已经能产出 5MB+
MAX_SOURCE_CHARS = 20_000
# 超过这个长度的输出不在页面上整段预览（浏览器会卡），但仍可完整下载
MAX_PREVIEW_CHARS = 200_000
# 超过这个长度就不再做 compile 语法自检（只为省时间）
CHECK_SYNTAX_MAX = 2_000_000

SAMPLES: list[dict[str, str]] = [
    {"name": "Hello World", "code": 'print("Hello, world!")'},
    {
        "name": "FizzBuzz",
        "code": (
            "for i in range(1, 21):\n"
            "    if i % 15 == 0:\n"
            "        print('FizzBuzz')\n"
            "    elif i % 3 == 0:\n"
            "        print('Fizz')\n"
            "    elif i % 5 == 0:\n"
            "        print('Buzz')\n"
            "    else:\n"
            "        print(i)\n"
        ),
    },
    {
        "name": "递归 · 斐波那契",
        "code": (
            "def fib(n):\n"
            "    return n if n < 2 else fib(n - 1) + fib(n - 2)\n"
            "\n"
            "print([fib(i) for i in range(15)])\n"
        ),
    },
    {
        "name": "类与推导式",
        "code": (
            "class Point:\n"
            "    def __init__(self, x, y):\n"
            "        self.x, self.y = x, y\n"
            "\n"
            "    def __repr__(self):\n"
            "        return f'({self.x}, {self.y})'\n"
            "\n"
            "print([Point(i, i * i) for i in range(4)])\n"
        ),
    },
    {
        "name": "中文与 Emoji",
        "code": 'print("你好，世界 🌍", sum(range(101)))',
    },
    {
        "name": "标准库调用",
        "code": (
            "import json, math\n"
            "print(json.dumps({'sqrt': math.isqrt(2026)}, ensure_ascii=False))\n"
        ),
    },
]


@app.get("/")
def index():
    return render_template(
        "index.html",
        samples=SAMPLES,
        source='print("Hello, world!")',
        auto_print=True,
        result=None,
        error=None,
        alphabet="".join(sorted(pe.ALPHABET)),
        max_source=MAX_SOURCE_CHARS,
    )


@app.post("/")
def encode():
    source = request.form.get("source", "")
    auto_print = request.form.get("auto_print") == "on"

    result = None
    error = None
    try:
        if not source.strip():
            raise pe.EncodeError("源码不能为空")
        if len(source) > MAX_SOURCE_CHARS:
            raise pe.EncodeError(
                f"源码过长（{len(source)} 字符），上限 {MAX_SOURCE_CHARS} 字符。"
                "输出体积约为源码的 250~400 倍。"
            )
        # 输出体积约是源码的 250~400 倍，先估算一下决定是否做 compile 自检
        check_syntax = len(source) * 450 <= CHECK_SYNTAX_MAX
        stats = pe.encode_with_stats(source, auto_print=auto_print, check_syntax=check_syntax)
        code = stats.code
        result = {
            "length": len(code),
            "source_length": len(source),
            "char_count": len(set(code)),
            "chars": "".join(sorted(set(code))),
            "ratio": len(code) / len(source),
            "elapsed_ms": stats.elapsed * 1000,
            "charset_ok": set(code) <= pe.ALPHABET,
            "syntax_ok": True if check_syntax else None,
            "truncated": len(code) > MAX_PREVIEW_CHARS,
            "preview": code[:MAX_PREVIEW_CHARS],
        }
    except pe.EncodeError as exc:
        error = str(exc)
    except MemoryError:
        error = "内存不足：源码太长，输出的混淆代码过大。"
    except RecursionError:
        error = "表达式嵌套过深，无法编码当前源码。"
    except Exception as exc:  # pragma: no cover
        error = f"编码失败：{type(exc).__name__}: {exc}"

    return render_template(
        "index.html",
        samples=SAMPLES,
        source=source,
        auto_print=auto_print,
        result=result,
        error=error,
        alphabet="".join(sorted(pe.ALPHABET)),
        max_source=MAX_SOURCE_CHARS,
    )


@app.post("/download")
def download():
    """完整下载（不截断），走 HTTP 附件响应，浏览器不会离开当前页面。"""
    source = request.form.get("source", "")
    auto_print = request.form.get("auto_print") == "on"
    try:
        code = pe.encode_program(source, auto_print=auto_print)
    except pe.EncodeError as exc:
        return str(exc), 400
    return Response(
        code,
        mimetype="text/x-python",
        headers={
            "Content-Disposition": 'attachment; filename="pyfuck_output.py"',
            "Cache-Control": "no-store",
        },
    )


def run(host: str = "127.0.0.1", port: int = 5000, *, debug: bool = False) -> None:
    """启动开发服务器。"""
    pe.selfcheck()  # 启动前先确认原语在当前 Python 上成立
    print(f"Pyfuck Web: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)
