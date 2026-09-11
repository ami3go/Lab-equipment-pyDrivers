# LPDS-005 — Driver Package Specification

**Document ID:** LPDS-005  
**Version:** 1.3  
**Status:** Draft Project Standard (Normative)  
**Applies to:** Every LPDS Python instrument driver repository, development-gate package, and public release package

---

## Revision 1.3 summary

Version 1.3 consolidates the required repository and release-package layout and aligns it with the current LPDS platform, AI-contract, lifecycle, and call/protocol-conformance requirements.

This revision:

- preserves the public ZIP name `<driver_name>_v<year>.<release>.zip`;
- preserves the stable internal root folder `<driver_name>/`;
- requires current `history/`, `review/`, `examples/`, `scripts/`, `guide/`, `README.md`, and GitHub Pages content in every release;
- requires at least ten complete plain-Python driver examples;
- defines the authoritative `src/`-layout Python driver package, with any framework adapter kept in a separate, optional, clearly bounded directory;
- incorporates LPDS-017 AI Driver Contract files;
- provides an LPDS-018 bench-contract template location without embedding a real bench definition in the driver;
- incorporates the complete LPDS-019 call and protocol conformance structure, runners, and evidence requirements;
- distinguishes repository content, distributable package content, runtime results, and release evidence;
- defines mandatory structure validation, exclusions, release-integrity records, and acceptance criteria.

---

## 1. Purpose

This specification defines the mandatory repository, Python package, test, example, script, documentation, review, history, AI-contract, and release-archive layout for LPDS Python instrument drivers.

Its objectives are to ensure that every driver:

1. has a predictable structure;
2. can replace an earlier extracted revision without changing the project path;
3. exposes one authoritative Python public API;
4. separates driver logic (device semantics, protocol handling, transport handling) from any optional automation-framework adaptation layer;
5. can be installed, tested, documented, reviewed, and released consistently;
6. contains sufficient examples and setup instructions for practical use;
7. contains traceable change and review records for every delivered revision;
8. supports deterministic software-only testing and controlled hardware testing;
9. contains synchronized LPDS-017 and LPDS-019 machine-readable artifacts;
10. produces verifiable release archives with consistent version identity.

LPDS-005 defines **where required artifacts belong and what minimum content they shall contain**. It does not define device-specific command semantics or the complete public API standard.

---

## 2. Scope boundary

### 2.1 In scope

LPDS-005 covers:

- repository naming;
- public release ZIP naming;
- development-gate artifact naming;
- stable internal ZIP root;
- Python driver package layout;
- optional framework adapter layout;
- transport, protocol, model, configuration, and diagnostics locations;
- LPDS-017 AI Driver Contract locations;
- LPDS-018 template location;
- LPDS-019 conformance-test locations;
- unit, conformance, integration, replay, HIL, compatibility, and performance test locations;
- examples and example runners;
- setup, test, conformance, documentation, and release scripts;
- history and review evidence;
- README, guides, generated API reference, and GitHub Pages sources;
- release manifests, checksums, SBOM, and release exclusions;
- structure validation and minimum release acceptance.

### 2.2 Out of scope

LPDS-005 does not independently define:

- vendor protocol commands;
- complete device-capability coverage;
- mandatory public API method names and signatures;
- common base-class implementation details;
- transport behavior;
- error taxonomy;
- physical measurement accuracy;
- calibration requirements;
- bench wiring;
- electrical safety limits;
- performance targets;
- release approval authority beyond required package evidence.

These are governed by other LPDS documents and device-specific requirements.

---

## 3. Normative references

A conforming project shall follow the applicable approved revisions of:

- **LPDS-001 — Platform Requirements**;
- **LPDS-002 — Mandatory Public API Standard**;
- **LPDS-003 — BaseInstrument Specification**;
- **LPDS-004 — Transport Layer Specification**;
- **LPDS-008 — Logging and Evidence Standard**;
- **LPDS-017 — AI Driver Contract Specification**;
- **LPDS-018 — AI Test Bench Contract Specification**;
- **LPDS-019 — Driver Call and Protocol Conformance Test Specification**;
- **LPDS-020 — Driver Implementation Lifecycle**;
- the device-specific implementation requirement;
- the vendor programming, protocol, SDK, or command documentation.

When requirements conflict, the following precedence shall apply:

1. safety requirement;
2. approved device-specific hardware constraint;
3. latest approved LPDS normative requirement;
4. this package specification;
5. examples and historical project patterns.

Every approved exception shall be recorded in both:

```text
review/requirement_traceability.md
review/known_risks.md
```

---

## 4. Normative terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement; deviation requires documented justification;
- **may** — permitted implementation choice;
- **repository** — the complete source-control project;
- **gate package** — a reviewable lifecycle engineering delivery;
- **public release package** — the approved distributable driver ZIP;
- **runtime output** — generated logs, reports, traces, caches, locks, and temporary files;
- **release evidence** — reviewed evidence used to justify a release verdict;
- **driver** — the plain, framework-independent Python package that implements device control and exposes the public API;
- **adapter** — a separate, optional, thin translation layer that exposes a driver instance's public API to one specific automation framework or interface; an adapter contains no device logic of its own.

A required directory shall not be represented by an unexplained empty placeholder. Before its intended lifecycle gate, it may contain a `README.md` stating what will populate it and at which gate.

---

## 5. Naming and release identity

### 5.1 Driver identifier

