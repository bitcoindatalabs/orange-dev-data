# 📰 This Week in Bitcoin (2026-11-09 to 2026-11-15)

## 📌 The TL;DR
- Significant discussions are underway regarding the long-term cryptographic security of Bitcoin, specifically exploring a new Post-Quantum Address Format (bc1z) using ML-DSA-65 to future-proof against quantum computing threats.
- The community is actively debating the practical adoption and user experience implications of recent protocol upgrades, particularly whether wallets should default to Taproot (bc1p) or SegWit (bc1q) receive addresses given varying service support.

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

#### [#36105: bitcoin wrapper: Fix Windows exec so wrapper waits for child process](https://github.com/bitcoin/bitcoin/pull/36105)
**Author:** [@ryanofsky](https://github.com/ryanofsky) | **[Wallet & User Tools]** *(Activity: 17 review events)*
> This PR fixes an issue on Windows where the `bitcoin` wrapper script would not correctly wait for the main Bitcoin Core process to finish. This ensures proper process management and prevents orphaned processes or unexpected behavior when launching the node.

**Technical Details:** The fix addresses a specific behavior of `exec` or process launching on Windows within the `bitcoin` wrapper. It modifies the wrapper's logic to correctly handle child process termination, likely by using appropriate Windows API calls (e.g., `WaitForSingleObject`) to ensure the parent wrapper process waits for the Bitcoin Core child process to exit before terminating itself. This prevents resource leaks and ensures consistent application lifecycle management.

#### [#36068: fuzz: reuse one fuzzed wallet across inputs](https://github.com/bitcoin/bitcoin/pull/36068)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 15 review events)*
> This PR optimizes the fuzzer for wallet-related code by reusing a single fuzzed wallet instance across multiple test inputs. This significantly improves the efficiency and speed of wallet fuzz testing.

**Technical Details:** The wallet fuzzer harness is modified to initialize a single `CWallet` object at the start of the fuzzing process. This instance is then reused for subsequent fuzzed inputs, avoiding the overhead of repeated wallet creation and destruction. This optimization allows for a greater number of fuzzing iterations within the same timeframe, enhancing test coverage.

#### [#36642: rpc: parse each batch element into its own request](https://github.com/bitcoin/bitcoin/pull/36642)
**Author:** [@fametrano](https://github.com/fametrano) | **[Maintenance & Tech Debt]** *(Activity: 12 review events)*
> This PR refactors the RPC batch processing mechanism to parse each element as an independent request. This improves the robustness and consistency of batch RPC calls, especially in handling individual request failures.

**Technical Details:** The modification alters the RPC server's batch request handler. Instead of processing the entire batch as a single unit, each JSON object within the batch array is now individually parsed into its own `JSONRPCRequest` object. This allows for more granular error reporting and processing, ensuring that errors in one batch element do not necessarily prevent the processing of others, and aligns the internal representation of batch elements with single RPC calls.

#### [#36757: net: ignore privacy network peer's view of our address](https://github.com/bitcoin/bitcoin/pull/36757)
**Author:** [@stratospher](https://github.com/stratospher) | **[Network & Privacy]** *(Activity: 10 review events)*
> This PR enhances privacy by preventing Bitcoin Core from considering address advertisements from peers on privacy networks (like Tor/I2P) as reliable indicators of our own external IP address. This reduces the risk of leaking our real IP address when operating over privacy-preserving transports.

**Technical Details:** The change modifies the address management logic within the networking subsystem. Specifically, when a peer connected via a privacy network (e.g., a Tor or I2P connection) advertises an address that it believes is "our" external address, this PR ensures that such advertisements are ignored for the purpose of updating our own perceived external IP. This prevents privacy-preserving connections from inadvertently revealing or confirming our clearnet IP address to other nodes.

#### [#36224: test: Add test coverage for `PartiallySignedTransaction::Merge()`](https://github.com/bitcoin/bitcoin/pull/36224)
**Author:** [@nebula-21](https://github.com/nebula-21) | **[Maintenance & Tech Debt]** *(Activity: 9 review events)*
> This PR adds new test coverage for the `PartiallySignedTransaction::Merge()` function, which is crucial for combining PSBTs. This ensures the merging logic works correctly and reliably, improving the robustness of PSBT handling.

**Technical Details:** The PR introduces a new set of unit tests specifically targeting the `Merge()` method of the `PartiallySignedTransaction` class. These tests cover various scenarios, including merging PSBTs with different inputs, outputs, and witness data, to verify that the combined PSBT is valid and correctly represents the merged transaction. This enhances the confidence in the correctness of PSBT operations.

#### [#36488: rpc: wallet: Schedule mixed-case confTarget option deprecation](https://github.com/bitcoin/bitcoin/pull/36488)
**Author:** [@maflcko](https://github.com/maflcko) | **[Wallet & User Tools]** *(Activity: 7 review events)*
> This PR schedules the deprecation of mixed-case `confTarget` options within wallet RPCs. This change aims to standardize RPC parameter naming, improving consistency and ease of use for developers and users.

**Technical Details:** The PR introduces a deprecation warning for RPC calls that use mixed-case variations of the `confTarget` parameter (e.g., `confTarget` vs `conftarget`). The underlying RPC logic will still accept these mixed-case inputs for a transitional period but will log a warning, guiding users to adopt the standardized, typically lowercase, naming convention. This is a step towards enforcing stricter API consistency and simplifying future RPC development and documentation for wallet interactions.

#### [#36791: test: fix waitTipChanged timeout on slow hosts and use monotonic clock in interface_ipc_mining](https://github.com/bitcoin/bitcoin/pull/36791)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR fixes a flaky test that could time out on slower systems and improves the reliability of mining-related interface tests. It ensures tests pass consistently across different hardware environments by using a monotonic clock for timing.

**Technical Details:** The PR addresses test flakiness by adjusting the `waitTipChanged` timeout to be more forgiving on resource-constrained CI runners or development machines. Additionally, it modifies the `interface_ipc_mining` test to use `std::chrono::steady_clock` (a monotonic clock) for measuring durations. This prevents issues where system clock adjustments could interfere with test timing, leading to false failures.

#### [#36815: doc: Fix Doxygen attribution of file-level comments](https://github.com/bitcoin/bitcoin/pull/36815)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR corrects how Doxygen attributes file-level comments in the documentation. This ensures that the generated documentation accurately reflects the intended authorship and context for each file.

**Technical Details:** The Doxygen comments within the codebase are adjusted to conform to the tool's specific syntax for file-level attribution. This involves verifying and correcting Doxygen commands such as `@file` and `@author` at the top of source files. The fix ensures that the generated API documentation correctly associates file-level descriptions and metadata with their respective files.

#### [#36805: Enclose all header content in include guards](https://github.com/bitcoin/bitcoin/pull/36805)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR ensures that all header files in the Bitcoin Core codebase are properly enclosed in include guards. This prevents multiple inclusions of the same header, which can lead to compilation errors and increased build times.

**Technical Details:** A systematic review of all header files (`.h` or `.hpp`) was conducted to verify the presence and correct implementation of include guards (e.g., `#ifndef`, `#define`, `#endif`). Missing guards were added to ensure that each header's content is processed only once per compilation unit. This practice is crucial for build robustness, preventing redefinition errors and optimizing compilation efficiency.

#### [#36074: scripted-diff: [fuzz] Add util/check.h includes for assertions](https://github.com/bitcoin/bitcoin/pull/36074)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR, applied via a scripted diff, updates fuzzing targets to include `util/check.h` for assertions. This ensures consistent and robust error checking within the fuzzing framework, improving the reliability of tests.

**Technical Details:** The change is a mass update, likely applied programmatically, to various fuzzing test files. It involves adding `#include <util/check.h>` to these files, which provides access to assertion macros like `CHECK_NONFATAL` or `CHECK_FATAL`. This standardizes the assertion mechanism used within the fuzzing harnesses, ensuring that critical conditions are properly validated and reported during fuzzing runs, aiding in the discovery of bugs.

#### [#36810: test: construct `miner_tests` transactions declaratively](https://github.com/bitcoin/bitcoin/pull/36810)
**Author:** [@yuvicc](https://github.com/yuvicc) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR refactors the `miner_tests` suite to construct transactions using a more declarative style. This improves the readability and maintainability of the test code.

**Technical Details:** The transaction construction logic within `miner_tests` is updated from an imperative, step-by-step approach to a more declarative one. This likely involves introducing helper functions or a builder pattern that allows test cases to define transaction properties concisely. The change reduces boilerplate, makes the intent of test transactions clearer, and simplifies future modifications to the test suite.

#### [#36807: refactor: Move `NodeId` declaration into `net_types.h` and fix includes in related modules](https://github.com/bitcoin/bitcoin/pull/36807)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR refactors the declaration of `NodeId` to a more appropriate location, improving code organization and maintainability. It helps streamline dependencies within the networking codebase.

**Technical Details:** The `NodeId` type, previously declared in a less specific header, is moved to `net_types.h`. This change centralizes network-related type definitions, reducing circular dependencies and improving module encapsulation. It also involves updating include paths in all files that reference `NodeId` to reflect its new location, ensuring consistent and correct compilation.

#### [#36574: ci: Reword stale readme](https://github.com/bitcoin/bitcoin/pull/36574)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR updates and rewords a stale README file related to continuous integration, improving the accuracy and clarity of documentation for developers. This helps maintain up-to-date project information.

**Technical Details:** The change involves editing the content of a specific README file within the CI directory. It updates outdated instructions, clarifies existing procedures, and ensures the documentation accurately reflects the current state of the CI system. This is a pure documentation update to improve developer experience.

#### [#36408: test: allow 3 bytes of fee overestimate in assert_fee_amount](https://github.com/bitcoin/bitcoin/pull/36408)
**Author:** [@fametrano](https://github.com/fametrano) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR adjusts a test assertion to allow for a small, 3-byte overestimate in transaction fee calculations. This makes the test more robust against minor, acceptable variations in fee estimation without compromising accuracy.

**Technical Details:** The `assert_fee_amount` utility function, used in various tests, is modified to include a small tolerance for fee overestimation. This accounts for potential off-by-one or minor rounding differences that can occur in fee calculation logic, especially when dealing with different transaction sizes or script types. The change prevents brittle tests from failing due to negligible, non-critical fee discrepancies.

#### [#36556: depends: fix non-atomic reads in capnp debug assertions](https://github.com/bitcoin/bitcoin/pull/36556)
**Author:** [@xyzconstant](https://github.com/xyzconstant) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR addresses a potential issue in the `depends` system's `capnp` library where debug assertions could involve non-atomic reads. Fixing this ensures correctness and prevents undefined behavior in specific debug scenarios.

**Technical Details:** The `capnp` dependency, used within the `depends` build system, contained debug assertions that might perform non-atomic reads on shared memory, potentially leading to race conditions or incorrect state in multi-threaded debug environments. This change modifies the relevant code paths to ensure that these reads are performed atomically, guaranteeing data consistency and preventing subtle bugs during development and debugging.

#### [#36785: rpc: wallet: Add snake_case aliases for listunspent options](https://github.com/bitcoin/bitcoin/pull/36785)
**Author:** [@maflcko](https://github.com/maflcko) | **[Wallet & User Tools]** *(Activity: 4 review events)*
> This PR enhances the `listunspent` RPC command by introducing `snake_case` aliases for its options, providing more flexible and idiomatic parameter naming for users. This improves the usability and consistency of the RPC interface.

**Technical Details:** The change involves modifying the RPC argument parsing logic for the `listunspent` command. It adds alternative `snake_case` names (e.g., `min_depth` instead of `minDepth`) to the existing `camelCase` options. The RPC server's parameter validation and mapping layer is updated to recognize both naming conventions, allowing users to interchangeably use either format when calling the RPC without altering the underlying C++ function signatures or data structures.

#### [#36824: ci: Switch to self-hosted CDash](https://github.com/bitcoin/bitcoin/pull/36824)
**Author:** [@willcl-ark](https://github.com/willcl-ark) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR updates the Continuous Integration (CI) system to use a self-hosted instance of CDash for reporting test results. This provides more control and potentially better integration with Bitcoin Core's development infrastructure.

**Technical Details:** The CI configuration scripts are modified to direct test result uploads to a newly established self-hosted CDash server. This involves updating target URLs and potentially API keys or authentication mechanisms. The transition ensures that build and test data remain within the project's control, offering enhanced privacy and customization options for reporting.

#### [#36798: test: spend an existing output in `TestBasicMining` double spend case](https://github.com/bitcoin/bitcoin/pull/36798)
**Author:** [@yuvicc](https://github.com/yuvicc) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR improves the `TestBasicMining` suite by making the double-spend test case more realistic. It now spends an existing output, which better simulates real-world double-spend attempts.

**Technical Details:** The `TestBasicMining` double-spend scenario is enhanced to create a more authentic test environment. Instead of using a synthetic or non-existent output, the test now first mines a block to create a spendable UTXO. Subsequently, two conflicting transactions are constructed, both attempting to spend this specific, existing output, thereby more accurately simulating a real-world double-spend attempt on the network.

#### [#36817: ipc: remove pre-v14 libmultiprocess compat definitions](https://github.com/bitcoin/bitcoin/pull/36817)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR removes outdated compatibility definitions related to `libmultiprocess` for versions older than v14. This cleans up the codebase by removing legacy code that is no longer needed.

**Technical Details:** The `ipc` (Inter-Process Communication) component previously included code paths and definitions to maintain compatibility with `libmultiprocess` versions prior to v14. As the minimum supported dependency versions have advanced, these compatibility layers are now obsolete. This PR identifies and removes these unused code segments, reducing the overall codebase size and simplifying future maintenance.

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#35026: mempool: recalculate stale BIP68 lockpoints in removeForReorg](https://github.com/bitcoin/bitcoin/pull/35026)
**Author:** [@javierpmateos](https://github.com/javierpmateos) | **[Network & Privacy]** *(Activity: 11 review events this week)*
> This PR improves mempool reliability by correctly recalculating BIP68 lockpoints for transactions that rely on their mempool parents during a chain reorganization. This ensures that validly locked transactions are not dropped from the mempool prematurely during reorgs, maintaining consistent transaction relay policy.

#### [#36187: http: Restore requirement of IPv4 bind success](https://github.com/bitcoin/bitcoin/pull/36187)
**Author:** [@hodlinator](https://github.com/hodlinator) | **[Network & Privacy]** *(Activity: 11 review events this week)*
> This PR restores the requirement for Bitcoin Core's HTTP server to successfully bind to an IPv4 address. This ensures the server operates as expected and prevents it from starting in a degraded state if IPv4 binding fails.

#### [#36147: ci: add [free|open|net]BSD ci test jobs](https://github.com/bitcoin/bitcoin/pull/36147)
**Author:** [@willcl-ark](https://github.com/willcl-ark) | **[Maintenance & Tech Debt]** *(Activity: 11 review events this week)*
> This PR expands Bitcoin Core's continuous integration (CI) system to include test jobs for FreeBSD, OpenBSD, and NetBSD. This improves the project's cross-platform compatibility and ensures the software functions correctly on these operating systems.

#### [#36451: refactor: Use NotNull for CreateNewBlock and pimpls](https://github.com/bitcoin/bitcoin/pull/36451)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 10 review events this week)*
> This PR refactors internal code to use `NotNull` types, improving code safety and readability. It helps prevent null pointer dereferences at compile time, making the block creation logic more robust.

#### [#36049: streams: handle buffered write failures outside the destructor](https://github.com/bitcoin/bitcoin/pull/36049)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Maintenance & Tech Debt]** *(Activity: 9 review events this week)*
> This PR improves the robustness of Bitcoin Core's stream handling by ensuring buffered write failures are managed explicitly, rather than silently ignored in destructors. This prevents potential data loss or unexpected behavior by allowing errors to be properly reported and handled.

## 🗓️ Dev Meeting
Summary of the core dev IRC meeting on 2026-11-12 with 27 participants.

- Fuzzing WG Update: No update reported by eugenesiegel.
- addr-relay WG Update: stratospher reported no update, ongoing work on addr-relay protections, write-ups expected soon.
- Kernel WG Update: sedited noted purpleKarrot posted RFC issue #36842 on encapsulation of vocabulary types, encouraging comments.
- Benchmarking WG Update: l0rinc was absent. andrewtoth reported sedited's branch achieved chainstate reindex in ~20 minutes, others under an hour. This leverages sipa's negative UTXO set suggestion, enabling parallel block connecting and binding validation performance to CPU cores without assumevalid.
- QA WG Update: brunoerg ran mutation testing on src/validation.cpp, identifying over 300 surviving mutants on mutanthub.space, indicating test gaps.
- QML GUI WG Update: johnny9dev reported jarolrod's QA with "clankers" found 300 findings against gui-qml, delaying the PR to bitcoin/bitcoin but confirming feature completeness. Project Loupe engagement is planned.
- re-activate Erlay WG and Signal chat (or alternative): sr_gi requested re-activation of the Erlay WG and its Signal group for discussions.
- Erlay WG Update: sr_gi rebased the Erlay PR on master and is addressing coredev points. A proposal was made to use BIP-434 for the Erlay handshake, replacing custom negotiation, aligning with BIP-330 draft status.

**Action Items:**
- Developers are encouraged to comment on Kernel WG RFC issue #36842.
- brunoerg requests PR descriptions include links to mutants from mutanthub.space and/or git diffs of mutants for QA.
- sr_gi will re-activate the Erlay WG on GitHub and its Signal group; interested parties should contact sr_gi to join the chat.
- sr_gi will create a todo list and provide regular reports on Erlay updates.

## 🗣️ Research & Governance
Top active threads across mailing lists and research forums.

### [Should wallets default to Taproot or SegWit receive addresses while some services still reject bc1p?](https://delvingbitcoin.org/t/should-wallets-default-to-taproot-or-segwit-receive-addresses-while-some-services-still-reject-bc1p/3056/2)
**Source:** Delving | **Started By:** {'username': 'Anzus', 'uuid': 'auto_anzus'} | **Messages:** 8
> We're exploring ways to make receiving Bitcoin simpler and more reliable for users, aiming to prevent common errors when withdrawing funds from exchanges or other sources.

**Technical Details:** The discussion highlights a recurring user experience issue where users encounter difficulties when copying Bitcoin receive addresses for withdrawals, likely due to address format confusion or network compatibility challenges. This points to a need for improved address validation, clearer user interface guidance, or potentially standardized mechanisms for address verification across different platforms. Solutions could involve enhanced client-side checks within wallets or better communication protocols between wallets and exchanges to mitigate user errors before transactions are initiated.

### [Decentralized Coinbase Payout Protocols (DCPP): A Framework for Discussion](https://delvingbitcoin.org/t/decentralized-coinbase-payout-protocols-dcpp-a-framework-for-discussion/3060/1)
**Source:** Delving | **Started By:** {'username': '7d5x9', 'uuid': 'auto_7d5x9'} | **Messages:** 8
> Developers are discussing critical limits within mining protocols to ensure the security and reliability of new open-source mining technologies. The goal is to make mining operations more robust and efficient for everyone.

**Technical Details:** The discussion centers on understanding the rationale behind an apparent 'limit of 16' within mining protocols, and its implications for sharechains and payout sets. A key architectural debate has emerged regarding the safety of allowing the 'slot count' to depend on 'claimed firmware support.' The concern is that such a dependency could introduce vulnerabilities or instability, necessitating a re-evaluation of how these critical parameters are determined and validated within the open mining stack.

### [Towards A K-of-N Lightning Network Node](https://delvingbitcoin.org/t/towards-a-k-of-n-lightning-network-node/2395/13)
**Source:** Delving | **Started By:** {'username': 'ZmnSCPxj jxPCSnmZ', 'uuid': 'auto_zmnscpxj_jxpcsnmz'} | **Messages:** 6
> We're exploring new ways to secure Lightning Network funds using shared control, making it safer and more resilient for users. This allows multiple parties to collectively manage a Lightning node, enhancing security against loss or compromise.

**Technical Details:** The thread explores building a k-of-n multisig self-custodial Lightning node, leveraging Nested MuSig2 for enhanced fund security. A key technical debate now focuses on the storage costs of Lightning channel state updates, specifically how Core Lightning and lnd handle these differently. This impacts the operational overhead and scalability of a multisig node, requiring optimization of state management to minimize storage requirements for a robust k-of-n setup.

### [[BIP Draft] Co-signer Spending Policies](https://delvingbitcoin.org/t/bip-draft-co-signer-spending-policies/2955/8)
**Source:** Delving | **Started By:** {'username': 'nonAnon', 'uuid': 'auto_nonanon'} | **Messages:** 5
> Efforts are underway to make multi-signature transactions smarter and more reliable by standardizing how co-signers enforce rules. This will enable more advanced Bitcoin transactions that automatically follow predefined conditions, enhancing security and predictability.

**Technical Details:** The discussion focuses on standardizing co-signer policies to enable covenant-like behavior, where co-signers sign only when a specific predicate holds. A critical feedback point highlights that the current `statement-v0` draft signs event ID, outcome, and timestamp, but fails to specify if the outcome is final or mutable. This omission could lead to co-signers acting on a preliminary or subsequently invalidated outcome. The policy standardization must therefore explicitly address outcome finality to ensure co-signers operate on definitive data, preventing potential transaction invalidations.

### [[bitcoindev] BIP Draft Post-Quantum Address Format (bc1z) using ML-DSA-65](https://gnusha.org/pi/bitcoindev/9463348c-b2ec-4c6f-b9ec-2e9e2fc7d105n@googlegroups.com)
**Source:** Mailing List | **Started By:** {'username': 'Hans Stringuer', 'uuid': 'auto_hans_stringuer'} | **Messages:** 4

## 🏆 Contributor Shoutouts
### ✍️ Top Authors
The most active PR authors this week: [@maflcko](https://github.com/maflcko), [@hebasto](https://github.com/hebasto), [@fametrano](https://github.com/fametrano), [@yuvicc](https://github.com/yuvicc), [@fanquake](https://github.com/fanquake)

### 🕵️ Top Reviewers
Providing critical review and testing: [@maflcko](https://github.com/maflcko), [@fanquake](https://github.com/fanquake), [@hebasto](https://github.com/hebasto), [@l0rinc](https://github.com/l0rinc), [@sedited](https://github.com/sedited)
