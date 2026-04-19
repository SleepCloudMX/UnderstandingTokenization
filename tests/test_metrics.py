"""
tests/test_metrics.py — 单元测试

验证统计口径的关键边界情况：
- 空字符串
- 纯空白字符串
- emoji
- 多行文本
- 普通文本

以及对以下模块的覆盖：
- src.tokenizer.BaseTokenizer（tokenize_to_bytes / tokenize_to_strings）
- src.variant_exporter._group_segments
- src.variant_exporter.export_variant_mds
"""

from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

# 确保从项目根目录运行时能找到 src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from src.metrics import _compute_metrics, MetricRow, compute_case_metrics
from src.schema import Case, Variant
from src.tokenizer import BaseTokenizer
from src.variant_exporter import _group_segments, export_variant_mds


# ---------------------------------------------------------------------------
# Mock tokenizer
# ---------------------------------------------------------------------------


class MockTokenizer(BaseTokenizer):
    """用于测试的 mock tokenizer，每个字符对应一个 token（id = 字符序号）。"""

    name = "mock"

    def encode(self, text: str) -> list[int]:
        if not text:
            return []
        return list(range(len(text)))

    def tokenize_to_bytes(self, text: str) -> list[bytes]:
        """每个字符的 UTF-8 字节作为一个 token（保证段分组正确性）。"""
        if not text:
            return []
        return [ch.encode("utf-8") for ch in text]

    def tokenize_to_strings(self, text: str) -> list[str]:
        return list(text)


class ZeroTokenizer(BaseTokenizer):
    """返回 0 个 token 的边界 tokenizer。"""

    name = "zero"

    def encode(self, text: str) -> list[int]:
        return []

    def tokenize_to_bytes(self, text: str) -> list[bytes]:
        return []

    def tokenize_to_strings(self, text: str) -> list[str]:
        return []


# ---------------------------------------------------------------------------
# _compute_metrics 边界测试
# ---------------------------------------------------------------------------


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
        text = "😊🎉"
        char_count, token_count, cpt, tpc = _compute_metrics(text, self.tok)
        self.assertEqual(char_count, len(text))  # Python len 按 codepoint 计算
        self.assertEqual(token_count, len(text))

    def test_no_divide_by_zero_when_tokenizer_returns_empty(self) -> None:
        """当 tokenizer 对非空文本返回 0 个 token 时不应抛出异常。"""
        tok = ZeroTokenizer()
        char_count, token_count, cpt, tpc = _compute_metrics("some text", tok)
        self.assertEqual(char_count, 9)
        self.assertEqual(token_count, 0)
        self.assertIsNone(cpt)
        self.assertIsNotNone(tpc)  # token_per_char = 0/9 = 0.0


# ---------------------------------------------------------------------------
# compute_case_metrics 测试
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# tokenize_to_bytes 测试
# ---------------------------------------------------------------------------


class TestTokenizeToBytes(unittest.TestCase):

    def setUp(self) -> None:
        self.tok = MockTokenizer()

    def test_empty(self) -> None:
        self.assertEqual(self.tok.tokenize_to_bytes(""), [])

    def test_ascii(self) -> None:
        result = self.tok.tokenize_to_bytes("Hi")
        self.assertEqual(result, [b"H", b"i"])

    def test_cjk(self) -> None:
        # 每个汉字 encode("utf-8") = 3 字节
        result = self.tok.tokenize_to_bytes("你好")
        self.assertEqual(result, ["你".encode("utf-8"), "好".encode("utf-8")])
        self.assertEqual(result[0], b"\xe4\xbd\xa0")

    def test_emoji(self) -> None:
        result = self.tok.tokenize_to_bytes("😊")
        self.assertEqual(result, ["😊".encode("utf-8")])

    def test_length_matches_encode(self) -> None:
        text = "Hello 世界"
        self.assertEqual(
            len(self.tok.tokenize_to_bytes(text)),
            len(self.tok.encode(text)),
        )


# ---------------------------------------------------------------------------
# _group_segments 测试
# ---------------------------------------------------------------------------