Every driver shall define one stable identifier:

```text
<driver_name>
```

Rules:

- lowercase ASCII;
- `snake_case` only;
- no spaces;
- no hyphens;
- no embedded version;
- vendor and device family should be recognizable;
- the same identifier shall be used consistently in the repository root, import package, documentation, scripts, AI contract, and release metadata unless Python distribution normalization requires a documented alternative.

Examples:

```text
keysight34970
keysight_n6700
hp34401a
bk8500b
phidget_relay
climate_chamber
```

### 5.2 Public release ZIP

Every approved public release or update shall use:

```text
<driver_name>_v<year>.<release>.zip
```

Where:

- `<year>` is the two-digit project year;
- `<release>` is the monotonically increasing public release or update number for that driver within the year, zero-padded to two digits per LPDS-011 §5.2 (the sole normative source for the exact version-string format).

Examples:

```text
keysight34970_v26.05.zip
hp34401a_v26.06.zip
hp34401a_v27.01.zip
```

The public archive name shall not contain:

- spaces;
- `final`, `new`, `latest`, `fixed`, or similar words;
- a gate name;
- an unreviewed build identifier;
- another date in addition to the version;
- nested version suffixes that are not part of the approved version model.

### 5.3 Development gate package

A lifecycle gate package may use:

```text
<driver_name>_vYY.PP.GG.zip
```

Where:

- `YY` is the two-digit year;
- `PP` is the implementation phase;
- `GG` is the gate number.

Example:

```text
keysight34970_v26.02.04.zip
```

A gate package is not a public release. Promotion after Gate 5 shall regenerate public version metadata, history, reviews, documentation, manifests, checksums, and the public ZIP name.

### 5.4 Stable internal ZIP root

Every gate and public ZIP shall contain exactly one top-level folder:

```text
<driver_name>/
```

Example:

```text
keysight34970_v26.05.zip
└── keysight34970/
```

The internal root shall never include a version. No README, checksum, nested ZIP, or other file may exist beside the internal root inside the archive.

### 5.5 Version identity

The project shall document and validate:

- public ZIP version;
- display version;
- Python distribution version;
- Python import package (the driver);
- driver/core version when separate;
- for each published adapter: its distribution version and its import path;
- AI contract version;
- conformance-specification version.

All representations shall identify the same release. Python packaging normalization differences shall be documented in `docs/release_notes.md` and release metadata.

---

## 6. Canonical repository and package layout

New LPDS driver projects shall use the following layout. Device-specific files may be added. Mandatory paths shall not be renamed, relocated, or replaced by equivalent content in an undocumented location.

```text
<driver_name>/
├── src/
│   └── <driver_name>/
│       ├── __init__.py
│       ├── driver.py
│       ├── sessions.py
│       ├── converters.py
│       ├── models.py
│       ├── exceptions.py
│       ├── configuration.py
│       ├── diagnostics.py
│       ├── capabilities.py
│       ├── version.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── ...
│       ├── protocol/
│       │   ├── __init__.py
│       │   └── ...
│       ├── transports/
│       │   ├── __init__.py
│       │   ├── simulator.py
│       │   └── ...
│       └── resources/
│           └── ...
├── adapters/
│   └── robotframework/
│       ├── __init__.py
│       ├── keywords.py
│       ├── resources/
│       │   ├── common.resource
│       │   └── variables.example.yaml
│       ├── examples/
│       │   ├── 01_*.robot
│       │   └── ...
│       └── tests/
├── ai/
│   ├── ai_contract.yaml
│   ├── ai_contract.lock
│   └── system_ai_contract.template.yaml
├── config/
│   ├── schema.json
│   ├── schema.lock
│   ├── default.json
│   ├── example.json
│   ├── hil_resources.example.yaml
│   ├── profiles/
│   │   └── simulator.json
│   └── migrations/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── compatibility/
│   ├── replay/
│   ├── hil/
│   ├── performance/
│   ├── support/
│   ├── data/
│   └── conformance/
│       ├── test_driver_call_protocol_conformance.py
│       ├── conftest.py
│       ├── data/
│       │   ├── method_inventory.yaml
│       │   ├── protocol_vectors.yaml
│       │   └── exclusions.yaml
│       └── expected/
│           └── response_schemas/
├── examples/
│   ├── README.md
│   ├── 01_*.py
│   ├── 02_*.py
│   ├── ...
│   └── 10_*.py
├── scripts/
│   ├── setup_venv.bat
│   ├── setup_venv.ps1
│   ├── setup_venv.sh
│   ├── run_example.bat
│   ├── run_example.ps1
│   ├── run_example.sh
│   ├── run_all_examples.bat
│   ├── run_all_examples.ps1
│   ├── run_all_examples.sh
│   ├── run_tests.bat
│   ├── run_tests.ps1
│   ├── run_tests.sh
│   ├── run_hil_tests.bat
│   ├── run_hil_tests.ps1
│   ├── run_hil_tests.sh
│   ├── run_call_protocol_conformance.bat
│   ├── run_call_protocol_conformance.ps1
│   ├── run_call_protocol_conformance.sh
│   ├── generate_api_docs.bat
│   ├── generate_api_docs.ps1
│   ├── generate_api_docs.sh
│   ├── validate_structure.py
│   ├── validate_ai_contract.py
│   ├── validate_call_protocol_conformance.py
│   ├── compare_public_api.py
│   └── build_release.py
├── history/
│   ├── README.md
│   └── v<version>.md
├── review/
│   ├── README.md
│   ├── v<version>_code_review.md
│   ├── v<version>_architecture_review.md
│   ├── v<version>_api_review.md
│   ├── v<version>_documentation_review.md
│   ├── v<version>_conformance_review.md
│   ├── v<version>_security_review.md
│   ├── v<version>_compatibility_review.md
│   ├── v<version>_release_readiness.md
│   ├── requirement_traceability.md
│   ├── known_risks.md
│   └── evidence/
│       └── v<version>/
├── guide/
│   ├── pycharm_setup.md
│   ├── windows_setup.md
│   ├── linux_setup.md
│   ├── hardware_setup.md
│   └── troubleshooting.md
├── docs/
│   ├── index.md
│   ├── installation.md
│   ├── quick_start.md
│   ├── api_reference.md
│   ├── architecture.md
│   ├── configuration.md
│   ├── compatibility.md
│   ├── migration.md
│   ├── support_policy.md
│   ├── examples.md
│   ├── safety.md
│   ├── call_protocol_conformance.md
│   ├── hardware_validation.md
│   ├── troubleshooting.md
│   └── release_notes.md
├── generated/
│   ├── api_reference/
│   └── api_manifest/
├── release/
│   ├── release_manifest.json
│   ├── sbom.spdx.json
│   └── SHA256SUMS
├── results/
│   └── .gitkeep
├── .github/
│   ├── CODEOWNERS
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   ├── dependabot.yml
│   └── workflows/
│       ├── ci.yml
│       ├── compatibility.yml
│       ├── security.yml
│       ├── pages.yml
│       ├── hil-manual.yml
│       └── release.yml
├── README.md
├── CHANGELOG.md
├── AGENTS.md
├── SUPPORT.md
├── GOVERNANCE.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── pyproject.toml
├── mkdocs.yml
├── MANIFEST.in
├── .pre-commit-config.yaml
├── noxfile.py or tox.ini
├── .gitignore
└── .editorconfig
```

