# LPDS-013 — Driver Capability Model and Feature Discovery Specification

**Version:** 1.0  
**Document ID:** LPDS-013  
**Status:** Draft project requirement  
**Applies to:** All LPDS Python instrument driver packages  
**Primary audience:** Driver developers, adapter developers, generic application developers, test planners, GUI/CLI developers, orchestration systems, and AI agents

---

## 1. Purpose

This specification defines the mandatory, machine-readable **capability model** that allows a generic application to discover what an LPDS driver can do without importing driver source code, hard-coding device-specific method names, or interpreting free-form documentation.

The model shall allow a generic application to determine:

1. driver identity and version;
2. supported functional capabilities;
3. public API methods that implement each capability;
4. required and optional arguments;
5. argument types, ranges, units, enumerations, and defaults;
6. returned values and result schemas;
7. required connection and driver states;
8. capability availability in the current runtime state;
9. side effects, timing, risk, and resource use;
10. supported channels, modes, features, and limits;
11. safe setup, execution, and cleanup operations;
12. capability dependencies and conflicts;
13. deprecation, aliases, and compatibility information;
14. how to invoke the capability through the driver's public Python API (and, where applicable, through a framework adapter);
15. whether capability information is static, configured, detected, or queried from the device.

The intended discovery path is:

```text
Generic application
        ↓
LPDS capability discovery interface
        ↓
machine-readable driver capability model
        ↓
selected capability and invocation binding
        ↓
public API method on the driver
        ↓
driver and physical device
```

A generic application normally calls the public API method directly. When the application is itself a framework-specific consumer (a pytest test suite, a CLI, a REST client), a thin framework adapter may sit between the application and the driver, translating calls and results — the adapter contains no device logic and the discovery contract described here is unchanged by its presence.

The capability model is a **functional discovery contract**. It is not merely generated method documentation.

---

## 2. Goals

LPDS-013 shall enable the following classes of generic application:

- device setup applications;
- instrument control panels;
- test-sequence editors;
- automated test generators;
- automatic bench planners;
- test-execution dashboards;
- remote-control services;
- capability browsers;
- driver compatibility checkers;
- multi-instrument orchestration systems;
- AI-assisted test-development tools.

A conforming application shall be able to discover and use common driver functions without a device-specific software plug-in when those functions are represented by the standard capability taxonomy defined in this specification.

---

## 3. Scope Boundary

### 3.1 In scope

LPDS-013 covers:

- a canonical capability taxonomy;
- stable capability identifiers;
- capability metadata and schemas;
- mapping capabilities to public driver API methods;
- discovery of supported functionality;
- static and runtime capability information;
- state-aware availability;
- device-derived limits and supported options;
- channel and subsystem discovery;
- argument and return-value metadata;
- units, numeric constraints, and enumerations;
- preconditions, postconditions, and side effects;
- resource ownership and conflicts;
- risk and safety metadata;
- timing and stabilization metadata;
- feature dependencies;
- aliases and deprecation;
- model validation and compatibility;
- discovery through the driver's public Python API and through framework adapters built on it;
- cached and live discovery modes;
- evidence required to prove model accuracy.

### 3.2 Out of scope

LPDS-013 does not define:

- the complete mandatory public driver API;
- the internal Python architecture of a driver;
- transport implementation details;
- complete device protocol mappings;
- full vendor-manual feature coverage;
- physical measurement accuracy;
- calibration procedures;
- test-bench wiring;
- complete AI planning semantics;
- implementation lifecycle and release gates;
- package structure beyond the LPDS-013 artifacts;
- graphical layout of a generic application;
- protocol conformance testing;
- security authentication protocols.

These matters are addressed by other LPDS specifications and device-specific requirements.

---

## 4. Normative Terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement; deviations require justification;
- **may** — permitted implementation choice;
- **capability** — a normalized function the driver can perform;
- **feature** — a supported option, mode, subsystem, or device characteristic;
- **capability binding** — the mapping from a capability to a public driver API method, and, where applicable, to the framework adapter bindings built on top of it;
- **static discovery** — capability information available without opening the device;
- **configured discovery** — capability information derived from driver configuration;
- **live discovery** — capability information obtained from the connected device;
- **effective capability model** — the merged result of static, configured, and live discovery;
- **availability** — whether a capability can be invoked in the current state;
- **support state** — whether a capability is implemented, unavailable, restricted, or unknown.

---

## 5. Design Principles

### 5.1 Stable semantics

Capability meaning shall be represented by a stable identifier rather than inferred only from a human-readable public method name.

### 5.2 Method independence

A generic application shall identify the intended function by `capability_id`. The model shall separately provide the public method used to invoke it.

### 5.3 Explicit constraints

A generic application shall not be required to parse prose to determine valid ranges, units, enumerations, required states, or return types.

### 5.4 State awareness

The model shall distinguish between:

- implemented capability;
- capability available in the current connection and device state;
- capability temporarily blocked by another operation;
- capability unsupported by the detected model or installed module;
- capability whose support cannot be determined.

### 5.5 Safe generic use

Capabilities that can energize outputs, move mechanisms, modify calibration, erase data, reset hardware, change firmware, or otherwise create risk shall expose explicit risk and confirmation metadata.

### 5.6 Conservative discovery

The driver shall not report a capability as supported unless the implementation can invoke it through the declared public interface.

### 5.7 Deterministic output

For the same driver version, configuration, device identity, installed modules, and device state, discovery output shall be semantically deterministic.

### 5.8 Extensibility

Vendor-specific capabilities may be added without changing the meaning of standard LPDS capability identifiers.

---

## 6. Required Artifacts

Each driver package shall provide:

```text
<driver_name>/
├── capability/
│   ├── capability_model.yaml
│   ├── capability_model.schema.json
│   ├── capability_taxonomy_extensions.yaml      # optional
│   └── examples/
│       ├── capability_snapshot.json
│       └── capability_query_examples.py
├── tests/
│   └── capability/
│       ├── test_capability_model_validation.py
│       ├── test_capability_binding_validation.py
│       ├── test_capability_runtime_discovery.py
│       └── expected/
│           └── minimum_capabilities.yaml
└── docs/
    └── capability_model.md
```

Equivalent locations may be used only when the package specification explicitly defines them and all references remain deterministic.

The release package shall contain a validated static capability model even when live device discovery is also supported.

---

## 7. Discovery Interfaces

### 7.1 Mandatory public API methods

Every LPDS driver shall expose the following public discovery methods, or project-standard aliases defined by LPDS-002, directly on the driver class:

