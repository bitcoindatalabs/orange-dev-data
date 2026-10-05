# 📰 This Week in Bitcoin (2026-09-28 to 2026-10-04)

## 📌 The TL;DR
- Intensified focus on Post-Quantum Cryptography (PQC):** Multiple discussions highlight the growing importance of PQC, exploring its implications for both L1 and L2 (Lightning Network) security, and initiating technical deep-dives into potential PQC output types for future protocol upgrades.
- Renewed exploration of L1 privacy solutions:** The "Shielded Bitcoin" discussion signals a significant technical conversation around implementing private transfers directly on the Bitcoin base layer, indicating a potential long-term shift towards enhanced on-chain confidentiality.

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

#### [#36233: guix: Update time-machine to `60f6956aeffa7f30285745bd0ea615e9acfc74f8`](https://github.com/bitcoin/bitcoin/pull/36233)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 37 review events)*
> This PR updates the Guix build system's 'time-machine' reference, ensuring that reproducible builds of Bitcoin Core continue to use a consistent and verified set of dependencies. This is crucial for maintaining the integrity and trustworthiness of Bitcoin Core binaries.

**Technical Details:** The Guix build system relies on a 'time-machine' mechanism to pin all build dependencies to specific, cryptographically verifiable versions, ensuring bit-for-bit reproducible builds. This PR updates the Git commit hash (`60f6956aeffa7f30285745bd0ea615e9acfc74f8`) that defines this 'time-machine' state. This involves modifying the Guix build scripts or configuration files to point to the new, updated snapshot of the Guix package collection, thereby refreshing the environment used for reproducible builds.

#### [#34213: net: preserve anchors when network is disabled](https://github.com/bitcoin/bitcoin/pull/34213)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Network & Privacy]** *(Activity: 33 review events)*
> This PR ensures that network anchor nodes are preserved even when the network interface is temporarily disabled, allowing for faster reconnection upon re-enabling. This improves the reliability and startup time of a Bitcoin Core node.

**Technical Details:** Previously, when the network interface of Bitcoin Core was disabled (e.g., via `setnetworkactive false` RPC), the list of known network anchors (peer addresses used for bootstrapping connections) might have been inadvertently cleared or not properly persisted. This PR modifies the network management logic to ensure these anchor addresses are retained in memory or saved to disk even when the network is inactive. This means that when the network is re-enabled, the node can quickly attempt connections to these known good peers without having to rediscover them, leading to faster and more reliable network bootstrapping.

#### [#35833: log: prevent user input from injecting fake log lines](https://github.com/bitcoin/bitcoin/pull/35833)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Security & Consensus]** *(Activity: 24 review events)*
> This crucial security update prevents malicious user input from fabricating misleading log entries within Bitcoin Core, safeguarding users from potential social engineering or confusion. It sanitizes input to maintain log integrity.

**Technical Details:** The PR introduces input sanitization, specifically targeting newline characters (`\n`, `\r`), in user-provided strings before they are incorporated into log messages by RPC and wallet components. Previously, an attacker could embed these characters in inputs like transaction labels or RPC parameters to inject arbitrary log lines, potentially obscuring legitimate logs or deceiving users. This change modifies `LogPrint` calls in vulnerable code paths to ensure user input generates only single-line log entries, preventing log injection attacks.

