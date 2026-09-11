# LPDS-001 — Platform Requirements

## Overall Project Goals and Architecture

**Version:** 1.2
**Document ID:** LPDS-001
**Status:** Review candidate
**Applies to:** All LPDS Python instrument driver projects, shared platform components, protocol simulators, examples, and validation suites

---

## 1. Purpose

This specification defines the top-level goals and architecture for the LPDS Lab pyDrivers Platform: a hub of independently maintained Python instrument-driver repositories, each publishable and useful on its own by one person or a small team.

LPDS-001 is the parent platform specification. It establishes the common model that all device-specific drivers and all subordinate LPDS specifications shall follow.

**LPDS-001-PUR-001 — Platform purpose**
The platform shall provide a consistent, practical method to:

1. implement Python drivers for laboratory, industrial, embedded, and test equipment;
2. expose those drivers through a stable, framework-independent public Python API, with optional adapters exposing that same API to specific automation frameworks;
3. describe each driver in a machine-readable form that an AI agent can safely use;
4. verify that each public driver method reaches the intended device protocol operation;
5. generate repeatable tests, examples, and documentation;
6. preserve compatibility and maintainability across driver revisions.

---

## 2. Platform Vision

**LPDS-001-VIS-001 — Coherent driver ecosystem**
The LPDS platform shall make heterogeneous hardware drivers behave as members of one coherent ecosystem rather than as unrelated scripts or vendor-specific libraries.

A user, test developer, or AI agent shall be able to:

- identify a driver and its supported device;
- install the driver package in a clean declared environment;
- connect to the device through a declared transport profile;
- discover and call documented public Python methods, directly or through a framework adapter;
- understand method preconditions, postconditions, side effects, timing, safety, and return values;
- execute examples and conformance tests;
- update to a compatible revision without unnecessary changes to existing tests or adapters.

**LPDS-001-VIS-002 — Platform priorities**
The platform shall prioritize correctness, deterministic behaviour, safe hardware control, finite execution, clear failure reporting, reproducibility, and long-term API stability.

---

## 3. Driver vs Adapter Architecture

This section states the architectural thesis that every subordinate LPDS specification builds on.

**LPDS-001-DA-001 — Driver definition**
A **driver** is a plain, framework-independent Python class exposing a documented public API (typed methods, properties, docstrings) per LPDS-002. A driver shall:

- be fully constructible, controllable, and testable from a plain Python or pytest session with **no** test-automation framework installed;
- not import, subclass, decorate with, or otherwise depend on a pytest plugin, or any other test-automation or GUI framework;
- express all device semantics, protocol handling, transport I/O, state, error handling, and logging entirely in terms of its own public Python API and LPDS-003's shared base class.

**LPDS-001-DA-002 — Adapter definition**
An **adapter** is a separate, thin translation layer that exposes an already-verified driver's public API to one specific automation framework or interface: pytest fixtures, a CLI, a REST endpoint, a GUI test bench, or similar. An adapter shall:

- contain no device logic, protocol logic, or transport logic of its own;
- translate calls and results between its framework and the driver's public API only;
- be written, versioned, tested, and released independently of the driver and of any other adapter for the same driver;
- be discoverable independently of the driver it targets, per LPDS-015.

The same driver may have zero, one, or several adapters at once. A driver that has no adapter at all is still complete and releasable: it is fully usable directly from Python.

**LPDS-001-DA-003 — Order of work**
A driver should be designed, implemented, and verified on its own public Python API — unit tests against a simulated transport, then hardware-in-the-loop tests against real equipment per LPDS-009 — before any adapter for it is written. An adapter is verified afterward and separately, using thin translation-correctness tests rather than device-logic tests, per LPDS-019's adapter conformance appendix.

**LPDS-001-DA-004 — Why this separation exists**
This separation exists so that:

1. a driver can be trusted and used without requiring any particular automation framework to be installed, working, or even chosen yet;
2. the same verified driver logic can be reused unchanged by multiple frameworks and consumers (pytest, a CLI, a REST layer, an AI agent calling Python directly);
3. a defect is never simultaneously a device-logic defect and a framework-translation defect — it is always attributable to exactly one side of the boundary;
4. adding, replacing, or dropping support for an automation framework never requires touching device logic.

Every subordinate LPDS specification that historically assumed one specific automation framework was the sole consumer of a driver instead treats that framework, where relevant, as one example adapter among possible others.

---

## 4. Project Goals

**LPDS-001-GOAL-001 — Primary platform goals**
The LPDS platform shall:

1. provide a unified, framework-independent Python driver architecture;
2. standardize public API design;
3. support real hardware and approved protocol simulators;
4. separate test intent from device semantics, protocol implementation, and transport I/O;
5. provide machine-readable contracts for AI-assisted planning and test generation;
6. provide objective callability and protocol-conformance evidence;
7. support small, reviewable, incremental delivery.

**LPDS-001-GOAL-002 — Released-driver qualities**
A released driver shall be:

- predictable;
- testable;
- maintainable;
- documented;
- installable;
- recoverable after supported communication faults;
- safe for its declared operating profile;
- understandable without reading the complete source code;
- usable from plain Python with no automation framework installed, and additionally usable through any adapter provided for it.

**LPDS-001-GOAL-003 — AI planning support**
The platform shall provide enough structured information for an AI agent to:

- select the correct driver and method;
- construct valid method arguments;
- satisfy connection and state preconditions;
- plan setup, execution, verification, recovery, and teardown;
- interpret return values and failures;
- identify unknown, ambiguous, or unsupported operations instead of inventing behaviour.

---

## 5. Scope Boundary

### 5.1 In scope

**LPDS-001-SCP-001 — Platform scope**
LPDS-001 covers:

- overall platform architecture, including the driver/adapter split;
- mandatory driver layers and responsibility boundaries;
- canonical package and repository model;
- common driver lifecycle capability profile;
- Python driver architecture principles;
- transport and protocol abstraction principles;
- AI driver contract integration;
- testing and conformance integration;
- safety, state ownership, cancellation, and resource-control principles;
- documentation and example expectations;
- compatibility rules.

### 5.2 Out of scope

LPDS-001 does not define:

- the complete public API for a specific device;
- vendor-specific command syntax;
- detailed electrical accuracy requirements;
- device calibration procedures;
- a specific simulator implementation;
- a specific CI service vendor or hosting provider;
- detailed requirements assigned to subordinate LPDS specifications.

Device-specific requirements shall be defined in the driver's own documentation, AI contract, protocol vectors, and applicable subordinate LPDS specifications.

---

## 6. Normative Terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement, worth deviating from when there's a good reason — document the reason if it isn't obvious;
- **may** — permitted implementation choice;
- **driver** — the complete LPDS package exposing a device or logical hardware service through a plain, framework-independent public Python API, per §3;
- **driver core** — Python implementation containing device semantics, entirely independent of any automation framework;
- **adapter** — a separate, thin translation layer exposing a driver's public API to one specific automation framework or interface, per §3;
- **transport** — VISA, serial, TCP, UDP, HTTP, USB, CAN, Modbus, vendor SDK, GPIO SDK, or equivalent communication mechanism;
- **protocol operation** — command, query, request, frame, transaction, or SDK call sent toward the device boundary;
- **AI Driver Contract** — the single-driver machine-readable contract defined by LPDS-017;
- **conformance evidence** — recorded proof that a public method call produced the expected protocol behaviour;
- **approved simulator** — a versioned simulator operating at the protocol boundary used by the real driver connection;
- **public method** — a method intentionally exported as part of the driver's public API;
- **canonical method name** — the preferred public name for a capability;
- **alias** — an additional supported public name mapping to the same declared capability;
- **release package** — the distributable archive containing the complete driver project;
- **internal root folder** — the stable top-level folder contained inside the release archive.

---

## 7. Requirement Identification

**LPDS-001-REQ-001 — Stable requirement identifiers**
Where this document and its siblings state a specific mandatory requirement, it carries a stable identifier in the form `LPDS-001-<AREA>-<NUMBER>` (for example, `LPDS-001-ARCH-001`) so other documents and driver reviews can reference it precisely. A published identifier is not reused for a different requirement; requirements removed in a later revision are just dropped, not reassigned.

---

## 8. Document Precedence and Ownership

### 8.1 Precedence

**LPDS-001-GOV-001 — Document precedence**
Unless legal, regulatory, or safety obligations require stricter controls, LPDS requirements are interpreted using this hierarchy: applicable law/safety requirements, then LPDS-001, then the applicable subordinate LPDS specification, then the device-specific driver's own documented decisions. A lower-level document may add stricter requirements but shall not silently weaken a higher-level one.

### 8.2 Subject ownership

**LPDS-001-GOV-002 — Specification ownership**
LPDS-001 defines platform-level intent. Detailed normative ownership is delegated as follows:

