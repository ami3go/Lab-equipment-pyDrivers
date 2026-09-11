# LPDS-019 — Driver Conformance Test Specification

**Version:** 1.1
**Document ID:** LPDS-019
**Status:** Project requirement
**Applies to:** All LPDS Python instrument driver projects

---

## 1. Purpose

This specification defines the mandatory test used to verify the interface path between:

```text
pytest conformance test
        ↓
public driver method (plain Python API)
        ↓
driver protocol operation
        ↓
physical device or approved protocol simulator
        ↓
device response
        ↓
driver-parsed Python result
```

The test shall prove that every supported public method on a driver's plain Python API:

1. is discoverable;
2. can be called directly through plain Python with valid arguments;
3. invokes the intended driver operation;
4. sends the expected device protocol command, query, request, frame, or SDK call;
5. receives the expected device response when a response is applicable;
6. parses and returns that response correctly as a plain Python value;
7. reports protocol errors, malformed responses, and timeouts correctly;
8. remains traceable to recorded protocol evidence.

LPDS-019 verifies **driver callability and driver-to-device protocol conformance only**, and it verifies both **entirely against the driver's plain Python public API**. No automation framework — a CLI, pytest, a REST layer, a GUI test bench, or anything else — needs to be installed to execute or satisfy this specification. A driver is conformant, or it is not, independent of which framework (if any) is later layered on top of it.

Where a framework-specific adapter exists, its own conformance is a thin, separate concern: an adapter is conformant when each of its exposed operations is a faithful pass-through to an already-LPDS-019-conformant driver method. This relationship is illustrated, non-normatively, in Appendix B using a CLI adapter as one example.

---

## 2. Scope Boundary

### 2.1 In scope

LPDS-019 covers:

- enumeration of exported public methods on the driver's Python API;
- invocation of each supported public method directly through plain Python;
- validation of method names, arguments, defaults, aliases, and return values;
- mapping of each device-facing method to its expected protocol operation;
- capture and comparison of transmitted protocol data;
- capture and comparison of received protocol data;
- verification of response parsing and documented Python return values;
- command-only operations that intentionally have no response;
- query and read operations;
- connection and disconnection protocol operations;
- documented protocol errors;
- protocol timeouts;
- malformed or incomplete protocol responses;
- protocol recovery sufficient to execute a subsequent valid method call;
- approved simulator-based protocol verification;
- real-device protocol verification where safe and practical.

### 2.2 Out of scope

LPDS-019 does not verify:

- whether the driver implements every function available in the vendor manual;
- internal driver architecture or source-code quality;
- private methods and implementation helpers;
- unit-test line or branch coverage;
- package structure, wheel creation, installation, CI, or release packaging;
- README, GitHub Pages, examples, or general documentation completeness;
- physical measurement accuracy;
- instrument calibration accuracy;
- electrical performance;
- waveform quality;
- long-duration stability, stress, or throughput;
- multi-session concurrency unless it changes the protocol exchange under test;
- complete safety certification;
- full driver production readiness;
- the correctness of any framework-specific adapter (see Appendix B) beyond confirming it is a thin pass-through.

These matters shall be covered by other LPDS requirements and device-specific implementation tasks.

---

## 3. Normative Terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement; deviations require justification;
- **may** — permitted implementation choice.

---

## 4. Required Test Artifacts

Each driver package shall provide, directly or through equivalent files:

```text
<driver_name>/
└── tests/
    └── conformance/
        ├── test_driver_call_protocol_conformance.py
        ├── conftest.py
        ├── data/
        │   ├── method_inventory.yaml
        │   ├── protocol_vectors.yaml
        │   └── exclusions.yaml
        └── expected/
            └── response_schemas/
```

The package shall also provide a repeatable command or script that executes the conformance suite (for example `pytest tests/conformance`) and creates a timestamped results directory.

---

## 5. Method Inventory

