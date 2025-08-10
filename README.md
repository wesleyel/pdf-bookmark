# pdf-bookmark

为 PDF 添加目录书签的实用工具，支持命令行与简易 GUI。通过“手动粘贴目录文本 + 页码偏移”的方式生成 PDF 书签（大纲/Outline）。

- 运行环境：Python 3.9+
- 依赖：pypdf（写书签）
- 提供方式：CLI、Tk GUI、Python API

## 功能概览
- 手动粘贴目录文本（每行以书中页码结尾），自动解析标题、页码与层级（1..6）
- 支持页码偏移（实际页码 - 书籍页码），用于扫描件/前置页差异
- 支持行首星号标记：如 `*1.1 Title` 或 `* 1.1 Title`，星号将保留到最终标题
- 将条目以父子层级写入 PDF 书签
- 提供 CLI 与 GUI；亦可通过 Python API 使用

## 快速开始

### 安装与运行（uv 推荐）
本仓库使用 uv 管理与分发工具。

1) 一键安装命令行工具（推荐）：
```bash
uv tool install .
# 安装后可直接使用：
pdf-bookmark --help
pdf-bookmark-gui
```

2) 直接运行（无需安装为工具）：
```bash
# CLI
uv run python -m pdf_bookmark.cli --help

# GUI
uv run python -m pdf_bookmark.gui
```

3) 使用 pip 可编辑安装（备选）：
```bash
# 可编辑安装，导出命令 pdf-bookmark / pdf-bookmark-gui（不使用 uv tool 时）
pip install -e .

# 现在可直接使用：
pdf-bookmark --help
pdf-bookmark-gui
```

## 命令行使用（CLI）
已安装（或用 `uv run` 运行）后，基本命令如下：

```bash
pdf-bookmark <input.pdf> [-o OUT] [--toc-file TOC.txt] [--page-offset N] [--min-len N]
```

参数说明：
- input.pdf：输入 PDF 路径
- -o/--out：输出 PDF 路径；未指定时将使用“原文件名.bookmarked.pdf”
- --toc-file：目录文本文件（每行末尾为书中页码，前缀编号用于推断层级）
- --page-offset：页码偏移（实际页码 - 书籍页码）
- --min-len：最短行长度（默认 3），过短的行会被忽略

示例：
```bash
# 使用本地目录文本 + 页码偏移
pdf-bookmark input.pdf --toc-file toc.txt --page-offset 14

# 指定输出
pdf-bookmark input.pdf -o output.pdf

# 放宽行长度过滤（默认 3）
pdf-bookmark input.pdf --toc-file toc.txt --min-len 2
```

## 图形界面（GUI）
提供一个基于 Tk 的简易界面，便于在桌面环境下操作：
```bash
pdf-bookmark-gui
# 或
uv run python -m pdf_bookmark.gui
```
基本流程：
- 选择输入 PDF
- 可选：修改输出路径
- 在 “TOC text” 中粘贴目录文本；在 “Page Offset” 填写偏移（实际 - 书籍）
- 点击 “Parse TOC Text” 查看解析结果
- 点击 “Generate” 生成带书签的 PDF

提示：Linux 上若缺少 tkinter，可通过安装系统包启用（例如 Debian/Ubuntu：`sudo apt-get update && sudo apt-get install -y python3-tk`）。

## Python API
如需在你自己的 Python 程序中复用逻辑，可直接导入：

```python
from pdf_bookmark import parse_toc_lines, generate_bookmarks

toc = """
第1章 基础 1
1.1 Scala解释器 3
* 1.2 声明值和变量 4
""".strip()

headings = parse_toc_lines(toc, page_offset=14, min_len=1)
generate_bookmarks("input.pdf", "output.pdf", headings)
```

类型与数据结构（简述）：
- Heading：包含 `title: str`、`page: int`（1 基）、`level: int`（1..6）

## 目录文本格式（约定）
- 每一行以书籍页码结尾（纯数字），示例：`1.2 某小节 37`
- 行首可包含编号用于推断层级：
  - `第1章` => 视为顶层
  - `1`、`1.2`、`1.2.3` => 段数映射为层级（`1.2` 为 2 级）
- 行首可包含星号：`*1.1 标题` 或 `* 1.1 标题`；星号会被保留至最终书签标题
- `--page-offset` 为 正数 时，表示 PDF 实际页码 = 书籍页码 + 偏移（常见于前置页/扫描件）

## 限制与建议
- 目录文本须在行尾提供“书籍页码”；若缺失将被忽略
- 对于非常短的标题（如仅数字）建议提高 `--min-len` 过滤阈值
- 若行中含有非常规字符/排版，可在生成前手动调整文本

## 故障排查
- ModuleNotFoundError: pdf_bookmark
  - 建议使用 `uv tool install .` 安装工具，或 `pip install -e .`
- 缺少 tkinter（GUI 无法启动）
  - Linux 可安装 `python3-tk` 系统包；容器/最小系统常见
- 生成的 PDF 无书签
  - 目录文本行尾可能缺少页码；或被 `--min-len` 过滤

## 开发与测试
- 代码检查与测试：
```bash
uv tool install .  # 安装命令，便于本地手动验证
uv run pytest -q
# 可选：
uv run ruff check
uv run mypy pdf_bookmark
```

- 项目结构：
```
pdf_bookmark/
  core.py   # 目录解析与书签生成核心逻辑
  cli.py    # 命令行入口
  gui.py    # Tk GUI 入口
  tests/    # 单元测试（pytest）
```

## 许可证
本项目的许可证见仓库中的 LICENSE 文件。
