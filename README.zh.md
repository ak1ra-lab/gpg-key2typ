# gpg-key2typ

[![GitHub](https://img.shields.io/badge/GitHub-ak1ra--lab%2Fgpg--key2typ-181717?logo=github&logoColor=white)](https://github.com/ak1ra-lab/gpg-key2typ)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Typst 0.13+](https://img.shields.io/badge/Typst-0.13%2B-239DAD?logo=typst&logoColor=white)](https://typst.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) · 简体中文

`gpg-key2typ` 把 GnuPG 密钥串里的 OpenPGP 密钥渲染成 key signing party 用的指纹纸条：一整页带边框的小纸条，每张上都印着所请求密钥的指纹和 User ID。它是 Debian [signing-party](https://salsa.debian.org/signing-party-team/signing-party) 里 [`gpg-key2ps(1)`](https://manpages.debian.org/unstable/signing-party/gpg-key2ps.1.en.html) 的重实现，只是输出 [Typst](https://typst.app/) 源码而不是 PostScript。纸条的版式和命令行选项沿袭原版；日期、算法名和密钥用途标记则按 gpg 自己的写法打印。

```sh
./gpg-key2typ -p a4 Alice Bob > slips.typ
typst compile slips.typ slips.pdf

# 或者直接进 PDF
./gpg-key2typ Alice Bob | typst compile - slips.pdf

# 也可以直接从下载的密钥文件（或标准输入）读取，无需先导入：
./gpg-key2typ -i alice-pubkey.asc > slips.typ
curl -s https://example.org/alice.asc | ./gpg-key2typ -i - > slips.typ
```

输出是一张横向纸面，平铺着同一张纸条：默认两栏（`-1` 改为一栏），每个密钥块显示

```text
pub ed25519/DF95CC16 2026-10-10 [SC]
Key fingerprint = 21A3 835B 8A4C 5C82 8F8A  218D 4B8C 03A2 DF95 CC16
uid Alice Example <alice@example.org>
```

每个 User ID 一行 `uid`，加 `-s` 时每个子钥再加一行 `sub`（`sub cv25519/0FA1B2C3 2026-10-10 [E]`）。打印出来，沿纸条边框裁开，就可以在活动现场分发了。

## 运行要求

- Python 3.9 或更新（只用标准库）
- GnuPG（`PATH` 里的 `gpg`，或用 `GNUPGBIN` 指定）
- 用来编译输出的 [Typst](https://typst.app/) 0.13 或更新
- 可选：libpaper 的 `paperconf`，用于内置列表之外的纸张名

## 安装

```sh
install -m 755 gpg-key2typ ~/.local/bin
# 或者用 just：
just install
```

## 选项

| 选项 | 说明 |
| --- | --- |
| `-p, --paper-size NAME` | 纸张尺寸。常见名字（`a4`、`a3`、`a5`、`b5`、`letter`、`legal` 等）内置；装了 libpaper 的 `paperconf` 时，其它名字交给它解析。默认：`a4`。 |
| `-i, --input FILE` | 从 `FILE` 而不是密钥串读取密钥（`-` 表示标准输入），无需先导入（*扩展*）。 |
| `-o, --output FILE` | 把 Typst 源码写进 `FILE`，而不是标准输出（*扩展*）。 |
| `-s, --show-subkeys` | 在纸条上打印子钥信息。 |
| `-r, --revoked-style ST` | 如何标注已吊销的 User ID 和子钥：`hide`（默认）、`show`、`grey`、`note`（追加 `[revoked]`）、`strike`（划线）。 |
| `-1` | 只打一栏纸条，而不是两栏；User ID 很长时有用。 |
| `--qr` | 为每个密钥块添加指纹 QR 码（*扩展*）。 |
| `-h, --help` | 打印用法并退出。 |
| `-v, --version` | 打印版本并退出。 |

密钥参数的写法和 `gpg --list-keys` 一样：key ID、指纹或（部分）名字都行。`--input` 则改用 `gpg --show-keys` 从文件或标准输入列出密钥，不会把它们导入密钥串，因此不能和密钥参数同时使用。环境变量：`GNUPGBIN`（gpg 可执行文件，默认 `gpg`）、`GNUPGHOME`（密钥串位置，gpg 自己会读）、`PAPERSIZE`（libpaper 纸张名）。

## QR 码

gpg-key2ps 没有 QR 码，所以这里默认也不加。`--qr` 会在每个密钥块左侧的空白栏（本来就不印字的地方）放一个 QR 码，内容是去掉空格的指纹——正好是你下载密钥时要核对的那串字符串。QR 码由 Typst 包 [`@preview/qrypst:0.1.1`](https://typst.app/universe/package/qrypst/) 绘制，首次编译时 Typst 会下载它（之后走缓存）；含静默区整枚约 17 mm 见方。

有必要加 QR 码吗?没有必要——纸条的意义就是让指纹方便用眼睛核对，gpg-key2ps 也刻意止步于此。QR 码只是方便之后记录或复检指纹，不能替代开口核对；需要时再加 `--qr` 即可。

## 与原版的差异

- 输出 Typst 源码而不是 PostScript，写到标准输出；`-i`、`-o` 和 `--qr` 是扩展，其余选项与原版一致。
- 默认纸张固定为 A4；gpg-key2ps 跟随 libpaper 的 `/etc/papersize`。常见尺寸内置，装有 `paperconf` 时可解析其它名字。
- User ID 保留 UTF-8；gpg-key2ps 会把它们转成 Latin-1。
- 支持 v6 指纹（64 位十六进制，[RFC 9580](https://www.rfc-editor.org/rfc/rfc9580.html)），分组方式与 v4 一致；gpg-key2ps 只认 v3 和 v4。
- 密钥按 gpg 的叫法命名：`rsa4096`、`nistp256`，常见 ECC 密钥用曲线名 `ed25519`/`cv25519`；gpg-key2ps 打的是 `eddsa255`/`ecdh255`，其算法表之外的算法一概打 `xxx`。
- 创建日期打印为 `YYYY-MM-DD`（UTC，同 `gpg --list-keys`），不再是 gpg-key2ps 的原始 Unix 时间戳。
- 每把密钥末尾带上用途标记（`[SC]`、`[E]` 等），同 `gpg --list-keys`；gpg-key2ps 不打印用途。
- User ID 的值紧跟在 `uid` 标签之后（x = 70 pt），不再用 gpg-key2ps 的远端值栏（x = 200 pt），长 UID 因此能用满整行；若某一栏会压到下一栏（或超出纸条），就横向压缩使其放下（gpg-key2ps 会直接裁掉）。`-1` 能给长行留出最多空间。
- 密钥之间的分隔线计入纸条高度；纸条放不下整页时在 stderr 警告；最后一张纸条不会被裁掉。
- 原先 90 × 55 mm 名片版式及其 Typst 模板已移除；本项目只做指纹纸条这件事。

## Key signing party

纸条背后的流程——现场核对什么、回家认证前做什么——见[《Key signing party 指南》](docs/key-signing-party.zh.md)。

## 开发

`gpg-key2typ` 是单个无依赖的 Python 文件；测试直接加载它，并用假 `gpg` 驱动：

```sh
just test          # python3 -m unittest discover -s tests -v
just slips Alice   # 在仓库里直接跑 CLI
```

## 许可证

[MIT](LICENSE)