| Document | Authoritative subject |
|---|---|
| LPDS-001 | Platform goals, architecture, driver/adapter split |
| LPDS-002 | Mandatory public API, method naming, signatures, compatibility rules |
| LPDS-003 | BaseInstrument and common base-class design |
| LPDS-004 | Transport abstraction and supported transport behaviour |
| LPDS-005 | Driver package and repository structure |
| LPDS-006 | Python coding, typing, documentation, and logging standard |
| LPDS-007 | Exception taxonomy, diagnostics, and error representation |
| LPDS-008 | Logging and evidence schema |
| LPDS-009 | Unit, simulator, integration, hardware, and adapter-conformance testing |
| LPDS-010 | Driver review checklist |
| LPDS-011 | Versioning, changelog, packaging, and release process |
| LPDS-013 | Capability discovery model |
| LPDS-014 | Configuration import, export, and validation |
| LPDS-015 | Plugin and adapter architecture and dynamic discovery |
| LPDS-017 | AI-readable contract for one driver |
| LPDS-019 | Public API callability and driver-to-device protocol conformance |
| LPDS-020 | Phase-and-gate implementation workflow |

Where a subject has a listed owner, LPDS-001 states the platform expectation and the subordinate specification states the detailed implementation and verification rules.

### 8.3 Conflicts

