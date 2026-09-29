# Pyfuck -- Esoteric Python using only **[(+travels')]**.

How few distinct characters can we use to write and execute any python program?

We can at least do 13! **[(+travels')]**

My initial hope is to avoid all alphanumeric characters. Unfortunately, because python has strong-typing (as opposed to javascript), we cannot implicitly cast between e.g. integers and strings. This means that, as far as I could figure out, there's no way to call a function or get a string without using some alphanumeric character to start with.


Luckily, we can still avoid all numbers, and only use 7 letters to enable `eval` and `str`, which allows we'll construct everything else.

Inspired by [jsfuck](jsfuck.com).

*Note*: Evidently, this can be done in [7 characters in Python2](https://codegolf.stackexchange.com/a/110722). Ah well, this was tons of fun! :cry:



# 本仓库新增：编码器 + Web UI + CLI

> 原始单文件脚本保留在 `legacy/pyfuck.py`（未改动），下面是新增的部分。

## 目录结构

```
pyfuck/
├── app.py                  # Web 启动脚本：python app.py
├── pyproject.toml          # 打包元数据 + ruff 配置（可选 pip install -e .）
├── requirements.txt        # Flask>=3.0
├── .gitignore              # 缓存 / 构建产物 / 混淆产物
├── .gitattributes          # 仓库内统一 LF、二进制标记、混淆产物不 diff
├── .github/
│   └── workflows/ci.yml    # CI：测试矩阵 + ruff + 打包冒烟
├── pyfuck/                 # 核心包
│   ├── __init__.py         # 对外 API：encode_program / encode_string / ALPHABET ...
│   ├── __main__.py         # python -m pyfuck 入口
│   ├── encoder.py          # 编码器（四层构造 + 启动自检）
│   ├── cli.py              # 命令行
│   ├── web.py              # Flask 应用（/ 编码页，/download 下载）
│   └── templates/
│       └── index.html      # 前端页面（暗色，含 CSS/JS）
├── tests/                  # python -m unittest -v
│   ├── test_encoder.py     # 单元测试：原语 / 往返 / 字符集 / 边界
│   └── test_end_to_end.py  # 端到端：子进程真跑 + CLI + Web 测试客户端
└── legacy/
    └── pyfuck.py           # 最初的单文件实现（存档，仅支持表达式）
```

## 三种用法

```bash
pip install -r requirements.txt

# 1) Web UI
python app.py                            # 打开 http://127.0.0.1:5000
python -m pyfuck --server --port 8000     # 等价写法，可指定端口

# 2) 命令行
python -m pyfuck hello.py -o hello.fuck.py --stats   # 编码文件
python -m pyfuck -c "print('hi')" --run              # 编码片段并立刻运行验证
echo "print(1)" | python -m pyfuck                   # 从 stdin 读源码

# 3) 当库用
python -c "import pyfuck; print(pyfuck.encode_program('print(1)')[:40])"

# 测试
python -m unittest -v                    # 36 个测试，约 7 秒

# 代码检查（配置在 pyproject.toml，与 CI 完全一致）
ruff check .                             # pip install ruff
```

## CI

`.github/workflows/ci.yml` 三个 job，推送到任意分支或开 PR 就会跑：

| job | 内容 |
| --- | --- |
| `test` | 矩阵：ubuntu × Python 3.10/3.11/3.12/3.13，外加 windows × 3.13；跑 `python -m unittest -v`（含真跑子进程的端到端测试） |
| `lint` | `ruff check --output-format=github .`，问题直接标在 PR 的 diff 上 |
| `package` | `python -m build` → 装 wheel → 在临时目录自检（确认 templates 进了 wheel）+ 跑一次 `pyfuck` CLI，最后上传 dist |

> 本仓库 origin 指向上游 `wanqizhu/pyfuck`，fork 到自己账号推送后 CI 自动生效。

## 相比 `legacy/pyfuck.py` 的改进

| 问题 | 原实现 | `pyfuck/encoder.py` |
| --- | --- | --- |
| 只支持单个表达式 | `eval(<字符串>)` | `eval("exec")(<字符串>)`，支持 `def`/`for`/`import` 等任意语句 |
| 单个 `0`/`1` | 生成 `str + int` → TypeError | 数字统一走 `str(1+1+…)` 字符串拼接 |
| 依赖正则替换数字 | `re.sub('\d+')`，字符集易被破坏 | 全程字符串拼接，输出保证 ⊆ 13 字符 |
| 超长表达式 | 左深 `a+b+c+…`，编译器递归可能爆栈 | 项数 >256 时用平衡括号拼接（深度 log₂n） |
| 正确性 | 无校验 | import 时 `selfcheck()` 自检全部原语；`compile()` 语法自检 |

实测：1.3 万字符源码 → 367 万字符输出，可编译、可运行；膨胀率约 250~400×。

## 编码原理（四层）

1. **整数**：`all([])` 是 `True`、`all([[]])` 是 `False`，加 `+` 得到 `1`/`0`，相加得到任意整数
2. **单字符**：用整数给 `str(str)`、`str(eval)`、`str(str.count)`、`str(float(1))` 的结果取下标，
   得到 `c u n f o ' . h`；字母 `t r a v e l s` 本来就在字符集里 → 拼出 `chr`、`str`
3. **任意字符串**：`chr(N)` 拿到任意字符，用 `+` 拼起来
4. **任意程序**：把整份源码变成一个字符串，`eval("exec")(源码字符串)` 执行
   （`exec` 这个名字里的 `x` 不在字符集里，所以先用字符串拼出 `"exec"` 再 `eval` 成函数对象）



# Encoding Process

To evaluate any python expression, we can turn it into a string and call `eval()`. Because we can decompose the string arbitrarily (break up each character and rebuilding with `+`), our main idea is to use our small set of characters and map to an arbitrary character, which then enables us to execute arbitrarily complex python code.


First, we notice that `+True` converts the boolean into the integer 1, and `+False` gives 0. This allows us to build up the integers:

```python
digits =
{
    0: '+all([[]])',
    1:  '+all([])',
    2: 'all([])+all([])'  # 1 + 1
                          # and so forth
}
```

With integers, we can take advantage of string indexing to get individual characters. In particular, calling `str` on an object/function gives its definition/docstrings, from which we can pick out individual characters.

```python
# python 3; slightly different str(...) in python2
str(str)
"<class 'str'>"

str(eval)
'<built-in function eval>'
```

For example, `str(str)[1]` gives `c`. This gives us the following characters:

```python
{
    'c': 'str(str)[+all([])]',                                              # str(str)[1]
    'f': 'str(eval)[eval(str(' + digits[1] + ')+str(' + digits[0] + '))]',  # str(eval)[10]
    'n': 'str(eval)[' + digits[8] + ']',                                    # str(eval)[8]
    'o': 'str(eval)[eval(str(' + digits[1] + ')+str(' + digits[6] + '))]',  # str(eval)[16]
    'u': 'str(eval)[' + digits[2] + ']'.                                    # str(eval)[2]
}

```

where digits[i] is the string representation of the number i from above. Note how to get 10 or larger numbers, we use string concatenation on each digit, so we don't need a million copies of `'+all([])'` to form large numbers.

This allows us to build more complex characters, using additional docstrings:

```python
{
  # str(float(1))[1]
  # eval('str(' + 'f' + 'l' + 'o' + 'at(' + '1' + '))[' + '1' + ']')
  '.': "+".join(["eval('str('", DICT['f'], "'l'", DICT['o'],
                 "'at(" + digits[1] + "))[" + digits[1] + "]')"])

  # str(str.count)[4]
  'h': "+".join(["eval('str(str'", DICT['.'],
                 DICT['c'], DICT['o'], DICT['u'], DICT['n'], "'t)[" + digits[4] + "]')"])
}
```

We use `+` to build up the string we want, and then wraps it around in eval to get the desired character.


Now, we have the characters `chr` and access to any integer, so we can simply call `chr()` to get any ascii character! Bingo.

```python
>>> chr(119) + chr(111) + chr(119)
'wow'
```



Writing the actual encoding function turned out to be a pain. Quotation nesting / use of eval(...) / repeated substitution was really messy to encode. Alas, it seem to work now!


See [source code](legacy/pyfuck.py) for full details!



# Examples

## Encoding arbitrary characters

```python
'@' = chr(64)
    = eval('c'                + 'h'                                   + 'r(' + '64' + ')')
    = eval(str(str)[+all([])] + str(str.count)[4]                     + 'r(' + str(6) + str(4) + ')')
    = ...                     + eval('str(str' + '.' + 'count)[4]')   + 'r(' + str((1+1+1+1+1+1)+str((1+1+1+1)+')')
    
    = ...                     # substituting expression for '.', 'c', 'o', 'u', 'n'; substituing +all([]) for 1


    = eval(''+eval('str(str)[+all([])]')      # 'c'


                                              # 'h' = str(str.count)[4]
             +eval('str(str'                                              # str(str
                                                                          # '.' = str(float(1)[1])

                    +eval('str('                                                          # str(
                          +str(eval)[eval(str((+all([])))+str((+all([[]]))))]             # f
                          +'l'                                                            # l
                          +str(eval)[eval(str((+all([])))                                 # o
                                         +str((all([])+all([])+all([])
                                              +all([])+all([])+all([]))))]
                          +'at((+all([]))))[(+all([]))]')                                 # at(1)[1]

                    +str(str)[+all([])]                                   # c 
                                                                          # o = str(eval)[16]
                    +str(eval)[eval(str((+all([])))
                                    +str((all([])+all([])+all([])
                                         +all([])+all([])+all([]))))]
                                                 
                    +str(eval)[(all([])+all([]))]                         # u
                                                               
                    +str(eval)[(all([])+all([])+all([])+all([])           # n
                               +all([])+all([])+all([])+all([]))]
                                                                 
                    +'t)[(all([])+all([])+all([])+all([]))]')             # t)[4]

             +'r('                            # 'r(
              '
             +str((all([])+all([])+all([])    # '6'
                  +all([])+all([])+all([])))
                                              # '4'
             +str((all([])+all([])+all([])+all([])))
             +')'                             # ')'
          )

```


## Hello World

The following code will encode `print("Hello, world!")`:


```python
eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])))+')')+'r'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([
]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]')+'t('+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'
at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])))+str((all([])+all([])))+')')+'ell'+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([
])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+a
ll([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+'rl'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((+all([[]])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval
(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+')'

```

```python
# without linebreak
eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])))+')')+'r'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]')+'t('+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])))+str((all([])+all([])))+')')+'ell'+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([])))+')')+eval('str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]')+'rl'+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((+all([])))+str((+all([[]])))+str((+all([[]])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])))+')')+eval(''+eval('str(str)[+all([])]')+eval('str(str'+eval('str('+str(eval)[eval(str((+all([])))+str((+all([[]]))))]+'l'+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+'at((+all([]))))[(+all([]))]')+str(str)[+all([])]+str(eval)[eval(str((+all([])))+str((all([])+all([])+all([])+all([])+all([])+all([]))))]+str(eval)[(all([])+all([]))]+str(eval)[(all([])+all([])+all([])+all([])+all([])+all([])+all([])+all([]))]+'t)[(all([])+all([])+all([])+all([]))]')+'r('+str((all([])+all([])+all([])))+str((all([])+all([])+all([])+all([])))+')')+')'
```

6019 characters, but only 13 unique ones!

Test it yourself, and the expression above evaluates to`'print("Hello world!)'`! Add eval(...) around it to actually run the command.





# TODO

* Make compatible with python2
* Integrate with https://github.com/csvoss/onelinerizer to execute any python program
* Enable the use of 'exec' instead of 'eval'
* Shorter / more efficient encoding

* REMOVE THE NEED OF `'`  -- this is actually possible!
  - We can globally replace `'` with `str(str)[(all([])+all([])+all([])+all([])+all([])+all([])+all([]))] = str(str)[8]`, for example, and reduce our character set to 12 characters.
* Can we use even fewer characters? What's the limit?


