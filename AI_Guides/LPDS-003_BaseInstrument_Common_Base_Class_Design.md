# LPDS-003 — BaseInstrument Common Base Class Design

**Document ID:** LPDS-003  
**Version:** 1.0  
**Status:** Draft Project Standard (Normative)  
**Applies to:** All LPDS Python instrument driver projects and the shared LPDS core package

---

## 1. Purpose

This specification defines the mandatory design and behavioural contract of the shared `BaseInstrument` used by LPDS Python instrument drivers.

The base class shall provide one consistent implementation foundation for:

- connection and session lifecycle management;
- explicit driver state;
- finite timeout handling;
- controlled retry and recovery;
- structured logging and evidence correlation;
- driver metadata and capability reporting;
- standard exception translation;
- diagnostics export;
- deterministic cleanup;
- dependency injection and protocol-boundary testability;
- framework-coupling-prevention safeguards.

The base class shall reduce duplicated infrastructure without absorbing device-specific semantics, protocol syntax, or bench-specific safety policy.

---

## 2. Goals

`BaseInstrument` shall:

1. make common driver behaviour consistent across instrument types;
2. prevent each driver from independently reimplementing connection, timeout, retry, error, logging, and cleanup logic;
3. enforce explicit state and deterministic resource ownership;
4. permit simulator, replay, spy, and real-device transports to be injected through the same boundary;
5. prevent accidental framework coupling: the base class shall not acquire a dependency on any specific automation framework, and shall not implicitly export its methods to one;
6. preserve causal error information while producing errors that are directly actionable from plain Python and that a framework adapter can translate into a framework-native failure without losing that information;
7. support one or more named sessions where the concrete driver permits them;
8. expose enough evidence hooks for LPDS-019 protocol-conformance testing;
9. be pure Python with zero dependency on, or awareness of, any automation or GUI framework — it shall have no concept of any such framework at all, and shall be fully constructible, controllable, and testable from a plain Python/pytest session with no automation framework installed;
10. evolve independently as a versioned LPDS shared component.

---

## 3. Scope Boundary

### 3.1 In scope

LPDS-003 defines:

- the base-class responsibility boundary;
- required interfaces, models, state transitions, and extension hooks;
- connection and disconnection semantics;
- session aliases and ownership;
- operation execution policy;
- timeout, retry, recovery, and cancellation behaviour;
- common metadata, capabilities, logging, diagnostics, and redaction support;
- standard cleanup orchestration;
- Python import safety and public-API exposure rules that prevent framework coupling;
- testing and acceptance requirements for the shared base implementation;
- compatibility rules between a driver and the shared LPDS core package.

### 3.2 Out of scope

LPDS-003 does not define:

- the complete public API surface or canonical method names governed by LPDS-002;
- VISA, serial, TCP/IP, USB, CAN, Modbus, HTTP, GPIO, or vendor-SDK implementation details governed by LPDS-004;
- the complete exception catalogue and message standard governed by LPDS-007;
- device-specific protocol commands, responses, limits, capabilities, or state machines;
- bench wiring, shared hardware resources, or global emergency sequences governed by LPDS-018;
- package-tree placement beyond the shared-component requirements necessary to use this base class;
- physical measurement accuracy or calibration correctness;
- the full logging and evidence schema governed by LPDS-008.

Where a subordinate specification defines a stricter applicable rule, the stricter rule shall apply.

---

## 4. Normative References

Implementations conforming to LPDS-003 shall also follow the applicable requirements of:

- LPDS-001 — Platform Requirements;
- LPDS-002 — Mandatory Public API Standard;
- LPDS-004 — Transport Layer Specification;
- LPDS-005 — Driver Package Specification;
- LPDS-006 — Coding Standard;
- LPDS-007 — Error and Exception Standard;
- LPDS-008 — Logging and Evidence Standard;
- LPDS-009 — Testing Standard;
- LPDS-013 — Capability Model;
- LPDS-014 — Driver Configuration Model Specification;
- LPDS-017 — AI Driver Contract Specification;
- LPDS-018 — AI Test Bench Contract Specification;
- LPDS-019 — Driver Call and Protocol Conformance Test Specification;
- LPDS-020 — Driver Implementation Lifecycle.

LPDS-003 defines shared implementation semantics. It shall not silently redefine a public API owned by LPDS-002 or device behaviour owned by a device-specific requirement.

---

## 5. Normative Terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement; deviation requires documented justification;
- **may** — permitted implementation choice;
- **base class** — the shared `BaseInstrument` implementation;
- **concrete driver** — a device-specific Python driver derived from the base class;
- **driver core** — device-semantics implementation independent of any particular framework adapter's presentation where practical;
- **adapter** — a separate, thin translation layer that exposes a driver instance's public API to one specific automation framework or interface (pytest fixtures, a CLI command set, a REST endpoint, ...); an adapter contains no device logic of its own and may be one of several wrapping the same driver;
- **session** — one logical connection and its associated state, transport, identity, configuration, locks, and evidence context;
- **alias** — caller-visible name identifying a session;
- **transport** — the object performing communication at the device boundary;
- **operation** — one logical driver action executed under base-class lifecycle, timeout, retry, logging, and locking policy;
- **hook** — a protected extension point intentionally implemented by a concrete driver;
- **safe state** — the safest achievable device condition declared by the device driver or bench contract;
- **deadline** — absolute monotonic time after which an operation shall no longer block or retry.

---

## 6. Architectural Position

The required execution structure is:

```text
Framework adapter (pytest fixtures, CLI, REST, ...)
or a direct plain-Python caller
                ↓
Concrete LPDS driver
                ↓
BaseInstrument infrastructure
                ↓
Driver core / device-semantics service
                ↓
Protocol layer
                ↓
Transport interface
                ↓
Physical device or approved simulator
```

`BaseInstrument` is an infrastructure coordinator. It shall not become a second protocol layer and shall not contain copied vendor commands.

The concrete driver may inherit common infrastructure behaviour from the base class, but the public API method names and signatures remain governed by LPDS-002 and the driver's LPDS-017 contract. A framework adapter shall not add device logic of its own; it shall only translate calls and results between its framework and the driver's public API, and multiple adapters may wrap the same driver instance concurrently.

---

## 7. Core Design Principles

### 7.1 Infrastructure, not device semantics

The base class shall manage generic concerns. It shall not decide what voltage, current, channel, trigger mode, relay pattern, temperature, resistance, waveform, or calibration operation means for a specific device.

### 7.2 Composition below inheritance

The concrete driver shall inherit from `BaseInstrument`, while transports, clocks, retry policies, redactors, diagnostic writers, protocol observers, and driver-core services should be supplied through composition and dependency injection.

### 7.3 Explicit public API exposure

