# 📰 This Week in Bitcoin (2026-11-02 to 2026-11-08)

## 📌 The TL;DR
- Exploring architectural shifts for Lightning Network nodes to enhance fund security and availability through K-of-N multi-signature schemes.
- Investigating TCP hole punching to significantly improve the connectivity and decentralization of Bitcoin full nodes behind home NATs.

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

*No major merges this week.*

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#1566: BIP458: Schnorr (Incremental) Half Aggregation](https://github.com/bitcoin-core/secp256k1/pull/1566)
**Author:** [@fjahr](https://github.com/fjahr) | **[Maintenance & Tech Debt]** *(Activity: 1 review events this week)*

#### [#1754: BIP459: Add FullAgg (DahLIAS) module](https://github.com/bitcoin-core/secp256k1/pull/1754)
**Author:** [@fjahr](https://github.com/fjahr) | **[Maintenance & Tech Debt]** *(Activity: 1 review events this week)*

#### [#36648: descriptor, rpc, wallet: do not echo key material in error messages](https://github.com/bitcoin/bitcoin/pull/36648)
**Author:** [@fametrano](https://github.com/fametrano) | **[Maintenance & Tech Debt]** *(Activity: 1 review events this week)*

## 🗓️ Dev Meeting
Summary of the core dev IRC meeting on 2026-11-05 with 16 participants.

- Benchmarking WG Update (l0rinc): l0rinc pushed #36778, which replaces the `loadtxoutset` RPC with a startup argument, aiming to narrow AssumeUTXO's scope and avoid corner cases when loading a UTXO set on an existing chainstate.
- Kernel WG Update (sedited): sedited is seeking review for #35641, which adds a script evaluation tracer to the kernel. sedited also highlighted #36692, a tracking issue for making unit tests more declarative.
- QA WG Update (brunoerg): No update was provided this week.
- addr-relay WG update (stratospher): A new WG has been formed to address ongoing spam of existing addresses with fresh timestamps, which pins addresses in the new table. Discussions were held on mitigation strategies. The WG will also address longstanding Addrman issues, including service flags problems and address relay problems due to peers controlling address timestamps. lightlike provided links to bnoc.xyz/t/address-relay-under-stress/163 and bnoc.xyz/t/address-relay-under-stress-attack-characteristics-and-measuring-its-effects/164 for further details.
- Disk error handling inconsistencies (bitcoindev1337): bitcoindev1337 noted that disk error handling is inconsistent, varying between being ignored in `process_messages` try/catch blocks and causing node shutdowns in RPC paths. This requires a unified plan rather than piecemeal fixes. #36101 (doc: Add an error handling strategy by purpleKarrot) and #35003 (validation: improve block data I/O error handling in P2P paths by furszy) were referenced as relevant discussions.
- CVE-2026-117349 and CVE-2026-117350 followups (darosior): Patches for CVE-2026-117349 and CVE-2026-117350 were deployed last week, with binaries available within 48 hours. darosior initiated discussion on fundamental cleanups and improved testing. For CVE-2026-117349, the root cause is unbounded growth in p2p data structures, with a timer-based stopgap implemented. Proposed cleanups include: 1) changing the tx INVs token bucket manager to use a single, bounded queue; 2) moving parts of `SendMessages()` to early return on `fPauseSend`; and 3) minor cleanups for other announcements. For CVE-2026-117350, darosior is hardening tests and opened #36761 (RFC: switch from select() to poll() on all platforms) for longer-term cleanups.

**Action Items:**
- sedited requested review for #35641 (kernel: Add script evaluation tracer).
- bitcoindev1337 will review existing discussions on #36101 and #35003 regarding disk error handling.
- darosior requested review commitment for potential refactorings related to CVE-2026-117349 cleanups. dzxzg, eugenesiegel, and jonatack offered to review.
- stratospher invited interested developers to join the new Addr-Relay WG.

## 🗣️ Research & Governance
Top active threads across mailing lists and research forums.

### [Public key recovery for EC leaves in P2MR (BIP-360)](https://delvingbitcoin.org/t/public-key-recovery-for-ec-leaves-in-p2mr-bip-360/2603/35)
**Source:** Delving | **Started By:** {'username': 'Boris Nagaev', 'uuid': 'can_boris_nagaev'} | **Messages:** 4
> A proposal to optimize future Bitcoin transactions for efficiency and cost using public key recovery is being discussed, though its origin has been questioned.