```python
get_capability_model(...)
get_driver_capability(capability_id, ...)
find_driver_capabilities(...)
get_driver_features(...)
refresh_driver_capabilities(...)
validate_driver_capabilities(...)
```

`get_capability_model` is deliberately distinct from LPDS-002's `get_driver_capabilities`, which returns the fixed, flat `list[str]` of LPDS-002 group-level capability names. `get_capability_model` returns the richer LPDS-013 structure defined below. A driver shall implement both, and the AI Driver Contract shall map each LPDS-002 group name to its corresponding LPDS-013 `capability_id` entries.

The canonical behavior shall be:

| Method | Required behavior |
|---|---|
| `get_capability_model` | Return the effective capability model or a filtered capability list. |
| `get_driver_capability` | Return one capability by exact capability ID. |
| `find_driver_capabilities` | Return capabilities matching structured filters. |
| `get_driver_features` | Return normalized device and driver feature data. |
| `refresh_driver_capabilities` | Re-evaluate configured and live capability information. |
| `validate_driver_capabilities` | Validate the model and bindings; return a structured validation result. |

A driver may expose additional convenience discovery methods, but they shall not replace the canonical discovery behavior. The exact class layout (methods vs. properties, module organization) is implementation-defined, but the public behavior and returned schemas shall conform to this specification.

### 7.2 Framework adapter bindings

Where a driver is consumed through a framework-specific adapter (a pytest fixture library, a CLI command set, a REST layer, ...), the adapter shall expose the same discovery operations under whatever naming convention its framework requires, by calling straight through to the driver's public discovery methods. An adapter shall not reimplement discovery logic, filter results independently of the driver, or cache a copy of the model that can diverge from the driver's own state. Multiple adapters may wrap the same driver instance simultaneously without conflict, since none of them hold discovery state of their own.

Example: CLI adapter

```text
$ keysight-n6700 get-capability-model
$ keysight-n6700 get-driver-capability measure.voltage.dc
```

Here, `get-capability-model` and `get-driver-capability` are thin adapter subcommands that call `driver.get_capability_model()` and `driver.get_driver_capability(...)` respectively and translate the returned values into whatever representation the framework expects (see §7.3). A driver may document the expected adapter method-to-command naming convention, but the mapping itself is an adapter concern, not a driver requirement.

### 7.3 Return transport

The discovery methods shall return values composed only of:

- dictionaries;
- lists;
- strings;
- integers;
- finite floating-point values;
- booleans;
- `None` where explicitly allowed.

The default return shall not require consumers to instantiate driver-specific Python classes. This keeps the return value directly JSON-serializable and directly consumable by any framework adapter without a bespoke translation step.

### 7.4 Serialization

The model shall be serializable to JSON without loss of semantic information.

YAML may be used as the maintained source file. Runtime discovery results shall be exportable as JSON.

---

## 8. Discovery Modes

Every discovery response shall identify its discovery mode.

### 8.1 Static mode

Static mode shall be available without opening the transport or communicating with the device.

It shall describe:

- capabilities implemented by the installed driver;
- public method bindings;
- generic argument and result structure;
- driver-declared limits that do not depend on connected hardware;
- known supported model families;
- capability metadata that is valid before connection.

### 8.2 Configured mode

Configured mode may refine the model using:

- selected transport;
- configured model profile;
- enabled modules;
- feature flags;
- driver configuration file;
- simulator profile;
- user-selected channel count;
- optional dependency availability.

### 8.3 Live mode

Live mode may communicate with the device to determine:

- detected manufacturer and model;
- firmware version;
- installed modules;
- channel count;
- supported ranges;
- available modes;
- option codes;
- protocol feature support;
- current operating state;
- lock or interlock state;
- device-derived constraints.

Live discovery shall not make hazardous state changes solely to determine support.

### 8.4 Effective mode

The effective model shall merge static, configured, and live data according to the precedence rules in Section 22.

---

## 9. Top-Level Capability Model

The capability model shall contain at least:

```yaml
schema:
  name: lpds-capability-model
  version: "1.0"

driver:
  id: keysight_n6700
  name: Keysight N6700 Driver
  version: "26.03"
  api_version: "1.0"
  capability_model_version: "1.0"

source:
  discovery_mode: effective
  generated_at: "2026-07-26T12:00:00+03:00"
  connected: true
  stale: false

identity:
  manufacturer: Keysight Technologies
  model: N6705C
  serial_number: MY00000000
  firmware_version: A.03.10

features: {}
resources: []
capabilities: []
validation: {}
extensions: {}
```

### 9.1 Mandatory top-level fields

| Field | Requirement |
|---|---|
| `schema` | Capability schema name and version. |
| `driver` | Driver identity and version information. |
| `source` | Discovery source, timestamp, connection state, and freshness. |
| `identity` | Known device identity; unknown fields shall be explicit. |
| `features` | Normalized device and driver feature information. |
| `resources` | Channels, subsystems, endpoints, or exclusive resources. |
| `capabilities` | Capability records. |
| `validation` | Model and binding validation summary. |
| `extensions` | Namespaced vendor or project extensions. |

---

## 10. Capability Taxonomy

### 10.1 Capability ID format

A standard capability ID shall use lowercase dot-separated segments:

```text
<domain>.<object>.<operation>
```

Examples:

```text
connection.session.open
connection.session.close
identity.device.read
source.voltage.set
source.voltage.read
source.output.enable
measure.voltage.dc
measure.resistance.two_wire
load.current.set
switch.relay.close
switch.relay.open
system.error.read
system.reset.execute
file.calibration.upload
```

IDs shall be stable across driver versions when the capability semantics remain compatible.

### 10.2 Standard domains

LPDS defines the following primary domains:

| Domain | Purpose |
|---|---|
| `connection` | Open, close, reconnect, detect, and transport-session functions. |
| `identity` | Device, driver, firmware, module, and option identification. |
| `configuration` | Non-measurement configuration and operating modes. |
| `source` | Generate or apply electrical, digital, thermal, mechanical, or other stimuli. |
| `measure` | Acquire measured values. |
| `load` | Apply an electrical or mechanical load. |
| `switch` | Relays, matrices, routing, and connection states. |
| `trigger` | Trigger setup, arming, initiation, and status. |
| `acquisition` | Sampling, capture, buffering, and trace acquisition. |
| `waveform` | Waveform definition, generation, and retrieval. |
| `channel` | Channel selection, configuration, and metadata. |
| `status` | Operational, condition, event, and readiness status. |
| `system` | Reset, self-test, error queue, time, health, and general system functions. |
| `safety` | Output inhibition, interlocks, limits, and emergency actions. |
| `calibration` | Calibration data and calibration workflows. |
| `file` | Device file and data transfer operations. |
| `logging` | Driver or device logging and diagnostic capture. |
| `firmware` | Firmware identity, update, and rollback operations. |
| `simulation` | Simulator controls and simulation-state discovery. |
| `utility` | Generic conversion or helper operations with no better domain. |