### 6.1 Driver-package layout rule

A new LPDS driver shall use a `src/`-layout package: the installable driver package shall exist at `src/<driver_name>/` below the stable project root, never directly at the project root. LPDS-005 is the sole normative source for this rule; LPDS-001's illustrative package tree is a platform-level minimum only and reflects this layout.

The driver package shall be fully importable, constructible, and testable with only `src/<driver_name>/` on the Python path and no automation framework installed. It shall not import, reference, or depend on anything under `adapters/`.

Any framework adapter shall live under `adapters/<framework_name>/` (for example `adapters/robotframework/`, `adapters/pytest/`), as a sibling of `src/`, never nested inside the driver package. An adapter:

- shall depend on the driver package's public API only, typically via a normal Python import of the installed driver distribution;
- shall not be imported by, or referenced from, any file under `src/<driver_name>/`;
- shall contain no device, protocol, or transport logic of its own;
- may be distributed as an optional extra of the same distribution (for example `pip install <driver_name>[robotframework]`) or as a separate sibling distribution, provided the dependency direction above is preserved;
- is entirely optional — a conforming driver package may ship with zero adapters.

A reviewed legacy or upstream driver package may remain separate only when restructuring would create unacceptable compatibility risk. The architecture review shall document the exception, and the driver package shall remain the sole authority for device semantics and the public API.

### 6.2 Legacy layout migration exception

A reviewed driver that was originally built under an earlier flat (non-`src/`) layout may retain that layout only when migration would create unacceptable compatibility risk for existing consumers:

```text
hp34401a/
├── hp34401a/
└── hp34401a_dmm/
```

Requirements:

- `hp34401a/driver.py` (or a historical `library.py`) remains the sole authoritative public API surface;
- protocol and device logic shall not be duplicated between the legacy layout and any newly added adapter;
- both the legacy driver layout and any adapter shall be included in tests, manifests, SBOM, compatibility checks, and release review;
- the architecture review shall document the exception, the consumer-compatibility risk, and a target migration milestone to the `src/`-layout defined in §6.1.

---

## 7. Mandatory package-content baseline

Every public release and reviewable gate package shall contain current content for the following requirements.

| Requirement | Mandatory location | Release rule |
|---|---|---|
| Stable installable driver package | `src/<driver_name>/` | Imports without contacting hardware or requiring any automation framework |
| Change description | `history/` | Current revision has a complete chronological entry |
| Review evidence | `review/` | Current delta is reviewed; findings and residual risks are recorded |
| At least ten examples | `examples/` | Ten or more numbered, runnable plain-Python example scripts |
| Example and test runners | `scripts/` | Supported Windows and Linux execution paths exist |
| Current GitHub README | `README.md` | Matches package version, API, support, setup, and validation status |
| Current GitHub Pages | `docs/`, `mkdocs.yml`, `pages.yml` | Strict build passes and navigation is current |
| PyCharm and driver development guide | `guide/pycharm_setup.md` | Reproducible setup, run, debug, and troubleshooting steps |
| AI Driver Contract | `ai/ai_contract.yaml`, `ai_contract.lock` | Matches the released public API |
| Call/protocol conformance | `tests/conformance/` | LPDS-019 inventory, vectors, exclusions, and oracles are present |
| Deterministic offline validation | `transports/simulator.py` or `tests/replay/` | Normal and applicable failure behavior is testable without hardware |
| Requirements traceability | `review/requirement_traceability.md` | Requirements map to implementation, tests, docs, reviews, and evidence |
| Release integrity | `release/` | Manifest, SBOM, and checksums match final artifacts |
| AI coding guidance | `AGENTS.md` | Defines commands, sources of truth, constraints, and prohibited changes |

