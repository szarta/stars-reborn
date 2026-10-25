"""Regression tests for project_facts.evaluate (the facts-vs-docs check).

Also asserts the real repo's pins all pass, so this doubles as the integration
guard: committing a doc that contradicts docs/project_facts.json fails here.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import project_facts  # noqa: E402


class EvaluateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.docs = Path(self._tmp.name)
        (self.docs / "a.rst").write_text(
            "The cap is **20 widgets** and the base is 25,000 units.\n"
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _fact(self, **kw) -> dict:
        base = {
            "id": "widgets",
            "value": "20",
            "targets": ["a.rst"],
            "patterns": [r"\*\*(\d+) widgets\*\*"],
        }
        base.update(kw)
        return base

    def test_matching_value_passes(self):
        stale, dead, checked = project_facts.evaluate([self._fact()], self.docs)
        self.assertEqual((stale, dead), ([], []))
        self.assertEqual(checked, 1)

    def test_stale_value_is_flagged(self):
        stale, dead, _ = project_facts.evaluate([self._fact(value="19")], self.docs)
        self.assertEqual(dead, [])
        self.assertEqual(len(stale), 1)
        self.assertIn("widgets", stale[0])
        self.assertIn("a.rst:1", stale[0])

    def test_pattern_matching_nothing_is_a_dead_pin(self):
        stale, dead, _ = project_facts.evaluate(
            [self._fact(patterns=[r"\*\*(\d+) gadgets\*\*"])], self.docs
        )
        self.assertEqual(stale, [])
        self.assertEqual(len(dead), 1)
        self.assertIn("widgets", dead[0])

    def test_missing_target_is_dead(self):
        stale, dead, _ = project_facts.evaluate(
            [self._fact(targets=["missing.rst"])], self.docs
        )
        self.assertEqual(stale, [])
        self.assertTrue(any("does not exist" in d for d in dead))

    def test_pattern_may_span_line_wraps(self):
        (self.docs / "wrap.rst").write_text("a **20 starbase\ndesigns** b\n")
        fact = self._fact(
            id="starbase",
            targets=["wrap.rst"],
            patterns=[r"\*\*(\d+) starbase\s+designs\*\*"],
        )
        stale, dead, checked = project_facts.evaluate([fact], self.docs)
        self.assertEqual((stale, dead), ([], []))
        self.assertEqual(checked, 1)

    def test_real_repo_pins_all_match(self):
        pins = project_facts.load_facts()
        stale, dead, checked = project_facts.evaluate(pins, project_facts.DOCS)
        self.assertEqual(stale, [], "stale figures in the design docs")
        self.assertEqual(dead, [], "dead pins in project_facts.json")
        self.assertGreaterEqual(checked, len(pins))


if __name__ == "__main__":
    unittest.main()