**Technical Details:** The discussion centers on a BIP-360 optimization for P2MR outputs, suggesting EC public key recovery for 'cheap' leaves alongside post-quantum leaves. Boris Nagaev is evaluating the cost model, referencing BIP342's accounting with a 50-unit charge per recovery, and comparing it to Schnorr verification. However, Pieter Wuille's comment that the original post is from an AI spam bot introduces significant doubt about the proposal's legitimacy. The architectural debate involves integrating new cryptographic primitives and their cost models into Bitcoin's script system. The immediate next step is to verify the proposal's authenticity before further technical analysis.

### [Towards A K-of-N Lightning Network Node](https://delvingbitcoin.org/t/towards-a-k-of-n-lightning-network-node/2395/10)
**Source:** Delving | **Started By:** {'username': 'ZmnSCPxj jxPCSnmZ', 'uuid': 'auto_zmnscpxj_jxpcsnmz'} | **Messages:** 3
> We're exploring new ways to secure Lightning Network funds using shared control, making it safer and more resilient for users. This allows multiple parties to collectively manage a Lightning node, enhancing security against loss or compromise.

**Technical Details:** The thread explores building a k-of-n multisig self-custodial Lightning node, leveraging Nested MuSig2 for enhanced fund security. A key technical debate now focuses on the storage costs of Lightning channel state updates, specifically how Core Lightning and lnd handle these differently. This impacts the operational overhead and scalability of a multisig node, requiring optimization of state management to minimize storage requirements for a robust k-of-n setup.

### [Forwardable Peerswap Incentives, And Closing Surreptitious Communications Tunnels](https://delvingbitcoin.org/t/forwardable-peerswap-incentives-and-closing-surreptitious-communications-tunnels/2917/4)
**Source:** Delving | **Started By:** {'username': 'ZmnSCPxj jxPCSnmZ', 'uuid': 'auto_zmnscpxj_jxpcsnmz'} | **Messages:** 2
> Developers are refining a new Lightning Network protocol, Forwardable Peerswaps, to improve liquidity management. The current focus is on ensuring all protocol commitments are cryptographically secure and enforceable on-chain.

**Technical Details:** The discussion centers on the precise definition of 'commit' within the Forwardable Peerswaps protocol's hash-exchange argument. It's argued that 'commit' must strictly imply an enforceable on-chain commitment, rather than just off-chain signed messages or an agreement to continue. This distinction is critical for the protocol's security and trustlessness, ensuring that all commitments are cryptographically binding. The protocol specification requires explicit clarification to define this commitment mechanism clearly and prevent any ambiguity.

### [TCP hole punching for Bitcoin nodes behind home NATs?](https://delvingbitcoin.org/t/tcp-hole-punching-for-bitcoin-nodes-behind-home-nats/2497/34)
**Source:** Delving | **Started By:** {'username': '0xB10C', 'uuid': 'can_0xb10c'} | **Messages:** 2
> We're exploring ways to help more home users run reachable Bitcoin nodes, boosting network decentralization and resilience. This involves carefully balancing ease of connectivity with robust security against potential network attacks.

**Technical Details:** The discussion centers on increasing reachable nodes in residential ISPs, particularly through techniques like holepunching. Key questions include the specific problems solved by such features, how to implement them to raise attacker costs, and the security implications for home users given recent TCP stack and protocol vulnerabilities (e.g., CVE-2026-117350, CVS-2026-117349). The architectural debate weighs the benefits of enhanced decentralization against the risks of exposing home nodes to potential exploits, questioning if increased reachability is 'sensible' under current conditions.

### [Direct Messages (DMs)](https://delvingbitcoin.org/t/direct-messages-dms/3027/1)
**Source:** Delving | **Started By:** {'username': 'ORANGEMART', 'uuid': 'auto_orangemart'} | **Messages:** 2
> We're working to empower artists by enabling direct Bitcoin payments from listeners. Our goal is to connect an artist with their fans on btcplaylist.com so listeners can easily 'zap' them for their music.

**Technical Details:** The immediate technical task is to acquire the Nostr public key (`npub`) for artist @neonrooks to integrate Lightning zapping functionality on btcplaylist.com. This will allow listeners to send direct Bitcoin payments. The current challenge is a communication hurdle, as the developer is unable to find a direct messaging mechanism on the platform to request the `npub`, highlighting a potential need for improved key exchange protocols or platform-specific contact methods for Nostr identity integration.

## 🏆 Contributor Shoutouts
### 🕵️ Top Reviewers
Providing critical review and testing: [@fametrano](https://github.com/fametrano), [@fjahr](https://github.com/fjahr)