The base class and concrete drivers shall not rely on, or implicitly trigger, framework-specific method export. A method is part of the supported public API only when it is intentionally defined as public, documented, and covered by the driver's public API contract. A framework adapter shall explicitly select which public methods it exposes to its framework; it shall not expose the driver's full attribute surface through blanket reflection.

### 7.4 No hardware access during import

Importing the Python package, constructing the driver object, generating API documentation, or inspecting capabilities shall not open hardware, enumerate buses, modify device state, or require an available instrument.

### 7.5 Deterministic cleanup

Every acquired resource shall have a deterministic release path. A partial connection failure shall not leave an open transport or registered live session.

### 7.6 Finite blocking

Every blocking operation shall use a finite timeout or an externally interruptible mechanism approved by the applicable specification.

### 7.7 Fail visibly

The base class shall not convert validation, state, transport, protocol, timeout, device, safety, or cleanup failures into success.

### 7.8 Preserve device independence

No base API shall require a driver to be SCPI-based. The same base implementation shall support text, binary, request/response, command-only, SDK, and message-oriented devices.

---

## 8. Shared Package Model

### 8.1 Authoritative package

The authoritative base implementation should be delivered as a separately versioned Python distribution, recommended name:

```text
lpds-core
```

Recommended import path:

```python
from lpds_core import BaseInstrument
```

### 8.2 Driver dependency

Each LPDS driver shall declare a compatible `lpds-core` version range in its installation metadata.

Example:

```toml
dependencies = [
  "lpds-core>=1.0,<2.0"
]
```

### 8.3 No divergent private copies

A driver shall not maintain a modified private copy of the base-class source under the same identity. An offline release package may include an approved `lpds-core` wheel, but that wheel shall match the declared dependency and checksum.

### 8.4 Version evidence

Driver information and diagnostic bundles shall record the effective `lpds-core` version.

---

## 9. Recommended Shared Module Structure

The shared package should provide an equivalent of:

```text
lpds_core/
├── __init__.py
├── base.py
├── session.py
├── state.py
├── contracts.py
├── metadata.py
├── capabilities.py
├── errors.py
├── timeout.py
├── retry.py
├── recovery.py
├── cleanup.py
├── logging.py
├── diagnostics.py
├── redaction.py
├── conversion.py
├── concurrency.py
└── testing/
    ├── fake_clock.py
    ├── fake_transport.py
    └── trace_spy.py
```

Equivalent layouts may be approved, but responsibilities shall remain separated and testable.

---

## 10. Base Class Construction

### 10.1 Constructor behaviour

The constructor shall:

- validate static driver metadata;
- store normalized driver defaults;
- initialize an empty session registry;
- initialize logging and diagnostic components;
- initialize capability data that does not require hardware;
- perform no device communication;
- perform no implicit connection;
- avoid loading proprietary SDKs unless the concrete driver explicitly requires them for import-safe type availability.

### 10.2 Required constructor dependencies

The base class shall accept or otherwise provide equivalent access to:

- immutable `DriverMetadata`;
- normalized default configuration;
- transport factory or transport-provider interface;
- logger or structured event sink;
- timeout policy;
- retry policy;
- redaction policy;
- monotonic clock;
- optional protocol observer;
- optional diagnostic exporter.

Dependencies that affect deterministic testing should be injectable.

### 10.3 Constructor compatibility

Concrete drivers may expose simplified constructor arguments intended for use by a framework adapter or CLI wrapper, but they shall normalize those values before passing them into the base infrastructure.

---

## 11. Required Data Models

### 11.1 DriverMetadata

`DriverMetadata` shall be immutable and shall contain at least:

- driver name;
- driver display name;
- driver version;
- package name;
- manufacturer scope;
- supported model declarations;
- supported firmware declarations where known;
- supported transport profiles;
- build date when available;
- Git revision when available;
- LPDS API compatibility version;
- `lpds-core` compatibility declaration.

Unknown metadata shall be represented explicitly as unknown or absent. It shall not be invented.

### 11.2 InstrumentIdentity

A connected identity result should contain:

- manufacturer;
- model;
- serial number;
- firmware version;
- raw identity response when safe to retain;
- identity verification status;
- timestamp.

### 11.3 ConnectionRequest

A normalized connection request shall contain equivalent information to:

- alias;
- transport profile;
- resource or address;
- finite connection timeout;
- operation timeout default;
- transport options;
- identity-verification policy;
- reconnect policy;
- optional safety profile reference.

### 11.4 ConnectionInfo

Connection information shall be representable using plain, framework-neutral data types (for example a dataclass convertible to a dict or JSON-compatible structure) after conversion, so that any framework adapter can consume it, and should include:

- alias;
- current state;
- transport profile;
- redacted resource identifier;
- connected timestamp;
- last successful communication timestamp;
- identity summary;
- timeout settings;
- retry policy summary;
- session generation identifier.

### 11.5 OperationContext

Every base-managed operation shall create an operation context containing at least:

- operation name;
- public API method name when known;
- session alias;
- correlation identifier;
- start time;
- deadline;
- attempt number;
- idempotency declaration;
- required session states;
- state before execution;
- evidence or protocol-vector reference when supplied.

### 11.6 ErrorRecord

The last-error record shall contain:

- timestamp;
- exception category;
- stable error code when defined;
- operation;
- alias;
- state;
- redacted message;
- retryability;
- recovery status;
- causal exception type;
- correlation identifier.

---

## 12. Session Registry and Alias Model

### 12.1 Session registry

The base class shall own a session registry. Each entry shall contain the session's transport, state, locks, effective configuration, identity, last error, cleanup stack, and evidence context.

### 12.2 Default alias

The default alias shall be:

```text
default
```

A concrete driver may expose a device-specific conventional alias, but it shall still map deterministically to a registry entry.

### 12.3 Alias normalization

Aliases shall:

- be non-empty strings;
- be trimmed;
- be compared using a documented normalization rule;
- reject ambiguous duplicates after normalization;
- be preserved in user-facing output in a stable display form.

Case-insensitive matching is recommended.

### 12.4 Session capacity

The base infrastructure shall support multiple named sessions. A concrete driver may limit capacity to one session and shall report an actionable state or resource error when an additional session is requested.

### 12.5 Session generation

Each successful new connection shall increment or replace a session-generation identifier. Evidence from a previous physical connection shall not be silently attributed to a later reconnection with the same alias.

### 12.6 Active session selection

When a public API permits omission of `alias`, the base shall resolve the target deterministically:

1. use `default` when present;
2. otherwise use the only connected session when exactly one exists and LPDS-002 permits this convenience;
3. otherwise fail with an ambiguity error.

It shall not select an arbitrary session.

---

## 13. State Model

### 13.1 Required infrastructure states

