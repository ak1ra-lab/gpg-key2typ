# Key signing party

English · [简体中文](key-signing-party.zh.md)

Process guide for [`gpg-key2typ`](../README.md): the in-person exchange and the checks done at home before certifying.

## The two-phase keysigning process

A key signing party proves, in person, that a fingerprint belongs to the person (or pseudonym) presenting it. The OpenPGP certification itself is produced later, at home, with the private key — ideally an offline primary certification key. Splitting the process this way keeps the private key away from the event, where it could be exposed to compromised machines, and keeps the in-person part as simple as a fingerprint and a pen.

```mermaid
flowchart TD
    subgraph P1["Phase 1 · in person (offline)"]
        A1["Exchange slips,<br/>read fingerprints back"]
        A2{"Real-name UID?"}
        A3["Check government-issued<br/>photo ID"]
        A4["Skip the legal ID check"]
        A5["Agree on communication<br/>channels"]
        A6["Record fingerprint, channels,<br/>checks, date, event"]
        A1 --> A2
        A2 -->|yes| A3
        A2 -->|no, pseudonymous| A4
        A3 --> A5
        A4 --> A5
        A5 --> A6
    end

    subgraph P2["Phase 2 · at home (secure environment)"]
        B1["Obtain the full public key"]
        B2["Re-check the fingerprint"]
        B3["Prove key possession<br/>(challenge–response)"]
        B4["Prove channel possession<br/>(response over the channel)"]
        B5["Certify the verified UID(s)<br/>with the offline primary key"]
        B6["Send the signed certificate<br/>privately to its owner"]
        B7["Owner imports it and decides<br/>whether to publish"]
        B1 --> B2 --> B3 --> B4 --> B5 --> B6 --> B7
    end

    A6 --> B1
```

### Phase 1 — in person (offline)