### 10.3 Standard operation verbs

The final segment should use a normalized verb where applicable:

```text
open, close, connect, disconnect, reconnect, detect,
read, query, get, set, configure, enable, disable,
start, stop, initiate, abort, clear, reset, execute,
upload, download, list, delete, validate, refresh,
measure, acquire, route, select, wait, check
```

`get` shall normally represent driver-held or cached information.  
`read` or `query` shall normally represent an operation that communicates with the device.  
`measure` shall represent a measurement operation with measurement semantics.

### 10.4 Vendor-specific IDs

Vendor-specific capabilities shall be namespaced:

```text
vendor.<vendor_id>.<domain>.<object>.<operation>
```

Example:

```text
vendor.keysight.n6700.smu.quadrant.configure
```

A vendor-specific capability shall not redefine a standard LPDS capability ID with incompatible semantics.

---

## 11. Capability Record

Each capability record shall contain at least:

```yaml
capability_id: source.voltage.set
display_name: Set DC Voltage
description: Set the programmed DC output voltage for one channel.
category: source
standard: true
support:
  state: supported
  reason: null
  confidence: confirmed
binding:
  python_method: set_dc_voltage
  canonical_method: set_dc_voltage
  aliases: []
  driver_class: keysight_n6700.KeysightN6700
  adapters: {}
arguments: []
returns: []
preconditions: []
postconditions: []
side_effects: []
availability: {}
timing: {}
risk: {}
resources: []
dependencies: []
conflicts: []
cleanup: []
provenance: {}
lifecycle: {}
```

### 11.1 Identity fields

Each capability shall define:

- `capability_id`;
- `display_name`;
- `description`;
- `category`;
- `standard`.

### 11.2 Support fields

Each capability shall define:

- `support.state`;
- `support.reason`;
- `support.confidence`;
- `support.detected_for` when support is model-specific;
- `support.requires_option` when an optional module or licence is required.

### 11.3 Binding fields

Each executable capability shall define:

- `python_method` — the canonical public method or property on the driver that implements the capability;
- `canonical_method` — the stable canonical name, even when aliased;
- `aliases` — alternate public method names, if any;
- `driver_class` — the importable class implementing the capability;
- whether the binding is direct, compatibility, composed, or virtual;
- `adapters` (optional) — a namespaced map of framework-specific binding information (for example, a pytest fixture name, a CLI command, or a REST route) for each framework adapter that wraps this driver. Adapter entries are informational for tooling; the driver's own conformance does not depend on any adapter existing.

A capability may be descriptive-only only when `binding.executable` is `false` and the reason is explicit.

---

## 12. Support States

Only the following support states are permitted:

| State | Meaning |
|---|---|
| `supported` | Implemented and supported for the effective device/profile. |
| `unsupported` | Not supported by the driver or effective device/profile. |
| `conditional` | Supported only when declared conditions are satisfied. |
| `restricted` | Implemented but intentionally restricted by safety, role, policy, or profile. |
| `unavailable` | Supported in principle but currently unavailable because of runtime state or missing prerequisite. |
| `deprecated` | Supported for compatibility but scheduled for removal. |
| `unknown` | Support cannot be determined safely or reliably. |

`unknown` shall not be interpreted as `supported`.

---

## 13. Support Confidence

The `support.confidence` field shall use:

- `declared` — based on the static driver model;
- `configured` — based on selected configuration;
- `detected` — inferred from connected-device information;
- `confirmed` — verified by a safe device query or capability test;
- `assumed` — temporarily inferred; shall include justification;
- `unknown` — no reliable determination.

A generic application may use confidence to choose whether operator confirmation is needed.

---

## 14. Argument Model

Each argument shall provide equivalent information to:

```yaml
- name: voltage
  display_name: Voltage
  position: 2
  required: true
  type: number
  python_type: float
  transport_type: float
  unit: V
  quantity: electric_potential
  minimum: 0.0
  maximum: 20.0
  minimum_inclusive: true
  maximum_inclusive: true
  resolution: 0.001
  default: null
  enum: null
  pattern: null
  allow_none: false
  semantic_role: setpoint
  channel_dependent: true
  source: live
  description: Programmed channel voltage.
```

### 14.1 Required argument fields

Every argument shall define:

- name;
- required/optional status;
- logical type;
- framework-agnostic, JSON-serializable transport type;
- position or named-only behavior;
- default when optional;
- nullability;
- description.

### 14.2 Supported logical types

The following logical types are standard:

```text
string
integer
number
boolean
enum
list
object
binary
path
duration
timestamp
channel
resource_reference
capability_reference
```

### 14.3 Units and quantities

Numeric physical values shall declare:

- unit;
- physical quantity;
- minimum and maximum where known;
- inclusivity;
- resolution or step where known;
- tolerance where relevant;
- whether values are device-, range-, mode-, or channel-dependent.

SI unit symbols should be used where appropriate.

A missing unit shall mean dimensionless only when explicitly declared.

### 14.4 Enumerations

Enumerated arguments shall define stable machine values and human-readable labels:

```yaml
enum:
  - value: CC
    label: Constant Current
    aliases: [CURRENT]
  - value: CV
    label: Constant Voltage
    aliases: [VOLTAGE]
```

### 14.5 Dynamic constraints

When a constraint depends on another argument or feature, the model shall express the dependency:

```yaml
constraints:
  - when:
      argument: range
      equals: LOW
    maximum: 1.0
  - when:
      feature: module.model
      equals: N6775A
    maximum: 20.0
```

Free-form descriptions may supplement, but shall not replace, structured constraints.

### 14.6 Sensitive arguments

Credentials, tokens, and secrets shall be marked:

```yaml
sensitive: true
redact_in_logs: true
```

Discovery output shall not contain secret values.

---

## 15. Return Model

Each return value shall define:

- name;
- type;
- framework-agnostic, JSON-serializable representation;
- unit and physical quantity when applicable;
- schema for objects or lists;
- nullability;
- meaning;
- whether the value is measured, programmed, cached, calculated, or device-reported;
- timestamp behavior when applicable;
- quality or validity indicators where applicable.