LPDS-003 is the sole normative source for the connection/session state enum used across the platform. LPDS-001, LPDS-002, and LPDS-012 each expose a reduced, presentation-specific projection of this enum (for example LPDS-002's lowercase public `state` field); those projections shall map onto the states below rather than defining independent state names.

Each session shall use the following base-level states:

```text
DISCONNECTED
CONNECTING
CONNECTED
CONFIGURED
BUSY
WAITING
RECOVERING
ERROR
CLOSING
```

The concrete driver may maintain additional device-semantic state, but it shall not contradict the base session state.

### 13.2 State meanings

- **DISCONNECTED** — no usable transport is owned by the session;
- **CONNECTING** — transport creation, opening, or communication verification is in progress;
- **CONNECTED** — communication is established and the session may accept supported operations;
- **CONFIGURED** — a device-specific required configuration has been applied;
- **BUSY** — an active synchronous operation owns the session I/O boundary;
- **WAITING** — the driver is waiting for a device condition, response, trigger, or stabilization interval;
- **RECOVERING** — recovery or reconnect activity is in progress;
- **ERROR** — the session is not currently safe to use without an explicit recovery or disconnect decision;
- **CLOSING** — safe-state, cleanup, or transport release is in progress.

### 13.3 Minimum transition rules

The base class shall enforce at least:

```text
DISCONNECTED → CONNECTING
CONNECTING   → CONNECTED | ERROR | DISCONNECTED
CONNECTED    → CONFIGURED | BUSY | WAITING | RECOVERING | CLOSING | ERROR
CONFIGURED   → BUSY | WAITING | RECOVERING | CLOSING | ERROR | CONNECTED
BUSY         → CONNECTED | CONFIGURED | WAITING | RECOVERING | ERROR | CLOSING
WAITING      → CONNECTED | CONFIGURED | BUSY | RECOVERING | ERROR | CLOSING
RECOVERING   → CONNECTED | CONFIGURED | ERROR | CLOSING | DISCONNECTED
ERROR        → RECOVERING | CLOSING | DISCONNECTED
CLOSING      → DISCONNECTED | ERROR
```

Illegal transitions shall raise a state error and shall not silently modify the state.

### 13.4 Device-semantic state

Output-enabled, trigger-armed, measurement-configured, relay-closed, remote/local, calibration, acquisition, and similar states belong to the concrete driver core. The base class may store them as typed session annotations but shall not define their meaning.

### 13.5 State observation

State changes shall be logged with before-state, after-state, alias, operation, timestamp, and correlation identifier.

---

## 14. Connection Lifecycle

### 14.1 Connect template

A base-managed connection shall execute equivalent steps in this order:

1. normalize and validate the connection request;
2. reserve the alias and required software resource;
3. create a session in `CONNECTING` state;
4. create the transport through the injected factory;
5. apply finite transport timeouts;
6. open the transport;
7. execute the concrete communication-probe hook;
8. execute identity discovery or verification when required;
9. run the concrete post-connect hook;
10. commit the session as `CONNECTED` or `CONFIGURED`;
11. publish connection metadata and evidence.

### 14.2 Partial failure cleanup

When any connection step fails, the base class shall:

- preserve the original failure as the primary cause;
- attempt to close any partially opened transport;
- release the alias and resource reservation;
- record cleanup failures separately;
- leave no session that appears connected;
- return the session to `DISCONNECTED` or retain a clearly unusable `ERROR` record according to the approved error policy;
- raise a documented connection-related exception.

### 14.3 Repeated connect

For an already connected alias:

- the same effective request may be treated as idempotent only when the driver explicitly declares this behaviour;
- the base should perform a lightweight communication check before reporting the existing session as healthy;
- a materially different request shall fail unless an explicit reconnect or replace policy is requested;
- repeated connect shall never create an untracked second transport.

### 14.4 Communication verification

A successful transport open alone shall not prove a successful instrument connection when a safe probe is available. The concrete driver shall implement the lowest-risk valid communication check, such as identity, status, ping, handshake, or SDK health call.

### 14.5 Auto-connect

Auto-connect at module import or construction is prohibited.

A concrete driver may support explicit constructor configuration that requests connection during first public operation, but lazy connection shall be documented, deterministic, opt-in, finite, and visible in evidence.

---

## 15. Disconnection and Close Lifecycle

### 15.1 Disconnect template

A base-managed disconnect shall execute equivalent steps:

1. resolve the target session;
2. prevent new operations from entering;
3. transition to `CLOSING`;
4. request cancellation of interruptible waits;
5. execute the concrete safe-state hook when applicable;
6. execute registered cleanup actions in defined order;
7. close the transport;
8. release locks and resource reservations;
9. clear live transport references;
10. transition to `DISCONNECTED`;
11. publish cleanup evidence.

### 15.2 Cleanup despite failure

Failure of safe-state or one cleanup action shall not prevent attempts to execute remaining independent cleanup actions and transport close.

### 15.3 Aggregated cleanup errors

When multiple cleanup steps fail, the base shall raise or record one primary cleanup exception with a structured list of secondary failures. The user shall be able to determine whether the transport was closed and whether the declared safe state was verified.

### 15.4 Repeated disconnect

Disconnecting an already disconnected alias shall be idempotent unless LPDS-002 explicitly requires strict failure. It shall not create a new error by default.

### 15.5 Close all

The base shall support deterministic closure of all sessions. It shall attempt every session even if one fails and shall provide an aggregated result.

---

## 16. Safe-State and Cleanup Contract

### 16.1 Base responsibility

The base class shall orchestrate safe-state execution but shall not invent device-specific shutdown commands.

### 16.2 Concrete hook

A concrete driver with controllable hazardous or stateful outputs shall implement a safe-state hook equivalent to:

```python
def _apply_safe_state(self, session: InstrumentSession, reason: CleanupReason) -> SafeStateResult:
    ...
```

### 16.3 Cleanup registration

The base should permit concrete components to register cleanup actions with:

- stable action name;
- execution priority;
- timeout;
- idempotency declaration;
- continue-on-failure policy;
- evidence classification.

Cleanup order shall be deterministic. Last-in-first-out is recommended for acquired resources; safety actions may use explicit higher priority.

### 16.4 Verification

Where the device supports read-back or status verification, the concrete safe-state hook should verify the resulting state. "Command sent" shall not be represented as "safe state verified" unless no stronger oracle is available and this limitation is explicit.

### 16.5 Bench responsibility

A bench-wide emergency sequence remains governed by LPDS-018. The driver safe-state hook shall expose enough behaviour to participate in that sequence.

---

## 17. Operation Execution Wrapper

### 17.1 Purpose

All device-facing concrete operations should execute through one base-managed wrapper equivalent to:

```python
_execute_operation(
    operation_name,
    callable,
    *,
    alias="default",
    timeout=None,
    retry_policy=None,
    idempotent=False,
    required_states=(SessionState.CONNECTED, SessionState.CONFIGURED),
    waiting=False,
    method_name=None,
    protocol_vector=None,
)
```

### 17.2 Required behaviour

The wrapper shall:

- resolve the session deterministically;
- validate the current state;
- acquire the required session lock;
- create an operation context and correlation identifier;
- calculate one absolute deadline;
- transition the session to `BUSY` or `WAITING` as appropriate;
- invoke the operation;
- apply only approved retries;
- translate lower-level errors without losing the cause;
- update last-success or last-error data;
- restore the correct post-operation state;
- emit start, retry, success, failure, and state-transition events;
- release the lock in all outcomes.

### 17.3 No hidden semantic success

The wrapper shall not infer successful device behaviour solely because the callable returned. Device acknowledgement, response parsing, error queue checks, read-back, or other semantic verification remain the concrete driver's responsibility.

### 17.4 Nested operations

Nested base-managed operations shall either:

- share one operation context and re-entrant session lock under a documented rule; or
- be prohibited with a clear concurrency/state error.

They shall not create deadlock or conflicting independent deadlines.

---

## 18. Timeout and Deadline Policy

### 18.1 Timeout precedence

The effective timeout shall be resolved in this order:

1. explicit per-call timeout;
2. operation-specific driver configuration;
3. session-level operation timeout;
4. driver default timeout;
5. LPDS platform default.

### 18.2 Validation

Timeout values shall be finite positive durations. Zero, negative, NaN, infinity, and invalid text shall be rejected before communication.

### 18.3 Absolute deadline

Retries, polling loops, stabilization waits, and sub-operations shall share one absolute monotonic deadline unless the public contract explicitly defines separate phases.

A retry shall not reset the caller's total timeout.

### 18.4 Transport propagation

The remaining deadline should be propagated to transport reads, writes, queries, SDK waits, and polling loops where supported.

### 18.5 Timeout exception

Timeout failures shall identify:

- operation;
- alias;
- configured timeout;
- elapsed duration;
- state at timeout;
- retry attempts;
- whether recovery or cleanup succeeded.

### 18.6 Uninterruptible vendor calls

When a vendor SDK cannot be interrupted, the limitation shall be documented. The base shall not falsely claim strict timeout enforcement. Such calls require an approved containment strategy, such as process isolation, SDK-native timeout configuration, or externally managed worker termination.

---

## 19. Retry Policy

### 19.1 Default

The platform default shall be no automatic retry unless the operation or transport primitive is explicitly classified as retry-safe.

### 19.2 Retry eligibility

Automatic retry may occur only when all of the following are true:

- the failure category is declared retryable;
- the operation is idempotent or has a proven duplicate-suppression mechanism;
- the remaining deadline is sufficient;
- retry does not violate device or bench safety;
- retry does not conceal the original failed attempt.

### 19.3 Prohibited automatic retries

The base shall not automatically retry, without a device-specific approved policy:

- output enable or disable operations;
- motion commands;
- relay topology changes;
- calibration writes;
- firmware updates;
- destructive file operations;
- cumulative increments;
- triggers that may execute more than once;
- commands with unknown acknowledgement state.

### 19.4 Backoff

Retry policy shall define:

- maximum attempts;
- initial delay;
- backoff function;
- maximum delay;
- jitter policy if any;
- retryable exception classes or codes;
- post-failure recovery action.

Deterministic tests shall be possible by injecting the clock and delay function.

### 19.5 Evidence

Every retry shall be visible in structured logs and diagnostics with attempt number, reason, delay, and final outcome.

---

## 20. Recovery Policy

### 20.1 Recovery is distinct from retry

Retry repeats an operation. Recovery attempts to restore a usable session. The two shall not be treated as synonyms.

### 20.2 Recovery hook

A concrete driver may implement an approved recovery hook equivalent to:

```python
def _recover_session(
    self,
    session: InstrumentSession,
    error: BaseException,
    context: OperationContext,
) -> RecoveryResult:
    ...
```

### 20.3 Recovery outcomes

Recovery shall report one of:

- recovered and communication verified;
- recovered transport but device state unknown;
- reconnect required;
- unrecoverable;
- recovery prohibited by safety policy.

### 20.4 Original operation result

Successful recovery shall not convert the original failed operation into a pass unless the operation is safely retried and then succeeds under the documented retry policy.

### 20.5 Post-recovery verification

After recovery, a known-good low-risk communication operation should verify the session before returning it to `CONNECTED` or `CONFIGURED`.

---

## 21. Error Model Integration

### 21.1 Required categories

LPDS-007 is the sole normative source for exact exception class names and hierarchy. The base implementation shall support, directly or through LPDS-007's `DriverError`-rooted hierarchy, at least equivalent semantic categories for: configuration, validation, state, connection, transport (including timeout), protocol, device, resource/concurrency, safety, and cleanup failures. Category names used by `lpds-core` shall match LPDS-007's names exactly rather than introducing parallel unprefixed names.

### 21.2 Causal preservation

Translated errors shall preserve the original exception as the Python cause when safe and practical.

### 21.3 Actionable context

Errors shall identify the failed operation and enough redacted context to act on the failure. They shall not expose passwords, tokens, private keys, or unredacted credentials.

### 21.4 Unknown exceptions

Unexpected exceptions shall not pass through as misleading success. They should be wrapped at the appropriate infrastructure boundary while preserving traceback and cause for diagnostics.

### 21.5 Last error

Each session shall retain a structured last-error record. Clearing that record shall not alter device state or erase retained release evidence.

---

## 22. Logging and Evidence Integration

### 22.1 Structured events

The base shall emit structured events for at least:

- driver initialization;
- connection request and outcome;
- disconnection and cleanup outcome;
- state transition;
- operation start and completion;
- retry;
- timeout;
- recovery;
- device identity acquisition;
- capability snapshot;
- diagnostics export.

### 22.2 Minimum event fields

Events shall contain equivalent fields to:

- UTC timestamp;
- monotonic timestamp or duration basis;
- event name;
- severity;
- driver name and version;
- `lpds-core` version;
- alias;
- session generation;
- correlation identifier;
- public API method and internal operation when known;
- state before and after;
- duration;
- attempt number;
- outcome;
- redacted parameters;
- error category and code when applicable;
- protocol-vector or test reference when supplied.

### 22.3 Protocol payload separation

Raw outbound and inbound protocol data should be recorded by the protocol observer or transport trace system, not indiscriminately duplicated in general logs.

### 22.4 Secret redaction

Redaction shall occur before persistent output. Diagnostic exporters shall not rely only on downstream display filtering.

### 22.5 Adapter-facing logging

The base may publish concise operational messages that a framework adapter forwards to its own logging surface (for example pytest captured output, a CLI console, or a REST response log), but structured evidence shall remain available independently of any adapter or framework internals.

### 22.6 Relationship to LPDS-008

LPDS-008 is the sole normative source for the complete evidence schema, event envelope, evidence manifest, and diagnostic-bundle format. The base-class requirements above are the minimum structured-event surface the common base shall provide; concrete field names, schema versions, and file layouts shall follow LPDS-008.

---

## 23. Protocol Observation Interface

### 23.1 Purpose

The base shall provide a way to associate a public API method and operation context with protocol evidence captured near the transport boundary.

### 23.2 Observer contract

An observer should support equivalent notifications:

```python
on_operation_start(context)
on_outbound(context, payload_metadata)
on_inbound(context, payload_metadata)
on_operation_end(context, outcome)
```

### 23.3 Non-interference

Observation shall not intentionally change serialization, timing semantics, returned values, or exception behaviour.

### 23.4 LPDS-019 correlation

The operation context shall permit LPDS-019 to correlate:

```text
Public API call
    ↔ operation
    ↔ protocol vector
    ↔ outbound trace
    ↔ inbound trace
    ↔ parsed result
```

Internal method mocking without serialized protocol evidence is not sufficient for device-facing conformance.

---

## 24. Metadata and Capability Reporting

### 24.1 Static metadata

Static driver metadata shall be available without a connection.

### 24.2 Dynamic metadata

Instrument identity, firmware, installed modules, channel count, feature options, and similar dynamic data shall be marked unavailable until safely queried.

### 24.3 Capability descriptors

Capabilities shall use stable identifiers and should contain:

- capability identifier;
- availability status;
- source of availability information;
- required connection state;
- risk class where applicable;
- public API method references;
- limitations;
- transport or model constraints.

### 24.4 No capability invention

The base shall not infer device capabilities merely from transport type. For example, a VISA connection does not automatically imply SCPI capability.

### 24.5 Synchronization

Capability reporting shall remain consistent with LPDS-013, the driver's LPDS-017 contract, documentation, and exported public API.

---

## 25. Framework Adapter Integration

### 25.1 No implicit framework export

The base and concrete driver classes shall not import, subclass, decorate, or otherwise structurally depend on any automation-framework base class, decorator, or metaclass. The base class shall not provide automatic, reflection-based export of its methods to any framework. A framework adapter shall explicitly declare which public methods it exposes to its framework.

Example: framework adapter

```python
class ExampleInstrumentAdapter:
    """Thin adapter around ExampleInstrumentDriver, for whichever
    automation framework this adapter package targets.

    Contains no device logic; every call is forwarded to the driver's
    public API and results are converted to whatever representation
    that framework expects.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._driver = ExampleInstrumentDriver(*args, **kwargs)

    def connect_example_instrument(self, resource: str, alias: str = "default") -> dict:
        return self._driver.connect(resource=resource, alias=alias).to_dict()

    def get_example_instrument_identity(self, alias: str = "default") -> dict:
        return self._driver.get_identity(alias=alias).to_dict()
```

The equivalent plain-Python usage, with no framework installed, is:

```python
driver = ExampleInstrumentDriver()
driver.connect(resource="TCPIP::192.168.0.20::INSTR", alias="default")
identity = driver.get_identity(alias="default")
driver.disconnect(alias="default")
```

### 25.2 Adapter lifecycle scope

The recommended default is that one adapter instance owns exactly one driver instance for the lifetime of one automation-scope equivalent (for example, one pytest fixture scope, or one CLI process invocation). Broader sharing across multiple automation-scope equivalents may be used only when session ownership, cleanup, parallel execution, and cross-suite state retention are explicitly designed and tested by the adapter.

### 25.3 Adapter version reporting

A framework adapter shall expose the driver's version as its own reported version (for example, as the adapter package's own reported version). The effective `lpds-core` version shall be included in driver information and diagnostics rather than substituted for the driver version.

