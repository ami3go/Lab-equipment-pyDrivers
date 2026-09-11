# AI Guides — Lab pyDrivers Standard (LPDS)

This folder is the normative standard that AI agents and human contributors follow when
designing, building, testing, and releasing a driver for this hub's ecosystem of
independent lab-equipment driver repositories.

## Core architecture: driver first, adapter later

Every document in this series is built on one principle:

- **Driver** — a plain, framework-independent Python class exposing a documented public
  API (typed methods, properties, docstrings). A driver must be fully constructible,
  controllable, and testable from a plain Python/pytest session with **no** test-automation
  framework installed. It shall not import, subclass, or depend on a pytest plugin, or
  any other framework.
- **Adapter** — a separate, thin translation layer that exposes an already-verified
  driver's public API to one specific automation framework or interface: pytest
  fixtures, a CLI, a REST endpoint, a GUI test bench, etc. An adapter
  contains no device logic of its own; it only translates calls and results between its
  framework and the driver's public API. The same driver can have several adapters at
  once, written and versioned independently of the driver and of each other.
- **Order of work**: design, implement, and verify the driver completely on its own — unit
  tests against a simulated transport, then hardware-in-the-loop tests against real
  equipment — *before* writing any adapter. An adapter is verified separately afterward,
  with thin translation-correctness tests, not device-logic tests.

This is why the series is framework-agnostic where the original single-automation-framework
standard it descends from was not: any automation framework is always an optional adapter
on top of a driver, never a requirement of the driver itself.

## Documents

| ID | Title | Covers |
|---|---|---|
| [LPDS-001](LPDS-001_Platform_Requirements.md) | Platform Requirements | Overall architecture, driver/adapter split, platform-wide requirements |
| [LPDS-002](LPDS-002_Mandatory_Public_API_Standard.md) | Mandatory Public API Standard | Public method naming, signatures, docstrings, risk levels |
| [LPDS-003](LPDS-003_BaseInstrument_Common_Base_Class_Design.md) | BaseInstrument Common Base Class Design | Shared base class: connection/session lifecycle, state machine, timeouts, retries |
| [LPDS-004](LPDS-004_Transport_Layer_Specification.md) | Transport Layer Specification | VISA/serial/TCP/USB/CAN transport abstraction |
| [LPDS-005](LPDS-005_Driver_Package_Specification.md) | Driver Package Specification | Repository/package layout, driver vs. adapters folder split |
| [LPDS-006](LPDS-006_Coding_Standard.md) | Coding Standard | Python style, typing, imports, formatting |
| [LPDS-007](LPDS-007_Error_and_Exception_Standard.md) | Error and Exception Standard | Exception hierarchy, error codes, message format |
| [LPDS-008](LPDS-008_Logging_and_Evidence_Standard.md) | Logging and Evidence Standard | Structured logging, evidence correlation, diagnostics export |
| [LPDS-009](LPDS-009_Testing_Standard.md) | Testing Standard | Unit / hardware-in-the-loop / adapter-conformance test layers |
| [LPDS-010](LPDS-010_Driver_Review_Checklist.md) | Driver Review Checklist | Mandatory pre-release review checklist |
| [LPDS-011](LPDS-011_Release_Process.md) | Release Process | Versioning, packaging, changelog, release steps |
| [LPDS-012](LPDS-012_Automation_and_GUI_Integration_Specification.md) | Automation and GUI Integration Specification | Integrating drivers into GUIs, dashboards, and automation consumers |
| [LPDS-013](LPDS-013_Capability_Model.md) | Capability Model | Self-describing capability taxonomy and identifiers |
| [LPDS-014](LPDS-014_Driver_Configuration_Model_Specification.md) | Driver Configuration Model Specification | Connection parameters, calibration, limits schema |
| [LPDS-015](LPDS-015_Plugin_and_Adapter_Architecture.md) | Plugin and Adapter Architecture | Entry-points based discovery for drivers and, separately, adapters |
| [LPDS-017](LPDS-017_AI_Driver_Contract.md) | AI Driver Contract | `ai_contract.yaml`: machine-readable, adapter-independent driver description |
| [LPDS-018](LPDS-018_AI_Test_Bench_Contract.md) | AI Test Bench Contract | Multi-driver bench topology and system-level contract |
| [LPDS-019](LPDS-019_Driver_Conformance_Test_Specification.md) | Driver Conformance Test Specification | Call/protocol conformance vectors for a driver's public API, with a worked CLI adapter example |
| [LPDS-020](LPDS-020_Driver_Implementation_Lifecycle.md) | Driver Implementation Lifecycle | Phase/gate implementation and review process |

(Numbering intentionally skips 016 and starts renumbering-free at 017 to preserve
traceability with this series' origin document set.)

## Provenance

This standard was migrated and generalized from an earlier, single-automation-framework-
specific "RFDS" driver standard used in an earlier, framework-coupled driver project. The
generalization work stripped every automation-framework dependency out of the
driver-design requirements and moved framework integration into the optional adapter
concept described above.