Example:

```yaml
returns:
  - name: measured_voltage
    type: number
    transport_type: float
    unit: V
    quantity: electric_potential
    value_origin: measured
    nullable: false
  - name: metadata
    type: object
    schema_ref: measurement_result_v1
    nullable: false
```

A structured measurement result should support:

```yaml
value: 4.9987
unit: V
timestamp: "2026-07-26T12:00:00.125+03:00"
channel: 1
status: valid
range: 10V
resolution: 0.0001
```

A driver may return a scalar for simple compatibility while also declaring an optional structured result capability.

---

## 16. Features Model

Features represent discoverable driver or device characteristics that are not themselves invocable operations.

Examples include:

- channel count;
- channel names;
- installed modules;
- supported measurement functions;
- supported source modes;
- ranges;
- maximum sample rate;
- trigger sources;
- transport types;
- simulator availability;
- binary block support;
- error queue support;
- remote/local mode support;
- firmware update support;
- hardware interlock presence.

Feature keys shall use lowercase dot-separated identifiers:

```yaml
features:
  channel.count:
    value: 4
    type: integer
    source: live
  transport.supported:
    value: [usb, tcpip, gpib]
    type: list
    source: static
  source.voltage.ranges:
    value: [5.0, 10.0, 20.0]
    unit: V
    type: list
    source: live
```

Each feature shall identify:

- value;
- type;
- source;
- confidence;
- freshness;
- scope;
- unknown reason when not known.

---

## 17. Resource Model

A resource is a logical or physical entity consumed, controlled, or observed by a capability.

Standard resource types include:

- driver instance;
- transport session;
- instrument;
- channel;
- output;
- input;
- relay;
- switch path;
- trigger bus;
- acquisition engine;
- file system;
- calibration store;
- firmware updater;
- fixture;
- operator;
- safety interlock.

Example:

```yaml
resources:
  - resource_id: channel.1
    type: channel
    display_name: Output Channel 1
    parent: instrument.main
    state: available
    attributes:
      module_model: N6775A
      four_quadrant: false
```

Capability records shall declare resource access:

```yaml
resources:
  - resource_id: channel.{channel}
    access: exclusive_write
  - resource_id: transport.session
    access: shared
```

Allowed access modes are:

- `read`;
- `shared`;
- `exclusive_write`;
- `exclusive_operation`;
- `consumes`;
- `provides`.

---

## 18. Preconditions, Postconditions, and State

### 18.1 Preconditions

A capability shall declare every required state that a generic application must establish before invocation.

Example:

```yaml
preconditions:
  - condition: driver.connected
    equals: true
    satisfaction_capability: connection.session.open
  - condition: channel.enabled
    equals: false
    reason: Range may only be changed with output disabled.
```

### 18.2 Postconditions

Capabilities that change state shall declare expected postconditions:

```yaml
postconditions:
  - condition: channel.voltage_setpoint
    equals_argument: voltage
```

### 18.3 State keys

State identifiers shall be stable and machine-readable, for example:

```text
driver.connected
driver.busy
device.remote
channel.<n>.enabled
channel.<n>.mode
acquisition.armed
calibration.active
firmware.update_active
safety.interlock_closed
```

### 18.4 State acquisition

The capability model shall identify how state is obtained:

- cached driver state;
- device query;
- calculated state;
- configured state;
- unknown.

A generic application shall not be told that a precondition is satisfied when the driver cannot determine it reliably.

---

## 19. Runtime Availability

Capability support and current availability are separate properties.

Each capability shall provide:

```yaml
availability:
  available: true
  state: ready
  reason: null
  checked_at: "2026-07-26T12:00:00+03:00"
  valid_for_s: 5
  blocking_resources: []
  missing_preconditions: []
```

Allowed availability states are:

- `ready`;
- `not_connected`;
- `busy`;
- `blocked`;
- `interlocked`;
- `missing_dependency`;
- `wrong_mode`;
- `wrong_device`;
- `restricted`;
- `stale`;
- `unknown`.

Availability checks shall not silently perform the operation being checked.

---

## 20. Side Effects and Cleanup

Each capability shall declare side effects, including:

- output state changes;
- signal generation;
- relay movement;
- device mode changes;
- data acquisition;
- buffer clearing;
- file creation or deletion;
- persistent configuration changes;
- calibration changes;
- reboot;
- transport reconnection;
- operator-visible effects.

Example:

```yaml
side_effects:
  - type: output_change
    target: channel.{channel}
    persistent_after_call: true

cleanup:
  required: true
  capabilities:
    - source.output.disable
  automatic_on_failure: recommended
```

A generic application shall be able to determine whether cleanup is required before it invokes a capability.

---

## 21. Timing and Execution Characteristics

Each executable capability shall declare:

```yaml
timing:
  timeout_s: 10
  typical_duration_s: 0.2
  maximum_duration_s: 5
  stabilization_s: 0.5
  polling_supported: false
  cancellable: false
  idempotent: true
  retry:
    safe: true
    maximum_attempts: 2
    backoff_s: 0.2
```

### 21.1 Timeout

A timeout shall be declared for every device-facing capability.

### 21.2 Stabilization

A capability that changes a physical condition shall declare stabilization behavior separately from protocol completion.

### 21.3 Idempotency

The model shall declare whether repeating an invocation with identical arguments is expected to produce an equivalent safe state.

### 21.4 Cancellation

Long-running capabilities shall declare whether they can be cancelled and which capability performs cancellation.

---

## 22. Merge and Precedence Rules

The effective capability model shall be created using this precedence, from highest to lowest:

1. validated live device data;
2. validated configured profile data;
3. static driver capability data;
4. explicit unknown value.

Live data shall not override a static safety restriction with a less restrictive value unless the static model explicitly permits that override.

The merged record shall retain provenance for overridden fields.

Example:

```yaml
maximum: 20.0
provenance:
  source: live
  supersedes:
    source: static
    value: 60.0
  reason: Detected module N6775A limit.
```

When sources conflict and no safe deterministic rule exists, the effective value shall be marked unknown or use the more restrictive safe limit.

---

## 23. Risk and Safety Metadata

Each executable capability shall define a risk level:

- `none`;
- `low`;
- `medium`;
- `high`;
- `critical`.

Example:

```yaml
risk:
  level: high
  categories: [energize_output, overcurrent]
  confirmation_required: true
  operator_required: false
  safe_in_simulation: true
  forbidden_when:
    - condition: safety.interlock_closed
      equals: false
  safe_defaults:
    voltage: 0.0
    current_limit: 0.01
```

