"""
main.py — CLI 入口

用法示例
--------
# 默认：扫描全部 data/，输出到 output/
python main.py

# 只运行一个子任务，输出自动镜像到 output/lang/en_main/
python main.py --subpath lang/en_main

# 完整参数
python main.py --subpath lang/en_main --data-dir data --output-dir output \
               --tokenizer tiktoken --model gpt-4o --output-prefix results

# 查看帮助
python main.py --help
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

from src.exporter import export_csv, export_json, export_md
from src.loader import scan_data_dir
from src.metrics import compute_all_metrics
from src.plotter import plot_metrics
from src.tokenizer import get_tokenizer, list_tokenizers


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
        help="结果输出根目录（自动创建）",
    )
    parser.add_argument(
        "--subpath",
        default=None,
        metavar="TASK/SUBGROUP",
        help=(
            "只处理指定子路径，如 lang/en_main。"
            "输出目录自动镜像为 <output-dir>/<subpath>/。"
            "不指定则扫描全部数据，输出到 <output-dir>/。"
        ),
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
        help="输出文件名前缀，生成 <prefix>.json / .csv / .md / .png",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        default=False,
        help="跳过图表生成（无 matplotlib 环境时使用）",
    )
    parser.add_argument(
        "--warn-errors",
        action="store_true",
        default=False,
        help="将校验警告输出到 stderr（默认静默跳过）",
    )
    return parser


# ---------------------------------------------------------------------------
# 主流程辅助
# ---------------------------------------------------------------------------


def _resolve_output_dir(output_dir: Path, subpath: str | None) -> Path:
    """
    根据 subpath 镜像输出目录。
    - subpath="lang/en_main"  →  output_dir / "lang" / "en_main"
    - subpath=None            →  output_dir
    """
    if subpath:
        return output_dir / Path(subpath)
    return output_dir


def _make_chart_title(args: argparse.Namespace) -> str:
    scope = args.subpath if args.subpath else "all"
    return (
        f"字符 & Token 统计数据  |  scope={scope}"
        f"  tokenizer={args.tokenizer}({args.model})"
    )


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def run(args: argparse.Namespace) -> int:
    """执行完整流程，返回退出码（0=成功，1=有错误）。"""

    if args.warn_errors:
        warnings.simplefilter("always")
    else:
        warnings.simplefilter("ignore")

    data_dir = Path(args.data_dir)
    output_dir = _resolve_output_dir(Path(args.output_dir), args.subpath)

    # 1. 扫描数据文件
    scope = f"data/{args.subpath}" if args.subpath else "data（全部）"
    print(f"[1/5] 扫描数据目录: {data_dir.resolve()}  scope={scope}")
    try:
        cases = scan_data_dir(data_dir, subpath=args.subpath)
    except FileNotFoundError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    if not cases:
        print("警告: 未找到任何有效样例，请检查数据目录结构或 --subpath 参数。")
        return 1

    print(f"      找到 {len(cases)} 个样例")

    # 2. 初始化 tokenizer
    print(f"[2/5] 初始化 tokenizer: {args.tokenizer} (model={args.model})")
    try:
        tok = get_tokenizer(args.tokenizer, model=args.model)
    except (ImportError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    # 3. 计算指标
    print("[3/5] 计算指标 ...")
    rows = compute_all_metrics(cases, tokenizers=[tok])
    print(f"      共生成 {len(rows)} 条统计记录")

    # 4. 导出结构化结果
    prefix = args.output_prefix
    print(f"[4/5] 导出结果到: {output_dir.resolve()}")
    json_path = export_json(rows, output_dir / f"{prefix}.json")
    csv_path  = export_csv(rows,  output_dir / f"{prefix}.csv")
    md_path   = export_md(rows,   output_dir / f"{prefix}.md")
    print(f"      JSON => {json_path}")
    print(f"      CSV  => {csv_path}")
    print(f"      MD   => {md_path}")

    # 5. 绘制学术图表
    if args.no_plot:
        print("[5/5] 图表生成已跳过（--no-plot）")
    else:
        print("[5/5] 绘制图表 ...")
        try:
            png_path = plot_metrics(
                rows,
                output_dir / f"{prefix}.png",
                title=_make_chart_title(args),
            )
            print(f"      PNG  => {png_path}")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"      警告: 图表生成失败（{exc}），已跳过。", file=sys.stderr)

    print("完成。")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