class TestGroupSegments(unittest.TestCase):

    def _bytes_and_ids(self, text: str) -> tuple[list[bytes], list[int]]:
        """用 MockTokenizer 的规则生成 token_bytes / token_ids。"""
        tok = MockTokenizer()
        return tok.tokenize_to_bytes(text), tok.encode(text)

    def test_ascii_each_char_one_segment(self) -> None:
        tb, ids = self._bytes_and_ids("abc")
        segs = _group_segments(tb, ids)
        self.assertEqual(len(segs), 3)
        texts = [s for s, _ in segs]
        self.assertEqual(texts, ["a", "b", "c"])

    def test_ids_preserved(self) -> None:
        tb, ids = self._bytes_and_ids("Hi")
        segs = _group_segments(tb, ids)
        # MockTokenizer: id = 字符序号 → H=0, i=1
        self.assertEqual(segs[0][1], [0])
        self.assertEqual(segs[1][1], [1])

    def test_roundtrip_text(self) -> None:
        """分段拼合后应严格等于原始文本。"""
        for text in ["hello", "你好世界", "😊🎉", "مرحبا", "안녕"]:
            tb, ids = self._bytes_and_ids(text)
            segs = _group_segments(tb, ids)
            rejoined = "".join(s for s, _ in segs)
            self.assertEqual(rejoined, text, f"roundtrip failed for {text!r}")

    def test_no_replacement_char(self) -> None:
        """分段文本中不应含有 Unicode 替换字符。"""
        for text in ["hello", "你好", "😊", "مرحبا"]:
            tb, ids = self._bytes_and_ids(text)
            segs = _group_segments(tb, ids)
            for seg_text, _ in segs:
                self.assertNotIn("\ufffd", seg_text,
                                 f"replacement char in segment {seg_text!r}")

    def test_empty_input(self) -> None:
        self.assertEqual(_group_segments([], []), [])

    def test_multi_token_segment_simulated(self) -> None:
        """模拟 BPE 将一个汉字拆成两个不完整字节 token 的情况。"""
        # 汉字"中" = b'\xe4\xb8\xad'（3 字节），人为拆成两个 token
        part1 = b"\xe4\xb8"   # 前 2 字节（不完整）
        part2 = b"\xad"       # 最后 1 字节
        segs = _group_segments([part1, part2], [100, 101])
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0][0], "中")
        self.assertEqual(segs[0][1], [100, 101])  # 两个 token 合并为一段


# ---------------------------------------------------------------------------
# export_variant_mds 测试
# ---------------------------------------------------------------------------


class TestExportVariantMds(unittest.TestCase):

    def setUp(self) -> None:
        self.tok = MockTokenizer()
        self.case = Case(
            case_id="vis_001",
            task_type="lang",
            subgroup="en_main",
            description="visualization test",
            tags=[],
            variants=[
                Variant(variant_id="英文", language="en", text="Hi"),
                Variant(variant_id="中文", language="zh", text="你好"),
            ],
            source_file="data/lang/en_main/001.json",
        )
        self.rows: list[MetricRow] = compute_case_metrics(self.case, [self.tok])

    def test_files_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            written = export_variant_mds(self.rows, self.tok, out_dir)
            self.assertEqual(len(written), 2)
            for p in written:
                self.assertTrue(p.exists(), f"{p} not created")

    def test_subdir_named_by_stem(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            written = export_variant_mds(self.rows, self.tok, out_dir)
            # 子目录应为 JSON 文件的 stem，即 "001"
            subdirs = {p.parent.name for p in written}
            self.assertEqual(subdirs, {"001"})

    def test_filename_is_variant_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            written = export_variant_mds(self.rows, self.tok, out_dir)
            names = {p.stem for p in written}
            self.assertIn("英文", names)
            self.assertIn("中文", names)

    def test_md_header_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            written = export_variant_mds(self.rows, self.tok, out_dir)
            for p in written:
                content = p.read_text(encoding="utf-8")
                self.assertTrue(content.startswith("# "),
                                f"{p.name} header missing")
                self.assertIn("chars =", content)
                self.assertIn("tokens =", content)
                self.assertIn("chars/tokens =", content)

    def test_md_contains_span_with_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            written = export_variant_mds(self.rows, self.tok, out_dir)
            for p in written:
                content = p.read_text(encoding="utf-8")
                self.assertIn('<span title="tokens:', content,
                              f"{p.name} missing title attribute")

    def test_no_replacement_char_in_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            written = export_variant_mds(self.rows, self.tok, out_dir)
            for p in written:
                content = p.read_text(encoding="utf-8")
                self.assertNotIn("\ufffd", content,
                                 f"{p.name} contains replacement char")

    def test_text_roundtrip_in_spans(self) -> None:
        """span 内文本拼合（去掉 <br>）应等于原始文本。"""
        import re
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            en_row = next(r for r in self.rows if r.variant_id == "英文")
            written = export_variant_mds([en_row], self.tok, out_dir)
            content = written[0].read_text(encoding="utf-8")
            spans = re.findall(r"<span[^>]*>([^<]*)</span>", content)
            rejoined = "".join(s.replace("<br>", "\n") for s in spans)
            self.assertEqual(rejoined, en_row.text)


if __name__ == "__main__":
    unittest.main()