The test shall generate the public method inventory using Python runtime introspection (for example `inspect.signature`, `__mro__` walking, or documented public-API decorators/markers), or an equivalent deterministic method.

Each inventory entry shall contain at least:

- public method name;
- canonical method name;
- aliases, when applicable (for example a deprecated method name retained as a thin wrapper);
- implementation target (the method itself, or the underlying implementation it delegates to);
- argument names;
- required arguments;
- optional arguments and defaults;
- return type;
- device-facing classification: `yes` or `no`;
- protocol vector reference;
- execution status;
- exclusion reason, when applicable.

A public method shall not be silently omitted.

Private methods (by convention, name-prefixed with `_`) and methods intentionally excluded from the public API shall not be included in the public method denominator.

---

## 6. Conformance Levels

### 6.1 Level 0 — Method Discovery

Verify that:

- the driver module imports without contacting hardware or raising;
- public methods can be enumerated through introspection;
- method names are unique;
- aliases are identified and traceable to their canonical method;
- signatures and defaults are valid (bindable via `inspect.signature` with no ambiguity);
- every device-facing method has a protocol vector or approved exclusion.

See Conformance Vector CV-9 in §7.3 for a worked alias-discovery example.

### 6.2 Level 1 — Python Callability

Invoke every supported public method directly through its plain Python API with at least one valid argument set.

This level shall detect:

- missing methods;
- incorrect method names;
- incorrect argument counts;
- invalid defaults;
- Python argument-binding or type-conversion failures;
- unexpected `AttributeError` or `TypeError`;
- return values that cannot be represented in the documented type or serialized to the documented evidence format;
- deadlock or unbounded execution.

See Conformance Vector CV-4 in §7.3 for a worked argument-validation example.

### 6.3 Level 2 — Outbound Protocol Verification

For each device-facing method, verify the transmitted protocol operation.

Supported operation types include:

- SCPI command or query;
- serial ASCII command;
- serial binary frame;
- VISA write or query;
- HTTP request;
- Modbus transaction;
- CAN frame;
- USB request;
- vendor SDK function call;
- GPIO or relay command exposed through an SDK.

The test shall compare the actual transmitted operation with the expected operation defined by the protocol vector.

See Conformance Vector CV-1 in §7.3.

### 6.4 Level 3 — Inbound Protocol and Return Verification

Where a device response is expected, verify:

1. the raw response received from the device or simulator;
2. protocol framing and termination;
3. response parsing;
4. conversion to the documented Python type (dataclass, enum, primitive, or equivalent);
5. conversion to any additional documented public representation (for example a `to_dict()` or serialization method), where the driver documents one;
6. returned value, schema, or tolerance.

For command-only operations, the vector shall explicitly declare that no response is expected and shall define any required acknowledgement or error check.

See Conformance Vector CV-2 in §7.3.

### 6.5 Level 4 — Protocol Error and Recovery Verification

Verify the driver behavior for applicable protocol failures:

- timeout;
- empty response;
- malformed response;
- incomplete frame;
- unexpected response type;
- device error code;
- transport disconnection;
- unsupported command response;
- checksum or frame-integrity failure.

Each failure shall surface as the corresponding LPDS-007 exception class (for example `DriverTimeoutError`, `DriverMalformedResponseError`, `DriverIncompleteResponseError`, `DriverUnexpectedResponseError`, `DriverDeviceError`/`DriverCommandRejectedError`, `DriverTransportClosedError`, `DriverUnsupportedOperationError`, `DriverChecksumError`) rather than an undocumented or generic error.

After a documented recoverable failure, the suite shall execute a subsequent valid method call and verify that protocol communication still works or is correctly re-established.

See Conformance Vectors CV-6, CV-7, CV-8 in §7.3.

---

## 7. Protocol Vector Requirements

Every device-facing public method shall have at least one protocol vector.

### 7.1 Vector schema

A vector shall define equivalent information to:

