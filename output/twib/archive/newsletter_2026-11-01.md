# 📰 This Week in Bitcoin (2026-10-26 to 2026-11-01)

## 📌 The TL;DR
- Continued focus on long-term protocol resilience and advanced on-chain capabilities:** Discussions around mitigating quantum-vulnerable UTXOs highlight a proactive approach to future security threats, while the BIP draft for Co-signer Spending Policies and the extension of Silent Payments to multiparty wallets indicate significant progress towards more robust and private on-chain contract designs. The allowance of non-standard scripts on testnets further supports experimentation for future protocol evolution.
- Sustained investment in code quality, testing, and development infrastructure:** A substantial volume of merged PRs focused on fuzzing, comprehensive testing, CI improvements, and extensive refactoring demonstrates a continuous, high-priority effort to enhance the codebase's robustness, maintainability, and reliability.

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

#### [#29843: policy: Allow non-standard scripts with -acceptnonstdtxn=1 (test nets only)](https://github.com/bitcoin/bitcoin/pull/29843)
**Author:** [@ajtowns](https://github.com/ajtowns) | **[Network & Privacy]** *(Activity: 41 review events)*
> This PR introduces a new configuration option, `-acceptnonstdtxn=1`, specifically for test networks. It allows nodes on testnets to accept transactions with non-standard scripts, facilitating broader testing and experimentation with novel script types.

**Technical Details:** The implementation modifies transaction policy logic to conditionally bypass standardness checks when the `-acceptnonstdtxn=1` flag is enabled. `CheckInputsScriptStandard` and related validation functions will incorporate a check for this new flag, allowing previously rejected non-standard scripts to pass validation on test networks. This enables developers to test experimental script constructions without requiring full network consensus for standardness. It affects how a node interacts with the network regarding non-standard transactions.

#### [#36124: http: Make `HTTPRequest` update state internally](https://github.com/bitcoin/bitcoin/pull/36124)
**Author:** [@hodlinator](https://github.com/hodlinator) | **[Maintenance & Tech Debt]** *(Activity: 20 review events)*
> This PR refines the HTTP request handling by allowing the `HTTPRequest` object to manage its internal state. This improves the clarity and encapsulation of the HTTP server's operation.

**Technical Details:** Previously, the `HTTPRequest` object's state updates might have been managed externally. This change modifies the `HTTPRequest` class to internally handle its state transitions, likely through methods that directly manipulate its member variables. This reduces external dependencies and simplifies the logic where `HTTPRequest` instances are used, making the HTTP server more robust.

#### [#36098: fuzz: add corpus reachability checks](https://github.com/bitcoin/bitcoin/pull/36098)
**Author:** [@HowHsu](https://github.com/HowHsu) | **[Maintenance & Tech Debt]** *(Activity: 20 review events)*
> This PR enhances Bitcoin Core's automated testing by adding checks to ensure that all parts of the test data are actually used. This helps developers create more effective tests and find bugs more efficiently.

**Technical Details:** This PR introduces corpus reachability checks to the fuzzing infrastructure. It verifies that all inputs within the fuzzer's corpus actually exercise the code paths they are intended to cover. This helps identify redundant or ineffective corpus entries, improving the efficiency and coverage of fuzz testing.

#### [#35714: validation: return block-file flush errors](https://github.com/bitcoin/bitcoin/pull/35714)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Security & Consensus]** *(Activity: 17 review events)*
> This PR enhances the validation component by ensuring that all database write operations cease immediately following a flush failure. This critical change prevents potential data corruption and safeguards the integrity of the blockchain state on disk.

**Technical Details:** Database flush operations are crucial for persisting the chainstate to disk reliably. A failure during a flush (e.g., due to disk full or I/O error) leaves the on-disk state potentially corrupted or inconsistent. This PR introduces a mechanism to detect such flush failures and, upon detection, transitions the database writer into a 'failed' state. In this state, subsequent attempts to write data are actively prevented or cause a controlled shutdown, ensuring that no further inconsistent data is written. This protects the integrity of the node's blockchain data against severe forms of corruption.

#### [#1937: tests: silentpayments: cover rejection of invalid keypair alongside a valid one](https://github.com/bitcoin-core/secp256k1/pull/1937)
**Author:** [@Yudis-bit](https://github.com/Yudis-bit) | **[Security & Consensus]** *(Activity: 13 review events)*
> This PR adds a new test case to the `secp256k1` library, specifically for Silent Payments. It ensures that the library correctly rejects invalid keypairs even when they are presented alongside valid ones, improving the robustness and security of Silent Payments implementations.

**Technical Details:** The test case extends the existing Silent Payments test suite within `secp256k1`. It constructs a scenario where a transaction or message contains a mix of valid and intentionally invalid keypairs for Silent Payments. The test then asserts that the library's validation logic correctly identifies and rejects the invalid components, preventing potential vulnerabilities or unexpected behavior in applications using Silent Payments.

#### [#36606: test, bench: construct inputs/outputs declaratively in context-dependent cases](https://github.com/bitcoin/bitcoin/pull/36606)
**Author:** [@alexanderwiederin](https://github.com/alexanderwiederin) | **[Maintenance & Tech Debt]** *(Activity: 13 review events)*
> This PR improves the clarity and maintainability of Bitcoin Core's tests and benchmarks by using a more structured way to define transaction inputs and outputs. This makes it easier for developers to write and understand complex test scenarios.

**Technical Details:** This PR introduces a declarative style for constructing transaction inputs and outputs within tests and benchmarks, particularly for context-dependent scenarios. Instead of imperative step-by-step construction, it uses a more descriptive approach, enhancing readability and reducing boilerplate code for common patterns in test setup.

#### [#36667: net: enforce timeout interval for paused send peers](https://github.com/bitcoin/bitcoin/pull/36667)
**Author:** [@darosior](https://github.com/darosior) | **[Security & Consensus]** *(Activity: 11 review events)*
> This PR enhances network reliability by enforcing timeout intervals for peers that have paused sending data. This prevents stalled connections from consuming resources indefinitely, improving the overall health and responsiveness of the Bitcoin network.

**Technical Details:** The change introduces logic within the peer-to-peer networking stack to monitor and disconnect peers that have entered a 'paused send' state for an extended period. This involves tracking the last activity timestamp for such peers and applying a configurable timeout, preventing resource exhaustion from unresponsive peers and improving network resilience.

#### [#36665: sock: align exception monitoring between poll() and select() backends](https://github.com/bitcoin/bitcoin/pull/36665)
**Author:** [@darosior](https://github.com/darosior) | **[Network & Privacy]** *(Activity: 11 review events)*
> This PR aligns how network socket exceptions are monitored across different operating system backends. This ensures consistent and reliable error handling for network operations, making Bitcoin Core more robust regardless of the underlying system.

**Technical Details:** The change involves harmonizing the exception handling logic for network sockets, specifically ensuring that both `poll()` and `select()` system call backends correctly detect and report exceptional conditions. This typically means ensuring that the `POLLPRI` flag for `poll()` and the `exceptfds` set for `select()` are consistently checked and processed, leading to uniform error propagation and connection management.

#### [#36594: net: make orphan reconsideration more granular](https://github.com/bitcoin/bitcoin/pull/36594)
**Author:** [@darosior](https://github.com/darosior) | **[Performance & Optimization]** *(Activity: 10 review events)*
> This PR improves how Bitcoin Core handles orphaned transactions, making the reconsideration process more efficient. It helps the node process transactions more quickly when blocks arrive out of order or with missing parents.

**Technical Details:** Previously, orphan reconsideration was a global process. This PR refactors `MaybeReconsiderOrphans` to operate on a per-transaction basis, allowing individual orphans to be re-evaluated for inclusion in the mempool without re-scanning all orphans. It introduces a mechanism to only re-evaluate orphans whose parents have recently become available, significantly reducing CPU overhead during orphan processing.

#### [#36011: btcsignals: destroy callbacks on disconnect](https://github.com/bitcoin/bitcoin/pull/36011)
**Author:** [@ryanofsky](https://github.com/ryanofsky) | **[Maintenance & Tech Debt]** *(Activity: 10 review events)*
> This PR ensures that signal callbacks are properly destroyed when a connection is disconnected, preventing potential memory leaks and improving resource management. This contributes to a more stable and efficient node operation over time.

**Technical Details:** The `btcsignals` system facilitates inter-component communication. This PR addresses a scenario where, upon a component or connection disconnecting, associated signal callbacks might not have been properly unregistered or deallocated. By explicitly destroying these callbacks on disconnect, it prevents dangling pointers or accumulated memory usage, ensuring resources are correctly released and avoiding potential crashes or memory exhaustion.

#### [#36611: test: consolidate mempool constants](https://github.com/bitcoin/bitcoin/pull/36611)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 9 review events)*
> This PR refactors the test suite by consolidating various mempool-related constants into a single, centralized location. This improves test maintainability and readability by reducing duplication and making constant values easier to manage.

**Technical Details:** The PR identifies multiple instances where the same numerical or string constants related to mempool behavior (e.g., transaction sizes, fee rates, policy limits) are defined across different test files. It then moves these definitions into a shared header or utility file accessible by all relevant tests, reducing boilerplate, ensuring consistency, and simplifying future updates to these constant values.

#### [#36529: test: measure rpcwaittimeout floor with monotonic time](https://github.com/bitcoin/bitcoin/pull/36529)
**Author:** [@nervana21](https://github.com/nervana21) | **[Maintenance & Tech Debt]** *(Activity: 9 review events)*
> This PR improves the accuracy of RPC wait timeout measurements in tests by using monotonic time. This ensures more reliable and consistent testing of RPC behavior, especially under varying system loads.

**Technical Details:** The PR modifies existing test infrastructure, specifically tests related to `rpcwaittimeout`. It switches the timing mechanism from a potentially system-clock-dependent method to one utilizing a monotonic clock source (e.g., `std::chrono::steady_clock` or similar platform-specific API). This change prevents issues where system clock adjustments could skew timeout measurements, providing more robust and reproducible test results for RPC call behavior.

#### [#36588: refactor: Enable more tidy bugprone checks](https://github.com/bitcoin/bitcoin/pull/36588)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR enhances code quality and helps prevent potential bugs by enabling additional `clang-tidy` bug-prone checks. This improves the maintainability and reliability of the Bitcoin Core codebase.

**Technical Details:** The change involves updating the project's `clang-tidy` configuration, likely in `.clang-tidy` or a similar build system file. It enables a set of `bugprone-*` checks, which identify common programming errors and anti-patterns that could lead to undefined behavior or subtle bugs. This helps developers catch issues earlier in the development cycle and enforces stricter code quality standards across the project.

#### [#36666: [29.x] Finalise 29.5](https://github.com/bitcoin/bitcoin/pull/36666)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR finalizes the 29.5 release branch, preparing it for official release. It ensures all necessary changes are integrated and the release is ready for deployment, providing users with the latest stable version of Bitcoin Core.

**Technical Details:** This typically involves merging release-critical branches, updating versioning information, and ensuring all release notes and build artifacts are correctly generated. It's a final synchronization and tagging step before the official release announcement, ensuring consistency across the codebase for the specified version.

#### [#36669: refactor: store positions as a 64 bits integer in flatfiles](https://github.com/bitcoin/bitcoin/pull/36669)
**Author:** [@darosior](https://github.com/darosior) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR refactors how data positions are stored in flatfiles, switching to 64-bit integers. This change improves the system's ability to handle larger data files, ensuring future scalability and robustness for Bitcoin Core's data storage.

**Technical Details:** The refactoring involves modifying the serialization format for positions within flatfiles (e.g., `blk*.dat` files) from a smaller integer type to a `uint64_t`. This change impacts the `CAutoFile` and related serialization logic, ensuring that offsets and sizes can correctly address files larger than 4GB, which is a limitation of 32-bit integers.

#### [#36658: [32.x] Finalise 32.1](https://github.com/bitcoin/bitcoin/pull/36658)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR finalizes the 32.1 release branch, marking it ready for official release. It represents a significant milestone in the development cycle, preparing the next stable version for users.

**Technical Details:** This PR typically involves a series of administrative and build-related tasks. It might include updating version numbers, generating release notes, ensuring all intended backports are merged, and preparing the build system for release artifacts. The 'Finalise' step ensures that the release branch is stable, complete, and ready for tagging and distribution, signifying the culmination of a release cycle for a specific major version.

#### [#36701: ci: Disable tests on ARM32 in GHA yaml](https://github.com/bitcoin/bitcoin/pull/36701)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 7 review events)*
> This PR disables certain tests on ARM32 architecture within the GitHub Actions CI configuration. This addresses known build failures or performance issues specific to ARM32, allowing the CI to pass for other architectures while ARM32 issues are investigated.

**Technical Details:** The PR modifies the GitHub Actions workflow YAML file to conditionally skip or disable specific test suites when the build environment is detected as ARM32. This is a temporary measure to prevent CI pipelines from failing entirely due to known, architecture-specific problems, enabling continuous integration for more widely used platforms while the ARM32-specific issues are debugged or resolved separately.

#### [#35818: bloom: avoid undefined sizing calculations](https://github.com/bitcoin/bitcoin/pull/35818)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Network & Privacy]** *(Activity: 5 review events)*
> This PR fixes a potential bug in the Bloom filter implementation by preventing undefined behavior in sizing calculations. This ensures the correct and reliable operation of Bloom filters, which are used for lightweight client filtering.

**Technical Details:** The PR addresses specific arithmetic operations within the Bloom filter sizing logic that could lead to undefined behavior (e.g., integer overflow) under certain input conditions. It likely introduces bounds checks, uses safer arithmetic types, or refactors the calculation to guarantee well-defined results across all valid inputs, improving the robustness and predictability of Bloom filter construction and usage within the P2P layer.

#### [#36071: refactor: fuzz: remove cost_of_change from coin-grinder fuzz target](https://github.com/bitcoin/bitcoin/pull/36071)
**Author:** [@yancyribbens](https://github.com/yancyribbens) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR refines a testing tool used by developers to find bugs, making it more focused and efficient. It removes an unnecessary calculation from a specific fuzzing target, improving the quality of automated testing.

**Technical Details:** The `coin-grinder` fuzz target was incorrectly calculating `cost_of_change`, which is specific to `fundrawtransaction` and not relevant for `CreateTransaction` in the context of the fuzzer. This PR removes the `cost_of_change` calculation from the fuzzer's transaction creation logic, simplifying the fuzzer and ensuring it focuses on relevant aspects of coin selection without introducing irrelevant complexities.

#### [#36663: test: Use single node in mempool_reorg.py](https://github.com/bitcoin/bitcoin/pull/36663)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR simplifies a specific test case for mempool behavior during blockchain reorganizations, making the test more robust and easier to understand. It ensures the test accurately verifies how transactions are handled when the blockchain changes.

**Technical Details:** The `mempool_reorg.py` functional test previously used two nodes, but only one was actively used for the relevant mempool reorg logic. This PR modifies the test to use a single node, removing unnecessary complexity and potential for confusion, while maintaining the test's coverage of mempool reorg scenarios.

#### [#36714: net_processing: remove m_wtxid_relay_peers](https://github.com/bitcoin/bitcoin/pull/36714)
**Author:** [@fanquake](https://github.com/fanquake) | **[Performance & Optimization]** *(Activity: 4 review events)*
> This PR removes the `m_wtxid_relay_peers` data structure from the `net_processing` module, streamlining the code and simplifying transaction relay logic. This is part of ongoing efforts to refine and optimize how transactions are propagated across the network.

**Technical Details:** The `m_wtxid_relay_peers` member was previously used to track peers supporting wtxid-based transaction relay. Its removal suggests that this specific tracking mechanism is no longer necessary, possibly due to a change in how wtxid relay is managed (e.g., it's now assumed for all modern peers, or a more efficient mechanism is used). This refactoring reduces memory footprint and simplifies the `net_processing` codebase by removing associated overhead.

#### [#36676: cli: respect -rpcclienttimeout even when sending](https://github.com/bitcoin/bitcoin/pull/36676)
**Author:** [@darosior](https://github.com/darosior) | **[Wallet & User Tools]** *(Activity: 4 review events)*
> This PR ensures that the command-line interface (CLI) for Bitcoin Core properly applies timeout settings to all RPC communications, including when sending data. This prevents commands from hanging indefinitely during network issues.

**Technical Details:** Previously, the `-rpcclienttimeout` setting was only applied to the receive phase of RPC requests. This PR extends its application to cover the send phase as well, ensuring that the entire RPC request-response cycle respects the configured timeout. This prevents CLI commands from blocking indefinitely if the connection hangs during the request transmission.

#### [#36703: test: Sync blocks in test_witness_block in p2p_segwit.py](https://github.com/bitcoin/bitcoin/pull/36703)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR improves a P2P SegWit test by adding explicit synchronization for blocks within the `test_witness_block` function. This ensures that test assertions are made only after all relevant blocks have been fully processed by the node, making the test more reliable.

**Technical Details:** The `test_witness_block` in `p2p_segwit.py` involves sending SegWit blocks to a test node and then asserting its state. This PR introduces `sync_blocks` or similar synchronization primitives to ensure that the test harness waits for the node to fully process and integrate the sent blocks into its chain state before proceeding with assertions. This prevents race conditions and flaky test failures that could occur if assertions were made on an outdated or partially processed node state.

#### [#36682: refactor: Use std::erase and std::erase_if](https://github.com/bitcoin/bitcoin/pull/36682)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR updates the codebase to use modern C++ features for removing elements from containers, making the code cleaner and more efficient. It's a standard library improvement that simplifies common programming patterns.

**Technical Details:** This PR replaces manual `erase-remove` idiom loops with the C++20 `std::erase` and `std::erase_if` algorithms where applicable. This simplifies the code, improves readability, and leverages optimized standard library implementations for removing elements from `std::vector` and `std::string` containers.

#### [#36678: doc: adapt release notes template to security disclosure policy update](https://github.com/bitcoin/bitcoin/pull/36678)
**Author:** [@darosior](https://github.com/darosior) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR updates the release notes template to align with recent changes in the project's security disclosure policy. It ensures that future release notes accurately reflect the process for handling security-related information.

**Technical Details:** The change involves modifying the `doc/release-notes.md` template. Specifically, it updates the sections pertaining to security disclosures, likely adding or rephrasing guidance on how to document security fixes or advisories in a standardized manner. This ensures consistency and clarity in communicating security-sensitive information to users and developers, improving the project's release management practices.

#### [#36664: [30.x] Finalise 30.4](https://github.com/bitcoin/bitcoin/pull/36664)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR finalizes the 30.4 release branch, preparing it for official release. It ensures all necessary updates and fixes are included and the branch is stable for distribution.

**Technical Details:** Similar to other 'Finalise' PRs, this involves administrative and build-related tasks for the 30.4 release. It typically includes updating version strings, consolidating release notes, verifying that all targeted backports have been integrated, and performing final checks to ensure the branch is stable and ready for tagging and public release. This marks the completion of the development cycle for this specific point release.

#### [#36662: [31.x] Backports](https://github.com/bitcoin/bitcoin/pull/36662)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR consolidates a set of backported changes into the 31.x release branch. These backports bring important fixes and minor improvements from newer development branches to enhance the stability and functionality of the 31.x series.

**Technical Details:** This PR aggregates multiple individual commits or smaller PRs that have been cherry-picked or rebased from a more recent development branch (e.g., `master` or `HEAD`) into the `31.x` release branch. These backports typically address bugs, security fixes, or minor enhancements deemed important for the stability and maintenance of the older release line, ensuring that critical improvements are propagated without waiting for a full major release.

#### [#36661: [31.x] Finalise 31.2](https://github.com/bitcoin/bitcoin/pull/36661)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR finalizes the 31.2 release branch, preparing it for official release. It ensures all necessary updates and fixes are included and the branch is stable for distribution.

**Technical Details:** Similar to other 'Finalise' PRs, this involves administrative and build-related tasks for the 31.2 release. It typically includes updating version strings, consolidating release notes, verifying that all targeted backports have been integrated, and performing final checks to ensure the branch is stable and ready for tagging and public release. This marks the completion of the development cycle for this specific point release.

#### [#36610: test: add `plyvel` to deps table](https://github.com/bitcoin/bitcoin/pull/36610)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR updates the project's dependency table to include `plyvel`, a Python binding for LevelDB. This ensures that testing environments can correctly install and utilize necessary components for database-related tests, improving the reliability of the test suite.

**Technical Details:** The change involves modifying the `depends/packages` or similar dependency management configuration to list `plyvel` as a required package for certain test environments, likely Python-based functional tests that interact with LevelDB. This ensures that automated CI/CD pipelines and developer setups can correctly resolve and install this dependency, preventing test failures due to missing libraries.

#### [#970: Remove legacy BIP70 merchant name from tx details window](https://github.com/bitcoin-core/gui/pull/970)
**Author:** [@maflcko](https://github.com/maflcko) | **[Wallet & User Tools]** *(Activity: 3 review events)*
> This PR removes the display of legacy BIP70 merchant names from the transaction details window in the Bitcoin Core GUI. This streamlines the user interface by removing outdated information, as BIP70 is no longer widely used or supported.

**Technical Details:** The change involves modifying the GUI's transaction details view to no longer query or display the `merchant_name` field associated with BIP70 payment requests. This includes removing the corresponding UI elements (e.g., labels, text fields) and the underlying logic that would attempt to retrieve this information, simplifying the codebase and reducing reliance on deprecated protocols.

#### [#36687: test: wait for the node to finish the last block in p2p_ping_ibd](https://github.com/bitcoin/bitcoin/pull/36687)
**Author:** [@instagibbs](https://github.com/instagibbs) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR enhances a P2P test by ensuring the node fully processes the last block during Initial Block Download (IBD) before the test concludes. This makes the test more robust and accurately reflects real-world node synchronization behavior.

**Technical Details:** The `p2p_ping_ibd` test simulates a node undergoing IBD. This PR adds a synchronization mechanism, such as waiting for a specific event or using a `wait_until` condition, to confirm that the node has completely finished processing the final block received during IBD. This prevents race conditions where the test might assert conditions before the node's internal state has fully updated, leading to flaky test results.

#### [#36684: test: check AddToBlockIndex keeps first-seen header on equal work](https://github.com/bitcoin/bitcoin/pull/36684)
**Author:** [@brunoerg](https://github.com/brunoerg) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR adds a new test to confirm that Bitcoin Core correctly handles situations where two different block headers have the same amount of work. It verifies that the node consistently prefers the first header it encountered, which is crucial for network stability.

**Technical Details:** This PR introduces a functional test to specifically verify the behavior of `AddToBlockIndex` when presented with two block headers that represent chains of equal total work. The test confirms that the node correctly retains the header that was first seen, adhering to the tie-breaking rule for chain selection.

#### [#36683: doc: fix `v32.1` release notes archive](https://github.com/bitcoin/bitcoin/pull/36683)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR corrects an error in the archived release notes for a previous Bitcoin Core version, ensuring that historical documentation is accurate.

**Technical Details:** This PR addresses a typo or incorrect path in the `v32.1` release notes archive, specifically fixing the link or reference to the release notes file. It ensures that the documentation system correctly points to and displays the historical release notes for that version.

#### [#36674: Update leveldb subtree to latest master](https://github.com/bitcoin/bitcoin/pull/36674)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR updates the bundled LevelDB library to its latest master version. This ensures Bitcoin Core benefits from the most recent bug fixes, performance improvements, and security enhancements in its underlying database component.

**Technical Details:** This PR involves updating the `src/leveldb` subtree within the Bitcoin Core repository. This is typically done by fetching the latest commits from the upstream LevelDB repository's `master` branch and merging them into the local subtree. This process brings in all upstream changes, including bug fixes, performance optimizations, and potentially new features or API adjustments, which are then integrated and tested within Bitcoin Core's build system.

#### [#1978: ci: Run ctime_tests in the arm64 Debian job](https://github.com/bitcoin-core/secp256k1/pull/1978)
**Author:** [@fametrano](https://github.com/fametrano) | **[Maintenance & Tech Debt]** *(Activity: 2 review events)*
> This PR updates the Continuous Integration (CI) configuration for the `secp256k1` library to include `ctime_tests` in the ARM64 Debian job. This ensures that critical cryptographic timing tests are run on an additional architecture, improving the overall test coverage and reliability of the library.

**Technical Details:** The change modifies the `.gitlab-ci.yml` or similar CI configuration file to add `ctime_tests` to the list of test suites executed within the ARM64 Debian build environment. This involves updating the test script or command for that specific job, ensuring that the timing-related cryptographic tests are compiled and run, thereby verifying performance and side-channel resistance on the ARM64 architecture.

#### [#36672: [30.x] Backport ci: inline runner selection](https://github.com/bitcoin/bitcoin/pull/36672)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR backports a continuous integration (CI) improvement to the 30.x branch, enabling more flexible and efficient runner selection. This enhances the automated testing infrastructure for this older release line.

**Technical Details:** This PR integrates the 'inline runner selection' CI enhancement, previously applied to other branches, into the 30.x release branch. This involves modifying the CI workflow definitions (e.g., `.github/workflows/*.yml`) to allow specifying or dynamically selecting CI runners directly within job configurations. This improves the efficiency and control over CI resource allocation for the 30.x branch, ensuring its tests run optimally.

#### [#36671: [31.x] Backport ci: inline runner selection](https://github.com/bitcoin/bitcoin/pull/36671)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR backports a continuous integration (CI) improvement to the 31.x branch, allowing for more efficient and flexible runner selection. This streamlines the automated testing process for this release line.

**Technical Details:** This PR integrates a CI enhancement, likely from a more recent development branch, into the 31.x release branch. The 'inline runner selection' likely refers to a mechanism within the CI configuration (e.g., GitHub Actions workflows) that allows specifying or dynamically choosing CI runners directly within the job definition, rather than relying on global or predefined labels. This improves the granularity and efficiency of CI resource allocation for the 31.x branch.

#### [#36604: [29.x] Backports](https://github.com/bitcoin/bitcoin/pull/36604)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR incorporates a collection of backported changes into the 29.x release branch. These backports ensure that the release includes important bug fixes, minor improvements, or security updates from the main development branch, enhancing its stability and functionality.

**Technical Details:** This PR aggregates several commits from the `master` or `main` branch and applies them to the `29.x` release branch. This process typically involves cherry-picking specific commits, resolving any merge conflicts, and verifying that the integrated changes do not introduce regressions. The goal is to bring critical updates to a stable release branch without waiting for the next major version.

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#36688: net: receive TCP urgent data inline](https://github.com/bitcoin/bitcoin/pull/36688)
**Author:** [@darosior](https://github.com/darosior) | **[Network & Privacy]** *(Activity: 31 review events this week)*
> This PR changes how Bitcoin Core handles a specific type of network data, ensuring that all incoming information is processed in a consistent order. This prevents potential issues with out-of-order data processing from peers.

#### [#36628: net: reimplement private broadcast as jobs isolated from the node](https://github.com/bitcoin/bitcoin/pull/36628)
**Author:** [@instagibbs](https://github.com/instagibbs) | **[Network & Privacy]** *(Activity: 22 review events this week)*
> This PR rearchitects how private transaction broadcasts are handled, isolating them as separate jobs from the main node's operation. This improves the reliability and efficiency of private transaction relay, particularly for wallet-initiated transactions.

#### [#36673: [DRAFT] ci: Monitor Windows signing certificate expiry](https://github.com/bitcoin/bitcoin/pull/36673)
**Author:** [@willcl-ark](https://github.com/willcl-ark) | **[Maintenance & Tech Debt]** *(Activity: 13 review events this week)*
> This PR introduces a CI job to monitor the expiry of the Windows signing certificate. This proactive check helps prevent issues with signed binaries by providing early warnings before the certificate becomes invalid.

#### [#36667: net: enforce timeout interval for paused send peers](https://github.com/bitcoin/bitcoin/pull/36667)
**Author:** [@darosior](https://github.com/darosior) | **[Security & Consensus]** *(Activity: 11 review events this week)*
> This PR enhances network reliability by enforcing timeout intervals for peers that have paused sending data. This prevents stalled connections from consuming resources indefinitely, improving the overall health and responsiveness of the Bitcoin network.

#### [#36665: sock: align exception monitoring between poll() and select() backends](https://github.com/bitcoin/bitcoin/pull/36665)
**Author:** [@darosior](https://github.com/darosior) | **[Network & Privacy]** *(Activity: 11 review events this week)*
> This PR aligns how network socket exceptions are monitored across different operating system backends. This ensures consistent and reliable error handling for network operations, making Bitcoin Core more robust regardless of the underlying system.

## 🗓️ Dev Meeting
Summary of the core dev IRC meeting on 2026-10-29 with 14 participants.

- Fuzzing WG: No update provided by eugenesiegel.
- QML GUI WG: johnny9dev reported integration test fixtures merged. Focus is on multi-wallet management improvements and threading, preparing for staging branch build-up.
- QA WG: brunoerg uploaded mutation testing results for `src/node/blockstorage.cpp` to mutanthub.space, highlighting interesting cases.
- Release Process Efficiency: stickies-v noted the rapid TCP OOM vulnerability release (2026-10-23 to 2026-10-28) and proposed reviewing release notes only in the initial PR, not during release, potentially with LLM-lintable rules. vasild supported this proposal.
- Merge Policy Documentation: yancy inquired about the Bitcoin Core merge policy. stickies-v stated it is not explicitly documented due to difficulty in quantifying non-gameable criteria. vasild referenced `CONTRIBUTING.md`'s "Decision Making" section.

**Action Items:**
- Review mutation testing results for `src/node/blockstorage.cpp` on mutanthub.space (brunoerg).
- Discuss proposals for streamlining the release note review process (stickies-v).

## 🗣️ Research & Governance
Top active threads across mailing lists and research forums.

### [Thoughts on a network policy for quantum-vulnerable UTXOs (long-exposure quantum attacks)](https://delvingbitcoin.org/t/thoughts-on-a-network-policy-for-quantum-vulnerable-utxos-long-exposure-quantum-attacks/2111/3)
**Source:** Delving | **Started By:** {'username': 'Sho', 'uuid': 'auto_sho'} | **Messages:** 3
> The community is starting discussions on how Bitcoin will proactively protect users' funds against potential future threats from quantum computers, ensuring long-term security and reliability for everyone.

**Technical Details:** A foundational discussion has begun to establish a policy framework for handling UTXOs that could become vulnerable to quantum attacks after a hypothetical 'Q-day'. The initial focus is on categorizing potential approaches to mitigate risk, likely involving protocol-level considerations or consensus changes to address at-risk funds and prevent large-scale theft, aiming to pre-emptively define how the network should react to this future threat.

### [Silent Payments for Multiparty Wallets](https://delvingbitcoin.org/t/silent-payments-for-multiparty-wallets/2960/2)
**Source:** Delving | **Started By:** {'username': 'Oleks', 'uuid': 'auto_olkurbatov'} | **Messages:** 3
> We're making strides to enable groups of people to use Silent Payments securely, bringing enhanced privacy to shared Bitcoin wallets and multi-party transactions. This work ensures that the benefits of private payments can be reliably extended to collaborative spending.

**Technical Details:** The discussion centers on a new protocol to securely compose BIP-352 Silent Payments with multiparty signing schemes like FROST and MuSig2, addressing the initial lack of a security proof. Recent feedback clarified cryptographic notation regarding commitment aggregation (e.g., `c_i` vs `hat c_i = g * c_i`) and the proper application of accumulated parity, referencing BIP-327 and BIP-445. The architectural debate is on establishing a robust, shared interface that ensures cryptographic soundness when integrating diverse multiparty schemes, requiring careful construction of individual signer contributions and their aggregation.

### [We made the bitcoin-dev mailing list readable: 15 years, 24,699 messages](https://delvingbitcoin.org/t/we-made-the-bitcoin-dev-mailing-list-readable-15-years-24-699-messages/2985/1)
**Source:** Delving | **Started By:** {'username': 'LearnBitcoin.com', 'uuid': 'auto_learnbitcoin_com'} | **Messages:** 3
> A new, user-friendly archive of the bitcoin-dev mailing list is now available, making it much easier to browse and understand the historical discussions that shape Bitcoin's development. It offers a more organized and readable way to explore past technical debates and proposals.

**Technical Details:** A new web-based mirror for the bitcoin-dev mailing list archive has been launched, providing enhanced readability and navigation compared to existing public-inbox solutions. It features daily refreshes, single-page thread views with folded quotes, and stable permalinks by Message-ID, along with three distinct indexes. Architecturally, the content is organized by year and month, accessible via a 'Years' navigation entry that lists all years since 2011 with thread counts, facilitating structured historical browsing.

### [[BIP Draft] Co-signer Spending Policies](https://delvingbitcoin.org/t/bip-draft-co-signer-spending-policies/2955/3)
**Source:** Delving | **Started By:** {'username': 'nonAnon', 'uuid': 'auto_nonanon'} | **Messages:** 3
> Efforts are underway to make multi-signature transactions smarter and more reliable by standardizing how co-signers enforce rules. This will enable more advanced Bitcoin transactions that automatically follow predefined conditions, enhancing security and predictability.

**Technical Details:** The discussion focuses on standardizing co-signer policies to enable covenant-like behavior, where co-signers sign only when a specific predicate holds. A critical feedback point highlights that the current `statement-v0` draft signs event ID, outcome, and timestamp, but fails to specify if the outcome is final or mutable. This omission could lead to co-signers acting on a preliminary or subsequently invalidated outcome. The policy standardization must therefore explicitly address outcome finality to ensure co-signers operate on definitive data, preventing potential transaction invalidations.

### [Where should wallets explain the differences between on-chain Bitcoin and Lightning?](https://delvingbitcoin.org/t/where-should-wallets-explain-the-differences-between-on-chain-bitcoin-and-lightning/2922/2)
**Source:** Delving | **Started By:** {'username': 'Anzus', 'uuid': 'auto_anzus'} | **Messages:** 2
> Efforts are underway to simplify Bitcoin transactions for new users by clearly labeling payment types (on-chain vs. Lightning) at the confirmation stage, preventing common errors and improving user experience.

**Technical Details:** A recurring usability issue has been identified where users fail to distinguish between on-chain Bitcoin and Lightning Network payments, leading to confusion. The proposed solution focuses on a UI enhancement: explicitly labeling the payment type on the transaction confirmation screen. This approach is supported by observations from support teams, indicating that most user confusion occurs at the point of confirmation, suggesting that proactive labeling at this critical stage is more effective than relying on users to understand the distinction beforehand.

## 🏆 Contributor Shoutouts
### ✍️ Top Authors
The most active PR authors this week: [@fanquake](https://github.com/fanquake), [@darosior](https://github.com/darosior), [@maflcko](https://github.com/maflcko), [@l0rinc](https://github.com/l0rinc), [@HowHsu](https://github.com/HowHsu)

### 🕵️ Top Reviewers
Providing critical review and testing: [@maflcko](https://github.com/maflcko), [@fanquake](https://github.com/fanquake), [@sedited](https://github.com/sedited), [@hebasto](https://github.com/hebasto), [@Sjors](https://github.com/Sjors)
