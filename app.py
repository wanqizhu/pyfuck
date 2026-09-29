"""Web 入口：``python app.py`` → http://127.0.0.1:5000

真正的应用在 :mod:`pyfuck.web`，这里保留根目录启动脚本是为了旧用法/习惯，
等价写法：``python -m pyfuck --server``。
"""

from __future__ import annotations

from pyfuck.web import run

if __name__ == "__main__":
    run()