```yaml
method: set_dc_voltage
canonical_method: set_dc_voltage
aliases: []
arguments:
  channel: 1
  voltage: 5.0
preconditions:
  - connected
expected_outbound:
  transport: scpi
  operation: "VOLT 5.0,(@1)"
expected_inbound:
  response_required: false
expected_return:
  type: null
protocol_error_check:
  operation: "SYST:ERR?"
  expected: '0,"No error"'
timeout_s: 10
cleanup_calls:
  - "driver.set_dc_voltage(channel=1, voltage=0.0)"
```

For a query:

```yaml
method: get_identity
canonical_method: get_identity
aliases: []
arguments: {}
preconditions:
  - connected
expected_outbound:
  transport: scpi
  operation: "*IDN?"
expected_inbound:
  response_required: true
  raw_pattern: "<manufacturer>,<model>,<serial>,<firmware>"
expected_return:
  type: IdentityInfo
  schema: idn_string
timeout_s: 5
```

The schema may be adapted to the protocol, but it shall preserve the same verification intent.

### 7.2 Realization as pytest tests

Every vector shall be realized as one or more executable pytest test functions that call the driver method directly and assert against the transport observation point described in §10. A vector definition (§7.1) is data; the pytest test is the executable proof that the data holds.

### 7.3 Conformance Vectors — worked examples

The following vectors show how representative RFDS-era protocol-level test logic is re-expressed as plain pytest tests against the driver's public API, with no automation framework involved. They are illustrative realizations of the levels and rules defined in §6–§9, not an exhaustive vector set — a real driver's `protocol_vectors.yaml` shall cover every device-facing method it exposes.

All examples assume a `driver` fixture that returns a connected instance of a concrete driver (for example a SCPI power supply subclassing the LPDS-003 `BaseInstrument`), and a `transport_spy` fixture that exposes the bytes/text actually written to and read from the transport, per the observation requirements of §10.

**CV-1 — Command-only outbound verification** (Level 2, Oracle 9.1/9.6)

```python
def test_set_dc_voltage_sends_expected_scpi_command(driver, transport_spy):
    driver.set_dc_voltage(channel=1, voltage=5.0)

    assert transport_spy.last_write == "VOLT 5.0,(@1)"
    assert transport_spy.last_read is None  # command-only: no response awaited

    # protocol error oracle (9.7): device reports no error after the write
    assert driver.get_error_queue() == []

    driver.set_dc_voltage(channel=1, voltage=0.0)  # cleanup
```

**CV-2 — Query outbound + inbound + return verification** (Level 2/3, Oracle 9.4/9.5)

```python
def test_get_identity_round_trip(driver, transport_spy):
    identity = driver.get_identity()

    assert transport_spy.last_write == "*IDN?"
    assert isinstance(identity, IdentityInfo)
    assert identity.manufacturer and identity.model
    assert identity.serial and identity.firmware
```

**CV-3 — Precondition/state conformance** (Level 4; LPDS-003 §13.1; LPDS-007 §6/§7.3)

```python
def test_operation_before_connect_raises_precondition_error(disconnected_driver):
    with pytest.raises(DriverPreconditionError) as excinfo:
        disconnected_driver.set_dc_voltage(channel=1, voltage=5.0)

    assert disconnected_driver.state == DriverState.DISCONNECTED  # LPDS-003 §13.1
    assert excinfo.value.code.startswith("LPDS-STA-")
```

**CV-4 — Local argument validation** (Level 1; §8 bullet "invalid value that shall be rejected before transmission"; LPDS-007 §7.2)

```python
def test_out_of_range_voltage_is_rejected_before_transmission(driver, transport_spy):
    with pytest.raises(DriverRangeError):
        driver.set_dc_voltage(channel=1, voltage=1_000.0)

    assert transport_spy.last_write is None  # rejected locally; nothing sent
```

