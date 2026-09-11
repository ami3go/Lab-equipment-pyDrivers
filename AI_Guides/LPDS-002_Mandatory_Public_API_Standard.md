# LPDS-002 — Mandatory Public API Standard

**Version:** 1.0
**Document ID:** LPDS-002
**Status:** Draft project requirement
**Applies to:** All LPDS Python instrument driver packages

---

## 1. Purpose

This specification defines the mandatory public API for every LPDS driver: naming conventions, type-hinted signatures, return types, error behavior, compatibility rules, and documentation requirements for the public Python methods exposed on a driver class.

The standard has four goals:

1. make different hardware drivers predictable to human developers integrating them;
2. make public methods safe and unambiguous for AI-generated test plans and automation code;
3. provide a stable contract that can be inventoried and tested automatically;
4. prevent private helpers, transport details, and accidental methods from becoming part of the public Python API.

The canonical public interface of an LPDS driver is its public Python API: the explicitly registered, documented set of public methods on the driver class, fully usable from a plain Python session with no test-automation framework installed. Any automation-framework adapter (pytest, a CLI, a REST layer, a GUI test bench, ...) is a separate, thin translation layer built on top of this API. An adapter shall not contradict the driver's public Python API, and shall not define behavior that does not trace back to exactly one canonical driver method.

---

## 2. Scope

### 2.1 In scope

LPDS-002 covers:

- public method discovery;
- mandatory universal driver methods;
- conditional capability method groups;
- canonical method names, aliases, and naming conventions;
- method signatures, arguments, defaults, and type conversion;
- return values and adapter-safe data types;
- connection and session semantics;
- state, safety, timeout, retry, and error behavior;
- method documentation and metadata (including risk-level metadata);
- API compatibility, deprecation, and removal;
- public API inventory and machine-readable API declaration;
- API-level acceptance criteria.

### 2.2 Out of scope

LPDS-002 does not define:

- device-specific protocol commands or frame formats;
- complete vendor-manual feature coverage;
- physical measurement accuracy;
- calibration accuracy;
- package layout outside API-related artifacts;
- detailed code architecture;
- the complete AI contract schema;
- bench topology or multi-instrument planning;
- protocol conformance execution details.

Those subjects are covered by device-specific requirements and other LPDS specifications.

---

## 3. Normative terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement; deviations require documented justification;
- **may** — permitted implementation choice;
- **canonical method** — the primary supported public method name;
- **alias** — an additional public method name mapped to a canonical method;
- **device-facing method** — a method that causes or may cause a transport, protocol, SDK, GPIO, or physical-device operation;
- **query method** — a method that obtains data without intentionally changing device state;
- **command method** — a method that intentionally changes driver or device state;
- **dangerous method** — a method capable of creating an unsafe electrical, mechanical, thermal, data-loss, or equipment-damage condition.

---

## 4. Public API layers

An LPDS driver may contain the following layers:

```text
automation-framework adapter (pytest, CLI, REST, ...)
        ↓
canonical public Python API (driver class methods)
        ↓
internal implementation methods
        ↓
validated device-domain service
        ↓
transport / vendor SDK / protocol implementation
        ↓
physical device or approved simulator
```

Only the canonical public Python API layer is mandatory for every driver. The adapter layer is optional, and multiple adapters may coexist over the same driver instance.

### 4.1 Canonical public Python API

The canonical API shall:

