"""
tokenizer.py — Tokenizer 适配层

设计原则：
- 定义统一的 BaseTokenizer 接口
- 每种 tokenizer 实现一个子类
- 通过 get_tokenizer(name) 工厂函数统一获取实例（带缓存）
- 未来新增 tokenizer 只需在此文件中添加子类并注册到 _REGISTRY

当前支持：
- tiktoken（OpenAI 官方 BPE tokenizer）

预留扩展：
- transformers（HuggingFace）
- sentencepiece
- 自定义字符级 tokenizer
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import ClassVar


# ---------------------------------------------------------------------------
# 基类
# ---------------------------------------------------------------------------


class BaseTokenizer(ABC):
    """所有 tokenizer 的统一接口。"""

    #: 该 tokenizer 的唯一名称，用于输出和命令行参数
    name: ClassVar[str]

    @abstractmethod
    def encode(self, text: str) -> list[int]:
        """将文本编码为 token id 列表。空文本应返回空列表。"""
        ...

    @abstractmethod
    def tokenize_to_strings(self, text: str) -> list[str]:
        """将文本切分为 token 字符串列表（解码后），空文本返回空列表。"""
        ...

    def count_tokens(self, text: str) -> int:
        """返回 token 数量，对空文本安全。"""
        if not text:
            return 0
        return len(self.encode(text))


# ---------------------------------------------------------------------------
# tiktoken 实现
# ---------------------------------------------------------------------------


class TiktokenTokenizer(BaseTokenizer):
    """
    基于 tiktoken 的 BPE tokenizer。
    支持指定 OpenAI 模型名（model）或直接指定编码名（encoding）。
    """

    name: ClassVar[str] = "tiktoken"

    def __init__(
        self,
        model: str = "gpt-4o",
        encoding: str | None = None,
    ) -> None:
        try:
            import tiktoken  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "tiktoken 未安装，请执行: pip install tiktoken"
            ) from exc

        if encoding is not None:
            self._enc = tiktoken.get_encoding(encoding)
        else:
            self._enc = tiktoken.encoding_for_model(model)

        self._model = model

    def encode(self, text: str) -> list[int]:
        if not text:
            return []
        # disallowed_special=() 允许编码所有特殊 token（如 <|endoftext|>）
        return self._enc.encode(text, disallowed_special=())

    def tokenize_to_strings(self, text: str) -> list[str]:
        if not text:
            return []
        token_ids = self._enc.encode(text, disallowed_special=())
        # 不能使用 self._enc.decode([tid])：其内部以 errors="replace" 调用
        # bytes.decode("utf-8")，对 BPE 切出的不完整多字节序列会产生 \ufffd。
        # 改用 decode_single_token_bytes 获取原始字节，再手动解码：
        #   - 完整 UTF-8 序列（绝大多数情况）→ 直接 decode("utf-8")
        #   - 不完整字节序列（BPE 跨字节切分）→ decode("latin-1") 无损保留字节值
        result: list[str] = []
        for tid in token_ids:
            raw: bytes = self._enc.decode_single_token_bytes(tid)
            try:
                result.append(raw.decode("utf-8"))
            except UnicodeDecodeError:
                result.append(raw.decode("latin-1"))
        return result

    @property
    def model(self) -> str:
        return self._model


# ---------------------------------------------------------------------------
# 预留：HuggingFace transformers tokenizer（示例骨架，未激活）
# ---------------------------------------------------------------------------

# class HFTokenizer(BaseTokenizer):
#     name: ClassVar[str] = "hf"
#
#     def __init__(self, model_name: str = "bert-base-uncased") -> None:
#         from transformers import AutoTokenizer
#         self._tok = AutoTokenizer.from_pretrained(model_name)
#         self._model_name = model_name
#
#     def encode(self, text: str) -> list[int]:
#         if not text:
#             return []
#         return self._tok.encode(text, add_special_tokens=False)


# ---------------------------------------------------------------------------
# 注册表与工厂
# ---------------------------------------------------------------------------

# 注册表：name -> 构造函数（可 callable）
_REGISTRY: dict[str, type[BaseTokenizer]] = {
    TiktokenTokenizer.name: TiktokenTokenizer,
    # HFTokenizer.name: HFTokenizer,  # 取消注释即可启用
}


@lru_cache(maxsize=16)
def get_tokenizer(name: str, **kwargs: str) -> BaseTokenizer:
    """
    工厂函数，按名称获取 tokenizer 实例（带 lru_cache 缓存，避免重复加载）。

    参数
    ----
    name : str
        tokenizer 名称，如 "tiktoken"。
    **kwargs
        传递给具体 tokenizer 构造函数的额外参数（如 model="gpt-4o"）。
        注意：lru_cache 要求参数可哈希，因此 kwargs 在内部转换为 frozenset。

    示例
    ----
    tok = get_tokenizer("tiktoken", model="gpt-4o")
    """
    if name not in _REGISTRY:
        raise ValueError(
            f"未知 tokenizer: '{name}'。"
            f"可用选项: {sorted(_REGISTRY.keys())}"
        )
    cls = _REGISTRY[name]
    return cls(**kwargs)  # type: ignore[call-arg]


def list_tokenizers() -> list[str]:
    """返回所有已注册 tokenizer 的名称列表。"""
    return sorted(_REGISTRY.keys())