**CV-5 — Device-rejected value** (Level 4; §8 bullet "invalid value that the device is expected to reject"; Oracle 9.7)

```python
def test_device_rejected_value_raises_command_rejected_error(driver, simulator):
    simulator.queue_error("-222,\"Data out of range\"")

    with pytest.raises(DriverCommandRejectedError) as excinfo:
        driver.set_dc_voltage(channel=1, voltage=4.999)  # within local bounds

    assert excinfo.value.details["device_error_code"] == "-222"
```

**CV-6 — Timeout** (Level 4; LPDS-004 §12.5; LPDS-007 §14)

```python
def test_query_timeout_raises_driver_timeout_error(driver, simulator):
    simulator.suppress_next_response()

    with pytest.raises(DriverTimeoutError) as excinfo:
        driver.get_identity()

    assert excinfo.value.details["timed_out_phase"] == "read"
    assert excinfo.value.details["configured_timeout_s"] == pytest.approx(5.0)
```

**CV-7 — Malformed response** (Level 4; Oracle 9.3/9.4)

```python
def test_malformed_identity_response_raises_malformed_response_error(driver, simulator):
    simulator.queue_raw_response(b"NOT,AN,IDN\x00")

    with pytest.raises(DriverMalformedResponseError):
        driver.get_identity()
```

**CV-8 — Transport disconnection and recovery** (Level 4; recovery requirement of §6.5)

```python
def test_recovery_after_transport_disconnection(driver, simulator):
    simulator.drop_connection()

    with pytest.raises(DriverTransportClosedError):
        driver.get_identity()

    driver.reconnect()  # documented recovery path
    identity = driver.get_identity()  # known-good call after recovery

    assert isinstance(identity, IdentityInfo)
```

**CV-9 — Alias equivalence** (Level 0/6.1)

```python
def test_deprecated_alias_matches_canonical_method_protocol_behavior(driver, transport_spy):
    driver.set_voltage(channel=1, voltage=5.0)  # deprecated alias
    alias_write = transport_spy.last_write

    driver.set_dc_voltage(channel=1, voltage=5.0)  # canonical method
    canonical_write = transport_spy.last_write

    assert alias_write == canonical_write == "VOLT 5.0,(@1)"
```

**CV-10 — Capability-binding conformance** (§19; LPDS-013 capability model)

```python
def test_capability_record_matches_bound_method_signature(driver):
    capability = driver.describe_capabilities()["dc.voltage.set"]

    assert capability.binding.method == "set_dc_voltage"
    assert set(capability.arguments) == {"channel", "voltage"}
    assert capability.return_model.type in (None, "null")
```

---

## 8. Argument Coverage

The objective of argument testing under LPDS-019 is to confirm correct call construction and protocol serialization.

For each argument-bearing device method, vectors shall cover as applicable:

- one nominal valid value;
- minimum and maximum supported values when these change protocol serialization;
- representative enum or mode values;
- omitted optional argument;
- explicit default argument;
- invalid value that shall be rejected before transmission (CV-4);
- invalid value that the device is expected to reject (CV-5);
- repeated invocation when the protocol behavior may differ.

This is naturally expressed as a parametrized pytest test:

```python
@pytest.mark.parametrize(
    "voltage, expected_outbound",
    [
        (5.0, "VOLT 5.0,(@1)"),      # nominal
        (0.0, "VOLT 0.0,(@1)"),      # minimum
        (30.0, "VOLT 30.0,(@1)"),    # maximum
    ],
)
def test_set_dc_voltage_argument_coverage(driver, transport_spy, voltage, expected_outbound):
    driver.set_dc_voltage(channel=1, voltage=voltage)
    assert transport_spy.last_write == expected_outbound
```

LPDS-019 does not require exhaustive functional or physical boundary characterization.

---

## 9. Protocol Oracles

Each device-facing vector shall use one or more explicit oracles.

### 9.1 Outbound Exact-Match Oracle