1. Prepare fingerprint slips (`gpg-key2ps`, or this repository's [`gpg-key2typ`](../README.md) to render them with Typst), and know your own fingerprint well enough to check it.
2. Exchange slips with each person. Read your fingerprint aloud and have the other party follow along; both parties write down (or scan) the other's fingerprint. Compare the full fingerprint — a scanned QR code is at best a convenience.
3. If the key's User ID is a real name, check a government-issued photo ID, per the event's or the two parties' signing policy. If the User ID is a pseudonym, no legal identity check is needed; instead, agree on the online channel (Telegram, Matrix, Signal, email, …) through which that pseudonym can be reached.
4. Record what you verified: fingerprint, channel(s), what was checked, date, and event. At list-based parties, tick the "Fingerprint OK" and "ID OK" boxes on the printed participant list.
5. Leave the private key at home. Nothing in this phase needs a computer or a network.

```mermaid
sequenceDiagram
    autonumber
    actor A as Alice
    actor B as Bob

    Note over A,B: In person · offline · no computer, no private key
    A->>B: Hand over the slip
    B->>A: Hand over the slip
    A->>B: Read my fingerprint aloud, follow along
    B->>A: Read my fingerprint aloud, follow along
    opt Real-name UID
        A->>B: Show government-issued photo ID
        B->>A: Show government-issued photo ID
    end
    opt Pseudonymous UID
        A->>B: Agree on Telegram / Matrix / Signal / email
        B->>A: Agree on Telegram / Matrix / Signal / email
    end
    Note over A,B: Both write down fingerprint, channels, checks, date, event
```

If you already know the other party through an authenticated channel (for example a previously verified Signal safety number, or long-standing correspondence), the in-person step can be reduced to exchanging and checking the fingerprint — but the Phase 2 checks below still apply. Skipping the in-person step entirely is possible, but then it is no longer a key signing party.

### Phase 2 — at home (secure environment)

1. Obtain the full public key from a reliable source: directly from its owner over an already verified channel, or from a keyserver. Then compare the **full fingerprint** against your Phase 1 record. Don't trust the source; trust the fingerprint.
2. Verify key possession with a challenge–response: encrypt a fresh, random challenge with the other party's public key and send it over the verified channel; require the plaintext back. Naming the verified primary fingerprint as recipient is enough — GnuPG picks an encryption-capable subkey on its own. If you specifically need signing capability, ask for a signature over the challenge made by the signing subkey (see the notes below).
3. Verify channel possession: the response must arrive over the channel agreed in Phase 1. That confirms the key owner still controls the channel — and, for a pseudonymous UID, is what binds the key to the pseudonym.
4. Certify only the User ID(s) whose binding you actually verified, with the primary key, in an offline environment (for example `gpg --ask-cert-level --sign-key <fingerprint>`, or `gpg --quick-sign-key <fingerprint> '<uid pattern>'` to pick individual UIDs). Choose a certification level that reflects how thoroughly you verified the identity.
5. Export the certification (or the updated certificate) and send it privately to the key owner over a verified channel. Let the owner decide whether to publish it. Never upload someone else's key to a keyserver without their consent.

```mermaid
sequenceDiagram
    autonumber
    actor A as Alice (signer)
    participant S as Key source
    actor B as Bob (key owner)
    participant K as Offline primary key

    A->>S: Fetch Bob's public key
    S-->>A: Public key
    A->>A: Compare fingerprint with Phase 1 notes
    A->>B: Encrypted challenge, sent over the verified channel
    B->>B: Decrypt with the private key
    B-->>A: Return the challenge over the same channel
    A->>A: Key possession and channel possession confirmed
    A->>K: Certify Bob's verified UID(s)
    K-->>A: Certification signature
    A->>B: Signed certificate, sent privately
    B->>B: Import and decide whether to publish
```

### What gets bound to what

```mermaid
flowchart LR
    person(("Person / pseudonym"))
    fp["Fingerprint"]
    ch["Communication channel"]
    key["Public key"]

    person -->|"Phase 1 · in person"| fp
    person -->|"Phase 1 · exchange<br/>Phase 2 · response"| ch
    fp -->|"Phase 2 · fingerprint check"| key
    ch -->|"Phase 2 · challenge–response"| key
```

| Binding | Established in | Verified by |
| --- | --- | --- |
| Person / pseudonym ↔ fingerprint | Phase 1 (in person) | Photo ID, or agreement on a channel |
| Person / pseudonym ↔ channel | Phase 1 (exchange) + Phase 2 (response) | Challenge–response over that channel |
| Fingerprint ↔ public key | Phase 2 | Local fingerprint comparison |
| Public key ↔ private key | Phase 2 | Decrypting the challenge (encryption subkey) |

### Notes and pitfalls

- **Possession proof stops at the subkey.** A challenge encrypted with the key is decrypted by an encryption subkey's private key, so it proves control of *that subkey*, not of the primary key that issues certifications. This is generally accepted; if your policy demands more, ask for a fresh signature made by the primary key. A signature made by a signing subkey proves only that subkey — it still does not prove the primary key's private key.
- **One fingerprint per key.** The fingerprint exchanged in Phase 1 and compared in Phase 2 is the primary key's. Subkeys have fingerprints of their own, but they carry no User IDs and are bound to the primary by the primary key's subkey binding signatures, so they are never verified separately.
- **Certifications are per UID.** OpenPGP certifications are issued by the primary key over individual User IDs. Verify and certify only the UIDs whose binding you checked — the email address that answered, the pseudonym whose channel answered, the name on the ID you saw.
- **Fingerprint lengths differ.** The slips are laid out for 40-hex-digit v4 fingerprints (SHA-1), the common case. v6 keys ([RFC 9580](https://www.rfc-editor.org/rfc/rfc9580.html)) have 64-hex-digit fingerprints (SHA-256); `gpg-key2typ` prints them in full, but they run long, so give them room with `-1` (one column). The experimental v5 keys from the `--rfc4880bis` drafts have the same length.
- **Publishing is the owner's call.** Never upload someone else's key or your certification to a keyserver without consent. Note that [keys.openpgp.org](https://keys.openpgp.org/about/faq) does not distribute third-party certifications by default (only first-party attested ones), so signatures made at a key signing party do not propagate through it; traditional keyservers and project keyrings (e.g. Debian's) behave differently.
- **Certifications are revocable.** If a verification later turns out to be wrong, revoke the certification (`gpg --edit-key` → `revsig`), and keep your own key's revocation certificate somewhere safe.

## Automation (out of scope)

Tools such as `caff` from the [`signing-party`](https://salsa.debian.org/signing-party-team/signing-party) package can simplify part of the post-party work. Describing those workflows is beyond the scope of this document; see [`caff(1)`](https://manpages.debian.org/unstable/signing-party/caff.1.en.html) and the rest of the package's documentation if you want to use them.

## References

Background:

- [The Keysigning Party HOWTO](https://www.cryptnet.net/fdp/crypto/keysigning_party/en/keysigning_party.html) — the classic guide, including the Zimmermann–Sassaman method.
- [Wikipedia: Key signing party](https://en.wikipedia.org/wiki/Key_signing_party)
- [Wikipedia: Zimmermann–Sassaman key-signing protocol](https://en.wikipedia.org/wiki/Zimmermann%E2%80%93Sassaman_key-signing_protocol)

Practical guidance and real-world events:

- [Debian: Keysigning](https://www.debian.org/events/keysigning.en.html) — how to run a keysigning session.
- [Debian Wiki: Keysigning](https://wiki.debian.org/Keysigning) and [Keysigning/Offers](https://wiki.debian.org/Keysigning/Offers)
- [DebConf 10 keysigning example](https://people.debian.org/~anibal/ksp-dc10/ksp-dc10.html)

Tools:

- [`signing-party`](https://salsa.debian.org/signing-party-team/signing-party) — `caff`, `gpgparticipants`, `gpg-key2ps`, and friends.
- [`gpg-key2typ`](../README.md) — this repository; the same slips as Typst output.
- [`caff(1)`](https://manpages.debian.org/unstable/signing-party/caff.1.en.html), [`gpgparticipants(1)`](https://manpages.debian.org/unstable/signing-party/gpgparticipants.1.en.html), [`gpg-key2ps(1)`](https://manpages.debian.org/unstable/signing-party/gpg-key2ps.1.en.html)
- [Debian business-card templates](https://www.debian.org/events/materials/business-cards/) — an alternative to fingerprint slips.

Specifications and key servers:

- [GnuPG manual: OpenPGP Key Management](https://gnupg.org/documentation/manuals/gnupg/OpenPGP-Key-Management.html)
- [RFC 9580 — OpenPGP](https://www.rfc-editor.org/rfc/rfc9580.html)
- [keys.openpgp.org FAQ](https://keys.openpgp.org/about/faq) — why third-party certifications are not distributed by default.
