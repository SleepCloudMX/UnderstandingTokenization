# PR-exp3 · Multi-Language Token Counter

批量统计多语言 / 多格式测试文本的**字符数**与 **token 数**，并导出 JSON、CSV、Markdown 表格和学术图表。

---

## 目录结构

```
PR-exp3/
├── data/                          # 测试数据（按任务类型/子类别/样例组织）
│   ├── lang/
│   │   ├── en_main/               # 英文作为主语言
│   │   │   ├── 001.json           # 打招呼句（5 种语言）
│   │   │   ├── 002.json           # 科技段落（3 种语言）
│   │   │   └── 003.json           # Transformer 论文摘要（9 种语言）
│   │   └── zh_main/               # 中文作为主语言
│   │       └── 001.json
│   ├── code/
│   │   └── python_whitespace/
│   │       └── 001.json           # 缩进风格对比（含空字符串边界）
│   └── emoji/
│       └── mixed/
│           └── 001.json           # emoji + 生僻字 + ZWJ 序列
├── src/
│   ├── schema.py                  # 数据模型（dataclass）+ 校验
│   ├── loader.py                  # 目录扫描 + JSON 加载（支持 subpath 过滤）
│   ├── tokenizer.py               # Tokenizer 适配层（BaseTokenizer + tiktoken）
│   ├── metrics.py                 # 指标计算（char / token / ratio）
│   ├── exporter.py                # 导出 JSON / CSV / Markdown
│   └── plotter.py                 # 学术图表（分组柱 + 双纵轴折线）
├── scripts/
│   └── lang.bat                   # 批量运行 lang/ 下所有子任务
├── tests/
│   └── test_metrics.py            # 单元测试（边界情况）
├── main.py                        # CLI 入口
├── requirements.txt
└── README.md
```

---

## 数据组织方式

```
data/
  <task_type>/           ← 第一层：任务类型（lang / code / emoji / …）
    <subgroup>/          ← 第二层：子类别（en_main / zh_main / python_whitespace / …）
      001.json           ← 单个样例（含多个 variants）
      002.json
```

每个 JSON 文件的最小结构：

```json
{
  "case_id": "lang_en_main_001",
  "task_type": "lang",
  "subgroup": "en_main",
  "description": "…",
  "tags": ["greeting", "baseline"],
  "variants": [
    { "variant_id": "en", "language": "en", "text": "Hello, world!" },
    { "variant_id": "zh", "language": "zh", "text": "你好，世界！" }
  ]
}
```

> `task_type` / `subgroup` 在 JSON 内**显式冗余存储**，避免单纯依赖路径推断，文件移动后仍可追溯。

---

## 统计口径

| 指标 | 定义 |
|---|---|
| `char_count` | `len(text)`，空格 / 换行 / tab 全部计入 |
| `token_count` | tokenizer 编码结果长度 |
| `char_per_token` | `char_count / token_count`，`token_count=0` 时为 `null` |
| `token_per_char` | `token_count / char_count`，`char_count=0` 时为 `null` |

---

## 环境配置

```bash
# 使用项目指定的 conda 环境（已含 tiktoken）
conda activate ai

# 或手动安装依赖
pip install -r requirements.txt
```

---

## 运行方式

### 1. 扫描全部数据

```bash
python main.py
# 输出到 output/
```

### 2. 只运行一个子任务（推荐）

```bash
python main.py --subpath lang/en_main
# 输出自动镜像到 output/lang/en_main/
```

### 3. 批量运行 lang/ 下所有子任务

```bat
scripts\lang.bat
# 或指定模型
scripts\lang.bat gpt-4o-mini
```

### 4. 完整参数说明

```
--data-dir      数据根目录（默认 data）
--output-dir    输出根目录（默认 output）
--subpath       子路径过滤，如 lang/en_main（输出自动镜像）
--tokenizer     tokenizer 名称（默认 tiktoken）
--model         tiktoken 模型名（默认 gpt-4o）
--output-prefix 输出文件名前缀（默认 results）
--no-plot       跳过图表生成
--warn-errors   将跳过警告打印到 stderr
```

---

## 输出文件

每次运行会在对应输出目录下生成：

| 文件 | 说明 |
|---|---|
| `results.json` | 完整统计结果（结构化，null 保留） |
| `results.csv` | 表格结果（utf-8-sig，Excel 可直接打开） |
| `results.md` | Markdown 表格（GitHub 友好） |
| `results.png` | 学术图表（分组柱 + 双纵轴折线，按 token 升序） |

输出路径镜像示例：

```
data/lang/en_main/001.json  →  output/lang/en_main/results.{json,csv,md,png}
data/lang/zh_main/001.json  →  output/lang/zh_main/results.{json,csv,md,png}
```

---

## 运行单元测试

```bash
python -m pytest tests/ -v
```

---

## 扩展方式

### 新增 tokenizer

在 `src/tokenizer.py` 中继承 `BaseTokenizer` 并注册到 `_REGISTRY`：

```python
class MyTokenizer(BaseTokenizer):
    name = "my_tok"

    def encode(self, text: str) -> list[int]:
        ...

_REGISTRY["my_tok"] = MyTokenizer
```

之后 `--tokenizer my_tok` 即可使用，无需修改其他文件。

### 新增任务类型

直接在 `data/` 下按规范创建目录和 JSON 文件，无需修改代码。

### 新增指标

修改 `src/metrics.py` 中的 `MetricRow` dataclass 和 `_compute_metrics()` 函数，
`exporter.py` 通过 `dataclasses.asdict()` 会自动把新字段写入 CSV。

---

## 设计说明

- **en_main / zh_main 分离**：未来可对比"以不同语言为主语言"时 tokenizer 的偏差。
- **JSON 内冗余 metadata**：`task_type` / `subgroup` 在 JSON 内显式存储，校验时可比对路径一致性。
- **subpath 镜像输出**：`--subpath lang/en_main` 自动把结果写入 `output/lang/en_main/`，目录结构与数据完全对应，便于批量比较。
- **除零安全**：`token_count=0` 或 `char_count=0` 时对应比率返回 `null`，不抛异常。
