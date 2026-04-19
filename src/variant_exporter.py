"""
variant_exporter.py — 按词元着色的 Markdown 可视化导出

对每个样例（JSON 文件）下的每个变体，生成独立的 .md 文件：
    output/<subpath>/<case_stem>/<variant_id>.md

文件结构
--------
# <variant_id> (<language>)

chars = X, tokens = Y, chars/tokens = Z.ZZ

<词元着色 HTML 正文>

颜色配置从 src/colors.json 中循环读取（20 色）。
相邻词元颜色交替，保证视觉对比度。
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Optional

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

    # ---- 词元着色正文 ----
    tokens = tokenizer.tokenize_to_strings(row.text)
    if not tokens:
        body = "_（空文本）_\n"
    else:
        parts: list[str] = []
        for i, tok in enumerate(tokens):
            color = colors[i % len(colors)]
            # 转义 HTML 特殊字符，保留换行为 <br>
            escaped = html.escape(tok).replace("\n", "<br>\n")
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
