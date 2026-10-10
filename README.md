# gpg-key2typ

[![GitHub](https://img.shields.io/badge/GitHub-ak1ra--lab%2Fpgp--info--card-181717?logo=github&logoColor=white)](https://github.com/ak1ra-lab/pgp-info-card)
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
content, the positions inside a slip, and the command line options follow the
original.

```sh
./gpg-key2typ -p a4 Alice Bob > slips.typ
typst compile slips.typ slips.pdf

# or straight to a PDF
./gpg-key2typ Alice Bob | typst compile - slips.pdf
```

The output is one landscape sheet filled with identical slips — two columns of
slips by default, one with `-1` — each key block showing

```text
pub eddsa255/DF95CC16 1791606480
Key fingerprint = 21A3 835B 8A4C 5C82 8F8A  218D 4B8C 03A2 DF95 CC16
uid Alice Example <alice@example.org>
```

plus one `uid` line per User ID and, with `-s`, one `sub` line per subkey.
Print it, cut along the slip borders, and hand the slips out at the party.

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
| `-o, --output FILE` | Write the Typst source to `FILE` instead of stdout *(extension)*. |
| `-s, --show-subkeys` | Print subkey information on the slips. |
| `-r, --revoked-style ST` | How to mark revoked User IDs and subkeys: `hide` (default), `show`, `grey`, `note` (append `[revoked]`), or `strike`. |
| `-1` | Print one column of slips instead of two; useful for long User IDs. |
| `--qr` | Add a QR code with the fingerprint to each key block *(extension)*. |
| `-h, --help` | Print usage and exit. |
| `-v, --version` | Print version and exit. |

The key arguments are the same patterns `gpg --list-keys` accepts: a key ID,
a fingerprint, or a (partial) name. Environment variables: `GNUPGBIN` (gpg
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

- Typst source instead of PostScript, written to stdout; `-o` and `--qr` are
  extensions, everything else mirrors the original options.
- The default paper is always A4; gpg-key2ps follows libpaper's
  `/etc/papersize`. Common names are built in, and `paperconf` resolves other
  names when it is installed.
- User IDs stay UTF-8; gpg-key2ps re-encodes them as Latin-1.
- v6 fingerprints (64 hex digits, [RFC 9580](https://www.rfc-editor.org/rfc/rfc9580.html))
  are grouped like v4 ones; gpg-key2ps only knows v3 and v4.
- A User ID's value sits right after the `uid` label (x = 70 pt) instead of
  gpg-key2ps's far-right column (x = 200 pt), so long User IDs keep the full
  line width; text that would still leave a slip is condensed horizontally
  until it fits, where gpg-key2ps clips it at the column edge. `-1` gives
  long lines the most room.
- The separator line between keys counts towards the slip height, a slip that
  does not fit the sheet warns on stderr, and the last slip is not clipped.
- The creation date is printed as a Unix timestamp — deliberately, because
  that is what gpg-key2ps prints.
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