### 25.4 Public common methods

LPDS-002 owns the canonical public method names and signatures. The base shall provide implementation support for the approved common groups, including:

- connection state inspection;
- driver information;
- capability reporting;
- last-error inspection;
- diagnostics export;
- close-all behaviour;
- shared verification semantics where adopted by LPDS-002.

### 25.5 Private helpers

Protected hooks, transport primitives, retry wrappers, session registry access, raw queries, raw writes, observer controls, and cleanup internals shall not be exported by the driver as part of its public API, and a framework adapter shall not expose them to its framework.

### 25.6 Return conversion

Public results shall be convertible to plain, framework-neutral data types suitable for consumption by any adapter. The base should provide deterministic conversion for:

- enums to stable strings;
- dataclasses to dictionaries;
- paths to strings;
- tuples to lists when a target schema requires lists;
- timestamps to documented ISO 8601 strings;
- optional values to `None` or an explicitly documented sentinel.

Opaque transport or SDK objects shall not leak through the driver's public API.

### 25.7 Failure messages

Failures raised by the driver shall be concise enough for an adapter to surface directly to its consumer (for example in a pytest assertion message, a CLI error line, or a REST error response) while retaining structured details in diagnostics and evidence.

---

## 26. Common Verification Support

### 26.1 Scope

