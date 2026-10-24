"""Tests for bin/odapkit-stackup on the fixture in tests/fixtures/stackup (needs uv on PATH).

Run from the repository root: python3 -m unittest discover tests
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "bin", "odapkit-stackup")
FIXTURE = os.path.join(HERE, "fixtures", "stackup", "fixture.toml")
sys.path.insert(0, os.path.join(HERE, "..", "tools", "stackup"))


@unittest.skipIf(shutil.which("uv") is None, "uv not on PATH")
class Stackup(unittest.TestCase):
    def run_tool(self, *args):
        return subprocess.run([TOOL, *args], capture_output=True, text=True)

    def variant(self, old, new):
        with open(FIXTURE) as f:
            text = f.read()
        self.assertIn(old, text)
        fd, path = tempfile.mkstemp(suffix=".toml")
        with os.fdopen(fd, "w") as f:
            f.write(text.replace(old, new, 1))
        self.addCleanup(os.remove, path)
        return path

    def test_validate(self):
        r = self.run_tool("validate", "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rows = json.loads(r.stdout)["rows"]
        cohn = [x for x in rows if x["formula"] == "Cohn (exact)"]
        self.assertEqual(len(cohn), 3)
        self.assertTrue(all(abs(x["error_pct"]) < 0.5 for x in cohn))

    def test_fixture_check_passes(self):
        r = self.run_tool("check", FIXTURE, "--json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rep = json.loads(r.stdout)
        byname = {c["name"]: c for c in rep["classes"]}
        self.assertAlmostEqual(byname["MS50"]["z_ohm"], 50.0, delta=0.5)
        self.assertAlmostEqual(byname["MS90D"]["z_ohm"], 90.0, delta=0.9)
        self.assertAlmostEqual(byname["MS90D"]["zodd"] * 2, byname["MS90D"]["z_ohm"], delta=0.01)
        self.assertAlmostEqual(byname["SL50"]["z_ohm"], 50.0, delta=0.5)
        # thinner dielectric -> lower impedance; wider trace -> lower impedance
        sens = byname["MS50"]["corners"]["sensitivity"]
        self.assertLess(sens["dielectric"][0], 0)
        self.assertLess(sens["width"][1], 0)

    def test_microstrip_matches_hammerstad_jensen(self):
        import analytic
        z, _ = analytic.hammerstad_jensen_microstrip(172.5, 100, 35, 4.2)
        r = self.run_tool("check", FIXTURE, "--only", "MS50", "--no-corners", "--json")
        zs = json.loads(r.stdout)["classes"][0]["z_ohm"]
        self.assertLess(abs(zs - z) / z, 0.015)

    def test_design_reproduces_recorded_width(self):
        r = self.run_tool("design", FIXTURE, "--only", "SL50", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertAlmostEqual(json.loads(r.stdout)[0]["width_um"], 118.5, delta=1.0)

    def test_stale_and_off_target_fail(self):
        path = self.variant("width_um = 172.5\nz_ohm = 50.0", "width_um = 120.0\nz_ohm = 50.0")
        r = self.run_tool("check", path, "--only", "MS50", "--no-corners", "--json")
        self.assertEqual(r.returncode, 1)
        reason = json.loads(r.stdout)["classes"][0]["reason"]
        self.assertIn("outside", reason)
        self.assertIn("stale", reason)

    def test_distance_and_thickness_checks(self):
        path = self.variant("thickness_um = 100\n", "thickness_um = 120\n")
        r = self.run_tool("stack", path, "--json")
        self.assertEqual(r.returncode, 1)
        checks = json.loads(r.stdout)["checks"]
        self.assertFalse(checks[0]["ok"])
        self.assertEqual(checks[0]["value_um"], 120.0)

    def test_mirrored_reference(self):
        # a line referenced only from above (bottom side) is solved on the mirrored stack
        path = self.variant('layer = "L1"\nreference = ["L2"]', 'layer = "L4"\nreference = ["L3"]')
        r = self.run_tool("check", path, "--only", "MS50", "--no-corners", "--json")
        self.assertIn('"z_ohm"', r.stdout, r.stderr)

    def test_bad_file(self):
        path = self.variant("version = 1", "version = 2")
        self.assertEqual(self.run_tool("stack", path).returncode, 2)


if __name__ == "__main__":
    unittest.main()