Verify exact transmitted bytes or text after documented normalization.

### 9.2 Outbound Structured Oracle

Decode and verify fields such as:

- command header;
- address;
- channel;
- function code;
- data length;
- payload;
- checksum;
- terminator;
- HTTP method, path, headers, and body;
- SDK function and arguments.

### 9.3 Raw Response Oracle

Verify the raw response bytes or text before parsing.

### 9.4 Response-Schema Oracle

Verify the documented response structure, fields, types, units, enum values, and nullability.

### 9.5 Parsed-Value Oracle

Verify exact equality, pattern matching, or documented numeric tolerance for the value returned by the plain Python call.

### 9.6 No-Response Oracle

Verify that the operation is command-only and that the driver does not incorrectly wait for a response.

### 9.7 Protocol Error Oracle

Verify the documented exception type (per the LPDS-007 hierarchy), exception message, device error code, or transport error.

A method call shall not pass only because it returned without an exception.

---

## 10. Transport Observation

The conformance implementation shall provide a way to observe protocol exchange using one or more of:

- instrumented simulator;
- transport spy or wrapper;
- mock transport at the protocol boundary;
- VISA trace;
- serial trace;
- TCP proxy or packet capture;
- HTTP request log;
- CAN trace;
- vendor SDK spy;
- device diagnostic log.

The selected observation point shall be close enough to the device boundary to prove what the driver attempted to transmit and what it received.

Mocking the driver's own public methods (rather than the transport boundary beneath them) is insufficient when it does not verify the serialized device protocol — such mocking proves nothing about protocol conformance because it replaces the very layer under test.

Credentials and other secrets shall be redacted from evidence.

---

## 11. Simulator and Real-Device Use

### 11.1 Approved simulator

An approved simulator may be used to verify:

- all outbound commands and queries;
- valid responses;
- malformed responses;
- timeouts;
- protocol error codes;
- framing and parsing;
- deterministic edge cases.

The simulator shall operate at the same protocol boundary used by the real device connection.

### 11.2 Real device

A real device should be used to confirm representative protocol exchanges for each protocol family and command class supported by the driver.

LPDS-019 does not require independent physical measurement of the device output. The real-device result may be verified through:

- device acknowledgement;
- documented query response;
- read-back command;
- status or error query;
- device-side protocol log.

Operations that cannot be safely executed shall use an approved simulator or transport spy and shall be listed in `exclusions.yaml`.

---

## 12. Required Execution Workflow

### Step 1 — Preflight

- capture driver package version;
- capture Python version;
- capture pytest (or equivalent runner) version;
- capture operating system;
- capture transport type and configuration;
- select simulator or real-device profile;
- confirm the protocol trace mechanism.

### Step 2 — Inventory

- enumerate public methods on the driver's Python API;
- identify canonical methods and aliases;
- identify device-facing methods;
- associate each device-facing method with a protocol vector;
- fail on unexplained omissions.

### Step 3 — Establish Communication

- call the driver's `connect()` method (or documented equivalent);
- verify the expected open/connect protocol behavior;
- execute the identity or equivalent communication query when supported;
- record the raw and parsed response.

### Step 4 — Execute Callability Tests

- call every supported public method directly through its plain Python API;
- record arguments, result, duration, and status.

### Step 5 — Verify Outbound Protocol

For every device-facing method:

- start trace capture;
- call the method;
- stop trace capture;
- compare actual and expected outbound protocol data.

### Step 6 — Verify Inbound Protocol

For every response-producing method:

- record the raw response;
- verify framing and schema;
- verify parsed return type and value.

### Step 7 — Verify Protocol Failures

Execute applicable timeout, malformed-response, device-error, and disconnect vectors.

### Step 8 — Verify Recovery

After each recoverable protocol fault, execute one known-good communication method call and verify successful communication.

### Step 9 — Disconnect

