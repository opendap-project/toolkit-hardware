"""Tests for the schematic and symbol part of bin/odapkit-craft (tools/sch-craft-check.py).

Fixtures in tests/fixtures/craft-sch/: good/ is a copy of kicad-lib's examples/load-switch and must
pass every check and reach Q4; bad/ and bad.kicad_sym are written from it by make_fixture.py and must
fail every check. The S-expression checks need only Python; the ERC fold and the netlist check need
kicad-cli (KiCad 10) and are skipped without it.

Run from the repository root: python3 -m unittest discover tests
"""
import json
import os
import shutil
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "bin", "odapkit-craft")
FIX = os.path.join(HERE, "fixtures", "craft-sch")
APP = os.environ.get("KICAD_APP", "/Applications/KiCad/KiCad.app")
HAVE_CLI = bool(os.path.exists(os.path.join(APP, "Contents", "MacOS", "kicad-cli")) or shutil.which("kicad-cli"))
GOOD = os.path.join(FIX, "good", "load-switch.kicad_sch")
BAD = os.path.join(FIX, "bad", "load-switch.kicad_sch")

# Every check the script runs on a schematic, with its level; each passes on good and fails on bad.
SCHEMATIC = {
    "CRAFT-80": "Q1", "CRAFT-81": "Q2", "CRAFT-82": "Q1", "CRAFT-84": "Q1", "CRAFT-85": "Q1",
    "CRAFT-86": "Q2", "CRAFT-100": "Q1", "CRAFT-101": "Q2", "CRAFT-102": "Q2", "CRAFT-103": "Q2",
    "CRAFT-110": "Q2", "CRAFT-111": "Q3", "CRAFT-112": "Q1", "CRAFT-113": "Q2", "CRAFT-114": "Q3",
    "CRAFT-115": "Q2", "CRAFT-116": "Q3", "CRAFT-133": "Q2", "CRAFT-141": "Q2", "CRAFT-143": "Q2",
    "CRAFT-144": "Q3", "CRAFT-145": "Q1", "CRAFT-146": "Q3", "CRAFT-147": "Q1", "CRAFT-148": "Q3",
    "CRAFT-150": "Q1", "CRAFT-151": "Q2", "CRAFT-152": "Q1", "CRAFT-153": "Q2", "CRAFT-154": "Q2",
    "CRAFT-155": "Q2", "CRAFT-157": "Q3", "CRAFT-158": "Q1", "CRAFT-172": "Q3", "CRAFT-173": "Q2",
    "CRAFT-176": "Q2",
}
SYMBOL = {
    "CRAFT-121": "Q2", "CRAFT-122": "Q1", "CRAFT-123": "Q2", "CRAFT-124": "Q1", "CRAFT-125": "Q1",
    "CRAFT-126": "Q2", "CRAFT-127": "Q3", "CRAFT-128": "Q2", "CRAFT-129": "Q2", "CRAFT-130": "Q1",
    "CRAFT-131": "Q3", "CRAFT-140": "Q1",
}
NEEDS_CLI = {"CRAFT-152", "CRAFT-157"}  # ERC and the netlist


def run(*args):
    return subprocess.run([TOOL, *args], capture_output=True, text=True)


def results(report):
    return {r["id"]: r for lv in report["levels"].values() for r in lv}


class SchematicCraft(unittest.TestCase):
    def check(self, path, *extra):
        r = run("check", "--json", *extra, path)
        self.assertIn(r.returncode, (0, 1), r.stderr)
        return r.returncode, json.loads(r.stdout)

    @unittest.skipIf(not HAVE_CLI, "kicad-cli not found")
    def test_good_passes_everything(self):
        code, report = self.check(GOOD)
        got = results(report)
        for cid, level in {**SCHEMATIC, **SYMBOL}.items():
            self.assertEqual(got[cid]["level"], level, cid)
            self.assertEqual(got[cid]["status"], "pass", (cid, got[cid]["findings"]))
        self.assertEqual(got["ERC"]["status"], "pass", got["ERC"]["findings"])
        self.assertEqual(report["reached"], "Q4")
        self.assertEqual(report["target"], "Q4")  # from load-switch.craft.toml
        self.assertEqual(code, 0)

    def test_good_without_erc(self):
        code, report = self.check(GOOD, "--no-erc")
        got = results(report)
        for cid in set(SCHEMATIC) - NEEDS_CLI:
            self.assertEqual(got[cid]["status"], "pass", (cid, got[cid]["findings"]))
        self.assertNotIn("ERC", got)

    @unittest.skipIf(not HAVE_CLI, "kicad-cli not found")
    def test_bad_fails_everything(self):
        code, report = self.check(BAD)
        got = results(report)
        for cid in {**SCHEMATIC, **SYMBOL}:
            self.assertEqual(got[cid]["status"], "fail", cid)
        self.assertEqual(got["ERC"]["level"], "Q0")
        self.assertEqual(got["ERC"]["status"], "fail")  # unconnected wires and pins
        self.assertEqual(got["CRAFT-152"]["enforcement"], "ERC")
        self.assertIsNone(report["reached"])  # a Q0 item fails
        self.assertEqual(code, 1)

    def test_bad_without_erc(self):
        code, report = self.check(BAD, "--no-erc")
        got = results(report)
        for cid in set(SCHEMATIC) - NEEDS_CLI:
            self.assertEqual(got[cid]["status"], "fail", cid)
        self.assertEqual(report["reached"], "Q0")
        self.assertEqual(code, 1)

    def test_target_and_debt(self):
        _, report = self.check(BAD, "--no-erc", "--target", "Q0")
        self.assertTrue(report["target_met"])
        self.assertIn("CRAFT-111", report["debt"])
        _, report = self.check(GOOD, "--no-erc", "--target", "Q1")
        self.assertEqual(report["debt"], [])

    def test_symbol_libraries(self):
        code, report = self.check(os.path.join(FIX, "good", "example.kicad_sym"))
        got = results(report)
        self.assertEqual(set(got), set(SYMBOL))
        for cid in SYMBOL:
            self.assertEqual(got[cid]["status"], "pass", (cid, got[cid]["findings"]))
        self.assertEqual(code, 0)
        code, report = self.check(os.path.join(FIX, "bad.kicad_sym"))
        got = results(report)
        for cid in SYMBOL:
            self.assertEqual(got[cid]["status"], "fail", cid)
        self.assertEqual(code, 1)

    def test_usage(self):
        self.assertEqual(run("check", "--target", "Q9", GOOD).returncode, 2)
        self.assertEqual(run("check", os.path.join(FIX, "missing.kicad_sch")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