The base may provide reusable verification utilities, but it shall not impose device-specific units, tolerances, stabilization criteria, or calibration semantics.

### 26.2 Required utility semantics

Where adopted by LPDS-002, shared verification support should include equivalent semantics for:

- exact equality;
- inclusive range;
- greater-than and less-than checks;
- absolute tolerance;
- relative tolerance;
- combined absolute/relative tolerance;
- Boolean state assertions;
- connected/disconnected assertions;
- polling until a predicate becomes true under a finite deadline.

### 26.3 Numeric validation

Numeric utilities shall define behaviour for:

- NaN;
- positive and negative infinity;
- `None`;
- Boolean values passed as numbers;
- unit mismatch;
- zero expected value with relative tolerance;
- inclusive and exclusive boundaries.

### 26.4 Stabilization

A generic stabilization helper may calculate windows, median, standard deviation, or relative spread, but the concrete driver or test shall supply the acquisition function, thresholds, sample count, interval, and maximum duration.

### 26.5 Evidence

Verification failures shall report actual value, expected condition, tolerance, unit, sample statistics where applicable, and source operation.

---

## 27. Concurrency and Thread Safety

### 27.1 Default policy

Concurrent access to one session shall be disabled by default.

### 27.2 Per-session lock

Each session shall own a lock guarding transport and mutable session state. A re-entrant lock may be used when nested internal calls are explicitly supported.

### 27.3 Registry lock

Creation, replacement, selection, and removal of sessions shall be protected by a separate registry lock.

### 27.4 Cross-session concurrency

Different sessions may execute concurrently only when:

- the concrete driver declares support;
- transports and shared SDK resources are thread-safe or externally serialized;
- no shared physical resource conflict exists;
- LPDS-018 does not prohibit parallel operation.

### 27.5 Lock timeout

Waiting for an operation lock shall respect the caller's deadline and shall fail with a concurrency or timeout error rather than blocking indefinitely.

### 27.6 Async implementations

