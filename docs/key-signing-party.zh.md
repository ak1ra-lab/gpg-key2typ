# Key signing party

[English](key-signing-party.md) · 简体中文

[gpg-key2typ](../README.zh.md) 的流程文档：线下怎么交换纸条，以及回家认证之前要核对什么。

## 两阶段的 keysigning 流程

key signing party 的意义，就是当面确认某个指纹确实属于出示它的人（或化名）。OpenPGP 认证本身等回家再做，用私钥签——最好用离线的、只做认证的主密钥。这样拆开，私钥不用出现在活动现场（现场机器未必干净），线下环节也简单，一张卡片、一支笔就够了。

```mermaid
flowchart TD
    subgraph P1["阶段一 · 线下"]
        A1["交换纸条，<br/>核对彼此的指纹"]
        A2{"UID 是真名？"}
        A3["核对政府签发的<br/>带照片证件"]
        A4["不查法定证件"]
        A5["约定沟通渠道"]
        A6["记下指纹、渠道、<br/>核对内容、日期、活动"]
        A1 --> A2
        A2 -->|是| A3
        A2 -->|否，化名| A4
        A3 --> A5
        A4 --> A5
        A5 --> A6
    end

    subgraph P2["阶段二 · 在家"]
        B1["获取完整公钥"]
        B2["再核对一遍指纹"]
        B3["验证私钥持有<br/>（challenge–response）"]
        B4["验证渠道持有<br/>（经渠道应答）"]
        B5["用离线主密钥<br/>认证核对过的 UID"]
        B6["把签好的证书<br/>私下发给对方"]
        B7["对方导入后<br/>决定是否公开"]
        B1 --> B2 --> B3 --> B4 --> B5 --> B6 --> B7
    end

    A6 --> B1
```

### 阶段一 —— 线下

1. 准备好指纹纸条（`gpg-key2ps`，或者用本仓库的 [`gpg-key2typ`](../README.zh.md) 以 Typst 渲染）；自己的指纹要熟到能核对。
2. 和每个人交换纸条。你读出自己的指纹，对方跟着核对；双方各自记下（或扫描）对方的指纹。一定核对完整指纹——扫出来的 QR 码顶多只是顺手用的。
3. UID 是真名，就按活动或双方约定的签名规则核对政府签发的带照片证件；UID 是化名，不用查证件，改成约定一个能找到这个化名的在线渠道（Telegram、Matrix、Signal、电子邮件等）。
4. 把核对过的东西记下来：指纹、渠道、核对内容、日期、活动。按名单进行的活动，就在打印的名单上勾选 "Fingerprint OK" 和 "ID OK"。
5. 私钥留在家里。这一步不用电脑，也不用联网。

```mermaid
sequenceDiagram
    autonumber
    actor A as Alice
    actor B as Bob

    Note over A,B: 线下 · 离线 · 不用电脑，不碰私钥
    A->>B: 递交纸条
    B->>A: 递交纸条
    A->>B: 我读指纹，你核对
    B->>A: 我读指纹，你核对
    opt 真名 UID
        A->>B: 出示政府签发的带照片证件
        B->>A: 出示政府签发的带照片证件
    end
    opt 化名 UID
        A->>B: 约定 Telegram / Matrix / Signal / 电子邮件
        B->>A: 约定 Telegram / Matrix / Signal / 电子邮件
    end
    Note over A,B: 双方记下指纹、渠道、核对内容、日期、活动
```

如果你们本来就在某个已验证的渠道上认识（比如核对过 Signal 安全码，或者长期通信），线下这步可以缩到只交换、核对指纹——但阶段二的检查还是得做。跳过线下环节也不是不行，只是那样就不算 key signing party 了。

### 阶段二 —— 在家

1. 从可靠来源拿完整公钥：通过已验证的渠道直接向本人要，或者从 keyserver 下载。然后拿**完整指纹**和阶段一的记录比对。来源可以不信，指纹必须信。
2. 用 challenge–response 验证对方持有私钥：用对方的公钥加密一个新的随机挑战，经已验证渠道发过去，要求把明文发回来。recipient 填阶段一核对过的主密钥指纹即可，GnuPG 会自己挑一个可加密的 subkey。如果更看重签名能力，也可以请对方用签名 subkey 对挑战签名（见下面的注意事项）。
3. 验证渠道持有：应答必须从阶段一约定的渠道回来。这能说明密钥主人还握着那个渠道——化名 UID 之所以能绑到密钥上，靠的就是这一步。
4. 只认证你确实核对过绑定关系的 User ID，在离线环境用主密钥签（例如 `gpg --ask-cert-level --sign-key <fingerprint>`，或者用 `gpg --quick-sign-key <fingerprint> '<uid pattern>'` 挑单个 UID）。认证级别和核对程度要对得上。
5. 把认证（或更新后的证书）导出来，通过已验证渠道私下发给本人，由本人决定要不要公开。没有同意，别把别人的密钥传上 keyserver。

```mermaid
sequenceDiagram
    autonumber
    actor A as Alice（签名方）
    participant S as 公钥来源
    actor B as Bob（密钥所有者）
    participant K as 离线主密钥

    A->>S: 获取 Bob 的公钥
    S-->>A: 公钥
    A->>A: 和阶段一的记录比对指纹
    A->>B: 加密的挑战，经已验证渠道发送
    B->>B: 用私钥解密
    B-->>A: 经同一渠道返回
    A->>A: 私钥持有、渠道持有都确认
    A->>K: 认证 Bob 核对过的 UID
    K-->>A: 认证签名
    A->>B: 签好的证书，私下发送
    B->>B: 导入后决定是否公开
```

