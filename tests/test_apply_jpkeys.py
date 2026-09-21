import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).parents[1] / "tools" / "apply_jpkeys.py"
spec = importlib.util.spec_from_file_location("apply_jpkeys", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


class TransformTests(unittest.TestCase):
    def test_direct_key(self):
        out, mapping = mod.transform('[keymap]\nkeys = """JP_AT JP_YEN"""\n')
        self.assertIn("LeftBracket International3", out)
        self.assertEqual({}, mapping)

    def test_shift_morph_injects_fork(self):
        out, mapping = mod.transform('[keymap]\nkeys = """JP_MINUSUNDER"""\n\n[ble]\nenabled = true\n')
        self.assertEqual("F13", mapping["JP_MINUSUNDER"])
        self.assertIn('trigger = "F13"', out)
        self.assertIn('negative_output = "Minus"', out)
        self.assertIn('positive_output = "WM(International1, LShift)"', out)
        self.assertLess(out.index("[behavior.fork]"), out.index("[ble]"))

    def test_rejects_reserved_trigger_collision(self):
        with self.assertRaises(ValueError):
            mod.transform('[keymap]\nkeys = """F13 JP_EQUALPLUS"""\n')

    def test_stable_trigger_mapping(self):
        out, mapping = mod.transform('[keymap]\nkeys = """JP_QUOTEDQUOTE JP_YENPIPE"""\n')
        self.assertEqual("F16", mapping["JP_QUOTEDQUOTE"])
        self.assertEqual("F17", mapping["JP_YENPIPE"])
        self.assertIn("F16 F17", out)

    def test_merges_existing_forks(self):
        source = '''[keymap]
keys = """JP_YENPIPE"""

[behavior.fork]
forks = [
  { trigger = "A", negative_output = "A", positive_output = "B", match_any = "LShift" },
]
'''
        out, _ = mod.transform(source)
        self.assertEqual(1, out.count("[behavior.fork]"))
        self.assertNotIn("JP_YENPIPE", out)
        self.assertIn('trigger = "F17"', out)

    def test_runtime_abi_emits_all_morph_triggers(self):
        out, mapping = mod.transform('[keymap]\nkeys = """JP_AT"""\n', runtime_abi=True)
        self.assertEqual(set(mod.MORPHS), set(mapping))
        for number in range(13, 21):
            self.assertIn(f'trigger = "F{number}"', out)
        self.assertIn("LeftBracket", out)

    def test_runtime_abi_rejects_any_reserved_trigger_collision(self):
        with self.assertRaises(ValueError):
            mod.transform('[keymap]\nkeys = """F20 JP_AT"""\n', runtime_abi=True)


if __name__ == "__main__":
    unittest.main()
