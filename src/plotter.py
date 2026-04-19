"""
plotter.py — 学术风格图表绘制

绘制单张图：分组柱状图（char_count / token_count）+ 双纵轴折线（char_per_token）。
X 轴按 token_count 从小到大排序。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.metrics import MetricRow


# 必须在导入 pyplot 之前设置非交互后端，否则在无显示器的脚本环境中会阻塞
import matplotlib
matplotlib.use("Agg")


# 尝试使用 seaborn 样式；若未安装则回退到 matplotlib 内置样式
def _setup_style() -> None:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    # 通过路径查找 CJK 字体（优先 Microsoft YaHei / SimHei），
    # 注册并设为全局字体，保证中日韩标签正常渲染
    _CJK_PATHS = [
        r"C:\Windows\Fonts\msyh.ttc",    # Microsoft YaHei（Win 内置）
        r"C:\Windows\Fonts\simhei.ttf",  # SimHei
        r"C:\Windows\Fonts\simsun.ttc",  # SimSun
        "/System/Library/Fonts/PingFang.ttc",       # macOS
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
    ]
    _font_set = False
    for path in _CJK_PATHS:
        import os
        if os.path.exists(path):
            fm.fontManager.addfont(path)
            prop = fm.FontProperties(fname=path)
            mpl.rcParams["font.family"] = prop.get_name()
            _font_set = True
            break

    try:
        import seaborn as sns  # type: ignore[import]
        sns.set_theme(style="whitegrid", font_scale=1.1)
        # seaborn 会重置 font.family，需重新设置
        if _font_set:
            mpl.rcParams["font.family"] = prop.get_name()  # type: ignore[possibly-undefined]
    except ImportError:
        try:
            plt.style.use("seaborn-v0_8-whitegrid")
        except OSError:
            pass


def plot_metrics(
    rows: list[MetricRow],
    output_path: str | Path,
    title: str = "字符数 & Tokens 统计数据",
    dpi: int = 150,
) -> Path:
    """
    为一组 MetricRow 绘制学术风格图表并保存。

    图表设计
    --------
    - 主纵轴（左）：分组柱状图，蓝色=char_count，橙色=token_count
    - 副纵轴（右）：折线图，绿色=char_per_token（token_count=0 的点跳过）
    - X 轴：按 token_count 升序排列的 variant_id (language)
    - 无子图（twin axis）

    参数
    ----
    rows : list[MetricRow]
        同一 tokenizer 下的统计行列表（建议只传单 tokenizer 的数据）。
    output_path : str | Path
        输出图像路径（.png 或 .pdf）。
    title : str
        图表标题。
    dpi : int
        输出分辨率。

    返回
    ----
    Path
        实际写入的文件路径。
    """
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np

    _setup_style()

    # --- 数据准备 ---
    # 按 token_count 升序排列
    sorted_rows = sorted(rows, key=lambda r: r.token_count)

    labels = [f"{r.variant_id}\n({r.language})" for r in sorted_rows]
    char_counts = [r.char_count for r in sorted_rows]
    token_counts = [r.token_count for r in sorted_rows]
    # char_per_token: None（除零）时用 nan 替代，折线会自动断开
    cpt_values = [
        r.char_per_token if r.char_per_token is not None else float("nan")
        for r in sorted_rows
    ]

    n = len(labels)
    x = np.arange(n)
    bar_width = 0.35

    # --- 图形初始化 ---
    fig, ax1 = plt.subplots(figsize=(max(8, n * 1.1), 6))

    # 主轴：分组柱状图
    bars1 = ax1.bar(
        x - bar_width / 2,
        char_counts,
        width=bar_width,
        label="Chars",
        color="#4878CF",
        alpha=0.85,
        zorder=3,
    )
    bars2 = ax1.bar(
        x + bar_width / 2,
        token_counts,
        width=bar_width,
        label="Tokens",
        color="#E87C2E",
        alpha=0.85,
        zorder=3,
    )

    ax1.set_xlabel("语言/语种", fontsize=12, labelpad=8)
    ax1.set_ylabel("Chars & Tokens", fontsize=12, labelpad=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=9)
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax1.tick_params(axis="y", labelsize=10)
    ax1.set_ylim(bottom=0)
    ax1.grid(
        axis="y",
        linestyle="--",
        linewidth=0.8,
        alpha=0.5,
        zorder=0,
    )
    ax1.grid(axis="x", visible=False)

    # 柱顶数值标注（仅在柱数不多时显示，避免拥挤）
    if n <= 12:
        for bar in bars1:
            h = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                h + ax1.get_ylim()[1] * 0.005,
                str(int(h)),
                ha="center", va="bottom", fontsize=7, color="#4878CF",
            )
        for bar in bars2:
            h = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                h + ax1.get_ylim()[1] * 0.005,
                str(int(h)),
                ha="center", va="bottom", fontsize=7, color="#E87C2E",
            )

    # 副轴：char_per_token 折线
    ax2 = ax1.twinx()
    line, = ax2.plot(
        x,
        cpt_values,
        color="#2CA02C",
        marker="o",
        markersize=6,
        linewidth=1.8,
        linestyle="--",
        label="字符/Token",
        zorder=4,
    )
    ax2.set_ylabel("chars/tokens", fontsize=12, labelpad=8, color="#2CA02C")
    ax2.spines["right"].set_color("#2CA02C")
    ax2.grid(
        axis="y",
        linestyle="--",
        linewidth=0.8,
        color="#2CA02C",
        alpha=0.3,
        zorder=1,
    )
    ax2.grid(axis="x", visible=False)
    ax2.tick_params(axis="y", labelcolor="#2CA02C", labelsize=10)
    # 副轴下限留 0，上限留 10% 空间
    valid_cpt = [v for v in cpt_values if not (v != v)]  # filter nan
    if valid_cpt:
        ax2.set_ylim(bottom=0, top=max(valid_cpt) * 1.15)

    # --- 标题：贴近图像，用轴标题而非 suptitle ---
    ax1.set_title(title, fontsize=13, fontweight="bold", pad=40)

    # --- 图例：置于标题正下方、图像顶部内侧，3 列水平排列 ---
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.0),   # 坐标相对于 ax1：正好在轴区顶缘下方
        ncol=3,
        fontsize=10,
        framealpha=0.92,
        edgecolor="#cccccc",
        borderpad=0.6,
        handlelength=1.8,
    )

    # --- 布局：预留标题 + 图例的空间 ---
    fig.tight_layout()
    # 在 tight_layout 后手动把上边界往上调一下，空出图例行高
    fig.subplots_adjust(top=0.82)

    # --- 保存 ---
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return out