An asynchronous concrete implementation may adapt the base contract, but it shall preserve the same observable lifecycle, state, timeout, retry, error, cleanup, and evidence semantics.

---

## 28. Configuration Integration

### 28.1 Normalized input

The base should consume normalized configuration objects governed by LPDS-014 rather than parsing arbitrary files throughout the lifecycle code.

### 28.2 Precedence evidence

The effective configuration source and precedence shall be recorded with secrets redacted.

### 28.3 Immutable session configuration

Connection-critical configuration should be immutable for the life of a session. Changing address, transport profile, baud rate, SDK target, or equivalent fields shall require reconnect or an explicitly supported reconfiguration path.

### 28.4 Validation timing

Configuration values that can be validated without hardware shall be rejected before transport creation. Device-dependent validation may occur after identity or capability discovery.

### 28.5 Secret-bearing values

Secret fields shall be represented using typed secret containers or explicit schema metadata so they can be redacted before logging and diagnostics export.

---

## 29. Diagnostics Export

### 29.1 Required function

The base shall provide a diagnostic export service callable through the approved public API.

### 29.2 Minimum content

A diagnostic bundle shall contain equivalent information to:

```text
diagnostics/<driver>/<timestamp>/
├── summary.json
├── environment.json
├── driver_metadata.json
├── capabilities.json
├── sessions.json
├── recent_events.jsonl
├── errors.json
├── effective_configuration.redacted.json
└── manifest.json
```

Protocol traces may be included by reference or copied when policy permits.

### 29.3 Required metadata

The bundle shall record:

- driver and `lpds-core` versions;
- Python version and, where an adapter is in use, the adapter's framework version;
- operating system;
- transport profiles;
- simulator or connected-device identity when available;
- session states;
- timeouts and retry policy summaries;
- recent errors and recovery outcomes;
- bundle schema version;
- file checksums.

### 29.4 Safety and privacy

The exporter shall redact secrets and should permit exclusion of raw payloads, local usernames, hostnames, absolute paths, and serial numbers according to project policy.

### 29.5 Export failure

Failure to export diagnostics shall not alter the device state. The error shall identify the failed destination and preserve the original filesystem or serialization cause.

---

## 30. Required Extension Hooks

The base class shall define or provide equivalent protected hooks. Concrete drivers shall override only the hooks they need.

```python
_build_transport(request) -> Transport
_validate_connection_request(request) -> None
_probe_communication(session, context) -> None
_read_identity(session, context) -> InstrumentIdentity | None
_on_connected(session, context) -> None
_apply_safe_state(session, reason) -> SafeStateResult
_on_disconnecting(session, reason) -> None
_recover_session(session, error, context) -> RecoveryResult
_get_dynamic_capabilities(session) -> Iterable[Capability]
_redact_driver_value(name, value) -> object
```

### 30.1 Hook rules

Hooks shall:

- be protected, not part of the public API surface exposed through a framework adapter;
- receive explicit session or context objects;
- obey the caller's deadline;
- avoid opening unmanaged secondary transports;
- raise documented LPDS exception categories;
- not swallow required failures;
- be unit-testable with injected dependencies.

### 30.2 Lifecycle method overrides

Concrete drivers should not override the base orchestration methods for connect, disconnect, operation execution, timeout calculation, logging, or registry management. When an override is unavoidable, it shall be reviewed, documented, and covered by compatibility and lifecycle tests.

---

## 31. Transport Contract Expected by the Base

The transport boundary shall provide an equivalent protocol-oriented interface. Not every transport must implement every primitive.

```python
class Transport(Protocol):
    def open(self, *, deadline: float) -> None: ...
    def close(self, *, deadline: float) -> None: ...
    def is_open(self) -> bool: ...
    def write(self, data: bytes | str, *, deadline: float) -> None: ...
    def read(self, *, deadline: float) -> bytes | str: ...
    def query(self, data: bytes | str, *, deadline: float) -> bytes | str: ...
    def cancel(self) -> bool: ...
    def connection_info(self) -> Mapping[str, object]: ...
```

Binary, streaming, callback, message, transaction, and SDK transports may expose specialized interfaces. The base shall depend on declared capabilities rather than assume every transport supports text `query()`.

Transport methods shall expose failures without reporting false success and shall permit protocol observation close to the device boundary.

---

## 32. Reference Class Skeleton

The following skeleton is informative but illustrates the required separation:

```python
from __future__ import annotations

from abc import ABC
from collections.abc import Callable, Mapping
from typing import Any, TypeVar

T = TypeVar("T")


class BaseInstrument(ABC):
    def __init__(
        self,
        *,
        metadata: DriverMetadata,
        transport_factory: TransportFactory,
        configuration: DriverConfiguration,
        logger: EventSink | None = None,
        clock: Clock | None = None,
        retry_policy: RetryPolicy | None = None,
        timeout_policy: TimeoutPolicy | None = None,
        observer: ProtocolObserver | None = None,
    ) -> None:
        self._metadata = metadata
        self._transport_factory = transport_factory
        self._configuration = configuration
        self._logger = logger or DefaultEventSink()
        self._clock = clock or SystemClock()
        self._retry_policy = retry_policy or RetryPolicy.no_retry()
        self._timeout_policy = timeout_policy or TimeoutPolicy.defaults()
        self._observer = observer or NullProtocolObserver()
        self._sessions = SessionRegistry()

    def _connect_session(self, request: ConnectionRequest) -> ConnectionInfo:
        """Final lifecycle orchestration; concrete behaviour enters through hooks."""
        ...

    def _disconnect_session(self, alias: str, reason: CleanupReason) -> None:
        """Run safe-state, cleanup and transport release deterministically."""
        ...

    def _execute_operation(
        self,
        operation_name: str,
        operation: Callable[[InstrumentSession, OperationContext], T],
        *,
        alias: str = "default",
        timeout: float | None = None,
        retry_policy: RetryPolicy | None = None,
        idempotent: bool = False,
        required_states: tuple[SessionState, ...] = (
            SessionState.CONNECTED,
            SessionState.CONFIGURED,
        ),
        method_name: str | None = None,
        protocol_vector: str | None = None,
    ) -> T:
        ...

    def _build_transport(self, request: ConnectionRequest) -> Transport:
        raise NotImplementedError

    def _probe_communication(
        self,
        session: InstrumentSession,
        context: OperationContext,
    ) -> None:
        raise NotImplementedError

    def _read_identity(
        self,
        session: InstrumentSession,
        context: OperationContext,
    ) -> InstrumentIdentity | None:
        return None

    def _apply_safe_state(
        self,
        session: InstrumentSession,
        reason: CleanupReason,
    ) -> SafeStateResult:
        return SafeStateResult.not_applicable()
```

Note that `BaseInstrument` carries no framework-specific class attributes (no automatic-export flags, no framework scope declarations, no framework version fields); those concerns belong entirely to an adapter, never to the driver.

