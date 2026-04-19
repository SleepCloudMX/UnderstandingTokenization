"""
tests/test_metrics.py — 单元测试

验证统计口径的关键边界情况：
- 空字符串
- 纯空白字符串
- emoji
- 多行文本
- 普通文本
"""

from __future__ import annotations

import sys
import os

# 确保从项目根目录运行时能找到 src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock

from src.metrics import _compute_metrics, MetricRow, compute_case_metrics
from src.schema import Case, Variant
from src.tokenizer import BaseTokenizer


class MockTokenizer(BaseTokenizer):
    """用于测试的 mock tokenizer，每个非空字符返回一个 token。"""

    name = "mock"

    def encode(self, text: str) -> list[int]:
        # 每个字符一个 token（仅用于测试逻辑，不代表真实 tokenizer 行为）
        if not text:
            return []
        return list(range(len(text)))


class TestComputeMetrics(unittest.TestCase):

    def setUp(self) -> None:
        self.tok = MockTokenizer()

    def test_empty_string(self) -> None:
        char_count, token_count, cpt, tpc = _compute_metrics("", self.tok)
        self.assertEqual(char_count, 0)
        self.assertEqual(token_count, 0)
        self.assertIsNone(cpt)
        self.assertIsNone(tpc)

    def test_whitespace_only(self) -> None:
        text = "   \n\t  "
        char_count, token_count, cpt, tpc = _compute_metrics(text, self.tok)
        self.assertEqual(char_count, len(text))  # 空白字符计入
        self.assertEqual(token_count, len(text))
        self.assertIsNotNone(cpt)
        self.assertIsNotNone(tpc)

    def test_plain_ascii(self) -> None:
        text = "Hello"
        char_count, token_count, cpt, tpc = _compute_metrics(text, self.tok)
        self.assertEqual(char_count, 5)
        self.assertEqual(token_count, 5)
        self.assertAlmostEqual(cpt, 1.0)
        self.assertAlmostEqual(tpc, 1.0)

    def test_multiline(self) -> None:
        text = "line1\nline2\nline3"
        char_count, token_count, cpt, tpc = _compute_metrics(text, self.tok)
        self.assertEqual(char_count, len(text))  # 换行符计入
        self.assertEqual(token_count, len(text))

    def test_emoji(self) -> None:
        # 单个 emoji 可能是多个 codepoint，但 len() 对 Python str 按 codepoint 计算
        text = "😊🎉"
        char_count, token_count, cpt, tpc = _compute_metrics(text, self.tok)
        self.assertEqual(char_count, len(text))  # Python len 对 emoji 的行为
        self.assertEqual(token_count, len(text))

    def test_no_divide_by_zero_when_tokenizer_returns_empty(self) -> None:
        """当 tokenizer 对非空文本返回 0 个 token 时不应抛出异常。"""

        class ZeroTokenizer(BaseTokenizer):
            name = "zero"

            def encode(self, text: str) -> list[int]:
                return []

        tok = ZeroTokenizer()
        char_count, token_count, cpt, tpc = _compute_metrics("some text", tok)
        self.assertEqual(char_count, 9)
        self.assertEqual(token_count, 0)
        self.assertIsNone(cpt)
        self.assertIsNotNone(tpc)  # token_per_char = 0/9 = 0.0


class TestComputeCaseMetrics(unittest.TestCase):

    def setUp(self) -> None:
        self.tok = MockTokenizer()
        self.case = Case(
            case_id="test_001",
            task_type="test",
            subgroup="unit",
            description="unit test case",
            tags=[],
            variants=[
                Variant(variant_id="en", language="en", text="hello"),
                Variant(variant_id="zh", language="zh", text="你好"),
            ],
            source_file="test/001.json",
        )

    def test_row_count(self) -> None:
        rows = compute_case_metrics(self.case, [self.tok])
        # 2 variants × 1 tokenizer = 2 rows
        self.assertEqual(len(rows), 2)

    def test_multiple_tokenizers(self) -> None:
        tok2 = MockTokenizer()
        tok2.name = "mock2"  # type: ignore[assignment]
        rows = compute_case_metrics(self.case, [self.tok, tok2])
        # 2 variants × 2 tokenizers = 4 rows
        self.assertEqual(len(rows), 4)

    def test_row_fields(self) -> None:
        rows = compute_case_metrics(self.case, [self.tok])
        row = rows[0]
        self.assertEqual(row.task_type, "test")
        self.assertEqual(row.subgroup, "unit")
        self.assertEqual(row.case_id, "test_001")
        self.assertEqual(row.source_file, "test/001.json")


if __name__ == "__main__":
    unittest.main()
