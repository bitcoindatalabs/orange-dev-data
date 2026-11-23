# 📰 This Week in Bitcoin (2026-11-16 to 2026-11-22)

## 📌 The TL;DR
- A significant technical discussion centered on the potential of zero-knowledge proofs, specifically STARKs, for verifying Bitcoin's UTXO set, indicating a forward-looking research direction for more efficient and trust-minimized state verification.
- Wallet development focused on enhancing security and user experience, including the deprecation of the `encryptwallet` RPC for existing wallets, refinements to RBF behavior to prevent locktime backdating, and foundational testing for future privacy features like BIP352 (Silent Payments).

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

#### [#36040: Wallet: Don't backdate locktime rbf](https://github.com/bitcoin/bitcoin/pull/36040)
**Author:** [@Bicaru20](https://github.com/Bicaru20) | **[Wallet & User Tools]** *(Activity: 38 review events)*
> This PR prevents the wallet from backdating the locktime of Replace-by-Fee (RBF) transactions. This ensures that RBF transactions adhere to expected locktime behavior, preventing potential issues with transaction validity or unexpected delays.

**Technical Details:** The wallet logic for creating or modifying RBF transactions is updated to explicitly disallow setting a locktime that is earlier than the original transaction's locktime or the current block height/time. This prevents a scenario where an RBF replacement could inadvertently become invalid or have its confirmation delayed due to an invalid locktime, ensuring that RBF replacements always progress forward in time.

#### [#36387: wallet: rpc: Deprecate `encryptwallet` RPC for encrypting existing wallets.](https://github.com/bitcoin/bitcoin/pull/36387)
**Author:** [@davidgumberg](https://github.com/davidgumberg) | **[Wallet & User Tools]** *(Activity: 21 review events)*
> This PR deprecates the `encryptwallet` RPC for wallets that are already encrypted. This prevents accidental re-encryption attempts and guides users towards appropriate wallet management tools.

**Technical Details:** The `encryptwallet` RPC previously allowed re-encrypting an already encrypted wallet, which is an invalid operation. This change modifies the RPC to return an error when called on an already encrypted wallet, preventing potential misuse. Users are now directed to use `walletpassphrasechange` for password updates.

#### [#36451: refactor: Use NotNull for CreateNewBlock and pimpls](https://github.com/bitcoin/bitcoin/pull/36451)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 19 review events)*
> This refactoring PR adopts the NotNull pointer wrapper for CreateNewBlock and pointer-to-implementation (pimpl) idioms. It enforces stricter null-safety guarantees at the type system level.

**Technical Details:** The changes introduce the NotNull smart pointer wrapper into block assembly pathways, specifically targeting CreateNewBlock and selected pimpl patterns. By leveraging the type system to statically guarantee non-null invariants, the code reduces defensive runtime assertions and invalid pointer dereference risks. This improves overall codebase robustness and readability without altering consensus-critical block generation logic.

#### [#36890: Update secp256k1 subtree to latest master](https://github.com/bitcoin/bitcoin/pull/36890)
**Author:** [@hebasto](https://github.com/hebasto) | **[Performance & Optimization]** *(Activity: 17 review events)*
> This PR updates the embedded `secp256k1` library to its latest master version. This brings in the latest cryptographic optimizations, bug fixes, and security improvements from the underlying elliptic curve cryptography library.

**Technical Details:** Bitcoin Core uses `libsecp256k1` for signature verification and generation. This PR updates the git subtree or submodule reference to the most recent commit on the `secp256k1` master branch. This ensures Bitcoin Core benefits from any performance enhancements, security patches, or new features implemented in the upstream library.

#### [#36586: coins: warn of low disk space before chainstate compaction](https://github.com/bitcoin/bitcoin/pull/36586)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Performance & Optimization]** *(Activity: 15 review events)*
> This PR adds a warning mechanism to alert users about low disk space before initiating chainstate compaction. This helps prevent critical disk space issues during a resource-intensive operation, improving node stability and user experience.

**Technical Details:** Before starting the chainstate compaction process, the node now performs a check on the available disk space. If the free space falls below a predefined threshold, a warning message is logged and potentially displayed to the user. This proactive check allows users to address disk space constraints before the compaction process potentially fails or causes the system to run out of space.

#### [#36501: refactor : Reorder CBlockIndex members to save 8 bytes](https://github.com/bitcoin/bitcoin/pull/36501)
**Author:** [@bartoli](https://github.com/bartoli) | **[Performance & Optimization]** *(Activity: 14 review events)*
> This PR optimizes memory usage by reordering members within the `CBlockIndex` structure. This small change contributes to a more efficient use of memory, especially for nodes storing a large number of block indexes.

**Technical Details:** The `CBlockIndex` structure contains various members of different sizes. By reordering these members according to their size, the compiler can pack them more efficiently, reducing padding bytes. This specific change saves 8 bytes per `CBlockIndex` instance, leading to cumulative memory savings across the blockchain index.

#### [#36087: util: Add and use AssertUnreachable](https://github.com/bitcoin/bitcoin/pull/36087)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 14 review events)*
> This PR introduces a new utility function, `AssertUnreachable`, to clearly mark code paths that should never be reached. This improves code clarity and helps developers identify logical errors during development and testing.

**Technical Details:** `AssertUnreachable` is a macro or function that, when hit, indicates a severe logical error in the program's flow. It typically triggers an assertion failure or crash in debug builds, documenting and enforcing invariants. Its primary purpose is to make unexpected code execution immediately apparent to developers.

#### [#36342: wallet: reject recipient amounts above MAX_MONEY](https://github.com/bitcoin/bitcoin/pull/36342)
**Author:** [@Bruce039](https://github.com/Bruce039) | **[Wallet & User Tools]** *(Activity: 13 review events)*
> This PR enhances wallet security by ensuring it rejects transaction recipient amounts exceeding the `MAX_MONEY` limit. This prevents users from accidentally creating invalid transactions that would be rejected by the network.

**Technical Details:** The wallet's transaction creation or recipient validation logic is updated to include a check against the `MAX_MONEY` constant (21 million BTC). If a user attempts to specify an output amount greater than this value, the wallet will now explicitly reject the transaction before broadcasting, providing immediate feedback and preventing the creation of consensus-invalid transactions.

#### [#36835: test: add BIP352 scanning to the functional test framework](https://github.com/bitcoin/bitcoin/pull/36835)
**Author:** [@rustaceanrob](https://github.com/rustaceanrob) | **[Maintenance & Tech Debt]** *(Activity: 13 review events)*
> This PR integrates testing for BIP352 (Silent Payments) scanning into Bitcoin Core's functional test framework. This addition is crucial for validating the correct implementation and behavior of Silent Payments, a privacy-enhancing feature.

**Technical Details:** The change introduces new test cases and utilities within the functional test framework to simulate and verify the scanning process for BIP352 Silent Payments. This involves creating test transactions conforming to BIP352, generating blocks, and then asserting that the wallet or node correctly identifies and processes these payments, ensuring the privacy feature functions as intended.

#### [#36894: net_processing: set fDisconnect instead of calling DisconnectNode](https://github.com/bitcoin/bitcoin/pull/36894)
**Author:** [@Crypt-iQ](https://github.com/Crypt-iQ) | **[Maintenance & Tech Debt]** *(Activity: 12 review events)*
> This PR refactors how nodes are disconnected in `net_processing` by setting a flag instead of directly calling `DisconnectNode`. This streamlines the disconnection process, making it more consistent and potentially preventing race conditions or unexpected behavior.

**Technical Details:** Instead of directly invoking `DisconnectNode`, which might have immediate side effects or require specific locking, this PR introduces a `fDisconnect` flag on the peer object. The actual disconnection logic is then handled asynchronously or in a centralized loop that checks this flag, ensuring a more controlled and robust shutdown of the connection within the `net_processing` component.

#### [#36637: torcontrol: send -torpassword hex-encoded to avoid escaping bugs](https://github.com/bitcoin/bitcoin/pull/36637)
**Author:** [@jpk68](https://github.com/jpk68) | **[Network & Privacy]** *(Activity: 9 review events)*
> This PR improves the robustness of Tor control communication by hex-encoding the Tor password. This prevents potential escaping bugs that could arise from special characters in the password, ensuring reliable Tor connectivity.

**Technical Details:** The `torcontrol` module's implementation for sending the `-torpassword` argument to the Tor daemon is modified. Instead of sending the password as a plain string, it is now hex-encoded. This encoding ensures that any special characters within the password are safely transmitted without being misinterpreted by shell or command-line parsing mechanisms, thereby preventing connection failures or authentication issues.

#### [#36864: rpc: deprecate iswatchonly field of getaddressinfo](https://github.com/bitcoin/bitcoin/pull/36864)
**Author:** [@w0xlt](https://github.com/w0xlt) | **[Wallet & User Tools]** *(Activity: 7 review events)*
> This PR deprecates the `iswatchonly` field in the `getaddressinfo` RPC, signaling that this field will be removed in future versions. This change streamlines the RPC interface by removing redundant or less useful information, encouraging users to adopt more robust methods for wallet queries.

**Technical Details:** This PR modifies the `getaddressinfo` RPC handler to mark the `iswatchonly` field as deprecated. This typically involves adding a deprecation warning to the RPC output or documentation, and potentially updating internal data structures or logic to phase out reliance on this field. The change aims to simplify the RPC interface by removing a field that might be redundant with other address properties or less relevant in modern wallet architectures, guiding developers towards more precise query methods and reducing API surface area.

#### [#36889: cmake: Switch `include_directories` -> `target_include_directories`](https://github.com/bitcoin/bitcoin/pull/36889)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR updates the build system configuration to use `target_include_directories` instead of `include_directories` in CMake. This modernizes the build system, improving its robustness and making include paths more precise and encapsulated for specific targets.

**Technical Details:** In CMake, `include_directories` adds include paths globally, potentially leading to unintended dependencies. `target_include_directories` associates include paths directly with specific targets (executables, libraries), ensuring only necessary paths are exposed. This change improves modularity and prevents potential build issues from overly broad include paths.

#### [#36875: scripted-diff: Drop `IWYU pragma: keep` from build config includes](https://github.com/bitcoin/bitcoin/pull/36875)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This scripted-diff removes outdated Include-What-You-Use (IWYU) pragmas from build configuration includes. It streamlines code annotations and keeps header dependency tracking clean.

**Technical Details:** Using a scripted-diff, this PR strips out obsolete `IWYU pragma: keep` directives from build-related configuration include blocks across the codebase. These pragmas are no longer required by the current static analysis tooling configuration. Consequently, it reduces visual clutter in header blocks without modifying actual compile-time dependencies or binary outputs.

#### [#36742: lint: shellcheck files with shell shebang](https://github.com/bitcoin/bitcoin/pull/36742)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR integrates `shellcheck` into the linting process for shell scripts. This improves code quality and reliability by automatically identifying common issues and potential bugs in shell scripts.

**Technical Details:** `shellcheck` is a static analysis tool for shell scripts. This PR adds a step to the continuous integration (CI) or local linting scripts to run `shellcheck` against all files identified as shell scripts (e.g., by their shebang `#!/bin/bash`). This ensures that shell scripts adhere to best practices and are free from common pitfalls.

#### [#36868: test: remove unused nodes and restarts from wallet tests](https://github.com/bitcoin/bitcoin/pull/36868)
**Author:** [@w0xlt](https://github.com/w0xlt) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR refactors wallet functional tests by removing unnecessary test nodes and restarts. This optimization makes the test suite run faster and more efficiently, improving developer productivity and reducing CI resource usage.

**Technical Details:** This PR analyzes existing wallet functional tests to identify and eliminate redundant `add_nodes()` calls and `stop_node()`/`start_node()` sequences. By optimizing the test setup and teardown, it reduces the overhead associated with node initialization and state resets, leading to faster test execution. This cleanup improves the overall efficiency of the test suite without altering test coverage or behavior, making the CI pipeline more performant.

#### [#36869: refactor, memusage: Make fields of STL helper structs public](https://github.com/bitcoin/bitcoin/pull/36869)
**Author:** [@hebasto](https://github.com/hebasto) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR modifies STL helper structs in the memusage module to make their fields public. This change improves code ergonomics and accessibility for memory estimation utilities.

**Technical Details:** The pull request refactors specific Standard Template Library (STL) helper structures within memusage.h/cpp by changing internal field visibility to public. This eliminates unnecessary getter and setter boilerplates, allowing direct member access across internal memory calculation routines. It has no runtime impact on consensus or node behavior, acting purely as a structural code clean-up.

#### [#36924: test: Speed up interface_ipc_mining.py and fix large timeout-factor bug](https://github.com/bitcoin/bitcoin/pull/36924)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR improves the efficiency of a specific interface test and corrects a bug related to its timeout factor. These changes make the test suite run faster and more reliably, improving developer productivity.

**Technical Details:** The PR targets `interface_ipc_mining.py`, optimizing its execution by likely reducing redundant operations or improving test setup/teardown. Additionally, it addresses a bug where a timeout factor was incorrectly applied or calculated, potentially leading to flaky or excessively long test runs. The fix ensures timeouts are appropriate for the test's expected duration.

#### [#36704: doc: fix docs and enable `-Wdocumentation-pedantic`](https://github.com/bitcoin/bitcoin/pull/36704)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR improves the quality and accuracy of Bitcoin Core's documentation by fixing existing issues and enabling a stricter documentation warning flag. This ensures that developer-facing documentation is clear, consistent, and up-to-date.

**Technical Details:** The changes involve reviewing and correcting various documentation strings, comments, or external documentation files. Crucially, it enables the `-Wdocumentation-pedantic` compiler flag, which enforces stricter rules for documentation comments (e.g., Doxygen style). This flag will now catch potential documentation errors or inconsistencies during compilation, preventing future regressions.

#### [#36893: [30.x] Backport #35878 and prep for v30.5](https://github.com/bitcoin/bitcoin/pull/36893)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR backports a specific change, #35878, to the `30.x` release branch and prepares it for the `v30.5` point release. This ensures that the `v30.5` release includes a critical update and is ready for distribution.

**Technical Details:** This PR specifically cherry-picks or applies the changes from PR #35878 onto the `30.x` release branch. Additionally, it includes any necessary preparatory steps for the `v30.5` point release, which might involve updating version strings, release notes, or other metadata. This ensures the `30.x` branch is stable and correctly configured for the upcoming maintenance release, facilitating a smooth release process.

#### [#36862: test: use long timeout for event waits in interface_ipc_mining](https://github.com/bitcoin/bitcoin/pull/36862)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This test framework update increases timeouts for event waits in the interface_ipc_mining integration test. It prevents false-positive test failures on heavily loaded systems.

**Technical Details:** The test harness configuration for interface_ipc_mining.py is updated to utilize a longer timeout threshold when awaiting asynchronous event loops over IPC boundaries. Slower CI runner nodes frequently triggered race conditions or timeout exceptions under high resource contention. Adjusting these thresholds stabilizes the test suite without altering any production node codebase logic.

#### [#36848: test: drop flaky "server too slow" check from interface_http.py](https://github.com/bitcoin/bitcoin/pull/36848)
**Author:** [@pinheadmz](https://github.com/pinheadmz) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This test improvement drops a flaky "server too slow" check from interface_http.py. It eliminates intermittent CI test failures caused by noisy runner environments.

**Technical Details:** The PR removes a brittle response-time assertion (`server too slow`) within the HTTP functional test suite. Operating system scheduling jitter and background load spikes on CI infrastructure often caused benign execution delays to breach strict timing boundaries. Removing this check hardens the test suite against environmental noise while maintaining core functional assertions.

#### [#36867: test: remove legacy wallet leftovers from wallet functional tests](https://github.com/bitcoin/bitcoin/pull/36867)
**Author:** [@w0xlt](https://github.com/w0xlt) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR cleans up the functional tests for the wallet by removing outdated elements related to legacy wallet features. This improves the test suite's clarity and maintainability, ensuring tests accurately reflect current wallet functionality.

**Technical Details:** This PR refactors existing wallet functional tests by identifying and removing test cases or setup logic specifically designed for legacy wallet features that are no longer relevant. It likely involves deleting or modifying test helper functions, `setup()` methods, or specific assertions that targeted deprecated wallet behaviors. The change streamlines the test suite, reduces technical debt, and ensures test coverage remains focused on current wallet implementations.

#### [#36727: [32.x] Backports](https://github.com/bitcoin/bitcoin/pull/36727)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR incorporates a collection of previously approved changes from the main development branch into the `32.x` release branch. This ensures that the upcoming `32.x` release benefits from recent bug fixes, minor improvements, and updated features.

**Technical Details:** This PR bundles multiple commits, cherry-picked or rebased, from the `master` or a more recent development branch onto the `32.x` release branch. The specific changes are not detailed in the title but typically include bug fixes, minor performance enhancements, or non-disruptive feature updates. This process ensures that the `32.x` branch remains up-to-date with critical improvements before its official release, maintaining stability and functionality.

#### [#36914: test: simplify wallet_basic and rpc_getblockfilter tests](https://github.com/bitcoin/bitcoin/pull/36914)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR simplifies the functional tests for basic wallet operations and the `getblockfilter` RPC. By making these tests more concise and easier to understand, it enhances the maintainability and reliability of Bitcoin Core's test suite.

**Technical Details:** This PR refactors the `wallet_basic` and `rpc_getblockfilter` functional tests to reduce complexity and improve readability. This likely involves consolidating redundant test steps, utilizing more efficient test helpers, or restructuring test cases to be more modular. The goal is to achieve the same test coverage with less code, making future test development and debugging more straightforward and efficient.

#### [#947: Update RPC console wallet when the active wallet changes](https://github.com/bitcoin-core/gui/pull/947)
**Author:** [@kwsantiago](https://github.com/kwsantiago) | **[Wallet & User Tools]** *(Activity: 3 review events)*
> This GUI pull request ensures the RPC console wallet context updates correctly whenever the active wallet changes. It fixes synchronization bugs between the UI and backend wallet state.

**Technical Details:** The Qt-based GUI codebase is updated to listen for active wallet context modification signals and propagate them directly to the RPC console model. Previously, switching the active wallet via the UI selector did not consistently refresh the execution context of commands evaluated within the RPC console tab. This patch binds the console's evaluation scope to the primary GUI wallet selection notifier.

#### [#36927: [32.x] build: remove *dev* errors from dev-mode](https://github.com/bitcoin/bitcoin/pull/36927)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR cleans up the build process by removing 'dev' related errors that appear in development mode. This improves the developer experience by reducing noise and focusing error messages on actual issues.

**Technical Details:** In development mode, certain checks or warnings might be enabled that are specific to development practices. This PR likely identifies and suppresses or reclassifies messages that are not true errors but rather development-specific diagnostics, ensuring that developers only see actionable error messages. This involves adjusting compiler flags or build script logic for dev builds.

#### [#36901: [31.x] Backports](https://github.com/bitcoin/bitcoin/pull/36901)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR integrates a set of approved changes from the main development branch into the `31.x` release branch. This ensures that the upcoming `31.x` release includes important bug fixes, minor enhancements, and updated functionality.

**Technical Details:** This PR aggregates several commits, either cherry-picked or rebased, from the `master` or a more recent development branch onto the `31.x` release branch. The specific content of these backports is not specified but generally comprises bug fixes, small performance improvements, or non-breaking feature updates. This procedure maintains the `31.x` branch's currency with essential developments prior to its official release, enhancing its robustness.

#### [#36892: [31.x] Backport #35878 and prep for v31.3](https://github.com/bitcoin/bitcoin/pull/36892)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR backports a specific change, #35878, to the `31.x` release branch and prepares it for the `v31.3` point release. This ensures that the `v31.3` release includes a critical update and is ready for distribution.

**Technical Details:** This PR specifically cherry-picks or applies the changes from PR #35878 onto the `31.x` release branch. Additionally, it includes any necessary preparatory steps for the `v31.3` point release, which might involve updating version strings, release notes, or other metadata. This ensures the `31.x` branch is stable and correctly configured for the upcoming maintenance release, facilitating a smooth release process.

#### [#36888: test: construct `coinselection_tests` output declaratively](https://github.com/bitcoin/bitcoin/pull/36888)
**Author:** [@yuvicc](https://github.com/yuvicc) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR refactors the `coinselection_tests` to use a more declarative style for constructing test outputs. This makes the tests easier to read, understand, and maintain, improving the quality and reliability of the coin selection logic.

**Technical Details:** Previously, test outputs in `coinselection_tests` might have been constructed imperatively. This change likely introduces helper functions or data structures that allow defining the desired test output state in a single, concise declaration. This reduces boilerplate and improves the clarity of test scenarios for coin selection.

#### [#36903: doc: archive release notes](https://github.com/bitcoin/bitcoin/pull/36903)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR archives older release notes, moving them to a dedicated historical section. This helps keep the documentation organized and ensures that current release notes are easily accessible, while still preserving historical records.

**Technical Details:** This PR involves relocating existing release note files (e.g., `release-notes/release-notes-X.Y.Z.md`) from their primary location to an archive directory (e.g., `doc/release-notes/archive/`). This is a pure documentation management task, updating file paths and potentially internal links within the documentation system to reflect the new structure. No code changes are involved, only documentation file organization.

#### [#36912: doc: relax clang-format loop and template declaration rules](https://github.com/bitcoin/bitcoin/pull/36912)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR adjusts the `clang-format` configuration to relax certain rules for loop and template declarations. This change aims to improve code readability and maintainability by allowing more natural formatting in specific common code patterns.

**Technical Details:** The PR modifies the `.clang-format` configuration file, specifically targeting rules related to the formatting of `for`, `while`, `do-while` loops and template declarations. By relaxing these rules, it allows `clang-format` to apply less rigid formatting in these contexts, potentially aligning better with common C++ idioms and developer preferences without sacrificing overall code consistency.

#### [#36902: [30.x] More Backports](https://github.com/bitcoin/bitcoin/pull/36902)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR incorporates additional approved changes from the main development branch into the `30.x` release branch. This ensures that the `30.x` release continues to benefit from recent bug fixes and minor improvements, enhancing its stability and functionality.

**Technical Details:** This PR bundles further commits, cherry-picked or rebased, from the `master` or a more recent development branch onto the `30.x` release branch. These backports typically consist of bug fixes, minor performance enhancements, or non-disruptive feature updates. This ongoing process ensures the `30.x` branch remains current with important improvements for its maintenance cycle, contributing to its long-term reliability.

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#36147: ci: add native freeBSD ci job](https://github.com/bitcoin/bitcoin/pull/36147)
**Author:** [@willcl-ark](https://github.com/willcl-ark) | **[Maintenance & Tech Debt]** *(Activity: 25 review events this week)*
> This PR adds a new Continuous Integration job specifically for FreeBSD. This expands the testing matrix, ensuring Bitcoin Core remains compatible and stable on another important operating system.

#### [#36890: Update secp256k1 subtree to latest master](https://github.com/bitcoin/bitcoin/pull/36890)
**Author:** [@hebasto](https://github.com/hebasto) | **[Performance & Optimization]** *(Activity: 17 review events this week)*
> This PR updates the embedded `secp256k1` library to its latest master version. This brings in the latest cryptographic optimizations, bug fixes, and security improvements from the underlying elliptic curve cryptography library.

#### [#36895: Keep witness stacks in serialized form in CScriptWitness](https://github.com/bitcoin/bitcoin/pull/36895)
**Author:** [@sipa](https://github.com/sipa) | **[Performance & Optimization]** *(Activity: 13 review events this week)*
> This PR optimizes the storage of witness stacks within `CScriptWitness` by keeping them in their serialized form. This reduces redundant serialization/deserialization operations, leading to performance improvements and potentially lower memory overhead.

#### [#36894: net_processing: set fDisconnect instead of calling DisconnectNode](https://github.com/bitcoin/bitcoin/pull/36894)
**Author:** [@Crypt-iQ](https://github.com/Crypt-iQ) | **[Maintenance & Tech Debt]** *(Activity: 12 review events this week)*
> This PR refactors how nodes are disconnected in `net_processing` by setting a flag instead of directly calling `DisconnectNode`. This streamlines the disconnection process, making it more consistent and potentially preventing race conditions or unexpected behavior.

#### [#36896: test: use Jacobian coordinates in `FastGEMul`](https://github.com/bitcoin/bitcoin/pull/36896)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 11 review events this week)*
> This PR updates a test to use Jacobian coordinates for cryptographic operations. It ensures the correctness and efficiency of underlying elliptic curve arithmetic implementations within Bitcoin Core.

## 🗓️ Dev Meeting
Summary of the core dev IRC meeting on 2026-11-19 with 15 participants.

- Fuzzing WG: No update reported by eugenesiegel and marcofleon.
- Kernel WG: sedited noted several open pull requests, including #36692, focused on improving tests.
- QML GUI WG: johnny9dev reported 248 of 329 issues resolved, with 7 pre-PR fixes. Cleanup and deslop are in progress. Desktop notifications are the final feature before staging.
- QA WG: No update reported by brunoerg.
- Address Relay: b10c investigated address-refresh spam expiration over the weekend, identifying potential fixes.

## 🗣️ Research & Governance
Top active threads across mailing lists and research forums.

### [A STARK proof of Bitcoin's UTXO set at block 972,500, with circuits proven in Lean](https://delvingbitcoin.org/t/a-stark-proof-of-bitcoins-utxo-set-at-block-972-500-with-circuits-proven-in-lean/3070/4)
**Source:** Delving | **Started By:** {'username': 'Henri', 'uuid': 'auto_henri'} | **Messages:** 3
> Developers are exploring innovative cryptographic proofs (STARKs) to make verifying Bitcoin's entire history faster and more efficient, aiming to enhance accessibility and scalability for all users.

**Technical Details:** A STARK prover for Bitcoin consensus is under development, demonstrating the ability to prove Bitcoin's state. However, a significant performance bottleneck has been identified: 70.7 seconds of a 72-second proof generation are spent reading a 9.4 GB snapshot from disk to recompute its hash. The current debate focuses on optimizing this by re-evaluating the necessary structure of this hash, with suggestions to explore alternatives like a Merkle tree ordered by `txid/vout` or an MMR to drastically reduce I/O and computation overhead.

### [We made the bitcoin-dev mailing list readable: 15 years, 24,699 messages](https://delvingbitcoin.org/t/we-made-the-bitcoin-dev-mailing-list-readable-15-years-24-699-messages/2985/5)
**Source:** Delving | **Started By:** {'username': 'LearnBitcoin.com', 'uuid': 'auto_learnbitcoin_com'} | **Messages:** 2
> Developers have created a reliable, readable mirror of the bitcoin-dev mailing list archive. This ensures the history and discussions of Bitcoin development remain permanently accessible to everyone.

**Technical Details:** The discussion highlights the fragility of relying on single hosting providers, as demonstrated by the Linux Foundation temporarily taking down its mailing list archive. The newly introduced mirror provides distinct advantages over public-inbox by featuring single-page threads with folded quotes, stable permalinks tied directly to Message-IDs, and three dedicated indexes. This setup guarantees long-term archival resilience against dead links and disappearing repositories. Going forward, developers must ensure continuous syncing and redundancy to maintain these archives independently.

### [Open Question on a hypothetical minor "slow-sliding MTP" attack introduced by BIP 54](https://delvingbitcoin.org/t/open-question-on-a-hypothetical-minor-slow-sliding-mtp-attack-introduced-by-bip-54/3101/1)
**Source:** Delving | **Started By:** {'username': 'Antoine Riard', 'uuid': 'can_antoine_riard'} | **Messages:** 2
> Developers are reviewing BIP54 and analyzing how Median Time Past (MTP) is used in forward blocks. The goal is to ensure these proposals maintain Bitcoin's high security standards.

**Technical Details:** The discussion centers on potential subtle security implications introduced by BIP54, specifically regarding the usage of Median Time Past (MTP) by forward blocks. Reviewers are scrutinizing timing assumptions, block validation rules, and potential edge cases in the proposed specification. Careful analysis of the timestamp logic is required to prevent unintended consensus vulnerabilities or manipulation vectors. Further peer review and edge-case testing of the MTP mechanism within the proposed framework are needed before proceeding.

### [Re: [bitcoindev] RFC: Two years of BIP Editing, time for some new faces?](https://gnusha.org/pi/bitcoindev/62bb6c9b-d3a4-4b5e-97e7-60a2c8c91a2a@murch.one)
**Source:** Mailing List | **Started By:** {'username': 'Mark Erhardt', 'uuid': 'can_mark_erhardt'} | **Messages:** 1
> To ensure new Bitcoin improvements are reviewed and published efficiently, the community is discussing adding more editors to the BIP team, benefiting everyone by speeding up proposal processing.

**Technical Details:** Murch has initiated a discussion regarding the current capacity constraints of the BIP Editor team, noting a recent inability to keep pace with incoming Bitcoin Improvement Proposals (BIPs). The core proposal is to expand the team to alleviate bottlenecks in the review and publication process, which necessitates defining selection criteria and a formal onboarding process for new editors.

### [Re: [bitcoindev] Quantum Landmines and Vulnerable Coin Auctions](https://gnusha.org/pi/bitcoindev/ffd99327-f633-4e2e-bc54-cc1389ffebccn@googlegroups.com)
**Source:** Mailing List | **Started By:** {'username': 'Cory Fields', 'uuid': 'can_cory_fields'} | **Messages:** 1
> Bitcoin Core developers are beginning to explore a new, conceptually interesting idea. The specific benefits and details are yet to be outlined as the discussion is in its earliest stages.

**Technical Details:** The current thread, featuring initial input from 'conduition' and a response from Cory Fields, indicates the very early conceptualization of an unspecified 'neat idea'. No technical specifics, architectural considerations, or concrete action items have been presented, suggesting the discussion is pre-proposal. Further context is needed to identify the technical problem being addressed or the proposed solution's details.

## 🏆 Contributor Shoutouts
### 🎉 First-Time Merges
Welcome to the codebase: [@bartoli](https://github.com/bartoli)

### ✍️ Top Authors
The most active PR authors this week: [@fanquake](https://github.com/fanquake), [@maflcko](https://github.com/maflcko), [@hebasto](https://github.com/hebasto), [@w0xlt](https://github.com/w0xlt), [@Crypt-iQ](https://github.com/Crypt-iQ)

### 🕵️ Top Reviewers
Providing critical review and testing: [@maflcko](https://github.com/maflcko), [@hebasto](https://github.com/hebasto), [@fanquake](https://github.com/fanquake), [@fjahr](https://github.com/fjahr), [@l0rinc](https://github.com/l0rinc)