#### [#36235: ci: fail iwyu job on compiler errors instead of silently logging them](https://github.com/bitcoin/bitcoin/pull/36235)
**Author:** [@David-Uka](https://github.com/David-Uka) | **[Maintenance & Tech Debt]** *(Activity: 20 review events)*
> This PR improves our continuous integration system by making the 'Include What You Use' (IWYU) job fail explicitly on compiler errors. This ensures that potential build issues are immediately visible and addressed, preventing silent failures.

**Technical Details:** Previously, the IWYU CI job would log compiler errors but continue to pass, potentially masking underlying build problems. This change modifies the CI script to detect and propagate compiler errors as job failures. By integrating error-checking mechanisms into the IWYU script execution, the CI pipeline will now correctly report build-related issues, enforcing stricter code quality checks and preventing silent regressions.

#### [#36336: log: move CreateNewBlock() log line behind a new mining category](https://github.com/bitcoin/bitcoin/pull/36336)
**Author:** [@ismaelsadeeq](https://github.com/ismaelsadeeq) | **[Maintenance & Tech Debt]** *(Activity: 14 review events)*
> This PR refines the logging system by moving the `CreateNewBlock()` log line under a new, dedicated mining category. This allows users to more easily filter and control log output specifically related to block creation.

**Technical Details:** The change modifies the logging call for the `CreateNewBlock()` function to associate it with a newly introduced logging category, likely `LogFlags::MINING`. This enables users to selectively enable or disable this particular log output via runtime configuration options (e.g., `-debug=mining`), providing more granular control over the verbosity of the logs. This improves debugging and monitoring capabilities for mining-related activities without affecting other system log messages.

#### [#36365: fees: fall back to `block_policy` and minor api change](https://github.com/bitcoin/bitcoin/pull/36365)
**Author:** [@ismaelsadeeq](https://github.com/ismaelsadeeq) | **[Performance & Optimization]** *(Activity: 12 review events)*
> This PR enhances the fee estimation logic by introducing a fallback mechanism to `block_policy` when more precise fee estimation methods are unavailable. This ensures more reliable transaction fee recommendations, especially under unusual network conditions or when specific fee targets are difficult to meet.

**Technical Details:** This change modifies the fee estimation module, likely within `src/feerate.cpp`, to implement a fallback path. If the primary fee estimation algorithm (e.g., based on historical mempool data) cannot provide a confident estimate for a given target, it will default to a `block_policy` derived feerate. This involves adjusting the `estimatesmartfee` RPC or internal transaction creation logic to query `block_policy` for a default feerate, potentially including minor API adjustments to expose or utilize this fallback more effectively.

#### [#36321: net: cast vector size to avoid overflow, truncation, sign change](https://github.com/bitcoin/bitcoin/pull/36321)
**Author:** [@Crypt-iQ](https://github.com/Crypt-iQ) | **[Security & Consensus]** *(Activity: 10 review events)*
> This PR enhances network robustness by ensuring correct type casting for vector sizes in network operations. It prevents potential overflows, truncations, and sign changes that could lead to incorrect data handling or system instability.

**Technical Details:** The change involves explicitly casting the return value of `std::vector::size()` to appropriate signed integer types when used in contexts that expect them. This mitigates risks associated with implicit type conversions, which could cause unexpected behavior, memory corruption, or denial-of-service vulnerabilities if large unsigned sizes are misinterpreted as negative or truncated. By enforcing correct type usage, the PR improves the reliability and security of network message processing.

#### [#36272: guix: split Linux toolchain](https://github.com/bitcoin/bitcoin/pull/36272)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR refactors the Guix build system by splitting the Linux toolchain into more granular components. This improves the maintainability and flexibility of Bitcoin Core's reproducible build environment, making it easier to update and manage build dependencies.

**Technical Details:** The change involves modifying the Guix manifests and build scripts to separate the monolithic Linux toolchain definition into distinct packages or modules. This modularization allows for independent updates of components like compilers, standard libraries, and other build tools, reducing the complexity of managing the entire toolchain. It enhances the reproducibility and auditability of the build process by providing clearer dependency graphs and improving overall build system hygiene.

#### [#1948: tests: add ECDSA verify case where r + n overflows p](https://github.com/bitcoin-core/secp256k1/pull/1948)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Security & Consensus]** *(Activity: 9 review events)*

#### [#36375: wallet: accept uppercase addresses without amount in sendall](https://github.com/bitcoin/bitcoin/pull/36375)
**Author:** [@FlashWayne](https://github.com/FlashWayne) | **[Wallet & User Tools]** *(Activity: 8 review events)*
> This PR enhances the wallet's `sendall` RPC by allowing it to accept uppercase Bitcoin addresses, making it more robust and user-friendly. Users will no longer encounter errors when providing valid but uppercase addresses for sending all funds.

**Technical Details:** This change modifies the wallet's address parsing logic within the `sendall` RPC to correctly handle and normalize uppercase Bitcoin addresses, ensuring they are recognized as valid destinations even when the amount is implicitly 'all' funds. It likely involves updating the `CBitcoinAddress` validation or a similar utility function used by the RPC to be case-insensitive or to normalize input addresses before processing.

#### [#36052: ci: Doc: Move all config comments right next to the option they explain](https://github.com/bitcoin/bitcoin/pull/36052)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR improves the readability of configuration files in the continuous integration system by repositioning comments. This makes it easier for developers to understand and modify CI settings.

**Technical Details:** This is a purely cosmetic change applied to the continuous integration configuration files, such as `.gitlab-ci.yml`. The modification involves reformatting the placement of comments, moving them from potentially separate blocks or lines to be directly adjacent to the specific configuration options they describe. This enhances the clarity and maintainability of the CI setup, making it easier for developers to quickly grasp the purpose of each setting.

#### [#36299: cli: Improve empty-response and fix -rpcclienttimeout regression](https://github.com/bitcoin/bitcoin/pull/36299)
**Author:** [@fjahr](https://github.com/fjahr) | **[Wallet & User Tools]** *(Activity: 7 review events)*
> This PR enhances the command-line interface's handling of empty RPC responses and fixes a regression related to the `-rpcclienttimeout` option. These improvements make the CLI more robust and reliable for users interacting with Bitcoin Core.

**Technical Details:** The PR addresses two distinct issues within the CLI client. For empty RPC responses, it modifies the parsing or display logic to gracefully handle such cases, preventing errors or confusing output. The fix for the `-rpcclienttimeout` regression involves re-establishing the correct application and interpretation of the timeout setting, which had been inadvertently broken in a previous change. This ensures that RPC calls correctly respect the user-configured timeout duration.

#### [#36383: util: remove unused exception parameter in `Popen::execute_process`](https://github.com/bitcoin/bitcoin/pull/36383)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR cleans up the codebase by removing an unused exception parameter from the `Popen::execute_process` utility function. This minor refactoring improves code clarity and reduces unnecessary complexity.

**Technical Details:** The `Popen::execute_process` function previously included a parameter for an exception object that was declared but never actually utilized within the function's implementation. This PR removes that redundant parameter from the function's signature and all associated declarations. The change simplifies the function's interface, making it clearer what inputs are truly necessary and reducing potential confusion for future maintainers.

#### [#1950: tests: silentpayments: check found outputs are distinct in vector tests](https://github.com/bitcoin-core/secp256k1/pull/1950)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*

#### [#1933: refactor: introduce `ecmult_const_ge` helper (preventing accidential gej leaks)](https://github.com/bitcoin-core/secp256k1/pull/1933)
**Author:** [@theStack](https://github.com/theStack) | **[Security & Consensus]** *(Activity: 6 review events)*

#### [#36364: tools: Call SHA256AutoDetect in bitcoin-util, bitcoin-tx and bitcoin-wallet](https://github.com/bitcoin/bitcoin/pull/36364)
**Author:** [@torkelrogstad](https://github.com/torkelrogstad) | **[Performance & Optimization]** *(Activity: 5 review events)*
> This PR improves the performance of cryptographic operations in `bitcoin-util`, `bitcoin-tx`, and `bitcoin-wallet` by enabling automatic detection and use of optimized SHA256 implementations. This results in faster execution for these command-line tools.

**Technical Details:** The change integrates the `SHA256AutoDetect()` function call into the initialization sequences of `bitcoin-util`, `bitcoin-tx`, and `bitcoin-wallet`. This function dynamically probes the system for available hardware acceleration (e.g., SHA extensions on x86-64 architectures) and selects the most performant SHA256 implementation. By leveraging these optimized cryptographic primitives, the tools can execute hashing operations, such as those involved in transaction signing and address generation, significantly faster.

#### [#36415: rpc: clarify preciousblock help text](https://github.com/bitcoin/bitcoin/pull/36415)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Wallet & User Tools]** *(Activity: 5 review events)*
> This PR improves the help text for the `preciousblock` RPC command, making its purpose and usage clearer. Better documentation helps users understand and correctly utilize Bitcoin Core's features.

**Technical Details:** The change involves updating the string literal that provides the help message for the `preciousblock` RPC. This is a purely documentation-related modification within the RPC interface definition. The goal is to provide a more precise and understandable explanation of what `preciousblock` does, such as marking a block as preferred for chain selection, to aid developers and users.

#### [#36404: fuzz: don't set random state for private broadcast test](https://github.com/bitcoin/bitcoin/pull/36404)
**Author:** [@andrewtoth](https://github.com/andrewtoth) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR refines a fuzzing test related to private broadcast by removing an unnecessary random state initialization. This makes the test more focused and potentially more effective at finding specific issues.

**Technical Details:** Within the context of a fuzzing test specifically targeting private broadcast functionality, this PR removes a call that initializes or seeds a random number generator. By doing so, the test's input generation becomes more deterministic or solely controlled by the fuzzer's own mechanisms. This prevents potential interference from an additional, possibly conflicting, random state, allowing the fuzzer to explore the target code paths more effectively.

#### [#36300: [32.x] More Backports](https://github.com/bitcoin/bitcoin/pull/36300)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR integrates a collection of recent bug fixes and minor improvements from the main development branch into the 32.x release branch. This ensures that the stable release benefits from the latest code enhancements and stability fixes.

**Technical Details:** This is a routine backporting PR, typically involving cherry-picking or merging a series of commits from the `master` (or `main`) branch into a designated release branch, such as `32.x`. The specific changes are not detailed in the title but generally include bug fixes, minor performance tweaks, and non-breaking feature updates that have been deemed stable and ready for a release. The process involves careful conflict resolution and verification to maintain the stability of the target branch.

#### [#36377: doc: add 461 (Deterministic ECDSA signatures with low-R grinding) to bips.md](https://github.com/bitcoin/bitcoin/pull/36377)
**Author:** [@theStack](https://github.com/theStack) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR updates the project's documentation by adding BIP 461, which specifies deterministic ECDSA signatures with low-R grinding, to the `bips.md` file. This ensures that the documentation accurately reflects relevant Bitcoin Improvement Proposals.

**Technical Details:** The change involves a straightforward modification to the `bips.md` markdown file within the Bitcoin Core repository. A new entry for BIP 461 is added, including its title and potentially a link to the official BIP document. This update helps maintain comprehensive and up-to-date documentation, making it easier for developers and users to discover and reference important Bitcoin standards and specifications.

#### [#36381: test: avoid testing at the exact `-maxfeerate` boundary](https://github.com/bitcoin/bitcoin/pull/36381)
**Author:** [@ismaelsadeeq](https://github.com/ismaelsadeeq) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR refines a test by avoiding edge-case testing at the exact maximum fee rate boundary. This makes the test more robust and less prone to flakiness due to precision issues.

**Technical Details:** The test in question likely involves scenarios where transaction fee rates are compared against the configured `-maxfeerate` option. This PR modifies the test's input values or assertions to ensure that the tested fee rates are either clearly above or clearly below the boundary, rather than precisely at it. This avoids potential issues arising from floating-point comparisons, off-by-one errors, or subtle interpretations of boundary conditions, making the test more reliable and stable.

#### [#36275: build: enable `-Wunused-const-variable`](https://github.com/bitcoin/bitcoin/pull/36275)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR enhances code quality by enabling the `-Wunused-const-variable` compiler warning during the build process. This helps developers identify and remove unnecessary constant variables, leading to cleaner and more efficient code.

**Technical Details:** The modification involves adding the `-Wunused-const-variable` flag to the compiler options within the build system (e.g., `configure.ac`, `Makefile.am`, or CMakeLists.txt). This flag instructs the compiler to emit warnings for `const` variables that are declared but never used, promoting better coding practices. While not changing runtime behavior, it improves the codebase's maintainability and reduces potential for dead code by enforcing stricter compiler checks.

#### [#1949: ecdsa: Clarify derivation of the r check in `_sig_verify`](https://github.com/bitcoin-core/secp256k1/pull/1949)
**Author:** [@real-or-random](https://github.com/real-or-random) | **[Security & Consensus]** *(Activity: 4 review events)*

#### [#36024: ci: Make `test_bitcoin-qt.exe` output visible](https://github.com/bitcoin/bitcoin/pull/36024)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR improves the Continuous Integration (CI) system by making the output of `test_bitcoin-qt.exe` visible during test runs. This significantly aids in debugging failures related to the Bitcoin Core GUI, allowing developers to quickly diagnose and resolve issues.

**Technical Details:** The change involves modifying the CI configuration scripts (e.g., GitHub Actions workflows) to capture and display the standard output and standard error streams generated by the `test_bitcoin-qt.exe` executable. Previously, this output might have been suppressed or redirected, making it difficult to understand why GUI tests failed. By exposing this information, developers gain crucial insights into the test execution environment and application behavior during automated testing, streamlining the debugging process.

#### [#36400: [32.x] 32.0rc3](https://github.com/bitcoin/bitcoin/pull/36400)
**Author:** [@fanquake](https://github.com/fanquake) | **[Strategic Initiatives]** *(Activity: 3 review events)*
> This PR prepares the third release candidate for Bitcoin Core version 32.0. It bundles various bug fixes, performance improvements, and new features accumulated since the previous release candidate, ensuring a stable and robust final release.

**Technical Details:** As a release candidate, this PR primarily involves merging and stabilizing the `32.x` development branch into a release tag. It includes a comprehensive set of changes from numerous individual PRs, covering updates to the P2P network, wallet functionality, RPC interfaces, and underlying consensus logic. The process typically involves extensive testing and integration to ensure all components function cohesively before the final release, marking a significant project milestone.

#### [#1946: doc: clean up lingering ECMULT_WINDOW_SIZE comment](https://github.com/bitcoin-core/secp256k1/pull/1946)
**Author:** [@Yudis-bit](https://github.com/Yudis-bit) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*

#### [#36391: test: fix typo in rpc_psbt](https://github.com/bitcoin/bitcoin/pull/36391)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR corrects a minor typo within the test suite for Partially Signed Bitcoin Transactions (PSBT) RPCs. This ensures the accuracy and reliability of automated tests, which are crucial for maintaining the integrity of wallet functionality.

**Technical Details:** The change specifically targets a string literal or variable name within a test case file, likely `test/functional/rpc_psbt.py` or a similar C++ test. By correcting the typo, the test logic becomes more precise, preventing potential misinterpretations or failures in future test runs. This is a localized fix that improves the robustness of the existing test infrastructure without altering any production code.

#### [#1953: ci: bump macOS ARM64 runner to macos-15](https://github.com/bitcoin-core/secp256k1/pull/1953)
**Author:** [@theStack](https://github.com/theStack) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*

#### [#36411: ci: drop `-Wno-error=maybe-uninitialized` from win64 cxx flags](https://github.com/bitcoin/bitcoin/pull/36411)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR removes a specific compiler flag for Windows 64-bit builds in the continuous integration system. This allows the compiler to report potential 'maybe-uninitialized' warnings as errors, improving code quality by catching such issues early.

**Technical Details:** The change modifies the CI configuration files, specifically the C++ compiler options for the `win64` target, by removing the `-Wno-error=maybe-uninitialized` flag. With this flag removed, the build system will now treat any `maybe-uninitialized` warnings as compilation errors. This enforces a stricter code quality standard, ensuring that developers address potential initialization issues before code is merged into the codebase.

#### [#36412: ci: drop `-U_FORTIFY_SOURCE` from TSAN job](https://github.com/bitcoin/bitcoin/pull/36412)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR removes a specific compiler flag from the ThreadSanitizer (TSAN) continuous integration job. This change ensures that TSAN can operate without interference from `_FORTIFY_SOURCE`, potentially improving its effectiveness in detecting threading issues.

**Technical Details:** The `-U_FORTIFY_SOURCE` flag undefines the `_FORTIFY_SOURCE` macro, which enables certain buffer overflow checks at compile time. By removing this flag specifically from the TSAN job's compiler options, it ensures that `_FORTIFY_SOURCE` is not explicitly undefined during TSAN builds. This prevents potential conflicts or ensures that TSAN's own instrumentation for detecting threading issues is not hindered by or interfering with `_FORTIFY_SOURCE`'s runtime checks, allowing for more accurate and comprehensive analysis.

#### [#1947: musig: test nonce_gen_counter with random counters](https://github.com/bitcoin-core/secp256k1/pull/1947)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Security & Consensus]** *(Activity: 1 review events)*

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#36340: util: cap Sock::WaitMany timeout to fix -rpcclienttimeout=0 on macOS](https://github.com/bitcoin/bitcoin/pull/36340)
**Author:** [@kriss39](https://github.com/kriss39) | **[Wallet & User Tools]** *(Activity: 22 review events this week)*
> This PR fixes an issue on macOS where setting the RPC client timeout to zero would cause unexpected behavior. It caps the `Sock::WaitMany` timeout to ensure proper functionality and prevent potential hangs or errors specific to the macOS platform.

#### [#36365: fees: fall back to `block_policy` and minor api change](https://github.com/bitcoin/bitcoin/pull/36365)
**Author:** [@ismaelsadeeq](https://github.com/ismaelsadeeq) | **[Performance & Optimization]** *(Activity: 12 review events this week)*
> This PR enhances the fee estimation logic by introducing a fallback mechanism to `block_policy` when more precise fee estimation methods are unavailable. This ensures more reliable transaction fee recommendations, especially under unusual network conditions or when specific fee targets are difficult to meet.

#### [#36330: [NO MERGE] wallet: don't resubmit transactions under -privatebroadcast](https://github.com/bitcoin/bitcoin/pull/36330)
**Author:** [@instagibbs](https://github.com/instagibbs) | **[Network & Privacy]** *(Activity: 12 review events this week)*
> This PR prevents the wallet from automatically resubmitting transactions when the `-privatebroadcast` option is enabled. This ensures that transactions intended for private broadcast are not inadvertently exposed to the wider network.

#### [#36336: log: move CreateNewBlock() log line behind a new mining category](https://github.com/bitcoin/bitcoin/pull/36336)
**Author:** [@ismaelsadeeq](https://github.com/ismaelsadeeq) | **[Maintenance & Tech Debt]** *(Activity: 12 review events this week)*
> This PR refines the logging system by moving the `CreateNewBlock()` log line under a new, dedicated mining category. This allows users to more easily filter and control log output specifically related to block creation.

#### [#1948: tests: add ECDSA verify case where r + n overflows p](https://github.com/bitcoin-core/secp256k1/pull/1948)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 9 review events this week)*

## 🗓️ Dev Meeting
Summary of the core dev IRC meeting on 2026-10-01 with 24 participants.

- Fuzzing WG Update: eugenesiegel and marcofleon reported no updates this week, with marcofleon indicating a possible update next week.
- Benchmarking WG Update: l0rinc had no update but plans to present next week. andrewtoth_ requested removal as a lead, stating continued active review of speedup PRs and benchmarking, but no regular updates. abubakarsadiq suggested archiving the WG if l0rinc also has no update.
- QML GUI WG Update: johnny9dev reported pseudoramdom completed a comprehensive UX overhaul, nearing a release-ready design. Feedback is being sought, with the current work available in the qt6 branch. Pre-built binaries will be available on bitcoincore.app.
- QA WG Update: brunoerg launched mutanthub.space, a collaborative mutation testing platform designed to centralize mutant submission, reproduction, and evaluation. This platform will replace bitcoincore.space and secp256k1.space. Mutants can be submitted by clicking lines in source code or via bulk import, with approval required. Killed mutants are defined as those detected by existing tests at the mutant's creation commit point.
- Bitcoin Core 32.0 Milestone: dzxzg requested assistance with remaining items on milestone #84.
- Automated Review Proposals: eugenesiegel proposed a bot/label system for requesting fuzzamoto builds on PRs, noting the 'ir' scenario covers most P2P code. willcl-ark proposed a limited trial of automated AI reviews (via 'ralph' bot) on PRs, initially for external contributors, citing testing on git.fish.foo/bitcoin/bitcoin. Concerns were raised by andrewtoth_ and abubakarsadiq regarding LLM output potentially being noise and requiring distillation by experienced contributors.

**Action Items:**
- l0rinc to prepare a presentation for the Benchmarking WG next week.
- johnny9dev to gather more feedback on the QML GUI UX overhaul.
- willcl-ark to provide more details/links to bot code/prompts for the AI review bot.
- Developers to review and assist with remaining items on Bitcoin Core 32.0 milestone #84.

## 🗣️ Research & Governance
Top active threads across mailing lists and research forums.

### [Shielded Bitcoin: Private Transfers on the Bitcoin L1](https://delvingbitcoin.org/t/shielded-bitcoin-private-transfers-on-the-bitcoin-l1/2912/4)
**Source:** Delving | **Started By:** {'username': 'misha komarov', 'uuid': 'auto_misha_komarov'} | **Messages:** 9
> We're exploring how to enable private Bitcoin transactions directly on the main blockchain, focusing on a secure and lightweight way to verify these transfers without needing new network rules.

**Technical Details:** The discussion centers on the verification mechanism for 'Shielded Bitcoin' L1 privacy, specifically distinguishing the proposed 'amount of PoW' approach from traditional SPV proofs. A key architectural debate has emerged regarding the necessity of a robust challenge mechanism for such proofs, potentially leveraging a 'heavier chain' or similar. This is critical for ensuring security and preventing fraud, especially if the model introduces concepts akin to sidechains with different miner sets, requiring further clarification on dispute resolution.

### [Stats on compact block reconstructions](https://delvingbitcoin.org/t/stats-on-compact-block-reconstructions/1052/54)
**Source:** Delving | **Started By:** {'username': '0xB10C', 'uuid': 'can_0xb10c'} | **Messages:** 8
> We're analyzing how quickly new blocks are shared across the Bitcoin network to ensure transactions confirm reliably and the network remains robust. While some propagation metrics show improvement, we're investigating all factors influencing block relay speed.

**Technical Details:** The discussion began by examining compact block reconstruction statistics, specifically the frequency of extra `getblocktxn` round-trips. However, analysis of KIT's propagation delay graph reveals that while the 90% line shows improvement, the 50% line remains unchanged, suggesting other bottlenecks are at play. Gregory Sanders points to 'laggy GETDATA responses' and node validation load as potential contributors to transaction relay delays. Johnny Santos further hypothesizes that external network events, such as the ColdCard hack's impact on mempools and RBF activity, could be influencing these observed propagation patterns, necessitating a broader investigation into all factors affecting block relay.

### [What does "post-quantum" actually mean for a Bitcoin L2 when settlement still happens on a non-PQ L1?](https://delvingbitcoin.org/t/what-does-post-quantum-actually-mean-for-a-bitcoin-l2-when-settlement-still-happens-on-a-non-pq-l1/2715/2)
**Source:** Delving | **Started By:** {'username': 'Hal_03', 'uuid': 'auto_hal_03'} | **Messages:** 6
> Developers are exploring how to future-proof Bitcoin's off-chain payment channels against quantum computing threats, ensuring secure and efficient transactions for years to come.

**Technical Details:** The discussion centers on securing Bitcoin's off-chain state channels against future quantum computing threats. An argument was made that the quantum security of Layer 2 (L2) solutions is inherently linked to Layer 1 (L1) Bitcoin security, implying that if L2s are vulnerable, so is Bitcoin itself. References to Post-Quantum Lightning Network (PQLN) research were made, suggesting existing work addresses these concerns. The core technical challenge remains integrating post-quantum cryptography into L2 architectures while maintaining compatibility and efficiency.

### [PQC output type discussion](https://delvingbitcoin.org/t/pqc-output-type-discussion/2749/38)
**Source:** Delving | **Started By:** {'username': 'Pieter Wuille', 'uuid': 'can_pieter_wuille'} | **Messages:** 3
> Developers are actively planning for Bitcoin's future security against quantum computers by exploring new transaction types. This ensures your funds remain safe and resilient for decades to come.

**Technical Details:** The ongoing discussion on Post-Quantum Cryptography (PQC) transaction output types is grappling with the implications of address reuse, a persistent user behavior that complicates security guarantees. While some propose education and wallet design as mitigations, others express skepticism about their full efficacy in minimizing exposure to quantum threats. A critical architectural debate centers on how PQC integration strategies will influence the eventual, credible disabling of current Elliptic Curve (EC) cryptography, emphasizing the need for design choices that facilitate a secure and reliable transition.

### [PQLN: Post-Quantum Security for the Bitcoin Lightning Network's Off-Chain Surfaces](https://delvingbitcoin.org/t/pqln-post-quantum-security-for-the-bitcoin-lightning-networks-off-chain-surfaces/2893/2)
**Source:** Delving | **Started By:** {'username': 'user1', 'uuid': 'auto_ahmet_kurt'} | **Messages:** 3
> Researchers are developing PQLN, a new project to future-proof the Lightning Network against potential threats from quantum computing. This initiative aims to ensure the long-term safety and resilience of Lightning transactions.

**Technical Details:** Ahmet Kurt introduced PQLN, a project focused on integrating hybrid post-quantum (PQ) cryptographic extensions into the Lightning Network. Following a detailed reply from Laolu, the discussion highlights the need for more context on PQLN's architectural approach and its integration strategy within the existing Lightning protocol. The next steps involve Ahmet providing further technical details to address potential challenges and outline how PQLN plans to secure Lightning against quantum threats, likely sparking debate on feasibility and impact.

## 🏆 Contributor Shoutouts
### 🎉 First-Time Merges
Welcome to the codebase: [@David-Uka](https://github.com/David-Uka), [@FlashWayne](https://github.com/FlashWayne)

### ✍️ Top Authors
The most active PR authors this week: [@fanquake](https://github.com/fanquake), [@ismaelsadeeq](https://github.com/ismaelsadeeq), [@brunoerg](https://github.com/brunoerg), [@hebasto](https://github.com/hebasto), [@David-Uka](https://github.com/David-Uka)

### 🕵️ Top Reviewers
Providing critical review and testing: [@maflcko](https://github.com/maflcko), [@fametrano](https://github.com/fametrano), [@hebasto](https://github.com/hebasto), [@l0rinc](https://github.com/l0rinc), [@achow101](https://github.com/achow101)
