"""
main.py — CLI 入口

用法示例
--------
# 默认：扫描 ./data，使用 tiktoken(gpt-4o)，输出到 ./output
python main.py

# 指定数据目录、输出目录、tokenizer 模型
python main.py --data-dir data --output-dir output --tokenizer tiktoken --model gpt-4o

# 查看帮助
python main.py --help
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

from src.exporter import export_csv, export_json
from src.loader import scan_data_dir
from src.metrics import compute_all_metrics
from src.tokenizer import TiktokenTokenizer, get_tokenizer, list_tokenizers


# ---------------------------------------------------------------------------
# 参数解析
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="token-counter",
        description="批量统计多语言 / 多格式测试文本的字符数与 token 数，并导出结果。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="数据根目录（包含 task_type/subgroup/*.json 结构）",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="结果输出目录（自动创建）",
    )
    parser.add_argument(
        "--tokenizer",
        default="tiktoken",
        choices=list_tokenizers(),
        help="要使用的 tokenizer 名称",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="tiktoken: 指定 OpenAI 模型名（决定编码方案）",
    )
    parser.add_argument(
        "--output-prefix",
        default="results",
        help="输出文件名前缀，最终生成 <prefix>.json 和 <prefix>.csv",
    )
    parser.add_argument(
        "--warn-errors",
        action="store_true",
        default=False,
        help="将校验警告输出到 stderr（默认静默跳过）",
    )
    return parser


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def run(args: argparse.Namespace) -> int:
    """执行完整流程，返回退出码（0=成功，1=有错误）。"""

    # 1. 可选：让 warnings 打印到 stderr
    if args.warn_errors:
        warnings.simplefilter("always")
    else:
        warnings.simplefilter("ignore")

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)

    # 2. 扫描数据文件
    print(f"[1/4] 扫描数据目录: {data_dir.resolve()}")
    try:
        cases = scan_data_dir(data_dir)
    except FileNotFoundError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    if not cases:
        print("警告: 未找到任何有效样例，请检查数据目录结构。")
        return 1

    print(f"      找到 {len(cases)} 个样例")

    # 3. 初始化 tokenizer
    print(f"[2/4] 初始化 tokenizer: {args.tokenizer} (model={args.model})")
    try:
        tok = get_tokenizer(args.tokenizer, model=args.model)
    except (ImportError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    # 4. 计算指标
    print("[3/4] 计算指标 ...")
    rows = compute_all_metrics(cases, tokenizers=[tok])
    print(f"      共生成 {len(rows)} 条统计记录")

    # 5. 导出结果
    print(f"[4/4] 导出结果到: {output_dir.resolve()}")
    prefix = args.output_prefix
    json_path = export_json(rows, output_dir / f"{prefix}.json")
    csv_path = export_csv(rows, output_dir / f"{prefix}.csv")

    print(f"      JSON => {json_path}")
    print(f"      CSV  => {csv_path}")
    print("完成。")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