- call the driver's `disconnect()` or `close()` method;
- verify the expected transport close behavior;
- confirm that no protocol operation remains blocked indefinitely.

### Step 10 — Generate Evidence

Generate the mandatory coverage and protocol reports.

---

## 13. Coverage Matrix

The generated coverage matrix shall contain at least:

| Field | Requirement |
|---|---|
| Method name | Exported public Python method name |
| Canonical method | Canonical public name |
| Implementation target | Underlying implementation the method delegates to |
| Device-facing | Yes/No |
| Transport type | SCPI, serial, HTTP, SDK, and so on |
| Protocol vector | Vector identifier |
| Callability tested | Yes/No |
| Outbound verified | PASS/FAIL/N/A |
| Raw response verified | PASS/FAIL/N/A |
| Parsed result verified | PASS/FAIL/N/A |
| Protocol error tested | PASS/FAIL/N/A |
| Recovery tested | PASS/FAIL/N/A |
| Result | PASS/FAIL/SKIP/EXCLUDED |
| Evidence | Trace or report reference |
| Reason | Required for SKIP or EXCLUDED |

Aliases shall be listed individually, even when they map to the same implementation target.

---

## 14. Coverage Metrics

The report shall calculate:

```text
Method Inventory Coverage
    = inventoried public methods / exported public methods

Method Callability Coverage
    = called public methods / executable public methods

Protocol Vector Coverage
    = device-facing methods with vectors / device-facing public methods

Outbound Protocol Coverage
    = outbound-verified methods / device-facing executable methods

Inbound Protocol Coverage
    = response-verified methods / response-producing executable methods

Protocol Error Coverage
    = executed protocol-error vectors / applicable protocol-error vectors
```

Skipped and excluded methods shall remain visible in the report.

---

## 15. Acceptance Criteria

A driver passes LPDS-019 only when:

1. 100% of exported public Python API methods are inventoried;
2. 100% of supported executable public methods are called directly through their plain Python API;
3. every device-facing public method has a protocol vector or approved exclusion;
4. every executed device-facing method transmits the expected protocol operation;
5. every response-producing method receives and parses the expected protocol response;
6. every returned value has the documented Python type;
7. command-only methods do not incorrectly wait for a response;
8. documented protocol timeouts and malformed responses produce the expected failure, raised as the correct LPDS-007 exception;
9. recoverable protocol failures permit a subsequent known-good call after recovery;
10. aliases produce protocol behavior equivalent to their canonical method unless explicitly documented otherwise;
11. every PASS result has traceable evidence;
12. all mandatory vectors pass;
13. every SKIP or EXCLUDED result has a documented and approved reason.

---

## 16. Failure Conditions

LPDS-019 shall fail when:

- an exported public method is omitted from inventory;
- a supported public method cannot be invoked directly through its plain Python API;
- the method calls the wrong driver operation;
- a device-facing method has no protocol vector and no approved exclusion;
- the driver transmits the wrong command, query, request, frame, or SDK call;
- arguments are serialized incorrectly;
- command framing, checksum, terminator, address, or payload is incorrect;
- a query reads the wrong response or parses it incorrectly;
- the returned Python value has the wrong type or content;
- a command-only operation waits for an undefined response;
- a device protocol error is reported as success;
- a timeout or malformed response produces undocumented behavior, or raises the wrong LPDS-007 exception class;
- a documented recoverable protocol failure leaves communication unusable;
- an alias produces different protocol behavior without documentation;
- required trace evidence is missing.

---

## 17. Result Statuses

Only these statuses are permitted:

- **PASS** — required call and protocol oracles passed;
- **FAIL** — one or more required call or protocol oracles failed;
- **SKIP** — execution could not occur because a declared prerequisite was unavailable;
- **EXCLUDED** — execution is intentionally prohibited or not applicable and has an approved reason;
- **NOT RUN** — no execution occurred; this fails acceptance unless converted to approved SKIP or EXCLUDED.