### 23.1 Mandatory critical-operation metadata

Capabilities involving firmware updates, calibration writes, factory reset, data erasure, hazardous output, mechanism motion, or safety bypass shall define:

- confirmation requirement;
- required role or policy;
- interlocks;
- reversible/irreversible classification;
- recovery or rollback method;
- required cleanup;
- prohibited states.

### 23.2 Emergency capability

When a device supports a safe immediate shutdown, the model should expose:

```text
safety.emergency_stop.execute
```

or an equivalent standard safety capability.

---

## 24. Dependencies and Conflicts

A capability may depend on:

- another capability;
- optional Python package;
- transport type;
- device option;
- firmware version;
- module model;
- connected fixture;
- operator action;
- safety state;
- resource availability.

Example:

```yaml
dependencies:
  - type: capability
    id: connection.session.open
  - type: feature
    id: device.option.arb
    equals: true

conflicts:
  - type: resource
    id: acquisition.engine
    when_access: exclusive_operation
  - type: capability_state
    id: firmware.update.execute
    state: running
```

Dependencies shall be structured wherever possible.

---

## 25. Capability Composition

A capability binding may use one of four binding types:

| Type | Meaning |
|---|---|
| `direct` | One capability maps directly to one public API method. |
| `compatibility` | One capability maps to a compatibility-wrapper method retained on the driver's own public API for backward compatibility (distinct from a framework adapter, which lives outside the driver). |
| `composed` | One capability is implemented by an ordered sequence of public API method calls. |
| `virtual` | Capability is calculated or represented without a direct device action. |

A composed capability shall declare its steps:

```yaml
binding:
  type: composed
  executable: true
  steps:
    - capability_id: source.voltage.set
      argument_map:
        channel: $.channel
        voltage: $.voltage
    - capability_id: source.output.enable
      argument_map:
        channel: $.channel
```

Composed capabilities shall define failure cleanup and partial-execution behavior.

---

## 26. Query and Filtering Model

`find_driver_capabilities` shall support structured filtering by at least:

- capability ID or prefix;
- category/domain;
- support state;
- current availability;
- risk level;
- resource type or resource ID;
- argument quantity or unit;
- return quantity or unit;
- standard or vendor-specific status;
- deprecated status;
- tag;
- free-text search over display name and description.

Example usage:

```python
caps = driver.find_driver_capabilities(
    category="measure",
    available=True,
    return_quantity="electric_potential",
    maximum_risk="low",
)
```

Example: CLI adapter

```text
$ example-driver find-driver-capabilities \
    --category measure \
    --available \
    --return-quantity electric_potential \
    --maximum-risk low
```

The query shall return an empty list when no capabilities match. It shall not fail solely because there are no matches.

Exact lookup by capability ID shall fail clearly when the ID is unknown unless the caller requests a nullable result.

---

## 27. Channel and Subsystem Discovery

Drivers with channels or modular subsystems shall expose them as resources and features.

A channel record should include:

```yaml
resource_id: channel.1
type: channel
index: 1
name: Channel 1
label: Main output
present: true
enabled: false
module:
  manufacturer: Keysight
  model: N6775A
  serial_number: null
capabilities:
  - source.voltage.set
  - source.current_limit.set
  - measure.voltage.dc
limits:
  voltage:
    minimum: 0.0
    maximum: 20.0
    unit: V
```

Capabilities with channel-dependent limits shall support either:

- resource-specific capability records; or
- argument constraints indexed by channel/resource.

A generic application shall not assume all channels are identical.

---

## 28. Capability Lifecycle and Compatibility

Each capability shall contain lifecycle metadata:

```yaml
lifecycle:
  introduced_in: "26.01"
  changed_in: "26.03"
  deprecated: false
  deprecated_in: null
  removal_planned_in: null
  replacement_capability_id: null
  compatibility: backward_compatible
```

### 28.1 Compatibility classifications

Allowed classifications are:

- `backward_compatible`;
- `behavior_extended`;
- `constraint_tightened`;
- `constraint_relaxed`;
- `return_extended`;
- `breaking`.

### 28.2 Stable identifiers

A method rename shall not require a capability ID change when semantics remain compatible.

A semantic breaking change shall use a new capability ID or a versioned capability variant when both behaviors must coexist.

### 28.3 Aliases

Method aliases shall be declared in the binding. Framework adapter aliases (for example, alternate CLI subcommand names) shall be declared within that adapter's own binding entry. Capability aliases, when unavoidable, shall be declared separately and resolve to one canonical capability ID.

---

## 29. Provenance and Freshness

Every field whose value may vary by connection, configuration, module, firmware, or device state shall expose provenance directly or through inherited record-level metadata.

Allowed source values are:

- `static`;
- `configured`;
- `live`;
- `calculated`;
- `cached_live`;
- `operator`;
- `unknown`.

Live and cached values shall include:

- acquisition timestamp;
- device identity used;
- validity period or stale flag;
- query or capability used to obtain the value where practical.

A capability snapshot from one device shall not be reused for a different detected device identity without being marked stale and refreshed.

---

## 30. Error Model

Discovery operations shall use the standard LPDS exception model and return structured validation data where requested.

The model shall distinguish:

- schema error;
- binding error;
- unknown capability;
- unsupported capability;
- currently unavailable capability;
- live discovery timeout;
- identity mismatch;
- stale model;
- conflicting discovery sources;
- unsafe discovery operation;
- optional dependency missing.

Example validation result:

```yaml
valid: false
errors:
  - code: CAP_BINDING_METHOD_MISSING
    capability_id: measure.voltage.dc
    message: Bound public API method was not exported.
warnings:
  - code: CAP_LIVE_DISCOVERY_SKIPPED
    message: Device was not connected; static model only.
```

A validation warning shall not be silently converted into success when it invalidates a mandatory field.

---

## 31. Validation Requirements

`validate_driver_capabilities` shall verify at least:

1. schema validity;
2. unique capability IDs;
3. valid taxonomy format;
4. all mandatory fields;
5. valid argument and return schemas;
6. valid units and constraints;
7. minimum not greater than maximum;
8. defaults within declared constraints;
9. enum uniqueness;
10. valid support and availability states;
11. valid risk levels;
12. valid capability references;
13. valid resource references;
14. no unresolved dependency cycles unless explicitly supported;
15. executable capability bindings reference exported public API methods;
16. declared method signatures are compatible with capability arguments;
17. declared return metadata is compatible with the public contract;
18. aliases resolve correctly;
19. deprecated capabilities identify a replacement or explicit no-replacement reason;
20. discovery output is JSON serializable.

