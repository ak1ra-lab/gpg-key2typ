"""Tests for the gpg-key2typ CLI."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import io
import os
import stat
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_LOADER = importlib.machinery.SourceFileLoader("gpg_key2typ", str(ROOT / "gpg-key2typ"))
_SPEC = importlib.util.spec_from_loader(_LOADER.name, _LOADER)
gpg_key2typ = importlib.util.module_from_spec(_SPEC)
sys.modules[_LOADER.name] = gpg_key2typ
_LOADER.exec_module(gpg_key2typ)

FIXTURE = (Path(__file__).resolve().parent / "fixtures" / "revoked.txt").read_bytes()
A4 = gpg_key2typ.Paper(gpg_key2typ.mm_to_pt(210.0), gpg_key2typ.mm_to_pt(297.0))


def parse(revoked_style: str = "hide", show_subkeys: bool = False):
    return gpg_key2typ.parse_keys(FIXTURE, revoked_style, show_subkeys)


def render(revoked_style: str = "hide", show_subkeys: bool = False, qr: bool = False):
    keys = parse(revoked_style, show_subkeys)
    layout = gpg_key2typ.compute_layout(keys, A4, False, qr, io.StringIO())
    return gpg_key2typ.render_document(keys, layout, revoked_style, qr), layout


class FingerprintTests(unittest.TestCase):
    def test_v4(self):
        self.assertEqual(
            gpg_key2typ.format_fingerprint("21A3835B8A4C5C828F8A218D4B8C03A2DF95CC16"),
            "21A3 835B 8A4C 5C82 8F8A  218D 4B8C 03A2 DF95 CC16",
        )

    def test_v3(self):
        self.assertEqual(
            gpg_key2typ.format_fingerprint("0123456789ABCDEF0123456789ABCDEF"),
            "01 23 45 67 89 AB CD EF  01 23 45 67 89 AB CD EF",
        )

    def test_v6(self):
        fingerprint = "0123456789ABCDEF" * 4
        formatted = gpg_key2typ.format_fingerprint(fingerprint)
        self.assertEqual(formatted.count("  "), 1)
        self.assertEqual(
            formatted.replace("  ", " ").split(),
            [fingerprint[i : i + 4] for i in range(0, 64, 4)],
        )


class ParseTests(unittest.TestCase):
    def test_hides_revoked_lines_by_default(self):
        keys = parse()
        self.assertEqual(len(keys), 1)
        self.assertEqual([line.kind for line in keys[0].lines], ["pub", "fpr", "uid"])
        self.assertEqual(keys[0].fingerprint, "0123456789ABCDEF0123456789ABCDEF01234567")

    def test_show_subkeys_keeps_revoked_subkeys(self):
        keys = parse(revoked_style="note", show_subkeys=True)
        self.assertEqual(
            [line.kind for line in keys[0].lines],
            ["pub", "fpr", "uid", "uid", "sub", "sub"],
        )
        self.assertEqual([line.revoked for line in keys[0].lines].count(True), 2)

    def test_pub_line_fields(self):
        runs = parse()[0].lines[0].runs
        self.assertEqual(
            [(run.x, run.text) for run in runs],
            [
                (gpg_key2typ.LABEL_X_PT, "pub"),
                (gpg_key2typ.VALUE_X_PT, "rsa4096/89ABCDEF"),
                (gpg_key2typ.DATE_X_PT, "1577836800"),
            ],
        )

    def test_escaped_utf8_uid(self):
        output = (
            b"pub:u:255:22:4B8C03A2DF95CC16:1577836800:::u:::cC:::::ed25519:::0:\n"
            b"fpr:::::::::21A3835B8A4C5C828F8A218D4B8C03A2DF95CC16:\n"
            b"uid:u::::1577836800::HASH::Jos\\xc3\\xa9 <jose@example.org>::::::::::0:\n"
        )
        keys = gpg_key2typ.parse_keys(output, "hide", False)
        uid = keys[0].lines[-1].runs[-1]
        self.assertEqual(uid.text, "José <jose@example.org>")


class RenderTests(unittest.TestCase):
    def test_grid_tiles_the_slips(self):
        document, layout = render(revoked_style="note", show_subkeys=True)
        self.assertIn("#grid(columns: (slip-w, slip-w)", document)
        self.assertIn(f"..range({layout.slip_count}).map(_ => slip)", document)
        self.assertIn('text("pub")', document)
        self.assertIn(" [revoked]", document)

    def test_one_column(self):
        keys = parse()
        layout = gpg_key2typ.compute_layout(keys, A4, True, False, io.StringIO())
        document = gpg_key2typ.render_document(keys, layout, "hide", False)
        self.assertIn("#grid(columns: (slip-w),", document)

    def test_qr_lives_in_the_left_gutter(self):
        document, _ = render(qr=True)
        self.assertIn('#import "@preview/qrypst:0.1.1": qr', document)
        self.assertIn('qr("0123456789ABCDEF0123456789ABCDEF01234567", module: ', document)
        self.assertIn(f"place(top + left, dx: {gpg_key2typ.QR_X_PT:g}pt", document)

    def test_qr_is_optional(self):
        document, _ = render()
        self.assertNotIn("qrypst", document)

    def test_long_lines_are_condensed_to_fit(self):
        document, _ = render()
        self.assertIn("#let fit(avail, body)", document)
        self.assertIn("scale(x: 100% * (avail / natural)", document)
        # User IDs start in the summary column, right after the label.
        self.assertIn(
            'put(50pt, 18.0000pt, text("uid")) + put(70pt, 329.1024pt, text("Test User <test@example.org>"))',
            document,
        )
        self.assertNotIn("put-uid", document)

    def test_key_summary_stops_before_the_date_column(self):
        output = (
            b"pub:-:255:22:762F67A0B2C39DE4:1742842581:1995130581::-:::scSC:::::"
            b"ed25519:::0:\n"
            b"fpr:::::::::41587F7DB8C774BCCF131416762F67A0B2C39DE4:\n"
        )
        keys = gpg_key2typ.parse_keys(output, "hide", False)
        layout = gpg_key2typ.compute_layout(keys, A4, False, False, io.StringIO())
        document = gpg_key2typ.render_document(keys, layout, "hide", False)
        # `eddsa255/B2C39DE4` is wider than the 80pt column between x = 70pt
        # and the date at x = 150pt, so it is condensed to 78pt instead of
        # running into the date.
        self.assertIn(
            'put(70pt, 78.0000pt, text("eddsa255/B2C39DE4")) + put(150pt, 249.1024pt, text("1742842581"))',
            document,
        )

    def test_qr_version_grows_with_the_fingerprint(self):
        v4_module, v4_box = gpg_key2typ.qr_geometry("A" * 40)
        v6_module, v6_box = gpg_key2typ.qr_geometry("A" * 64)
        self.assertAlmostEqual(v4_box, gpg_key2typ.QR_SIZE_PT, places=2)
        self.assertAlmostEqual(v6_box, gpg_key2typ.QR_SIZE_PT, places=2)
        self.assertLess(v6_module, v4_module)


class CliTests(unittest.TestCase):
    def run_cli(self, argv, env=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, env or {}):
            code = gpg_key2typ.run(argv, stdout, stderr)
        return code, stdout.getvalue(), stderr.getvalue()

    def fake_gpg_env(self, tmp: str) -> dict[str, str]:
        fake = Path(tmp) / "fake-gpg"
        fake.write_text('#!/bin/sh\ncat "$FAKE_GPG_DATA"\n', encoding="utf-8")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
        data = Path(tmp) / "keys.txt"
        data.write_bytes(FIXTURE)
        return {"GNUPGBIN": str(fake), "FAKE_GPG_DATA": str(data)}

    def test_no_arguments_prints_usage(self):
        code, _, stderr = self.run_cli([])
        self.assertEqual(code, 1)
        self.assertIn("usage:", stderr)
        self.assertIn("the following arguments are required: keyid-or-name", stderr)

    def test_unknown_revoked_style(self):
        code, _, stderr = self.run_cli(["-r", "nope", "Test User"])
        self.assertEqual(code, 1)
        self.assertIn("invalid choice: 'nope'", stderr)

    def test_help(self):
        code, stdout, stderr = self.run_cli(["--help"])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("usage:", stdout)
        self.assertIn("--paper-size", stdout)

    def test_version(self):
        code, stdout, _ = self.run_cli(["--version"])
        self.assertEqual(code, 0)
        self.assertIn(f"{gpg_key2typ.PROGRAM} {gpg_key2typ.VERSION}", stdout)

    def test_unknown_paper_size(self):
        code, _, stderr = self.run_cli(["-p", "nosuchpaper", "Test User"])
        self.assertEqual(code, 1)
        self.assertIn('unknown paper size "nosuchpaper"', stderr)

    def test_default_paper_is_a4(self):
        self.assertEqual(
            gpg_key2typ.resolve_paper(None),
            gpg_key2typ.Paper(gpg_key2typ.mm_to_pt(210.0), gpg_key2typ.mm_to_pt(297.0)),
        )

    def test_end_to_end_with_fake_gpg(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, stdout, stderr = self.run_cli(["-p", "a4", "Test User"], env=self.fake_gpg_env(tmp))
        self.assertEqual(code, 0, stderr)
        self.assertIn("width: 297.000mm", stdout)
        self.assertIn("height: 210.000mm", stdout)
        self.assertIn("#grid(columns: (slip-w, slip-w)", stdout)

    def test_end_to_end_defaults_to_a4(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, stdout, stderr = self.run_cli(["Test User"], env=self.fake_gpg_env(tmp))
        self.assertEqual(code, 0, stderr)
        self.assertIn("width: 297.000mm", stdout)
        self.assertIn("height: 210.000mm", stdout)

    def test_options_may_follow_the_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, stdout, stderr = self.run_cli(["Test User", "-p", "a4", "-1"], env=self.fake_gpg_env(tmp))
        self.assertEqual(code, 0, stderr)
        self.assertIn("#grid(columns: (slip-w),", stdout)

    def test_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "slips.typ"
            code, stdout, stderr = self.run_cli(
                ["-p", "a4", "-o", str(target), "Test User"],
                env=self.fake_gpg_env(tmp),
            )
            self.assertEqual(code, 0, stderr)
            self.assertEqual(stdout, "")
            self.assertIn("#grid(", target.read_text(encoding="utf-8"))

    def test_no_public_key_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = self.fake_gpg_env(tmp)
            Path(env["FAKE_GPG_DATA"]).write_bytes(b"")
            code, _, stderr = self.run_cli(["Test User"], env=env)
        self.assertEqual(code, 1)
        self.assertIn("No public key found.", stderr)


if __name__ == "__main__":
    unittest.main()
