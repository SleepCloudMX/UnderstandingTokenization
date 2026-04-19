"""
schema.py — 数据 schema 定义与校验

使用 dataclass 而非 pydantic，减少外部依赖。
校验失败时返回错误信息列表，而不是直接抛异常，方便批量处理时汇总。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


@dataclass
class Variant:
    """单个测试样例中的一个语言版本或变体。"""

    variant_id: str
    language: str
    text: str


@dataclass
class Case:
    """一个测试样例，对应 data/ 下的一个 JSON 文件。"""

    case_id: str
    task_type: str
    subgroup: str
    description: str
    tags: list[str]
    variants: list[Variant]
    source_file: str  # 原始 JSON 文件的路径（相对或绝对均可）


# ---------------------------------------------------------------------------
# 校验
# ---------------------------------------------------------------------------


def _check_str_field(obj: dict[str, Any], key: str, errors: list[str]) -> None:
    """检查字段存在且为非空字符串（允许空白，因为空白文本是有效的测试用例）。"""
    if key not in obj:
        errors.append(f"缺少必填字段: '{key}'")
    elif not isinstance(obj[key], str):
        errors.append(f"字段 '{key}' 必须是字符串，实际类型: {type(obj[key]).__name__}")


def validate_raw(data: dict[str, Any]) -> list[str]:
    """
    校验从 JSON 文件中读取的原始 dict，返回错误列表。
    列表为空 => 校验通过。
    """
    errors: list[str] = []

    # 顶层必填字段
    for key in ("case_id", "task_type", "subgroup", "description"):
        _check_str_field(data, key, errors)

    if "tags" not in data:
        errors.append("缺少必填字段: 'tags'")
    elif not isinstance(data["tags"], list):
        errors.append("字段 'tags' 必须是列表")

    if "variants" not in data:
        errors.append("缺少必填字段: 'variants'")
    elif not isinstance(data["variants"], list):
        errors.append("字段 'variants' 必须是列表")
    elif len(data["variants"]) == 0:
        errors.append("'variants' 列表不能为空")
    else:
        for i, v in enumerate(data["variants"]):
            if not isinstance(v, dict):
                errors.append(f"variants[{i}] 必须是对象")
                continue
            for key in ("variant_id", "language", "text"):
                if key not in v:
                    errors.append(f"variants[{i}] 缺少必填字段: '{key}'")
                elif key != "text" and not isinstance(v[key], str):
                    errors.append(
                        f"variants[{i}].{key} 必须是字符串，"
                        f"实际类型: {type(v[key]).__name__}"
                    )
            # text 允许为空字符串，但必须是 str
            if "text" in v and not isinstance(v["text"], str):
                errors.append(
                    f"variants[{i}].text 必须是字符串，"
                    f"实际类型: {type(v['text']).__name__}"
                )

    return errors


def parse_case(data: dict[str, Any], source_file: str) -> Case:
    """
    将通过校验的原始 dict 转换为 Case 对象。
    调用前应先执行 validate_raw 并确认无错误。
    """
    variants = [
        Variant(
            variant_id=v["variant_id"],
            language=v["language"],
            text=v["text"],
        )
        for v in data["variants"]
    ]
    return Case(
        case_id=data["case_id"],
        task_type=data["task_type"],
        subgroup=data["subgroup"],
        description=data["description"],
        tags=list(data.get("tags", [])),
        variants=variants,
        source_file=source_file,
    )
