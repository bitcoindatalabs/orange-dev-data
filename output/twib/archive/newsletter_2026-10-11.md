# 📰 This Week in Bitcoin (2026-10-05 to 2026-10-11)

## 📌 The TL;DR
- A significant focus on enhancing the core's robustness and security through extensive testing infrastructure improvements (fuzzing, CI isolation, race condition fixes, TSAN), critical bug fixes (e.g., BIP-352 malleability, CVE-2024-38365), and internal code quality refactors (e.g., structured logging, `NotNull` utility).
- Ongoing, critical discussions within the wider development community regarding future protocol extensions and scaling solutions, including novel Layer 2 constructions (Lichen), confidential transactions (Flame), and in-depth security analysis of major soft-fork proposals like Drivechains (BIP 300).

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

#### [#35037: ipc: support per-address max-connections options on -ipcbind](https://github.com/bitcoin/bitcoin/pull/35037)
**Author:** [@enirox001](https://github.com/enirox001) | **[Network & Privacy]** *(Activity: 57 review events)*
> This PR enhances the Inter-Process Communication (IPC) interface by allowing users to specify a maximum number of connections for each individual IPC binding address. This provides more granular control over resource usage and security for local applications interacting with Bitcoin Core.

**Technical Details:** The implementation modifies the IPC server to parse and apply a `max-connections` option associated with specific `ipcbind` addresses. This involves extending the configuration parsing logic for `ipcbind` entries to accommodate an optional integer connection limit per binding. The IPC connection handler then enforces this limit, rejecting new connections once the maximum for a given address is reached. This mechanism allows for tailored resource management based on the origin or purpose of different IPC consumers.

#### [#34374: kernel: use struct-based logging and simplify logging interface](https://github.com/bitcoin/bitcoin/pull/34374)
**Author:** [@stickies-v](https://github.com/stickies-v) | **[Strategic Initiatives]** *(Activity: 36 review events)*
> This PR updates the core logging system in the kernel module to use a structured format and simplifies its interface. This improves the readability and parsability of logs, making debugging and monitoring Bitcoin Core easier for developers and advanced users.

**Technical Details:** The change introduces structured logging principles within the `kernel` module, likely moving towards key-value pairs or JSON-like output. It refactors the logging interface to be more uniform and easier to use, potentially reducing boilerplate and improving consistency across different log messages, which is a foundational improvement for diagnostics.

#### [#36340: util: cap Sock::WaitMany timeout to fix -rpcclienttimeout=0 on macOS](https://github.com/bitcoin/bitcoin/pull/36340)
**Author:** [@kriss39](https://github.com/kriss39) | **[Wallet & User Tools]** *(Activity: 29 review events)*
> This PR fixes an issue on macOS where setting the RPC client timeout to zero would cause unexpected behavior. It caps the `Sock::WaitMany` timeout to ensure proper functionality and prevent potential hangs or errors specific to the macOS platform.

**Technical Details:** The change introduces a maximum cap for the `Sock::WaitMany` timeout parameter, specifically addressing a platform-dependent behavior on macOS. On macOS, a timeout value of zero, often intended to mean 'wait indefinitely,' can be misinterpreted by the underlying socket API, leading to immediate returns or incorrect handling. By capping this value, the PR ensures that the socket wait function behaves as expected, even when `-rpcclienttimeout=0` is specified, preventing hangs or erroneous behavior on macOS systems.

#### [#32895: wallet: Prepare for future upgrades by recording versions of last client to open and decrypt](https://github.com/bitcoin/bitcoin/pull/32895)
**Author:** [@achow101](https://github.com/achow101) | **[Wallet & User Tools]** *(Activity: 28 review events)*
> This PR enhances the wallet's internal structure by recording the Bitcoin Core version that last opened and decrypted it. This prepares the wallet for smoother future upgrades and allows for version-specific compatibility checks.

**Technical Details:** The wallet database schema is extended to store version information, specifically the client version that performed the last open and decrypt operations. This data will be persisted within the wallet file itself. In future upgrades, this recorded version can be used to detect potential incompatibilities, trigger specific migration routines, or provide better diagnostics if an older client tries to interact with a newer wallet, improving forward compatibility.

#### [#34844: util: Add util::NotNull<SmartPtrType>](https://github.com/bitcoin/bitcoin/pull/34844)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 28 review events)*
> This PR introduces a new utility type, `util::NotNull`, to ensure that smart pointers cannot hold null values, thereby preventing common programming errors. This enhances code safety and reduces the risk of dereferencing null pointers.

**Technical Details:** This change adds `util::NotNull<SmartPtrType>` which is a wrapper class designed to enforce non-nullability for smart pointers like `std::unique_ptr` or `std::shared_ptr`. It likely provides constructor overloads that assert non-null input and overloaded `operator*` and `operator->` for transparent access to the underlying pointer, ensuring that a `NotNull` instance always points to a valid object.

#### [#36277: net: always complete all initial private broadcast connections](https://github.com/bitcoin/bitcoin/pull/36277)
**Author:** [@andrewtoth](https://github.com/andrewtoth) | **[Network & Privacy]** *(Activity: 21 review events)*
> This PR ensures that Bitcoin Core always attempts to complete all initial private broadcast connections. This improves the reliability of private transaction propagation and enhances network privacy by ensuring messages reach their intended recipients.

**Technical Details:** This change modifies the network connection logic to guarantee that all configured initial private broadcast connections are fully established, rather than potentially being dropped or incomplete under certain conditions. This involves adjustments to the connection manager's state machine or retry logic for these specific connection types, ensuring robust and reliable private message dissemination and improving network privacy guarantees.

#### [#36303: http: Log bytes received from client, use to replace receive-throttle regression test](https://github.com/bitcoin/bitcoin/pull/36303)
**Author:** [@pinheadmz](https://github.com/pinheadmz) | **[Maintenance & Tech Debt]** *(Activity: 18 review events)*
> This PR improves the HTTP server's logging capabilities and refactors a related regression test. It provides better visibility into client communication and streamlines the testing of HTTP request handling.

**Technical Details:** The PR introduces logging for the number of bytes received from HTTP clients within the `http` module. This new metric is then utilized to replace an existing 'receive-throttle' regression test, likely by directly asserting on the logged byte counts rather than relying on indirect timing or resource consumption measurements. This change provides more precise and direct verification of the HTTP server's throttling mechanisms and client interaction.

#### [#35989: wallet: fix crash on importdescriptors with a range ending at 2^31-1](https://github.com/bitcoin/bitcoin/pull/35989)
**Author:** [@shuv-amp](https://github.com/shuv-amp) | **[Wallet & User Tools]** *(Activity: 17 review events)*
> This PR fixes a critical bug in the wallet's `importdescriptors` RPC command that caused a crash when importing a descriptor with a very large range. This prevents data loss and improves the reliability of wallet management for users.

**Technical Details:** The `importdescriptors` RPC command allows importing descriptor-based wallets, often with a key range (e.g., `[0-1000]`). A bug caused a crash when the upper bound of such a range was set to the maximum signed 32-bit integer value (`2^31-1`). This likely resulted from an integer overflow or off-by-one error in the underlying range iteration logic. The fix involves correctly handling this edge case, ensuring the range calculation and iteration proceed without triggering a crash.

#### [#34907: wallet, test: make wallet_fast_rescan robust](https://github.com/bitcoin/bitcoin/pull/34907)
**Author:** [@rkrux](https://github.com/rkrux) | **[Maintenance & Tech Debt]** *(Activity: 17 review events)*
> This PR improves the robustness of the `wallet_fast_rescan` test, making it more reliable and less prone to flaky failures. This ensures higher confidence in the wallet's fast rescan functionality during development and release cycles.

**Technical Details:** This PR modifies the existing `wallet_fast_rescan` functional test to address potential flakiness or improve its reliability. This might involve adjusting timing assumptions within the test, improving synchronization mechanisms between test components, or adding more comprehensive assertions to better validate the fast rescan behavior. The changes are strictly confined to the test suite and do not alter production code.

#### [#34729: Reduce log noise](https://github.com/bitcoin/bitcoin/pull/34729)
**Author:** [@ajtowns](https://github.com/ajtowns) | **[Maintenance & Tech Debt]** *(Activity: 15 review events)*
> This PR aims to reduce the volume and verbosity of log messages generated by Bitcoin Core, making logs easier to read and analyze. This helps users and developers quickly identify important events without being overwhelmed by excessive information.

**Technical Details:** This PR implements changes to various logging statements throughout the codebase, adjusting log levels or consolidating redundant messages to decrease the overall volume of output. The goal is to make the logs more focused on actionable or critical information, thereby reducing "noise" and improving the efficiency of log parsing and analysis for users and developers. This is a quality-of-life improvement for node operators and debuggers.

#### [#36151: makeseeds: fix off-by-one in field count check](https://github.com/bitcoin/bitcoin/pull/36151)
**Author:** [@amannx21](https://github.com/amannx21) | **[Maintenance & Tech Debt]** *(Activity: 13 review events)*
> This PR fixes a minor bug in the `makeseeds` tool, which is used to generate initial peer lists for new nodes. This ensures the tool operates correctly and provides accurate seed data for network bootstrapping.

**Technical Details:** The PR addresses an off-by-one error in the field count check within the `makeseeds` utility. This error likely caused incorrect parsing or validation of input data when generating seed nodes. By correcting the logic, the PR ensures that `makeseeds` accurately processes its input, leading to correctly formatted and reliable seed node lists for network bootstrapping.

#### [#36080: p2p: Suspend ping timeout while downloading blocks from a peer](https://github.com/bitcoin/bitcoin/pull/36080)
**Author:** [@mzumsande](https://github.com/mzumsande) | **[Network & Privacy]** *(Activity: 12 review events)*
> This PR improves network reliability by suspending the ping timeout mechanism when a peer is actively sending blocks. This prevents premature disconnections of valuable peers during Initial Block Download (IBD) or chain synchronization.

**Technical Details:** The change modifies the P2P peer management logic to temporarily disable or extend the standard ping timeout for peers from which the node is currently downloading blocks. This addresses scenarios where a peer might be slow to respond to pings due to being busy sending large amounts of block data, leading to unnecessary disconnections. By suspending the timeout, the node avoids disconnecting peers that are actively contributing to chain synchronization, improving IBD robustness and reducing the need for re-establishing connections.

#### [#36337: fuzz: Cover block filter P2P messages](https://github.com/bitcoin/bitcoin/pull/36337)
**Author:** [@maflcko](https://github.com/maflcko) | **[Security & Consensus]** *(Activity: 11 review events)*
> This PR expands the fuzzer coverage to include P2P messages related to compact block filters (BIP 157/158). This helps proactively identify potential vulnerabilities or bugs in the filter processing logic, enhancing the network's robustness.

**Technical Details:** This PR adds new fuzzing targets specifically for the P2P messages used in compact block filters, such as `getcfheaders`, `cfheaders`, `getcfilters`, and `cfilters`. By generating malformed or unexpected inputs for these messages, the fuzzer can uncover edge cases, crashes, or assertion failures in the node's handling of filter data. This proactive testing improves the overall security and stability of the compact block filter implementation, protecting against potential DoS vectors.

#### [#36271: Revert #36057 & document mingw-w64 requirement](https://github.com/bitcoin/bitcoin/pull/36271)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 11 review events)*
> This PR reverts a previous change that caused issues with Windows builds and adds documentation clarifying the specific `mingw-w64` compiler requirement. This ensures that Windows builds remain stable and provides clear guidance for developers.

**Technical Details:** PR #36057 introduced a change that led to build failures on Windows using `mingw-w64` due to compatibility issues. This PR fully reverts that problematic change to restore build stability for Windows users. Additionally, it updates the build documentation to explicitly state the minimum required version or specific configuration for `mingw-w64`, preventing similar build environment issues in the future and streamlining the development process.

#### [#36338: BIP-352: fix P2PKH pubkey extraction from malleated scriptSig](https://github.com/bitcoin/bitcoin/pull/36338)
**Author:** [@theStack](https://github.com/theStack) | **[Security & Consensus]** *(Activity: 10 review events)*
> This PR fixes an issue in the implementation of BIP-352 (Silent Payments) related to extracting P2PKH public keys from malleated scriptSigs. This ensures the correct and secure interpretation of transaction data, preventing potential issues with silent payment address derivation.

**Technical Details:** BIP-352 relies on specific rules for extracting public keys from transaction inputs to derive silent payment addresses. This fix addresses a scenario where a P2PKH `scriptSig` could be malleated (e.g., by adding extra data after the signature and public key), causing incorrect public key extraction. The PR modifies the parsing logic to robustly identify and extract the canonical public key even in the presence of such malleation, ensuring that silent payment derivations remain consistent and secure as intended by the BIP.

#### [#36427: [32.x] More Backports](https://github.com/bitcoin/bitcoin/pull/36427)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR incorporates a collection of previously merged fixes and improvements from the main development branch into the `32.x` release branch. This ensures that the upcoming release benefits from the latest stability enhancements and bug fixes.

**Technical Details:** This is a routine backport PR, cherry-picking multiple commits from the `master` branch into the `32.x` release branch. While the specific contents are not detailed in the title, such PRs typically include critical bug fixes, minor performance improvements, or security patches deemed necessary for the stability and robustness of the upcoming release. The process involves careful selection of commits, conflict resolution, and thorough testing to ensure smooth integration.

#### [#36447: test: Misc fixes for pending validation events races](https://github.com/bitcoin/bitcoin/pull/36447)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR introduces miscellaneous fixes to address race conditions in tests involving pending validation events. These improvements make the test suite more reliable and less prone to intermittent failures.

**Technical Details:** The existing test suite exhibited non-deterministic failures due to race conditions where validation events (e.g., block or transaction processing) were not fully settled before assertions were made. This PR likely introduces synchronization primitives, more robust polling mechanisms, or delays within specific test cases to ensure that all asynchronous validation events have completed and their effects are observable before proceeding with test assertions. This enhances the determinism and stability of the test environment.

#### [#36291: test: add script_tests cases covering interpreter mutants](https://github.com/bitcoin/bitcoin/pull/36291)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR enhances the robustness of Bitcoin's script interpreter by adding new test cases. It helps ensure the interpreter correctly handles various edge cases and potential vulnerabilities.

**Technical Details:** The PR introduces additional `script_tests` vectors specifically designed to cover 'interpreter mutants.' These mutants represent variations or edge cases in script execution logic, aiming to expose subtle bugs or inconsistencies. By expanding the test suite with these cases, the PR strengthens the interpreter's resilience against unexpected inputs and ensures its deterministic behavior across all scenarios.

#### [#36327: test: speed up secp256k1 fixed-base multiplication and Schnorr signing](https://github.com/bitcoin/bitcoin/pull/36327)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR optimizes the execution speed of tests related to `secp256k1` fixed-base multiplication and Schnorr signing. By making these tests run faster, it improves developer efficiency and reduces CI pipeline times.

**Technical Details:** The PR modifies the test suite to improve the performance of benchmarks or unit tests involving `secp256k1` operations, specifically fixed-base multiplication and Schnorr signing. This might involve optimizing test data generation, reducing redundant computations within the test harness, or using more efficient testing methodologies. The goal is to decrease the wall-clock time required to execute these cryptographic tests without altering the correctness or coverage of the tests themselves.

#### [#36435: ci: isolate container test networks](https://github.com/bitcoin/bitcoin/pull/36435)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 9 review events)*
> This PR improves the reliability and efficiency of Bitcoin Core's continuous integration (CI) system. By isolating test networks, it prevents interference between different test runs, leading to more consistent and accurate results.

**Technical Details:** The PR modifies the CI setup to ensure that containerized test networks are fully isolated from each other. This typically involves using distinct network namespaces or dedicated Docker networks for each test job. This isolation prevents resource contention, port conflicts, or unintended interactions between parallel test executions, thereby improving the determinism and reproducibility of CI runs.

#### [#36329: psbt: add new test vectors](https://github.com/bitcoin/bitcoin/pull/36329)
**Author:** [@Sjors](https://github.com/Sjors) | **[Wallet & User Tools]** *(Activity: 8 review events)*
> This PR expands the test suite for Partially Signed Bitcoin Transactions (PSBTs) by adding new test vectors. This ensures the correct and robust handling of various PSBT formats and scenarios, improving the reliability of wallet operations.

**Technical Details:** The PR introduces additional test vectors specifically for the PSBT (Partially Signed Bitcoin Transaction) implementation. These new vectors likely cover edge cases, complex signing scenarios, or newly identified interaction patterns within the PSBT specification. By expanding the test coverage, the PR aims to ensure the PSBT serialization, deserialization, and processing logic remains robust and compliant across a wider range of inputs.

#### [#36262: test: cover orphan reconsideration interruptibility](https://github.com/bitcoin/bitcoin/pull/36262)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR adds tests to ensure that the process of reconsidering orphan transactions can be interrupted efficiently. This improves the responsiveness and resource management of the node, especially under high transaction load.

**Technical Details:** The PR introduces new test cases to verify the interruptibility of the orphan reconsideration process. These tests simulate scenarios where the node needs to halt or pause the reconsideration of orphan transactions, for example, due to new block arrivals or shutdown signals. The goal is to ensure that the process can be gracefully interrupted without deadlocks or resource leaks, improving the node's responsiveness and stability.

#### [#36349: rpc: avoid copying unbroadcast transaction IDs just to count them](https://github.com/bitcoin/bitcoin/pull/36349)
**Author:** [@musaHaruna](https://github.com/musaHaruna) | **[Performance & Optimization]** *(Activity: 7 review events)*
> This PR optimizes RPC calls by preventing unnecessary copying of unbroadcast transaction IDs. It improves efficiency by reducing memory allocations and CPU cycles when simply counting these transactions.

**Technical Details:** Previously, certain RPC calls would create a copy of the entire set of unbroadcast transaction IDs in memory solely to determine their count. This change modifies the RPC handler to directly query the size of the underlying data structure (e.g., a `std::set` or `std::unordered_set`) without creating an intermediate copy. This reduces memory footprint and CPU overhead, especially when dealing with a large number of unbroadcast transactions, leading to better performance for nodes with active mempools.

#### [#36308: test: Set tsan enable_adaptive_delay=1 by default](https://github.com/bitcoin/bitcoin/pull/36308)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR improves the effectiveness of thread sanitizer (TSan) tests in Bitcoin Core. By enabling adaptive delay, it helps detect more concurrency bugs and race conditions during development.

**Technical Details:** The PR sets `enable_adaptive_delay=1` as the default for TSan (ThreadSanitizer) configurations within the test suite. This TSan option dynamically adjusts the delay introduced by the sanitizer, allowing it to better expose subtle timing-dependent race conditions and concurrency bugs that might otherwise be missed. This change enhances the diagnostic capabilities of TSan, leading to more robust multithreaded code.

#### [#36029: cmake: Detect and log MinGW-w64 version when cross-compiling for Windows](https://github.com/bitcoin/bitcoin/pull/36029)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR enhances the CMake build system to detect and log the MinGW-w64 version when cross-compiling for Windows. This provides valuable debugging information and improves the reproducibility of Windows builds.

**Technical Details:** When cross-compiling Bitcoin Core for Windows using MinGW-w64, the specific compiler toolchain version can impact build outcomes. This change modifies the CMake configuration scripts to query and capture the MinGW-w64 version during the configuration phase. This information is then logged, making it easier for developers to diagnose build issues related to toolchain compatibility and ensuring that build environments are consistently documented.

#### [#36471: bitcoin-util: print genesis hash in display order](https://github.com/bitcoin/bitcoin/pull/36471)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Wallet & User Tools]** *(Activity: 5 review events)*
> This PR updates the `bitcoin-util` tool to print the genesis hash in the standard display order. This ensures consistency and readability for users inspecting blockchain data.

**Technical Details:** Previously, `bitcoin-util` might have displayed the genesis hash in an internal byte order, which differs from the standard big-endian hexadecimal representation. This change modifies the utility's output formatting logic to reverse the byte order before hexadecimal conversion, aligning it with common blockchain explorers and user expectations. It involves adjusting the specific print function responsible for hash serialization.

#### [#36462: rpc: fix OpenRPC hex pattern to allow empty strings](https://github.com/bitcoin/bitcoin/pull/36462)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Wallet & User Tools]** *(Activity: 5 review events)*
> This PR fixes the OpenRPC specification for hexadecimal patterns to correctly allow empty strings. This ensures that RPC clients can validate parameters more accurately, especially for optional hex fields.

**Technical Details:** The OpenRPC schema, which describes Bitcoin Core's RPC interface, had a regex pattern for hexadecimal strings that implicitly disallowed empty strings. This fix modifies the regex pattern to explicitly permit zero-length strings, aligning the schema with the actual behavior of certain RPC methods where an empty hex string is a valid input or output. This prevents validation errors in client-side tools that strictly adhere to the OpenRPC specification.

#### [#36467: test: Set socket timeout in interface_http.py](https://github.com/bitcoin/bitcoin/pull/36467)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR adds a socket timeout to HTTP interface tests, preventing them from hanging indefinitely if a connection issue occurs. This makes the test suite more robust and reliable, improving developer productivity.

**Technical Details:** The `interface_http.py` test script interacts with the node's RPC interface over HTTP. Without a socket timeout, network issues or unresponsive nodes could cause these tests to stall indefinitely, consuming CI resources and delaying feedback. This PR introduces a reasonable timeout value for socket operations within these tests, ensuring that they fail gracefully and promptly instead of hanging, thereby improving test suite reliability and efficiency.

#### [#36416: test: use ipaddress in addr_to_hex](https://github.com/bitcoin/bitcoin/pull/36416)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR refactors test infrastructure to use the `ipaddress` module when converting addresses to hexadecimal format. This improves the robustness and correctness of network-related tests.

**Technical Details:** The `addr_to_hex` helper function, used in various network tests, previously might have had custom or less robust IP address parsing logic. By integrating Python's standard `ipaddress` module, the PR leverages a well-tested and comprehensive library for IP address manipulation. This change enhances the accuracy of address serialization within test scenarios, reducing potential edge-case bugs in test setup and validation.

#### [#36152: test: cover the feature-negotiation version boundary in p2p_leak](https://github.com/bitcoin/bitcoin/pull/36152)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR enhances the P2P network tests to cover specific version negotiation scenarios. It ensures that Bitcoin Core's peer-to-peer communication remains robust and secure even at the boundaries of feature negotiation.

**Technical Details:** The PR adds new test cases to the `p2p_leak` test suite, specifically targeting the 'feature-negotiation version boundary.' This involves simulating peer connections where the negotiated protocol version is at critical thresholds or edge cases. The goal is to verify that the P2P layer correctly handles these version transitions and does not leak sensitive information or exhibit unexpected behavior under various negotiation outcomes.

#### [#36418: kernel: document that btck_WriteBytes may receive a null pointer](https://github.com/bitcoin/bitcoin/pull/36418)
**Author:** [@alexanderwiederin](https://github.com/alexanderwiederin) | **[Strategic Initiatives]** *(Activity: 4 review events)*
> This PR adds crucial documentation to the `btck_WriteBytes` function within the new Bitcoin Core kernel, clarifying that it may receive a null pointer. This improves API clarity and helps developers correctly use and interact with the kernel's interfaces.

**Technical Details:** As part of the ongoing 'kernel' project, the `btck_WriteBytes` function's contract regarding null pointer inputs was ambiguous. This change explicitly documents that the function is designed to handle a null pointer for its data argument, likely by treating it as a zero-length write or an error condition depending on the specific implementation. This clarification is vital for external modules or future kernel components interacting with this API, ensuring correct error handling and preventing undefined behavior.

#### [#35835: test: add CONST_SCRIPTCODE failure-path vectors to script_tests.json](https://github.com/bitcoin/bitcoin/pull/35835)
**Author:** [@jeanpablojp](https://github.com/jeanpablojp) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR enhances the script interpreter tests by adding specific cases for `CONST_SCRIPTCODE` failure paths. This improves the robustness of script validation, ensuring that the interpreter correctly handles invalid or malformed script constants.

**Technical Details:** The PR extends `script_tests.json` with new failure-path vectors specifically targeting `CONST_SCRIPTCODE`. These test cases are designed to verify that the script interpreter correctly identifies and rejects scripts that misuse or malform the `CONST_SCRIPTCODE` opcode, leading to predictable failure states. This ensures the interpreter's resilience against invalid script constructions and maintains the integrity of script execution.

#### [#36320: test: refactor: make chain_dir consistent with CreateBaseChainParams](https://github.com/bitcoin/bitcoin/pull/36320)
**Author:** [@ekzyis](https://github.com/ekzyis) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR refactors test code to ensure consistency in how `chain_dir` is handled, aligning it with the `CreateBaseChainParams` function. This improves code readability and maintainability within the test suite.

**Technical Details:** The refactoring modifies test utilities to standardize the naming and usage of the `chain_dir` variable, making it consistent with the `CreateBaseChainParams` function's expectations. This involves updating various test helpers and fixtures to use a unified approach for managing chain data directories, reducing potential confusion and simplifying future test development. The change is purely cosmetic and does not alter test behavior, focusing solely on code cleanliness.

#### [#36128: test: add script_tests cases covering more interpreter mutants](https://github.com/bitcoin/bitcoin/pull/36128)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR expands the `script_tests` suite by adding new test cases designed to cover more "mutants" of the script interpreter. This enhances the robustness and reliability of Bitcoin's scripting engine by ensuring it behaves correctly under a wider range of conditions.

**Technical Details:** The PR introduces additional test vectors to the `script_tests` framework, specifically targeting edge cases and less common execution paths within the Bitcoin Script interpreter. These "mutant" tests are designed to expose potential bugs or inconsistencies that might arise from subtle variations in script execution. By increasing test coverage, the PR helps to ensure the interpreter's correctness and adherence to consensus rules, reducing the risk of unexpected behavior or vulnerabilities.

#### [#36432: wallet: show real fee_reason strings in help](https://github.com/bitcoin/bitcoin/pull/36432)
**Author:** [@jcastros](https://github.com/jcastros) | **[Wallet & User Tools]** *(Activity: 3 review events)*
> This PR updates the wallet's help documentation to display the actual `fee_reason` strings. This provides users with more accurate and helpful information when interpreting transaction fee explanations.

**Technical Details:** Previously, the help text for wallet RPCs or other user interfaces might have presented generic or placeholder descriptions for `fee_reason` fields. This change modifies the documentation generation or string lookup mechanisms to directly embed the precise, internal `fee_reason` strings that the wallet uses. This ensures that the user-facing explanations for why a certain fee was chosen or why a transaction failed to confirm are consistent and technically accurate.

#### [#36392: test: Extract and use sigterm_node in init_fd_overflow_test](https://github.com/bitcoin/bitcoin/pull/36392)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR refactors the test suite by extracting and reusing the `sigterm_node` helper function within `init_fd_overflow_test`. This improves code reuse and maintainability across the test infrastructure.

**Technical Details:** The `init_fd_overflow_test` likely contained duplicated logic for gracefully terminating a Bitcoin Core node using a SIGTERM signal. This PR identifies that common pattern and extracts it into a reusable `sigterm_node` helper function. By calling this new helper, the test reduces redundancy, centralizes node termination logic, and makes the test more concise and easier to understand.

#### [#36426: test: check IBD insufficient work disconnect of outbound peers](https://github.com/bitcoin/bitcoin/pull/36426)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR adds a new test case to verify that Bitcoin Core correctly disconnects outbound peers during Initial Block Download (IBD) if they provide insufficient proof-of-work. This ensures the network logic for IBD peer management is robust.

**Technical Details:** The new test case simulates an IBD scenario where an outbound peer offers a chain with insufficient accumulated work compared to the best known chain. The test asserts that Bitcoin Core's peer management logic correctly identifies this condition and disconnects the misbehaving peer. This validates the implementation of the `CBlockIndex::nChainWork` comparison and the peer disconnection mechanism during IBD, which is critical for preventing sybil attacks or wasting resources on invalid chains.

#### [#35873: test: add a tx_valid vector for CVE-2024-38365](https://github.com/bitcoin/bitcoin/pull/35873)
**Author:** [@jeanpablojp](https://github.com/jeanpablojp) | **[Security & Consensus]** *(Activity: 2 review events)*
> This PR adds a specific test case to validate transaction handling related to a recently identified vulnerability (CVE-2024-38365). This ensures that Bitcoin Core correctly rejects or processes transactions that could exploit this vulnerability, enhancing the network's security.

**Technical Details:** The PR introduces a new `tx_valid` vector into the transaction validation test suite. This vector is specifically crafted to represent an edge case or malformed transaction that could potentially trigger or exploit CVE-2024-38365. By adding this test, the PR ensures that the transaction validation logic correctly identifies and handles such transactions, preventing the vulnerability from being exploited on the network.

#### [#36450: test: Use timeout_factor for drain timeout in check_slow_read_throttle](https://github.com/bitcoin/bitcoin/pull/36450)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR improves the reliability of a specific test by making its timeout configurable via `timeout_factor`, adapting to different testing environments. This prevents flaky test failures and ensures consistent test results.

**Technical Details:** The `check_slow_read_throttle` test likely simulates slow network conditions to verify the node's throttling behavior. The 'drain timeout' refers to the time allowed for data processing. By replacing a hardcoded timeout with `timeout_factor * X`, the test can dynamically adjust its timeout based on the overall test suite's configured `timeout_factor`. This change is crucial for preventing flaky test failures in slower CI environments or on less powerful machines, ensuring more consistent and reliable test outcomes.

#### [#36436: ci: Derive CONTAINER_NAME from the ci config file name](https://github.com/bitcoin/bitcoin/pull/36436)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR streamlines the continuous integration (CI) configuration by automatically generating container names based on their respective CI job file names. This simplifies CI management and reduces potential for naming conflicts.

**Technical Details:** In CI systems, jobs often run within containers that require unique names. Previously, these names might have been manually specified or inconsistently derived. This PR introduces logic to automatically derive the `CONTAINER_NAME` variable from the name of the CI configuration file itself (e.g., `fuzz.yml` -> `fuzz_container`). This convention makes the CI setup more maintainable, less error-prone, and easier to scale by ensuring consistent and unique container naming without manual intervention.

#### [#36448: randomenv: use `KERN_POSIX1` over `KERN_OSREV`](https://github.com/bitcoin/bitcoin/pull/36448)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR updates the `randomenv` utility to use `KERN_POSIX1` instead of `KERN_OSREV` for system information retrieval. This improves the reliability and portability of environment data collection, particularly for randomness generation.

**Technical Details:** The `randomenv` component, responsible for gathering system entropy or environment details, previously relied on `KERN_OSREV` to obtain certain system information. This PR switches to using `KERN_POSIX1`, which is a more standardized and robust kernel identifier for POSIX version information. This change ensures that the environment data collected is more consistent across different operating systems and kernel versions, contributing to the overall reliability of entropy gathering processes.

#### [#36474: ci: Run valgrind --exclude tests again](https://github.com/bitcoin/bitcoin/pull/36474)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR re-enables a `valgrind` memory error detection run in the continuous integration (CI) system, specifically excluding certain tests. This helps catch memory leaks and other issues early in the development cycle, improving code quality and stability.

**Technical Details:** This PR modifies the CI configuration to re-introduce a `valgrind` job, a powerful memory debugging tool, which was previously disabled or misconfigured. It specifically uses the `--exclude` flag to skip tests known to be incompatible or excessively slow with `valgrind`. This allows critical parts of the codebase to be checked for memory errors, uninitialized reads, and other runtime issues without unduly impacting CI runtimes, thereby enhancing code quality.

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#36449: addrman: use uniform sampling inside buckets](https://github.com/bitcoin/bitcoin/pull/36449)
**Author:** [@sipa](https://github.com/sipa) | **[Network & Privacy]** *(Activity: 23 review events this week)*
> This PR improves the address manager's peer selection logic by ensuring more uniform sampling within its buckets. This helps Bitcoin Core discover and connect to a more diverse set of peers, enhancing network decentralization and resilience.

#### [#36427: [32.x] More Backports](https://github.com/bitcoin/bitcoin/pull/36427)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 10 review events this week)*
> This PR incorporates a collection of previously merged fixes and improvements from the main development branch into the `32.x` release branch. This ensures that the upcoming release benefits from the latest stability enhancements and bug fixes.

#### [#36447: test: Misc fixes for pending validation events races](https://github.com/bitcoin/bitcoin/pull/36447)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 10 review events this week)*
> This PR introduces miscellaneous fixes to address race conditions in tests involving pending validation events. These improvements make the test suite more reliable and less prone to intermittent failures.

#### [#36466: policy: make unstructured Taproot annexes standard](https://github.com/bitcoin/bitcoin/pull/36466)
**Author:** [@RobinLinus](https://github.com/RobinLinus) | **[Network & Privacy]** *(Activity: 9 review events this week)*
> This PR makes transactions with unstructured Taproot annexes standard, allowing them to be relayed and included in blocks by default. This improves compatibility and flexibility for future Taproot-based applications.

#### [#36435: ci: isolate container test networks](https://github.com/bitcoin/bitcoin/pull/36435)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 9 review events this week)*
> This PR improves the reliability and efficiency of Bitcoin Core's continuous integration (CI) system. By isolating test networks, it prevents interference between different test runs, leading to more consistent and accurate results.

## 🗓️ Dev Meeting
Summary of the core dev IRC meeting on 2026-10-08 with 22 participants.

- Fuzzing WG: marcofleon reported that high-quality fuzzing is actively occurring.
- Kernel WG: sedited merged #34374, which provides a more flexible, struct-based logging interface for kernel users and removes reliance on the logging module. sedited requested review for #35641 (kernel: Add script evaluation tracer), which alexanderwiederin is using for experimental BIP440 integration in rust-bitcoinkernel/pull/230.
- Benchmarking WG: l0rinc (via sedited) shared #36476, an opt-in pruned assumevalid mode that downloads blocks without witnesses, buffers them in memory, then deserializes and connects them without writing blocks or undo data to disk. Early tests show this could reduce pruned IBD on a 2 GB Pi 4 from ~22 days to under a week.
- QML GUI WG: johnny9dev reported positive feedback from last week's testing. The preview build has been updated, and the project board is being cleaned up. Current focus is on finalizing UX, moving all functions off the GUI thread with regression tests, and finalizing the feature set for upstreaming to bitcoin/bitcoin.
- QA WG: brunoerg announced that mutanthub.space now features a dedicated page for requesting mutation analysis for pull requests.

**Action Items:**
- Developers are requested to review #35641 (kernel: Add script evaluation tracer) by sedited.
- Developers are encouraged to request mutation analysis for their pull requests via the new dedicated page on mutanthub.space.
- johnny9dev's team will focus on finalizing QML GUI UX, migrating functions off the GUI thread with regression tests, and finalizing the feature set for upstreaming.

## 🗣️ Research & Governance
Top active threads across mailing lists and research forums.

### [[bitcoindev] Lichen: L2s In CHannels ENforced on bitcoin](https://gnusha.org/pi/bitcoindev/9dd171c9-e4fa-4b4d-b0d6-33bc46e48b30n@googlegroups.com)
**Source:** Mailing List | **Started By:** {'username': 'Adam Gibson', 'uuid': 'can_adam_gibson'} | **Messages:** 2
> A new proposal aims to enhance Bitcoin's privacy and scalability by enabling trust-minimized Layer 2 solutions with a central hub. This could unlock new applications and more efficient transactions for users.

**Technical Details:** The discussion centers on a proposal for trust-minimized Layer 2s using co-owned 2-of-2 contracts and a non-trusted hub. The current technical debate focuses on the cryptographic primitive Groth16, with concerns raised about its post-quantum vulnerability. Developers are questioning the responsibility of deploying such infrastructure now, necessitating a deeper evaluation of its long-term security and potential alternatives.

### [Disclosure: DoS vulnerabilities fixed in Eclair v0.14.1](https://delvingbitcoin.org/t/disclosure-dos-vulnerabilities-fixed-in-eclair-v0-14-1/2928/2)
**Source:** Delving | **Started By:** {'username': 'erick λ', 'uuid': 'auto_erick'} | **Messages:** 2
> Eclair users should upgrade to v0.14.1 to protect against denial-of-service vulnerabilities. Mobile wallet users, like Phoenix, are already safe as their service providers patched their nodes months ago.

**Technical Details:** Two denial-of-service vulnerabilities, including LNF-2026-0003 related to an `open_channel` race condition, were identified in Eclair's channel opening flow. Eclair users are advised to upgrade their nodes to v0.14.1 or later to mitigate these risks. However, users of mobile wallets that rely on an Eclair node as a Lightning Service Provider (LSP), such as Phoenix, are unaffected. This is because ACINQ, the operator of these LSPs, proactively patched their Eclair nodes several months prior to the public disclosure.

### [Anchoring an SPV light client on another chain: checkpoint trust, retargeting and reorg handling](https://delvingbitcoin.org/t/anchoring-an-spv-light-client-on-another-chain-checkpoint-trust-retargeting-and-reorg-handling/2939/1)
**Source:** Delving | **Started By:** {'username': 'sebastián salazar solano', 'uuid': 'auto_sebasti_n_salazar_solano'} | **Messages:** 2
> A new lending protocol is under review, enabling Bitcoin holders to secure USDC loans while their BTC collateral remains safely on the Bitcoin blockchain. This innovation aims to provide Bitcoin users with liquidity by allowing them to leverage their assets without moving them off-chain.

**Technical Details:** The Writz Protocol, an open-source lending platform, is seeking architectural critique for its Bitcoin-facing components. It proposes a unique cross-chain model where BTC collateral is held natively on the Bitcoin blockchain, while corresponding USDC loans are issued on the Stellar network. The core technical challenge lies in designing robust, secure, and verifiable Bitcoin scripts or mechanisms to manage the collateral's lifecycle, ensuring its state is accurately and trustlessly reflected for loan issuance, repayment, and liquidation processes on Stellar.

### [[bitcoindev] RE BIP 300: 26% censoring attack](https://gnusha.org/pi/bitcoindev/2e554c89-a2a1-4bcf-941c-32f6a8ba9567n@googlegroups.com)
**Source:** Mailing List | **Started By:** {'username': 'ori newman', 'uuid': 'auto_ori_newman'} | **Messages:** 1
> Discussions are underway to address a potential vulnerability in BIP 300 (Drivechains) that could allow a minority attacker to censor sidechain transactions. The aim is to ensure the secure and reliable operation of future Bitcoin features and innovations.

**Technical Details:** A critical vulnerability in BIP 300's bundle scoring mechanism has been identified, where a 26% attacker can indefinitely censor valid drivechain bundles. By consistently sending 'ALARM' messages, the attacker can reduce a bundle's score, preventing its inclusion. The core architectural debate revolves around the security implications of the current scoring and alarm system, necessitating a re-evaluation of how bundle validity and inclusion are determined to prevent censorship.

### [Re: [bitcoindev] Flame: confidential transactions with Bitcoin
 proof-of-burn consensus](https://gnusha.org/pi/bitcoindev/9517998B-3019-4ADE-B566-F30D42F33C37@gmail.com)
**Source:** Mailing List | **Started By:** {'username': 'Oleg Andreev OOO', 'uuid': 'auto_oleg_andreev_ooo'} | **Messages:** 1
> Developers are discussing a new way to expand Bitcoin's utility by creating 'SideCoins' on other networks. This involves a one-way conversion of Bitcoin, potentially unlocking new features and applications for users.

**Technical Details:** The 'Flame' project is evaluating a 'one-way peg' mechanism, proposed by Ruben, for converting BTC into a 'SideCoin.' This architecture entails 'burning' BTC on the main chain to issue an equivalent amount of SideCoin, making the transfer irreversible. The current discussion, led by Oleg Andreev, is likely weighing the architectural implications, security models, and the 'pros' (e.g., simplicity, finality) and implied 'cons' (e.g., lack of reversibility, trust assumptions) of this specific pegging design compared to other sidechain solutions. Further debate is needed to fully articulate the trade-offs and determine the optimal design for Flame.

## 🏆 Contributor Shoutouts
### 🎉 First-Time Merges
Welcome to the codebase: [@amannx21](https://github.com/amannx21), [@jcastros](https://github.com/jcastros)

### ✍️ Top Authors
The most active PR authors this week: [@maflcko](https://github.com/maflcko), [@ViniciusCestarii](https://github.com/ViniciusCestarii), [@fanquake](https://github.com/fanquake), [@brunoerg](https://github.com/brunoerg), [@jeanpablojp](https://github.com/jeanpablojp)

### 🕵️ Top Reviewers
Providing critical review and testing: [@sedited](https://github.com/sedited), [@maflcko](https://github.com/maflcko), [@w0xlt](https://github.com/w0xlt), [@willcl-ark](https://github.com/willcl-ark), [@l0rinc](https://github.com/l0rinc)
