"""
metrics.py — 指标计算

统计口径（严格遵守）
--------------------
- char_count    = len(text)          空格、换行、tab 全部计入
- token_count   = tokenizer 编码结果长度
- char_per_token = char_count / token_count  （token_count=0 时为 None）
- token_per_char = token_count / char_count  （char_count=0 时为 None）

所有计算对以下边界情况安全：
- 空字符串 ""
- 纯空白字符串（如 "   \\n\\t"）
- 含 emoji、生僻汉字、多行文本
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.schema import Case, Variant
from src.tokenizer import BaseTokenizer


# ---------------------------------------------------------------------------
# 单行统计结果
# ---------------------------------------------------------------------------


@dataclass
class MetricRow:
    """一条统计记录，对应一个 (case × variant × tokenizer) 组合。"""

    task_type: str
    subgroup: str
    case_id: str
    variant_id: str
    language: str
    tokenizer: str
    char_count: int
    token_count: int
    char_per_token: Optional[float]
    token_per_char: Optional[float]
    text: str
    source_file: str


# ---------------------------------------------------------------------------
# 核心计算
# ---------------------------------------------------------------------------


def _compute_metrics(
    text: str,
    tokenizer: BaseTokenizer,
) -> tuple[int, int, Optional[float], Optional[float]]:
    """
    计算单条文本的四项指标。

    返回 (char_count, token_count, char_per_token, token_per_char)。
    """
    char_count: int = len(text)
    token_count: int = tokenizer.count_tokens(text)

    char_per_token: Optional[float] = (
        char_count / token_count if token_count > 0 else None
    )
    token_per_char: Optional[float] = (
        token_count / char_count if char_count > 0 else None
    )

    return char_count, token_count, char_per_token, token_per_char


def compute_case_metrics(
    case: Case,
    tokenizers: list[BaseTokenizer],
) -> list[MetricRow]:
    """
    对一个 Case 的所有 variants × 所有 tokenizers 计算指标。

    参数
    ----
    case : Case
        已加载并校验的测试样例。
    tokenizers : list[BaseTokenizer]
        要使用的 tokenizer 列表。

    返回
    ----
    list[MetricRow]
        按 (variant_id, tokenizer.name) 排序的统计行列表。
    """
    rows: list[MetricRow] = []

    for variant in case.variants:
        for tok in tokenizers:
            char_count, token_count, char_per_token, token_per_char = (
                _compute_metrics(variant.text, tok)
            )
            rows.append(
                MetricRow(
                    task_type=case.task_type,
                    subgroup=case.subgroup,
                    case_id=case.case_id,
                    variant_id=variant.variant_id,
                    language=variant.language,
                    tokenizer=tok.name,
                    char_count=char_count,
                    token_count=token_count,
                    char_per_token=char_per_token,
                    token_per_char=token_per_char,
                    text=variant.text,
                    source_file=case.source_file,
                )
            )

    return rows


def compute_all_metrics(
    cases: list[Case],
    tokenizers: list[BaseTokenizer],
) -> list[MetricRow]:
    """
    对所有 cases 批量计算指标，返回汇总后的行列表。
    """
    all_rows: list[MetricRow] = []
    for case in cases:
        all_rows.extend(compute_case_metrics(case, tokenizers))
    return all_rows
