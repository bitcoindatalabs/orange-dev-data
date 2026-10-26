# 📰 This Week in Bitcoin (2026-10-19 to 2026-10-25)

## 📌 The TL;DR
- P2P Network Hardening:** Recent merges significantly bolster the P2P layer's resilience and security, including uniform address sampling within addrman buckets to improve decentralization, stricter enforcement against invalid compact blocks, and capping maximum connections to enhance node stability.
- Addressing NAT Traversal for Decentralization:** Active discussions around TCP hole punching indicate a critical focus on enabling better connectivity for nodes behind home NATs, which could represent a major technical shift towards improving network decentralization and inbound connection availability.

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

#### [#36449: addrman: use uniform sampling inside buckets](https://github.com/bitcoin/bitcoin/pull/36449)
**Author:** [@sipa](https://github.com/sipa) | **[Network & Privacy]** *(Activity: 29 review events)*
> This PR improves the address manager's peer selection logic by ensuring more uniform sampling within its buckets. This helps Bitcoin Core discover and connect to a more diverse set of peers, enhancing network decentralization and resilience.

**Technical Details:** The `addrman` stores known peer addresses in buckets to mitigate eclipse attacks. Previously, when selecting an address from a bucket, the sampling method could introduce biases by iterating from a random starting point. This PR modifies the selection process to use truly uniform random sampling within a bucket by directly picking a random index. This change prevents potential biases in peer selection, improving the distribution of connections and making the node more resistant to targeted attacks.

#### [#35461: util: Clarify the assertion message in assertion failures (Assert, Assume, etc.)](https://github.com/bitcoin/bitcoin/pull/35461)
**Author:** [@optout21](https://github.com/optout21) | **[Maintenance & Tech Debt]** *(Activity: 22 review events)*
> This PR enhances the utility functions responsible for assertions (like Assert and Assume) by clarifying the messages displayed during assertion failures. This makes debugging easier and faster for developers by providing more informative error outputs.

**Technical Details:** The change involves modifying the implementation of assertion macros or functions to include more context in the failure message. This might include adding the file name, line number, the exact expression that failed, and potentially the values of relevant variables. By providing richer diagnostic information directly in the assertion message, developers can more quickly pinpoint the root cause of unexpected program states, significantly streamlining the debugging process during development and testing.

#### [#35321: p2p: Misbehave on invalid compact block in optimistic reconstruction](https://github.com/bitcoin/bitcoin/pull/35321)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Security & Consensus]** *(Activity: 18 review events)*
> This PR enhances network security by introducing a 'misbehavior' penalty for peers that send invalid compact blocks during optimistic reconstruction. This protection helps nodes identify and disconnect from malicious or buggy peers, preventing the propagation of invalid block data and potential resource exhaustion.

**Technical Details:** During optimistic compact block reconstruction (BIP 152), if a peer provides a compact block that, after being fully reconstructed locally, fails fundamental block validation rules (e.g., coinbase validity, size limits, or other structural checks), the node will now mark that peer as 'misbehaving'. This results in a score decrement, potentially leading to the peer being disconnected, thereby protecting the node from processing or relaying invalid chain data.

#### [#35395: doc: Improve test suite dependencies documentation](https://github.com/bitcoin/bitcoin/pull/35395)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 18 review events)*
> This PR enhances the documentation regarding the dependencies required for running Bitcoin Core's test suite. This makes it easier for developers and contributors to set up their development environment and run tests effectively.

**Technical Details:** The changes involve updating and clarifying sections within the project's documentation (e.g., `doc/dependencies.md`, `CONTRIBUTING.md`) that outline the necessary libraries, tools, and configurations for building and executing the unit, functional, and integration tests. This improves onboarding for new contributors and ensures that the documented setup accurately reflects the current testing environment requirements.

#### [#35919: p2p: cap maxconnections at 2,000 to reduce crash risk](https://github.com/bitcoin/bitcoin/pull/35919)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Security & Consensus]** *(Activity: 17 review events)*
> Implements a hard cap of 2,000 on the maximum number of peer connections a node can establish. This change significantly reduces the risk of crashes or resource exhaustion under high connection loads, improving the overall stability of the Bitcoin Core client.

**Technical Details:** This PR introduces a hard limit of 2,000 for the `maxconnections` configuration parameter within the P2P networking layer. By capping the total number of inbound and outbound connections, the change aims to prevent resource exhaustion (e.g., memory, file descriptors) that could lead to node instability or crashes under extreme network conditions or DoS attempts. This provides a safeguard against excessive peer connections.

#### [#36581: subprocess: fix command line memory leak on Windows](https://github.com/bitcoin/bitcoin/pull/36581)
**Author:** [@stickies-v](https://github.com/stickies-v) | **[Performance & Optimization]** *(Activity: 14 review events)*
> Addresses a memory leak issue on Windows when Bitcoin Core interacts with external processes. This fix improves the stability and resource management of the application, especially for users on Windows operating systems.

**Technical Details:** This PR identifies and resolves a memory leak occurring in the `subprocess` module specifically on Windows platforms. The leak likely stems from improper handling or release of resources allocated for command-line arguments or process handles when spawning child processes. The fix involves ensuring that all allocated memory and system handles are correctly deallocated after subprocess execution, preventing gradual memory consumption.

#### [#36397: scripted-diff: [wallet] Remove trailing newlines from one-line log messages](https://github.com/bitcoin/bitcoin/pull/36397)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 14 review events)*
> This PR cleans up log messages within the wallet component by removing redundant trailing newlines. This minor improvement makes log files more consistent and easier to read for developers and users debugging issues.

**Technical Details:** The change is a `scripted-diff` targeting log messages within the `wallet` subsystem that were inadvertently adding an extra newline character at the end of single-line messages. By systematically removing these trailing newlines, the PR ensures that log output is consistently formatted. This prevents unnecessary blank lines and improves readability for both automated parsing and human inspection of log files.

#### [#36524: common: drop locale setting hack](https://github.com/bitcoin/bitcoin/pull/36524)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 14 review events)*
> This PR removes an unnecessary workaround related to locale settings, simplifying the codebase. It improves the internal consistency and maintainability of Bitcoin Core by removing a non-standard practice.

**Technical Details:** Previously, Bitcoin Core included a 'hack' to explicitly set the locale to 'C' for certain operations, which was a workaround for specific environment issues. This PR removes that explicit locale setting from the `common` utility library, relying on the system's default or more standard practices. The change ensures that locale-dependent functions behave predictably without manual overrides, streamlining the codebase.

#### [#36453: util, cli: name the Sock wait timeout cap and use it for -rpcclienttimeout=0](https://github.com/bitcoin/bitcoin/pull/36453)
**Author:** [@kriss39](https://github.com/kriss39) | **[Wallet & User Tools]** *(Activity: 11 review events)*
> This PR improves the clarity and consistency of RPC client timeout handling by naming a specific socket wait timeout cap and applying it to the `-rpcclienttimeout=0` setting. This ensures that RPC clients behave predictably when an indefinite timeout is requested, preventing unintended immediate timeouts.

**Technical Details:** Previously, the behavior for `-rpcclienttimeout=0` might have been implicitly handled or inconsistent. This PR introduces a named constant for the maximum socket wait timeout, which is then explicitly used when `-rpcclienttimeout` is set to `0`. This effectively translates an 'infinite' timeout request into the maximum allowed system timeout for socket operations, preventing the client from blocking indefinitely while still allowing for very long waits. This change standardizes the interpretation of an 'infinite' timeout, making the RPC client more robust and predictable.

#### [#36177: net: fix startup failures from stale Tor examples](https://github.com/bitcoin/bitcoin/pull/36177)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Network & Privacy]** *(Activity: 10 review events)*
> This PR resolves an issue where Bitcoin Core could fail to start due to outdated Tor configuration examples. It improves the reliability of Tor integration, ensuring users can connect to the network more smoothly and privately.

**Technical Details:** The problem arose because the example Tor configuration provided within Bitcoin Core became stale, leading to startup failures when users attempted to configure Tor based on these outdated instructions. This PR updates the internal Tor configuration examples to reflect current best practices and syntax. This ensures that users leveraging Tor for network connectivity can successfully initialize their nodes without encountering configuration-related startup errors, enhancing privacy and connectivity.

#### [#1943: tests: silentpayments: cover labeled output beyond the first label batch](https://github.com/bitcoin-core/secp256k1/pull/1943)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR enhances the test suite for Silent Payments within the `secp256k1` library. It adds coverage for scenarios involving multiple 'label batches,' ensuring the robustness of this privacy-enhancing feature.

**Technical Details:** The PR introduces new test vectors and logic to validate the `secp256k1` library's handling of Silent Payments, particularly when dealing with labeled outputs that extend beyond a single 'label batch.' This involves simulating the generation and verification of multiple ephemeral keys and associated labels across different batches, ensuring that the cryptographic operations remain correct and consistent for complex Silent Payments constructions. The goal is to prevent edge-case failures in the privacy protocol.

#### [#36465: Test: Add P2SH scriptSig stack-size boundary tests](https://github.com/bitcoin/bitcoin/pull/36465)
**Author:** [@benthecarman](https://github.com/benthecarman) | **[Security & Consensus]** *(Activity: 9 review events)*
> Introduces new tests to verify Bitcoin Core's handling of P2SH scriptSig stack-size boundaries. This ensures the node correctly enforces script execution limits, protecting against potential denial-of-service vectors.

**Technical Details:** This PR adds specific test cases to validate the behavior of Bitcoin Core's script interpreter when encountering P2SH `scriptSig` inputs that push the stack size to its defined boundaries. The tests aim to confirm that the node correctly applies the maximum stack element limits during script execution, preventing excessive resource consumption or potential DoS attacks via maliciously crafted scripts. This reinforces the script validation logic.

#### [#36159: http: Improve HTTPRemoteClient::MaybeDisconnect()](https://github.com/bitcoin/bitcoin/pull/36159)
**Author:** [@hodlinator](https://github.com/hodlinator) | **[Performance & Optimization]** *(Activity: 9 review events)*
> This PR enhances the `HTTPRemoteClient`'s disconnection logic, making it more robust and efficient in managing HTTP connections. This improvement contributes to better resource management and overall stability when interacting with HTTP services.

**Technical Details:** The `HTTPRemoteClient::MaybeDisconnect()` function is responsible for determining when an HTTP connection should be closed. This PR refines the logic within this function, potentially by improving conditions for disconnection, handling edge cases more gracefully, or optimizing the timing of disconnections. The goal is to ensure that connections are closed promptly when no longer needed, preventing resource leaks or stale connections, while also keeping them open efficiently when active, thereby improving the client's overall HTTP communication reliability and resource utilization.

#### [#36457: Test: Cover malformed merkle trees and nBits](https://github.com/bitcoin/bitcoin/pull/36457)
**Author:** [@benthecarman](https://github.com/benthecarman) | **[Security & Consensus]** *(Activity: 7 review events)*
> Adds new tests to cover scenarios involving malformed Merkle trees and invalid `nBits` values in blocks. This strengthens Bitcoin Core's block validation logic, ensuring it robustly rejects invalid blocks and maintains chain integrity.

**Technical Details:** This PR introduces new test vectors and scenarios to specifically validate Bitcoin Core's handling of malformed Merkle trees and incorrect `nBits` values within block headers. The tests ensure that the block validation engine correctly identifies and rejects blocks that violate these fundamental consensus rules, preventing the acceptance of invalid blocks and maintaining the integrity of the blockchain.

#### [#36368: bitcoin-tx: reject in and outscript arguments with too many separators](https://github.com/bitcoin/bitcoin/pull/36368)
**Author:** [@Bruce039](https://github.com/Bruce039) | **[Wallet & User Tools]** *(Activity: 7 review events)*
> This PR improves the `bitcoin-tx` command-line utility by adding stricter validation for script arguments. It now rejects inputs with too many separators, making the tool more robust and user-friendly by preventing common input errors.

**Technical Details:** The change modifies the argument parsing logic within the `bitcoin-tx` utility. Specifically, it introduces a check for the `inscript` and `outscript` arguments to ensure they do not contain an excessive number of separators. Previously, malformed inputs with extra separators might have led to unexpected parsing behavior or errors. By explicitly rejecting such inputs, the utility provides clearer feedback to the user and prevents potential issues arising from ambiguous argument structures.

#### [#36508: [32.0] Finalize](https://github.com/bitcoin/bitcoin/pull/36508)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> Prepares the codebase for the upcoming 32.0 release, ensuring all necessary updates and checks are complete for a stable launch. This PR finalizes the development cycle for the next major version of Bitcoin Core.

**Technical Details:** This PR likely involves updating version strings, release notes, and potentially performing final sanity checks or build system adjustments specific to the 32.0 release branch. It ensures that all release-critical tasks are completed and the codebase is ready for tagging and distribution. This typically includes reviewing dependencies and build configurations.

#### [#36596: [32.x] Backports](https://github.com/bitcoin/bitcoin/pull/36596)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR bundles a collection of backported changes for the 32.x release branch of Bitcoin Core. It ensures that important fixes and minor improvements from the main development branch are integrated into the stable release, enhancing its overall stability and functionality.

**Technical Details:** This PR represents a meta-PR, incorporating a set of cherry-picked commits from the `master` branch into the `32.x` release branch. These backports typically include critical bug fixes, minor performance enhancements, or security patches deemed essential for the stability and robustness of the maintenance release, without introducing major new features or breaking changes.

#### [#36287: build: Bump Xcode CLT minimum supported version to 26.3](https://github.com/bitcoin/bitcoin/pull/36287)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> Updates the minimum required Xcode Command Line Tools version for building Bitcoin Core on macOS to 26.3. This ensures compatibility with modern development environments and allows developers to use up-to-date tools.

**Technical Details:** This PR modifies the build system configuration, specifically for macOS, to increase the minimum supported version of Xcode Command Line Tools (CLT) to 26.3. This adjustment is typically made to align with newer compiler versions, SDKs, or to leverage features/fixes available in more recent CLTs, ensuring the project can be built with contemporary Apple development tools. It might involve updating CI configurations as well.

#### [#36559: test: zero-pad the port in feature_anchors' expected hex](https://github.com/bitcoin/bitcoin/pull/36559)
**Author:** [@kravens](https://github.com/kravens) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR makes a minor adjustment to a test related to the `feature_anchors` by ensuring that port numbers in expected hexadecimal outputs are consistently zero-padded. This improves the robustness of the test by aligning with standard data representation and preventing potential test failures due to formatting discrepancies.

**Technical Details:** In network protocols or data serialization, numerical values like port numbers are often represented in a fixed-width format, sometimes requiring zero-padding for consistency. This test likely involves comparing a generated hexadecimal string (which includes a port number) against an expected value. The change ensures that the expected hexadecimal string correctly accounts for zero-padding of the port number, preventing false negatives in the test due to a mismatch in string representation rather than actual data content. This is a precise fix for a test's expected output.

#### [#36231: test: add pow tests covering live mutants](https://github.com/bitcoin/bitcoin/pull/36231)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR enhances the robustness of Bitcoin Core's Proof-of-Work validation by adding new tests. These tests specifically target 'live mutants' to ensure the PoW logic is thoroughly covered and resilient to subtle changes.

**Technical Details:** The PR introduces additional test cases for the Proof-of-Work validation logic. These tests are designed using a mutant testing approach, where specific, subtle variations (mutants) of the PoW implementation are considered. The new tests aim to 'kill' these mutants, thereby proving that the existing test suite is comprehensive enough to detect even minor deviations in PoW calculation or verification. This strengthens the confidence in the correctness of the consensus-critical PoW implementation.

#### [#36438: test: a switch to tx relay via filterclear can trigger eviction](https://github.com/bitcoin/bitcoin/pull/36438)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR adds a test case to ensure Bitcoin Core correctly handles specific network scenarios related to transaction relay. It verifies that a peer switching its transaction relay method can properly trigger mempool eviction logic.

**Technical Details:** The new test simulates a peer's behavior where it initially uses one method for transaction relay (e.g., compact blocks) and then switches to another, such as relaying individual transactions after a `filterclear` message. The test specifically checks that this change in relay strategy correctly interacts with the node's mempool eviction mechanisms. This ensures that the node's resource management and transaction processing remain robust even when peer behavior changes dynamically.

#### [#36531: guix: use `--load-path` for local modules](https://github.com/bitcoin/bitcoin/pull/36531)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR updates the Guix build system to correctly use `--load-path` for local modules, improving the reliability and maintainability of Bitcoin Core's reproducible builds. This ensures that the build environment consistently locates necessary components.

**Technical Details:** The Guix build system relies on modules to define packages and build recipes. When local, custom modules are used, Guix needs to know where to find them. This PR modifies the Guix build invocation or configuration to explicitly pass the `--load-path` option, directing Guix to the directory containing these local modules. This resolves potential issues where modules might not be found, ensuring that the reproducible build process for Bitcoin Core remains robust and consistent across different environments.

#### [#36422: test: check unconnecting headers don't reset the getheaders rate limit](https://github.com/bitcoin/bitcoin/pull/36422)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR introduces a test to verify that receiving invalid or unconnecting block headers does not reset the rate limit for requesting headers from peers. This is crucial for protecting the node from denial-of-service attacks.

**Technical Details:** The test case simulates a scenario where a peer sends `getheaders` messages, and the node receives headers that do not connect to its current best chain. The objective is to confirm that the internal rate limiting mechanism for `getheaders` requests is not inadvertently reset by these unconnecting headers. This prevents a malicious peer from exploiting the rate limit by sending non-useful headers, thereby ensuring the node's ability to maintain its header synchronization process efficiently and securely.

#### [#36545: test: Fix intermittent issue in p2p_initial_headers_sync.py](https://github.com/bitcoin/bitcoin/pull/36545)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR resolves an intermittent failure in the `p2p_initial_headers_sync.py` test, making the test suite more reliable. By fixing this sporadic issue, developers can trust the test results more, ensuring the stability of the initial block header synchronization process.

**Technical Details:** The `p2p_initial_headers_sync.py` test simulates the process of a new node synchronizing its block headers with the network. An intermittent issue suggests a race condition, timing dependency, or subtle state management problem within the test setup or assertion. This PR identifies and addresses the root cause of this flakiness, likely by adding appropriate delays, improving synchronization points, or refining assertions to account for network variability, thereby ensuring the test consistently passes when the underlying code is correct.

#### [#36456: Test: Cover malformed and truncated tx encodings](https://github.com/bitcoin/bitcoin/pull/36456)
**Author:** [@benthecarman](https://github.com/benthecarman) | **[Security & Consensus]** *(Activity: 4 review events)*
> Adds new tests to cover scenarios involving malformed and truncated transaction encodings. This enhances the robustness of Bitcoin Core by ensuring it correctly handles and rejects invalid transaction data, preventing potential issues.

**Technical Details:** This PR introduces new unit and/or functional tests specifically designed to validate Bitcoin Core's handling of malformed and truncated transaction encodings. The tests aim to ensure that the deserialization and validation logic correctly identifies and rejects transactions that do not conform to the Bitcoin protocol's serialization rules. This improves the resilience of the node against invalid or maliciously crafted transaction data.

#### [#36339: wallet: avoid int overflow in listtransactions](https://github.com/bitcoin/bitcoin/pull/36339)
**Author:** [@kriss39](https://github.com/kriss39) | **[Wallet & User Tools]** *(Activity: 4 review events)*
> This PR fixes a potential integer overflow bug in the `listtransactions` RPC, preventing crashes or incorrect results under specific conditions. This improves the stability and reliability of wallet transaction listing, especially for wallets with a very large number of transactions.

**Technical Details:** The `listtransactions` RPC internally uses an integer type to count or index transactions. For wallets with an extremely high number of transactions, this integer could potentially overflow, leading to undefined behavior, crashes, or incorrect transaction listings. This PR identifies the specific integer variable susceptible to overflow and upgrades its type (e.g., from `int` to `size_t` or `long long`) to accommodate a much larger range of values. This ensures the RPC remains robust even with very large transaction histories.

#### [#36616: test: keep noban_tx_relay config after node is restarted](https://github.com/bitcoin/bitcoin/pull/36616)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR ensures that the `noban_tx_relay` configuration setting persists even after a node restart in tests. This improves the consistency and reliability of testing scenarios involving this specific transaction relay policy.

**Technical Details:** The change likely involves modifying the test framework or node configuration handling within tests to ensure that the `noban_tx_relay` setting, once applied, is correctly saved and reloaded when a test node is shut down and restarted. This prevents test flakiness where the desired relay behavior might not be active after a simulated restart, ensuring more accurate and repeatable testing of transaction relay policies.

#### [#36319: [31.x] More Backports](https://github.com/bitcoin/bitcoin/pull/36319)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> Incorporates additional bug fixes and minor improvements from the main development branch into the 31.x release series. This ensures users on the 31.x branch receive important updates without waiting for a full new major release.

**Technical Details:** This PR cherry-picks or merges a collection of commits from a more recent development branch (e.g., `master`) into the `31.x` release branch. The backported changes typically include bug fixes, minor performance enhancements, or non-disruptive improvements that are deemed stable and beneficial for the maintenance release. This process ensures critical updates are available to users on older stable versions.

#### [#36599: test: Fix intermittent timeout waiting for ibd_wtxid getdata](https://github.com/bitcoin/bitcoin/pull/36599)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> Resolves an intermittent timeout issue in tests related to initial block download and witness transaction ID requests. This improves the reliability of our automated testing suite, ensuring more consistent and accurate test results.

**Technical Details:** This PR addresses an intermittent test failure where a timeout occurs while waiting for `ibd_wtxid getdata` messages during initial block download simulations. The fix likely involves adjusting test synchronization mechanisms, increasing timeout thresholds, or refining the test's simulation of network conditions to prevent race conditions or unexpected delays. This ensures the test suite accurately reflects expected behavior rather than failing due to timing sensitivities.

#### [#36579: refactor: Enable some string performance tidy rules](https://github.com/bitcoin/bitcoin/pull/36579)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR refactors the codebase by enabling specific static analysis rules focused on improving string performance. This helps ensure that string manipulations within Bitcoin Core are handled efficiently, contributing to overall code quality and minor performance gains.

**Technical Details:** This change likely involves updating the `.clang-tidy` configuration or similar static analysis tool settings to enable checks related to inefficient string operations, such as unnecessary copies or suboptimal concatenations. The refactoring itself would then involve applying the suggestions from these rules to existing code, modifying string usage patterns to be more performant. This ensures that string objects are handled in a way that minimizes allocations and copies, leading to slightly faster execution and reduced memory overhead in string-heavy operations.

#### [#36582: test: reorder functional tests by current runtimes](https://github.com/bitcoin/bitcoin/pull/36582)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR reorders the functional tests based on their current execution runtimes, aiming to optimize the overall test suite duration. By running faster tests first or grouping similar runtime tests, it can improve CI efficiency and provide quicker feedback.

**Technical Details:** The change involves analyzing the execution times of individual functional tests and then modifying the test runner configuration or script to prioritize tests based on these observed runtimes. A common strategy is to run the fastest tests first to get quick feedback on basic functionality, or to group tests of similar duration to better utilize parallel execution resources. This optimization helps to reduce the total time required for the continuous integration (CI) pipeline, making development cycles more efficient.

#### [#36573: test: cover gettxspendingprevout error without txospenderindex](https://github.com/bitcoin/bitcoin/pull/36573)
**Author:** [@mercie-ux](https://github.com/mercie-ux) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR adds a new test case to cover an error scenario for the `gettxspendingprevout` RPC when the `txospenderindex` is not available. This ensures the RPC's error handling is robust and predictable, improving the reliability of wallet and transaction-related queries.

**Technical Details:** The `gettxspendingprevout` RPC is used to query information about transactions spending specific previous outputs. This test specifically targets a scenario where the `txospenderindex` (transaction output spender index) might be missing or unavailable, which should result in a defined error. The test likely involves calling the RPC with parameters that trigger this error condition and then asserting that the expected error code and message are returned. This verifies the correct behavior of the RPC's input validation and error reporting mechanisms.

#### [#36295: refactor: Remove args-wrappers in favor of naked value_or()](https://github.com/bitcoin/bitcoin/pull/36295)
**Author:** [@hodlinator](https://github.com/hodlinator) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR refactors internal code by replacing argument wrappers with a more direct `value_or()` pattern. This improves code readability and maintainability for developers working on Bitcoin Core.

**Technical Details:** The change removes boilerplate code associated with `args-wrappers` that previously handled optional arguments. By directly using `value_or()` on `std::optional` or similar types, the code becomes more concise and idiomatic C++. This simplifies argument access and reduces potential for errors in argument parsing logic, leading to cleaner and more robust internal APIs.

#### [#36624: test: Enable noban_tx_relay in a few more tests](https://github.com/bitcoin/bitcoin/pull/36624)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR expands the use of the `noban_tx_relay` configuration option in additional tests. This helps ensure that the transaction relay logic, especially for unbannable transactions, is thoroughly tested under various scenarios, improving the reliability of transaction propagation.

**Technical Details:** The PR modifies existing test setups to include the `noban_tx_relay` configuration flag for specific test nodes. This allows the tests to simulate scenarios where certain transactions are always relayed, even from peers that might otherwise be banned, ensuring that the transaction relay policy and its interactions with peer management are correctly implemented and robust.

#### [#1975: ci: Run ctime_tests under Valgrind on arm64](https://github.com/bitcoin-core/secp256k1/pull/1975)
**Author:** [@fametrano](https://github.com/fametrano) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR enhances the `secp256k1` library's continuous integration by running constant-time tests under Valgrind on ARM64 architecture. This helps detect memory errors and ensures the cryptographic code remains robust and secure on a wider range of platforms.

**Technical Details:** The change modifies the CI configuration for the `secp256k1` library. Specifically, it adds a new job or step to execute the `ctime_tests` (tests designed to verify constant-time execution properties) using Valgrind, a memory error detection tool, on an `arm64` architecture build. This ensures that memory access patterns and allocations within critical cryptographic functions are free from leaks, invalid accesses, or other memory-related bugs, particularly on a platform where such issues might manifest differently than on x86.

#### [#36509: refactor: remove more dead code](https://github.com/bitcoin/bitcoin/pull/36509)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR cleans up the Bitcoin Core codebase by identifying and removing additional dead code. This effort reduces the project's technical debt, making the codebase smaller, easier to understand, and more maintainable.

**Technical Details:** The change involves identifying code paths or functions that are no longer reachable or used by any part of the application. This typically requires static analysis tools or careful manual inspection of call graphs. Removing dead code simplifies the compilation unit, potentially reducing binary size and improving build times. It also reduces the cognitive load for developers, as there is less irrelevant code to sift through, improving overall code quality and maintainability.

#### [#36279: test: non-inbound version message promotes address to tried table](https://github.com/bitcoin/bitcoin/pull/36279)
**Author:** [@naiyoma](https://github.com/naiyoma) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR adds a new test to ensure that Bitcoin Core correctly handles addresses from non-inbound version messages, promoting reliable peer addresses to the tried table. This helps maintain a robust and well-connected peer network by verifying address management logic.

**Technical Details:** The test specifically simulates a scenario where a peer sends a `VERSION` message without being an inbound connection. It then verifies that the address associated with this peer is correctly added to the node's 'tried' table, which stores addresses of peers that have proven to be useful. This ensures the address manager's logic for promoting addresses based on successful handshakes, regardless of connection direction, is functioning as expected. The test likely involves mocking network interactions or using a test framework to control peer behavior.

#### [#36407: test: make orphanage_dos_many fill the orphanage](https://github.com/bitcoin/bitcoin/pull/36407)
**Author:** [@fametrano](https://github.com/fametrano) | **[Security & Consensus]** *(Activity: 2 review events)*
> This PR enhances a Denial of Service (DoS) test by ensuring it effectively fills the transaction orphanage, a mechanism that temporarily holds unconfirmed transactions. This improves the test's ability to verify the robustness of Bitcoin Core's DoS protection against attacks that attempt to overload the orphanage.

**Technical Details:** The transaction orphanage is a memory-limited cache for transactions whose parents are not yet known. A DoS attack could try to fill this orphanage with invalid or unspendable transactions to evict legitimate ones. This test, `orphanage_dos_many`, is designed to simulate such an attack. The PR likely modifies the test's parameters or transaction generation logic to ensure that it reliably pushes the orphanage to its capacity limits, thereby thoroughly exercising the eviction policies and size constraints of the orphanage to confirm its resilience against DoS attempts.

#### [#36341: wallet: return error from bitcoin-wallet create](https://github.com/bitcoin/bitcoin/pull/36341)
**Author:** [@kriss39](https://github.com/kriss39) | **[Wallet & User Tools]** *(Activity: 2 review events)*
> This PR improves the `bitcoin-wallet create` command by making it return a proper error code when wallet creation fails. This provides clearer feedback to users and scripts, allowing for better automation and error handling.

**Technical Details:** Previously, if the `bitcoin-wallet create` command encountered an error (e.g., trying to create an already existing wallet), it might have exited without a non-zero error code. This PR modifies the command-line utility to explicitly return a non-zero exit status (e.g., `EXIT_FAILURE`) when an error occurs during wallet creation. This change aligns the command's behavior with standard Unix error reporting conventions, significantly improving its usability in automated environments and scripts.

#### [#1961: ci: run exhaustive_tests for group orders 7 and 199](https://github.com/bitcoin-core/secp256k1/pull/1961)
**Author:** [@fametrano](https://github.com/fametrano) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This update enhances the testing of Bitcoin's core cryptographic library, secp256k1, by adding more thorough checks for specific mathematical properties. This ensures the foundational cryptography remains robust and secure, strengthening Bitcoin's overall reliability.

**Technical Details:** This PR modifies the Continuous Integration (CI) configuration for the `secp256k1` library. It extends the `exhaustive_tests` suite to include checks for group orders 7 and 199, which are small prime orders used to test edge cases in scalar and point arithmetic. By running these additional, computationally intensive tests, the PR aims to catch subtle bugs or inconsistencies in the curve's implementation. This improves the confidence in the correctness of the cryptographic primitives used throughout Bitcoin Core.

#### [#36590: doc: archive release notes for v32.0](https://github.com/bitcoin/bitcoin/pull/36590)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR archives the release notes for Bitcoin Core version 32.0. This ensures that historical release information is properly organized and accessible for future reference.

**Technical Details:** The PR moves the release notes document for version 32.0 from a temporary or current location to a designated archive directory within the project's documentation structure. This organizational task helps maintain a clear history of changes and features introduced in past releases, making it easier to track development over time.

#### [#1952: util: make STATIC_ASSERT usable at file scope](https://github.com/bitcoin-core/secp256k1/pull/1952)
**Author:** [@real-or-random](https://github.com/real-or-random) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR improves the `secp256k1` library by making its `STATIC_ASSERT` macro usable at the file scope. This allows developers to perform compile-time checks on global data structures and constants, enhancing code correctness and robustness.

**Technical Details:** The change modifies the `STATIC_ASSERT` macro definition within the `secp256k1` utility library. Previously, its usage might have been restricted to function scope due to implementation details. By adjusting the macro, it can now be invoked directly at the file level, outside of any function definition. This enables compile-time validation of global variables, struct sizes, or other constants, ensuring fundamental assumptions about the code's data layout are met before runtime.

#### [#36401: [30.x] More Backports](https://github.com/bitcoin/bitcoin/pull/36401)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> Integrates additional bug fixes and minor enhancements from the main development branch into the 30.x release series. This ensures users on the 30.x branch benefit from important updates and stability improvements.

**Technical Details:** This PR incorporates a set of commits, typically cherry-picked, from a more recent development branch into the `30.x` release branch. The backported changes are generally bug fixes, minor performance improvements, or non-disruptive code quality enhancements that are deemed stable and beneficial for the ongoing maintenance of the `30.x` series. This process helps keep older stable releases up-to-date with critical patches.

#### [#36553: test: Add missing sync_mempools in wallet_conflicts.py](https://github.com/bitcoin/bitcoin/pull/36553)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR enhances the reliability of wallet conflict tests by adding a crucial synchronization step. This ensures that test scenarios accurately reflect real-world network conditions, leading to more robust and dependable wallet functionality.

**Technical Details:** The `wallet_conflicts.py` test suite simulates scenarios where transactions might conflict in a multi-node environment. The missing `sync_mempools` call meant that nodes in the test might not have had a consistent view of pending transactions before conflict resolution logic was tested. By adding this synchronization, the test ensures that all participating nodes' mempools are aligned, making the test results more deterministic and accurately validating the wallet's conflict handling mechanisms.

#### [#1965: remove unused SECP256K1_GE_CONST_INFINITY](https://github.com/bitcoin-core/secp256k1/pull/1965)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR cleans up the `secp256k1` library by removing an unused constant, `SECP256K1_GE_CONST_INFINITY`. This reduces code bloat and improves overall maintainability.

**Technical Details:** The change identifies and removes the `SECP256K1_GE_CONST_INFINITY` constant definition from the `secp256k1` codebase. Static analysis or code review determined that this constant was no longer referenced anywhere in the library's implementation. Eliminating dead code reduces the compiled binary size, improves compilation times, and simplifies future code navigation and maintenance efforts.

#### [#36541: test: Small p2p_node_network_limited.py cleanups](https://github.com/bitcoin/bitcoin/pull/36541)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR introduces minor cleanups to the `p2p_node_network_limited.py` test, improving its readability and maintainability. These small refinements contribute to a more organized and easier-to-understand test suite.

**Technical Details:** This PR involves refactoring and minor adjustments within the `p2p_node_network_limited.py` test file. These cleanups might include removing redundant code, improving variable names, reordering statements for clarity, or standardizing formatting. The goal is to make the test code more maintainable and easier for developers to understand and extend without altering the test's functional behavior or coverage, ensuring long-term test suite health.

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#36581: subprocess: fix command line memory leak on Windows](https://github.com/bitcoin/bitcoin/pull/36581)
**Author:** [@stickies-v](https://github.com/stickies-v) | **[Performance & Optimization]** *(Activity: 14 review events this week)*
> Addresses a memory leak issue on Windows when Bitcoin Core interacts with external processes. This fix improves the stability and resource management of the application, especially for users on Windows operating systems.

#### [#36620: test: Add case for libstdc++ bug on Windows](https://github.com/bitcoin/bitcoin/pull/36620)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 11 review events this week)*
> This PR adds a new test case to address a specific bug in the `libstdc++` library when running Bitcoin Core on Windows. It ensures the software behaves correctly and reliably for Windows users by preventing potential crashes or incorrect behavior related to this library bug.

#### [#36586: coins: warn of low disk space before chainstate compaction](https://github.com/bitcoin/bitcoin/pull/36586)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Wallet & User Tools]** *(Activity: 10 review events this week)*
> This PR introduces a warning mechanism to alert users when their disk space is running low before the chainstate compaction process begins. This helps users avoid potential issues like crashes or data corruption due to insufficient disk space during a critical operation.

#### [#36525: mining: add getTotalFees(), protect m_block_template with mutex](https://github.com/bitcoin/bitcoin/pull/36525)
**Author:** [@Sjors](https://github.com/Sjors) | **[Wallet & User Tools]** *(Activity: 9 review events this week)*
> This PR enhances the mining module by adding a function to calculate total fees and protecting the block template with a mutex. These changes improve the robustness and accuracy of fee reporting for miners and ensure thread-safe access to critical mining data.

#### [#36036: build: Bump clang minimum supported version to 19](https://github.com/bitcoin/bitcoin/pull/36036)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 9 review events this week)*
> This PR updates the minimum required Clang compiler version to 19 for building Bitcoin Core. This ensures that developers are using modern compiler features and optimizations, contributing to a more robust and performant build process.

## 🗓️ Dev Meeting
Summary of the core dev IRC meeting on 2026-10-22 with 19 participants.

- Fuzzing WG Update (eugenesiegel, marcofleon): eugenesiegel is working on getting bedrock into shape for fuzzamoto, which found minor database consistency issues (e.g., a node having power loss during -reindex prevents startup). stickies-v suggested not to over-engineer fixes for loud failures, while darosior recommended opening an issue for potential underlying bugs.
- QML GUI WG Update (johnny9dev): The team is addressing feedback from last week, with a PR to clarify storage choices during onboarding. Priority is getting the staging branch ready. johnny9dev is exploring pruned wallet setup, including txindex and compact block filters for pruned rescans and block retrieval. Murch raised the possibility of merging the new GUI into v33, but hebasto and stickies-v deemed it premature until the staging branch is available, which johnny9dev expects by late November/early December.
- Windows Code Signer (achow101): achow101 highlighted that he is currently the sole Windows code signer, creating a single point of failure. He requested volunteers who are committed to building all releases and release candidates shortly after tagging to contact him.
- Reimplement private broadcast as node state-less jobs + package relay support (#36608) (instagibbs): instagibbs presented PR #36608, a node state-less private broadcast variant with 1p1c package relay support, proposed for v33. The PR involves ~4.6k net LOC in logic, entirely outside consensus-critical code. instagibbs sought high-level spec discussions, project buy-in for v33, feedback on including a standalone tool variant, and advice on splitting the PR (e.g., one PR for the swap, one for package relay). andrewtoth_ questioned the feasibility of a 17k line PR for v33 and whether previous concerns were addressed. darosior supported the structural fix to node state leaks for privacy guarantees, suggesting the standalone tool could be integrated into bitcoin-util and the swap should be a single PR, with package relay as a follow-up. stickies-v agreed with darosior on the PR splitting.
- General Updates (fanquake): fanquake announced that Bitcoin Core v32.0 has been tagged. Updates to the security policy have been merged (bitcoincore.org PR #1281), and a PR to enroll Core in the Anthropic OSS scanner (anthropics/oss-scanner PR #1018) is open.

**Action Items:**
- eugenesiegel: Open an issue for the minor database consistency issues found during fuzzing.
- achow101: Interested developers to contact him regarding becoming an additional Windows code signer.
- instagibbs: Continue offline discussions regarding the design and implementation of PR #36608.
- cfields: Review PR #36608 and discuss potential overlap with multi-process p2p work with instagibbs out-of-band.
- Developers: Review instagibbs's PR #36608.

## 🗣️ Research & Governance
Top active threads across mailing lists and research forums.

### [TCP hole punching for Bitcoin nodes behind home NATs?](https://delvingbitcoin.org/t/tcp-hole-punching-for-bitcoin-nodes-behind-home-nats/2497/25)
**Source:** Delving | **Started By:** {'username': '0xB10C', 'uuid': 'can_0xb10c'} | **Messages:** 9
> Developers are actively discussing methods to increase the number of reachable Bitcoin nodes, particularly for home users, enhancing the network's decentralization and resilience. This involves exploring advanced networking techniques to help nodes behind residential internet connections connect more reliably.

**Technical Details:** The discussion on increasing residential node reachability has evolved into a deeper architectural debate, questioning the fundamental problem solved by NAT traversal features. Anthony Towns clarified the nuanced behavior of SO_REUSEADDR/PORT with NAT mappings, suggesting a single IP:port can be reused for multiple connections under specific conditions. This led to 0xB10C proposing a strategy of publishing hundreds or thousands of holepunch requests to scale reachability, while also considering methods to raise the cost for potential attackers. The focus is now on securely implementing scalable NAT traversal, balancing increased node connectivity with robust attack mitigation strategies.

### [Best critiques of BIP300/drivechains?](https://delvingbitcoin.org/t/best-critiques-of-bip300-drivechains/2969/1)
**Source:** Delving | **Started By:** {'username': 'user3', 'uuid': 'auto_user3'} | **Messages:** 3
> Community members are seeking to understand and critically evaluate alternative blockchain scaling and feature proposals, specifically focusing on the eCash fork and related technologies like drivechains.

**Technical Details:** The discussion centers on a critical evaluation of the upcoming eCash fork, alongside deep dives into BIP300 (drivechains) and blind merged mining. Participants are seeking well-reasoned technical critiques concerning the architectural implications of these proposals. Key areas of debate include the security model of drivechains, the decentralization aspects of blind merged mining, and the overall impact of such designs on the core Bitcoin protocol's integrity and censorship resistance. The community is tasked with compiling and analyzing existing arguments to foster a comprehensive understanding of these alternative scaling and feature extension mechanisms.

### [Several projects to make merchant adoption easier and cheaper](https://delvingbitcoin.org/t/several-projects-to-make-merchant-adoption-easier-and-cheaper/2967/1)
**Source:** Delving | **Started By:** {'username': 'user3', 'uuid': 'auto_user3'} | **Messages:** 3
> Developers are working to simplify merchant onboarding, especially for Lightning payments, by ensuring reliable payment options and smooth fallbacks for a better user experience.

**Technical Details:** The discussion centers on improving merchant payment reliability by implementing robust fallback mechanisms. On-chain payment options are proposed to be consistently displayed on checkout screens when enabled. For Lightning payments, a critical fallback system is being designed where if a merchant's Lightning wallet is offline or lacks sufficient liquidity, the payment flow automatically transitions to an alternative Lightning option or a pre-defined next payment method. This aims to address common Lightning reliability issues and streamline the payment experience.

### [Cost-Bounded Transaction Filtering Language](https://delvingbitcoin.org/t/cost-bounded-transaction-filtering-language/2966/1)
**Source:** Delving | **Started By:** {'username': 'epoch', 'uuid': 'auto_epoch'} | **Messages:** 2
> A new feature allows Bitcoin node operators to precisely control which types of transactions their node processes. This gives users more power to customize their node's behavior and potentially improve efficiency.

**Technical Details:** A new proposal introduces a Domain Specific Language (DSL) for defining custom transaction filtering policies. This DSL has been implemented in `satd`, a Bitcoin node written in Rust, enabling node operators to specify precise criteria for the transaction shapes they wish to process and relay. The aim is to provide granular control over mempool contents and resource usage, allowing for tailored node behavior beyond standard policy rules.

### [[bitcoindev] btc-verified October Update: Connecting Map to Territory](https://gnusha.org/pi/bitcoindev/CALeFGL04_h6212x9D0u7-uJSyDDAyie-cohBazYS3Yo9P36NVA@mail.gmail.com)
**Source:** Mailing List | **Started By:** {'username': 'Keagan McClelland', 'uuid': 'can_keagan_mcclelland'} | **Messages:** 2
> We're making progress on formally proving that all Bitcoin software interprets transactions identically, which is crucial for preventing errors and enhancing the network's security and reliability. This ensures the 'map' (specifications) perfectly matches the 'territory' (code).

**Technical Details:** The thread, originating from a discussion on connecting formal models ('map') to code implementations ('territory'), now highlights active work on formal equivalence proofs for Bitcoin script engines. Matt Corallo reports that resources are being allocated to use 'agents' (likely automated formal verification tools) to mathematically demonstrate that different script execution environments yield identical results. This effort is critical for guaranteeing consensus consistency across the network and mitigating potential consensus-split vulnerabilities by formally verifying implementation correctness against specifications or other implementations.

## 🏆 Contributor Shoutouts
### 🎉 First-Time Merges
Welcome to the codebase: [@Bruce039](https://github.com/Bruce039), [@kravens](https://github.com/kravens)

### ✍️ Top Authors
The most active PR authors this week: [@fanquake](https://github.com/fanquake), [@maflcko](https://github.com/maflcko), [@ViniciusCestarii](https://github.com/ViniciusCestarii), [@kriss39](https://github.com/kriss39), [@benthecarman](https://github.com/benthecarman)

### 🕵️ Top Reviewers
Providing critical review and testing: [@fametrano](https://github.com/fametrano), [@maflcko](https://github.com/maflcko), [@sedited](https://github.com/sedited), [@hebasto](https://github.com/hebasto), [@fanquake](https://github.com/fanquake)
