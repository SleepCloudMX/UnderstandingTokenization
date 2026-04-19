"""
exporter.py — 结果导出

支持导出为：
- JSON（结构化，便于程序读取）
- CSV （表格化，便于 Excel / pandas 分析）

输出目录不存在时自动创建。
浮点数保留 6 位有效数字，None 值在 CSV 中输出为空字符串。
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from src.metrics import MetricRow


# CSV 列顺序（与需求一致）
_CSV_FIELDS = [
    "task_type",
    "subgroup",
    "case_id",
    "variant_id",
    "language",
    "tokenizer",
    "char_count",
    "token_count",
    "char_per_token",
    "token_per_char",
    "text",
    "source_file",
]


def _format_float(value: Optional[float]) -> str:
    """将浮点数格式化为字符串，None 输出为空串。"""
    if value is None:
        return ""
    return f"{value:.6g}"


def export_json(rows: list[MetricRow], output_path: str | Path) -> Path:
    """
    将统计结果导出为 JSON 文件。

    参数
    ----
    rows : list[MetricRow]
        指标行列表。
    output_path : str | Path
        输出文件路径（含文件名），父目录不存在时自动创建。

    返回
    ----
    Path
        实际写入的文件路径。
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 将 dataclass 转为 dict，None 保留为 null
    data = [asdict(row) for row in rows]

    out.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out


def export_csv(rows: list[MetricRow], output_path: str | Path) -> Path:
    """
    将统计结果导出为 CSV 文件。

    参数
    ----
    rows : list[MetricRow]
        指标行列表。
    output_path : str | Path
        输出文件路径（含文件名），父目录不存在时自动创建。

    返回
    ----
    Path
        实际写入的文件路径。
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", newline="", encoding="utf-8-sig") as f:
        # utf-8-sig 写入 BOM，方便 Excel 直接打开中文不乱码
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()

        for row in rows:
            d = asdict(row)
            # 处理浮点 None
            d["char_per_token"] = _format_float(d["char_per_token"])
            d["token_per_char"] = _format_float(d["token_per_char"])
            writer.writerow(d)

    return out
