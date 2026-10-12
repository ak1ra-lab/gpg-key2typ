# gpg-key2typ

[![GitHub](https://img.shields.io/badge/GitHub-ak1ra--lab%2Fgpg--key2typ-181717?logo=github&logoColor=white)](https://github.com/ak1ra-lab/gpg-key2typ)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Typst 0.13+](https://img.shields.io/badge/Typst-0.13%2B-239DAD?logo=typst&logoColor=white)](https://typst.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

English · [简体中文](README.zh.md)

`gpg-key2typ` prints the OpenPGP keys in your GnuPG keyring as keysigning
slips: pages of small bordered slips, each carrying all requested keys'
fingerprints and User IDs. It is a reimplementation of
[`gpg-key2ps(1)`](https://manpages.debian.org/unstable/signing-party/gpg-key2ps.1.en.html)
from Debian's [signing-party](https://salsa.debian.org/signing-party-team/signing-party)
that writes [Typst](https://typst.app/) source instead of PostScript. The slip
geometry and the command line options follow the original; dates, algorithm
names, and key capability flags are printed the way gpg itself labels keys.

```sh
./gpg-key2typ -p a4 Alice Bob > slips.typ
typst compile slips.typ slips.pdf

# or straight to a PDF
./gpg-key2typ Alice Bob | typst compile - slips.pdf

# or from a downloaded key file (or stdin), without importing it:
./gpg-key2typ -i alice-pubkey.asc > slips.typ
curl -s https://example.org/alice.asc | ./gpg-key2typ -i - > slips.typ
```

The output is one landscape sheet filled with identical slips — two columns of
slips by default, one with `-1` — each key block showing

```text
pub ed25519/DF95CC16 2026-10-10 [SC]
Key fingerprint = 21A3 835B 8A4C 5C82 8F8A  218D 4B8C 03A2 DF95 CC16
uid Alice Example <alice@example.org>
```

plus one `uid` line per User ID and, with `-s`, one `sub` line per subkey
(`sub cv25519/0FA1B2C3 2026-10-10 [E]`). Print it, cut along the slip borders,
and hand the slips out at the party.

## Requirements

- Python 3.9 or later (standard library only)
- GnuPG (`gpg` in `PATH`, or point `GNUPGBIN` at another binary)
- [Typst](https://typst.app/) 0.13 or later to compile the generated document
- Optional: libpaper's `paperconf` for paper names beyond the built-in ones

## Install

```sh
install -m 755 gpg-key2typ ~/.local/bin
# or, with just:
just install
```

## Options

| Option | Description |
| --- | --- |
| `-p, --paper-size NAME` | Sheet size. Common names (`a4`, `a3`, `a5`, `b5`, `letter`, `legal`, …) are built in; other names are resolved with libpaper's `paperconf` when installed. Default: `a4`. |
| `-i, --input FILE` | Read keys from `FILE` instead of the keyring (`-` reads stdin), so they do not have to be imported first *(extension)*. |
| `-o, --output FILE` | Write the Typst source to `FILE` instead of stdout *(extension)*. |
| `-s, --show-subkeys` | Print subkey information on the slips. |
| `-r, --revoked-style ST` | How to mark revoked User IDs and subkeys: `hide` (default), `show`, `grey`, `note` (append `[revoked]`), or `strike`. |
| `-1` | Print one column of slips instead of two; useful for long User IDs. |
| `--qr` | Add a QR code with the fingerprint to each key block *(extension)*. |
| `-h, --help` | Print usage and exit. |
| `-v, --version` | Print version and exit. |

The key arguments are the same patterns `gpg --list-keys` accepts: a key ID,
a fingerprint, or a (partial) name. `--input` reads keys from a file or stdin
via `gpg --show-keys` instead, so they are listed without being imported, and
cannot be combined with key patterns. Environment variables: `GNUPGBIN` (gpg
binary, default `gpg`), `GNUPGHOME` (keyring; gpg reads it itself), and
`PAPERSIZE` (libpaper paper name).

## QR codes

gpg-key2ps has no QR codes, so they are off by default. `--qr` adds one to
each key block in the left gutter — where no text is printed — with the
fingerprint (no whitespace) as payload, exactly the string you compare against
the downloaded key. The QR is drawn by the Typst package
[`@preview/qrypst:0.1.1`](https://typst.app/universe/package/qrypst/), which
Typst downloads on first compile (or reuses from its cache); the symbol is
about 17 mm across including its quiet zone.

Is a QR necessary? No — a slip's job is to make the fingerprint easy to read
and compare by eye, and gpg-key2ps deliberately stops there. The QR is a
convenience for recording or re-checking the fingerprint later, not a
replacement for reading it aloud; `--qr` adds it when you want it.

## Differences from gpg-key2ps

- Typst source instead of PostScript, written to stdout; `-i`, `-o`, and
  `--qr` are extensions, the remaining options mirror the original.
- The default paper is always A4; gpg-key2ps follows libpaper's
  `/etc/papersize`. Common names are built in, and `paperconf` resolves other
  names when it is installed.
- User IDs stay UTF-8; gpg-key2ps re-encodes them as Latin-1.
- Keys are named the way gpg names them: `rsa4096`, `nistp256`, and the curve
  names `ed25519`/`cv25519` for the usual ECC keys, where gpg-key2ps prints
  `eddsa255`/`ecdh255` and `xxx` for algorithms outside its own table.
- The creation date is printed as `YYYY-MM-DD` (UTC), as in
  `gpg --list-keys`, instead of gpg-key2ps's raw Unix timestamp.
- Each key line ends with the key's capabilities (`[SC]`, `[E]`, …) as
  `gpg --list-keys` marks them; gpg-key2ps prints no capability information.
- v6 fingerprints (64 hex digits, [RFC 9580](https://www.rfc-editor.org/rfc/rfc9580.html))
  are grouped like v4 ones; gpg-key2ps only knows v3 and v4.
- A User ID's value sits right after the `uid` label (x = 70 pt) instead of
  gpg-key2ps's far-right column (x = 200 pt), so long User IDs keep the full
  line width; a field that would overrun the next column (or the slip edge)
  is condensed horizontally until it fits, where gpg-key2ps clips it at the
  column edge. `-1` gives long lines the most room.
- The separator line between keys counts towards the slip height, a slip that
  does not fit the sheet warns on stderr, and the last slip is not clipped.
- The earlier 90 × 55 mm business-card layout and its Typst template are gone;
  this tool covers the fingerprint-slip use case.

## The key signing party

The process around the slips — what to check in person and what to do at home
before certifying — is documented in the
[key signing party guide](docs/key-signing-party.md).

## Development

`gpg-key2typ` is a single Python file with no dependencies; the tests load it
directly and drive a fake `gpg`:

```sh
just test          # python3 -m unittest discover -s tests -v
just slips Alice   # run the CLI from the checkout
```

## License

[MIT](LICENSE)