**LPDS-001-GOV-003 — Conflict handling**
A conflict between documents should be fixed by correcting the conflicting document. Where that isn't immediately possible, document the interpretation you're using and why, close to the code it affects (a code comment, a note in the driver's README, or a CHANGELOG entry) rather than leaving the contradiction silent.

---

## 9. Driver Status

**LPDS-001-STATUS-001 — Status labels**
Every driver repository declares one status in its README, matching the hub's existing convention:

| Status | Meaning |
|---|---|
| `wip` | In development. Incomplete is fine; say what's missing. |
| `untested` | Feature-complete against its declared scope and passes LPDS-019 conformance against a simulator, but has not been verified against real hardware yet. |
| `stable` | Verified end-to-end: LPDS-019 conformance passes against real hardware, examples run, documentation is current. |

There is no formal approval process or release authority — the maintainer sets and updates this label honestly. A driver can move backward (e.g. `stable` → `wip`) if a regression is found; say so in the CHANGELOG.

A driver that depends on hardware you don't personally have access to may reasonably stay `untested` indefinitely — that's a legitimate, permanent state, not a defect.

---

## 10. Architectural Principles

All LPDS drivers should follow these principles.

**LPDS-001-ARCH-001 — Stable public API**
Consumers — tests, adapters, AI agents, or other code — depend on the driver's declared public API, not on private methods, transport internals, or vendor-library implementation details.

**LPDS-001-ARCH-002 — Separation of concerns**
Framework adapter translation (where present), device semantics, protocol serialization, transport I/O, and configuration are separated enough to permit focused testing and maintenance.

**LPDS-001-ARCH-003 — Explicit state**
Connection state, selected channel, active mode, output state, and other operational state are explicit and queryable where applicable.

**LPDS-001-ARCH-004 — Deterministic behaviour**
Given equivalent valid preconditions, arguments, device response, and configuration, a method produces the same protocol intent and an equivalent result.

**LPDS-001-ARCH-005 — Visible failure**
A driver does not report success when a required protocol operation, response, validation, safety check, or state transition failed.

**LPDS-001-ARCH-006 — Safe default behaviour**
Initial state, disconnect behaviour, error recovery, and cancellation prefer the safest declared device state.

**LPDS-001-ARCH-007 — Compatibility first**
Existing public methods, arguments, defaults, aliases, return schemas, error codes, and documented behaviour remain compatible unless a breaking change is deliberately made and versioned accordingly (LPDS-011 §10).

**LPDS-001-ARCH-008 — AI-readable semantics**
Machine-readable contracts describe operational meaning, not merely duplicate function names and argument lists.

**LPDS-001-ARCH-009 — Framework independence of the driver**
A driver does not import, subclass, or otherwise depend on any automation framework. Any framework-specific behaviour lives exclusively in a separate adapter per §3.

---

## 11. Logical Platform Architecture

The normative execution path is:

```text
Test requirement or operator intent
                ↓
pytest suite / AI-generated plan / framework adapter's native test format
                ↓
Framework adapter (optional) — translation only, no device logic
                ↓
Driver's public Python API
                ↓
Driver service and device-semantics layer
                ↓
Protocol adapter / command builder / SDK adapter
                ↓
Transport boundary
                ↓
Physical device or approved protocol simulator
                ↓
Raw device response, acknowledgement, or fault
                ↓
Transport and protocol parsing
                ↓
Typed driver result or documented exception
                ↓
Result, translated by any adapter present into its framework's native form
```

The normative planning path is:

```text
LPDS-017 AI Driver Contract
                +
Test requirements and safety constraints
                ↓
AI planner or human test designer
                ↓
Test suite calling the driver's public API directly, or through a declared adapter
```

The normative verification path is:

```text
Driver public API inventory
                ↓
LPDS-019 call and protocol conformance suite
                ↓
Observed outbound and inbound protocol evidence
                ↓
Coverage matrix and test reports
```

---

## 12. Architectural Layers

### 12.1 Test and orchestration layer

Express test intent in pytest or, when a framework adapter is used, in that framework's native format. Coordinate setup, actions, measurements, verification, cancellation, and teardown. Avoid direct use of private driver implementation details.

### 12.2 Framework adapter layer (optional)

When an adapter is present, it translates one automation framework's calling convention (pytest fixtures, a CLI, a REST endpoint, ...) into calls on the driver's public API, and translates the driver's return values and raised exceptions back into that framework's native success/failure representation. It adds no device logic, protocol logic, or transport logic of its own, and remains a separate, independently versioned component per LPDS-015.

A driver with no adapter simply skips this layer; test and orchestration code calls the public Python API layer directly.

### 12.3 Public Python API layer

Exposes public methods intentionally, with stable method names and signatures per LPDS-002. Validates caller-facing arguments, converts results into stable documented values, and translates internal exceptions into the documented `DriverError` hierarchy per LPDS-007. Does not silently alter device semantics and does not depend on any automation framework.

### 12.4 Driver service and device-semantics layer

Implements device capabilities and state transitions, enforces device-level preconditions and ranges, applies stabilization/retry/timeout/cancellation/recovery policy. Remains fully independent of any automation framework to permit focused Python testing.

### 12.5 Protocol adapter layer

(Not to be confused with the framework adapter layer in §12.2 — this layer adapts between driver semantics and device *protocol*, not between the driver and an automation framework.)

Maps semantic driver operations to device protocol operations: serializes commands/queries/frames, applies addressing/units/encoding/framing/checksums, parses raw protocol responses, and exposes protocol evidence hooks needed by LPDS-019.

### 12.6 Transport layer

Opens, maintains, and closes communication sessions; implements read/write/query/transaction primitives; applies timeouts; exposes transport errors without misreporting success; prevents indefinite blocking.

### 12.7 Device or simulator layer

The driver may communicate with a physical device, an approved protocol simulator, an instrumented proxy, a vendor SDK connected to hardware, or a transport spy. A simulator used for conformance preserves the protocol boundary relevant to the real connection.

### 12.8 Metadata and contract layer

Describes driver identity and capabilities: preconditions, postconditions, side effects, risk, timing, retry, and resources, kept synchronized with the released public API.

### 12.9 Validation and evidence layer

Executes unit, integration, simulator, real-device, and conformance tests, plus adapter-translation tests where an adapter exists, and generates coverage/protocol evidence.

---

## 13. Component Responsibility Rules

**LPDS-001-CMP-001 — Public API use in tests**
Test suites and adapters use the driver's public API. Raw protocol construction is reserved for dedicated protocol-validation or device-development tests where that purpose is explicit.

**LPDS-001-CMP-002 — Test-suite independence**
A driver does not require hidden variables or execution ordering that exists only in a particular example or test suite.

**LPDS-001-CMP-003 — Authoritative protocol knowledge**
Command construction and response parsing have an authoritative implementation location, not duplicated inconsistently across public methods, tests, or examples.

**LPDS-001-CMP-004 — Externalized configuration**
Addresses, ports, serial numbers, channels, timeouts, and safety limits are not hard-coded into reusable driver logic except as documented device defaults.

**LPDS-001-CMP-005 — Enforceable safety**
Safety rules that can't actually be enforced in code are documented as advisory, not stated as if they were guaranteed.

**LPDS-001-CMP-006 — Non-intrusive evidence hooks**
Tracing, logging, or protocol observation does not intentionally modify the semantic operation being verified.

---

## 14. Canonical Driver Package Model

LPDS-005 is the sole normative source for the exact repository structure; this section states the platform-level minimum only.

### 14.1 Release naming

**LPDS-001-PKG-001 — Release identity**
A driver release uses a lowercase, filesystem-safe `<driver_name>` and a `vYY.RR` version per LPDS-011 (for example `keysight34970_v26.05.zip`), with the archive's internal root folder (`<driver_name>/`) staying stable across releases even as the outer archive name changes.

### 14.2 Minimum package content

**LPDS-001-PKG-002 — Mandatory paths**
LPDS-005 mandates a `src/`-layout: the installable driver package lives at `src/<driver_name>/`, with any framework adapter kept in a separate, optional `adapters/<framework_name>/` directory that depends on the driver package but never the reverse. Every driver package contains at least:

```text
<driver_name>/
├── README.md
├── LICENSE
├── pyproject.toml
├── src/<driver_name>/
├── adapters/            (optional, one subfolder per framework adapter)
├── ai/
├── tests/
└── examples/
```

`docs/`, `guide/`, `history/`, and `release/` (with a release manifest, and optionally checksums/SBOM/traceability records for a driver mature enough to want them) are recommended as the project grows past its first release — see LPDS-005 §6 for the full recommended layout.

---

## 15. Release Manifest

**LPDS-001-MAN-001 — Release manifest**
A driver release should provide `release/release_manifest.yaml` as a machine-readable package index, containing at least:

```yaml
schema_version: "1.0"
driver_name: keysight34970
release_version: "26.05"
api_version: "1.0"
status: stable
driver_import_path: keysight34970.driver
driver_class: Keysight34970Driver

supported_devices: []
supported_transports: []
python_versions: []
adapters: []            # e.g. [{name: pytest, version: "1.0"}]

conformance:
  result: PASS
  evidence_path: tests/conformance/results
```

Checksums, an SBOM, and a requirements-traceability record are useful once a driver has external consumers depending on supply-chain guarantees, but are not expected for a typical single-maintainer driver — add them if and when they're actually needed.

---

## 16. Public Python API Requirements

### 16.1 Discoverability

**LPDS-001-API-001 — Discoverable public API**
The driver package imports successfully and exposes its intended public methods through standard Python introspection (`dir()`, `help()`, type stubs). Private helpers don't become public methods accidentally (leading underscore, or an equivalent deterministic convention per LPDS-002).

### 16.2 Canonical common lifecycle profile

**LPDS-001-API-002 — Common lifecycle capability names**
When the corresponding capability is supported, the canonical public method name is:

```text
connect
disconnect
is_connected
get_identity
get_driver_information
get_device_errors
clear_device_errors
reset_device
enter_safe_state
```

A device that doesn't support one of these may omit it. Detailed signatures and compatibility rules belong to LPDS-002.

### 16.3 Naming, signatures, return values

**LPDS-001-API-003 — Naming and signatures**
Public method names use `snake_case`, describe user intent, and remain unique. Every public method declares required/optional arguments with type hints, units where applicable, return type, connection/state preconditions, side effects, and timeout/cancellation behaviour where applicable. Return values use stable, documented Python types.

### 16.4 Connection lifecycle, idempotency, deprecation

**LPDS-001-API-004 — Connection lifecycle**
Each connection-capable driver defines and tests connect/disconnect behaviour (including repeated calls), timeout policy, and recovery policy.

**LPDS-001-API-005 — Idempotency and deprecation**
Methods with cumulative, destructive, irreversible, or hazardous effects state those side effects explicitly. A deprecated method stays discoverable for a documented interval, identifies its replacement, and raises `DeprecationWarning`.

---

## 17. Error and Exception Model

**LPDS-001-ERR-001 — Common exception categories**
Drivers map applicable failures into the common LPDS categories defined by LPDS-007. LPDS-007 is the sole normative source for exact exception class names, hierarchy, and error codes; the platform-level view below is illustrative only:

```text
DriverError
├── DriverConfigurationError
├── DriverValidationError
├── DriverStateError
├── DriverConnectionError
├── DriverTransportError        (includes DriverTimeoutError)
├── DriverProtocolError
├── DriverDeviceError
├── DriverResourceError
├── DriverSafetyError
├── DriverDependencyError
└── DriverInternalError
```

**LPDS-001-ERR-002 — Error context**
Errors include actionable context, avoid exposing credentials or secrets, preserve the original cause for diagnostic logging, and never convert a failed required operation into a silent pass.

---

## 18. Python Driver Requirements

**LPDS-001-PY-001 — Python architecture**
The implementation uses clear modules and responsibility boundaries, provides a stable documented import path for the driver class, validates arguments before unsafe transmission where possible, closes resources deterministically, supports dependency injection or an equivalent seam for transport testing, avoids unbounded loops/reads/waits/retries, and remains fully importable and usable with no automation framework installed.

---

## 19. Transport and Protocol Requirements

**LPDS-001-IO-001 — Declared transports**
Each driver declares its supported transport profiles and required configuration.

**LPDS-001-IO-002 — Finite blocking operations**
All blocking I/O has a finite timeout or a documented externally interruptible control mechanism.

**LPDS-001-IO-003 — Protocol serialization and validation**
Protocol operations apply the documented command syntax, framing, addressing, and units. The driver validates relevant response structure and integrity before reporting success, and does not wait for a response on operations that intentionally have none.

**LPDS-001-IO-004 — Recovery and observation**
Recoverable transport or protocol failures have documented recovery behaviour that doesn't conceal the original failure. The implementation permits capturing the protocol exchange close enough to the device boundary to prove what was transmitted and received.

---

## 20. State Ownership, Cancellation, and Recovery

**LPDS-001-STATE-001 — Declared operational states**
Each connection-capable driver declares equivalent states for: initial, connected idle, active operation, normal disconnect, operation-failure, and emergency safe. These six conceptual states are platform-level minimums, not a naming standard — LPDS-003 is the sole normative source for the exact connection/session state enum, and drivers use that enum rather than inventing an equivalent one.

**LPDS-001-STATE-002 — State ownership**
The driver declares which device state it owns, whether connection changes device configuration, and how state is resynchronized after external changes.

**LPDS-001-STATE-003 — Cooperative cancellation**
Long-running operations (scans, acquisitions, calibration, stabilization waits) provide a documented cancellation mechanism where interruption is operationally required, defining cancellation latency, cleanup behaviour, and treatment of partial results.

**LPDS-001-STATE-004 — Recovery verification**
After a documented recoverable fault, testing executes a known-good public method to verify successful recovery.

---

## 21. AI Driver Contract Integration

**LPDS-001-AI-001 — AI Driver Contract**
A driver that publishes an AI contract provides:

```text
ai/
├── ai_contract.yaml
└── ai_contract.lock
```

The LPDS-017 AI Driver Contract describes one driver and is adapter-independent: it never encodes any framework's syntax. The released contract matches the released public Python API — a capability added, removed, renamed, or changed updates the contract in the same revision.

---

## 22. Conformance Architecture

**LPDS-001-CONF-001 — LPDS-019 integration**
A driver integrates the LPDS-019 call and protocol conformance model so that, for every supported public method, it's possible to determine whether the method is exported and discoverable, which protocol vector applies, what outbound/inbound behaviour is expected, and where the trace evidence is stored. A public device-facing method is not silently omitted from conformance coverage, and the conformance test operates through the public Python API rather than proving only an internal mocked call.

---

## 23. Simulator Approval Model

**LPDS-001-SIM-001 — Simulator declaration**
A simulator used for conformance evidence has a versioned profile documenting its identity, the protocol boundary it reproduces, supported and unsupported behaviours, its timing model, and its known differences from physical hardware. A simulator pass is not represented as proof of physical measurement accuracy, electrical performance, calibration, or hardware safety unless independently verified.

---

## 24. Testing Strategy

**LPDS-001-TEST-001 — Test levels**
A released driver should exercise: unit tests, protocol serialization/parsing tests, simulator integration tests, import/discovery/callability tests, LPDS-019 protocol conformance tests, representative real-device tests where hardware is available, safety/timeout/cancellation/recovery tests, and adapter translation-correctness tests for each adapter that exists.

**LPDS-001-TEST-002 — Independence and regression**
Tests declare prerequisites rather than relying on undocumented ordering. A reproducible corrected defect gets a regression test at the lowest effective layer.

**LPDS-001-TEST-003 — Compatibility tests**
A compatibility test is added whenever a revision changes a public method name, argument, default, return schema, or error code.

---

## 25. CI and Automated Validation

**LPDS-001-CI-001 — Recommended validation jobs**
A repeatable local or CI workflow covering package-layout validation, clean-environment installation, linting, type checking, unit tests, import/discovery checks, LPDS-019 conformance, and adapter translation-correctness tests (where an adapter exists) is recommended once a driver is past its earliest `wip` stage. LPDS-001 does not mandate a specific CI service vendor, and a solo driver without CI infrastructure yet is not thereby non-conformant — it's earlier in its lifecycle.

---

## 26. Safety Architecture

**LPDS-001-SAFE-001 — Safety enforcement**
Safety requirements may exist at method, driver, device, or operator-procedure level; the responsible layer is stated.

**LPDS-001-SAFE-002 — Safe initialization and teardown**
Connection or driver initialization does not unintentionally enable hazardous outputs. Disconnect, exception cleanup, and cancellation place affected resources into the safest achievable declared state.

**LPDS-001-SAFE-003 — Configurable limits and forbidden sequences**
Voltage/current/power/temperature/other applicable limits are configurable, documented, and validated at the responsible layer. Known unsafe command sequences are represented in the driver's own documentation and enforced where technically possible.

**LPDS-001-SAFE-004 — Operator actions**
Operations requiring manual confirmation, physical reconfiguration, or protective equipment are explicit and not silently automated.

---

## 27. Resource and Concurrency Model

**LPDS-001-RES-001 — Resource declaration and access mode**
The driver identifies relevant resources (communication sessions, ports, channels, files requiring controlled access) and classifies each as exclusive, shareable, read-only shareable, multiplexed, or unsafe for parallel operation.

**LPDS-001-RES-002 — Default concurrency policy**
Concurrency is disabled by default when the device, protocol, transport, or driver is not proven safe for concurrent access.

---

## 28. Configuration Requirements

**LPDS-001-CFG-001 — Configuration model**
Configuration supports declared files, environment variables, or constructor arguments with a documented precedence, validates required fields, avoids embedding credentials in source or reports, and permits deterministic export of effective configuration with secrets redacted.

**LPDS-001-CFG-002 — Portable examples**
A released example does not depend on an undocumented local path, developer-specific device identifier, or hidden environment state.

---

## 29. Logging and Evidence

**LPDS-001-LOG-001 — Operational logging**
Drivers log enough information to diagnose connection attempts, state transitions, protocol failures, timeouts, retries, and cleanup results, and redact passwords/tokens/credentials from logs and evidence.

LPDS-008 is the sole normative source for the fuller logging and evidence schema; the requirement above is the platform-level minimum.

---

## 30. Documentation and Examples

**LPDS-001-DOC-001 — Documentation**
A driver's documentation covers supported devices/transports, installation, a connection example, the public API, safety notes, errors/troubleshooting, and known limitations, and doesn't contradict the code, the AI contract, or the README.

**LPDS-001-DOC-002 — Examples**
A driver provides a handful of useful, runnable examples — at minimum, enough to demonstrate connecting, one representative read/query operation, and one representative write/action operation. Each example states its purpose and whether it needs real hardware or works against the simulator. Examples use the driver's public API, not private internals.

---

## 31. Development Lifecycle

**LPDS-001-LIFE-001 — Phase-and-gate lifecycle**
Driver implementation should follow LPDS-020's incremental phase structure (architecture skeleton → core implementation → extended features → tests and docs → review and release). This is a useful shape for pacing the work even as a solo author — each phase updates implementation, tests, documentation, and the AI Driver Contract together, and gets a self-review against LPDS-010 before moving to the next.

---

## 32. Handling Gaps and Limitations

**LPDS-001-DEV-001 — Documenting what's incomplete**
If a driver doesn't yet meet part of this standard — real-hardware validation isn't possible, a capability isn't implemented, test coverage is thin — say so plainly in the README or CHANGELOG rather than silently shipping it as if complete. There's no formal deviation-approval process; honest documentation of a gap is the whole mechanism. A `wip` or `untested` status (§9) is the normal way to signal this.

---

## 33. Versioning and Compatibility

**LPDS-001-VER-001 — Version identity**
A release distinguishes `release_version` (the `vYY.RR` public version, LPDS-011) from `api_version` (bumped only on a breaking API change). A package release update doesn't automatically imply an API version change, and the release version has one authoritative source, consistent across package metadata, README, and the AI contract.

**LPDS-001-VER-002 — Breaking changes**
A breaking public API or behaviour change gets migration guidance, an incremented API major version, and a clear release-note warning. See LPDS-011 §10 for what counts as breaking.

**LPDS-001-COMP-001 — Compatibility surface**
Compatibility is assessed for public method names, aliases, argument order/defaults, return types/schemas, error categories, configuration keys, AI contract capability identifiers, and — independently — each adapter's own translation surface.

---

## 34. Security

**LPDS-001-SEC-001 — Secure project handling**
Drivers avoid storing plaintext credentials in source control, redact secrets from logs and evidence, avoid executing untrusted shell content, and constrain firmware-update/file-upload/reset operations appropriately. A release does not knowingly bundle undocumented binaries. Security controls here are ordinary good hygiene, not a certification claim.

---

## 35. Reliability and Performance

**LPDS-001-REL-001 — Failure behaviour and recovery**
A driver defines behaviour for invalid arguments, connection loss, timeout, and malformed responses. Recovery (retry, reconnection, safe shutdown) never conceals the original failed operation.

**LPDS-001-PERF-001 — Performance notes**
Where relevant, a driver documents expected connection time, stabilization delay, and known slow operations. Performance optimization never bypasses validation, safety, or required settling.

---

## 36. Checklist

Use this before calling a driver `stable` (§9). None of this needs a separate reviewer — it's meant as a solo self-check.

**Architecture**
- [ ] The driver is plain Python, importable and usable with zero automation framework installed.
- [ ] Any adapter lives under `adapters/<framework>/`, contains no device logic, and is independently testable.
- [ ] Public API, device semantics, protocol handling, and transport are reasonably separated (§12).

**Public API**
- [ ] Public methods use `snake_case`, are type-hinted, and are documented (name, args, return, preconditions, side effects).
- [ ] Connection state is explicit and queryable.
- [ ] A failed operation raises a `DriverError` subclass rather than returning a misleading success value.

**Safety**
- [ ] Initialization doesn't unexpectedly energize outputs; teardown leaves the device in a safe state.
- [ ] Configurable limits (voltage/current/etc., where applicable) are documented.
- [ ] Blocking I/O has a finite timeout.

**Tests and evidence**
- [ ] Unit tests run against a simulated transport with no hardware required.
- [ ] LPDS-019 conformance passes for the driver's device-facing methods (against the simulator at minimum; against real hardware for `stable` status).
- [ ] If an adapter exists, it has its own thin translation-correctness tests.

**Docs and package**
- [ ] README states the driver's status (§9), supported devices/transports, install steps, and a usage example.
- [ ] A handful of runnable examples exist and use the public API.
- [ ] The AI Driver Contract (if published) matches the current public API.
- [ ] Anything incomplete or unverified is documented rather than silently omitted (§32).

---

## 37. Goal

Provide a consistent, framework-independent Python instrument driver platform where any driver — built by one person or a small team — has a clear architecture, a stable public API, honest status reporting, and (where wanted) cleanly separated automation-framework adapters.

---

## Appendix A — Reference Architecture Diagram

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Test requirements and operator intent                                │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                 ┌──────────────▼──────────────┐
                 │ Human designer or AI planner│
                 │ LPDS-017 AI Driver Contract │
                 └──────────────┬──────────────┘
                                │
                 ┌──────────────▼──────────────┐
                 │ pytest suites / resources    │
                 │ or a framework adapter       │
                 └──────────────┬──────────────┘
                                │ public API calls
                 ┌──────────────▼──────────────┐
                 │ Public Python API layer      │
                 └──────────────┬──────────────┘
                                │ semantic calls
                 ┌──────────────▼──────────────┐
                 │ Driver core / device model  │
                 └──────────────┬──────────────┘
                                │ protocol intent
                 ┌──────────────▼──────────────┐
                 │ Protocol adapter            │
                 └──────────────┬──────────────┘
                                │ bytes, text, request, SDK call
                 ┌──────────────▼──────────────┐
                 │ Transport boundary          │◄──── trace / spy / proxy
                 └──────────────┬──────────────┘
                                │
                 ┌──────────────▼──────────────┐
                 │ Device or approved simulator│
                 └──────────────┬──────────────┘
                                │ response / acknowledgement / fault
                 ┌──────────────▼──────────────┐
                 │ Parsing, typed result, error│
                 └──────────────┬──────────────┘
                                │
                 ┌──────────────▼──────────────┐
                 │ Result and evidence          │
                 │ LPDS-019 coverage and traces │
                 └─────────────────────────────┘
```

---

## Appendix B — Recommended Release Tree

```text
<driver_name>_v<YY>.<RR>.zip
└── <driver_name>/
    ├── README.md
    ├── LICENSE
    ├── pyproject.toml
    ├── src/
    │   └── <driver_name>/
    ├── adapters/            (optional)
    ├── ai/
    │   ├── ai_contract.yaml
    │   └── ai_contract.lock
    ├── tests/
    │   ├── unit/
    │   ├── integration/
    │   └── conformance/
    ├── examples/
    ├── docs/                (recommended once past wip)
    ├── guide/                (recommended once past wip)
    ├── history/               (recommended once past wip)
    └── release/
        └── release_manifest.yaml
            # checksums.sha256, sbom.json, compatibility_report.json:
            # add these once you have consumers who need them, not before
```

---

## Appendix C — Change Record

### Deep trim to solo/small-team scale

Removed the 5-tier D0/D1/D2/P1/B1 release-class system and its applicability matrix, replacing it with the hub's existing simple `wip`/`untested`/`stable` status labels (§9). Removed formal deviation governance (named "release authority," approval/expiry dates) in favor of a one-paragraph "document what's incomplete" rule (§32). Removed §22 "AI Test Bench Contract Integration" entirely, since LPDS-018 (multi-instrument bench contract) was retired as out of scope for this hub. Downgraded SBOM, checksums, and requirements-traceability CSV from mandatory to "add them once you have consumers who need them." Reduced the ten-example minimum to a handful of representative examples. Consolidated the four overlapping closing sections (Acceptance Criteria, Failure Conditions, Minimum Definition of Done, Review Checklist — over 100 line items combined) into a single practical self-check checklist (§36). Removed the CSV requirements-traceability appendix. Throughout, softened "shall" gated by release class into either an unconditional "shall" (safety-relevant) or a "should" (good practice, judgment allowed).

### Migration to LPDS

Generalized from an earlier, single-automation-framework-specific platform requirements document into a framework-independent Python driver platform standard: added §3 "Driver vs Adapter Architecture" stating the platform's core thesis; renamed every framework-specific keyword/library concept to "public Python method" / "driver"; updated the canonical package tree to the `src/`-layout plus optional `adapters/` directory.
