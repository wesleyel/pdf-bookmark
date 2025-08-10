# TocSmith

为 PDF 添加目录书签的实用工具，支持命令行与简易 GUI。通过“手动粘贴目录文本 + 页码偏移”的方式生成 PDF 书签（大纲/Outline）。

- 运行环境：Python 3.9+
- 依赖：pypdf（写书签）
- 提供方式：CLI、Tk GUI、Python API

## 功能概览
- 手动粘贴目录文本（每行以书中页码结尾），自动解析标题、页码与层级（1..6）
- 支持页码偏移（实际页码 - 书籍页码），用于扫描件/前置页差异
- 编号前缀会被保留到标题中：如 `第1章`、`1.1` 将出现在最终书签标题里
- 支持行首星号标记：允许输入 `*1.1 Title` 或 `* 1.1 Title`，输出统一为 `*1.1 Title`
- 将条目以父子层级写入 PDF 书签
- 提供 CLI 与 GUI；亦可通过 Python API 使用

## 快速开始

### 安装与运行（uv 推荐）
本仓库使用 uv 管理与分发工具。

1) 通过uv安装命令行工具（推荐）：
```bash
uv tool install tocsmith
# 安装后可直接使用：
tocsmith --help
tocsmith-gui
```

2) 使用 pip 安装（备选）：
```bash
pip install tocsmith

# 现在可直接使用：
tocsmith --help
tocsmith-gui
```

3) 本地开发
```bash
git clone https://github.com/wesleyel/pdf-bookmark.git
cd pdf-bookmark
uv sync

uv tool install . --reinstall

tocsmith --help
tocsmith-gui
```

## 命令行使用（CLI）

```bash
tocsmith --help
```

### 通过 TOML 批量执行（自定义格式）
支持通过 TOML 配置批量执行多个任务。相对路径均以配置文件所在目录为基准；还可以通过 `defaults.input_prefix` 与 `defaults.output_prefix` 设定输入/输出根目录。

示例 `config.toml`：

```toml
[defaults]
# global page offset
page_offset = 0
# global minimum length
min_len = 3

# input folder
input_prefix = "input"
# output folder
output_prefix = "output"
# output file name append
output_suffix = ".bookmarked.pdf"

[[tasks]]
# input file name. relative to input_prefix
input_file = "book1.pdf"
toc = """
第一章 绪论 1
1.1 引言 3
1.2 数学分析的基本概念 5
"""
page_offset = 10
min_len = 2
```

运行：

```bash
tocsmith --config config.toml
```

说明：
- `defaults` 中的 `page_offset`、`min_len` 可被每个任务覆盖。
- `input_prefix` 用于解析任务中的 `input_file`；`output_prefix` 为输出目录根。
- 输出文件名为 `{stem}{output_suffix}`，其中 `stem` 来源于 `input_file`。
- 任务可直接内联 `toc` 文本；也兼容 `toc_file` 指定外部文件。

## 图形界面（GUI）
提供一个基于 Tk 的简易界面，便于在桌面环境下操作：
```bash
tocsmith-gui
# 或
uv run python -m tocsmith.gui
```
基本流程：
- 选择输入 PDF
- 可选：修改输出路径
- 在 “TOC text” 中粘贴目录文本；在 “Page Offset” 填写偏移（实际 - 书籍）
- 点击 “Parse TOC Text” 查看解析结果
- 点击 “Generate” 生成带书签的 PDF

提示：Linux 上若缺少 tkinter，可通过安装系统包启用（例如 Debian/Ubuntu：`sudo apt-get update && sudo apt-get install -y python3-tk`）。

## 开发与测试

- 代码检查与测试：
```bash
uv tool install .  # 安装命令，便于本地手动验证
uv run pytest -q
# 可选：
uv run ruff check
uv run mypy tocsmith
```

- 项目结构：
```
tocsmith/
  core.py   # 目录解析与书签生成核心逻辑
  cli.py    # 命令行入口
  gui.py    # Tk GUI 入口
  tests/    # 单元测试（pytest）
```

## 许可证

MIT