Validation shall return a machine-readable result and shall be usable as a release-gate test.

---

## 32. Binding Verification

Every executable capability shall be traceable to a public API method on the driver.

The binding validator shall compare the capability model against deterministic driver metadata obtained by Python introspection (for example, `inspect.signature`), a generated API manifest, or an equivalent mechanism.

The validator shall detect:

- missing bound method;
- normalized method-name collision;
- incompatible argument count;
- missing required argument metadata;
- incorrect default;
- undocumented alias;
- capability bound to a private helper;
- non-serializable return declaration;
- stale binding after a method rename or removal.

Where a framework adapter is present, the adapter's own keyword/fixture/command bindings may be verified separately by adapter-level tooling (for example, a CLI adapter's own `--help`-based verification), but that verification is an adapter concern and is not required for driver conformance.

LPDS-013 binding validation proves discoverability and metadata consistency. LPDS-019 proves callability and protocol behavior.

---

## 33. Runtime Discovery Safety

Live discovery shall be read-only unless a state change is unavoidable and explicitly approved.

The driver shall not perform the following merely to populate the capability model:

- energize an output;
- close an external relay path;
- move a mechanism;
- change calibration;
- erase files;
- update firmware;
- factory reset;
- alter safety limits;
- override an interlock;
- execute a self-test that can disturb a connected DUT without explicit permission.

Any live discovery action with side effects shall:

- be opt-in;
- declare the side effect;
- declare risk;
- define restoration behavior;
- record evidence.

---

## 34. Caching and Refresh

### 34.1 Static cache

Static driver capability information may be loaded once per driver version.

### 34.2 Live cache

Live discovery data may be cached only when:

- device identity is recorded;
- timestamp is recorded;
- staleness rules are defined;
- reconnect or identity change invalidates the cache;
- the caller can request a forced refresh.

### 34.3 Refresh behavior

`refresh_driver_capabilities` shall support:

```text
static
configured
live
effective
```

A live refresh shall clearly report partial success when some device queries fail.

---

## 35. Minimal Standard Capability Set

Every driver shall expose the capabilities that are applicable to its device class.

The following capabilities are mandatory when the corresponding function exists:

```text
connection.session.open
connection.session.close
connection.session.status
identity.device.read
identity.driver.read
system.error.read
system.error.clear
system.reset.execute
system.self_test.execute
safety.output.disable_all
```

A driver shall not invent a nonfunctional implementation only to satisfy this list. Non-applicable capabilities shall be absent or explicitly `unsupported` according to project policy.

At minimum, every driver shall expose:

```text
identity.driver.read
```

and its LPDS-013 discovery capabilities.

---

## 36. Example Capability — Voltage Source

```yaml
capability_id: source.voltage.set
display_name: Set DC Voltage
description: Set the programmed voltage on one output channel.
category: source
standard: true
support:
  state: supported
  reason: null
  confidence: confirmed
binding:
  executable: true
  type: direct
  python_method: set_dc_voltage
  canonical_method: set_dc_voltage
  aliases: [program_voltage]
  driver_class: keysight_n6700.KeysightN6700
  adapters:
    cli:
      command: set-dc-voltage
      aliases: [program-voltage]
arguments:
  - name: channel
    position: 1
    required: true
    type: channel
    transport_type: integer
    minimum: 1
    maximum_feature: channel.count
    allow_none: false
    semantic_role: target
  - name: voltage
    position: 2
    required: true
    type: number
    transport_type: float
    unit: V
    quantity: electric_potential
    minimum: 0.0
    maximum_by_resource: source.voltage.maximum
    resolution_by_resource: source.voltage.resolution
    allow_none: false
    semantic_role: setpoint
returns: []
preconditions:
  - condition: driver.connected
    equals: true
    satisfaction_capability: connection.session.open
  - condition: firmware.update_active
    equals: false
postconditions:
  - condition: channel.{channel}.voltage_setpoint
    equals_argument: voltage
side_effects:
  - type: programmed_state_change
    target: channel.{channel}
    persistent_after_call: true
availability:
  available: true
  state: ready
timing:
  timeout_s: 10
  typical_duration_s: 0.15
  stabilization_s: 0.0
  idempotent: true
  cancellable: false
  retry:
    safe: true
    maximum_attempts: 2
risk:
  level: medium
  categories: [output_configuration]
  confirmation_required: false
resources:
  - resource_id: channel.{channel}
    access: exclusive_write
  - resource_id: transport.session
    access: shared
dependencies:
  - type: capability
    id: connection.session.open
conflicts:
  - type: capability_state
    id: firmware.update.execute
    state: running
cleanup:
  required: false
provenance:
  source: effective
lifecycle:
  introduced_in: "26.01"
  deprecated: false
  compatibility: backward_compatible
```

---

## 37. Example Capability — Measurement

```yaml
capability_id: measure.voltage.dc
display_name: Measure DC Voltage
description: Perform a DC voltage measurement and return the measured value.
category: measure
standard: true
support:
  state: supported
  confidence: confirmed
binding:
  executable: true
  type: direct
  python_method: measure_dc_voltage
  canonical_method: measure_dc_voltage
  aliases: []
  driver_class: keysight_n6700.KeysightN6700
  adapters:
    cli:
      command: measure-dc-voltage
arguments:
  - name: channel
    position: 1
    required: false
    default: 1
    type: channel
    transport_type: integer
    minimum: 1
    maximum_feature: channel.count
  - name: samples
    position: 2
    required: false
    default: 1
    type: integer
    transport_type: integer
    minimum: 1
    maximum: 1000
returns:
  - name: voltage
    type: number
    transport_type: float
    unit: V
    quantity: electric_potential
    value_origin: measured
    nullable: false
preconditions:
  - condition: driver.connected
    equals: true
availability:
  available: true
  state: ready
timing:
  timeout_s: 30
  typical_duration_s: 0.5
  maximum_duration_s: 30
  stabilization_s: 0.0
  idempotent: false
  cancellable: false
  retry:
    safe: true
    maximum_attempts: 2
risk:
  level: low
  categories: [measurement]
resources:
  - resource_id: acquisition.engine
    access: exclusive_operation
  - resource_id: channel.{channel}
    access: read
cleanup:
  required: false
```

---

## 38. Example Discovery Workflow

