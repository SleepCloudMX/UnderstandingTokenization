"""
loader.py — 扫描 data/ 目录并加载所有测试样例

目录规范：
    data/
        <task_type>/          ← 第一层：任务类型
            <subgroup>/       ← 第二层：子类别
                *.json        ← 单个样例文件

非 .json 文件、不符合两层目录结构的文件将被跳过，并输出警告。
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

from src.schema import Case, parse_case, validate_raw


def _load_single(path: Path) -> Case | None:
    """
    加载并校验单个 JSON 样例文件。
    校验失败或解析出错时输出警告并返回 None，不中断整体流程。
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        warnings.warn(f"[跳过] 无法读取文件 {path}: {exc}")
        return None

    errors = validate_raw(raw)
    if errors:
        warnings.warn(
            f"[跳过] 文件 {path} 校验失败:\n  " + "\n  ".join(errors)
        )
        return None

    return parse_case(raw, source_file=str(path))


def scan_data_dir(
    data_dir: str | Path,
    subpath: str | None = None,
) -> list[Case]:
    """
    递归扫描 data_dir，收集所有符合两层目录规范的 JSON 样例。

    参数
    ----
    data_dir : str | Path
        数据根目录路径（即 data/）。
    subpath : str | None
        可选的子路径过滤器，例如 "lang/en_main"。
        仅加载该子目录下的样例；为 None 时扫描全部。

    返回
    ----
    list[Case]
        按文件路径排序的 Case 列表。
    """
    root = Path(data_dir).resolve()
    if not root.exists():
        raise FileNotFoundError(f"数据目录不存在: {root}")

    # 确定实际扫描的起始目录
    if subpath:
        scan_root = root / Path(subpath)
        if not scan_root.exists():
            raise FileNotFoundError(
                f"子路径不存在: {scan_root}（--subpath 参数值: {subpath}）"
            )
    else:
        scan_root = root

    cases: list[Case] = []
    json_files = sorted(scan_root.rglob("*.json"))

    for path in json_files:
        # 相对于 data root 的路径各段（保持统一的两层检验基准）
        rel_parts = path.relative_to(root).parts
        # 必须恰好是  task_type / subgroup / filename.json  三段
        if len(rel_parts) != 3:
            warnings.warn(
                f"[跳过] {path} 不符合 task_type/subgroup/file.json 结构"
            )
            continue

        case = _load_single(path)
        if case is not None:
            cases.append(case)

    return cases
