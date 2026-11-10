# 📰 This Week in Bitcoin (2026-11-02 to 2026-11-08)

## 📌 The TL;DR
- A significant technical shift is the intensified focus on foundational code quality and reliability, evidenced by a high volume of merged PRs dedicated to expanding test coverage, improving test framework robustness, enhancing static analysis, and standardizing cross-platform build environments (e.g., `clang-cl` for Windows, Guix variants, updated compilers/SDKs).
- Ongoing development and discussions are centered on refining P2P networking for privacy and efficiency (e.g., Tor validation, package relay, Minisketch updates), evolving wallet capabilities (e.g., PSBT v0, RBF transaction details), and exploring advanced protocol features like P2MR, Lightning Network scalability, and improved node connectivity for a more robust network.

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

#### [#31507: build: Use clang-cl to build on Windows natively](https://github.com/bitcoin/bitcoin/pull/31507)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 80 review events)*
> This PR updates the build system to use `clang-cl` for native Windows builds of Bitcoin Core. Leveraging `clang-cl` offers potential improvements in build times, better diagnostics, and alignment with modern compiler features across platforms.

**Technical Details:** The build configuration (likely CMake or Autotools) is adjusted to detect and utilize `clang-cl`, Clang's MSVC-compatible driver, as the C/C++ compiler when building natively on Windows. This involves setting appropriate compiler paths, flags, and library dependencies to ensure ABI compatibility with MSVC while benefiting from Clang's frontend capabilities. The change standardizes the compiler toolchain somewhat, aligning Windows builds more closely with Linux/macOS Clang-based compilation workflows.

