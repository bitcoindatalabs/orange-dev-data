# 📰 This Week in Bitcoin (2026-10-12 to 2026-10-18)

## 📌 The TL;DR
- A significant technical focus on improving node connectivity and initial synchronization, evidenced by discussions on TCP hole punching for NAT traversal and the IBD Booster PoC, alongside ongoing `cmpctblock` optimizations to enhance network resilience and lower the barrier to running full nodes.
- Continued development and hardening of advanced cryptographic features, with progress on MuSig and Silent Payments, and proactive discussions on long-term security challenges such as post-quantum cryptography for L2s, demonstrating a commitment to evolving Bitcoin's privacy and security capabilities.

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

#### [#35724: cmpctblock: Improve logging of `cmpctblock` message reconstruction statistics [part of prefill series]](https://github.com/bitcoin/bitcoin/pull/35724)
**Author:** [@davidgumberg](https://github.com/davidgumberg) | **[Network & Privacy]** *(Activity: 29 review events)*
> This PR enhances the logging for `cmpctblock` (compact block) message reconstruction, providing more detailed statistics. This helps developers better understand and debug the performance and efficiency of compact block relay.

**Technical Details:** The logging mechanisms for `cmpctblock` message reconstruction are augmented to include more granular statistics. This involves capturing and reporting metrics such as the number of missing transactions, successful reconstructions, and elapsed times. These detailed logs are invaluable for diagnosing issues and optimizing the compact block relay protocol, which is crucial for efficient block propagation.

#### [#1866: musig: Add hash context tests](https://github.com/bitcoin-core/secp256k1/pull/1866)
**Author:** [@mllwchrry](https://github.com/mllwchrry) | **[Security & Consensus]** *(Activity: 11 review events)*

#### [#36440: test: speed up functional tests by removing avoidable waits](https://github.com/bitcoin/bitcoin/pull/36440)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Performance & Optimization]** *(Activity: 11 review events)*
> This PR significantly accelerates the functional test suite by eliminating unnecessary waiting periods, allowing for faster test execution. This optimization helps developers iterate more quickly and improves the efficiency of the testing process.

**Technical Details:** Similar to other test speedup PRs, this change identifies and removes specific `sleep` calls or fixed-duration waits within the functional tests. It replaces them with more intelligent synchronization mechanisms, such as polling for specific conditions or waiting on events, ensuring tests progress as soon as their prerequisites are met. This directly reduces the overall time required to run the test suite.

#### [#36425: guix: declare python-setuptools in codesign manifest](https://github.com/bitcoin/bitcoin/pull/36425)
**Author:** [@willcl-ark](https://github.com/willcl-ark) | **[Maintenance & Tech Debt]** *(Activity: 9 review events)*
> This PR updates the Guix build system to correctly declare `python-setuptools` in the codesign manifest, ensuring the reproducible build process remains robust. It helps maintain the integrity and verifiability of Bitcoin Core releases.

**Technical Details:** The change modifies the Guix build manifest, specifically the `codesign` section, to explicitly include `python-setuptools` as a dependency. This ensures that all components required for the build, including those used in the codesigning process, are properly tracked and included in the reproducible build environment. This prevents potential build failures or inconsistencies related to missing Python dependencies.

#### [#36294: mempool: Remove -persistmempoolv1 option](https://github.com/bitcoin/bitcoin/pull/36294)
**Author:** [@fjahr](https://github.com/fjahr) | **[Maintenance & Tech Debt]** *(Activity: 9 review events)*
> This PR removes the deprecated `-persistmempoolv1` option, simplifying the mempool persistence mechanism. This ensures all nodes utilize the current, more efficient mempool persistence format, reducing code complexity and maintenance burden.

**Technical Details:** The change involves deleting the command-line option parsing logic for `-persistmempoolv1` and removing the associated code paths responsible for loading and saving the mempool in the older v1 format. This effectively deprecates and removes support for the legacy persistence mechanism, forcing all nodes to use the current, presumably more robust and performant, mempool persistence format. This reduces the codebase's technical debt.

#### [#36439: test: poll more frequently in sync helpers and RPC connection wait](https://github.com/bitcoin/bitcoin/pull/36439)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR adjusts test helpers to poll more frequently when waiting for synchronization or RPC connections. This makes tests run faster and more reliably by reducing unnecessary delays.

**Technical Details:** The polling intervals within test synchronization helpers and RPC connection wait functions are reduced. This modification allows tests to detect state changes, such as block synchronization or RPC server readiness, more quickly. This minimizes idle wait times, improving the overall execution speed and determinism of the test suite without affecting production code.

#### [#36469: refactor: deduplicate block validation state catcher](https://github.com/bitcoin/bitcoin/pull/36469)
**Author:** [@enirox001](https://github.com/enirox001) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR refactors the codebase by removing duplicate logic related to catching block validation states, making the code more concise and easier to maintain. It improves the overall quality and readability of the block validation infrastructure.

**Technical Details:** The change involves identifying common patterns or identical code blocks used across different parts of the block validation process, specifically concerning how validation states are captured or handled. The refactor consolidates these duplicate sections into a single, reusable function or class, reducing code redundancy. This architectural improvement simplifies future modifications and reduces the risk of inconsistencies.

#### [#36504: test: Add missing timeouts for HTTPConnection](https://github.com/bitcoin/bitcoin/pull/36504)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR enhances the reliability of functional tests by adding missing timeouts to `HTTPConnection` instances, preventing tests from hanging indefinitely. This makes the test suite more robust and provides clearer failure indications.

**Technical Details:** The change involves reviewing functional tests that utilize `HTTPConnection` objects and explicitly setting timeout parameters for these connections. Without timeouts, a test could block indefinitely if an HTTP request fails to receive a response, leading to stalled CI runs. Adding timeouts ensures that such network issues in tests are quickly identified and reported, improving test suite stability.

#### [#36441: doc: fix How to Upgrade section for bitcoin wrapper and libexec](https://github.com/bitcoin/bitcoin/pull/36441)
**Author:** [@yashspidey](https://github.com/yashspidey) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR updates the "How to Upgrade" documentation to correctly describe the process when using the `bitcoin` wrapper script and `libexec` directory. It ensures users have accurate instructions, preventing potential upgrade issues and improving the overall user experience.

**Technical Details:** This PR modifies the `doc/upgrade.md` file to clarify the steps for users who compile Bitcoin Core with the `bitcoin` wrapper script and utilize the `libexec` directory for executables. The update ensures that the documented upgrade procedure accurately reflects the file structure and execution flow for such installations. It corrects references to where binaries are expected to reside and how they should be replaced during an upgrade, preventing misconfigurations or failed upgrades.

#### [#36446: test: remove some avoidable test waits](https://github.com/bitcoin/bitcoin/pull/36446)
**Author:** [@willcl-ark](https://github.com/willcl-ark) | **[Performance & Optimization]** *(Activity: 5 review events)*
> This PR optimizes the functional test suite by eliminating unnecessary waiting periods, significantly speeding up test execution times. This improvement allows developers to run tests more quickly and efficiently, accelerating the development cycle.

**Technical Details:** The PR identifies specific points within various functional tests where `time.sleep()` or similar waiting mechanisms were used excessively or could be replaced with more precise synchronization methods. By leveraging event-driven waits or more accurate polling, the tests can proceed immediately once conditions are met, rather than waiting for a fixed duration. This reduces overall test runtime without compromising test reliability.

#### [#36379: fuzz: fix stale comments in http_request](https://github.com/bitcoin/bitcoin/pull/36379)
**Author:** [@frankomosh](https://github.com/frankomosh) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR updates outdated comments within the HTTP request fuzzer, improving code clarity and maintainability for developers. It ensures that the documentation accurately reflects the current state of the fuzzer's logic.

**Technical Details:** The change specifically targets comments in the `http_request` fuzzer module. It identifies and corrects comments that no longer accurately describe the associated code logic or assumptions. This involves reviewing the fuzzer's implementation details and aligning the explanatory text to prevent future misunderstandings during development or debugging.

#### [#36498: [32.0] 32.0rc4](https://github.com/bitcoin/bitcoin/pull/36498)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR marks the release candidate 4 for Bitcoin Core version 32.0, signifying a crucial step towards the official release. It bundles all changes merged up to this point for final testing and review before the stable version.

**Technical Details:** This PR typically involves updating version strings, creating a new git tag (`v32.0rc4`), and potentially updating release notes or build scripts to reflect the new release candidate status. It serves as a checkpoint for the release process, allowing for comprehensive testing of the accumulated changes in a release-ready package. No functional code changes are usually introduced in such a PR itself, rather it's a metadata update.

#### [#1963: doc: say the sha256 compression callback processes secrets](https://github.com/bitcoin-core/secp256k1/pull/1963)
**Author:** [@fametrano](https://github.com/fametrano) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*

#### [#1929: silentpayments: perform tweak addition with actual scalars](https://github.com/bitcoin-core/secp256k1/pull/1929)
**Author:** [@theStack](https://github.com/theStack) | **[Security & Consensus]** *(Activity: 3 review events)*

#### [#36522: test: check MIN_PEER_PROTO_VERSION peers are not disconnected](https://github.com/bitcoin/bitcoin/pull/36522)
**Author:** [@instagibbs](https://github.com/instagibbs) | **[Network & Privacy]** *(Activity: 3 review events)*
> This PR adds a test to ensure that peers running the minimum supported protocol version are not inadvertently disconnected. This helps maintain network compatibility and prevents unintended disconnections of valid nodes.

**Technical Details:** A new test case is introduced to specifically verify that nodes connecting with `MIN_PEER_PROTO_VERSION` are correctly handled and not prematurely disconnected by the peer management logic. This test ensures adherence to the protocol versioning policy, preventing regressions that could impact network connectivity for older, but still supported, nodes.

#### [#36552: refactor: drop lifetimebound `__has_attribute` check](https://github.com/bitcoin/bitcoin/pull/36552)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR removes a specific `__has_attribute` check related to `lifetimebound` during compilation. This refactoring simplifies the build process and removes a compiler-specific check that is no longer necessary.

**Technical Details:** The conditional compilation check for `__has_attribute(lifetimebound)` is eliminated from the build system. This attribute is specific to certain compiler versions or configurations, and its removal simplifies the codebase by reducing conditional compilation paths. This change contributes to a cleaner and more maintainable build system.

#### [#36517: Update crc32c subtree to latest master](https://github.com/bitcoin/bitcoin/pull/36517)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR updates the `crc32c` library subtree to its latest master version, incorporating upstream improvements and bug fixes. Keeping dependencies current ensures Bitcoin Core benefits from the latest advancements and maintains compatibility.

**Technical Details:** The change involves pulling the latest commits from the upstream `crc32c` repository into Bitcoin Core's vendored subtree. This process updates the `crc32c` implementation used within Bitcoin Core, potentially bringing performance enhancements, bug fixes, or security patches from the upstream project. It's a routine dependency management task to keep the codebase up-to-date.

#### [#36485: ci: refactor BUILD_TARGETS use](https://github.com/bitcoin/bitcoin/pull/36485)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR refactors how `BUILD_TARGETS` are used within the Continuous Integration (CI) system, streamlining the build configuration. It improves the clarity and maintainability of the CI scripts, making them easier to manage.

**Technical Details:** The change focuses on optimizing the definition and usage of `BUILD_TARGETS` variables within the CI configuration files. This could involve consolidating target definitions, improving variable expansion logic, or standardizing how different build targets are invoked. The goal is to reduce complexity and potential errors in the CI pipeline setup.

#### [#36535: policy: sum package weight in int64_t](https://github.com/bitcoin/bitcoin/pull/36535)
**Author:** [@fametrano](https://github.com/fametrano) | **[Security & Consensus]** *(Activity: 2 review events)*
> This PR updates the transaction package weight calculation to use `int64_t`, preventing potential overflows for very large transaction packages. This ensures the correct and robust handling of transaction package policies.

**Technical Details:** The data type used for summing transaction package weight is changed from a smaller integer type to `int64_t`. This modification prevents integer overflow issues that could arise with extremely large transaction packages, ensuring accurate weight calculations and correct application of mempool and relay policies, which are critical for network stability and transaction processing.

#### [#36511: test: Small mempool_compatibility.py cleanups](https://github.com/bitcoin/bitcoin/pull/36511)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR introduces minor cleanups to the `mempool_compatibility.py` test script, making the test suite more organized and easier to understand. It contributes to a cleaner and more maintainable codebase for future development.

**Technical Details:** The changes involve refactoring small aspects of the `mempool_compatibility.py` functional test. This could include removing redundant code, improving variable naming, or reordering test steps for better logical flow. The goal is to enhance readability and maintainability of the test script without altering its functional behavior or coverage.

#### [#36514: ci: Remove confusing -DBUILD_BENCH=ON -DBUILD_FUZZ_BINARY=ON from CONFIG_ALL](https://github.com/bitcoin/bitcoin/pull/36514)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR removes confusing and redundant build flags for benchmarks and fuzzing binaries from the `CONFIG_ALL` CI job. This simplifies the CI configuration and makes it clearer.

**Technical Details:** The `CONFIG_ALL` CI job's build command is modified to remove the explicit `-DBUILD_BENCH=ON` and `-DBUILD_FUZZ_BINARY=ON` flags. These flags were either redundant or caused confusion, as their behavior was already implicitly handled or not desired in that specific configuration. This cleanup streamlines the CI pipeline and improves its maintainability.

#### [#36544: test: Fix intermittent issue in p2p_eviction.py](https://github.com/bitcoin/bitcoin/pull/36544)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR fixes an intermittent issue in the `p2p_eviction.py` test script. This improves the reliability of the test suite, ensuring consistent and accurate testing of peer eviction logic.

**Technical Details:** The `p2p_eviction.py` test is updated to address a non-deterministic failure mode. This likely involves adjusting timing assumptions, synchronization points, or race conditions within the test environment to ensure it reliably passes across different execution contexts, thereby improving the robustness of the P2P eviction policy validation.

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#36524: common: drop locale setting hack](https://github.com/bitcoin/bitcoin/pull/36524)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 13 review events this week)*
> This PR removes a problematic 'locale setting hack' from common utility functions. This simplifies the codebase, improves consistency, and eliminates a source of potential locale-dependent bugs.

#### [#35724: cmpctblock: Improve logging of `cmpctblock` message reconstruction statistics [part of prefill series]](https://github.com/bitcoin/bitcoin/pull/35724)
**Author:** [@davidgumberg](https://github.com/davidgumberg) | **[Network & Privacy]** *(Activity: 11 review events this week)*
> This PR enhances the logging for `cmpctblock` (compact block) message reconstruction, providing more detailed statistics. This helps developers better understand and debug the performance and efficiency of compact block relay.

#### [#35728: rpc: Properly throw on internal I/O errors in GetTransaction](https://github.com/bitcoin/bitcoin/pull/35728)
**Author:** [@maflcko](https://github.com/maflcko) | **[Wallet & User Tools]** *(Activity: 11 review events this week)*
> This PR improves the `GetTransaction` RPC by ensuring it properly reports internal I/O errors. This makes the RPC more robust and provides clearer feedback to users or applications when underlying data access issues occur.

#### [#36525: mining: add getTotalFees(), protect m_block_template with mutex](https://github.com/bitcoin/bitcoin/pull/36525)
**Author:** [@Sjors](https://github.com/Sjors) | **[Security & Consensus]** *(Activity: 9 review events this week)*
> This PR introduces a function to calculate total fees in a block template and protects the template with a mutex. This enhances the robustness of the mining process by preventing race conditions and ensuring data integrity.

#### [#31507: build: Use clang-cl to build on Windows natively](https://github.com/bitcoin/bitcoin/pull/31507)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 9 review events this week)*
> This PR updates the build system to use `clang-cl` for native Windows builds of Bitcoin Core. Leveraging `clang-cl` offers potential improvements in build times, better diagnostics, and alignment with modern compiler features across platforms.

## 🗣️ Research & Governance
Top active threads across mailing lists and research forums.

### [TCP hole punching for Bitcoin nodes behind home NATs?](https://delvingbitcoin.org/t/tcp-hole-punching-for-bitcoin-nodes-behind-home-nats/2497/18)
**Source:** Delving | **Started By:** {'username': '0xB10C', 'uuid': 'can_0xb10c'} | **Messages:** 7
> Developers are exploring new methods to make more Bitcoin nodes easily discoverable and connectable, especially for home users, to enhance the network's decentralization and resilience. This aims to ensure a more robust and accessible Bitcoin network for everyone.

**Technical Details:** The discussion revolves around a proposed NAT holepunching feature to improve node reachability, particularly for residential ISPs, with questions raised about its precise problem-solving utility. A key architectural debate focuses on mitigating Sybil attacks, where an attacker could flood the node with fake or real addresses/public keys to monopolize connection attempts. Careful design of an 'holepunch address manager' and robust rate-limiting are critical to prevent resource exhaustion and connection monopolization. The main downside identified is the risk of an attacker monopolizing connections, necessitating robust defense strategies.

### [What does "post-quantum" actually mean for a Bitcoin L2 when settlement still happens on a non-PQ L1?](https://delvingbitcoin.org/t/what-does-post-quantum-actually-mean-for-a-bitcoin-l2-when-settlement-still-happens-on-a-non-pq-l1/2715/8)
**Source:** Delving | **Started By:** {'username': 'hal_03', 'uuid': 'auto_hal_03'} | **Messages:** 4
> We're discussing how to future-proof Bitcoin's fast, off-chain payment systems against quantum computer threats, ensuring their long-term security even as the main network evolves.

**Technical Details:** The core technical debate revolves around the design and utility of Post-Quantum (PQ) resistant Layer 2 (L2) solutions, like state channels, that settle on Bitcoin's currently quantum-vulnerable Layer 1 (L1). The discussion clarifies that the focus is not on L2s operating with already broken L1 cryptography, but rather on future-proofing L2 components. This involves considering how L2s can adopt PQ schemes now, anticipating potential L1 upgrades or a gradual transition, and defining the 'bridge' mechanisms for secure interaction.

### [Bitcoin-rs: an independent Bitcoin node written in Rust](https://delvingbitcoin.org/t/bitcoin-rs-an-independent-bitcoin-full-node-written-in-rust/2918/2)
**Source:** Delving | **Started By:** {'username': 'Gosunuts', 'uuid': 'auto_gosunuts'} | **Messages:** 2
> A new, independent Bitcoin full node is being developed in Rust, aiming to improve performance and explore new architectural designs. This initiative could lead to a more robust and efficient Bitcoin network for all users.

**Technical Details:** An early-stage project, `bitcoin-rs`, has been announced, proposing a new independent Bitcoin full node implementation written in Rust. Similar to `btcd`, its primary goal is to explore alternative architectural patterns and performance optimizations beyond the existing Bitcoin Core codebase. While currently just an initial share, the project implicitly opens a discussion on alternative architectural patterns and performance trade-offs compared to Bitcoin Core. Future technical review and collaboration will be essential to evaluate its potential impact on network decentralization and efficiency, and to identify specific areas for architectural innovation and debate.

### [Open-source Bitcoin multisig coordinator: shared signing queue, hardware wallets, live signet demo](https://delvingbitcoin.org/t/open-source-bitcoin-multisig-coordinator-shared-signing-queue-hardware-wallets-live-signet-demo/2957/1)
**Source:** Delving | **Started By:** {'username': 'Thomas Clement', 'uuid': 'auto_thomas_clement'} | **Messages:** 2
> A new open-source tool, btc-safe, simplifies secure Bitcoin multisig management, allowing multiple parties to easily coordinate and sign transactions from their own devices. It enhances fund security and user control through its self-hosted, watch-only design.

**Technical Details:** btc-safe is an open-source, self-hosted watch-only Bitcoin multisig coordinator. Its architecture facilitates transaction proposal by one owner, queuing it for co-signers. Each co-signer independently signs from their device, ensuring key isolation, before the coordinator broadcasts the final transaction. This design prioritizes self-custody and streamlined multi-party signing without holding private keys.

### [IBD Booster -- Speeding up IBD with pre-generated hints (PoC)](https://delvingbitcoin.org/t/swiftsync-speeding-up-ibd-with-pre-generated-hints-poc/1562/19)
**Source:** Delving | **Started By:** {'username': 'Sebastian Falbesoner', 'uuid': 'can_sebastian_falbesoner'} | **Messages:** 1
> Developers are actively working on significantly speeding up the Initial Block Download (IBD) process, making it much faster for new Bitcoin nodes to sync and verify the entire blockchain. This aims to improve the user experience by reducing the time it takes to get a fully validated node online.

**Technical Details:** The discussion revolves around optimizing Initial Block Download (IBD) by reducing chainstate operations. RubenSomsen initially proposed using pre-generated hints for this purpose. A significant new development is Floresta's implementation of SwiftSync, which leverages 'implicit deletions for Utreexo'—a technique for efficient UTXO set management—as an alternative or complementary approach to accelerate IBD. This introduces a new architectural path, potentially leveraging accumulator-based solutions like Utreexo, for substantial speed improvements, requiring further evaluation and integration considerations within Bitcoin Core.

## 🏆 Contributor Shoutouts
### 🎉 First-Time Merges
Welcome to the codebase: [@yashspidey](https://github.com/yashspidey)

### ✍️ Top Authors
The most active PR authors this week: [@maflcko](https://github.com/maflcko), [@fanquake](https://github.com/fanquake), [@ViniciusCestarii](https://github.com/ViniciusCestarii), [@willcl-ark](https://github.com/willcl-ark), [@davidgumberg](https://github.com/davidgumberg)

### 🕵️ Top Reviewers
Providing critical review and testing: [@maflcko](https://github.com/maflcko), [@fanquake](https://github.com/fanquake), [@fametrano](https://github.com/fametrano), [@pinheadmz](https://github.com/pinheadmz), [@hebasto](https://github.com/hebasto)
