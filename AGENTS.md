# AGENTS.md

Guidance for coding agents working on `gpg-key2typ`.

## Project

`gpg-key2typ` renders OpenPGP keys from a GnuPG keyring as keysigning
slips, written as Typst source. It is a single-file Python CLI (Python
3.9+, standard library only) and the generated document targets Typst
0.13+. Read `README.md` for usage and options.

The slip layout follows Debian signing-party's `gpg-key2ps(1)` (columns,
field positions, tiling), but the printed labels deliberately follow gpg
itself: curve names (`ed25519`, `cv25519`), UTC `YYYY-MM-DD` creation
dates, and capability flags (`[SC]`, `[E]`). Do not "restore" gpg-key2ps
output; the deviations are documented in the READMEs.

## Commands

Use the justfile recipes rather than invoking tools directly:

- `just test` - unit tests (`python3 -m unittest discover -s tests -v`)
- `just lint` - `ruff check --fix` and `ruff format` on `tests/` and `gpg-key2typ`
- `just slips <keys>` - run the CLI from the checkout, e.g. `just slips -s Alice > slips.typ`
- `just pdf <keys>` - render and compile to `slips.pdf` (needs Typst and gpg keys)
- `just install` - symlink the CLI into `~/.local/bin`

`just test` and `just lint` currently pass. `ruff.toml` sets line length
120 and Python 3.9 as the target.

## Layout

- `gpg-key2typ` - the whole CLI: gpg invocation, `--with-colons`
  parsing, slip layout, Typst document generation, argument parsing.
- `tests/test_gpg_key2typ.py` - unittest suite; loads the extensionless
  script with `SourceFileLoader` and drives a fake `gpg` through
  `GNUPGBIN`, so no real keyring is needed.
- `tests/fixtures/revoked.txt` - a hand-written `gpg --with-colons`
  listing used by the tests.
- `docs/key-signing-party.md`, `docs/key-signing-party.zh.md` - the
  keysigning party process guide shipped with the tool.
- `justfile`, `ruff.toml`, `.gitignore` - tooling. Generated `slips.typ`
  and `*.pdf` files are gitignored.

## Conventions

- Document user-visible behavior in both `README.md` and `README.zh.md`,
  and keep the two `docs/key-signing-party*.md` guides in sync the same
  way.
- Keep `gpg-key2typ` a single standard-library-only file; do not add
  runtime dependencies or split it into a package.
- Fixture and test data must use real `gpg --with-colons` field
  positions: capabilities are field 12 and the ECC curve name is field
  17 (1-based). Hand-written lines with shifted fields have caused
  subtle test bugs.
- The Typst document tiles fixed-height slip blocks computed in Python;
  overlong text is condensed with a Typst `measure`/`scale` helper. An
  experiment that let Typst compute slip heights and rows was abandoned
  because grid rows did not grow reliably; keep the Python-side layout.
- Session logs live in `.agents/sessions/` (gitignored in the main tree;
  past logs are kept on the `sessions` branch).

## Upstream reference

The reference `gpg-key2ps` Perl source is in Debian's signing-party
package. Salsa serves web pages behind an Anubis proof-of-work
challenge, so `webfetch` and similar tools return "I Challenge Thee";
`git clone https://salsa.debian.org/signing-party-team/signing-party.git`
works, as does unpacking `apt-get download signing-party`.