The concrete `driver.py` shall expose only LPDS-002-approved public methods and shall delegate infrastructure work to these base services. Any framework adapter shall be implemented as a separate module or package that wraps the concrete driver instance; it shall not be merged into the driver class.

---

## 33. Testing Requirements for `lpds-core`

### 33.1 Unit tests

The shared base package shall have deterministic unit tests covering at least:

- construction without hardware access;
- metadata validation;
- alias normalization and ambiguity;
- one-session and multi-session behaviour;
- every legal and illegal state transition;
- successful connection;
- transport-open failure;
- probe failure after open;
- identity failure policy;
- partial connection cleanup;
- repeated connect;
- successful disconnect;
- safe-state failure with continued close;
- transport-close failure;
- repeated disconnect;
- close-all aggregation;
- timeout precedence and invalid values;
- one absolute deadline across retries;
- retry eligibility and prohibited retries;
- recovery outcomes;
- lock timeout and concurrent-call rejection;
- causal exception preservation;
- redaction;
- structured event correlation;
- diagnostics export and checksums;
- framework-neutral result conversion;
- no accidental public API exposure through reflection or framework auto-registration.

### 33.2 Contract tests

A reusable contract-test suite shall be provided for concrete drivers. The suite should accept a test driver and fake transport and verify that the concrete implementation honours base lifecycle and hook requirements.

### 33.3 Adapter conformance tests

For each supported framework adapter, adapter-level conformance tests shall verify that:

- the concrete driver, and any adapter wrapping it, import without hardware;
- only approved common and device-specific public methods are visible through the adapter;
- base-supplied common methods have the LPDS-002 signatures;
- errors become actionable, adapter-appropriate failures (for example a pytest assertion failure, a non-zero CLI exit with message, or an HTTP error response);
- session aliases and return values convert correctly to the adapter's expected types;
- teardown closes all sessions after a failed test.

### 33.4 Protocol-conformance support

The test doubles and observer shall permit LPDS-019 to associate each device-facing public API call with captured outbound and inbound protocol evidence.

### 33.5 Compatibility matrix