```python
from keysight_n6700 import KeysightN6700

driver = KeysightN6700()

# Static discovery — no device connection required.
matches = driver.find_driver_capabilities(
    capability_id="measure.voltage.dc",
    maximum_risk="low",
)
assert matches, "expected measure.voltage.dc to be discoverable statically"

driver.connect("TCPIP0::192.168.0.10::inst0::INSTR")
try:
    driver.refresh_driver_capabilities(mode="effective")
    cap = driver.get_driver_capability("measure.voltage.dc")
    assert cap["availability"]["available"]

    voltage = driver.measure_dc_voltage(channel=1)
    print(f"Measured voltage: {voltage} V")
finally:
    driver.disconnect()
```

Example: pytest fixture adapter

```python
# adapters/pytest/keysight_n6700_fixtures.py
import pytest
from keysight_n6700 import KeysightN6700


@pytest.fixture
def psu():
    driver = KeysightN6700()
    model = driver.get_capability_model(mode="static")
    matches = driver.find_driver_capabilities(
        capability_id="measure.voltage.dc", maximum_risk="low"
    )
    assert matches

    driver.connect(resource="TCPIP0::192.168.0.10::inst0::INSTR")
    try:
        yield driver
    finally:
        driver.disconnect()


def test_discover_safe_voltage_measurement_capability(psu):
    model = psu.refresh_driver_capabilities(mode="effective")
    cap = psu.get_driver_capability("measure.voltage.dc")
    assert cap["availability"]["available"]
    voltage = psu.measure_dc_voltage(channel=1)
    print(f"Measured voltage: {voltage} V")
```

---

## 39. Generic Application Behavior

A generic application using LPDS-013 should:

1. load static discovery before connection;
2. validate schema compatibility;
3. show only supported capabilities by default;
4. distinguish unavailable from unsupported;
5. use display names for operators and IDs for internal logic;
6. render controls from structured argument metadata;
7. enforce declared ranges before invoking a method;
8. show units and enumerations explicitly;
9. request confirmation for high- and critical-risk operations;
10. honour resource conflicts and preconditions;
11. refresh live capabilities after connection, module change, firmware update, reset, or reconnect;
12. invalidate stale device-derived limits;
13. execute declared cleanup when an operation fails or a workflow ends;
14. store the capability-model version with generated tests or plans;
15. fail safely when required metadata is unknown.

The application shall not infer safety from the absence of risk metadata. Missing mandatory risk metadata is a model validation error.

---

## 40. Checklist

- [ ] The capability model loads without connecting to hardware (static discovery).
- [ ] Every capability has a stable, unique ID; standard IDs (Appendix A) are used where one applies, rather than inventing a vendor-specific one.
- [ ] Every executable capability binds to an actual exported public API method with a matching signature.
- [ ] Physical values declare units; return values are plain, serializable types.
- [ ] Support state (does the driver implement this) and current availability (can it run right now) are distinguishable — an unsupported capability and a temporarily-unavailable one aren't reported the same way.
- [ ] Live/configured discovery never performs an undeclared hazardous side effect, and doesn't require physical hardware to use static discovery.
- [ ] High-risk capabilities carry risk, precondition, and cleanup metadata.
- [ ] The model is JSON-serializable.

If you generate evidence for this (a `capability_validation.json`, a binding matrix), that's useful for a driver with many capabilities or external consumers relying on the model — it's not expected as a baseline artifact for every driver.

---

## 41. Change Control

Whenever a public feature, method, supported model, option, channel, range, unit, return schema, side effect, safety rule, dependency, or availability rule changes, the same driver revision shall update:

- static capability model;
- schema extension when required;
- public API binding, and framework adapter bindings where applicable;
- feature metadata;
- lifecycle metadata;
- capability examples;
- capability validation tests;
- LPDS-017 AI Driver Contract where semantics are affected;
- LPDS-019 protocol vectors where invocation or protocol behavior is affected;
- README and GitHub Pages capability documentation;
- `history/` change description;
- `review/` capability-model review.

A capability-affecting code change without the corresponding LPDS-013 update shall fail release review.

---

## 42. Integration with Other LPDS Specifications

### 44.1 LPDS-002 — Public API

LPDS-002 defines mandatory public method naming and signatures. LPDS-013 exposes those methods as machine-readable capability bindings.

### 44.2 LPDS-003 — BaseInstrument

LPDS-003 should provide common discovery implementation, model loading, validation, caching, and refresh behavior.

### 44.3 LPDS-005 — Package Specification

LPDS-005 defines the final required location of capability artifacts in every driver package.

### 44.4 LPDS-007 — Error and Exception Standard

LPDS-007 defines exceptions raised by discovery, validation, unavailable capability use, and stale or conflicting models.

### 44.5 LPDS-009 — Testing Standard

LPDS-009 defines unit, simulator, integration, and hardware testing required for capability discovery.

### 44.6 LPDS-010 — Driver Review Checklist

LPDS-010 shall include capability accuracy, binding integrity, safety metadata, compatibility, and evidence review.

### 44.7 LPDS-011 — Release Process

LPDS-011 shall require capability-model validation and a capability diff before release.

### 44.8 LPDS-017 — AI Driver Contract

LPDS-013 is the concise runtime discovery model for generic applications. LPDS-017 is the richer AI-readable semantic contract for one driver.

The two specifications shall agree on:

- capability identity;
- canonical method;
- arguments and returns;
- preconditions and postconditions;
- side effects;
- timing;
- risk;
- resources;
- limitations;
- errors.

LPDS-017 may contain planning and verification semantics that are intentionally outside LPDS-013.

### 44.9 LPDS-019 — Driver Call and Protocol Conformance

LPDS-019 shall verify that the public API method bound to an executable capability can be called and produces the declared protocol behavior — and, where a framework adapter is present, that the adapter correctly translates a framework-level call into that same method invocation.

LPDS-013 validates **what is discoverable and how it is described**. LPDS-019 validates **that the declared public call reaches the intended device protocol operation**.

---

## 43. Implementation Lifecycle Placement

LPDS-013 shall be maintained through every implementation phase:

### Gate 1 — Architecture and Skeleton

- create capability directory and schema;
- define initial taxonomy and IDs;
- implement static discovery skeleton;
- define common discovery interfaces.

### Gate 2 — Core Implementation

- bind implemented public API methods;
- define arguments, returns, states, and resources;
- add model and binding unit tests.

### Gate 3 — Extended Features

- add live discovery;
- add channel/module-dependent constraints;
- add dependencies, conflicts, and dynamic availability;
- update AI metadata.