---

## 18. Evidence and Reporting

Each run shall produce:

- a pytest JUnit XML report (`junit.xml`);
- a pytest HTML report (for example via `pytest-html`) or equivalent human-readable run report;
- machine-readable method inventory;
- CSV or JSON coverage matrix;
- protocol vector results;
- outbound protocol trace;
- inbound protocol trace where responses apply;
- environment and driver version record;
- connected device identity when available;
- skips and exclusions report;
- Markdown summary.

Recommended layout:

```text
results/call_protocol_conformance/<driver>/<timestamp>/
├── junit.xml
├── pytest_report.html
├── conformance_summary.md
├── method_inventory.json
├── method_coverage.csv
├── protocol_vector_results.json
├── outbound_trace.log
├── inbound_trace.log
├── environment.json
├── device_identity.json
└── exclusions.json
```

Every trace entry shall identify the method and protocol vector that produced it.

LPDS-008 defines the common evidence envelope, event schema, manifest, and storage rules shared across the platform; LPDS-019 remains authoritative for what must be verified and captured at the protocol boundary. The layout above is a conformance-specific view and should be reachable from, or nested under, the LPDS-008 §11 canonical result root for the same run rather than maintained as a wholly separate evidence tree.

---

## 19. Integration with LPDS-017

LPDS-017 may provide the following source information for LPDS-019:

- canonical method name;
- aliases;
- signature;
- argument types;
- return type;
- expected protocol operation;
- response schema;
- timeout behavior;
- protocol errors;
- connection preconditions.

LPDS-019 shall not use LPDS-017 to assess complete device-capability implementation. It uses LPDS-017 only to define and verify the declared public calls and expected protocol exchange.

Where a method is bound to a capability record under the LPDS-013 capability model, the protocol vector and the capability record shall agree on method name, arguments, and return model (CV-10, §7.3).

---

## 20. Change Control

Whenever a public method or its protocol behavior is added, removed, renamed, aliased, deprecated, or changed, the same driver revision shall update:

- method inventory;
- protocol vector;
- expected outbound operation;
- expected response or no-response declaration;
- expected return type;
- protocol-error vectors when applicable;
- conformance evidence.

A public call or protocol change without a corresponding LPDS-019 update shall fail conformance review.

---

## 21. Review Checklist

1. Are all exported public Python API methods inventoried?
2. Was every supported public method called directly through its plain Python API?
3. Is every device-facing method linked to a protocol vector?
4. Was the actual outbound protocol operation captured?
5. Does the outbound operation match the expected command, frame, request, or SDK call?
6. Was the raw device response captured when applicable?
7. Was the response parsed correctly?
8. Does the returned Python value have the expected type and value?
9. Are command-only operations explicitly marked as no-response operations?
10. Were documented timeouts and malformed responses tested?
11. Were device protocol errors reported correctly, as the correct LPDS-007 exception class?
12. Was communication restored after recoverable protocol failures?
13. Do aliases produce equivalent protocol behavior?
14. Are all skips and exclusions justified?
15. Is every result traceable to protocol evidence?

---

## 22. Minimum Definition of Done

LPDS-019 is complete when:

- the full public method inventory is generated;
- every supported public method is called directly through its plain Python API;
- every device-facing public method has an approved protocol vector;
- every executed device-facing method has outbound protocol evidence;
- every response-producing method has inbound and parsed-result evidence;
- applicable protocol error and recovery vectors pass;
- all required reports are generated;
- no mandatory call or protocol verification remains NOT RUN;
- all acceptance criteria in Section 15 pass.

---

## 23. Goal

Provide objective proof that every declared driver public API call reaches the intended device protocol operation and that every applicable device response is correctly received, interpreted, and returned by the driver — using nothing but the driver's plain Python interface.

---

## Appendix A — Changes from Version 1.0

Version 1.1 narrows LPDS-019 to:

- public method discovery;
- plain Python callability;
- outbound driver-to-device protocol verification;
- inbound device-to-driver response verification;
- protocol parsing;
- protocol errors, timeouts, and recovery;
- traceable conformance evidence.

The following subjects were removed from LPDS-019 scope:

- full driver implementation coverage;
- vendor-manual feature completeness;
- architecture review;
- packaging and release readiness;
- physical output accuracy;
- calibration verification;
- performance and soak testing;
- general documentation completeness;
- correctness of any framework-specific adapter beyond confirming it is a thin pass-through (see Appendix B).

---

## Appendix B — Example (Non-Normative): CLI Adapter Conformance Mapping

> **This appendix is illustrative only.** It is not a requirement of LPDS-019, and no particular automation framework is a mandated or implied consumer of any LPDS driver. It exists to show, briefly, how the driver-level conformance vectors above map onto **one possible** framework adapter. The same mapping pattern applies equally to a pytest adapter, a REST adapter, a GUI test-bench adapter, or any other thin translation layer.

### B.1 The pass-through principle

An adapter contains no device logic. A CLI adapter command is conformant **if and only if**:

1. the driver method it wraps is itself LPDS-019 conformant (proven by the vectors in §7.3, independent of any framework); and
2. the command forwards arguments to the driver method unchanged (after only the CLI framework's own argument-string conversion);
3. the command forwards the driver method's return value unchanged (after only the serialization the CLI framework requires to display or pass along a result);
4. the command forwards a raised `DriverError` as a CLI command failure without swallowing, downgrading, or reclassifying it.

Adapter conformance testing therefore does not re-verify protocol behavior (that is already proven at the driver level) — it verifies only that the translation layer is faithful.

### B.2 Illustrative adapter

```python
class PowerSupplyCli:
    """Thin CLI adapter over PowerSupplyDriver."""

    def __init__(self, driver: PowerSupplyDriver):
        self._driver = driver

    def set_dc_voltage(self, channel, voltage):
        return self._driver.set_dc_voltage(channel=int(channel), voltage=float(voltage))

    def get_identity(self):
        return self._driver.get_identity()
```

### B.3 Illustrative adapter-level test

```python
def test_set_dc_voltage_command_is_a_thin_passthrough(mocker):
    driver = mocker.Mock(spec=PowerSupplyDriver)
    cli = PowerSupplyCli(driver)

    cli.set_dc_voltage("1", "5.0")

    driver.set_dc_voltage.assert_called_once_with(channel=1, voltage=5.0)


def test_get_identity_command_forwards_driver_error(mocker):
    driver = mocker.Mock(spec=PowerSupplyDriver)
    driver.get_identity.side_effect = DriverTimeoutError(code="LPDS-TMO-001", message="timed out")
    cli = PowerSupplyCli(driver)

    with pytest.raises(DriverTimeoutError):
        cli.get_identity()
```

### B.4 Mapping table

| Driver-level conformance vector (§7.3) | Adapter-level concern | Adapter test proves |
|---|---|---|
| CV-1 (command-only outbound) | Argument forwarding | Command passes `channel`/`voltage` to the driver method unchanged |
| CV-2 (query round trip) | Return forwarding | Command returns the driver's `IdentityInfo` (or its CLI-displayable form) unchanged |
| CV-3–CV-8 (state/argument/protocol errors, timeout, recovery) | Exception forwarding | Command fails with the driver's `DriverError` rather than a generic adapter failure |
| CV-9 (alias equivalence) | Alias forwarding | Command aliases (if any) call the same driver method as their canonical command |
| CV-10 (capability binding) | Discovery forwarding | Command documentation/arguments match the capability record the driver exposes |

A CLI conformance suite built on this pattern is not re-running LPDS-019 — it is a separate, much smaller suite whose only job is proving the thinness of the translation. The device-protocol proof stays entirely at the driver level, in plain Python, per the rest of this document.