A public release is non-conformant when any mandatory path is missing, stale, contradictory, or represented only by an unexplained placeholder.

---

## 8. Installable Python package requirements

### 8.1 `driver.py`

`src/<driver_name>/driver.py` shall be the authoritative public driver API surface.

It shall:

- expose only intentional public methods, properties, and attributes;
- define public methods directly as documented class members, with no dependency on any automation-framework registration mechanism or decorator;
- document every public method, property, and constructor argument with docstrings and type hints suitable for generated API reference documentation;
- perform argument validation and conversion through shared converters;
- return plain Python types and values (no framework-specific value wrapping);
- map documented failures onto the driver's own exception hierarchy (LPDS-007);
- contain no hardware access during module import;
- support deterministic close, close-all, and context-manager behavior;
- expose driver and package metadata;
- remain synchronized with LPDS-017 and LPDS-019 inventories.

### 8.2 Layering

- `core/` shall own device semantics, state, safety policy, and high-level operations.
- `protocol/` shall own command construction, framing, parsing, checksums, and protocol-specific data conversion.
- `transports/` shall own VISA, serial, TCP/IP, USB, SDK, CAN, Modbus, or equivalent communication.
- `sessions.py` shall own aliases, active sessions, connection state, duplicate-alias policy, and close-all behavior.
- `converters.py` shall centralize boolean-like inputs, durations, enums, channels, paths, numeric limits, and structured values.
- `diagnostics.py` shall provide metadata, health, error, and evidence export support.
- `capabilities.py` shall expose machine-readable supported and unsupported capabilities.

The entire driver package under `src/<driver_name>/` — including `core/` and `protocol/` — shall remain usable, and fully testable, without importing or depending on any automation framework.

### 8.3 Package resources

Schemas, command maps, defaults, and other package data shall be stored under `resources/` and declared in `pyproject.toml` and `MANIFEST.in` when required.

The package shall not contain real credentials, private bench inventories, personal COM/VISA/LAN assignments, proprietary vendor installers, or undocumented binary dependencies.

### 8.4 Shared core dependency

Per LPDS-003, `src/<driver_name>/driver.py` shall build on the shared `lpds-core` package (`BaseInstrument` and its supporting infrastructure) rather than reimplementing connection, state, timeout, retry, logging, or diagnostics handling.

`pyproject.toml` shall declare a compatible `lpds-core` version range as a normal runtime dependency, for example:

```toml
[project]
dependencies = [
  "lpds-core>=1.0,<2.0",
]
```

A driver shall not vendor a modified private copy of `lpds-core` under the same identity. `release_manifest.yaml` shall record the effective `lpds-core` version the release was validated against, alongside the `lpds_compliance` block. Release validation shall fail when the installed `lpds-core` version falls outside the declared compatible range.

`lpds-core` itself is an ordinary LPDS-governed Python package: it is versioned and released through LPDS-011 independently of any driver, and a change to its own public API follows LPDS-011 §10's compatibility rules like any other public API change.

---

## 9. AI-contract requirements

Every driver shall include:

```text
ai/ai_contract.yaml
ai/ai_contract.lock
```

The contract shall comply with LPDS-017 and include the complete declared public API method semantics, including identity, mental model, states, resources, capabilities, errors, safety, setup/teardown, limitations, planning hints, verification objectives, and `UNKNOWN` handling.

The release build shall fail when:

- an exported public method is missing from the contract;
- a contracted method is absent from the driver;
- names, aliases, signatures, arguments, or return types differ;
- safety, timing, errors, or state requirements are stale;
- the lock file is invalid;
- contract and package versions disagree.

`ai/system_ai_contract.template.yaml` may provide an LPDS-018 integration template. It shall not claim actual bench wiring, DUT topology, or real laboratory resource assignments. The deployed bench contract belongs in the bench/test-system repository.

---

## 10. Test structure requirements

### 10.1 Test layers

| Directory | Purpose |
|---|---|
| `tests/unit/` | Pure Python logic, state, conversion, parser, model, and safety tests |
| `tests/conformance/` | LPDS-019 public API call and protocol-conformance suite (pytest-based, exercising the driver directly) |
| `tests/integration/` | Cross-module and transport integration without uncontrolled hardware |
| `tests/compatibility/` | Python and supported-backend compatibility |
| `tests/replay/` | Sanitized protocol replay and deterministic response tests |
| `tests/hil/` | Explicitly enabled physical-device tests |
| `tests/performance/` | Timing, stress, memory, soak, or concurrency tests where applicable |
| `tests/support/` | Fakes, spies, fixtures, simulators, and shared helpers |
| `tests/data/` | Deterministic vectors and sanitized captures |
| `adapters/<framework>/tests/` | Optional, thin adapter translation-correctness tests (framework binding only, not device logic) |

### 10.2 LPDS-019 conformance layout

The following structure is mandatory:

```text
tests/conformance/
├── test_driver_call_protocol_conformance.py
├── conftest.py
├── data/
│   ├── method_inventory.yaml
│   ├── protocol_vectors.yaml
│   └── exclusions.yaml
└── expected/
    └── response_schemas/
```