#### [#35728: rpc: Properly throw on internal I/O errors in GetTransaction](https://github.com/bitcoin/bitcoin/pull/35728)
**Author:** [@maflcko](https://github.com/maflcko) | **[Wallet & User Tools]** *(Activity: 31 review events)*
> This PR improves the `GetTransaction` RPC by ensuring it properly reports internal I/O errors. This makes the RPC more robust and provides clearer feedback to users or applications when underlying data access issues occur.

**Technical Details:** The `GetTransaction` RPC is modified to explicitly catch and re-throw exceptions originating from internal I/O operations, such as database access failures. This change ensures that callers receive appropriate error responses instead of encountering silent failures or unexpected behavior, significantly improving the reliability and debuggability of the RPC interface.

#### [#36091: test: Add debug output to common tested types](https://github.com/bitcoin/bitcoin/pull/36091)
**Author:** [@rustaceanrob](https://github.com/rustaceanrob) | **[Maintenance & Tech Debt]** *(Activity: 24 review events)*
> This PR enhances the debuggability of Bitcoin Core's test suite by adding debug output for commonly tested data types. This makes it easier for developers to diagnose test failures and understand test execution.

**Technical Details:** This PR involves implementing `operator<<` overloads or similar serialization functions for various core data structures (e.g., `COutPoint`, `CTxIn`, `CTxOut`) that are frequently used and compared within the test suite. When a test assertion fails, these debug outputs will provide more informative messages, displaying the actual values of the objects being compared, which significantly aids in pinpointing the exact discrepancy.

#### [#36193: guix: introduce a minimal `linux-base-gcc` variant](https://github.com/bitcoin/bitcoin/pull/36193)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 23 review events)*
> This PR introduces a new, minimal GCC variant for Guix builds, which helps reduce the size and complexity of the build environment for Linux. This streamlines the reproducible build process for Bitcoin Core.

**Technical Details:** The change involves adding a new package definition within the Guix build system, specifically a `linux-base-gcc` variant. This variant is configured with a reduced set of features and dependencies compared to the standard GCC package, focusing only on what's strictly necessary for compiling Bitcoin Core on Linux. This optimization aims to minimize the Guix store footprint and build times, contributing to more efficient and reproducible builds.

#### [#35170: test: Better test coverage for ParseHDKeypath()](https://github.com/bitcoin/bitcoin/pull/35170)
**Author:** [@optout21](https://github.com/optout21) | **[Wallet & User Tools]** *(Activity: 22 review events)*
> This PR improves the test coverage for the `ParseHDKeypath()` function, which is responsible for interpreting hierarchical deterministic (HD) key paths. This ensures the function correctly handles various input formats, enhancing the reliability of wallet operations.

**Technical Details:** The PR adds new unit tests or extends existing ones for the `ParseHDKeypath()` function. These tests likely cover a wider range of valid and invalid HD key path strings, including different prefix types (e.g., `m/`, `M/`), hardened vs. non-hardened derivations, and various index formats. The goal is to ensure the function robustly parses and validates all expected key path syntaxes and correctly rejects malformed inputs, preventing errors in HD wallet derivation.

#### [#36192: test: cover unsatisfiable mining timestamp](https://github.com/bitcoin/bitcoin/pull/36192)
**Author:** [@Sjors](https://github.com/Sjors) | **[Maintenance & Tech Debt]** *(Activity: 20 review events)*
> This PR adds a test case to cover scenarios where a mining timestamp is unsatisfiable. This improves the robustness of the test suite by ensuring the system handles edge cases related to block timestamp validation.

**Technical Details:** The change introduces a new functional or unit test that specifically constructs a scenario where a block's timestamp is invalid according to consensus rules, such as being too far in the future or past, or violating median-time-past rules. The test then asserts that the node correctly rejects such a block. This verifies the implementation of timestamp validation logic and ensures the network's integrity against invalid blocks.

#### [#36142: net: validate Tor onion service replies and cached keys](https://github.com/bitcoin/bitcoin/pull/36142)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Network & Privacy]** *(Activity: 18 review events)*
> This PR enhances the security and reliability of Bitcoin Core's Tor connections. It ensures that the client properly validates responses from Tor onion services and their cached keys, preventing potential connection issues or attacks.

**Technical Details:** This change introduces validation logic for Tor onion service replies, specifically checking the `AUTH_CHALLENGE` and `AUTH_REPLY` messages to ensure consistency and correct key derivation. It also validates cached onion service keys against the expected service ID, preventing the use of stale or malicious cached data. This hardens the Tor connection establishment process against various forms of manipulation.

#### [#36539: gui: Use PSBT v0](https://github.com/bitcoin/bitcoin/pull/36539)
**Author:** [@davidgumberg](https://github.com/davidgumberg) | **[Wallet & User Tools]** *(Activity: 17 review events)*
> This PR updates the Bitcoin Core GUI to utilize Partially Signed Bitcoin Transactions (PSBT) version 0. This integration significantly improves interoperability with external signing devices like hardware wallets, enhancing user security and convenience for transaction creation.

**Technical Details:** This change modifies the GUI's transaction creation and signing workflows to leverage PSBT v0 internally. Instead of directly constructing raw transactions, the GUI now generates and processes PSBT v0 objects, facilitating a standardized exchange format with external signers. This involves adapting `WalletModel` and `SendCoinsDialog` to serialize and deserialize PSBTs, ensuring compatibility with the `signrawtransactionwithkey` and `walletprocesspsbt` RPCs. The update streamlines multi-party signing and hardware wallet integration by standardizing the transaction data format presented to the user.

#### [#36036: build: Bump clang minimum supported version to 19](https://github.com/bitcoin/bitcoin/pull/36036)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 14 review events)*
> This PR updates the minimum required Clang compiler version to 19 for building Bitcoin Core. This ensures developers are using a modern compiler, benefiting from newer features, bug fixes, and improved code generation.

**Technical Details:** The change involves modifying the build system configuration to check for Clang version 19 or newer during compilation. This ensures that continuous integration (CI) environments and developer setups are aligned with the latest compiler toolchains. This alignment can potentially enable future C++ standard features or optimizations, improving the overall development environment.

#### [#35598: test: cover feeThreshold = MAX_MONEY in interface_ipc_mining.py](https://github.com/bitcoin/bitcoin/pull/35598)
**Author:** [@Sjors](https://github.com/Sjors) | **[Maintenance & Tech Debt]** *(Activity: 14 review events)*
> This PR adds a test case to cover the `feeThreshold = MAX_MONEY` scenario in the `interface_ipc_mining.py` test. This ensures the mining interface correctly handles extreme fee threshold values.

**Technical Details:** The change extends the `interface_ipc_mining.py` functional test to include a specific test vector where the `feeThreshold` parameter for mining operations is set to `MAX_MONEY`. The test then verifies that the system behaves as expected, likely by ensuring that no transactions are included if the threshold is effectively infinite, or that the system doesn't crash or produce incorrect results. This validates the robustness of the mining interface's fee handling.

#### [#36489: wallet: rpc: Add snake_case aliases for wallet funding options](https://github.com/bitcoin/bitcoin/pull/36489)
**Author:** [@maflcko](https://github.com/maflcko) | **[Wallet & User Tools]** *(Activity: 13 review events)*
> This PR adds `snake_case` aliases for existing `camelCase` wallet funding options in RPC calls. This improves API consistency and developer experience by offering more idiomatic naming conventions.

**Technical Details:** The implementation modifies the RPC argument parsing logic for wallet funding-related RPCs, such as `fundrawtransaction`. It introduces alternative `snake_case` names for existing `camelCase` parameters, allowing clients to use either convention. This is typically achieved by adding mapping logic that translates the `snake_case` alias to its internal `camelCase` counterpart before processing the argument, ensuring backward compatibility while improving usability.

#### [#36333: wallet: Delete `removeprunedfunds` RPC](https://github.com/bitcoin/bitcoin/pull/36333)
**Author:** [@davidgumberg](https://github.com/davidgumberg) | **[Wallet & User Tools]** *(Activity: 12 review events)*
> This PR removes the deprecated `removeprunedfunds` RPC and associated transaction deletion code from the wallet. This simplifies the codebase by eliminating unused and potentially confusing functionality, improving maintainability.

**Technical Details:** The PR systematically removes the `removeprunedfunds` RPC endpoint and all underlying code paths responsible for deleting transactions from the wallet database. This includes removing calls to `CWallet::RemovePrunedFunds` and related database operations, as this functionality is no longer necessary or desired in modern wallet management, reducing complexity and potential for misuse.

#### [#36470: test: make p2p_eviction actually exercise block-time protection](https://github.com/bitcoin/bitcoin/pull/36470)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 12 review events)*
> This PR enhances a P2P test to accurately verify Bitcoin Core's peer eviction logic, specifically ensuring that peers are correctly protected from eviction if they have recently provided valid blocks. This improves the reliability of the P2P network by preventing the premature disconnection of useful peers.

**Technical Details:** The `p2p_eviction.py` functional test is modified to simulate scenarios where peers provide blocks within the `BLOCK_TIME_PROTECTION_WINDOW`. This involves carefully timing block announcements and peer connections/disconnections within the test framework. The changes ensure that the test asserts the correct behavior of the eviction algorithm, verifying that peers contributing valid blocks are not evicted, thereby confirming the effectiveness of the block-time protection mechanism in `CNode`'s eviction logic.

#### [#36348: doc/i2p: mention -privatebroadcast bypasses persistent address](https://github.com/bitcoin/bitcoin/pull/36348)
**Author:** [@jpk68](https://github.com/jpk68) | **[Maintenance & Tech Debt]** *(Activity: 12 review events)*
> This PR updates the I2P documentation to clarify an important privacy-related behavior. It explicitly states that using the `-privatebroadcast` option bypasses the use of a persistent I2P address, which is crucial information for users concerned about their network privacy.

**Technical Details:** This documentation update adds a note to the I2P-specific documentation, likely within `doc/i2p.md`. The added text explains that when the `-privatebroadcast` configuration option is enabled, the Bitcoin Core node will not use a persistent I2P address for outgoing connections. This informs users that this setting impacts the long-term unlinkability of their I2P identity, providing critical context for privacy-conscious deployments.

#### [#35041: descriptor: speed-up `Parse` (xpub/xpriv) in ~30%](https://github.com/bitcoin/bitcoin/pull/35041)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Performance & Optimization]** *(Activity: 11 review events)*
> This PR significantly improves the parsing speed of extended public and private keys (xpub/xpriv) within descriptors by approximately 30%. This makes wallet and descriptor operations faster and more efficient, especially for users with many descriptors or complex wallet setups.

**Technical Details:** The optimization focuses on the `Parse` method for descriptor strings containing xpub/xpriv components. This likely involves profiling the existing implementation to identify bottlenecks, then applying algorithmic improvements such as optimizing string manipulation, reducing redundant computations, or using more efficient data structures during the parsing process. For example, it might involve pre-allocating buffers, using faster string searching algorithms, or caching intermediate results.

#### [#36578: p2p: clean up a 1p1c package child that is already in the mempool](https://github.com/bitcoin/bitcoin/pull/36578)
**Author:** [@instagibbs](https://github.com/instagibbs) | **[Network & Privacy]** *(Activity: 11 review events)*
> This update refines how Bitcoin nodes handle transaction packages, specifically when a child transaction is already known. It cleans up redundant data, improving the efficiency and reliability of transaction relay across the network.

**Technical Details:** This PR addresses a specific edge case in the P2P transaction relay logic concerning "one-parent-one-child" (1p1c) transaction packages. When a node receives a 1p1c package where the child transaction is already present in its mempool, the existing logic might not correctly clean up the temporary package state. This PR ensures that if the child transaction is already accepted, the corresponding package data is properly removed, preventing unnecessary processing and potential resource leaks. This improves the robustness and efficiency of mempool management and transaction relay.

#### [#36494: wallet: reject unknown options in sendall](https://github.com/bitcoin/bitcoin/pull/36494)
**Author:** [@thomasbuilds](https://github.com/thomasbuilds) | **[Wallet & User Tools]** *(Activity: 11 review events)*
> This PR improves the `sendall` RPC by making it more robust against invalid input. It now explicitly rejects unknown options, preventing potential misuse or unexpected behavior.

**Technical Details:** The `sendall` RPC handler is modified to iterate through the provided options. Instead of silently ignoring unrecognized parameters, the code now checks if each option is part of a predefined whitelist of accepted parameters. If an unknown option is encountered, the RPC call will return an error, guiding users to provide valid inputs and preventing silent failures or misinterpretations.

#### [#36252: ci, iwyu: skip subtrees in compilation database](https://github.com/bitcoin/bitcoin/pull/36252)
**Author:** [@ryanofsky](https://github.com/ryanofsky) | **[Maintenance & Tech Debt]** *(Activity: 11 review events)*
> This PR updates the CI and `iwyu` (Include What You Use) tooling to skip specific subtrees when generating the compilation database. This optimizes the build process and static analysis, making CI runs faster and more efficient.

**Technical Details:** The changes involve modifying the build system's configuration, likely `CMake` or `Makefile` rules, to exclude certain directories or source files from being processed by `iwyu` or included in the `compile_commands.json` database. This is typically done for third-party libraries or generated code where `iwyu` analysis is not beneficial or causes false positives. By skipping these subtrees, the PR reduces the scope of static analysis, speeding up CI checks and improving the signal-to-noise ratio of `iwyu` reports.

#### [#36747: Update libmultiprocess subtree to add nonunix platform support and fix race conditions](https://github.com/bitcoin/bitcoin/pull/36747)
**Author:** [@ryanofsky](https://github.com/ryanofsky) | **[Maintenance & Tech Debt]** *(Activity: 11 review events)*
> This PR updates the internal `libmultiprocess` subtree, adding support for non-Unix platforms and fixing existing race conditions. This enhances the robustness and portability of Bitcoin Core components that rely on this library.

**Technical Details:** The update integrates a newer version of the `libmultiprocess` subtree into the Bitcoin Core repository. Key improvements include the addition of platform-specific code and conditional compilation to enable functionality on non-Unix operating systems, such as Windows. Furthermore, the update resolves identified race conditions within the library's existing code, improving the reliability of inter-process communication and synchronization mechanisms used by various Bitcoin Core modules.

#### [#36712: fees: prevent divide by zero in CFeeRate](https://github.com/bitcoin/bitcoin/pull/36712)
**Author:** [@ismaelsadeeq](https://github.com/ismaelsadeeq) | **[Security & Consensus]** *(Activity: 10 review events)*
> This PR fixes a potential bug in the fee calculation logic by preventing a divide-by-zero error in the `CFeeRate` class. This ensures the stability and correctness of fee estimations, especially in edge cases, and prevents potential node crashes.

**Technical Details:** The `CFeeRate` class, which represents transaction fee rates, is modified to explicitly handle cases where the denominator (typically transaction size or weight) could be zero. Before performing division, a check is added to ensure the divisor is non-zero. In such edge cases, the fee rate might be set to a default safe value (e.g., zero) or an error condition is handled, preventing a program crash or undefined behavior that could be exploited for denial of service.

#### [#36554: cmake: Reject warnings in `check_cxx_source_compiles_with_flags()`, use `-msse4.1` for SHA-NI](https://github.com/bitcoin/bitcoin/pull/36554)
**Author:** [@hebasto](https://github.com/hebasto) | **[Performance & Optimization]** *(Activity: 10 review events)*
> This PR improves Bitcoin Core's build system by making it more robust against compiler warnings and enabling specific CPU optimizations. It ensures that the build process fails on warnings during flag checks and explicitly uses SSE4.1 instructions for SHA-NI acceleration when available, boosting cryptographic performance.

**Technical Details:** This PR modifies the CMake build configuration. Firstly, it enhances `check_cxx_source_compiles_with_flags()` to treat compiler warnings as errors, ensuring stricter adherence to code quality standards during feature detection. Secondly, it explicitly adds the `-msse4.1` flag when compiling code that utilizes SHA-NI instructions, enabling hardware acceleration for SHA-256 computations on compatible CPUs, thereby improving cryptographic performance.

#### [#36788: test, bench: construct inputs/outputs declaratively in txpackage, duplicate_inputs and p2sh tests](https://github.com/bitcoin/bitcoin/pull/36788)
**Author:** [@yuvicc](https://github.com/yuvicc) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR refactors several test and benchmark suites to use a more declarative method for constructing transaction inputs and outputs. This improves the readability and maintainability of these tests, making them easier to understand and extend.

**Technical Details:** The implementation introduces helper functions or a domain-specific language (DSL) within the test framework to define transaction components (inputs, outputs, scripts) in a more concise and readable manner. Instead of imperative, step-by-step construction, tests for `txpackage`, `duplicate_inputs`, and `p2sh` now leverage these declarative constructs. This reduces boilerplate code, minimizes errors in test setup, and allows future test additions to be written more efficiently by focusing on the test logic rather than the transaction assembly details.

#### [#36679: ci: enable IPC in the i686 job](https://github.com/bitcoin/bitcoin/pull/36679)
**Author:** [@Sjors](https://github.com/Sjors) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR updates the continuous integration (CI) setup to enable Inter-Process Communication (IPC) for the i686 architecture job. This ensures that all tests, including those relying on IPC, can run correctly on this specific build environment, improving test coverage and reliability.

**Technical Details:** The change involves modifying the CI configuration for the i686 job, likely within a `.yml` or script file, to explicitly enable IPC capabilities. This typically means adjusting kernel parameters or container settings to allow processes to communicate via shared memory, message queues, or semaphores. This ensures that tests involving multiple interacting processes, such as those for `bitcoind` and `bitcoin-cli` or `bitcoin-wallet`, can execute without failure due to IPC restrictions.

#### [#36615: guix: add --no-same-owner to codesign.sh TAR_OPTIONS](https://github.com/bitcoin/bitcoin/pull/36615)
**Author:** [@marcofleon](https://github.com/marcofleon) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR updates the Guix build system to include `--no-same-owner` in the `TAR_OPTIONS` for `codesign.sh`. This ensures that the ownership of files within the generated tarball is not preserved, which can prevent issues when extracting on different systems or with different user permissions.

**Technical Details:** The modification is made within the `guix` build scripts, specifically targeting the `codesign.sh` script or its configuration. By adding `--no-same-owner` to the `TAR_OPTIONS`, the `tar` command will create archives where all files are owned by the user extracting the archive, rather than attempting to preserve the original owner/group from the build environment. This is crucial for reproducible builds and cross-platform compatibility.

#### [#36305: net: Use exclusive P2P listen sockets on Windows](https://github.com/bitcoin/bitcoin/pull/36305)
**Author:** [@winterrdog](https://github.com/winterrdog) | **[Network & Privacy]** *(Activity: 9 review events)*
> This PR improves network reliability on Windows by ensuring Bitcoin Core uses exclusive P2P listen sockets. This prevents conflicts with other applications trying to bind to the same port, leading to more stable node operation.

**Technical Details:** On Windows, the `SO_REUSEADDR` socket option allows multiple sockets to bind to the same address and port, which can lead to unexpected behavior or port conflicts. This PR modifies the socket creation and binding process for P2P listen sockets on Windows to explicitly disable `SO_REUSEADDR` or use an equivalent exclusive option (e.g., `SO_EXCLUSIVEADDRUSE`). This guarantees that only one instance of Bitcoin Core (or any application) can listen on a specific P2P port at a time, improving network stability and predictability.

#### [#36618: test: Wait for index sync in all tests](https://github.com/bitcoin/bitcoin/pull/36618)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 9 review events)*
> This PR improves the reliability of Bitcoin Core's test suite by ensuring that all tests wait for indexes to fully synchronize before proceeding. This prevents flaky test failures caused by race conditions and ensures consistent test results.

**Technical Details:** The test framework is enhanced to include a synchronization mechanism that explicitly waits for all relevant indexes (e.g., block index, transaction index, UTXO set) to be fully caught up and consistent across nodes or within a single node's state before test assertions are made. This typically involves polling index status RPCs or internal state until a synchronized state is confirmed, eliminating timing-dependent failures in automated tests.

#### [#36384: rpc: Use self.Arg<_>(name) helper over manual and duplicate parsing](https://github.com/bitcoin/bitcoin/pull/36384)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR refactors RPC argument parsing to use a new `self.Arg<_>(name)` helper, replacing manual and duplicated parsing logic. This simplifies RPC code, reduces boilerplate, and improves maintainability.

**Technical Details:** The refactoring introduces a standardized helper function or method within the RPC framework that encapsulates common argument parsing patterns. Existing RPC handlers are then updated to call this helper, eliminating redundant code blocks that previously performed type checking, default value assignment, and error handling for arguments. This promotes consistency across RPC methods and reduces the chance of parsing bugs.

#### [#1974: silentpayments: reject label tweaks that overflow the group order](https://github.com/bitcoin-core/secp256k1/pull/1974)
**Author:** [@theStack](https://github.com/theStack) | **[Security & Consensus]** *(Activity: 7 review events)*
> This PR for the `secp256k1` library fixes a critical issue in the Silent Payments protocol by ensuring that label tweaks cannot overflow the elliptic curve group order. This prevents potential cryptographic vulnerabilities and ensures the mathematical integrity of Silent Payments.

**Technical Details:** The change introduces validation logic within the `secp256k1` library's Silent Payments implementation. Specifically, before applying a label tweak to a public key, the tweak value is checked to ensure it is strictly less than the curve's group order (N). If an overflow condition is detected, the operation is rejected, preventing the creation of invalid public keys or potential small-subgroup attacks. This ensures all derived points remain on the curve and within the valid scalar range.

#### [#36405: test: look for the wtxid in p2p_blocksonly](https://github.com/bitcoin/bitcoin/pull/36405)
**Author:** [@fametrano](https://github.com/fametrano) | **[Network & Privacy]** *(Activity: 7 review events)*
> This PR enhances a P2P test to verify that `wtxid` (witness transaction ID) is correctly transmitted in `blocksonly` mode. This ensures that nodes operating in this mode can properly identify and request witness data for transactions within blocks, improving network efficiency and functionality.

**Technical Details:** The `p2p_blocksonly.py` functional test is updated to include assertions that check for the presence and correctness of `wtxid` in relevant P2P messages when a node is configured for `blocksonly` operation. This involves simulating a peer sending a block and then verifying that the receiving `blocksonly` node correctly processes the `wtxid` information. This is crucial for requesting missing witness data without downloading full transactions, optimizing bandwidth for `blocksonly` nodes.

#### [#35492: wallet: fail dump on incomplete writes](https://github.com/bitcoin/bitcoin/pull/35492)
**Author:** [@OSINTv96](https://github.com/OSINTv96) | **[Wallet & User Tools]** *(Activity: 7 review events)*
> This PR enhances the wallet dump process by explicitly failing if a write operation is incomplete, preventing the creation of corrupted backup files. This ensures the integrity of wallet backups, safeguarding user funds.

**Technical Details:** The change modifies the `dumpwallet` RPC and associated internal logic to rigorously check the completion status of all write operations to the backup file. If any data write fails or is only partially completed during the dump process, the entire operation will now terminate with an error. This prevents the generation of truncated or unusable wallet dump files, which could lead to data loss during recovery. By ensuring atomic and complete writes, the PR significantly improves the reliability and safety of wallet backups.

#### [#36344: wallet: reject duplicate inputs in sendall](https://github.com/bitcoin/bitcoin/pull/36344)
**Author:** [@Bruce039](https://github.com/Bruce039) | **[Wallet & User Tools]** *(Activity: 7 review events)*
> This PR improves the `sendall` RPC by preventing the use of duplicate transaction inputs. This ensures that transactions created via `sendall` are always valid and prevents potential errors or unexpected behavior from malformed input.

**Technical Details:** The `sendall` RPC's input processing logic is enhanced to include a check for duplicate UTXOs (Unspent Transaction Outputs) provided as inputs. Before constructing the transaction, the code will now identify if the same `txid:vout` pair appears multiple times in the input list. If duplicates are found, the RPC call will be rejected with an error, ensuring that only unique and valid inputs are used for transaction creation.

#### [#36772: test: Remove `BOOST_FAIL` and add info in descriptor_tests](https://github.com/bitcoin/bitcoin/pull/36772)
**Author:** [@rustaceanrob](https://github.com/rustaceanrob) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR refactors `descriptor_tests` by removing `BOOST_FAIL` and adding more informative messages to test failures. This improves the clarity and debuggability of test results, making it easier to identify and fix issues related to output descriptors.

**Technical Details:** The implementation replaces calls to `BOOST_FAIL` with more specific assertion macros or custom failure messages within the `descriptor_tests` suite. Instead of a generic failure, the tests now provide context-rich information, such as the specific descriptor string, expected outcome, and actual outcome, when a test fails. This enhancement significantly aids developers in quickly understanding the root cause of descriptor-related test failures without needing to step through the code in a debugger.

#### [#36623: build: enable `-Wunreachable-code-aggressive`](https://github.com/bitcoin/bitcoin/pull/36623)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR enables the `-Wunreachable-code-aggressive` compiler warning during the build process. This helps identify and eliminate dead code, improving code quality and reducing the attack surface by removing unused logic.

**Technical Details:** The implementation modifies the build system, likely `configure.ac` or `Makefile.am` for `autotools`, or `CMakeLists.txt` for `CMake`, to add the `-Wunreachable-code-aggressive` flag to the compiler options for C++ code. This warning level is more stringent than standard unreachable code warnings and helps detect more subtle cases of dead code paths. Enabling this flag requires reviewing and potentially fixing existing code to ensure no legitimate code is flagged, ultimately leading to a cleaner and more robust codebase.

#### [#36775: test: wallet: BnB marks exhaustive search complete](https://github.com/bitcoin/bitcoin/pull/36775)
**Author:** [@Conradgabe](https://github.com/Conradgabe) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR enhances wallet tests for the Branch and Bound (BnB) coin selection algorithm by ensuring that the exhaustive search completion is correctly marked. This improves the reliability and coverage of tests for a critical wallet component.

**Technical Details:** The PR modifies existing unit or functional tests related to the BnB coin selection algorithm. It introduces assertions or checks to verify that the algorithm correctly identifies when an exhaustive search for a coin selection solution has been completed. This ensures the algorithm's internal logic for determining search completeness is robust, preventing premature termination or incomplete exploration of viable branches.

#### [#36458: Test: Add script vectors for interpreter edges](https://github.com/bitcoin/bitcoin/pull/36458)
**Author:** [@benthecarman](https://github.com/benthecarman) | **[Security & Consensus]** *(Activity: 6 review events)*
> This PR adds new test vectors to thoroughly check the Bitcoin Script interpreter's behavior at its operational limits and edge cases. This helps ensure the robustness and correctness of transaction validation, preventing potential consensus issues or vulnerabilities.

**Technical Details:** The PR introduces a set of new `script_valid` and `script_invalid` test vectors, specifically crafted to target 'edge cases' within the Bitcoin Script interpreter. These vectors likely involve unusual combinations of opcodes, stack manipulations, or data sizes that might expose subtle bugs or undefined behaviors in the `CScript` evaluation logic. By expanding coverage for these critical scenarios, the tests aim to prevent consensus divergence or unexpected transaction validation outcomes.

#### [#36475: bench: add BIP-352 pubkey extraction benchmarks (standard + P2PKH worst-case)](https://github.com/bitcoin/bitcoin/pull/36475)
**Author:** [@theStack](https://github.com/theStack) | **[Performance & Optimization]** *(Activity: 6 review events)*
> This PR introduces new benchmarks to measure the performance of public key extraction for BIP-352 (Taproot) transactions, including a worst-case P2PKH scenario. This helps developers monitor and optimize the efficiency of key extraction, which is crucial for transaction processing.

**Technical Details:** The PR adds new benchmark tests to the `src/bench` suite, specifically targeting the `CPubKey::ExtractPubKey` operation for BIP-352 (Taproot) related scripts. It includes scenarios for standard Taproot key extraction and a worst-case P2PKH script, which can be more computationally intensive. These benchmarks provide metrics for assessing and improving the cryptographic and script evaluation performance.

#### [#36694: test: construct `mempool_tests` inputs/outputs declaratively](https://github.com/bitcoin/bitcoin/pull/36694)
**Author:** [@alexanderwiederin](https://github.com/alexanderwiederin) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR refactors the mempool test suite to use a more declarative style for constructing transaction inputs and outputs. This improves the readability and maintainability of mempool tests, making them easier to understand and extend.

**Technical Details:** The PR modifies the `mempool_tests` to replace imperative input/output construction logic with a more declarative approach. This involves using helper functions or data structures that describe the desired transaction components rather than step-by-step assembly. The change aims to reduce boilerplate code and enhance clarity within the complex mempool testing environment.

#### [#36592: build: Bump macOS SDK version to 15.0](https://github.com/bitcoin/bitcoin/pull/36592)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR updates the macOS SDK version used for building Bitcoin Core to 15.0, ensuring compatibility with the latest Apple development tools. This helps maintain the build system and allows developers to leverage current macOS features.

**Technical Details:** The change involves modifying the build system configuration, likely within the `depends` system, to specify `15.0` as the target SDK version for macOS. This ensures that the compilation process utilizes the headers and libraries from the latest specified SDK, aligning with Apple's Xcode releases. This update prevents potential build failures or deprecation warnings that can arise from using older SDKs, contributing to a more stable development environment.

#### [#36617: test: Fix intermittent issue in p2p_orphan_handling.py](https://github.com/bitcoin/bitcoin/pull/36617)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR resolves an intermittent issue in the `p2p_orphan_handling.py` test, making the test suite more reliable. This ensures consistent and accurate testing of how Bitcoin Core handles unconfirmed transactions.

**Technical Details:** This PR addresses an intermittent failure in `p2p_orphan_handling.py`, likely caused by race conditions or timing sensitivities within the test environment. The fix could involve adjusting delays, improving synchronization mechanisms, or refining assertion conditions to ensure consistent behavior across different test runs, thereby stabilizing the CI pipeline and improving test determinism.

#### [#36686: test: cover cumulative input value range in CheckTxInput tests.](https://github.com/bitcoin/bitcoin/pull/36686)
**Author:** [@KY-U](https://github.com/KY-U) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR enhances the transaction validation tests by expanding coverage for the cumulative input value range in `CheckTxInput`. This helps ensure that transactions with very large or unusual input sums are correctly handled and validated, preventing potential edge-case bugs.

**Technical Details:** The PR adds new test cases to the `CheckTxInput` suite, specifically targeting scenarios where the sum of transaction input values approaches the maximum representable value (e.g., `MAX_MONEY`) or other boundary conditions. This involves crafting transactions with many inputs or inputs with large individual values and verifying that the validation logic correctly identifies valid transactions and rejects invalid ones (e.g., those exceeding `MAX_MONEY` or having negative sums).

#### [#36619: rest: don't log an error for /spenttxouts on a block without undo data](https://github.com/bitcoin/bitcoin/pull/36619)
**Author:** [@kriss39](https://github.com/kriss39) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR refines the REST interface behavior by preventing unnecessary error logging when `/rest/spenttxouts` is queried for a block that lacks undo data. This reduces log spam for nodes running in pruned mode or with specific configurations, making logs cleaner and more useful.

**Technical Details:** The modification targets the `spenttxouts` REST endpoint handler. When a request is made for a block hash, the handler attempts to retrieve undo data. In cases where undo data is legitimately unavailable (e.g., for pruned blocks or blocks before undo data was stored), the PR changes the logging level from an error to a debug or info message, or suppresses it entirely, as this is an expected condition rather than an actual error.

#### [#36612: doc: Merge all BSD build docs back into build-unix.md](https://github.com/bitcoin/bitcoin/pull/36612)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR streamlines Bitcoin Core's build documentation by consolidating all BSD-specific instructions into the main `build-unix.md` file. This makes it easier for users to find comprehensive build instructions for Unix-like systems, including BSD.

**Technical Details:** This change involves merging the content of separate BSD-specific build documentation files (e.g., `build-freebsd.md`, `build-openbsd.md`) back into the general `build-unix.md`. The goal is to centralize build instructions for all Unix-like operating systems, reducing fragmentation and ensuring consistency in documentation maintenance and discoverability.

#### [#36752: net_processing: always disconnect for SENDTXRCNCL after VERACK](https://github.com/bitcoin/bitcoin/pull/36752)
**Author:** [@vasild](https://github.com/vasild) | **[Network & Privacy]** *(Activity: 5 review events)*
> This PR modifies the network processing logic to always disconnect peers that send `SENDTXRCNCL` messages after `VERACK`. This enforces correct protocol behavior and helps protect the node from unexpected or potentially malicious peer behavior.

**Technical Details:** The PR introduces a stricter policy in `net_processing` regarding the `SENDTXRCNCL` message. Previously, a node might tolerate this message after `VERACK` under certain conditions. Now, any peer sending `SENDTXRCNCL` after the `VERACK` handshake is complete will be immediately disconnected. This ensures peers adhere to the expected message flow for transaction reconciliation, preventing protocol misuse or unexpected state transitions.

#### [#36636: netaddress: make .onion suffix check case-insensitive](https://github.com/bitcoin/bitcoin/pull/36636)
**Author:** [@jpk68](https://github.com/jpk68) | **[Network & Privacy]** *(Activity: 5 review events)*
> This PR enhances network address handling by making the check for `.onion` suffixes case-insensitive. This improves compatibility and robustness when dealing with Tor addresses, as some systems might present them with mixed casing.

**Technical Details:** The `IsOnion` function or similar network address parsing logic is updated to convert the relevant part of the hostname to lowercase before performing the `.onion` suffix check. This ensures that addresses like `example.ONION` or `example.oNiOn` are correctly identified as Tor addresses. This change aligns the behavior with common internet practices and prevents parsing errors due to case variations.

#### [#36685: wallet: export replaces_txid and replaced_by_txid](https://github.com/bitcoin/bitcoin/pull/36685)
**Author:** [@vasild](https://github.com/vasild) | **[Wallet & User Tools]** *(Activity: 5 review events)*
> This PR makes the `replaces_txid` and `replaced_by_txid` fields available in wallet RPC outputs. This provides users and applications with more detailed information about transaction replacement (RBF) status directly from their wallet, improving transparency and usability.

**Technical Details:** The change involves modifying the wallet's internal data structures and RPC serialization logic to include `replaces_txid` and `replaced_by_txid` fields in relevant RPC responses, such as `gettransaction` or `listtransactions`. These fields, which track the original transaction being replaced and the new transaction replacing it, are populated when a transaction is part of a Replace-by-Fee (RBF) sequence, allowing external tools to easily identify and track RBF activity.

#### [#36741: policy: Document rounding behavior of feerate fee getters](https://github.com/bitcoin/bitcoin/pull/36741)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR adds documentation explaining the rounding behavior of feerate fee getter functions within Bitcoin Core's policy code. This improves clarity for developers and users understanding how transaction fees are calculated and rounded.

**Technical Details:** The change involves adding comments, docstrings, or updating existing developer documentation files to explicitly describe how feerate calculations handle fractional satoshis per virtual byte. This clarifies whether rounding is up, down, or to the nearest integer, and at what stage of the calculation it occurs. Such precision is crucial for accurate fee estimation and consistent policy enforcement.

#### [#36707: net_processing: remove redundant `peer` check in `MaybePunishNodeForBlock`](https://github.com/bitcoin/bitcoin/pull/36707)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR cleans up the network processing code by removing a redundant check for a `peer` object in the `MaybePunishNodeForBlock` function. This simplifies the code and improves readability without changing behavior.

**Technical Details:** The `MaybePunishNodeForBlock` function, responsible for potentially penalizing misbehaving peers, contained an unnecessary null-pointer or existence check for the `peer` object. Analysis revealed that the function's call sites or preceding logic already guarantee the `peer` object's validity. This PR removes the redundant check, streamlining the function's logic and reducing cognitive overhead for developers.

#### [#36584: kernel: make btck_LogEntry opaque](https://github.com/bitcoin/bitcoin/pull/36584)
**Author:** [@stickies-v](https://github.com/stickies-v) | **[Strategic Initiatives]** *(Activity: 4 review events)*
> This PR refactors the Bitcoin Core kernel by making the `btck_LogEntry` struct opaque. This is a significant step towards modularizing the kernel, improving its internal architecture and reducing coupling between components.

**Technical Details:** The `btck_LogEntry` struct, which is part of the Bitcoin Core Kernel Library (libbitcoinkernel), is changed from a publicly exposed structure to an opaque type. This typically involves moving its definition into the `.cpp` implementation file and exposing only a forward declaration in the header, along with accessor functions. This encapsulation prevents external code from directly accessing or modifying its internal members, enforcing a cleaner API and facilitating future internal changes without breaking external dependencies.

#### [#36254: bench: add and use undo-data for BlockToJsonVerbosity3 bench](https://github.com/bitcoin/bitcoin/pull/36254)
**Author:** [@0xB10C](https://github.com/0xB10C) | **[Performance & Optimization]** *(Activity: 4 review events)*
> This PR enhances a benchmark for converting blocks to JSON (verbosity level 3) by incorporating undo data. This provides a more realistic and comprehensive performance measurement for this operation, especially for scenarios where undo data is present and processed.

**Technical Details:** The change involves modifying the `BlockToJsonVerbosity3` benchmark to include the generation and processing of undo data when converting a block to its JSON representation. This means the benchmark now simulates the overhead associated with serializing or deserializing undo data alongside the block, providing a more accurate performance profile for operations that require this information.

#### [#36613: test: add getblockfilter test coverage for header-only blocks](https://github.com/bitcoin/bitcoin/pull/36613)
**Author:** [@aaron-leeb](https://github.com/aaron-leeb) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR expands test coverage for the `getblockfilter` RPC by adding specific test cases for header-only blocks. This ensures the correct behavior of block filter generation and retrieval, even for blocks that are not fully downloaded.

**Technical Details:** The changes introduce new unit or functional tests that simulate scenarios where `getblockfilter` is called on blocks for which only the header is available, but not the full block data. The tests verify that the RPC correctly handles these edge cases, either by returning an appropriate error or by generating a filter based on available information if possible. This ensures robustness and predictable behavior for clients querying block filters in various synchronization states.

#### [#36731: test: use monotonic clock for durations in test framework and http_interface](https://github.com/bitcoin/bitcoin/pull/36731)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR updates the test framework and HTTP interface to use a monotonic clock for measuring durations. This ensures more accurate and reliable time-based tests, as monotonic clocks are not affected by system time adjustments.

**Technical Details:** The PR modifies the Bitcoin Core test framework and the `http_interface` to switch from system-wide wall clocks to monotonic clocks when calculating durations. This change prevents issues where system time changes (e.g., NTP synchronization) could skew test results or introduce flakiness in time-sensitive assertions, ensuring more consistent and reliable test execution.

#### [#36609: ci: update some lint infra](https://github.com/bitcoin/bitcoin/pull/36609)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR updates some of the linting infrastructure used in Bitcoin Core's continuous integration (CI) system. This ensures that code quality checks are up-to-date and effective.

**Technical Details:** The changes involve modifying configuration files or scripts related to linting tools (e.g., `clang-format`, `pylint`, `flake8`, or custom linters). This could include updating tool versions, adjusting linting rules, or improving the efficiency of how lint checks are executed within the CI pipeline. The goal is to ensure that code submissions consistently adhere to current style and quality standards.

#### [#36770: test: Fix log and comment in mempool_reorg.py](https://github.com/bitcoin/bitcoin/pull/36770)
**Author:** [@Waridi318](https://github.com/Waridi318) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR corrects a log message and a comment within the `mempool_reorg.py` test, improving the clarity and accuracy of the test's output and internal documentation. This helps developers better understand test failures and the intended behavior of the mempool reorg logic.

**Technical Details:** The change involves minor textual modifications to a log message and a comment within the `mempool_reorg.py` functional test. Specifically, a log message that might have been misleading or incorrect is updated to reflect the actual test scenario or outcome, and a comment is revised for better clarity or to correct outdated information. These changes are purely cosmetic and do not alter the test's logic or behavior.

#### [#36725: refactor: Use u64 consistently for flatfile sizes](https://github.com/bitcoin/bitcoin/pull/36725)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR refactors the codebase to consistently use `u64` (unsigned 64-bit integer) for representing flatfile sizes. This ensures proper handling of very large files, preventing potential overflow issues as the blockchain grows.

**Technical Details:** The refactoring involves identifying all instances where flatfile sizes (e.g., `blk*.dat` files) are stored or manipulated and changing their data type to `uint64_t` or a similar `u64` alias. This change affects data structures and function signatures dealing with file I/O and size calculations. It ensures that file sizes exceeding 4GB (the limit of `u32`) are correctly represented and processed throughout the system, enhancing robustness.

#### [#36406: test: make p2p_orphan_handling's never-requested checks able to fail](https://github.com/bitcoin/bitcoin/pull/36406)
**Author:** [@fametrano](https://github.com/fametrano) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR enhances the reliability of the `p2p_orphan_handling` test by ensuring that certain critical checks can correctly detect failures. This improves the test's ability to catch regressions related to how Bitcoin Core handles unrequested transactions.

**Technical Details:** This PR modifies the `p2p_orphan_handling` test to ensure that assertions related to 'never-requested' checks are properly configured to fail if the condition is violated. Previously, these checks might have silently passed even when an issue was present. The change likely involves adjusting the assertion logic or test framework integration to correctly propagate failures, making the test more robust and effective.

#### [#36670: fuzz: check GetStale() returns exactly the stale private broadcast txs](https://github.com/bitcoin/bitcoin/pull/36670)
**Author:** [@frankomosh](https://github.com/frankomosh) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR enhances the fuzzing tests for Bitcoin Core's transaction relay logic. It specifically verifies that the `GetStale()` function accurately identifies and returns only the transactions that are considered stale for private broadcasting, improving the robustness of the network layer.

**Technical Details:** This PR adds a new assertion or test case to an existing fuzzer, specifically targeting the `GetStale()` method. The fuzzer will now verify that `GetStale()` precisely identifies and returns only those transactions that have been marked as stale for private broadcast. This ensures no unintended transactions are included or excluded, improving the reliability of transaction handling within the mempool and relay mechanisms.

#### [#36706: policy: remove unused GetVirtualTransactionInputSize](https://github.com/bitcoin/bitcoin/pull/36706)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR removes an unused function `GetVirtualTransactionInputSize` from the transaction policy code. This cleans up the codebase by removing dead code, making it easier to maintain and understand.

**Technical Details:** The `GetVirtualTransactionInputSize` function was identified as no longer being called anywhere within the codebase. This PR simply deletes the function definition and any associated declarations. This is a pure refactoring effort, reducing the overall lines of code and removing potential confusion for future developers without altering any runtime behavior.

#### [#36632: kernel: document the import_blocks abort](https://github.com/bitcoin/bitcoin/pull/36632)
**Author:** [@fametrano](https://github.com/fametrano) | **[Strategic Initiatives]** *(Activity: 3 review events)*
> This PR adds documentation explaining the abort mechanism within the `import_blocks` function in the kernel. This improves code clarity and helps developers understand how block import can be safely interrupted, which is crucial for robust node operation.

**Technical Details:** The PR introduces comments or updates existing documentation within the `import_blocks` function, detailing the conditions under which the block import process can be aborted and how this abort is handled. This might include explaining the use of an atomic boolean flag or a CancellationToken-like mechanism that allows an external caller to signal an early exit, ensuring resources are cleaned up correctly and the node remains in a consistent state.

#### [#36744: refactor: fix mismatched and undefined declarations](https://github.com/bitcoin/bitcoin/pull/36744)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR addresses and corrects mismatched and undefined declarations within the codebase. This refactoring improves code consistency, reduces potential for subtle bugs, and enhances overall code quality and maintainability.

**Technical Details:** The changes involve identifying and rectifying instances where function prototypes, variable declarations, or type definitions do not align across different compilation units or headers. This might include ensuring `const` correctness, consistent use of `static` or `inline`, or resolving ambiguities in overloaded functions. The refactoring ensures that the compiler sees consistent declarations, preventing undefined behavior and improving the reliability of the codebase without altering any functional logic.

#### [#36713: test: remove unused `DynSock::Pipe::GetNetMsg` and `PushNetMsg`](https://github.com/bitcoin/bitcoin/pull/36713)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR cleans up the test suite by removing unused network message handling functions. This reduces code bloat and improves the maintainability of the test infrastructure.

**Technical Details:** The PR identifies and removes `GetNetMsg` and `PushNetMsg` methods from the `DynSock::Pipe` class within the test framework. These functions were no longer being called by any tests, indicating dead code. Their removal simplifies the test codebase and reduces potential confusion for future developers.

#### [#36783: Update minisketch subtree to latest master](https://github.com/bitcoin/bitcoin/pull/36783)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR updates the embedded Minisketch library to its latest master version. This ensures Bitcoin Core benefits from the latest bug fixes and improvements in the Minisketch set reconciliation protocol, which is used for efficient UTXO set synchronization.

**Technical Details:** The PR updates the `src/minisketch` subtree to synchronize with the upstream Minisketch repository's latest master branch. This update incorporates recent changes to the Minisketch library, which provides a compact data structure for set reconciliation, primarily used in Bitcoin Core for efficient UTXO set synchronization during initial block download or peer synchronization.

#### [#36765: fuzz: push messages to one of m_nodes in connman target](https://github.com/bitcoin/bitcoin/pull/36765)
**Author:** [@darosior](https://github.com/darosior) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR enhances the network connection manager fuzzer by allowing it to push messages to individual nodes. This improves the fuzzer's ability to discover edge cases and potential vulnerabilities in the P2P networking stack.

**Technical Details:** The PR modifies the `connman` fuzzing target to enable the fuzzer to direct specific network messages to one of the `m_nodes` managed by the connection manager, rather than broadcasting or using a generic approach. This granular control allows for more targeted fuzzing of individual peer states and message handling logic, increasing the likelihood of uncovering subtle bugs or unexpected behavior in the P2P protocol implementation.

#### [#36750: test: construct multisig_tests inputs/outputs declaratively](https://github.com/bitcoin/bitcoin/pull/36750)
**Author:** [@yuvicc](https://github.com/yuvicc) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR refactors the multisig tests to make them more readable and maintainable. It simplifies how test inputs and outputs are defined, making it easier for developers to understand and extend these tests.

**Technical Details:** This PR modifies the `multisig_tests` to adopt a declarative style for constructing transaction inputs and outputs. Instead of imperative, step-by-step construction, it introduces helper functions or data structures that define the desired state. This improves test code clarity, reduces boilerplate, and makes future test additions or modifications less error-prone by centralizing transaction component definitions.

#### [#36777: refactor: rpc: doc: Mark longpoll counter u32](https://github.com/bitcoin/bitcoin/pull/36777)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR refactors RPC documentation to explicitly mark the longpoll counter as a `u32` (unsigned 32-bit integer). This clarifies the expected data type for RPC clients interacting with long-polling mechanisms.

**Technical Details:** The change involves updating the RPC interface documentation, likely within the `doc/rpc/` directory or directly in the C++ source code comments for RPC methods that use a longpoll counter. By explicitly specifying `u32`, it informs RPC client developers about the expected range and type of the counter. This helps prevent potential integration issues or misinterpretations of the API, improving client compatibility.

#### [#36601: test: avoid reusing AssumeUTXO coin insertion method in test fixtures](https://github.com/bitcoin/bitcoin/pull/36601)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR refines Bitcoin Core's test suite by preventing the accidental reuse of a specific coin insertion method meant for AssumeUTXO in general test fixtures. This ensures tests are more accurate and less prone to unintended side effects.

**Technical Details:** This PR modifies test fixtures to explicitly avoid using the `AssumeUTXO` coin insertion method when it is not relevant to the test's purpose. This prevents potential misconfigurations or unintended interactions that could arise from using a specialized method in a general context, ensuring test isolation and correctness by maintaining distinct test environments.

#### [#36754: test: Use `contains` in miniminer_tests](https://github.com/bitcoin/bitcoin/pull/36754)
**Author:** [@rustaceanrob](https://github.com/rustaceanrob) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR updates the `miniminer_tests` to use the `contains` method for assertions, improving the readability and conciseness of the test code. This is a minor refactoring that makes the tests easier to understand and maintain.

**Technical Details:** The change involves replacing existing assertion patterns, likely involving string searching or collection checks, with the more idiomatic `contains` method provided by the testing framework or language. This simplifies the expression of test conditions, reducing boilerplate and making the intent of the assertion clearer to future developers.

#### [#36748: test: Small test sync fixups](https://github.com/bitcoin/bitcoin/pull/36748)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR includes minor synchronization adjustments and fixes within the test suite. These changes improve the reliability and stability of tests, particularly those involving concurrent operations or timing-sensitive interactions.

**Technical Details:** The changes involve addressing race conditions or timing issues in existing tests. This could include adding explicit waits, using synchronization primitives (e.g., mutexes, condition variables), or adjusting sleep durations to ensure that asynchronous operations complete before assertions are made. The goal is to eliminate flaky tests that fail intermittently due to non-deterministic execution order.

#### [#36378: test: Add SKIP_WRITE edge case to wallet_startup](https://github.com/bitcoin/bitcoin/pull/36378)
**Author:** [@aaron-leeb](https://github.com/aaron-leeb) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR adds a new test case to ensure the wallet's startup logic correctly handles a specific `SKIP_WRITE` edge case. This improves the robustness and reliability of wallet initialization.

**Technical Details:** The PR introduces a new test scenario within the `wallet_startup` test suite. It specifically targets an edge case involving the `SKIP_WRITE` flag, verifying that the wallet's initialization process behaves as expected under these conditions. This helps prevent regressions and ensures correct state management during wallet loading.

#### [#36591: test: deduplicate PSBT unknown-field coverage in `rpc_psbt.py`](https://github.com/bitcoin/bitcoin/pull/36591)
**Author:** [@nebula-21](https://github.com/nebula-21) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR refactors the PSBT RPC tests to remove redundant coverage for unknown fields. This makes the test suite more concise and easier to maintain without sacrificing coverage.

**Technical Details:** The PR modifies `rpc_psbt.py` to consolidate and deduplicate test cases related to handling unknown fields within Partially Signed Bitcoin Transactions (PSBTs). By identifying and merging redundant test logic, the PR streamlines the test suite, making it more efficient and less prone to errors when new PSBT features are introduced.

#### [#36779: Update leveldb subtree to latest master](https://github.com/bitcoin/bitcoin/pull/36779)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR updates the embedded LevelDB library to its latest master version. This ensures Bitcoin Core benefits from the latest bug fixes, performance improvements, and security patches from the upstream LevelDB project.

**Technical Details:** The PR updates the `src/leveldb` subtree to synchronize with the upstream LevelDB repository's latest master branch. This involves pulling in recent commits, which may include internal optimizations, bug fixes, or minor API adjustments within the LevelDB key-value store used by Bitcoin Core for various data storage needs, such as the chainstate.

#### [#36771: ci: Add missing --error-on=any to apt update](https://github.com/bitcoin/bitcoin/pull/36771)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR improves the reliability of Bitcoin Core's continuous integration (CI) system by ensuring that `apt update` commands fail explicitly on any error. This prevents silent failures during dependency updates, making CI runs more robust and trustworthy.

**Technical Details:** The change modifies CI scripts, specifically those executing `apt update` commands, to include the `--error-on=any` flag. This flag instructs `apt` to return a non-zero exit code if any error, including warnings or minor issues, occurs during the update process. This ensures that CI jobs immediately report problems with package repositories or updates, preventing subsequent build steps from proceeding with an incomplete or corrupted environment.

#### [#36769: doc: Permit snippets at /doc/release-notes-uniq-name.md](https://github.com/bitcoin/bitcoin/pull/36769)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR updates the documentation system to allow the inclusion of code or text snippets in release notes, improving the clarity and conciseness of future release announcements. This makes it easier to provide detailed yet digestible information to users and developers.

**Technical Details:** The change involves modifying the documentation build scripts or configuration, likely in `doc/README.md` or a similar build tool, to enable the `include` directive or a similar mechanism within `release-notes-uniq-name.md` files. This allows authors to embed content from other files directly into the release notes, facilitating the reuse of common explanations or code examples and ensuring consistency across documentation.

#### [#36580: refactor: Use util::log::FormatString in BaseIndex::FatalErrorf and LogConnectFailure](https://github.com/bitcoin/bitcoin/pull/36580)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR improves the internal logging mechanisms within Bitcoin Core by standardizing the use of a common formatting utility. This makes error messages more consistent and easier to maintain for developers.

**Technical Details:** This refactoring PR replaces direct string formatting in `BaseIndex::FatalErrorf` and `LogConnectFailure` with `util::log::FormatString`. This centralizes string formatting logic, potentially leveraging compile-time format string checks and reducing duplication across the codebase. It aims to improve code quality, maintainability, and consistency within the logging infrastructure.

#### [#1986: examples: exit with failure if signature verification fails](https://github.com/bitcoin-core/secp256k1/pull/1986)
**Author:** [@amartya1523](https://github.com/amartya1523) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR improves the `secp256k1` library's example programs by ensuring they correctly indicate failure when signature verification fails. This makes the examples more robust and easier for developers to use and understand.

**Technical Details:** The modification updates the example programs within the `secp256k1` repository. Previously, some examples might have continued execution or exited with a success code even if a signature verification operation returned false. This change explicitly checks the return value of verification functions and, upon failure, causes the example program to exit with a non-zero status code, signaling an error to the calling environment or script.

#### [#36715: refactor: Enable bugprone-signed-char-misuse](https://github.com/bitcoin/bitcoin/pull/36715)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR enables a new static analysis check, `bugprone-signed-char-misuse`, to identify and prevent potential issues related to `signed char` usage in the codebase. This improves code quality and reduces the likelihood of subtle bugs.

**Technical Details:** The change integrates the `bugprone-signed-char-misuse` check into the project's static analysis toolchain, likely Clang-Tidy. This involves updating build configurations or CI scripts to run this specific check. The rule flags implicit conversions or operations on `signed char` that could lead to unexpected behavior due to sign extension issues, promoting safer type handling across the codebase.

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#36740: test: SRD tie-break test](https://github.com/bitcoin/bitcoin/pull/36740)
**Author:** [@Zeegaths](https://github.com/Zeegaths) | **[Maintenance & Tech Debt]** *(Activity: 16 review events this week)*
> This PR adds a new test case for the SRD (Self-Referential Dependency) tie-breaking logic in the mempool. This ensures the correct behavior of transaction ordering under specific dependency scenarios, improving the robustness of the mempool.

#### [#35026: mempool: recalculate stale BIP68 lockpoints in removeForReorg](https://github.com/bitcoin/bitcoin/pull/35026)
**Author:** [@javierpmateos](https://github.com/javierpmateos) | **[Network & Privacy]** *(Activity: 15 review events this week)*
> This PR improves mempool reliability by correctly recalculating BIP68 lockpoints for transactions that rely on their mempool parents during a chain reorganization. This ensures that validly locked transactions are not dropped from the mempool prematurely during reorgs, maintaining consistent transaction relay policy.

#### [#36721: script: store interpreter stack elements as reference-counted objects](https://github.com/bitcoin/bitcoin/pull/36721)
**Author:** [@conduition](https://github.com/conduition) | **[Performance & Optimization]** *(Activity: 12 review events this week)*
> This PR refactors the Bitcoin script interpreter to store stack elements as reference-counted objects. This change aims to improve memory management and potentially performance during script execution by reducing data copying and enabling more efficient handling of script data.

#### [#36759: torcontrol: Improve connection logging](https://github.com/bitcoin/bitcoin/pull/36759)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Network & Privacy]** *(Activity: 11 review events this week)*
> This PR enhances the logging for Tor control connections, making it easier to diagnose and understand connection issues. This improves the reliability and debuggability of Bitcoin Core's Tor integration.

#### [#36747: Update libmultiprocess subtree to add nonunix platform support and fix race conditions](https://github.com/bitcoin/bitcoin/pull/36747)
**Author:** [@ryanofsky](https://github.com/ryanofsky) | **[Maintenance & Tech Debt]** *(Activity: 11 review events this week)*
> This PR updates the internal `libmultiprocess` subtree, adding support for non-Unix platforms and fixing existing race conditions. This enhances the robustness and portability of Bitcoin Core components that rely on this library.

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

### [Direct Messages (DMs)](https://delvingbitcoin.org/t/direct-messages-dms/3027/1)
**Source:** Delving | **Started By:** {'username': 'ORANGEMART', 'uuid': 'auto_orangemart'} | **Messages:** 2
> We're working to empower artists by enabling direct Bitcoin payments from listeners. Our goal is to connect an artist with their fans on btcplaylist.com so listeners can easily 'zap' them for their music.

**Technical Details:** The immediate technical task is to acquire the Nostr public key (`npub`) for artist @neonrooks to integrate Lightning zapping functionality on btcplaylist.com. This will allow listeners to send direct Bitcoin payments. The current challenge is a communication hurdle, as the developer is unable to find a direct messaging mechanism on the platform to request the `npub`, highlighting a potential need for improved key exchange protocols or platform-specific contact methods for Nostr identity integration.

### [Forwardable Peerswap Incentives, And Closing Surreptitious Communications Tunnels](https://delvingbitcoin.org/t/forwardable-peerswap-incentives-and-closing-surreptitious-communications-tunnels/2917/4)
**Source:** Delving | **Started By:** {'username': 'ZmnSCPxj jxPCSnmZ', 'uuid': 'auto_zmnscpxj_jxpcsnmz'} | **Messages:** 2
> Developers are refining a new Lightning Network protocol, Forwardable Peerswaps, to improve liquidity management. The current focus is on ensuring all protocol commitments are cryptographically secure and enforceable on-chain.

**Technical Details:** The discussion centers on the precise definition of 'commit' within the Forwardable Peerswaps protocol's hash-exchange argument. It's argued that 'commit' must strictly imply an enforceable on-chain commitment, rather than just off-chain signed messages or an agreement to continue. This distinction is critical for the protocol's security and trustlessness, ensuring that all commitments are cryptographically binding. The protocol specification requires explicit clarification to define this commitment mechanism clearly and prevent any ambiguity.

### [TCP hole punching for Bitcoin nodes behind home NATs?](https://delvingbitcoin.org/t/tcp-hole-punching-for-bitcoin-nodes-behind-home-nats/2497/34)
**Source:** Delving | **Started By:** {'username': '0xB10C', 'uuid': 'can_0xb10c'} | **Messages:** 2
> We're exploring ways to help more home users run reachable Bitcoin nodes, boosting network decentralization and resilience. This involves carefully balancing ease of connectivity with robust security against potential network attacks.

**Technical Details:** The discussion centers on increasing reachable nodes in residential ISPs, particularly through techniques like holepunching. Key questions include the specific problems solved by such features, how to implement them to raise attacker costs, and the security implications for home users given recent TCP stack and protocol vulnerabilities (e.g., CVE-2026-117350, CVS-2026-117349). The architectural debate weighs the benefits of enhanced decentralization against the risks of exposing home nodes to potential exploits, questioning if increased reachability is 'sensible' under current conditions.

## 🏆 Contributor Shoutouts
### 🎉 First-Time Merges
Welcome to the codebase: [@Conradgabe](https://github.com/Conradgabe), [@OSINTv96](https://github.com/OSINTv96), [@Waridi318](https://github.com/Waridi318), [@aaron-leeb](https://github.com/aaron-leeb)

### ✍️ Top Authors
The most active PR authors this week: [@maflcko](https://github.com/maflcko), [@fanquake](https://github.com/fanquake), [@fametrano](https://github.com/fametrano), [@rustaceanrob](https://github.com/rustaceanrob), [@hebasto](https://github.com/hebasto)

### 🕵️ Top Reviewers
Providing critical review and testing: [@sedited](https://github.com/sedited), [@maflcko](https://github.com/maflcko), [@fanquake](https://github.com/fanquake), [@fametrano](https://github.com/fametrano), [@achow101](https://github.com/achow101)
