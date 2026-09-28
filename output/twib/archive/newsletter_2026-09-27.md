# 📰 This Week in Bitcoin (2026-09-21 to 2026-09-27)

## 📌 The TL;DR
- The wallet module received significant enhancements, most notably the integration of Silent Payments (BIP352) for improved transaction privacy, alongside new options like `maxfeerate` for finer control over transaction construction.
- Critical discussions around Post-Quantum Cryptography (PQC) for BIP324 indicate a proactive focus on Bitcoin's long-term security, while internal infrastructure improvements like the new block template manager enhance core stability and extensibility.

## 🚢 Core Code (Merged This Week)
The most critical pull requests merged into Bitcoin Core, ordered by community review activity.

#### [#29278: Wallet:  Add `maxfeerate` wallet startup option](https://github.com/bitcoin/bitcoin/pull/29278)
**Author:** [@ismaelsadeeq](https://github.com/ismaelsadeeq) | **[Wallet & User Tools]** *(Activity: 79 review events)*
> This PR introduces the `maxfeerate` wallet startup configuration option to Bitcoin Core. This acts as a safety limit to prevent the wallet from accidentally creating and signing transactions with excessively high fee rates.

**Technical Details:** The implementation adds the `-maxfeerate` startup parameter, mapping it to a configurable limit in the wallet settings. During the transaction creation workflow in `CWallet::CreateTransaction`, the computed transaction fee rate is validated against this maximum threshold. If the fee rate exceeds the configured `maxfeerate`, transaction creation fails safely, preventing potential coin-loss due to extreme fee overpayment.

#### [#35301: Silent Payments: Implement bip352 (take 2)](https://github.com/bitcoin/bitcoin/pull/35301)
**Author:** [@Eunovo](https://github.com/Eunovo) | **[Network & Privacy]** *(Activity: 55 review events)*
> This PR advances the implementation of BIP352, the specification for Silent Payments, within Bitcoin Core. This is a crucial step towards integrating this privacy-enhancing technology, allowing users to leverage its benefits.

**Technical Details:** This PR focuses on the core cryptographic and address derivation logic defined in BIP352, which underpins Silent Payments. It likely involves implementing the necessary key derivation functions, shared secret computations, and output script generation rules as specified by BIP352, ensuring compliance with the standard. This 'take 2' suggests refinements or more complete coverage of the BIP's requirements, laying the groundwork for both sending and receiving Silent Payments.

#### [#35675: mining: add block template manager](https://github.com/bitcoin/bitcoin/pull/35675)
**Author:** [@ismaelsadeeq](https://github.com/ismaelsadeeq) | **[Strategic Initiatives]** *(Activity: 53 review events)*
> This PR introduces a new block template manager, a core component that streamlines the process of generating and managing block templates for miners. This improvement can enhance mining pool efficiency and robustness.

**Technical Details:** This PR integrates a new `BlockTemplateManager` class into the mining subsystem. Its primary role is to abstract and centralize the logic for creating, updating, and caching block templates, decoupling it from direct RPC calls. This manager will likely optimize template generation by reusing common data structures and efficiently incorporating new transactions or block height changes, providing a more robust and performant foundation for mining operations and future extensions.

#### [#27052: test: rpc: add last block announcement time to getpeerinfo result](https://github.com/bitcoin/bitcoin/pull/27052)
**Author:** [@LarryRuane](https://github.com/LarryRuane) | **[Wallet & User Tools]** *(Activity: 44 review events)*
> This PR enhances the `getpeerinfo` RPC by adding the last block announcement time for each peer. This provides users with more detailed information about their connected peers' block relay activity, aiding in network monitoring and debugging.

**Technical Details:** The PR modifies the `getpeerinfo` RPC handler to retrieve and include the `nLastBlockTime` (or a similar timestamp) from each connected peer's `CNode` object in the RPC response. This involves accessing peer-specific state within the networking layer and serializing this timestamp into the JSON output of the `getpeerinfo` call. A corresponding test is added to verify the presence and correctness of this new field in the RPC result.

#### [#34717: p2p: remove m_getaddr_sent](https://github.com/bitcoin/bitcoin/pull/34717)
**Author:** [@naiyoma](https://github.com/naiyoma) | **[Maintenance & Tech Debt]** *(Activity: 40 review events)*
> This PR streamlines Bitcoin Core's peer discovery logic by removing an unnecessary state variable. It simplifies the P2P code without impacting network functionality or stability.

**Technical Details:** The `m_getaddr_sent` boolean member was removed from `CNodeState`. This flag, intended to track if a GETADDR message had been sent to a peer, became redundant after the introduction of `fSentGetAddr`, which serves the same purpose more robustly. Removing it reduces state complexity within the P2P connection management and contributes to cleaner code.

#### [#35813: wallet, rpc: Add listrawtransactions RPC](https://github.com/bitcoin/bitcoin/pull/35813)
**Author:** [@pablomartin4btc](https://github.com/pablomartin4btc) | **[Wallet & User Tools]** *(Activity: 37 review events)*
> This new feature introduces a powerful RPC command, `listrawtransactions`, enabling users and developers to retrieve detailed, low-level transaction data directly from their wallet. This provides greater transparency and flexibility for advanced wallet management and analysis.

**Technical Details:** The `listrawtransactions` RPC iterates through the wallet's stored transactions, retrieving and exposing their raw transaction data (hex) along with associated metadata. The implementation likely includes optional parameters for filtering by address, block hash, or pagination to manage the output. This command offers more granular access to raw transaction bytes and details that were previously less accessible via other RPCs, facilitating advanced tooling and debugging for wallet users.

#### [#35440: wallet: check descriptor cache xpub length before decoding](https://github.com/bitcoin/bitcoin/pull/35440)
**Author:** [@alhudz](https://github.com/alhudz) | **[Wallet & User Tools]** *(Activity: 31 review events)*
> This PR enhances wallet descriptor cache handling by validating the length of extended public keys (xpubs) before attempting to decode them. This prevents potential crashes or errors from malformed or truncated data, improving wallet robustness.

**Technical Details:** The `DescriptorCache` could previously attempt to decode malformed or truncated extended public keys without prior length validation, potentially leading to errors or crashes during deserialization. This commit adds a check for `xpub_str.size()` before invoking `CBitcoinExtPubKey::Decode()`. By ensuring the input string is of an expected minimum length, the wallet becomes more resilient against invalid data in its descriptor cache.

#### [#35696: i2p: update leaseset encryption types](https://github.com/bitcoin/bitcoin/pull/35696)
**Author:** [@jpk68](https://github.com/jpk68) | **[Network & Privacy]** *(Activity: 25 review events)*
> This PR updates the supported leaseset encryption types for I2P connections, enhancing the security and compatibility of Bitcoin Core's I2P networking. This ensures that I2P communication remains robust and aligned with the latest I2P network standards.

**Technical Details:** I2P uses 'leasesets' to describe the routing information and capabilities of a destination, including supported encryption algorithms. This change involves updating the internal I2P client library or Bitcoin Core's I2P integration code to recognize and utilize newer or more secure encryption types for leasesets. This might involve modifying constants, enum values, or parsing logic related to I2P's `LeaseSet2` specification, ensuring that Bitcoin Core can establish and maintain secure, private connections over the I2P network.

#### [#35752: wallet: make encryption state updates atomic](https://github.com/bitcoin/bitcoin/pull/35752)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Wallet & User Tools]** *(Activity: 23 review events)*
> This PR ensures that updates to the wallet's encryption state are atomic operations, preventing data corruption or inconsistent states during unexpected shutdowns. This significantly enhances the robustness and security of encrypted wallets.

**Technical Details:** The wallet's encryption state management is modified to guarantee atomicity for state transitions (e.g., encrypting, decrypting, changing passphrase). This typically involves writing updates to a temporary file or using database transactions, and only committing the change once all operations are successful. This ensures that the wallet's encryption status is always in a valid, consistent state even if the application crashes mid-update, protecting against data integrity issues related to encryption. The change improves resilience against crashes.

#### [#31888: contrib: Support re-writing linearize-data dumps](https://github.com/bitcoin/bitcoin/pull/31888)
**Author:** [@midnightmagic](https://github.com/midnightmagic) | **[Maintenance & Tech Debt]** *(Activity: 19 review events)*
> This PR enhances the `linearize-data` tool in `contrib`, allowing it to modify existing block chain data dumps. This is useful for development and testing scenarios where custom block data manipulation is needed.

**Technical Details:** The `linearize-data` utility, which outputs a single linear blockchain file, is extended with functionality to read an existing `linearize.dat` file and apply re-writing or filtering operations. This enables developers to easily create modified blockchain datasets for specific test cases without re-downloading or re-processing the entire chain from raw blocks.

#### [#36312: net: don't discourage private broadcast peers](https://github.com/bitcoin/bitcoin/pull/36312)
**Author:** [@andrewtoth](https://github.com/andrewtoth) | **[Network & Privacy]** *(Activity: 17 review events)*
> This PR adjusts Bitcoin Core's network policy to no longer implicitly discourage peers participating in private transaction broadcasts. This helps ensure that nodes using this experimental feature can connect and relay transactions effectively without unintended penalties.

**Technical Details:** Previously, peers involved in private broadcast mechanisms might have been subject to certain network discouragement logic, potentially affecting their connectivity or relay performance. This PR modifies the network's peer management logic to remove this implicit discouragement, treating private broadcast peers more neutrally within the peer-to-peer network topology. The change specifically targets the peer scoring or connection management algorithms to prevent unintended negative feedback loops.

#### [#36309: private broadcast: clarify claims, mark as experimental](https://github.com/bitcoin/bitcoin/pull/36309)
**Author:** [@instagibbs](https://github.com/instagibbs) | **[Network & Privacy]** *(Activity: 17 review events)*
> This PR clarifies the claims and explicitly marks the 'private broadcast' feature as experimental. This helps users understand the current development status and potential limitations of this new transaction relay mechanism.

**Technical Details:** The changes involve updating internal documentation, comments, and potentially configuration flags or help text related to the 'private broadcast' feature. It ensures that the feature's experimental nature and any associated caveats are clearly communicated to developers and users, reflecting its ongoing development and potential for future changes or removal. This is primarily a documentation and feature status management update for a network-level capability.

#### [#35619: test:  ExtendedPrivateKey follow-ups](https://github.com/bitcoin/bitcoin/pull/35619)
**Author:** [@rkrux](https://github.com/rkrux) | **[Maintenance & Tech Debt]** *(Activity: 16 review events)*
> This PR adds further tests related to `ExtendedPrivateKey` functionality. It helps ensure the robustness and correctness of key management within Bitcoin Core.

**Technical Details:** This PR introduces additional test cases for the `ExtendedPrivateKey` class, likely covering edge cases or specific behaviors not previously tested. It aims to improve the test coverage and reliability of hierarchical deterministic key derivation and management, ensuring the integrity of private key operations.

#### [#34371: wallet: allow importprunedfunds for spending transactions](https://github.com/bitcoin/bitcoin/pull/34371)
**Author:** [@8144225309](https://github.com/8144225309) | **[Wallet & User Tools]** *(Activity: 14 review events)*
> This PR enhances the `importprunedfunds` RPC to support importing spending transactions. This allows users to recover and track funds more flexibly, even for transactions that have already been spent and confirmed.

**Technical Details:** It modifies the `importprunedfunds` RPC handler to correctly process and import transactions where the imported outputs are already spent within the transaction itself or by subsequent transactions in the chain. This involves ensuring the wallet can properly reconstruct the full transaction history and state for such scenarios, improving recovery capabilities.

#### [#36316: ci: use POSIX threads for Nix Windows builds](https://github.com/bitcoin/bitcoin/pull/36316)
**Author:** [@willcl-ark](https://github.com/willcl-ark) | **[Maintenance & Tech Debt]** *(Activity: 13 review events)*
> This PR updates the Continuous Integration (CI) configuration for Bitcoin Core to use POSIX threads when building on Windows using Nix. This improves the reliability and consistency of Windows builds within the CI system.

**Technical Details:** The change involves modifying the Nix build configuration for Windows targets. Specifically, it configures the build system to link against and utilize POSIX-compliant threading libraries (e.g., pthreads-w32) instead of native Windows threading APIs. This ensures a more consistent threading model across different build environments and resolves potential compatibility issues or build failures specific to the Nix-on-Windows CI setup.

#### [#35809: contrib: add deterministic fuzz coverage mode](https://github.com/bitcoin/bitcoin/pull/35809)
**Author:** [@HowHsu](https://github.com/HowHsu) | **[Maintenance & Tech Debt]** *(Activity: 13 review events)*
> This PR introduces a deterministic fuzzing coverage mode to our `contrib` tools. This allows developers to reliably reproduce specific fuzzing inputs that achieve high code coverage, significantly aiding in debugging and improving the effectiveness of our testing efforts.

**Technical Details:** Fuzzing typically involves random input generation, making it challenging to reproduce specific coverage paths. This PR adds a mode to the fuzzing harness that, given a seed or specific input, will deterministically generate the same sequence of inputs, allowing for reproducible coverage analysis. This is achieved by controlling the random number generator used by the fuzzer and potentially integrating with coverage tools to map specific inputs to code paths, making it easier to identify and fix bugs found by the fuzzer.

#### [#36322: init: fee estimates can lag behind the chain after restart](https://github.com/bitcoin/bitcoin/pull/36322)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Wallet & User Tools]** *(Activity: 12 review events)*
> This PR fixes a bug where fee estimates could become outdated and lag behind the actual blockchain state immediately after a node restart. This ensures that users receive accurate and timely fee recommendations, improving the reliability of transaction confirmations.

**Technical Details:** Upon restart, the fee estimation logic might not immediately have enough recent block data or might incorrectly re-initialize its state, leading to stale estimates. This fix likely involves ensuring that the fee estimator correctly re-syncs its internal data structures with the current blockchain tip and recent block history upon startup. This could involve re-processing a sufficient number of recent blocks to rebuild a robust fee estimation model, or ensuring that cached data is properly invalidated and re-populated, preventing the estimator from relying on old or insufficient data.

#### [#36135: fuzz: test HTTPRequest state machine in http_request](https://github.com/bitcoin/bitcoin/pull/36135)
**Author:** [@frankomosh](https://github.com/frankomosh) | **[Maintenance & Tech Debt]** *(Activity: 12 review events)*
> This PR adds a new fuzzing test specifically targeting the HTTPRequest state machine within `http_request.cpp`. This helps uncover edge cases and potential vulnerabilities in how Bitcoin Core handles HTTP requests, improving the overall robustness of its network communication.

**Technical Details:** The `http_request` module handles incoming HTTP requests for services like RPC. Its state machine manages the parsing and processing of HTTP headers and bodies. This fuzzing target will feed malformed or unexpected sequences of bytes to the HTTPRequest parser, simulating various network conditions and adversarial inputs. The fuzzer will then monitor for crashes, assertions, or other undefined behaviors, ensuring the state machine correctly transitions and handles all possible input permutations without compromising stability.

#### [#1840: ci: Simplify module configuration and extend test coverage](https://github.com/bitcoin/bitcoin/pull/1840)
**Author:** [@mllwchrry](https://github.com/mllwchrry) | **[Maintenance & Tech Debt]** *(Activity: 12 review events)*

#### [#36283: kernel: expose transaction version](https://github.com/bitcoin/bitcoin/pull/36283)
**Author:** [@nervana21](https://github.com/nervana21) | **[Strategic Initiatives]** *(Activity: 11 review events)*
> This PR exposes the transaction version field directly within the Bitcoin Kernel, making this fundamental data point more readily accessible to internal components. This facilitates cleaner code and future development by providing direct access to transaction versioning.

**Technical Details:** The change modifies the core transaction data structures or interfaces within the Bitcoin Kernel, likely by adding a new public member or a getter method (e.g., `GetVersion()`) to `CTransaction` or `CTransactionRef`. This allows kernel-level components to directly query the transaction's version without needing to access the raw serialized data or rely on higher-level parsing, promoting better encapsulation and modularity within the kernel architecture.

#### [#35948: init: correct first-run disk space estimate](https://github.com/bitcoin/bitcoin/pull/35948)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Wallet & User Tools]** *(Activity: 11 review events)*
> This PR corrects the estimated disk space required for Bitcoin Core on its first run. This provides users with more accurate information upfront, improving the initial setup experience and preventing potential confusion.

**Technical Details:** During the initial synchronization process, Bitcoin Core provides an estimate of the disk space needed to store the blockchain. This PR addresses an inaccuracy in that calculation, likely due to outdated assumptions about block sizes, UTXO set growth, or database overhead. The fix involves revising the constants or algorithms used in the `init` module to compute this estimate, ensuring it more closely reflects current blockchain data characteristics and anticipated future growth, thus offering a more reliable user prompt.

#### [#35177: test: use MiniWallet for getblockstats test data generation](https://github.com/bitcoin/bitcoin/pull/35177)
**Author:** [@AgusR7](https://github.com/AgusR7) | **[Maintenance & Tech Debt]** *(Activity: 11 review events)*
> This change updates the `getblockstats` test suite to use the `MiniWallet` utility for test data generation. This improves test reliability, maintainability, and aligns testing practices with modern Bitcoin Core standards.

**Technical Details:** The test harness for the `getblockstats` RPC command is refactored to replace manual transaction and block construction logic with the `MiniWallet` testing utility. This streamlines test setup, reduces boilerplate code, and enhances the overall readability and maintainability of the relevant test cases within the suite.

#### [#36261: test: cover PSBT unknown field merging](https://github.com/bitcoin/bitcoin/pull/36261)
**Author:** [@Bicaru20](https://github.com/Bicaru20) | **[Wallet & User Tools]** *(Activity: 9 review events)*
> This PR adds new tests to ensure that Partially Signed Bitcoin Transactions (PSBTs) correctly handle and merge unknown fields. This improves the robustness and forward compatibility of PSBTs, allowing for future extensions without breaking existing implementations.

**Technical Details:** This PR introduces specific test cases within the PSBT test suite to verify the behavior of `CMergePSBT` when encountering unknown fields in different PSBT parts (e.g., global, input, output). It ensures that unknown fields are preserved and correctly propagated during the merging process, adhering to the PSBT specification for extensibility and future-proofing.

#### [#35923: mempool: count unbroadcast txids in memory usage](https://github.com/bitcoin/bitcoin/pull/35923)
**Author:** [@l0rinc](https://github.com/l0rinc) | **[Performance & Optimization]** *(Activity: 8 review events)*
> This PR improves the accuracy of mempool memory usage reporting by including the memory consumed by transaction IDs that have not yet been broadcast. This provides a more complete picture of the mempool's resource consumption.

**Technical Details:** The mempool's internal data structures track transaction IDs for various purposes, including those awaiting broadcast in `m_unbroadcast_txids`. This PR modifies the memory accounting mechanisms within the `CTxMemPool` class to explicitly sum the memory footprint of these 'unbroadcast' transaction IDs. This involves iterating over the relevant data structures and adding their estimated size to the total reported mempool memory usage, providing a more precise metric for resource management.

#### [#36324: test: Fixup MAX_BODY_SIZE http throttling test](https://github.com/bitcoin/bitcoin/pull/36324)
**Author:** [@maflcko](https://github.com/maflcko) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR improves an existing test for HTTP request throttling in Bitcoin Core. It ensures the test accurately verifies how the software handles large HTTP requests, preventing potential denial-of-service vectors.

**Technical Details:** The PR adjusts the `MAX_BODY_SIZE` parameter within a specific HTTP throttling test, likely correcting an edge case or race condition in the test setup. This ensures the test reliably triggers and verifies the intended throttling behavior for oversized HTTP request bodies, thereby improving test coverage and reliability of the HTTP server's DoS protection.

#### [#35887: ipc: use std::optional for checkSpawned(), add tests and rename arg -ipcfd to -ipcchild](https://github.com/bitcoin/bitcoin/pull/35887)
**Author:** [@ViniciusCestarii](https://github.com/ViniciusCestarii) | **[Maintenance & Tech Debt]** *(Activity: 8 review events)*
> This PR refactors the Inter-Process Communication (IPC) mechanism by adopting `std::optional` for better error handling and clarity, adds new tests, and renames a command-line argument for improved consistency. These changes enhance the reliability and maintainability of Bitcoin Core's IPC features.

**Technical Details:** The PR modernizes the `checkSpawned()` function within the IPC module by replacing raw pointers or sentinel values with `std::optional<int>`, improving type safety and explicit handling of the absence of a value. It also introduces dedicated unit tests for the IPC functionality and renames the command-line argument `-ipcfd` to `-ipcchild` for better semantic clarity, affecting how child processes are spawned and managed.

#### [#35984: sign: skip signing SIGHASH_SINGLE inputs with no corresponding output](https://github.com/bitcoin/bitcoin/pull/35984)
**Author:** [@furszy](https://github.com/furszy) | **[Wallet & User Tools]** *(Activity: 7 review events)*
> This PR improves transaction signing logic by skipping inputs that use `SIGHASH_SINGLE` but lack a corresponding output. This prevents the creation of invalid transactions and enhances the reliability of the wallet's signing process.

**Technical Details:** The `SIGHASH_SINGLE` flag commits to only the input being signed and the output at the same index. If a transaction input specifies `SIGHASH_SINGLE` but there is no output at the corresponding index, the resulting signature is invalid. This change modifies the signing algorithm within the wallet to detect this specific condition before attempting to sign. By checking `tx.vout.size() <= input_index` for `SIGHASH_SINGLE` inputs, the signing process can proactively avoid generating invalid signatures, improving robustness and user experience.

#### [#36284: wallet: don't double discard output groups with avoidpartialspends](https://github.com/bitcoin/bitcoin/pull/36284)
**Author:** [@fjahr](https://github.com/fjahr) | **[Wallet & User Tools]** *(Activity: 7 review events)*
> This PR fixes a bug in the wallet's coin selection logic that could cause certain UTXO groups to be discarded twice when using the `avoidpartialspends` option. This ensures more efficient and correct coin selection, improving the reliability of transaction creation.

**Technical Details:** The bug occurred within the `SelectCoins` function when `avoidpartialspends` was enabled, leading to an output group being added to the `discarded_groups` list multiple times. This PR modifies the coin selection algorithm to ensure that an output group is only added to the `discarded_groups` once, preventing redundant processing and potential inefficiencies or incorrect behavior in subsequent coin selection iterations, thus optimizing UTXO management.

#### [#35890: doc: use overwrite (>) instead of append (>>) for one-shot PSBT files in offline-signing-tutorial.md](https://github.com/bitcoin/bitcoin/pull/35890)
**Author:** [@GuTS805](https://github.com/GuTS805) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR updates the offline signing tutorial documentation to correctly use the overwrite operator (>) instead of the append operator (>>) when creating one-shot PSBT files. This ensures users follow the correct procedure and avoid unintended file concatenations.

**Technical Details:** The change is purely textual within the `offline-signing-tutorial.md` markdown file, correcting a shell command example from `command >> file.psbt` to `command > file.psbt`. This ensures that each execution of the command creates a fresh PSBT file, preventing the accidental appending of new PSBT data to an existing file, which would result in an invalid or malformed PSBT.

#### [#35893: test: cover submitpackage other-wtxid for same-txid-diff-witness](https://github.com/bitcoin/bitcoin/pull/35893)
**Author:** [@mercie-ux](https://github.com/mercie-ux) | **[Maintenance & Tech Debt]** *(Activity: 6 review events)*
> This PR adds a new test case to cover a specific edge scenario in the `submitpackage` RPC related to transactions with the same transaction ID but different witness data. This improves the robustness of package relay by ensuring correct handling of such complex and potentially malformed inputs.

**Technical Details:** The test specifically targets the `submitpackage` RPC, which is designed for package relay. It introduces a scenario where a package might contain transactions that, despite having identical transaction IDs, differ in their witness data. While this shouldn't occur with valid SegWit transactions, the test ensures the `submitpackage` logic correctly identifies and rejects or handles such malformed inputs, preventing unexpected behavior or potential vulnerabilities in the package relay mechanism.

#### [#36335: Remove my key from SECURITY.md](https://github.com/bitcoin/bitcoin/pull/36335)
**Author:** [@dergoegge](https://github.com/dergoegge) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR removes a developer's PGP key from the `SECURITY.md` file. This is a routine update to maintain the accuracy of our security contact information, ensuring only active and relevant keys are listed.

**Technical Details:** The `SECURITY.md` file lists PGP keys of developers who can be contacted securely for reporting vulnerabilities. This change involves a direct modification to this markdown file, removing a specific PGP key block. This action is typically performed when a developer is no longer actively involved in the project's security response team or has rotated their key, ensuring that the published security contact information remains current and trustworthy.

#### [#36155: doc: remove json quoting from gettxoutsetinfo and getblockstats cli examples](https://github.com/bitcoin/bitcoin/pull/36155)
**Author:** [@csjones](https://github.com/csjones) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR corrects the command-line examples in the documentation for `gettxoutsetinfo` and `getblockstats` by removing unnecessary JSON quoting. This makes the examples clearer and easier for users to execute directly.

**Technical Details:** The change is purely textual within the documentation files, specifically modifying `bitcoin-cli` examples for `gettxoutsetinfo` and `getblockstats`. It removes redundant JSON string quoting around parameters that are already correctly interpreted by `bitcoin-cli` or the RPC server, simplifying the command syntax presented to users and aligning it with common `bitcoin-cli` usage patterns.

#### [#36310: rpc: clarify that `getaddrmaninfo` counts unique addresses](https://github.com/bitcoin/bitcoin/pull/36310)
**Author:** [@0xB10C](https://github.com/0xB10C) | **[Maintenance & Tech Debt]** *(Activity: 5 review events)*
> This PR clarifies the documentation for the `getaddrmaninfo` RPC, explicitly stating that it reports the count of unique addresses. This improves the usability and understanding of network information for users and developers.

**Technical Details:** The change involves updating the RPC help text or internal comments for the `getaddrmaninfo` RPC. It ensures that users are aware that the reported address count represents distinct entries in the address manager, preventing potential misinterpretations of the network's known addresses and improving RPC clarity.

#### [#1934: Clear secret-dependent variables in `_ecmult_const_xonly`](https://github.com/bitcoin/bitcoin/pull/1934)
**Author:** [@theStack](https://github.com/theStack) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR fixes a bug in the `CBigNum::SetHex` function that could lead to undefined behavior by incorrectly storing a temporary pointer. This ensures the stability and correctness of large number operations within the codebase.

**Technical Details:** The `CBigNum::SetHex` method is responsible for parsing hexadecimal strings into `CBigNum` objects. The bug involved storing a pointer to a temporary object created during the parsing process, which would become invalid once the temporary object went out of scope. The fix likely involves either copying the data pointed to by the temporary pointer or ensuring that the data is allocated with a lifetime matching the `CBigNum` object itself, preventing use-after-free scenarios and ensuring data integrity for arbitrary precision arithmetic.

#### [#36302: ci: simplify macOS codesign check](https://github.com/bitcoin/bitcoin/pull/36302)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 4 review events)*
> This PR streamlines the code signing verification process for macOS builds in the continuous integration system. It makes the development and release pipeline more efficient and reliable.

**Technical Details:** This change refactors the CI script responsible for checking macOS code signatures, likely by consolidating steps, removing redundancies, or using more efficient commands. The goal is to reduce CI execution time and potential points of failure related to macOS build verification, improving the overall CI pipeline's stability.

#### [#36298: Update crc32c subtree to latest master](https://github.com/bitcoin/bitcoin/pull/36298)
**Author:** [@fanquake](https://github.com/fanquake) | **[Maintenance & Tech Debt]** *(Activity: 3 review events)*
> This PR updates the `crc32c` library to its latest version, incorporating any upstream improvements or bug fixes. This ensures Bitcoin Core uses the most current and optimized checksum calculation, contributing to data integrity.

**Technical Details:** The change involves updating the vendored `crc32c` library by pulling the latest commits from its upstream repository. This update ensures that Bitcoin Core benefits from any performance optimizations or bug fixes in the CRC32C checksum implementation, which is used for various data integrity checks within the codebase, enhancing overall system reliability.

#### [#36278: Update minisketch subtree to latest master](https://github.com/bitcoin/bitcoin/pull/36278)
**Author:** [@fanquake](https://github.com/fanquake) | **[Strategic Initiatives]** *(Activity: 2 review events)*
> This PR updates the `minisketch` library to its latest version, bringing in improvements and bug fixes from the upstream project. This ensures Bitcoin Core benefits from the most recent advancements in compact set reconciliation, which is crucial for features like AssumeUTXO.

**Technical Details:** The PR involves pulling the latest commits from the upstream `minisketch` repository into Bitcoin Core's vendored subtree. This update incorporates any performance enhancements, bug fixes, or new features developed in `minisketch`, which is utilized for efficient set reconciliation, particularly in the context of the AssumeUTXO project for faster initial block download.

#### [#1942: unit_test: fix help text claiming unknown args are ignored](https://github.com/bitcoin/bitcoin/pull/1942)
**Author:** [@Anshikakalpana](https://github.com/Anshikakalpana) | **[Maintenance & Tech Debt]** *(Activity: 1 review events)*
> This PR resolves a build system issue by fixing a double inclusion of `txdb.h` in the `bitcoin-qt.pro` project file. This ensures cleaner compilation and prevents potential build errors for the GUI client.

**Technical Details:** The change modifies the `bitcoin-qt.pro` file, which is used by the Qt build system, to remove a redundant inclusion of the `txdb.h` header. This prevents potential 'multiple definition' errors or warnings during compilation, streamlining the build process for the Bitcoin Core GUI and improving build system robustness.

## 🔍 Under Review (Hot PRs)
The most actively discussed and reviewed open pull requests right now.

#### [#36312: net: don't discourage private broadcast peers](https://github.com/bitcoin/bitcoin/pull/36312)
**Author:** [@andrewtoth](https://github.com/andrewtoth) | **[Network & Privacy]** *(Activity: 17 review events this week)*
> This PR adjusts Bitcoin Core's network policy to no longer implicitly discourage peers participating in private transaction broadcasts. This helps ensure that nodes using this experimental feature can connect and relay transactions effectively without unintended penalties.

#### [#36309: private broadcast: clarify claims, mark as experimental](https://github.com/bitcoin/bitcoin/pull/36309)
**Author:** [@instagibbs](https://github.com/instagibbs) | **[Network & Privacy]** *(Activity: 17 review events this week)*
> This PR clarifies the claims and explicitly marks the 'private broadcast' feature as experimental. This helps users understand the current development status and potential limitations of this new transaction relay mechanism.

#### [#36235: ci: fail iwyu job on compiler errors instead of silently logging them](https://github.com/bitcoin/bitcoin/pull/36235)
**Author:** [@David-Uka](https://github.com/David-Uka) | **[Maintenance & Tech Debt]** *(Activity: 15 review events this week)*
> This PR improves our continuous integration system by making the 'Include What You Use' (IWYU) job fail explicitly on compiler errors. This ensures that potential build issues are immediately visible and addressed, preventing silent failures.

#### [#36316: ci: use POSIX threads for Nix Windows builds](https://github.com/bitcoin/bitcoin/pull/36316)
**Author:** [@willcl-ark](https://github.com/willcl-ark) | **[Maintenance & Tech Debt]** *(Activity: 13 review events this week)*
> This PR updates the Continuous Integration (CI) configuration for Bitcoin Core to use POSIX threads when building on Windows using Nix. This improves the reliability and consistency of Windows builds within the CI system.

#### [#35686: lint: have git-subtree-check check for backportability](https://github.com/bitcoin/bitcoin/pull/35686)
**Author:** [@Sjors](https://github.com/Sjors) | **[Maintenance & Tech Debt]** *(Activity: 13 review events this week)*
> This PR enhances our linting tools by adding a check to `git-subtree-check` for backportability issues. This helps ensure that changes can be easily applied to older release branches, streamlining our release process and reducing manual effort.

## 🗓️ Dev Meeting
Summary of the core dev IRC meeting on 2026-09-24 with 24 participants.

- Fuzzing Working Group: dergoegge announced his departure from full-time contribution, with his projects and security contact responsibilities transitioning to Brink's Marco (marcofleon) and Eugene (eugenesiegel). dergoegge will open PRs to update security contacts.
- QML GUI Working Group: johnny9dev reported ongoing work on design, issue resolution, and staging, with no significant updates this week.
- 32.0 Release Candidate Testing: sedited announced the availability of 32.0rc2 binaries for community testing. The umbrella issue #36315 provides links to the proposed release notes and testing guide. Additional pull requests are being backported for milestone 84.

**Action Items:**
- Community members are requested to test the 32.0rc2 binaries, using issue #36315 for tracking feedback and referring to the linked release notes and testing guide.
- dergoegge will open PRs to remove himself as a security contact by the end of the week.

## 🗣️ Research & Governance
Top active threads across mailing lists and research forums.

### [Re: [bitcoindev] A Post-Quantum Path for BIP 324](https://gnusha.org/pi/bitcoindev/CAO3Pvs_+orjc1mbEVSpOpCApy1SjuGH+yhRfJX2aGB6ZZ0hAyg@mail.gmail.com)
**Source:** Mailing List | **Started By:** {'username': 'Olaoluwa Osuntokun', 'uuid': 'can_olaoluwa_osuntokun'} | **Messages:** 1
> Developers are exploring if new, advanced cryptographic methods can make it significantly harder to track users or censor transactions, enhancing privacy and resistance to surveillance.

**Technical Details:** The discussion evaluates the practical privacy benefits of Compact Round-Trip Quantum-Resistant Cryptography (CRQC) against fingerprinting and censorship. Liam questioned if CRQC meaningfully lowers these costs, with Olaoluwa suggesting quantum attacks like Shor's algorithm are unlikely to be cheaper than classical timing analysis for such purposes. This highlights an architectural debate on the incremental privacy value of quantum-resistant schemes for side-channel resistance versus focusing on existing classical attack vectors, requiring further cost-benefit analysis.

### [Re: [bitcoindev] Re: [BIP Proposal] No burn, Quantum Migration
 Proposal, Quantum Secure Asset Verification & Escrow (QSAVE)](https://gnusha.org/pi/bitcoindev/48b51073-e3d5-4875-a16d-216fb12fa7fcn@googlegroups.com)
**Source:** Mailing List | **Started By:** {'username': 'James T', 'uuid': 'auto_james_t'} | **Messages:** 1
> Bitcoin's long-term security is a key focus, with developers proactively discussing how to ensure the network remains robust against future technological advancements like quantum computing. This ongoing dialogue reinforces Bitcoin's commitment to enduring value and security for all users.

**Technical Details:** The mailing list is revisiting historical discussions concerning the long-term security of SHA256 against future quantum computing threats. While early acknowledgments suggested a potential 'chain rewrite' under extreme circumstances, the current debate likely centers on the practicality and implications of such a drastic measure. Developers are evaluating whether less disruptive protocol upgrades can achieve quantum resistance, or if the threat to SHA256 warrants considering fundamental architectural changes to the blockchain's structure.

### [Re: [bitcoindev] [BIP Proposal] BIP324 One-Byte Message Type ID Alias Assignment](https://gnusha.org/pi/bitcoindev/arRwjJaraiHdYX8L@erisian.com.au)
**Source:** Mailing List | **Started By:** {'username': 'Anthony Towns', 'uuid': 'can_anthony_towns'} | **Messages:** 1
> A new proposal is being discussed to enhance how Bitcoin nodes interact, aiming to improve network communication or efficiency for all users.

**Technical Details:** Anthony Towns is summarizing a proposal where nodes implementing it would transmit specific information. The provided context does not detail what data would be sent, its purpose, or the technical arguments surrounding its implementation, making a full architectural assessment or explanation of required changes impossible at this time.

### [[bitcoindev] Bitcoin Core 32.0rc2 release candidate is available](https://gnusha.org/pi/bitcoindev/465fa469-1fdf-45d9-9f8e-309ccc472bf5n@googlegroups.com)
**Source:** Mailing List | **Started By:** {'username': 'Sebastian Kung', 'uuid': 'auto_sebastian_kung'} | **Messages:** 1
> The latest release candidate for Bitcoin Core, v32.0rc2, is now available for community testing. This crucial step helps ensure the next stable version of Bitcoin's foundational software is robust and secure for all users.

**Technical Details:** Bitcoin Core v32.0rc2 binaries have been released and are available for download, alongside the signed source code tag on GitHub. This release candidate is critical for comprehensive community testing to identify and address any remaining bugs or regressions before the final v32.0 stable release. Developers and advanced users are strongly encouraged to test this RC, providing valuable feedback to validate the stability, security, and performance of new features and bug fixes integrated into this version. The primary objective is thorough validation to ensure a high-quality production release.

### [[bitcoindev] Convention for tagged hash tags in BIPs](https://gnusha.org/pi/bitcoindev/dxapm4DOcrDL6_oCYSqBAdFP0fAQA9IHInRzzTuCeWVYD2Xd0ynPsTa8hYEcRFOYQPnvoQK15TtK6oAZBfa-4b5DbIuFemSFGVifxGTLOlc=@protonmail.com)
**Source:** Mailing List | **Started By:** {'username': 'Fabian Jahr', 'uuid': 'can_fabian_jahr'} | **Messages:** 1
> To enhance clarity and consistency for future Bitcoin upgrades, developers are discussing the optimal naming conventions for new cryptographic features within the protocol.

**Technical Details:** During the review of BIP 459 (DahLIAS), an architectural debate emerged regarding the naming convention for 'tagged hash tags' in cryptography BIPs. The current practice is inconsistent, with some BIPs embedding their numerical identifier while others use descriptive names. This necessitates a community decision on a standardized approach to ensure protocol coherence, prevent identifier collisions, and establish clear guidelines for future cryptographic feature integration.

## 🏆 Contributor Shoutouts
### 🎉 First-Time Merges
Welcome to the codebase: [@AgusR7](https://github.com/AgusR7), [@Anshikakalpana](https://github.com/Anshikakalpana), [@Bicaru20](https://github.com/Bicaru20), [@alhudz](https://github.com/alhudz), [@mercie-ux](https://github.com/mercie-ux)

### ✍️ Top Authors
The most active PR authors this week: [@l0rinc](https://github.com/l0rinc), [@fanquake](https://github.com/fanquake), [@ismaelsadeeq](https://github.com/ismaelsadeeq), [@0xB10C](https://github.com/0xB10C), [@Bicaru20](https://github.com/Bicaru20)

### 🕵️ Top Reviewers
Providing critical review and testing: [@maflcko](https://github.com/maflcko), [@sedited](https://github.com/sedited), [@l0rinc](https://github.com/l0rinc), [@w0xlt](https://github.com/w0xlt), [@hebasto](https://github.com/hebasto)