`lpds-core` shall be tested against the supported Python version matrix and, for each maintained adapter, against its supported framework version matrix (for example pytest, or a CLI library's own supported version range), and against representative driver classes, including at least:

- query-oriented instrument;
- command-only instrument or relay;
- binary serial protocol;
- vendor SDK adapter;
- multi-session driver;
- single-session driver.

---

## 34. Concrete Driver Requirements

Each concrete LPDS driver using `BaseInstrument` shall:

1. declare a compatible `lpds-core` version range;
2. inherit from the approved base class or an approved compatibility adapter;
3. avoid automatic, reflection-based exposure of methods to any framework, exposing only the intentionally documented public API;
4. perform no implicit hardware access during import or ordinary construction;
5. implement required transport and communication-probe hooks;
6. implement safe-state behaviour when the device controls a hazardous or persistent state;
7. route device-facing operations through the base operation wrapper or an approved equivalent;
8. declare operation idempotency before enabling automatic retry;
9. preserve finite timeout behaviour;
10. expose metadata and capabilities consistent with documentation and LPDS-017;
11. support diagnostic export;
12. remain compatible with LPDS-019 observation and correlation;
13. document concurrency and session limits;
14. provide lifecycle and failure regression tests;
15. record any approved deviation in `review/known_risks.md` and requirement traceability.

---

## 35. Lifecycle Integration

### Gate 1 — Architecture and Skeleton

- select the compatible `lpds-core` version;
- create the concrete driver, driver core, protocol, and transport boundaries;
- implement import-safe construction;
- define metadata, capabilities, connection request, and state model;
- implement fake transport and base contract-test skeleton;
- document extension hooks and deviations.

### Gate 2 — Core Implementation

- implement connect, probe, identity, disconnect, and primary operations;
- route operations through timeout, lock, logging, and error infrastructure;
- add unit and adapter-level lifecycle tests;
- add initial LPDS-019 observer correlation.

### Gate 3 — Extended Features

- implement recovery, multiple sessions where applicable, diagnostics, advanced capabilities, aliases, and edge cases;
- verify retry classification and safe-state behaviour;
- update LPDS-017 metadata.

### Gate 4 — Tests and Documentation

- execute the reusable base contract suite;
- complete lifecycle, timeout, retry, recovery, cleanup, concurrency, and diagnostics tests;
- document public common behaviour and troubleshooting;
- verify generated API documentation and its publication (for example Sphinx or pdoc output and GitHub Pages).

### Gate 5 — Review and Release

- verify the declared `lpds-core` dependency against packaged artifacts;
- review all lifecycle overrides and deviations;
- confirm no accidental public API exposure;
- confirm LPDS-019 evidence correlation;
- record code, architecture, API, documentation, and release-readiness reviews.

---

## 36. Compatibility and Change Control

### 36.1 Shared-core semantic versioning

The shared core shall use semantic compatibility rules:

- patch release — compatible defect correction with no intentional public or hook contract change;
- minor release — backward-compatible addition;
- major release — approved breaking change.

### 36.2 Protected compatibility surface

The compatibility surface includes:

- constructor dependency contracts;
- required data-model fields;
- session-state meanings;
- lifecycle semantics;
- protected extension hooks;
- error categories;
- diagnostics schema versioning;
- observer correlation fields;
- common public API method implementation semantics adopted by LPDS-002.

### 36.3 Driver update obligation

When a driver changes its required base version, the same driver revision shall update:

- dependency metadata;
- lock or release manifest;
- compatibility matrix;
- tests;
- history;
- architecture review;
- release notes;
- diagnostic version evidence.

### 36.4 Deprecation

A protected hook or shared public semantic shall be deprecated before removal. The replacement and compatibility interval shall be documented.

### 36.5 Schema evolution

Machine-readable diagnostics, capabilities, and metadata shall carry schema versions. Additive fields should remain backward compatible; removals or semantic changes require a schema-version change.

---

## 37. Acceptance Criteria

An implementation passes LPDS-003 only when:

1. the base class can be imported and constructed without hardware access;
2. concrete drivers expose their public API explicitly, not through blanket framework reflection;
3. connection lifecycle is deterministic and finite;
4. partial connection failures release all acquired resources;
5. repeated connect and disconnect behaviour is defined and tested;
6. every session has explicit state and legal transitions are enforced;
7. operation locking prevents unsafe concurrent access;
8. all blocking paths use finite deadlines or an approved documented exception;
9. retries occur only for explicitly retry-safe operations;
10. recovery does not conceal the original failed operation;
11. safe-state and cleanup continue as far as practical after individual failures;
12. errors preserve category, context, and causal information;
13. logs and diagnostics are structured, correlated, and redacted;
14. driver and `lpds-core` metadata are available without device communication;
15. dynamic device identity and capabilities are not invented before connection;
16. public return values are convertible to stable, framework-neutral forms usable by any adapter;
17. transport and protocol internals are not accidentally exposed as part of the public API;
18. LPDS-019 can correlate public calls with protocol-boundary evidence;
19. the reusable base contract-test suite passes for the concrete driver;
20. required history, reviews, documentation, and compatibility evidence are current.

---

## 38. Failure Conditions

LPDS-003 conformance shall fail when any of the following applies:

- driver import or construction opens hardware unexpectedly;
- automatic, reflection-based method export (by the driver or an adapter) exposes private or transport methods;
- connect reports success without a usable transport and required communication verification;
- a partial connection failure leaks a transport, lock, alias, or resource reservation;
- disconnect stops after the first cleanup failure without attempting independent required cleanup;
- state transitions are implicit, contradictory, or unvalidated;
- an operation can block indefinitely;
- retry resets the caller's total timeout;
- a non-idempotent operation is automatically retried without approved duplicate protection;
- recovery converts an unverified failed operation into success;
- exceptions lose the original cause without justification;
- secrets are written to persistent logs or diagnostics;
- session selection is ambiguous or arbitrary;
- concurrent calls can interleave on a non-thread-safe session;
- safe-state behaviour is absent for a driver that controls a hazardous or persistent output;
- the base class contains duplicated vendor protocol syntax;
- a concrete driver overrides lifecycle orchestration without review and regression coverage;
- `lpds-core` version evidence or compatibility declaration is missing;
- LPDS-019 protocol evidence cannot be correlated with the originating operation.

---

## 39. Review Checklist

1. Is `BaseInstrument` limited to shared infrastructure concerns?
2. Does import and construction avoid all device I/O?
3. Is the concrete driver's public API explicitly and intentionally exposed, not via blanket reflection?
4. Are private hooks and transport primitives hidden from every framework adapter?
5. Is session ownership explicit?
6. Are aliases normalized and selected deterministically?
7. Is the state machine enforced?
8. Does connect verify communication where safely possible?
9. Are partial connection failures fully cleaned up?
10. Are repeated connect and disconnect semantics defined?
11. Does disconnect attempt safe-state, cleanup, close, and release even after intermediate failures?
12. Are deadlines finite and monotonic?
13. Do retries share the original deadline?
14. Is each retried operation explicitly idempotent or duplicate-protected?
15. Is recovery separated from retry?
16. Are errors categorized and causally preserved?
17. Are logs structured and secrets redacted before persistence?
18. Can diagnostics be exported without changing device state?
19. Are metadata and static capabilities available offline?
20. Are dynamic capabilities marked unavailable until verified?
21. Is one session protected against unsafe concurrent access?
22. Are multi-session limits documented and tested?
23. Are safe-state semantics implemented at the correct layer?
24. Can LPDS-019 correlate a public API call with protocol traces?
25. Does the reusable contract-test suite pass?
26. Is the `lpds-core` compatibility range declared and verified?
27. Are all lifecycle overrides justified and reviewed?
28. Are LPDS-017, documentation, generated API docs, tests, and implementation synchronized?

---

## 40. Minimum Definition of Done

LPDS-003 is complete for the platform when:

- a versioned shared `lpds-core` implementation exists;
- the required state, session, timeout, retry, recovery, error, logging, diagnostics, redaction, conversion, and observation components are implemented;
- the reference base class and protected hooks are documented;
- deterministic fake clock, fake transport, and protocol observer test utilities exist;
- the shared package's unit and compatibility tests pass;
- a reusable concrete-driver contract-test suite exists;
- at least one query-oriented, one command-oriented, and one non-text or SDK-based reference driver pass the contract suite;
- documentation and migration guidance are published;
- no Critical or unresolved Major review finding remains.

LPDS-003 is complete for an individual driver when:

- the driver declares and uses a compatible shared-core version;
- all applicable concrete-driver requirements in Section 34 pass;
- lifecycle and failure tests pass;
- LPDS-019 observation correlation is demonstrated;
- the current release review records LPDS-003 compliance or approved deviations.

---

## 41. Goal

Provide one production-grade, transport-independent foundation that makes LPDS driver lifecycle, state, timeout, retry, recovery, logging, diagnostics, cleanup, and framework-coupling-prevention behaviour predictable across all supported hardware drivers while leaving device semantics and protocol implementation in their proper layers.

---

## Appendix A — Recommended Standard Session Dataclass

```python
@dataclass(slots=True)
class InstrumentSession:
    alias: str
    normalized_alias: str
    generation: str
    state: SessionState
    transport: Transport | None
    connection_request: ConnectionRequest
    effective_configuration: Mapping[str, object]
    identity: InstrumentIdentity | None
    connected_at: datetime | None
    last_communication_at: datetime | None
    last_error: ErrorRecord | None
    operation_lock: threading.RLock
    cancellation: CancellationToken
    cleanup_stack: CleanupStack
    annotations: dict[str, object]
```

The concrete driver shall not mutate lifecycle-owned fields outside approved base methods.

---

## Appendix B — Recommended Retry Decision Record

```python
@dataclass(frozen=True, slots=True)
class RetryDecision:
    retry: bool
    reason: str
    delay_s: float
    next_attempt: int
    remaining_s: float
    recovery_required: bool
```

Every retry decision should be available to structured evidence.

---

## Appendix C — Recommended Operation Result Evidence

```json
{
  "correlation_id": "5f6d8ca7-8bd9-4c87-a77b-ef15e6a23b23",
  "driver": "example_instrument",
  "driver_version": "26.01",
  "lpds_core_version": "1.0.0",
  "alias": "default",
  "session_generation": "3",
  "method": "get_identity",
  "operation": "read_identity",
  "protocol_vector": "IDN-001",
  "state_before": "CONNECTED",
  "state_after": "CONNECTED",
  "attempts": 1,
  "duration_s": 0.084,
  "outcome": "PASS"
}
```

---

## Appendix D — Design Decisions

### D.1 Multiple sessions are supported by the base

The shared infrastructure supports named sessions because many laboratory workflows use multiple same-class instruments. A concrete driver may intentionally restrict the maximum to one.

### D.2 No automatic retries by default

Hardware commands often have irreversible or duplicate side effects. Retry therefore requires explicit safety and idempotency classification.

### D.3 Safe-state is a hook, not a generic command

The base orchestrates cleanup but cannot know whether the safest action is output off, relay open, motion stop, load input off, chamber hold, local mode, or no state change.

### D.4 LPDS-002 remains the public API authority

LPDS-003 implements common semantics. This avoids public API drift when shared infrastructure evolves.

### D.5 `lpds-core` is a shared dependency

One authoritative version prevents copied base implementations from diverging across driver repositories. Offline packages may carry the approved wheel without forking it.