Every device-facing public method shall have a protocol vector or an approved exclusion. Every supported public method shall remain visible in the inventory.

The conformance runner shall create timestamped results under:

```text
results/call_protocol_conformance/<driver>/<timestamp>/
```

The result set shall contain LPDS-019-required pytest reports (for example JUnit XML and an HTML report), inventory, coverage matrix, vector results, outbound and inbound traces, environment data, device identity where available, exclusions, and Markdown summary.

### 10.3 HIL isolation

HIL tests shall:

- be disabled by default;
- require explicit enablement;
- use external resource variables or validated profiles;
- define allowed and prohibited operations;
- enforce safe limits;
- acquire required exclusive resource locks;
- record identity, firmware, transport, versions, and effective configuration;
- restore the documented safe state during teardown;
- never silently switch to simulation after a requested hardware connection fails.

---

## 11. Example requirements

Every public release and every Gate 4 or Gate 5 package shall include at least **ten complete, runnable plain-Python example scripts**.

Each example shall:

- be numbered with `01_`, `02_`, and so on;
- state purpose and prerequisites;
- state whether it uses simulation or hardware;
- define setup and teardown (for example via a context manager or `try`/`finally`);
- use only supported public methods;
- define required configuration or environment variables;
- avoid personal paths, real credentials, and private resource identifiers;
- define an expected result;
- leave the device in the documented safe state;
- be runnable by the generic example scripts (for example `python examples/03_read_measurement.py`).

The minimum example set should cover, where applicable:

1. package/import verification;
2. connection and identity;
3. status, health, or error queue;
4. basic configuration;
5. primary write/set operation;
6. query/read/measurement operation;
7. channel or resource selection;
8. validation failure and error handling;
9. recovery and safe cleanup;
10. realistic end-to-end workflow;
11. simulator use;
12. multiple sessions or bench integration.

`examples/README.md` shall index every example with its purpose, mode, prerequisites, required variables, expected result, and exact PowerShell, Batch where supported, and Linux shell command.

An adapter may additionally provide its own framework-specific example set (for example `.robot` suites under `adapters/robotframework/examples/`). Adapter examples supplement, but do not count toward, the ten-example minimum defined above, which applies to the plain-Python driver examples in `examples/`.

---

## 12. Script requirements

Scripts shall resolve the repository root from their own path and shall work regardless of the caller's current directory.

### 12.1 Setup scripts

`setup_venv.*` shall:

- create or reuse `.venv`;
- verify the supported Python version;
- install the selected dependency group;
- display the installed Python version (and, when an adapter dependency group was selected, the installed framework version);
- fail clearly on dependency or environment errors;
- never silently install proprietary vendor software.

### 12.2 Example runners

`run_example.*` shall accept an example number, basename, or relative file name. `run_all_examples.*` shall execute the approved example set.

Runners shall:

- provide help;
- list valid examples for invalid input;
- accept resources through parameters, variable files, or environment variables;
- create a results directory;
- preserve captured example output and, where an example produces structured logs or reports, preserve those artifacts;
- preserve the example process's exit code;
- return non-zero on failure.

### 12.3 Test runners

- `run_tests.*` shall execute approved software-only gates.
- `run_hil_tests.*` shall reject missing enablement, resources, or safety variables.
- `run_call_protocol_conformance.*` shall execute LPDS-019, preserve the pytest exit code, and print the timestamped result location.