- be explicitly declared;
- be discoverable using Python introspection (`help()`, `inspect`, or the driver's public API registry);
- expose only supported public operations;
- use stable method names and signatures;
- return adapter-safe values (Section 11);
- be represented in the LPDS-017 AI Driver Contract;
- be covered by LPDS-019 call and protocol conformance tests;
- be fully usable, and independently verifiable, from a plain Python/pytest session with no automation framework installed.

### 4.2 Framework adapters

A driver may be wrapped by one or more framework adapters (pytest fixtures, a CLI, a REST layer, ...) for use inside a specific test-automation environment.

When an adapter is provided:

- adapter operations should map one-to-one to canonical public Python methods where practical;
- an adapter shall not introduce device logic, validation, or state of its own — it only translates calls and results between its framework and the driver's public API;
- argument names, defaults, return values, and exceptions exposed by the adapter shall remain semantically equivalent to the underlying Python API;
- an adapter's own naming convention (for example, a CLI adapter's kebab-case subcommand names, or a REST adapter's route names) is derived mechanically from the driver's `snake_case` method names and is not part of the driver's public API contract;
- adapters are documented and verified separately from the driver (thin translation-correctness tests, not device-logic tests).

### 4.3 Internal APIs

Internal helpers, transport methods, protocol encoders, parsers, caches, fixtures, and test hooks are not part of the public API unless explicitly declared.

Internal methods shall not be treated as stable or callable by any adapter.

---

## 5. Mandatory driver class declaration

Each LPDS driver shall explicitly declare and register its public API rather than relying on implicit exposure.

A driver should use the equivalent of:

```python
from .api import public_api
from .version import __version__


class ExampleDriver:
    """Plain Python driver for the Example device family."""

    __version__ = __version__

    def __init__(self, default_timeout_s: float = 5.0) -> None:
        ...

    @public_api(risk_level="low", tags=["lpds:connection", "lpds:low_risk"])
    def connect(self, resource: str | None = None, alias: str = "default",
                timeout_s: float | None = None, **options: object) -> dict[str, object]:
        ...
```

Mandatory rules:

1. automatic promotion of methods to public-API status shall be disabled: a method is not part of the public API merely because its name lacks a leading underscore;
2. every public method shall be explicitly registered — for example via a `@public_api(...)` decorator or an equivalent, explicit class-level registry — with its metadata (category, capability, risk level, tags);
3. the driver package version shall be exposed as an attribute readable from Python (for example `__version__`);
4. the driver's instance-sharing policy shall be explicitly declared and documented (Section 5.1);
5. driver construction shall not open hardware connections or change device state;
6. all device I/O shall occur only after an explicit public connection or setup operation;
7. helper methods shall not become part of the public API accidentally.

### 5.1 Driver instance-sharing policy

The driver shall document one of the following supported instance-sharing policies and the reason for it:

- **session-shared** — a single driver instance is reused for many related operations or test cases within one logical grouping; recommended default for stateful hardware drivers because it limits state leakage between unrelated groupings;
- **process-shared** — a single driver instance represents one physical resource shared across an entire test run, used when the underlying hardware or transport must be a singleton for the life of the process;
- **per-test** — a fresh driver instance is constructed and torn down for each logical test, used only when opening and closing a session per test is safe, efficient, and intended.

This policy governs how a caller or adapter constructs and shares driver instances; it is not a property enforced by the driver's constructor itself. Regardless of the declared policy, `disconnect()` shall be safe to call during teardown.

---

## 6. Method exposure rules

A callable shall be public only when all of the following are true:

1. it is explicitly registered as part of the public API;
2. it has a canonical public name;
3. it has complete documentation;
4. it has a stable signature;
5. its arguments and return values are adapter-safe (Section 11);
6. it is present in the public API inventory;
7. it is represented in the AI Driver Contract;
8. it has LPDS-019 callability coverage;
9. a device-facing method has a protocol vector or an approved exclusion.

The following shall not be exported as public API:

- names beginning with `_`;
- low-level transport handles;
- raw vendor SDK objects;
- protocol encoder or parser helpers;
- debug-only methods;
- unit-test hooks;
- methods whose behavior is undocumented;
- public names that would collide under a target adapter's name-normalization rules (for example, an adapter that ignores case, spaces, or underscores when deriving its own names).

---

## 7. Method naming standard

### 7.1 General form

Canonical method names shall:

- use `snake_case`;
- start with a clear action verb;
- describe one primary operation;
- avoid unexplained abbreviations;
- avoid implementation-specific internal class or helper names;
- avoid punctuation other than the underscore word separator, unless part of an established technical term;
- remain unique within the driver's public namespace;
- avoid embedding argument values in the method name unless explicitly approved.

Preferred:

```python
connect
get_identity
set_dc_voltage
measure_dc_current
enable_output
open_relay
upload_calibration_file
device_should_be_connected
```

Not permitted as canonical names:

```python
do_connect
connect_to_dmm_device
setDcVoltage
SetDCVoltage
voltage
run_command
send_data
open_channel_3_relay
```

An automation-framework adapter may derive its own, framework-idiomatic name from a canonical method name — for example, a CLI adapter mechanically converting `set_dc_voltage` into the subcommand `set-dc-voltage` by replacing underscores with hyphens. This translation is entirely the adapter's responsibility; the driver's canonical name is always the `snake_case` method name defined here.

### 7.2 Verb semantics

The following verbs have standardized meanings:

| Verb | Required meaning |
|---|---|
| `connect` | Establish a driver-to-device session. |
| `disconnect` | Close a session and release associated resources. |
| `check` | Perform a bounded diagnostic and return success data or raise a diagnostic error. |
| `get` | Return known state, configuration, metadata, or a queried value. It shall not imply a physical measurement trigger unless documented. |
| `read` | Obtain available data or device state, normally through a device read/query operation. |
| `measure` | Trigger or acquire a physical measurement. |
| `set` | Change one primary value or state. |
| `configure` | Apply a coherent group of settings. |
| `enable` / `disable` | Change a binary operating mode. |
| `start` / `stop` | Control a time-based, buffered, or asynchronous operation. |
| `open` / `close` | Control a relay, switch, path, valve, port, or similar domain object; not a transport session. |
| `reset` | Restore a defined reset state. Potential side effects shall be explicit. |
| `clear` | Remove or acknowledge stored state, errors, data, or status. |
| `save` / `load` | Persist to or restore from the driver, local system, or device as documented. |
| `upload` / `download` | Transfer data toward or away from the physical device. |
| `list` | Return zero or more items without changing them. |
| `select` | Make an existing item, channel, or connection active. |
| `..._should_be_...` | Assert a condition and raise an exception when the condition is false. |

### 7.3 Device name in method names

Canonical methods should not repeat the device or driver name when the driver class context already identifies it.

Preferred:

```python
n6700.set_dc_voltage(1, 5.0)
dmm.measure_dc_voltage()
relay.open_relay(3)
```

Avoid:

```python
set_n6700_dc_voltage(1, 5.0)
measure_hp34401a_dc_voltage()
open_phidget_relay(3)
```

A device name may appear when required to distinguish two genuinely different concepts inside one driver.

### 7.4 Acronyms and units

Established acronyms may retain conventional uppercase spelling, including:

- AC;
- DC;
- RF;
- RMS;
- IDN;
- IP;
- LAN;
- USB;
- VISA;
- SCPI;
- CAN;
- GPIO;
- NPLC.

Units shall not be hidden in ambiguous argument names. Units shall be included in Python argument names, documentation, and structured return fields using normalized suffixes such as:

- `_v` for volts;
- `_a` for amperes;
- `_ohm` for ohms;
- `_hz` for hertz;
- `_s` for seconds;
- `_ms` for milliseconds;
- `_c` for degrees Celsius where the domain clearly requires temperature;
- `_pct` for percent.

---

## 8. Mandatory universal method set

Every LPDS hardware driver shall implement the canonical methods in this section.

### 8.1 `connect`

**Purpose:** Establish a driver-to-device session.

Canonical signature:

```python
def connect(
    self,
    resource: str | None = None,
    alias: str = "default",
    timeout_s: float | None = None,
    **options: object,
) -> dict[str, object]:
    ...
```

Mandatory behavior:

- validates arguments before transport activity where possible;
- establishes the requested session;
- performs a safe communication check when supported;
- does not change functional device outputs unless the connection protocol itself requires it;
- returns the normalized connection-state dictionary defined in Section 12;
- is idempotent when the same alias is already connected to the same resource and compatible options;
- shall not silently reconnect an alias to a different resource;
- shall fail with a state or validation error when an existing alias conflicts;
- shall redact credentials and secrets from logs and returned data.

`resource` is a normalized connection identifier. Examples include a VISA resource, serial port, IP address, hostname, SDK serial number, URL, or fixture-specific identifier.

### 8.2 `disconnect`

Canonical signature:

```python
def disconnect(self, alias: str | None = None) -> None:
    ...
```

Mandatory behavior:

- closes the specified or active session;
- releases locks, transport handles, worker threads, and temporary resources;
- is idempotent;
- does not fail merely because the requested alias is already disconnected;
- does not energize or reconfigure the device during cleanup;
- executes a documented safe-state action first when the device capability group requires it.

### 8.3 `is_connected`

Canonical signature:

```python
def is_connected(self, alias: str | None = None) -> bool:
    ...
```

Mandatory behavior:

- returns a real Boolean;
- does not raise merely because no session exists;
- does not perform a destructive or state-changing device operation;
- shall document whether it reports cached transport state or performs a live probe.

### 8.4 `get_connection_state`

Canonical signature:

```python
def get_connection_state(self, alias: str | None = None, refresh: bool = False) -> dict[str, object]:
    ...
```

Returns the normalized connection-state dictionary defined in Section 12.

When `refresh=True`, the driver shall perform a bounded safe probe if the transport and device support one.

### 8.5 `check_communication`

Canonical signature:

```python
def check_communication(self, alias: str | None = None) -> bool:
    ...
```

Mandatory behavior:

- performs a bounded, non-destructive communication operation;
- returns `True` when the communication check succeeds;
- raises a typed driver exception when the check cannot be completed;
- shall not return `False` for an unexplained transport or protocol failure;
- shall not change functional output state.

### 8.6 `get_identity`

Canonical signature:

```python
def get_identity(self, alias: str | None = None, refresh: bool = True) -> str:
    ...
```

Mandatory behavior:

- returns a stable human-readable identity string;
- queries the device when a standard identity operation exists and `refresh=True`;
- may return a documented configured or SDK-derived identity when the device has no identity query;
- shall not return `None` on success;
- shall preserve the raw device identity in evidence when applicable.

### 8.7 `get_driver_information`

Canonical signature:

```python
def get_driver_information(self) -> dict[str, object]:
    ...
```

The returned dictionary shall contain at least:

```yaml
name: example_driver
version: "26.01"
api_spec: LPDS-002
api_spec_version: "1.0"
python_min_version: "<declared version>"
instance_sharing_policy: session-shared
transport_types:
  - scpi_tcp
capability_ids:
  - connection
  - identity
```

Additional fields may include package build, Git commit, vendor, model family, supported operating systems, and protocol version.

### 8.8 `get_driver_capabilities`

Canonical signature:

```python
def get_driver_capabilities(self) -> list[str]:
    ...
```

Returns stable machine-readable capability identifiers. Capability identifiers shall use lowercase `snake_case` and shall be declared in the LPDS-017 AI Driver Contract.

This method returns LPDS-002's flat, group-level capability names for quick discovery of which conditional method groups (Section 9) a driver implements; the return type shall remain `list[str]` so that it stays trivially consumable by any adapter. LPDS-013 separately defines a hierarchical, dot-separated `capability_id` grammar (`<domain>.<object>.<operation>`) and a richer capability model carrying per-capability support state, availability, and metadata, exposed through the distinct `get_capability_model` method. These are complementary, not competing: LPDS-013 is authoritative for the exact hierarchical identifier grammar and the full capability model, and the AI Driver Contract shall map each LPDS-002 group name below to its corresponding LPDS-013 `capability_id`. A driver shall not expose two independently-maintained capability catalogues that can drift apart.

Examples:

```text
connection
identity
multi_connection
error_queue
channel_selection
dc_voltage_source
dc_voltage_measurement
relay_control
file_transfer
safe_shutdown
raw_io
```

### 8.9 `set_communication_timeout`

Canonical signature:

```python
def set_communication_timeout(self, timeout_s: float, alias: str | None = None) -> float:
    ...
```

Mandatory behavior:

- validates a finite, positive timeout;
- applies the timeout to the selected session or documented driver default;
- returns the effective timeout in seconds;
- shall not silently clamp the value unless the applied value is returned and documented.

### 8.10 `get_communication_timeout`

Canonical signature:

```python
def get_communication_timeout(self, alias: str | None = None) -> float:
    ...
```

Returns the effective timeout in seconds.

---

## 9. Conditional capability method groups

A conditional method group becomes mandatory when the driver declares the corresponding capability.

The driver shall not declare a capability unless all mandatory methods in its group are implemented or an explicit device-specific limitation is approved.

### 9.1 Multi-connection capability

Capability ID: `multi_connection`

Mandatory methods:

```text
list_connections() -> list[dict]
select_connection(alias) -> dict
disconnect_all() -> None
get_active_connection() -> str | None
```

Rules:

- every session has a unique string alias;
- `default` is the default alias when no alias is supplied;
- device-facing operations shall clearly identify which connection they use;
- the active alias shall never change implicitly as a side effect of an unrelated method.

### 9.2 Device error-queue capability

Capability ID: `error_queue`

Mandatory methods:

```text
get_device_error(alias=None) -> dict
get_all_device_errors(alias=None, max_count=100) -> list[dict]
clear_device_errors(alias=None) -> None
device_error_queue_should_be_empty(alias=None) -> None
```

The error dictionary shall contain, where available:

```yaml
code: 0
message: No error
raw: '0,"No error"'
source: device
```

The driver shall prevent unbounded reads from an error queue.

### 9.3 Channel-selection capability

Capability ID: `channel_selection`

Mandatory methods:

```text
list_channels(alias=None) -> list
validate_channel(channel, alias=None) -> bool
```

`select_channel` is mandatory only when the physical device has an active-channel concept. Drivers should prefer explicit `channel` arguments on functional methods instead of relying on hidden active-channel state.

### 9.4 Output-control capability

Capability ID: `output_control`

Mandatory methods:

```text
enable_output(channel=None, alias=None) -> None
disable_output(channel=None, alias=None) -> None
get_output_state(channel=None, alias=None) -> bool
output_should_be_enabled(channel=None, alias=None) -> None
output_should_be_disabled(channel=None, alias=None) -> None
```

Rules:

- Boolean output state shall be returned as `bool`;
- `disable_output` shall be idempotent;
- output-enable operations shall be classified for safety and shall validate prerequisites before transmission;
- connection teardown shall define whether outputs remain unchanged or are placed into a safe state.

### 9.5 Source or setpoint capability

Typical capability IDs include `dc_voltage_source`, `dc_current_source`, `electronic_load`, `temperature_control`, and `resistance_simulation`.

Each settable quantity shall provide, as applicable:

```text
set_<quantity>(value, channel=None, alias=None) -> None
get_<quantity>_setpoint(channel=None, alias=None) -> float
get_<quantity>_limits(channel=None, alias=None) -> dict
```

A driver shall not use `get_<quantity>` when it would be ambiguous whether the result is a configured setpoint or a live measurement.

### 9.6 Measurement capability

Typical capability IDs include `dc_voltage_measurement`, `dc_current_measurement`, `resistance_measurement`, `frequency_measurement`, and `temperature_measurement`.

Each physical measurement shall provide:

```text
measure_<quantity>(channel=None, alias=None, **options) -> float | dict
```

Rules:

- `measure_*` shall represent a live acquisition or explicit measurement cycle;
- the returned unit shall be fixed and documented;
- a scalar is preferred for a single measurement value;
- a dictionary shall be used when status, timestamp, range, uncertainty, or multiple values are returned;
- no formatted unit string shall replace the numeric value.

### 9.7 Relay or switch capability

Capability ID: `relay_control`

Mandatory methods:

```text
open_relay(channel, alias=None) -> None
close_relay(channel, alias=None) -> None
set_relay_state(channel, closed, alias=None) -> None
get_relay_state(channel, alias=None) -> bool
open_all_relays(alias=None) -> None
get_all_relay_states(alias=None) -> dict
relay_should_be_open(channel, alias=None) -> None
relay_should_be_closed(channel, alias=None) -> None
```

Canonical Boolean meaning:

```text
False = open
True  = closed
```

The methods `open_relay` and `close_relay` shall describe the electrical contact state, not the connection session state.

### 9.8 Reset capability

Capability ID: `device_reset`

Mandatory method:

```text
reset_device(alias=None, wait_until_ready=True, timeout_s=None) -> dict
```

The documentation shall state:

- reset type;
- output behavior;
- settings preserved or cleared;
- reconnect behavior;
- expected ready time;
- safety risk.

### 9.9 File-transfer capability

Capability ID: `file_transfer`

Mandatory methods, as applicable:

```text
list_device_files(path="/", alias=None) -> list[dict]
upload_file(local_path, device_path=None, overwrite=False, alias=None) -> dict
download_file(device_path, local_path=None, overwrite=False, alias=None) -> dict
delete_device_file(device_path, alias=None) -> None
```

Rules:

- local and device paths shall be distinguished explicitly;
- overwrite shall default to `False`;
- transferred byte count and final path shall be returned;
- destructive operations shall be clearly tagged;
- path traversal and unsafe local-path behavior shall be prevented.

### 9.10 Safe-shutdown capability

Capability ID: `safe_shutdown`

This capability is mandatory for drivers that can energize, load, heat, move, switch hazardous power, or otherwise create a persistent hazardous state.

Mandatory method:

```text
safe_shutdown(alias=None, timeout_s=None) -> dict
```

Mandatory behavior:

- attempts the documented safe-state sequence;
- is idempotent;
- continues best-effort cleanup after an individual safe-state step fails;
- returns a structured result when all requested actions complete;
- raises `DriverSafetyError` when the safe state cannot be confirmed;
- shall be suitable for test teardown and emergency cleanup.

### 9.11 Raw I/O capability

Capability ID: `raw_io`

Raw protocol methods are optional and shall not replace domain-level methods.

Permitted canonical names:

```text
write_raw_command(command, alias=None) -> None
query_raw_command(command, alias=None, timeout_s=None) -> str | bytes
read_raw_response(alias=None, timeout_s=None) -> str | bytes
```

Rules:

- raw I/O shall be disabled by default or require explicit opt-in when it can bypass driver safety validation;
- methods shall be tagged `lpds:raw_io` and `lpds:high_risk`;
- secrets shall be redacted;
- raw I/O shall not be presented as the primary public API;
- the AI Driver Contract shall warn that raw I/O may invalidate state tracking.

---

## 10. Method argument standard

### 10.1 Argument names

Python argument names shall:

- use `snake_case`;
- use domain terminology;
- include unit suffixes when the unit is not inherent in the parameter;
- use `channel` for a single channel identifier;
- use `channels` for a collection;
- use `alias` for a connection alias;
- use `timeout_s` for a timeout in seconds;
- use `resource` for a connection resource identifier;
- use `refresh` for an explicit live refresh instead of cached data;
- use `wait_until_ready` for a post-operation readiness wait;
- use `overwrite` for replacement of existing files or records;
- use `**options` only for genuinely transport- or model-specific options.

### 10.2 Positional and named arguments

- the most common required arguments shall appear first;
- optional arguments shall follow required arguments;
- safety-critical options should be keyword-only in Python where practical;
- examples shall demonstrate named arguments when multiple adjacent values have the same type or could be confused;
- adding a new optional argument at the end is backward-compatible;
- reordering existing arguments is a breaking API change.

### 10.3 Default values

Default values shall:

- be deterministic;
- be safe;
- be shown in generated API documentation and the API inventory;
- not depend on hidden environment state unless explicitly documented;
- not enable output, overwrite files, clear data, or perform destructive actions;
- use `None` when the driver or profile default is intentionally selected.

### 10.4 Type annotations and conversion

Every public Python method shall use type annotations for all arguments and return values.

Supported public argument types should be limited to:

- `str`;
- `int`;
- `float`;
- `bool`;
- `None` / optional values;
- enums with documented accepted names;
- `list`, `tuple`, or `dict` when necessary;
- `pathlib.Path` for local filesystem paths.

The driver shall validate:

- numeric finiteness;
- numeric range;
- enum membership;
- channel existence;
- resource format;
- file path safety;
- state preconditions;
- mutually exclusive arguments.

Validation that can be performed locally shall occur before protocol transmission.

An adapter that cannot natively pass a given Python type (for example, an older automation tool that only supports strings) is responsible for converting at the adapter boundary; this does not relax the driver's own type-hinted signature.

### 10.5 Boolean arguments

Boolean arguments shall use real Boolean semantics and shall not require device-specific text such as `ON`, `OFF`, `1`, or `0` from the caller.

Protocol-specific serialization belongs inside the driver.

### 10.6 Enum arguments

Accepted enum values shall:

- use lowercase or documented case-insensitive names at the Python boundary;
- be normalized by the driver;
- be listed in method documentation and LPDS-017;
- reject unknown values before transmission.

### 10.7 Variable argument lists

Public methods should avoid `*args` and unstructured `**kwargs` because they weaken generated API documentation, AI-contract, and conformance precision.

`**options` may be used only when:

- all accepted keys are documented;
- unknown keys are rejected;
- each key has a declared type and default;
- protocol vectors cover the options that affect transmitted data.

---

## 11. Return value standard

### 11.1 Permitted return types

Public methods shall return only adapter-safe values — plain data types that any adapter (pytest, REST, CLI, ...) can consume without special-casing:

- `None`;
- `bool`;
- `int`;
- `float`;
- `str`;
- `bytes` only for explicitly documented binary operations;
- `list` or `tuple` containing compatible values;
- `dict` with string keys and compatible values.

The following shall not be returned directly:

- transport objects;
- VISA resources;
- serial objects;
- sockets;
- vendor SDK handles;
- generators;
- iterators requiring later transport activity;
- custom domain objects;
- exceptions as data;
- dataclasses unless converted to dictionaries first.

### 11.2 Command returns

A command method should return `None` when successful.

A command may return a normalized dictionary when the result provides material information, such as:

- actual applied value;
- selected range;
- operation identifier;
- file transfer result;
- reset readiness;
- safe-shutdown confirmation.

A driver shall not return arbitrary success strings such as `OK`, `Done`, or `Success` when normal completion already indicates success.

### 11.3 Query and measurement returns

- a single logical value should return a scalar;
- multiple named values shall return a dictionary;
- repeated homogeneous values shall return a list;
- numeric values shall remain numeric;
- units shall be fixed and documented rather than appended to numeric strings;
- timestamps shall use ISO 8601 strings with timezone information when returned as text.

### 11.4 Dictionary schema stability

Keys in public return dictionaries are part of the public API.

They shall:

- use lowercase `snake_case`;
- remain stable across compatible releases;
- be listed in documentation and `public_api.yaml`;
- not disappear without deprecation or a breaking-version change;
- use `None` for known but unavailable optional values rather than changing the schema unpredictably.

---

## 12. Standard data schemas

### 12.1 Connection-state schema

`connect`, `get_connection_state`, `select_connection`, and related methods shall use the following normalized fields:

```yaml
alias: default
resource: TCPIP0::192.168.0.55::5025::SOCKET
connected: true
communication_ok: true
transport: scpi_tcp
identity: OpenBench,E-Resistor,SN001,0.8.0
connected_at: "2026-07-26T08:30:00+03:00"
last_communication_at: "2026-07-26T08:30:01+03:00"
timeout_s: 5.0
state: connected
```

Required keys:

- `alias`;
- `resource`;
- `connected`;
- `communication_ok`;
- `transport`;
- `identity`;
- `timeout_s`;
- `state`.

Allowed `state` values:

```text
disconnected
connecting
connected
degraded
recovering
faulted
```

This is the public, lowercase projection of the canonical session-state model that LPDS-003 §13.1 owns; LPDS-003 is authoritative for the complete internal state set. Implementers exposing the public `state` field shall map LPDS-003's internal states onto this reduced public vocabulary rather than inventing separate state names.

### 12.2 File-transfer result schema

```yaml
operation: upload
source_path: ./calibration/ch1.csv
destination_path: /calibration/ch1.csv
bytes_transferred: 4096
overwritten: false
verified: true
```

### 12.3 Safe-shutdown result schema

```yaml
safe: true
actions:
  - action: disable_output
    target: channel_1
    result: pass
  - action: open_relays
    target: all
    result: pass
failed_actions: []
confirmed_at: "2026-07-26T08:35:00+03:00"
```

---

## 13. Connection and state semantics

### 13.1 Constructor behavior

The driver constructor may:

- store configuration defaults;
- validate static configuration;
- initialize local data structures;
- create locks that do not interact with hardware.

The constructor shall not:

- open a device connection;
- send protocol commands;
- enable outputs;
- reset hardware;
- start non-daemon worker activity;
- require that hardware is present merely to import the driver module or instantiate the driver class.

### 13.2 Explicit state preconditions

Each device-facing method shall define its required state.

Typical states include:

```text
disconnected
connected
configured
ready
running
faulted
```

A method called in the wrong state shall fail with `DriverStateError` before unsafe transmission where possible.

### 13.3 Idempotency

The following shall be idempotent:

- `disconnect`;
- `disconnect_all`;
- `disable_output`;
- `open_relay` when already open;
- `close_relay` when already closed;
- `safe_shutdown`;
- clearing an already empty local driver error state.

Other method idempotency shall be documented.

### 13.4 Cached versus live data

Methods returning cached state shall say so explicitly.

Where both are useful, the method shall provide a `refresh` argument or separate clearly named operation. A cached value shall not be presented as a confirmed live device value.

---

## 14. Timeout, wait, and retry standard

### 14.1 Bounded execution

Every device-facing method shall have bounded execution.

A method shall not:

- wait forever for a response;
- poll indefinitely;
- block forever on a worker thread;
- retry without a finite attempt count or deadline.

### 14.2 Timeout units

Public timeout arguments shall use seconds and the `_s` suffix.

Timeout values shall be positive finite numbers.

### 14.3 Stabilization waits

A stabilization delay shall be separate from communication timeout when both concepts apply.

Preferred argument names:

```text
stabilization_s
settle_timeout_s
poll_interval_s
```

### 14.4 Retries

Retries shall be used only for documented transient failures.

The driver shall document:

- retryable error classes;
- maximum attempts;
- delay or backoff;
- total time bound;
- whether the command may be repeated safely;
- whether recovery changes device state.

A non-idempotent command shall not be retried automatically unless the protocol provides evidence that it was not applied.

---

## 15. Error and exception standard

### 15.1 Mandatory exception hierarchy

LPDS-007 is the sole normative source for the exact LPDS exception hierarchy, class names, and error codes. Every LPDS Python driver shall expose or internally use the LPDS-007 hierarchy, rooted at `DriverError`, with top-level categories for configuration, validation, state, connection, transport (including timeouts), protocol, device, resource, safety, dependency, and internal failures.

LPDS-002 does not restate the full hierarchy here; see LPDS-007 §6 for the complete, authoritative class tree. A package may add subclasses but shall preserve the LPDS-007 semantic categories and shall not introduce a competing top-level taxonomy.

### 15.2 Error messages

Expected driver failures shall use the stable diagnostic message format defined normatively by LPDS-007 §11:

```text
[<ERROR_CODE>] <operation> failed: <reason>. <context>. Retryable=<yes|no>. Recovery=<action|none>.
```

Where `<ERROR_CODE>` follows the LPDS-007 code grammar `LPDS-<DOMAIN>-<NNN>`. Example:

```text
[LPDS-TMO-001] get_identity failed: no response within 5.0 s. method=get_identity; alias=default. Retryable=yes. Recovery=Check cable and retry connect.
```

LPDS-007 is authoritative for the exact message grammar and error-code catalogue; LPDS-002 constrains only which contextual fields (method, alias) a device-facing failure shall include.

Mandatory rules:

- failure summaries shall be understandable without reading source code;
- the driver shall not expose passwords, access tokens, or private keys;
- raw binary data shall be bounded in length;
- the original exception shall be chained in Python when useful;
- protocol/device failures shall not be reported as success values;
- validation failures shall identify the argument and accepted range or values;
- errors shall distinguish local validation, driver state, transport, protocol, device, and safety causes.

### 15.3 Assertion methods

Methods named with an `..._should_be_...` (or equivalent `should_...`) pattern shall:

- return `None` on success;
- raise an assertion-style exception on mismatch;
- include actual and expected values;
- avoid changing device state unless the assertion explicitly requires a safe probe.

### 15.4 Recovery information

Recoverable errors should include a concrete recovery action.

LPDS-017 shall declare whether each expected error is:

- retryable;
- reconnect-required;
- reset-required;
- operator-action-required;
- non-recoverable within the current test.

---

## 16. Safety standard

### 16.1 Risk classification

Every device-facing public method shall declare one risk level:

```text
low
medium
high
critical
```

Recommended interpretation:

- `low` — read-only or benign local operation;
- `medium` — state change within normal safe limits;
- `high` — output, load, motion, heating, switching, reset, deletion, or raw protocol operation;
- `critical` — operation capable of immediate equipment damage, unsafe energy, irreversible loss, or fixture hazard without validated preconditions.

This four-level, lowercase `low`/`medium`/`high`/`critical` scale is the canonical LPDS risk-level vocabulary. LPDS-013 and LPDS-014 shall reuse these exact values (adding `none` only where a capability or field genuinely carries no risk) rather than introducing separately-cased or separately-named risk scales.

`risk_level` shall be declared as explicit method metadata rather than left implicit in prose documentation — for example as the `risk_level` argument to a `@public_api(...)` registration decorator, or as an entry in an equivalent class-level method-metadata registry.

### 16.2 Safety validation

High- and critical-risk methods shall:

- validate connection and device state;
- validate configured limits;
- validate channel and range;
- reject non-finite numeric values;
- document side effects;
- define cleanup or safe-state behavior;
- be included in the LPDS-017 safety rules.

### 16.3 Dangerous defaults

A default argument shall not:

- enable an output;
- select maximum voltage, current, load, temperature, or power;
- overwrite a device file;
- clear calibration;
- reset a device;
- bypass interlocks;
- activate raw I/O;
- disable error checks.

### 16.4 Emergency cleanup

A driver with persistent hazardous state shall provide `safe_shutdown` and document the exact teardown sequence.

Failure to confirm a safe state shall be visible as a test failure and shall not be reduced to a warning.

---

## 17. Logging and evidence

Public methods shall produce useful driver logs without exposing secrets or overwhelming the report.

### 17.1 Required logging

For device-facing methods, logs should include:

- canonical method name;
- selected alias and redacted resource;
- normalized arguments;
- operation duration;
- retry count;
- result summary;
- protocol trace reference when conformance tracing is enabled.

### 17.2 Protocol logging

Normal user logs should not expose unlimited raw protocol traffic.

Detailed TX/RX data may be emitted at debug or trace level and shall:

- be length-bounded;
- be timestamped;
- distinguish transmitted and received data;
- identify the method and protocol vector;
- redact credentials;
- preserve raw bytes in a deterministic representation when required by LPDS-019.

---

## 18. Method tags and metadata

Each public method shall declare relevant stable tags as part of its method metadata (for example, via the `tags` argument to a `@public_api(...)` registration decorator, or an equivalent class-level registry).

Required tag vocabulary:

```text
lpds:connection
lpds:identity
lpds:query
lpds:measurement
lpds:configuration
lpds:write
lpds:output
lpds:relay
lpds:file
lpds:diagnostic
lpds:assertion
lpds:safety
lpds:destructive
lpds:raw_io
lpds:deprecated
lpds:low_risk
lpds:medium_risk
lpds:high_risk
lpds:critical_risk
```

At minimum, each device-facing method shall have:

- one functional classification tag;
- one risk tag.

Tags are metadata and shall not replace documentation or LPDS-017 capability definitions.

---

## 19. Method documentation standard

Every public method shall document, in its docstring (or an explicitly linked reference document):

1. purpose;
2. canonical signature;
3. each argument and unit;
4. accepted values and ranges;
5. defaults;
6. return type and schema;
7. connection and state preconditions;
8. postconditions;
9. device side effects;
10. risk level;
11. communication timeout behavior;
12. stabilization or readiness wait;
13. retry behavior;
14. expected exception categories;
15. cleanup requirements;
16. aliases and deprecation status;
17. one minimal plain-Python usage example.

The first documentation paragraph shall be a concise operation summary suitable for automatic documentation generation (for example Sphinx or pydoc) and for adapter-generated help text.

Documentation shall distinguish:

- setpoint from measured value;
- cached from live value;
- command from query;
- device error from transport error;
- safe operation from potentially hazardous operation.

---

## 20. Assertions versus action methods

Drivers may provide domain-specific assertion methods when they improve readability or add device-aware tolerance and error handling.

Examples:

```python
device_should_be_connected()
output_should_be_disabled(channel=1)
voltage_should_be_within_limits(channel=1)
device_error_queue_should_be_empty()
relay_should_be_open(channel=3)
```

Rules:

- assertion methods shall not duplicate generic assertion mechanisms (such as a bare `assert` statement or a pytest assertion) without adding domain value;
- action methods shall not silently assert unrelated conditions after completing the requested action;
- verification that is required for safety may remain part of the action method and shall be documented;
- assertion tolerances and units shall be explicit.

---

## 21. Aliases, compatibility, and deprecation

### 21.1 Canonical names

Each operation shall have exactly one canonical method name.

Aliases may exist for:

- migration from a previous driver API;
- vendor terminology;
- compatibility with an established project interface;
- corrected spelling or naming.

Aliases shall not be used to create multiple competing canonical styles.

### 21.2 Alias equivalence

An alias shall:

- call the same implementation path as the canonical method;
- accept equivalent arguments unless a documented migration adapter is required;
- return the same type and semantic value;
- produce equivalent device protocol behavior;
- be listed separately in the public API inventory and LPDS-019 coverage matrix.

### 21.3 Deprecation

A deprecated method shall:

- remain callable during the deprecation window;
- emit a Python `DeprecationWarning` (via `warnings.warn`);
- identify the replacement method;
- appear in generated API documentation, README migration notes, history, and the AI Driver Contract;
- carry the `lpds:deprecated` tag;
- remain covered by LPDS-019 until removed.

Recommended documentation prefix:

```text
*DEPRECATED* Use `connect` instead. Scheduled for removal after v26.04.
```

### 21.4 Minimum deprecation window

A public method, argument, return key, or behavior shall remain deprecated for at least two subsequent released driver revisions before removal.

A shorter window is permitted only for:

- a safety defect;
- a security defect;
- an operation that cannot work correctly;
- accidental exposure of a private implementation method.

The reason shall be documented in `history/` and `review/`.

### 21.5 Breaking changes

The following are breaking API changes:

- removing a canonical method or alias;
- renaming a method without retaining an alias;
- changing argument order;
- removing an argument;
- changing a default with behavioral impact;
- changing a return type;
- removing or renaming a return dictionary key;
- changing units;
- changing Boolean meaning;
- changing output or safety side effects;
- changing protocol behavior in a way visible to the public contract.

Breaking changes require explicit release notes, migration guidance, contract updates, and conformance updates.

---

## 22. API artifacts

A driver's docstrings (§19) plus its LPDS-017 AI Driver Contract (when published) are the source of truth for its public API — there's no separate mandatory `public_api.yaml`/schema/`compatibility.yaml` artifact to keep in sync with them. Generated API reference documentation (for example via Sphinx or pdoc) is a nice addition once a driver has external users, published through GitHub Pages or similar, but isn't required to call a driver conformant.

If a project wants a machine-readable method inventory beyond what the AI contract already provides — for tooling that specifically needs it — the schema below is a reasonable shape to use. It's optional.

---

## 23. Optional: machine-readable method inventory schema

Each public method entry, if you choose to maintain one of these:

```yaml
api_spec:
  id: LPDS-002
  version: "1.0"

driver:
  name: example_driver
  version: "26.01"
  instance_sharing_policy: session-shared

methods:
  - name: connect
    canonical_name: connect
    aliases: []
    category: connection
    capability_id: connection
    device_facing: true
    risk: low
    arguments:
      - name: resource
        type: str | None
        required: false
        default: null
      - name: alias
        type: str
        required: false
        default: default
      - name: timeout_s
        type: float | None
        required: false
        default: null
      - name: options
        type: dict
        required: false
        default: {}
    returns:
      type: dict
      schema: connection_state
    preconditions: []
    postconditions:
      - requested alias is connected
    side_effects:
      - opens transport session
    timeout_behavior: bounded
    protocol_vector: connect.default
    tags:
      - lpds:connection
      - lpds:low_risk
    status: active
    deprecated_since: null
    replacement: null
```

If maintained, keep it consistent with the code and, where present, the AI contract and examples — a stale copy is worse than no copy.

---

## 24. Implementation skeleton

A compliant driver may use this pattern:

```python
from __future__ import annotations

from typing import Any

from .api import public_api
from .errors import DriverStateError
from .version import __version__


class ExampleDriver:
    """Plain Python driver for the Example device family.

    Fully constructible, controllable, and testable from a plain
    Python/pytest session with no automation framework installed.
    """

    __version__ = __version__

    def __init__(self, default_timeout_s: float = 5.0) -> None:
        self._default_timeout_s = self._validate_timeout(default_timeout_s)
        self._sessions: dict[str, Any] = {}
        self._active_alias: str | None = None

    @public_api(category="connection", risk_level="low",
                tags=["lpds:connection", "lpds:low_risk"])
    def connect(
        self,
        resource: str | None = None,
        alias: str = "default",
        timeout_s: float | None = None,
        **options: Any,
    ) -> dict[str, Any]:
        """Establish a device session and return normalized connection state."""
        ...

    @public_api(category="connection", risk_level="low",
                tags=["lpds:connection", "lpds:low_risk"])
    def disconnect(self, alias: str | None = None) -> None:
        """Close a device session. Safe to call more than once."""
        ...

    @public_api(category="query", risk_level="low",
                tags=["lpds:query", "lpds:low_risk"])
    def is_connected(self, alias: str | None = None) -> bool:
        """Return whether the selected session is currently connected."""
        ...

    @public_api(category="identity", risk_level="low",
                tags=["lpds:identity", "lpds:low_risk"])
    def get_identity(self, alias: str | None = None, refresh: bool = True) -> str:
        """Return the device identity string."""
        ...

    def _require_session(self, alias: str | None) -> Any:
        """Internal helper. Not part of the public API."""
        ...

    @staticmethod
    def _validate_timeout(value: float) -> float:
        ...
```

The `@public_api(...)` decorator is expected to record the method, its metadata (category, capability, risk level, tags), and its signature in a class-level public API registry at class-definition time. This registry is what satisfies the explicit-registration requirement of Section 5 and backs the `public_api.yaml` inventory of Section 23 — a method without this registration is not part of the driver's public API regardless of its name.

---

## 25. Usage example

The primary, mandatory way to use a driver is plain Python:

```python
from example_driver import ExampleDriver

driver = ExampleDriver()
try:
    state = driver.connect(
        resource="TCPIP0::192.168.0.55::5025::SOCKET",
        alias="psu",
        timeout_s=5.0,
    )
    assert state["connected"]

    ok = driver.check_communication(alias="psu")
    assert ok

    identity = driver.get_identity(alias="psu")
    assert identity
finally:
    if "safe_shutdown" in driver.get_driver_capabilities():
        driver.safe_shutdown(alias="psu")
    driver.disconnect(alias="psu")
```

*Example: pytest fixture adapter.* An adapter package built on top of the driver could expose the same operations as a pytest fixture, with fixture and helper names mechanically derived from the method names (see Section 7.1):

```python
# adapters/pytest/example_driver_fixtures.py
import pytest
from example_driver import ExampleDriver


@pytest.fixture
def psu():
    driver = ExampleDriver()
    state = driver.connect(
        resource="TCPIP0::192.168.0.55::5025::SOCKET",
        timeout_s=5.0,
    )
    assert state["connected"]
    try:
        yield driver
    finally:
        if "safe_shutdown" in driver.get_driver_capabilities():
            driver.safe_shutdown()
        driver.disconnect()


def test_read_device_identity(psu):
    assert psu.check_communication()
    assert psu.get_identity()
```

A driver that does not declare `safe_shutdown` shall omit that teardown step (in Python or in any adapter) and use `disconnect` only.

---

## 26. Mandatory API tests

Each driver shall provide automated tests that verify:

1. the driver module imports, and the driver class can be instantiated, without hardware access;
2. the public API is explicitly and completely registered — no method is public merely by omission of a leading underscore;
3. all expected canonical methods are exported;
4. no private helper is exported;
5. registered public method names are unique, and remain unique after any adapter-specific normalization;
6. mandatory universal signatures match this specification or an approved compatibility profile;
7. all arguments and return values are documented;
8. public methods have type annotations;
9. command and query return types match the API inventory;
10. invalid local arguments fail before transmission where practical;
11. `disconnect` is idempotent;
12. `is_connected` returns a Boolean;
13. `get_driver_information` and `get_driver_capabilities` match package metadata;
14. aliases are semantically equivalent;
15. deprecated methods emit warnings;
16. all device-facing methods are linked to LPDS-019 protocol vectors or approved exclusions.

---

## 27. Integration with other LPDS specifications

### 27.1 LPDS-017 — AI Driver Contract

LPDS-017 shall use LPDS-002 as the source of truth for:

- canonical method name;
- alias list;
- signature;
- argument types and units;
- return type and schema;
- preconditions and postconditions;
- side effects;
- risk level;
- timing, timeout, and retry behavior;
- errors and recovery;
- resource use.

Every public method in the LPDS-002 inventory shall have one corresponding LPDS-017 capability entry or an explicitly documented metadata-only classification.

### 27.2 LPDS-019 — Driver Call and Protocol Conformance

LPDS-019 shall verify:

- the exported method inventory;
- canonical and alias names;
- signatures and defaults;
- callability from a plain Python caller (and, where applicable, from any declared adapter);
- return types;
- outbound protocol behavior;
- inbound parsing;
- error behavior;
- alias equivalence.

A public API change is incomplete until corresponding LPDS-019 inventory, vectors, tests, and evidence are updated.

### 27.3 Driver implementation lifecycle

Each lifecycle gate that changes public behavior shall update:

- implementation;
- `public_api.yaml`;
- generated API documentation and method reference;
- LPDS-017 contract;
- LPDS-019 inventory and protocol vectors;
- examples;
- `history/` change record;
- `review/` API review.

---

## 28. Checklist

- [ ] Public-API export is explicit (no accidental promotion of helper methods, §6).
- [ ] All mandatory universal methods (§8) and each declared capability's mandatory method group (§9) are implemented.
- [ ] Canonical method names are unique, verb-first, and follow the naming rules (§7); aliases and deprecations are declared (§21).
- [ ] Every public method is fully type-annotated: arguments, defaults, units, return type (§10-11).
- [ ] Return values are adapter-safe plain data (§11) — no framework-specific or non-serializable objects.
- [ ] The constructor and module import don't touch hardware.
- [ ] Connection, timeout, and idempotency behavior match this spec and are covered by tests.
- [ ] High-risk operations carry explicit risk/safety metadata (§16); a safe-shutdown path exists where persistent hazardous state is possible.
- [ ] A failed operation raises the documented exception category rather than returning success.
- [ ] Every device-facing public method has LPDS-019 protocol coverage, or an explicit, documented exclusion.
- [ ] If an adapter exists, each public method is callable through it too.

This isn't a formal gate — it's what "the public API is in good shape" means in practice. Treat gaps as things to note in the driver's README (per LPDS-001 §32), not blockers to fix before anyone can look at the code.

---

## 29. Goal

Provide one predictable, safe, machine-verifiable public Python interface across all LPDS instrument drivers while preserving the device-specific capabilities necessary for real laboratory automation.

---

## Appendix A — Canonical mandatory method summary

### Universal methods

| Method | Return | Required for every driver |
|---|---:|---:|
| `connect` | `dict` | Yes |
| `disconnect` | `None` | Yes |
| `is_connected` | `bool` | Yes |
| `get_connection_state` | `dict` | Yes |
| `check_communication` | `bool` | Yes |
| `get_identity` | `str` | Yes |
| `get_driver_information` | `dict` | Yes |
| `get_driver_capabilities` | `list[str]` | Yes |
| `set_communication_timeout` | `float` | Yes |
| `get_communication_timeout` | `float` | Yes |

### Common conditional groups

| Capability | Mandatory canonical methods |
|---|---|
| Multi-connection | `list_connections`, `select_connection`, `disconnect_all`, `get_active_connection` |
| Error queue | `get_device_error`, `get_all_device_errors`, `clear_device_errors`, `device_error_queue_should_be_empty` |
| Channel selection | `list_channels`, `validate_channel` |
| Output control | `enable_output`, `disable_output`, `get_output_state`, output-state assertions |
| Measurement | `measure_<quantity>` |
| Source/setpoint | `set_<quantity>`, `get_<quantity>_setpoint`, `get_<quantity>_limits` |
| Relay control | open, close, set, get, all-open, all-state, and assertion methods |
| Reset | `reset_device` |
| File transfer | list, upload, download, and delete file methods |
| Safe shutdown | `safe_shutdown` |
| Raw I/O | raw write, query, and read methods with explicit opt-in |

---

## Appendix B — Recommended canonical migration aliases

Legacy driver packages may temporarily map earlier names to LPDS-002 canonical names:

| Legacy pattern | Canonical replacement |
|---|---|
| `open`, `open_connection`, `connect_to_device`, `connect_dmm`, `connect_relays` | `connect` |
| `close`, `close_connection`, `close_dmm`, `disconnect_relays` | `disconnect` |
| `get_idn`, `query_identity`, `read_identity` | `get_identity` |
| `set_timeout` | `set_communication_timeout` |
| `get_timeout` | `get_communication_timeout` |
| `close_all_relays` when meaning electrically close | Keep `close_all_relays`; do not map to `disconnect_all` |
| `open_all_relays` when meaning electrically open | Keep `open_all_relays`; do not map to `disconnect_all` |

Migration aliases shall be deprecated, tested, and removed only through the change-control process.

---

## Appendix C — Source basis

This specification is designed to align with:

- LPDS-017 — AI Driver Contract Specification;
- LPDS-019 — Driver Call and Protocol Conformance Test Specification;
- LPDS-020 — Driver Implementation Lifecycle;
- Python packaging and API-design conventions covering public/private naming, type hints (PEP 484), docstring conventions (PEP 257), deprecation warnings, and public API stability practices.
