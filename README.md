# pdf-bookmark

为 PDF 自动生成目录书签的实用工具，支持命令行与简易 GUI。通过基于字体大小与页面位置的启发式规则识别标题，写入 PDF 书签（大纲/Outline）。

- 运行环境：Python 3.9+
- 依赖：pdfminer.six（解析文本）、pypdf（写书签）
- 提供方式：CLI、Tk GUI、Python API

## 功能概览
- 自动分析 PDF 文本框，估计标题级别（1..6）
- 基于平均字符大小的分位数阈值与页面顶部区域加权判断层级
- 将识别的标题以嵌套书签形式写入输出 PDF
- 命令行与 GUI 双入口；也可作为库在 Python 中调用

## 快速开始

### 使用 uv（推荐）
本仓库使用 uv 管理依赖与锁文件。

1) 安装依赖（含开发工具可选）：
```bash
uv sync
# 如需测试/代码质量工具：
uv sync --extra dev
```

2) 直接运行（无需安装包）：
```bash
# CLI（推荐）
uv run python -m pdf_bookmark.cli --help

# GUI
uv run python -m pdf_bookmark.gui
```

3) 安装为可执行命令（可选）：
```bash
# 可编辑安装，导出命令 pdf-bookmark / pdf-bookmark-gui
uv run python -m pip install -e .

# 现在可直接使用：
pdf-bookmark --help
pdf-bookmark-gui
```

### 使用 pip（备选）
```bash
python -m venv .venv && source .venv/bin/activate  # Windows 请使用 .venv\Scripts\activate
pip install -e .[dev]  # 若不需要开发工具，可去掉 [dev]
python -m pdf_bookmark.cli --help
```

## 命令行使用（CLI）
已安装或用 `uv run` 执行时，命令如下：

```bash
pdf-bookmark <input.pdf> [-o OUT] [--min-len N]
```

参数说明：
- input.pdf：输入 PDF 路径
- -o/--out：输出 PDF 路径；未指定时将使用“原文件名.bookmarked.pdf”
- --min-len：最小标题文本长度（默认 3），过短的行会被忽略

示例：
```bash
# 简单用法，输出为 input.bookmarked.pdf
pdf-bookmark input.pdf

# 指定输出
pdf-bookmark input.pdf -o output.pdf

# 放宽标题长度过滤
pdf-bookmark input.pdf --min-len 2
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
- 点击 Analyze 查看识别到的标题（页码与层级）
- 点击 Generate 生成带书签的 PDF

提示：Linux 上若缺少 tkinter，可通过安装系统包启用（例如 Debian/Ubuntu：`sudo apt-get update && sudo apt-get install -y python3-tk`）。

## Python API
如需在你自己的 Python 程序中复用逻辑，可直接导入：

```python
from pdf_bookmark import analyze_pdf_headings, generate_bookmarks

# 1) 分析标题
headings = analyze_pdf_headings("input.pdf", min_len=3)
# 返回类似：[Heading(title="Intro", page=1, level=1), ...]

# 2) 生成书签
generate_bookmarks("input.pdf", "output.pdf", headings)
```

类型与数据结构（简述）：
- Heading：包含 `title: str`、`page: int`（1 基）、`level: int`（1..6）

## 工作原理（简述）
- 使用 pdfminer.six 遍历页面的文本框，收集每个文本框内字符的字体大小，计算平均值作为该文本行的“字号”参考
- 统计全局字号分布的分位数（默认使用约 70% 与 85%），将候选文本行划分为不同层级
- 对接近页面顶部的行给予层级“提升”，更可能被视作高层级标题
- 最终按页码与层级排序，使用 pypdf 以父子嵌套方式写入书签

注意：该方法是启发式的，针对“版式整齐、标题字号显著”的文档效果更佳；对扫描件或无可解析文本的 PDF 无能为力。

## 限制与建议
- 扫描版/图片版 PDF 不适用（无法解析文本）
- 极端复杂的版式/多栏排版可能降低识别效果
- 分位数阈值与“顶部加权”可能需要根据文档特性调整（当前为固定策略）
- 对于非常短的标题（如“1.”）建议提高 `--min-len` 过滤阈值或在生成后手动调整

## 故障排查
- ModuleNotFoundError: pdf_bookmark
  - 确认在项目根目录运行，或先 `uv sync`/`pip install -e .`
- 缺少 tkinter（GUI 无法启动）
  - Linux 可安装 `python3-tk` 系统包；容器/最小系统常见
- 生成的 PDF 无书签
  - 可能未识别到标题：尝试降低 `--min-len`；或该 PDF 主要为图片/无法解析文本

## 开发与测试
- 代码检查与测试：
```bash
uv sync --extra dev
uv run pytest -q
# 可选：
uv run ruff check
uv run mypy pdf_bookmark
```

- 项目结构：
```
pdf_bookmark/
  core.py   # 标题分析与书签生成核心逻辑
  cli.py    # 命令行入口
  gui.py    # Tk GUI 入口
  tests/    # 单元测试（pytest）
```

## 许可证
本项目的许可证见仓库中的 LICENSE 文件。
