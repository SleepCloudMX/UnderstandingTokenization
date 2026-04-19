# Understanding Tokenization in LLMs

批量统计多语言 / 多格式测试文本的**字符数**与 **Token 数**，生成结构化报表与可视化输出。

**推荐**：直接看[报告](docs\报告.html)中的图表与讨论分析即可。如果需要上手跑测试，可以继续阅读。

**参考工具**：[tiktokenizer](https://tiktokenizer.vercel.app/)、[Google AI Studio](https://aistudio.google.com/prompts/new_chat)。

---

### Demo

<span title="tokens: 1805" style="background:#a5f3fc;padding:1px 2px;border-radius:2px">【</span><span title="tokens: 35736, 121" style="background:#d9f99d;padding:1px 2px;border-radius:2px">鸽</span><span title="tokens: 7407" style="background:#fbcfe8;padding:1px 2px;border-radius:2px">子</span><span title="tokens: 3798, 242" style="background:#c7d2fe;padding:1px 2px;border-radius:2px">衔</span><span title="tokens: 154236" style="background:#fde68a;padding:1px 2px;border-radius:2px">枝</span><span title="tokens: 10708" style="background:#99f6e4;padding:1px 2px;border-radius:2px">之</span><span title="tokens: 2810" style="background:#fca5a5;padding:1px 2px;border-radius:2px">年</span><span title="tokens: 37157" style="background:#ddd6fe;padding:1px 2px;border-radius:2px">】<br></span><span title="tokens: 867" style="background:#bae6fd;padding:1px 2px;border-radius:2px">天</span><span title="tokens: 4286" style="background:#a7f3d0;padding:1px 2px;border-radius:2px">上</span><span title="tokens: 30360" style="background:#fcd34d;padding:1px 2px;border-radius:2px">永</span><span title="tokens: 78419" style="background:#f9a8d4;padding:1px 2px;border-radius:2px">恒</span><span title="tokens: 1616" style="background:#86efac;padding:1px 2px;border-radius:2px">的</span><span title="tokens: 15881" style="background:#93c5fd;padding:1px 2px;border-radius:2px">王</span><span title="tokens: 34158" style="background:#fecaca;padding:1px 2px;border-radius:2px">座</span><span title="tokens: 6946" style="background:#bfdbfe;padding:1px 2px;border-radius:2px">到</span><span title="tokens: 6727" style="background:#bbf7d0;padding:1px 2px;border-radius:2px">来</span><span title="tokens: 979" style="background:#fef08a;padding:1px 2px;border-radius:2px">，</span><span title="tokens: 28428" style="background:#e9d5ff;padding:1px 2px;border-radius:2px">世界</span><span title="tokens: 6209" style="background:#fed7aa;padding:1px 2px;border-radius:2px">为</span><span title="tokens: 10708" style="background:#a5f3fc;padding:1px 2px;border-radius:2px">之</span><span title="tokens: 6983, 243" style="background:#d9f99d;padding:1px 2px;border-radius:2px">焕</span><span title="tokens: 16125" style="background:#fbcfe8;padding:1px 2px;border-radius:2px">然</span><span title="tokens: 2432" style="background:#c7d2fe;padding:1px 2px;border-radius:2px">一</span><span title="tokens: 3711" style="background:#fde68a;padding:1px 2px;border-radius:2px">新</span><span title="tokens: 3414" style="background:#99f6e4;padding:1px 2px;border-radius:2px">。<br></span><span title="tokens: 119014" style="background:#fca5a5;padding:1px 2px;border-radius:2px">然后</span><span title="tokens: 7910" style="background:#ddd6fe;padding:1px 2px;border-radius:2px">真</span><span title="tokens: 15881" style="background:#bae6fd;padding:1px 2px;border-radius:2px">王</span><span title="tokens: 979" style="background:#a7f3d0;padding:1px 2px;border-radius:2px">，</span><span title="tokens: 14085" style="background:#fcd34d;padding:1px 2px;border-radius:2px">原</span><span title="tokens: 26719" style="background:#f9a8d4;padding:1px 2px;border-radius:2px">初</span><span title="tokens: 1616" style="background:#86efac;padding:1px 2px;border-radius:2px">的</span><span title="tokens: 18818" style="background:#93c5fd;padding:1px 2px;border-radius:2px">那</span><span title="tokens: 2432" style="background:#fecaca;padding:1px 2px;border-radius:2px">一</span><span title="tokens: 9838" style="background:#bfdbfe;padding:1px 2px;border-radius:2px">位</span><span title="tokens: 40914" style="background:#bbf7d0;padding:1px 2px;border-radius:2px">开始</span><span title="tokens: 5884" style="background:#fef08a;padding:1px 2px;border-radius:2px">和</span><span title="tokens: 67803" style="background:#e9d5ff;padding:1px 2px;border-radius:2px">旧</span><span title="tokens: 28428" style="background:#fed7aa;padding:1px 2px;border-radius:2px">世界</span><span title="tokens: 1616" style="background:#a5f3fc;padding:1px 2px;border-radius:2px">的</span><span title="tokens: 126207" style="background:#d9f99d;padding:1px 2px;border-radius:2px">主人</span><span title="tokens: 13932" style="background:#fbcfe8;padding:1px 2px;border-radius:2px">们</span><span title="tokens: 979" style="background:#c7d2fe;padding:1px 2px;border-radius:2px">，</span><span title="tokens: 28980" style="background:#fde68a;padding:1px 2px;border-radius:2px">七</span><span title="tokens: 9838" style="background:#99f6e4;padding:1px 2px;border-radius:2px">位</span><span title="tokens: 54436" style="background:#fca5a5;padding:1px 2px;border-radius:2px">恐</span><span title="tokens: 133986" style="background:#ddd6fe;padding:1px 2px;border-radius:2px">怖</span><span title="tokens: 1640" style="background:#bae6fd;padding:1px 2px;border-radius:2px">大</span><span title="tokens: 15881" style="background:#a7f3d0;padding:1px 2px;border-radius:2px">王</span><span title="tokens: 3044" style="background:#fcd34d;padding:1px 2px;border-radius:2px">开</span><span title="tokens: 19366" style="background:#f9a8d4;padding:1px 2px;border-radius:2px">战</span><span title="tokens: 3414" style="background:#86efac;padding:1px 2px;border-radius:2px">。<br></span><span title="tokens: 18818" style="background:#93c5fd;padding:1px 2px;border-radius:2px">那</span><span title="tokens: 54436" style="background:#fecaca;padding:1px 2px;border-radius:2px">恐</span><span title="tokens: 133986" style="background:#bfdbfe;padding:1px 2px;border-radius:2px">怖</span><span title="tokens: 134637" style="background:#bbf7d0;padding:1px 2px;border-radius:2px">的大</span><span title="tokens: 15881" style="background:#fef08a;padding:1px 2px;border-radius:2px">王</span><span title="tokens: 13932" style="background:#e9d5ff;padding:1px 2px;border-radius:2px">们</span><span title="tokens: 3221" style="background:#fed7aa;padding:1px 2px;border-radius:2px">是</span><span title="tokens: 16271" style="background:#a5f3fc;padding:1px 2px;border-radius:2px">龙</span><span title="tokens: 3414" style="background:#d9f99d;padding:1px 2px;border-radius:2px">。<br></span><span title="tokens: 14085" style="background:#fbcfe8;padding:1px 2px;border-radius:2px">原</span><span title="tokens: 26719" style="background:#c7d2fe;padding:1px 2px;border-radius:2px">初</span><span title="tokens: 1616" style="background:#fde68a;padding:1px 2px;border-radius:2px">的</span><span title="tokens: 18818" style="background:#99f6e4;padding:1px 2px;border-radius:2px">那</span><span title="tokens: 2432" style="background:#fca5a5;padding:1px 2px;border-radius:2px">一</span><span title="tokens: 9838" style="background:#ddd6fe;padding:1px 2px;border-radius:2px">位</span><span title="tokens: 23985" style="background:#bae6fd;padding:1px 2px;border-radius:2px">造</span><span title="tokens: 155198" style="background:#a7f3d0;padding:1px 2px;border-radius:2px">出了</span><span title="tokens: 39766" style="background:#fcd34d;padding:1px 2px;border-radius:2px">自己</span><span title="tokens: 2233" style="background:#f9a8d4;padding:1px 2px;border-radius:2px">发</span><span title="tokens: 17374" style="background:#86efac;padding:1px 2px;border-radius:2px">着</span><span title="tokens: 20244" style="background:#93c5fd;padding:1px 2px;border-radius:2px">光</span><span title="tokens: 1616" style="background:#fecaca;padding:1px 2px;border-radius:2px">的</span><span title="tokens: 5235" style="background:#bfdbfe;padding:1px 2px;border-radius:2px">影</span><span title="tokens: 7407" style="background:#bbf7d0;padding:1px 2px;border-radius:2px">子</span><span title="tokens: 3414" style="background:#fef08a;padding:1px 2px;border-radius:2px">。<br></span><span title="tokens: 15479" style="background:#e9d5ff;padding:1px 2px;border-radius:2px">而</span><span title="tokens: 5235" style="background:#fed7aa;padding:1px 2px;border-radius:2px">影</span><span title="tokens: 185317" style="background:#a5f3fc;padding:1px 2px;border-radius:2px">子的</span><span title="tokens: 80012" style="background:#d9f99d;padding:1px 2px;border-radius:2px">数量</span><span title="tokens: 3221" style="background:#fbcfe8;padding:1px 2px;border-radius:2px">是</span><span title="tokens: 11455" style="background:#c7d2fe;padding:1px 2px;border-radius:2px">四</span><span title="tokens: 1497" style="background:#fde68a;padding:1px 2px;border-radius:2px">。</span>

> **注**：若使用 .md 或 .html 打开，**鼠标悬浮在字符上会显示对应的 token**（一个字符可能会对应多个 tokens，例如 “鸽”）。

<img src="docs/image/1.2-zh_main.png" alt="1.2-zh_main" style="zoom:50%;" />

> **注**：本次测试样例中，中文/文言翻译到其他语言，则文言文的 tokens 最少；英文翻译至其他语言，则英文最少。无论是哪种，需要主要文言文虽然文字简练，但一个字可能对应多个 tokens，且由于互联网上大多数数据是白话文而非文言文，且网络词汇和技术用语用文言文表达比较僵硬，或者难免有语义的偏差，因此使用 LLM 时以文言文作为问答语言的方案有待商榷。

---

### 项目介绍

#### 功能概览

| 功能 | 说明 |
|------|------|
| 多语言统计 | 遍历 `data/` 下所有样例，计算字符数、token 数及比率 |
| 格式化导出 | JSON / CSV（utf-8-sig）/ Markdown 表格 |
| 学术图表 | 分组柱状图 + 双纵轴折线，按 token 数升序排列 |
| 词元着色 MD | 每个变体独立 `.md`，HTML `<span>` 对每个可解码片段着色，鼠标悬停显示 token ID |
| 任意层级目录 | `data/` 支持单层（`code/001.json`）与多层（`lang/en_main/001.json`）混用 |
| 子任务过滤 | `--subpath lang/en_main` 只处理指定路径，输出自动镜像 |

---

#### 项目结构

```
PR-exp3/
├── data/                        # 测试数据（可任意嵌套）
│   ├── code/                    # 代码片段
│   │   └── 001.json
│   ├── emoji/                   # Emoji / 特殊字符
│   │   └── 001.json
│   ├── extreme/                 # 极端边界情况
│   │   └── 001.json
│   ├── format/                  # 格式差异
│   │   └── 001.json
│   ├── lang/                    # 多语言对比（两层结构）
│   │   ├── en_main/
│   │   │   └── 001.json         # Transformer 论文摘要（9 语言）
│   │   ├── zh_main/
│   │   │   └── 001.json
│   │   └── zhc_main/
│   │       └── 001.json
│   └── num_symbol/              # 数字 / 符号
│       └── 001.json
│
├── src/
│   ├── schema.py                # 数据模型（Case / Variant dataclass）+ 字段校验
│   ├── loader.py                # 递归扫描 data/，支持 subpath 过滤
│   ├── tokenizer.py             # BaseTokenizer 接口 + TiktokenTokenizer 实现
│   ├── metrics.py               # 指标计算（char / token / ratio，除零安全）
│   ├── exporter.py              # 导出 JSON / CSV / Markdown
│   ├── plotter.py               # 学术图表（matplotlib + seaborn，支持 CJK 字体）
│   ├── variant_exporter.py      # 词元着色 Markdown 可视化
│   └── colors.json              # 20 色循环配色表
│
├── scripts/
|   ├── demo.bat                 # 使用 text 和 text_path 参数调用 main.py的示例
│   ├── lang.bat                 # 批量运行 lang/ 下三个子任务
│   └── run_all.bat              # 批量运行全部 8 个子任务
│
├── tests/
│   └── test_metrics.py          # 单元测试（27 个）
│
├── main.py                      # CLI 入口（6 步流水线）
├── requirements.txt
└── README.md
```

---

#### 数据格式

每个 `*.json` 文件对应一个**样例（Case）**，含若干**变体（Variant）**：

```json
{
  "case_id": "lang_en_main_001",
  "task_type": "lang",
  "subgroup": "en_main",
  "description": "Transformer 论文摘要（9 种语言）",
  "tags": ["nlp", "multilingual"],
  "variants": [
    { "variant_id": "英文",     "language": "en",      "text": "The dominant sequence..." },
    { "variant_id": "简体中文", "language": "zh-Hans", "text": "当前主流的序列..." }
  ]
}
```

> `task_type` / `subgroup` 在 JSON 内**显式冗余存储**，移动文件后仍可追溯，不依赖路径推断。

目录层级可任意嵌套：

```
data/code/001.json             ← 单层（task_type=code，subgroup 从 JSON 读取）
data/lang/en_main/001.json    ← 两层
```

---

#### 统计口径

| 指标 | 定义 |
|------|------|
| `char_count` | `len(text)`，空格 / 换行 / tab 全部计入 |
| `token_count` | tokenizer 编码结果长度 |
| `char_per_token` | `char_count / token_count`，`token_count = 0` 时为 `null` |
| `token_per_char` | `token_count / char_count`，`char_count = 0` 时为 `null` |

---

### 环境配置

```bash
conda create -n ai python=3.12
conda activate ai
pip install -r requirements.txt
```

**Python 版本要求**：3.12+

---

### 运行方式

#### （1）处理单个子任务（推荐）

```bash
python main.py --subpath lang/en_main
# 输出自动镜像到 output/lang/en_main/
```

#### （2）扫描全部数据

```bash
python main.py
# 输出到 output/
```

#### （3）内联文本（直接传入字符串）

```bash
python main.py --text "Hello world! 你好世界！😀🔥" --output-dir output/test --no-plot
# 输出到 output/test/inline/
```

#### （4）读取文本文件

```bash
python main.py --text-path "data/text/日月前事.txt" --output-dir output/test --no-plot
# 输出到 output/test/日月前事/（以文件名不含扩展名命名子目录）
```

#### （5）批量脚本

```bat
rem 只跑 lang/ 下三个子组
scripts\lang.bat

rem 跑全部 8 个子组（code / emoji / extreme / format / num_symbol / lang/...）
scripts\run_all.bat

rem 可选：指定 tiktoken 模型
scripts\run_all.bat gpt-4o-mini
```

#### （6）完整 CLI 参数

```
--data-dir       数据根目录（默认 data）
--output-dir     输出根目录（默认 output/temp）
--subpath        子路径过滤，如 lang/en_main（输出自动镜像同级目录）
--text TEXT      直接传入待统计文本，跳过 data 目录扫描；与 --text-path / --data-dir 互斥
--text-path PATH 读取 UTF-8 文本文件并统计，输出子目录以文件名不含扩展名命名；与 --text / --data-dir 互斥
--tokenizer      tokenizer 名称（默认 tiktoken）
--model          tiktoken 模型名（默认 gpt-4o）
--output-prefix  输出文件名前缀（默认 results）
--no-plot        跳过图表生成
--warn-errors    将校验警告打印到 stderr（默认静默跳过）
```

---

### 输出文件

每次运行输出两类文件：

#### （1）汇总报表

| 文件 | 说明 |
|------|------|
| `results.json` | 完整统计结果（结构化，`null` 保留） |
| `results.csv` | 表格结果（utf-8-sig，Excel 可直接打开） |
| `results.md` | Markdown 统计表格（GitHub 友好） |
| `results.png` | 学术图表（分组柱 + 双纵轴折线，按 token 数升序） |

#### （2）词元着色 Markdown（子目录 `<case_stem>/`）

```
output/lang/en_main/
├── results.json
├── results.csv
├── results.md
├── results.png
└── 001/                     ← 来自 001.json
    ├── 英文.md
    ├── 简体中文.md
    ├── 繁体中文.md
    ├── 日文.md
    └── ...（共 9 个变体）
```

每个变体 `.md` 文件结构：

```markdown
# 英文 (en)

chars = 1139, tokens = 219, chars/tokens = 5.20

<span title="tokens: 791" style="background:#fecaca;...">The</span><span title="tokens: 22621" style="..."> dominant</span>...
```

- 着色单位为**可解码显示片段**（1 片段 = 1 或多个 token），避免 BPE 跨字节切分导致字符分裂
- **鼠标悬停** `<span>` 时**显示对应的 token ID**（多个用逗号分隔）
- 20 种低饱和度配色循环，相邻片段颜色对比明显、整体柔和

---

### 运行单元测试

```bash
python -m pytest tests/ -v
```

共 27 个测试，覆盖：

| 测试类 | 覆盖内容 |
|--------|---------|
| `TestComputeMetrics` | 空串、空白串、ASCII、多行、emoji、除零边界 |
| `TestComputeCaseMetrics` | 多 variant、多 tokenizer、字段正确性 |
| `TestTokenizeToBytes` | 空串、ASCII、CJK、Emoji、与 encode 长度一致 |
| `TestGroupSegments` | 纯 ASCII、ID 保留、往返文本、无替换字符、空输入、模拟 BPE 跨字节合并 |
| `TestExportVariantMds` | 文件创建、子目录命名、文件名、MD 头格式、span title、无替换字符、文本往返 |

---

### 扩展指南

#### （1）新增 tokenizer

在 `src/tokenizer.py` 继承 `BaseTokenizer` 并注册：

```python
class MyTokenizer(BaseTokenizer):
    name = "my_tok"

    def encode(self, text: str) -> list[int]: ...
    def tokenize_to_strings(self, text: str) -> list[str]: ...
    def tokenize_to_bytes(self, text: str) -> list[bytes]: ...

_REGISTRY["my_tok"] = MyTokenizer
```

之后 `--tokenizer my_tok` 即可使用，无需修改其他文件。

#### （2）新增任务类型

直接在 `data/` 下创建目录和 JSON 文件，无需修改代码，`loader.py` 会自动发现。

#### （3）新增指标

修改 `src/metrics.py` 的 `MetricRow` dataclass 与 `_compute_metrics()`；`exporter.py` 通过 `dataclasses.asdict()` 自动将新字段写入 CSV。

---

### 设计说明

- **字节级分段渲染**：tiktoken（GPT 系列）是字节级 BPE，一个非 ASCII 字符有时跨多个 token 存储。`variant_exporter._group_segments()` 累积每个 token 的原始字节，直到字节序列能完整解码为 UTF-8 再输出一个 `<span>`，从根本上杜绝替换字符（`\ufffd`）。
- **subpath 镜像输出**：`--subpath lang/en_main` 将结果写到 `output/lang/en_main/`，目录结构与 `data/` 完全对应，便于批量比较与脚本遍历。
- **除零安全**：`char_count = 0` 或 `token_count = 0` 时对应比率返回 `null`，不抛异常。
- **CJK 图表字体**：优先加载系统内 Microsoft YaHei（`msyh.ttc`），回退到 SimHei / PingFang / Noto CJK，保证中日韩标签在图表中正常渲染。