### 什么绑定了什么

```mermaid
flowchart LR
    person(("人 / 化名"))
    fp["指纹"]
    ch["沟通渠道"]
    key["公钥"]

    person -->|"阶段一 · 线下"| fp
    person -->|"阶段一 · 交换<br/>阶段二 · 应答"| ch
    fp -->|"阶段二 · 核对指纹"| key
    ch -->|"阶段二 · challenge–response"| key
```

| 绑定 | 建立于 | 靠什么验证 |
| --- | --- | --- |
| 人 / 化名 ↔ 指纹 | 阶段一（线下） | 带照片证件，或约定某个渠道 |
| 人 / 化名 ↔ 渠道 | 阶段一（交换）+ 阶段二（应答） | 经该渠道的 challenge–response |
| 指纹 ↔ 公钥 | 阶段二 | 本地比对指纹 |
| 公钥 ↔ 私钥 | 阶段二 | 解密挑战（加密 subkey） |

### 注意事项

- **私钥持有证明止步于 subkey。** 挑战是用对方的公钥加密的，但只有加密 subkey 的私钥能解开，所以证明的是对方握有*那个 subkey* 的私钥，而不是签发认证的主密钥。这通常是可以接受的；要求更高的话，可以请对方用主密钥重新签一次。签名 subkey 做的签名也只能证明那个 subkey，证明不了主密钥的私钥。
- **一把 key 只有一个要核对的指纹。** 阶段一交换、阶段二比对的都是主密钥的指纹。subkey 也有自己的指纹，但上面没有 User ID；它们与主密钥的绑定由主密钥签发的 subkey binding signature 保证，不用逐个核对。
- **认证按 UID 分别签。** OpenPGP 认证由主密钥对单个 User ID 签发。只认证你确实核对过绑定关系的 UID——回信的邮箱、渠道有应答的化名、证件上的姓名。
- **指纹长度不一样。** 纸条按 40 位十六进制字符的 v4 指纹（SHA-1）排版，这是最常见的情形。v6 密钥（[RFC 9580](https://www.rfc-editor.org/rfc/rfc9580.html)）是 64 位（SHA-256）；`gpg-key2typ` 会完整打印，但一行会很长，用 `-1`（一栏）给它留足空间。`--rfc4880bis` 草案里的实验性 v5 密钥长度一样。
- **公不公开由本人决定。** 没有同意，别把他人的密钥或你的认证传上 keyserver。[keys.openpgp.org](https://keys.openpgp.org/about/faq) 默认不传播第三方认证（只传播第一方自证的），所以在 key signing party 上签的名不会经它扩散；传统 keyserver 和项目 keyring（比如 Debian 的）另说。
- **认证可以撤销。** 事后发现核对错了，就撤销认证（`gpg --edit-key` → `revsig`）；自己密钥的吊销证书也要收好。

## 自动化工具（超出本文档范围）

[`signing-party`](https://salsa.debian.org/signing-party-team/signing-party) 软件包里的 `caff` 等工具可以简化聚会之后的部分工作。具体用法超出本文档的范围，想用的话可以查阅 [`caff(1)`](https://manpages.debian.org/unstable/signing-party/caff.1.en.html) 等文档。

## 参考资料

背景：

- [The Keysigning Party HOWTO](https://www.cryptnet.net/fdp/crypto/keysigning_party/en/keysigning_party.html) —— 经典指南，含 Zimmermann–Sassaman 方法。
- [Wikipedia：Key signing party](https://en.wikipedia.org/wiki/Key_signing_party)
- [Wikipedia：Zimmermann–Sassaman key-signing protocol](https://en.wikipedia.org/wiki/Zimmermann%E2%80%93Sassaman_key-signing_protocol)

实践经验：

- [Debian：Keysigning](https://www.debian.org/events/keysigning.en.html) —— 怎么组织一场 keysigning。
- [Debian Wiki：Keysigning](https://wiki.debian.org/Keysigning) 和 [Keysigning/Offers](https://wiki.debian.org/Keysigning/Offers)
- [DebConf 10 的 keysigning 示例](https://people.debian.org/~anibal/ksp-dc10/ksp-dc10.html)

工具：

- [`signing-party`](https://salsa.debian.org/signing-party-team/signing-party) —— `caff`、`gpgparticipants`、`gpg-key2ps` 等。
- [`gpg-key2typ`](../README.zh.md) —— 本仓库；同样的纸条，Typst 输出。
- [`caff(1)`](https://manpages.debian.org/unstable/signing-party/caff.1.en.html)、[`gpgparticipants(1)`](https://manpages.debian.org/unstable/signing-party/gpgparticipants.1.en.html)、[`gpg-key2ps(1)`](https://manpages.debian.org/unstable/signing-party/gpg-key2ps.1.en.html)
- [Debian 名片模板](https://www.debian.org/events/materials/business-cards/) —— 指纹纸条之外的另一条路。

规范与 keyserver：

- [GnuPG 手册：OpenPGP Key Management](https://gnupg.org/documentation/manuals/gnupg/OpenPGP-Key-Management.html)
- [RFC 9580 —— OpenPGP](https://www.rfc-editor.org/rfc/rfc9580.html)
- [keys.openpgp.org FAQ](https://keys.openpgp.org/about/faq) —— 为什么默认不传播第三方认证。