An adapter directory may provide its own additional runner (for example to execute an installed Robot Framework adapter's `.robot` examples). Such adapter-specific runners are additional to, and do not replace, the driver-level runners above.

### 12.4 Validation and build scripts

- `validate_structure.py` shall validate LPDS-005.
- `validate_ai_contract.py` shall validate LPDS-017 and API synchronization.
- `validate_call_protocol_conformance.py` shall validate LPDS-019 inventory/vector completeness and expected schema structure.
- `compare_public_api.py` shall compare the current public API with the previous approved release.
- `generate_api_docs.*` shall generate the driver's public API reference (for example via Sphinx, pdoc, or mkdocstrings) and shall not open hardware.
- `build_release.py` shall run all mandatory release checks and generate the final ZIP.

---

## 13. History requirements

For every gate delivery and public release, `history/` shall contain one corresponding entry:

```text
history/vYY.PP.GG.md
history/vYY.RR.md
```

The entry shall record:

- version and date;
- phase and gate or public release number;
- user-visible changes;
- architecture and internal changes;
- public API method additions, changes, aliases, deprecations, and removals;
- protocol behavior changes;
- configuration and dependency changes;
- safety changes;
- bug fixes;
- tests and conformance vectors added or changed;
- examples, guides, README, and GitHub Pages updates;
- compatibility impact;
- hardware-validation status;
- known limitations.

Generic entries such as "updates" or "minor fixes" are insufficient.

---

## 14. Review requirements

Every delivered revision shall have review evidence for the current delta. Review records shall not be copied unchanged from the previous release.

Mandatory review dimensions are:

- code and functional correctness;
- architecture and layering;
- public API design;
- protocol mapping and parsing;
- LPDS-019 conformance;
- error handling and recovery;
- safety and cleanup;
- tests and evidence;
- documentation consistency;
- LPDS-017 contract consistency;
- compatibility and migration;
- security and secret handling;
- packaging and release readiness.

Each finding shall include:

- severity: `CRITICAL`, `MAJOR`, `MINOR`, or `NOTE`;
- affected file or area;
- evidence;
- impact;
- required or completed correction;
- validating test;
- residual risk;
- status.

`review/requirement_traceability.md` shall map requirements to implementation, tests, examples, documentation, review evidence, and hardware evidence where applicable.

`review/known_risks.md` shall identify unverified hardware behavior, protocol ambiguity, unsupported combinations, safety assumptions, deferred performance/concurrency work, dependency limitations, and approved structural exceptions.

LPDS-019 conformance evidence for an approved release should be retained under:

```text
review/evidence/v<version>/lpds019/
```

Generated runtime results may be copied into this location only after review and redaction.

---

## 15. Guide requirements

`guide/pycharm_setup.md` shall provide reproducible instructions for:

1. installing a supported Python version;
2. opening the stable `<driver_name>/` root in PyCharm;
3. creating and selecting `.venv`;
4. installing the driver project in editable mode;
5. installing development, hardware, documentation, and (where applicable) adapter extras;
6. configuring the IDE's Python interpreter and type-checking support for the driver package;
7. where an adapter is installed, configuring any IDE support the adapter's framework needs (for example associating `.robot` and `.resource` files for the Robot Framework adapter);
8. creating a run/debug configuration for a plain Python example script;
9. supplying serial, VISA, LAN, USB, SDK, or other resource variables;
10. running a simulated example;
11. running a hardware example;
12. running the LPDS-019 conformance suite;
13. locating logs, traces, and evidence;
14. debugging the driver's Python code directly, with no automation-framework indirection;
15. troubleshooting imports, permissions, ports, drivers, vendor runtimes, and environment variables.

Windows and Linux setup shall be covered either in this guide or in linked platform-specific guides.

---

## 16. README and GitHub Pages requirements

### 16.1 Root README

`README.md` shall include:

- project purpose;
- supported models and firmware status;
- public package and version identity;
- supported Python versions (and, for each published adapter, its supported framework versions);
- supported transports;
- installation;
- minimal plain-Python usage example;
- example-run commands;
- major public API method groups;
- available adapters, if any, and how to install them;
- safety principles;
- simulator status;
- LPDS-019 conformance status;
- hardware-validation status;
- known limitations;
- compatibility and support status;
- links to the generated API reference, GitHub Pages, guides, examples, history, and reviews;
- license and support path.

The README shall match the packaged revision and shall not claim HIL, conformance, compatibility, or safety evidence that has not been executed and reviewed.

### 16.2 GitHub Pages

GitHub Pages sources shall be stored under `docs/` and built through `mkdocs.yml` and `.github/workflows/pages.yml`.

The site shall include:

- installation and quick start;
- current public API reference or a generated API-reference link;
- architecture and configuration, including the driver/adapter boundary;
- examples;
- safety and limitations;
- compatibility and migration;
- LPDS-019 call/protocol conformance execution;
- hardware-validation status;
- troubleshooting;
- release notes.

A strict documentation build and internal-link validation shall pass before release.

---

## 17. Configuration and resource requirements

`config/` shall contain safe defaults, examples, schema, and HIL resource templates. Per LPDS-014, JSON (`schema.json`, `schema.lock`, `default.json`, `example.json`) is the canonical, authoritative configuration format; `hil_resources.example.yaml` remains YAML because it is a bench/HIL resource template outside the LPDS-014 configuration-schema domain, not a driver configuration document.

Requirements:

- real credentials and private laboratory inventory shall not be committed;
- examples shall use placeholders;
- unsafe outputs shall not be enabled by default;
- units shall be explicit;
- configuration precedence shall be documented;
- effective configuration shall be exportable with secrets redacted;
- HIL resource templates shall identify aliases, transport fields, safety limits, and exclusivity rules without providing a real bench definition.

An adapter directory (for example `adapters/robotframework/resources/`) may provide reusable, framework-specific resource and variable-template files for that adapter. Such files shall not duplicate the authoritative Python public API defined by the driver package.

---

## 18. Repository and workflow requirements

The repository shall provide:

- CI for structure, import, format, lint, typing, unit, conformance, replay, examples, docs, package builds, and clean-install smoke tests, plus adapter translation tests for any adapter included in the repository;
- compatibility testing across the supported Python range (and, for each published adapter, its supported framework version range);
- GitHub Pages build/deployment;
- manually controlled or protected HIL execution;
- security and dependency checks;
- release automation after mandatory gates pass.

Public workflow actions shall be pinned to immutable commit SHAs or use an approved equivalent control. Workflow permissions shall be explicit and least-privilege.

HIL workflows shall use protected configuration and exclusive resource locking. They shall not run on uncontrolled public runners.

---

## 19. Release-integrity requirements

Every approved public release shall include or generate:

```text
release/release_manifest.json
release/sbom.spdx.json
release/SHA256SUMS
```

The manifest shall identify at least:

- driver name and version;
- ZIP filename;
- internal root;
- Python distribution and import names;
- supported Python version range (and, for each included adapter, its supported framework version range);
- source revision;
- build environment;
- included history and review records;
- LPDS-017 validation status;
- LPDS-019 validation and execution status;
- HIL status;
- generated artifact hashes.

The SBOM shall cover packaged runtime dependencies and bundled upstream packages. Checksums shall be generated from the final immutable artifacts, not an earlier build.

A release provenance or attestation should be generated when supported by the hosting platform.

---

## 20. Runtime outputs and release exclusions

The following shall not be included in the public driver ZIP:

- `.venv/`;
- `__pycache__/` and caches;
- IDE metadata;
- build working directories;
- local test/example run outputs (for example pytest cache, coverage data, captured logs);
- active HIL lock files;
- coverage working files;
- temporary files;
- local configuration overrides;
- credentials, tokens, certificates, private keys, or secrets;
- real bench inventory files;
- proprietary vendor installers or runtimes without redistribution approval;
- unreviewed binary captures;
- nested prior release ZIPs;
- unrelated device manuals when redistribution is not permitted.

`results/` may remain as an empty runtime destination containing `.gitkeep`. Generated results shall be excluded unless intentionally copied, reviewed, sanitized, and retained as release evidence under `review/evidence/`.

A separate evidence archive may be published. It shall have an unambiguous name and shall not be confused with the driver ZIP.

---

## 21. Lifecycle maintenance rules

### Gate 1 — Architecture and skeleton

Create:

- canonical structure;
- installable driver package skeleton;
- public driver API skeleton;
- AI contract skeleton;
- conformance inventory/vector schema;
- simulator or protocol-observation strategy;
- initial README, guide, history, and review files.

### Gate 2 — Core implementation

Update:

- core functionality;
- public API methods;
- unit and conformance tests;
- initial examples;
- LPDS-017 capabilities;
- LPDS-019 vectors for implemented methods;
- history and reviews.

### Gate 3 — Extended features

Update:

- advanced features and edge cases;
- recovery and diagnostics;
- capability metadata;
- conformance vectors and error cases;
- compatibility and migration information;
- examples and documentation.

### Gate 4 — Tests and documentation

Complete:

- unit, conformance, integration, replay, and applicable HIL tests, plus adapter translation tests for any adapter included in this revision;
- complete LPDS-019 suite execution where prerequisites exist;
- ten or more verified examples;
- README, guides, generated API reference, and GitHub Pages;
- traceability and known risks.

### Gate 5 — Review and release

Complete:

- code, architecture, API, documentation, conformance, compatibility, security, and release reviews;
- correction of Critical findings;
- resolution or formal acceptance of Major findings;
- current history and changelog;
- final manifests, SBOM, checksums, and package validation;
- correctly named ZIP with one stable root.

No phase shall pass Gate 5 without current LPDS-019 conformance status and evidence. A prerequisite-based SKIP or approved EXCLUDED item shall remain visible and shall not be presented as PASS.

---

## 22. Release build workflow

`build_release.py` shall perform or invoke the following sequence:

1. resolve and validate version identity;
2. validate mandatory structure;
3. validate prohibited content and secret patterns;
4. validate LPDS-017 contract and lock;
5. generate and validate public method inventory;
6. validate LPDS-019 vector and exclusion coverage;
7. run formatting, linting, typing, and compilation checks;
8. run unit, conformance, integration, replay, and compatibility tests, plus adapter translation tests for any included adapter;
9. run LPDS-019 conformance in the approved software profile;
10. run or import reviewed HIL evidence when required and available;
11. execute or dry-run all examples through packaged runners;
12. compare the public API with the previous approved release;
13. build the generated API reference and GitHub Pages in strict mode;
14. build wheel and source distribution;
15. perform clean-install smoke tests from built artifacts;
16. generate release manifest and SBOM;
17. assemble the ZIP with exactly one stable internal root;
18. reject forbidden files and nested archives;
19. calculate final checksums;
20. update release-readiness evidence;
21. fail when any mandatory condition fails.

The final archive shall be validated from the packaged bytes, not only from the working tree.

---

## 23. Structure conformance checks

`validate_structure.py` and CI shall verify at minimum:

- the archive name matches approved release metadata;
- the ZIP contains exactly one top-level folder;
- the top-level folder is `<driver_name>/`;
- all mandatory directories and files exist;
- the driver package is present under the mandated `src/<driver_name>/` layout;
- the Python driver package imports without hardware access and without importing any automation framework;
- API reference generation succeeds without hardware access;
- at least ten numbered runnable plain-Python examples exist;
- every example is indexed and selectable through generic runners;
- Windows and Linux scripts exist;
- LPDS-017 files exist and validate;
- LPDS-019 conformance structure exists;
- all public methods are inventoried;
- every device-facing method has a vector or approved exclusion;
- history and review records exist for the current revision;
- each current change is covered by review evidence;
- README, docs, examples, AI contract, and API version references agree;
- GitHub Pages strict build passes;
- the PyCharm/driver-development guide uses current names and commands;
- no forbidden files, secrets, active locks, or nested ZIPs are packaged;
- release manifest, SBOM, and checksums match final artifacts;
- public API changes are classified and documented;
- any included adapter depends only on the driver package's public API and introduces no device logic of its own.

---

## 24. Minimum release acceptance criteria

A public driver release passes LPDS-005 only when:

1. the ZIP name follows `<driver_name>_v<year>.<release>.zip`;
2. the ZIP contains exactly one stable `<driver_name>/` root;
3. the canonical source, AI, configuration, test, conformance, example, script, history, review, guide, documentation, and release-integrity content exists;
4. the package imports without connecting to hardware or requiring any automation framework;
5. the driver package's public API can be imported and enumerated using plain Python alone; when an adapter is included, that adapter can load and expose the same public API to its target framework;
6. LPDS-017 matches the released public API;
7. LPDS-019 inventory and vector coverage are complete or approved exclusions are documented;
8. applicable mandatory LPDS-019 vectors pass and evidence is traceable;
9. at least ten current runnable plain-Python examples are included;
10. example and test runners work on supported Windows and Linux environments;
11. README, guides, GitHub Pages, generated API reference, examples, and code describe the same revision;
12. history describes every delivered change;
13. review evidence covers every delivered change;
14. no Critical review finding remains open;
15. Major findings are corrected or formally accepted with owner, risk, and limitation;
16. version identity is consistent across package, documentation, contracts, manifests, and archive;
17. prohibited runtime files and secrets are absent;
18. release manifest, SBOM, and checksums match the final package;
19. installation from the built distribution and execution of the declared basic workflow are reproducible;
20. hardware-validation status is explicit and is not overstated.

---

## 25. Failure conditions

LPDS-005 conformance shall fail when any of the following applies:

- incorrect ZIP naming;
- multiple ZIP top-level entries;
- versioned internal root;
- missing mandatory path;
- fewer than ten valid examples without an approved scope exception;
- examples cannot be run through packaged scripts;
- stale or contradictory README, guide, docs, examples, AI contract, or version metadata;
- missing current history or review record;
- a current change is absent from review evidence;
- package import contacts hardware, requires an automation framework, or fails in a clean environment;
- LPDS-017 files are missing or do not match the API;
- LPDS-019 conformance structure, inventory, vectors, exclusions, or runner is missing;
- a public method is omitted from inventory;
- a device-facing method lacks a protocol vector and approved exclusion;
- required test or conformance evidence is represented as passed when not executed;
- GitHub Pages cannot build;
- required setup guidance is missing;
- secrets, active locks, personal resource assignments, caches, local results, or nested ZIPs are included;
- release manifest, SBOM, or checksums are missing or inconsistent;
- unresolved Critical findings remain;
- an undocumented breaking API change is included;
- an adapter contains device logic that duplicates or diverges from the driver's public API.

---

## 26. Minimum definition of done

LPDS-005 is complete for a driver revision when:

- the required repository and package structure exists;
- naming and version identity are consistent;
- the driver package is importable and its public API is discoverable using plain Python alone; any included adapter is separately importable and depends only on the driver's public API;
- LPDS-017 files are complete and synchronized;
- LPDS-019 conformance artifacts and runners are complete;
- examples, scripts, guides, README, generated API reference, and GitHub Pages are current;
- history, review, traceability, and risk records are current;
- software-only tests and required conformance checks pass;
- hardware status is explicitly recorded;
- release-integrity artifacts are generated from the final package;
- the final ZIP validates with one stable internal root;
- all acceptance criteria in Section 24 pass.

---

## 27. Review checklist

1. Is the driver identifier stable and valid?
2. Does the public ZIP follow the approved naming pattern?
3. Does the ZIP contain exactly one `<driver_name>/` root?
4. Is the internal root version-independent?
5. Does the project use the canonical `src/<driver_name>/` driver-package layout, with any adapter clearly separated under `adapters/`?
6. Is `driver.py` the authoritative public driver API surface, importable and testable without any automation framework?
7. Are core, protocol, and transport responsibilities separated?
8. Does package import avoid hardware activity and automation-framework dependency?
9. Are LPDS-017 contract and lock files present and synchronized?
10. Is the LPDS-018 file clearly a template rather than a claimed bench definition?
11. Is the complete LPDS-019 conformance tree present?
12. Are all public methods inventoried?
13. Does every device-facing method have a vector or approved exclusion?
14. Are at least ten numbered runnable plain-Python examples present?
15. Can each example be run with the packaged scripts?
16. Are Windows and Linux paths supported?
17. Are history entries complete for the current delta?
18. Does review evidence cover every current change?
19. Are requirement traceability and known risks current?
20. Are README, guides, GitHub Pages, generated API reference, examples, and code consistent?
21. Are HIL tests isolated and explicitly enabled?
22. Are runtime outputs and secrets excluded?
23. Do manifest, SBOM, and checksums match the final artifacts?
24. Are Critical findings closed and Major findings resolved or formally accepted?
25. Can the package be clean-installed and its basic workflow reproduced?
26. Does any included adapter depend only on the driver's public API, with no device logic of its own?

---

## 28. Goal

Provide one predictable, reviewable, replaceable, installable, testable, documented, and evidence-backed package structure for every LPDS Python instrument driver.

The resulting package shall allow a developer, tester, reviewer, CI system, or AI agent to locate the public API, implementation layers, any adapters, AI semantics, conformance vectors, examples, setup instructions, change records, review evidence, and release-integrity records without reverse-engineering the project.

---

## Appendix A — Changes from version 1.2

Version 1.3:

- renames the document emphasis from project structure to the broader Driver Package Specification;
- aligns public release naming with the current `<driver_name>_v<year>.<release>.zip` project rule;
- adds the mandatory LPDS-019 conformance tree to the canonical package layout;
- adds cross-platform LPDS-019 runners and static conformance validation;
- adds conformance review and reviewed conformance-evidence locations;
- adds `docs/call_protocol_conformance.md`;
- requires conformance inventory and vector validation during release building;
- requires LPDS-019 status in README, manifests, Gate 5 review, and release acceptance;
- clarifies the boundary between repository files, public package content, runtime results, and reviewed release evidence;
- retains the stable internal root, ten-example minimum, current README/GitHub Pages, PyCharm guide, history, review, AI contract, simulator/replay, governance, compatibility, and release-integrity requirements.