### Gate 4 — Tests and Documentation

- run schema, binding, configured, simulator, and live-device tests;
- publish capability documentation and examples;
- generate evidence reports.

### Gate 5 — Review and Release

- review capability accuracy and safety;
- compare capability model with the previous release;
- resolve breaking changes;
- include updated capability artifacts in the release ZIP.

---

---

## 44. Goal

Provide a stable, safe, machine-readable model that allows generic applications to discover, present, validate, and invoke LPDS driver features without device-specific source-code knowledge or hard-coded method-name mappings.

---

## Appendix A — Recommended Standard Capability IDs

The following list is non-exhaustive. Drivers shall use applicable IDs and may propose additions through LPDS change control.

### Connection

```text
connection.session.open
connection.session.close
connection.session.reconnect
connection.session.status
connection.device.detect
connection.device.list
connection.timeout.get
connection.timeout.set
```

### Identity

```text
identity.driver.read
identity.device.read
identity.firmware.read
identity.modules.list
identity.options.list
```

### System

```text
system.error.read
system.error.clear
system.status.read
system.health.read
system.self_test.execute
system.reset.execute
system.local.execute
system.remote.execute
system.operation.wait
```

### Source

```text
source.output.enable
source.output.disable
source.output.disable_all
source.voltage.set
source.voltage.read
source.current.set
source.current.read
source.current_limit.set
source.power_limit.set
source.frequency.set
source.waveform.configure
source.waveform.start
source.waveform.stop
```

### Measurement

```text
measure.voltage.dc
measure.voltage.ac
measure.current.dc
measure.current.ac
measure.resistance.two_wire
measure.resistance.four_wire
measure.frequency
measure.period
measure.power.dc
measure.temperature
measure.continuity
measure.diode
```

### Load

```text
load.input.enable
load.input.disable
load.mode.set
load.current.set
load.voltage.set
load.resistance.set
load.power.set
load.transient.configure
load.transient.start
load.transient.stop
```

### Switching

```text
switch.relay.open
switch.relay.close
switch.relay.state.read
switch.all.open
switch.route.set
switch.route.read
switch.matrix.connect
switch.matrix.disconnect
```

### Trigger and acquisition

```text
trigger.source.set
trigger.level.set
trigger.arm
trigger.initiate
trigger.abort
trigger.status.read
acquisition.configure
acquisition.start
acquisition.stop
acquisition.status.read
acquisition.data.read
acquisition.buffer.clear
```

### Safety

```text
safety.interlock.read
safety.limits.read
safety.limits.set
safety.output.disable_all
safety.emergency_stop.execute
safety.safe_state.execute
```

### Calibration, files, and firmware

```text
calibration.status.read
calibration.data.read
calibration.data.write
calibration.start
calibration.abort
file.device.list
file.device.upload
file.device.download
file.device.delete
firmware.version.read
firmware.update.execute
firmware.rollback.execute
```

### Diagnostics and logging

```text
logging.driver.start
logging.driver.stop
logging.driver.export
logging.device.read
logging.trace.start
logging.trace.stop
logging.trace.export
system.diagnostics.read
```

---

## Appendix B — Minimum Static Capability Model Example

```yaml
schema:
  name: lpds-capability-model
  version: "1.0"

driver:
  id: example_meter
  name: Example Meter Driver
  version: "26.01"
  api_version: "1.0"
  capability_model_version: "1.0"

source:
  discovery_mode: static
  generated_at: null
  connected: false
  stale: false

identity:
  manufacturer: null
  model: null
  serial_number: null
  firmware_version: null

features:
  transport.supported:
    value: [visa, tcpip]
    type: list
    source: static
    confidence: declared

resources:
  - resource_id: instrument.main
    type: instrument
    display_name: Main instrument
    state: unknown

capabilities:
  - capability_id: identity.driver.read
    display_name: Get Driver Information
    description: Return driver identity and version information.
    category: identity
    standard: true
    support:
      state: supported
      reason: null
      confidence: declared
    binding:
      executable: true
      type: direct
      python_method: get_driver_information
      canonical_method: get_driver_information
      aliases: []
      driver_class: example_meter.ExampleMeter
      adapters:
        cli:
          command: get-driver-information
    arguments: []
    returns:
      - name: driver_information
        type: object
        transport_type: dict
        schema_ref: driver_identity_v1
        nullable: false
    preconditions: []
    postconditions: []
    side_effects: []
    availability:
      available: true
      state: ready
      reason: null
    timing:
      timeout_s: 1
      typical_duration_s: 0.01
      stabilization_s: 0
      idempotent: true
      cancellable: false
      retry:
        safe: true
        maximum_attempts: 1
    risk:
      level: none
      categories: []
      confirmation_required: false
    resources: []
    dependencies: []
    conflicts: []
    cleanup:
      required: false
    provenance:
      source: static
    lifecycle:
      introduced_in: "26.01"
      deprecated: false
      compatibility: backward_compatible

validation:
  valid: true
  errors: []
  warnings: []

extensions: {}
```

---

## Appendix C — LPDS-013 and LPDS-017 Information Boundary

| Information | LPDS-013 | LPDS-017 |
|---|---:|---:|
| Capability ID | Mandatory | Mandatory reference |
| Runtime availability | Mandatory | May consume |
| Method binding | Mandatory | Mandatory |
| Arguments and returns | Mandatory concise schema | Mandatory detailed semantics |
| Units and constraints | Mandatory | Mandatory |
| State preconditions | Mandatory | Mandatory, richer model |
| Side effects and risk | Mandatory | Mandatory |
| Timing and resources | Mandatory | Mandatory |
| Error catalogue | Capability-relevant summary | Full driver catalogue |
| Planning hints | Out of scope | Mandatory |
| Verification objectives | Reference only | Mandatory |
| Multi-step test synthesis semantics | Out of scope | In scope |
| Runtime feature filtering | Mandatory | Optional |
| Generic GUI control generation | Primary use case | Secondary use case |
| AI test-plan generation | Supporting input | Primary use case |

---

## Appendix D — Version 1.0 Design Decisions

Version 1.0 establishes:

- a stable capability-ID taxonomy;
- mandatory static discovery;
- optional configured and live discovery merged into an effective model;
- standardized support and availability states;
- structured arguments, returns, units, constraints, resources, risk, timing, and lifecycle data;
- a public Python discovery interface, with optional, informational framework adapter bindings;
- safe live discovery rules;
- deterministic validation and binding verification;
- explicit integration boundaries with LPDS-017 and LPDS-019.
