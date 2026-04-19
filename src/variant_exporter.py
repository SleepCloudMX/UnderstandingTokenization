"""
variant_exporter.py — 按词元着色的 Markdown 可视化导出

对每个样例（JSON 文件）下的每个变体，生成独立的 .md 文件：
    output/<subpath>/<case_stem>/<variant_id>.md

文件结构
--------
# <variant_id> (<language>)

chars = X, tokens = Y, chars/tokens = Z.ZZ

<词元着色 HTML 正文>

渲染策略
--------
以「可解码显示片段」为单位着色，而非逐 token 着色。

由于 BPE 是字节级分词，一个多字节 Unicode 字符（汉字、Emoji 等）有时会
被切分到相邻的多个 token 中（每个 token 持有不完整字节）。若逐 token 渲染
则无法合法解码，会产生乱码。

做法：累积每个 token 的原始字节，直到字节序列能完整解码为 UTF-8，才输出
一个 <span>。这样一个片段可能对应 1–N 个 token，但始终是视觉上完整的
字符序列。颜色按片段序号循环，20 种颜色来自 src/colors.json。
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from src.metrics import MetricRow
from src.tokenizer import BaseTokenizer


# ---------------------------------------------------------------------------
# 颜色加载
# ---------------------------------------------------------------------------

_COLORS: list[str] = []


def _load_colors() -> list[str]:
    global _COLORS
    if _COLORS:
        return _COLORS
    colors_path = Path(__file__).parent / "colors.json"
    with colors_path.open(encoding="utf-8") as f:
        data = json.load(f)
    _COLORS = data["colors"]
    return _COLORS


# ---------------------------------------------------------------------------
# 字节分段：将 token 字节列表合并为可解码的显示片段
# ---------------------------------------------------------------------------


def _group_segments(token_bytes: list[bytes]) -> list[tuple[str, int]]:
    """将逐 token 原始字节累积为可完整解码的 UTF-8 片段。

    返回值：list of (decoded_text, token_count)
        decoded_text  — 该片段对应的 Unicode 字符串（无乱码）
        token_count   — 合并了几个 token（通常为 1；跨字节字符 > 1）

    算法：逐字节累积，每次尝试 UTF-8 解码；
    成功则输出片段并重置缓冲区；最终残余字节用 latin-1 兜底（理论上不会
    出现，因为完整输入是合法 UTF-8，所有字节最终必能合并成完整字符）。
    """
    segments: list[tuple[str, int]] = []
    buf = b""
    count = 0
    for tb in token_bytes:
        buf += tb
        count += 1
        try:
            segments.append((buf.decode("utf-8"), count))
            buf = b""
            count = 0
        except UnicodeDecodeError:
            pass  # 字节序列尚不完整，继续累积
    if buf:
        # 兜底：剩余字节无法形成合法 UTF-8（极罕见），latin-1 无损呈现
        segments.append((buf.decode("latin-1"), count))
    return segments


# ---------------------------------------------------------------------------
# 核心：构建单个变体的 Markdown 文本
# ---------------------------------------------------------------------------


def _build_variant_md(
    row: MetricRow,
    tokenizer: BaseTokenizer,
    colors: list[str],
) -> str:
    """生成单个变体的 Markdown 内容（含 HTML 词元着色）。"""
    # ---- 标题与统计 ----
    cpt_str = (
        f"{row.char_per_token:.2f}" if row.char_per_token is not None else "N/A"
    )
    header = (
        f"# {row.variant_id} ({row.language})\n\n"
        f"chars = {row.char_count}, "
        f"tokens = {row.token_count}, "
        f"chars/tokens = {cpt_str}\n\n"
    )

    # ---- 词元着色正文（按可解码片段着色）----
    token_bytes = tokenizer.tokenize_to_bytes(row.text)
    if not token_bytes:
        body = "_（空文本）_\n"
    else:
        segments = _group_segments(token_bytes)
        parts: list[str] = []
        for i, (seg_text, _tok_count) in enumerate(segments):
            color = colors[i % len(colors)]
            # 转义 HTML 特殊字符，保留换行为 <br>
            escaped = html.escape(seg_text).replace("\n", "<br>\n")
            parts.append(
                f'<span style="background:{color};padding:1px 2px;border-radius:2px">'
                f"{escaped}</span>"
            )
        body = "".join(parts) + "\n"

    return header + body


# ---------------------------------------------------------------------------
# 公开接口
# ---------------------------------------------------------------------------


def export_variant_mds(
    rows: list[MetricRow],
    tokenizer: BaseTokenizer,
    output_dir: Path,
) -> list[Path]:
    """
    按 source_file（样例文件）分组，为每个变体生成着色 Markdown。

    输出路径规则
    ------------
    output_dir / <case_stem> / <variant_id>.md
    例：output/lang/en_main/001/英文.md

    参数
    ----
    rows        : 当前批次的全部 MetricRow（可跨多个 case）
    tokenizer   : 用于切词的 tokenizer 实例
    output_dir  : 对应本批次的输出根目录（已含 subpath 镜像）

    返回
    ----
    生成的 md 文件路径列表。
    """
    colors = _load_colors()
    written: list[Path] = []

    # 按 source_file 分组
    by_case: dict[str, list[MetricRow]] = {}
    for row in rows:
        by_case.setdefault(row.source_file, []).append(row)

    for source_file, case_rows in sorted(by_case.items()):
        # case_stem: 原始 JSON 文件的不含扩展名部分，如 "001"
        case_stem = Path(source_file).stem
        case_dir = output_dir / case_stem
        case_dir.mkdir(parents=True, exist_ok=True)

        for row in case_rows:
            # 文件名使用 variant_id，替换路径不安全字符
            safe_name = row.variant_id.replace("/", "-").replace("\\", "-")
            md_path = case_dir / f"{safe_name}.md"
            content = _build_variant_md(row, tokenizer, colors)
            md_path.write_text(content, encoding="utf-8")
            written.append(md_path)

    return written
