# LPDS-015 — Plugin and Adapter Architecture

## Dynamic Driver and Adapter Discovery

**Version:** 1.0
**Document ID:** LPDS-015
**Status:** Draft project requirement
**Applies to:** LPDS platform services, all discoverable LPDS driver packages, LPDS adapter packages, generic GUIs, framework adapters (pytest, CLI, REST, and others), AI planners, bench managers, validation tools, and release packages

---

## 1. Purpose

This specification defines the LPDS plugin architecture used to discover, identify, validate, select, load, instantiate, and unload installed LPDS driver packages, and the parallel architecture used to discover, validate, select, and load the framework-specific adapters that expose those drivers to pytest, a CLI, a REST layer, or any other automation framework — all without hard-coded imports.

The architecture shall allow a generic application to:

1. enumerate installed LPDS drivers;
2. identify each driver by a stable plugin identifier;
3. inspect driver metadata without connecting to hardware;
4. determine whether the driver is compatible with the current LPDS platform and runtime;
5. select a driver by explicit identity, supported model, transport, or declared capabilities;
6. load only the selected driver provider;
7. instantiate a driver without performing implicit hardware I/O;
8. keep multiple drivers isolated by stable aliases;
9. report discovery, compatibility, conflict, load, and unload failures consistently;
10. produce machine-readable discovery and loading evidence;
11. independently enumerate installed adapters that wrap a given driver plugin ID for a specific automation framework;
12. select and load the adapter appropriate to the active framework without the driver package needing to know that framework exists.

LPDS-015 shall provide dynamic extensibility without weakening LPDS requirements for explicit APIs, configuration validation, capability discovery, AI contracts, safety, protocol conformance, traceability, or release control.

---

## 2. Scope Boundary

### 2.1 In scope

LPDS-015 covers:

- discovery of installed Python distribution packages that advertise LPDS drivers;
- discovery of installed Python distribution packages that advertise LPDS adapters;
- the canonical Python entry-point groups used by LPDS drivers and LPDS adapters;
- stable plugin and adapter identifiers and naming rules;
- plugin provider and adapter provider contracts;
- machine-readable plugin manifests and adapter manifests;
- metadata-only candidate enumeration;
- isolated provider probing and validation;
- registry construction and refresh, for both drivers and adapters;
- compatibility and dependency evaluation;
- deterministic driver and adapter resolution;
- explicit loading and instantiation;
- framework-specific runtime integration performed by an adapter;
- application and GUI integration;
- capability-based selection integration;
- configuration handoff integration;
- AI contract and test-bench contract integration;
- duplicate plugin/adapter and version-conflict handling;
- enable, disable, allow-list, block-list, and quarantine behavior;
- unload and cleanup behavior;
- diagnostics, evidence, tests, reviews, and release requirements;
- security boundaries for executable plugin and adapter code.

### 2.2 Out of scope

LPDS-015 does not define:

- public driver method semantics;
- detailed capability taxonomy;
- configuration-field semantics for a specific driver;
- device protocol commands or response parsing;
- transport implementation;
- physical device discovery algorithms for a specific protocol;
- automatic installation of packages from the internet;
- package repository selection or dependency resolution by `pip`;
- remote code download;
- cryptographic signing infrastructure beyond integration with LPDS release evidence;
- complete operating-system process sandboxing;
- physical safety certification;
- bench wiring or resource topology;
- protocol-call conformance testing;
- hot replacement of Python code inside an active process;
- the internal design of any specific framework adapter (pytest fixture design, CLI argument design, REST route design, and similar) beyond the discovery/loading contract it must satisfy.

These subjects remain governed by the applicable LPDS specifications, device requirements, Python packaging tools, and deployment policy.

---

## 3. Normative Terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement; deviations require documented justification;
- **may** — permitted implementation choice;
- **plugin** — an installed LPDS driver distribution advertised through the LPDS driver entry-point group;
- **adapter** — an installed distribution that wraps one driver plugin's public API for one specific automation framework or interface, advertised through the LPDS adapter entry-point group;
- **plugin provider** — the side-effect-free Python object loaded from a driver entry point and used to return metadata and create driver instances;
- **adapter provider** — the side-effect-free Python object loaded from an adapter entry point and used to return metadata and bind a framework-specific object around an already-created driver instance;
- **plugin descriptor** — validated machine-readable metadata describing one driver plugin;
- **adapter descriptor** — validated machine-readable metadata describing one adapter;
- **plugin manifest** — packaged JSON representation of the plugin descriptor;
- **adapter manifest** — packaged JSON representation of the adapter descriptor;
- **candidate** — an installed entry point (driver or adapter) found before provider validation;
- **registry** — the current validated collection of discovered plugin records and adapter records;
- **resolver** — component that selects one plugin or one adapter from explicit requirements;
- **loader** — component that imports the selected provider and requests an instance or a binding;
- **instance** — one created driver instance object; for an adapter, one created framework-binding object produced by wrapping a driver instance;
- **hardware discovery** — active or passive search for connected physical devices; this is separate from installed-plugin and installed-adapter discovery;
- **distribution name** — the Python package-distribution name recorded in installed package metadata;
- **import package** — the Python package imported by the runtime;
- **plugin ID** — the stable LPDS identifier used to select a driver plugin independently of its installed version;
- **adapter ID** — the stable LPDS identifier used to select an adapter independently of its installed version;
- **target plugin ID** — the plugin ID of the driver an adapter is declared to wrap;
- **plugin API version** — the version of the provider/descriptor contract implemented by the driver plugin;
- **adapter API version** — the version of the provider/descriptor contract implemented by the adapter;
- **host** — the LPDS platform, GUI, orchestration manager, AI planner, or other application consuming plugins and adapters.

---

## 4. Architectural Principles

### 4.1 Discovery is not loading

Enumerating installed plugin or adapter entry points shall not instantiate a driver, bind an adapter, open a transport, scan the network, enumerate VISA resources, open a serial port, call a vendor SDK, or connect to hardware.

### 4.2 Loading is not connecting

Loading a provider or creating a driver instance shall not implicitly connect to a physical device unless a separately approved device-specific architecture requires constructor-time connection and documents the exception. New LPDS drivers shall not use such an exception. Binding an adapter around an existing driver instance shall never itself open a connection either.

### 4.3 Installed plugins and adapters are executable code

A plugin or adapter loaded into the host process has the privileges of that process. Entry-point discovery and quarantine are not security sandboxes. Only trusted, reviewed distributions shall be loaded in-process.

### 4.4 Metadata before behavior

The host shall inspect and validate plugin identity, version, compatibility, dependencies, manifest schema, and declared resources before creating a driver instance — and shall apply the equivalent inspection to an adapter's identity, target plugin ID, and framework requirements before binding it.

### 4.5 Explicit selection before state-changing use

A state-changing test, GUI workflow, or AI-generated plan shall not select a driver or an adapter through fuzzy name matching or an unresolved tie. It shall use an explicit plugin ID or adapter ID, or an unambiguous, evidence-based resolution result.

### 4.6 Deterministic conflict handling

Duplicate identifiers, incompatible versions, ambiguous candidates, invalid manifests, and missing dependencies shall produce visible registry states, for both plugins and adapters. The host shall not silently select whichever plugin or adapter is returned first by the operating system or Python runtime.

### 4.7 Import safety

Provider modules, driver modules, adapter modules, API-reference generation, capability inspection, and plugin/adapter validation shall be possible without connected hardware.

### 4.8 Source-of-truth separation

The plugin descriptor and adapter descriptor shall reference authoritative LPDS artifacts rather than duplicating their complete content. Public API methods, capabilities, configuration, AI semantics, bench topology, and protocol vectors retain their own authoritative sources.

### 4.9 Failure isolation

One broken or incompatible plugin or adapter shall not prevent other valid plugins or adapters from being discovered and used.

### 4.10 Observable lifecycle

Discovery, validation, selection, loading, instantiation, binding, unbinding, unload, and failure states shall be queryable and recorded in diagnostics, for both the driver-plugin lifecycle and the adapter lifecycle.

---

## 5. Logical Architecture

Driver discovery and loading path:

```text
Installed Python distributions
            ↓
importlib.metadata entry-point enumeration (lpds.drivers)
            ↓
Candidate records — no provider import
            ↓
Policy filter — enabled, allow-list, block-list
            ↓
Isolated provider probe with finite timeout
            ↓
Manifest and compatibility validation
            ↓
Validated LPDS driver registry
            ↓
Explicit ID or deterministic requirements resolver
            ↓
Selected plugin provider
            ↓
Configuration validation and instance request
            ↓
Driver instance — a plain, unconnected Python object
            ↓
Explicit connect() call or application action
            ↓
Physical device or approved simulator
```

Adapter discovery and binding path (independent of the driver path above):

```text
Installed Python distributions
            ↓
importlib.metadata entry-point enumeration (lpds.adapters)
            ↓
Candidate records — no provider import
            ↓
Policy filter — enabled, allow-list, block-list
            ↓
Isolated provider probe with finite timeout
            ↓
Manifest and compatibility validation (target_plugin_id / plugin-API range / framework)
            ↓
Validated LPDS adapter registry
            ↓
Explicit ID or deterministic requirements resolver
            ↓
Selected adapter provider
            ↓
bind() against an already-created, unconnected driver instance
            ↓
Framework-specific binding object (pytest fixture, CLI command group, REST route table, ...)
```

The hardware connection boundary shall remain below plugin discovery, provider validation, and normal driver instantiation. Adapter discovery and binding never touch hardware directly: an adapter only ever calls the already-validated public API of a driver instance it has been handed, and never creates or connects that instance itself.

---

## 6. Canonical Discovery Mechanism

### 6.1 Python entry-point group for drivers

Every discoverable LPDS driver distribution shall register exactly one entry point per driver provider in this group:

```text
lpds.drivers
```

The group name is owned by the LPDS platform and identifies objects implementing the LPDS driver-plugin provider contract.

### 6.2 Driver entry-point declaration

A driver shall declare its provider in `pyproject.toml` using equivalent metadata to:

```toml
[project.entry-points."lpds.drivers"]
"keysight.n6700" = "keysight_n6700.plugin:KeysightN6700Plugin"
```

The entry-point name shall equal the plugin ID.

The entry-point value shall reference one provider class or provider factory using the standard Python `module:attribute` form.

### 6.3 Primary discovery API

The platform shall enumerate entry points using the standard-library `importlib.metadata` API or a compatible implementation.

Equivalent behavior:

```python
from importlib.metadata import entry_points

candidates = entry_points(group="lpds.drivers")
```

Legacy `pkg_resources` discovery shall not be the primary implementation for new LPDS platform code.

### 6.4 No arbitrary filesystem scanning by default

The platform shall not recursively import Python files, scan project directories for a driver module by convention, or execute packages merely because their names match a naming convention.

An explicitly configured development-directory source may be supported for local engineering use, but it shall:

- be disabled by default in production;
- use an explicit path allow-list;
- produce a source type of `development_path`;
- never outrank an explicitly selected installed plugin;
- apply the same provider, manifest, validation, timeout, and conflict rules;
- be visible in evidence.

### 6.5 No automatic installation

Discovery shall inspect the current Python environment only. A missing driver may be reported with installation guidance, but the plugin manager shall not automatically run `pip`, download packages, modify the environment, or install vendor software.

### 6.6 Python entry-point group for adapters

Every discoverable LPDS adapter distribution shall register exactly one entry point per adapter provider in a separate group:

```text
lpds.adapters
```

This group is owned by the LPDS platform and identifies objects implementing the LPDS adapter provider contract (§10.5). It is enumerated, screened, probed, and validated using the same mechanism as §6.1–§6.5, substituting `lpds.adapters` for `lpds.drivers`:

```toml
[project.entry-points."lpds.adapters"]
"cli.keysight.n6700" = "keysight_n6700_cli_adapter.plugin:KeysightN6700CliAdapterPlugin"
```

```python
from importlib.metadata import entry_points

adapter_candidates = entry_points(group="lpds.adapters")
```

Adapter discovery is independent of driver discovery: a host may enumerate, validate, and inspect installed adapters without ever loading the driver they target, and a driver may be discovered, loaded, and used with zero adapters installed. Neither entry-point group shall be treated as a subset or superset of the other; they are parallel, separately versioned registries.

---

## 7. Plugin and Adapter Identifier Rules

### 7.1 Plugin ID format

Each driver plugin shall have one stable identifier:

```text
<vendor>.<device_family>
```

Rules:

- lowercase ASCII;
- two or more dot-separated segments;
- each segment contains only `a-z`, `0-9`, and `_`;
- no spaces or hyphens;
- no version number;
- no transport name unless the transport defines a genuinely separate driver implementation;
- stable across compatible releases;
- globally unique within the deployed LPDS environment.

Examples:

```text
keysight.n6700
keysight.hp34401a
bk_precision.8500b
openbench.eresistor_matrix
phidgets.interfacekit_relay
votsch.climate_chamber
```

### 7.2 Relationship to project naming

A plugin ID is not required to equal the project folder, Python distribution, import package, or driver class name.

Example:

| Identity type | Example |
|---|---|
| Plugin ID | `keysight.n6700` |
| Stable project root | `keysight_n6700/` |
| Python distribution | `keysight-n6700` |
| Python import package | `keysight_n6700` |
| Driver class | `KeysightN6700Driver` |

All forms shall be declared in the plugin manifest and checked for consistency.

### 7.3 Plugin identifier ownership

A plugin ID shall not be reused for an unrelated driver or incompatible device family. A replacement implementation for the same declared driver may retain the ID only when compatibility, migration, and ownership are explicitly reviewed.

### 7.4 Adapter ID format and ownership

Each adapter shall have one stable identifier, independent of but related to the driver it wraps:

```text
<framework>.<vendor>.<device_family>
```

using the same character rules as §7.1 (lowercase ASCII, dot-separated segments, `a-z0-9_` per segment, no version number, stable, globally unique within the deployed LPDS environment).

Examples:

```text
cli.keysight.n6700
pytest.keysight.n6700
cli.bk_precision.8500b
```

The adapter identifier is descriptive only; the authoritative link between an adapter and the driver it wraps is the manifest's `target_plugin_id` field (§9.6), not any parsing of the adapter ID string. An adapter ID shall not be reused for an adapter targeting a different plugin ID or a different framework.

---

## 8. Required Driver and Adapter Artifacts

### 8.1 Driver package artifacts

Every discoverable driver package shall add these artifacts to the LPDS-005 structure:

```text
<driver_name>/
├── <driver_name>/
│   ├── plugin.py
│   └── resources/
│       └── plugin_manifest.json
├── tests/
│   └── plugin/
│       ├── test_entry_point.py
│       ├── test_manifest.py
│       ├── test_import_safety.py
│       └── test_provider_lifecycle.py
└── docs/
    └── plugin_integration.md
```

The package shall also contain the `lpds.drivers` entry-point declaration in `pyproject.toml`.

`plugin.py` shall remain small. It shall adapt the driver package to the LPDS plugin-provider contract and shall not duplicate device protocol or public-API logic that belongs in the driver itself.

### 8.2 Adapter package artifacts

Every discoverable adapter shall add equivalent artifacts, normally in its own, separately released distribution:

```text
<driver_name>_<framework>_adapter/
├── <driver_name>_<framework>_adapter/
│   ├── plugin.py
│   ├── adapter.py
│   └── resources/
│       └── adapter_manifest.json
├── tests/
│   └── adapter/
│       ├── test_entry_point.py
│       ├── test_manifest.py
│       ├── test_import_safety.py
│       └── test_provider_lifecycle.py
└── docs/
    └── adapter_integration.md
```

The package shall also contain the `lpds.adapters` entry-point declaration in `pyproject.toml`.

An adapter should be packaged as its own independent Python distribution so that installing a driver never pulls in a specific automation framework as a mandatory dependency. Where project policy explicitly allows an adapter to ship as an optional extra of the driver's own distribution, it shall still register through the separate `lpds.adapters` entry-point group, shall remain importable independently of the driver's own runtime import path, and shall not be imported by the driver's own non-adapter code.

---

## 9. Plugin Manifest

### 9.1 Location and format

The canonical packaged plugin manifest shall be:

```text
<import_package>/resources/plugin_manifest.json
```

It shall be UTF-8 JSON and shall validate against the LPDS plugin-manifest schema for the declared schema version.

### 9.2 Mandatory fields

The plugin manifest shall contain at least:

- `schema_version`;
- `plugin_api_version`;
- `plugin_id`;
- `driver_name`;
- `display_name`;
- `description`;
- `distribution_name`;
- `distribution_version`;
- `provider`;
- `driver_import_path`;
- `driver_class`;
- `supported_device_families`;
- `supported_models`;
- `supported_transports`;
- `capability_descriptor` reference;
- `configuration_schema` reference;
- `ai_contract` reference;
- `documentation` reference;
- `minimum_python`;
- `lpds_platform_version` requirement;
- `optional_dependency_groups`;
- `multi_instance`;
- `thread_safe` declaration;
- `simulation_supported`;
- `hardware_discovery_supported`;
- `load_policy`;
- `deprecation` object;
- `manifest_hash_algorithm`.

The manifest shall not declare any automation-framework version requirement; a driver plugin has no framework dependency by construction. Framework version requirements belong to the adapter manifest (§9.6).

### 9.2.1 Resource-reference forms

Descriptor references shall use explicit, machine-readable forms rather than ambiguous relative strings. Permitted reference kinds are:

- `python_object` — a Python `module:attribute` that can be imported without hardware access;
- `package_resource` — a file installed inside an import package and readable through `importlib.resources`;
- `distribution_project_url` — a named project URL from installed distribution metadata;
- `repository_path` — a path available in the full LPDS source repository but not guaranteed to exist in a wheel.

Runtime-required schemas and contracts shall use `package_resource`. When LPDS-005 keeps the canonical authored file outside the import package, the release build shall generate a runtime package-resource copy and prove by SHA-256 that it matches the canonical source. Generated copies shall not be edited independently.

A reference object shall contain the fields needed for its kind and should contain a SHA-256 value when it identifies file content.

### 9.3 Example plugin manifest

```json
{
  "schema_version": "1.0",
  "plugin_api_version": "1.0",
  "plugin_id": "keysight.n6700",
  "driver_name": "keysight_n6700",
  "display_name": "Keysight N6700 Power System Driver",
  "description": "LPDS Python instrument driver for supported Keysight N6700-family mainframes and modules.",
  "distribution_name": "keysight-n6700",
  "distribution_version": "26.3",
  "provider": "keysight_n6700.plugin:KeysightN6700Plugin",
  "driver_import_path": "keysight_n6700.driver",
  "driver_class": "KeysightN6700Driver",
  "supported_device_families": ["keysight_n6700"],
  "supported_models": ["N6700A", "N6700B", "N6705A", "N6705B", "N6705C"],
  "supported_transports": ["visa", "tcpip", "usb", "simulator"],
  "capability_descriptor": {
    "kind": "python_object",
    "value": "keysight_n6700.capabilities:get_capabilities"
  },
  "configuration_schema": {
    "kind": "package_resource",
    "package": "keysight_n6700",
    "path": "resources/config.schema.json",
    "canonical_source": "config/schema.json",
    "sha256": "<digest>"
  },
  "ai_contract": {
    "kind": "package_resource",
    "package": "keysight_n6700",
    "path": "resources/ai_contract.yaml",
    "canonical_source": "ai/ai_contract.yaml",
    "sha256": "<digest>"
  },
  "documentation": {
    "kind": "distribution_project_url",
    "name": "Documentation"
  },
  "minimum_python": ">=3.11",
  "lpds_platform_version": ">=1,<2",
  "optional_dependency_groups": ["visa", "usb"],
  "multi_instance": true,
  "thread_safe": false,
  "simulation_supported": true,
  "hardware_discovery_supported": true,
  "load_policy": "explicit",
  "deprecation": {
    "deprecated": false,
    "replacement_plugin_id": null,
    "removal_version": null
  },
  "manifest_hash_algorithm": "sha256"
}
```

The example values are illustrative. Device support shall be based on the driver's reviewed compatibility evidence.

### 9.4 Manifest synchronization

The provider shall return descriptor data equivalent to the packaged manifest. The release build shall fail when the entry point, provider, manifest, installed distribution metadata, capability source, configuration schema, AI contract, documentation, or version files conflict.

### 9.5 No secrets

The manifest shall not contain:

- passwords or tokens;
- private keys;
- personal paths;
- real bench addresses;
- private COM-port assignments;
- customer identifiers;
- device serial numbers from a deployed bench.

### 9.6 Adapter Manifest

#### 9.6.1 Location and format

The canonical packaged adapter manifest shall be:

```text
<adapter_import_package>/resources/adapter_manifest.json
```

It shall be UTF-8 JSON and shall validate against the LPDS adapter-manifest schema for the declared schema version.

#### 9.6.2 Mandatory fields

The adapter manifest shall contain at least:

- `schema_version`;
- `adapter_api_version`;
- `adapter_id`;
- `target_plugin_id`;
- `target_plugin_api_version` (the plugin-API range of driver plugins this adapter can bind to);
- `adapter_name`;
- `display_name`;
- `description`;
- `distribution_name`;
- `distribution_version`;
- `provider`;
- `adapter_import_path`;
- `adapter_class`;
- `framework` (for example `pytest`, `cli`, `rest`);
- `framework_version` requirement;
- `minimum_python`;
- `lpds_platform_version` requirement;
- `deprecation` object;
- `manifest_hash_algorithm`.

Resource-reference forms follow §9.2.1. An adapter manifest shall not redeclare capability, configuration-schema, or AI-contract references; those remain owned exclusively by the target driver's own plugin manifest (§4.8).

#### 9.6.3 Example adapter manifest

```json
{
  "schema_version": "1.0",
  "adapter_api_version": "1.0",
  "adapter_id": "cli.keysight.n6700",
  "target_plugin_id": "keysight.n6700",
  "target_plugin_api_version": ">=1,<2",
  "adapter_name": "keysight_n6700_cli_adapter",
  "display_name": "Keysight N6700 CLI Adapter",
  "description": "CLI adapter wrapping the keysight.n6700 LPDS driver.",
  "distribution_name": "keysight-n6700-cli-adapter",
  "distribution_version": "26.3",
  "provider": "keysight_n6700_cli_adapter.plugin:KeysightN6700CliAdapterPlugin",
  "adapter_import_path": "keysight_n6700_cli_adapter.adapter",
  "adapter_class": "KeysightN6700CliLibrary",
  "framework": "cli",
  "framework_version": ">=1,<2",
  "minimum_python": ">=3.11",
  "lpds_platform_version": ">=1,<2",
  "deprecation": {
    "deprecated": false,
    "replacement_adapter_id": null,
    "removal_version": null
  },
  "manifest_hash_algorithm": "sha256"
}
```

#### 9.6.4 Manifest synchronization

The adapter provider shall return descriptor data equivalent to the packaged adapter manifest. The release build shall fail when the entry point, provider, manifest, installed distribution metadata, or version files conflict, using the same rule as §9.4.

#### 9.6.5 No secrets

The adapter manifest is subject to the same no-secrets rule as §9.5.

---

## 10. Plugin Provider Contract

### 10.1 Required provider operations

A driver provider shall implement behavior equivalent to:

```python
class DriverPluginProvider:
    @classmethod
    def get_descriptor(cls) -> dict:
        """Return the validated plugin descriptor without hardware I/O."""

    @classmethod
    def validate_environment(cls) -> dict:
        """Return dependency and runtime compatibility information."""

    @classmethod
    def create_driver(cls, *, config: dict | None = None) -> object:
        """Create one unconnected driver instance."""
```

A provider may additionally implement:

```python
    @classmethod
    def discover_hardware(cls, *, profile: dict) -> list[dict]:
        """Perform an explicit, read-only, bounded hardware search."""

    @classmethod
    def shutdown_provider(cls) -> None:
        """Release provider-level resources when such resources exist."""
```

### 10.2 Provider requirements

`get_descriptor()` shall:

- perform no device I/O;
- open no transport;
- require no credentials;
- return JSON-serializable data;
- complete within the configured provider-probe timeout;
- identify the manifest hash;
- not mutate global application state.

`validate_environment()` shall:

- inspect only local runtime and dependency availability;
- not connect to hardware;
- return explicit `PASS`, `FAIL`, or `WARNING` checks;
- identify missing optional dependencies separately from mandatory dependencies;
- redact sensitive environment values.

`create_driver()` shall:

- validate or delegate validation of provided configuration;
- create an unconnected instance;
- avoid global singleton state unless the manifest explicitly declares a singleton and the architecture review approves it;
- preserve causal exceptions;
- return the public driver object;
- not silently fall back from requested hardware mode to simulation.

### 10.3 Provider constructor

The provider class constructor shall not require device configuration. The platform should use class methods so descriptor inspection does not require provider instantiation.

### 10.4 Factory return types

The object returned by `create_driver()` shall be one of:

- the canonical driver class instance, exposing only its plain Python public API;
- an approved internal wrapper object containing that driver instance, when the platform's own composition requires one;
- a remote-driver service reference when the plugin explicitly implements an approved remote architecture.

Opaque vendor SDK objects shall not be returned as the public plugin instance. The driver instance returned by `create_driver()` shall not itself import, subclass, or depend on any automation framework; exposing the driver to a framework is the responsibility of an adapter (§10.5), never the driver plugin.

### 10.5 Adapter Provider Contract

An adapter provider shall implement behavior equivalent to:

```python
class AdapterPluginProvider:
    @classmethod
    def get_descriptor(cls) -> dict:
        """Return the validated adapter descriptor without hardware I/O."""

    @classmethod
    def validate_environment(cls) -> dict:
        """Return dependency and runtime compatibility information,
        including the target automation framework."""

    @classmethod
    def bind(cls, driver: object, *, alias: str | None = None) -> object:
        """Wrap an already-created, unconnected driver instance for one
        target framework."""
```

Requirements:

- `bind()` shall accept a driver instance created by a `DriverPluginProvider.create_driver()` call, or an equivalent object satisfying the target driver's public API, and shall not create or connect the driver itself;
- `bind()` shall perform no device I/O beyond what the wrapped driver instance already performs when its own public methods are subsequently called;
- an adapter provider's `get_descriptor()` and `validate_environment()` shall be callable even when the target automation framework is not installed; where the framework is a mandatory runtime dependency of the adapter distribution, `validate_environment()` shall report it as a missing mandatory dependency (`FAIL`) rather than raising an unhandled import error, and `bind()` may then fail with `AdapterDependencyError` (§25);
- an adapter shall not duplicate device protocol logic or reimplement driver behavior; it shall only translate between the target framework's calling convention and the driver's existing public API;
- `bind()` shall preserve causal exceptions raised by the wrapped driver rather than swallowing or re-typing them without cause chaining.

---

## 11. Source-of-Truth Rules

| Information | Authoritative source | LPDS-015 use |
|---|---|---|
| Plugin ID and provider contract | `plugin_manifest.json` plus `pyproject.toml` entry point | Discovery and loading |
| Adapter ID, target plugin ID, and provider contract | `adapter_manifest.json` plus `pyproject.toml` entry point | Adapter discovery and binding |
| Installed distribution version | Python distribution metadata | Compatibility and evidence |
| Driver display version | `version.py` under LPDS release rules | Consistency validation |
| Public driver API | driver module and generated API-reference manifest | Import and application usage |
| Capability truth | LPDS-013 authoritative capability model | Static filtering and runtime confirmation |
| Configuration semantics | LPDS-014 schema and configuration model | Validation and handoff |
| AI operational semantics | LPDS-017 `ai_contract.yaml` | AI planning and safe selection |
| Device protocol behavior | LPDS-019 protocol vectors and driver implementation | Not duplicated in plugin or adapter metadata |
| Supported compatibility | `docs/compatibility.md` plus CI/HIL evidence | Manifest validation |
| Release identity and integrity | LPDS release manifest, SBOM, checksums, provenance | Trust and audit |

A conflict between authoritative and derived information shall fail plugin validation, adapter validation, or release validation as applicable.

---

## 12. Discovery Levels

### 12.1 Level D0 — Candidate enumeration

The host shall enumerate `lpds.drivers` entry points without calling `EntryPoint.load()`.

For each candidate, it shall record:

- entry-point name;
- entry-point value;
- entry-point group;
- distribution name;
- installed distribution version;
- source location where safely available;
- discovery timestamp.

D0 shall not import the provider module.

### 12.2 Level D1 — Distribution screening

The host shall evaluate available package metadata before provider loading, including:

- distribution version;
- Python-version requirement;
- declared dependencies;
- enabled/disabled policy;
- allow-list or block-list;
- duplicate entry-point names;
- known revoked or quarantined package versions when deployment policy provides such data.

### 12.3 Level D2 — Isolated provider probe

The host shall load and inspect the provider using a finite, isolated probe process or an equivalent reviewed isolation mechanism.

The probe shall:

- import only the selected provider;
- call `get_descriptor()`;
- call `validate_environment()` when configured;
- serialize the result back to the host;
- terminate on timeout;
- capture standard output, standard error, warnings, exception class, exception message, and traceback;
- avoid exposing credentials;
- not inherit active driver sessions;
- not connect to hardware.

A provider-probe failure shall mark only that plugin as unavailable.

### 12.4 Level D3 — Registry validation

The host shall validate:

- manifest schema;
- plugin ID equality with the entry-point name;
- provider path equality with the entry-point value;
- distribution name and version consistency;
- plugin API compatibility;
- LPDS platform compatibility;
- Python compatibility;
- mandatory dependency availability;
- referenced package resources;
- capability, configuration, and AI-contract references;
- deprecation information;
- duplicate and conflict state.

### 12.5 Level D4 — Optional hardware discovery

Hardware discovery is not part of installed-plugin discovery.

Where supported, it shall be invoked explicitly after D3 and shall:

- be read-only unless a stricter device-specific requirement permits otherwise;
- have a finite timeout;
- use an explicitly supplied search scope;
- avoid changing persistent device configuration;
- record the transport and search profile;
- identify whether each result is verified, probable, or unverified;
- return zero or more candidate device descriptors;
- never connect a driver session automatically;
- never silently choose the first detected device when multiple matches exist.

### 12.6 Adapter discovery levels

Adapter discovery follows the same staged model, using the `lpds.adapters` entry-point group in place of `lpds.drivers`:

- **AD0 — Candidate enumeration**: entry-point name, value, group, distribution, version, source, and timestamp are recorded without importing the adapter provider.
- **AD1 — Distribution screening**: the same categories as D1, evaluated for the adapter distribution.
- **AD2 — Isolated provider probe**: the same isolation, timeout, and capture rules as D2, calling the adapter provider's `get_descriptor()` and `validate_environment()`.
- **AD3 — Registry validation**: manifest schema; adapter ID equality with the entry-point name; provider path equality with the entry-point value; distribution consistency; adapter API compatibility; LPDS platform compatibility; Python and target-framework compatibility; well-formedness of the declared `target_plugin_id` against §7.1; duplicate and conflict state.

An adapter may reach `AVAILABLE` status even when its `target_plugin_id` driver is not installed. The registry shall report this as a distinct `target_plugin_missing` condition rather than as an adapter validation failure, because a driver and the adapters that target it are independently installable and independently versioned.

---

## 13. Registry Model

### 13.1 Plugin registry record

Each plugin registry record shall contain at least:

- plugin ID;
- display name;
- entry-point group, name, and value;
- distribution name and installed version;
- plugin API version;
- manifest schema version;
- manifest hash;
- availability status;
- availability reason;
- compatibility report;
- dependency report;
- supported device families, models, and transports;
- static capability summary or reference;
- configuration-schema reference;
- AI-contract reference;
- deprecation state;
- source type;
- provider-probe duration;
- provider-probe timestamp;
- last validation error;
- runtime load state;
- loaded instance aliases;
- loaded instance count.

### 13.2 Availability statuses

Only these availability statuses are permitted:

- `AVAILABLE` — descriptor and compatibility validation passed;
- `DISABLED` — disabled by explicit configuration or policy;
- `INCOMPATIBLE` — plugin or runtime version requirements are not satisfied;
- `DEPENDENCY_MISSING` — one or more mandatory dependencies are unavailable;
- `CONFLICT` — duplicate or contradictory registrations exist;
- `BROKEN` — import, provider, manifest, or validation failed;
- `QUARANTINED` — blocked because of trust, integrity, security, or administrative policy;
- `DEPRECATED` — usable only under the declared support policy;
- `UNKNOWN` — discovery did not produce sufficient verified information; not loadable by default.

### 13.3 Runtime states

Availability and runtime state shall be separate.

Permitted runtime states:

- `NOT_LOADED`;
- `PROVIDER_LOADED`;
- `INSTANCE_CREATED`;
- `UNLOAD_IN_PROGRESS`;
- `UNLOADED`;
- `LOAD_FAILED`;
- `UNLOAD_FAILED`.

A device connection state such as `CONNECTED` is owned by the driver and shall not be represented as the plugin runtime state.

### 13.4 Registry refresh

Registry refresh shall:

- re-enumerate installed entry points;
- preserve active instance records;
- not unload active instances;
- identify added, removed, updated, and unchanged candidates;
- invalidate cached descriptor data for changed distributions;
- report that process restart is required when active code has changed;
- be deterministic for an unchanged environment.

### 13.5 Adapter registry record

Each adapter registry record shall contain at least:

- adapter ID;
- target plugin ID;
- target plugin-API version range;
- display name;
- entry-point group, name, and value;
- distribution name and installed version;
- adapter API version;
- manifest schema version;
- manifest hash;
- availability status;
- availability reason;
- target framework and framework-version requirement;
- `target_plugin_missing` flag;
- deprecation state;
- source type;
- provider-probe duration;
- provider-probe timestamp;
- last validation error;
- runtime load state;
- bound instance aliases.

Adapter records reuse the availability statuses of §13.2 and the runtime states of §13.3, applied to the adapter rather than to the driver plugin. Registry refresh for adapters follows the same rules as §13.4.

---

## 14. Compatibility Model

### 14.1 Plugin API version

The LPDS driver provider contract shall use a `MAJOR.MINOR` plugin API version.

Compatibility rules:

- different major versions are incompatible unless the host explicitly implements an adapter for the provider contract itself;
- a host shall declare the exact plugin API range it supports;
- a provider outside that range shall be marked `INCOMPATIBLE` before instantiation;
- compatibility shall not be inferred merely because import succeeds.

### 14.2 Runtime requirements

The plugin descriptor shall declare requirements for:

- Python;
- LPDS platform;
- mandatory third-party dependencies;
- optional transport or vendor-SDK dependencies;
- supported operating systems when constrained;
- native architecture when constrained.

### 14.3 Optional dependencies

Missing optional dependencies shall disable only the affected transport or feature where the driver can remain valid without them.

The capability and compatibility result shall show the reduced feature set. A plugin shall not claim a transport or capability whose required dependency is missing.

### 14.4 Unsupported hardware does not make the plugin incompatible

A valid installed plugin may be `AVAILABLE` when no physical device is attached. Hardware availability is a deployment state, not plugin compatibility.

### 14.5 Version selection

The LPDS platform should use one installed version of a distribution per Python environment. Where multiple environments or isolated providers expose more than one version of the same plugin ID, the resolver shall not merge them.

The selected version shall satisfy all declared constraints and shall be visible in the registry and evidence.

### 14.6 Adapter compatibility

The adapter provider contract shall use a `MAJOR.MINOR` adapter API version, subject to the same compatibility rules as §14.1 applied to the host's adapter-loading component.

In addition:

- an adapter shall declare its exact `target_plugin_id` and a plugin-API-version range it is compatible with;
- a host shall not bind an adapter to a driver instance created from a plugin API version outside that declared range; such an attempt shall fail with `AdapterCompatibilityError` (§25);
- the adapter's own framework-version requirement (for example a pytest or CLI-library version range) is evaluated independently of, and does not affect, the driver plugin's own compatibility state;
- an incompatible or unavailable adapter shall never be reported as a driver-plugin incompatibility; the driver plugin may remain fully `AVAILABLE` and usable directly.

---

## 15. Deterministic Plugin Resolution

### 15.1 Resolution inputs

The resolver may accept:

- explicit plugin ID;
- required driver/device family;
- exact model or model pattern;
- required transport;
- required capabilities;
- required simulation support;
- required multi-instance behavior;
- required compatibility range;
- preferred or prohibited vendor;
- deployed bench contract reference;
- configuration profile reference;
- allow-list and block-list policy.

### 15.2 Resolution order

The resolver shall apply this order:

1. exact plugin ID from an explicit request;
2. policy filtering and availability validation;
3. exact device-family and model compatibility;
4. required transport compatibility;
5. required capability compatibility;
6. required runtime and instance behavior;
7. explicit preference order from configuration;
8. version compatibility within the already selected plugin ID.

### 15.3 Ambiguity

When more than one candidate remains equally valid, resolution shall fail with `PluginResolutionAmbiguousError` and return the candidates and unmet tie-break information.

The resolver shall not select by:

- filesystem order;
- entry-point iteration order;
- package installation time;
- lexicographic order alone;
- fuzzy similarity alone;
- highest version across different plugin IDs;
- vendor preference not declared by the user, bench, or policy.

### 15.4 Capability confirmation

Static capability metadata may be used for pre-load filtering. After instance creation, the driver's runtime LPDS-013 capability result shall be treated as authoritative for the actual installed configuration and optional dependencies.

A mismatch shall fail validation or mark the instance degraded according to the applicable capability specification.

### 15.5 AI selection

An AI agent shall use an exact plugin ID it was explicitly given or that it resolved deterministically. It shall not invent a plugin ID or substitute a different driver merely because the substitute exposes a similar public API.

### 15.6 Adapter resolution

When a host needs to expose a driver instance to a specific framework, adapter resolution shall:

1. use an explicit adapter ID when supplied;
2. otherwise filter candidate adapters by exact `target_plugin_id` match to the already-resolved driver plugin ID;
3. filter by the automation framework the host is currently operating under;
4. filter by adapter availability and by plugin-API-range compatibility with the actual loaded driver instance's plugin API version;
5. fail with `AdapterResolutionAmbiguousError` (mirroring §15.3) when more than one adapter satisfies all filters, rather than choosing arbitrarily.

An adapter resolution failure shall not be treated as a driver resolution failure. A driver may be fully valid, connectable, and usable with zero adapters loaded, for example from a plain Python or pytest session with no automation framework installed at all.

---

## 16. Loading and Instantiation

### 16.1 Preconditions

A plugin may be loaded only when:

- its availability status permits loading;
- its plugin API is compatible;
- mandatory dependencies are present;
- no unresolved conflict exists;
- trust and policy checks pass;
- supplied configuration passes schema validation or is empty where permitted;
- requested alias is valid and unused;
- requested instance count complies with the manifest.

### 16.2 Load sequence

The loader shall:

1. obtain the current validated registry record;
2. re-check that installed distribution identity has not changed since validation;
3. load the provider;
4. verify the provider descriptor again in the host context;
5. validate effective configuration through LPDS-014 rules;
6. request one unconnected driver instance;
7. verify the returned object type and required metadata;
8. assign the explicit instance alias;
9. register the instance;
10. return an instance descriptor without connecting to hardware.

Loading a driver never requires selecting or loading an adapter. Adapter loading (§17) is always a separate, subsequent, optional step performed only when a specific framework binding is actually needed.

### 16.3 No silent simulation fallback

When a caller requests hardware mode and creation or connection fails, the loader or driver shall not silently create or connect a simulator. Simulation shall require an explicit configuration profile or explicit plugin/transport choice.

### 16.4 Instance aliases

Each loaded instance shall have a stable alias.

Alias rules:

- unique within the host process or test-session scope;
- explicit when more than one instance or plugin is loaded;
- not equal to a reserved manager namespace;
- preserved in evidence;
- used to avoid public-API name collisions when multiple driver instances are bound into the same framework session through one or more adapters.

### 16.5 Multi-instance behavior

When `multi_instance` is false, a second instance request shall fail visibly unless the caller explicitly requests the existing instance by alias.

When `multi_instance` is true, every instance shall own independent session state unless the driver documents shared vendor-SDK or process-global resources.

### 16.6 Thread safety

A plugin shall not be treated as thread-safe merely because it supports multiple instances. Thread-safety and concurrency rules shall be explicit in the descriptor, driver capability model, and AI contract.

---

## 17. Framework and Adapter Integration

### 17.1 Binding model

A loaded driver instance is plain Python and requires no adapter to be used directly from a Python script, a pytest test, a Jupyter notebook, or any other plain-Python context. LPDS-015 does not require every driver to be merged into one dynamic mega-object, and it does not require any driver to be bound to a framework at all.

Where a framework binding is needed, a shared LPDS plugin-and-adapter manager may expose management operations such as:

- `refresh_driver_registry`;
- `list_driver_plugins`;
- `get_driver_plugin_information`;
- `validate_driver_plugin`;
- `resolve_driver_plugin`;
- `load_driver_plugin`;
- `unload_driver_plugin`;
- `get_loaded_driver_plugins`;
- `export_driver_registry`;
- `list_adapters`;
- `resolve_adapter`;
- `bind_adapter`;
- `unbind_adapter`.

The names above are illustrative. A CLI, a pytest plugin, or a REST service may expose the equivalent operations under names natural to that framework.

### 17.2 Runtime binding

An adapter that binds a driver instance to its target framework shall use that framework's own supported mechanism for registering a callable surface (for example, a pytest fixture factory, a CLI command group, or a REST route table) or an equivalent reviewed API.

The bound object shall be registered under the requested alias, independent of any other adapter or driver instance active in the same process.

Illustrative workflow, plain Python, no automation framework required:

```python
from lpds_platform.plugins import PluginManager

manager = PluginManager()
manager.refresh_registry()
plugin = manager.resolve_plugin(plugin_id="keysight.n6700")
psu = manager.load_plugin(plugin.plugin_id, alias="psu", config=psu_config)
psu.connect(psu_resource)
try:
    psu.set_voltage(channel=1, volts=5.0)
finally:
    manager.unload_plugin("psu")
```

Example: CLI adapter

```text
$ psu-cli refresh-driver-registry
$ psu-cli resolve-driver-plugin --plugin-id keysight.n6700
$ psu-cli load-driver-plugin keysight.n6700 --alias PSU --config "$PSU_CONFIG"
$ psu-cli bind-adapter --adapter-id cli.keysight.n6700 --alias PSU
$ psu-cli psu connect "$PSU_RESOURCE"
$ psu-cli psu set-voltage --channel 1 --volts 5.0
$ psu-cli unload-driver-plugin PSU   # run on teardown
```

The exact manager API is governed by its own implementation specification. The required behavior in this section is normative; the CLI snippet illustrates one adapter among several, not the only supported integration.

### 17.3 Public API name collisions

The manager shall not silently merge identically named public API methods from multiple drivers or from multiple adapter bindings in the same framework session.

When multiple driver instances are bound through adapters into the same framework session:

- each shall use a distinct alias;
- the caller should use access qualified by alias, in the form natural to the target framework (for example `PSU.connect()` in Python or `psu-cli connect` as a CLI subcommand, and likewise `DMM.connect()` / `dmm-cli connect`);
- alias conflicts shall fail before binding;
- no adapter shall overwrite another binding's registration silently.

### 17.4 Static imports remain supported

LPDS-015 shall not prevent a caller from statically importing a driver class or a specific adapter class directly, bypassing dynamic discovery entirely. A script or test may continue to use:

```python
from keysight_n6700.driver import KeysightN6700Driver

psu = KeysightN6700Driver(config=psu_config)
psu.connect(psu_resource)
```

or, for a CLI adapter that does not need dynamic plugin management:

```python
from keysight_n6700_cli_adapter import CliAdapter

adapter = CliAdapter(config=psu_config)
```

Dynamic loading is an additional platform capability, not a mandatory replacement for explicit static imports of a driver or an adapter.

---

## 18. GUI and Application Integration

A generic GUI or application shall use the registry rather than a hard-coded list of driver or adapter classes.

The GUI should present:

- plugin display name;
- plugin ID;
- installed version;
- availability status and reason;
- supported device families and transports;
- compatibility state;
- simulation availability;
- deprecation state;
- documentation link;
- installed adapters that target this plugin ID and the frameworks they bind to;
- explicit validation and load action.

The GUI shall not:

- connect to hardware while merely opening the driver-selection page;
- hide broken, incompatible, or quarantined states, for either a plugin or an adapter;
- show unavailable transports as usable;
- auto-select an ambiguous plugin or adapter for a state-changing workflow;
- suppress manifest or dependency validation failures.

A GUI may remember a user's selected plugin ID and adapter ID in configuration under LPDS-014. It shall revalidate the selection at the next load.

---

## 19. Configuration Integration

### 19.1 Configuration ownership

LPDS-015 shall not redefine driver configuration fields. The plugin manifest shall reference the LPDS-014 configuration schema.

### 19.2 Validation before instance creation

The loader shall validate the plugin-selection and instance-creation portion of configuration before calling `create_driver()`.

Device connection settings may be validated by the driver at instance creation or explicit connection, according to LPDS-014 and the driver contract.

### 19.3 Configuration precedence

The effective configuration shall follow the LPDS-014 precedence model. The plugin manager shall not introduce hidden precedence rules.

### 19.4 Secrets

Secrets shall be passed through approved secret sources. They shall not be stored in registry exports, manifests, discovery logs, exception messages, or plugin- or adapter-selection history.

### 19.5 Effective configuration evidence

Evidence may include a redacted effective configuration hash and non-secret selection fields such as plugin ID, adapter ID, alias, transport profile, and simulator/hardware mode.

---

## 20. Capability Integration

The plugin manifest shall provide only the static capability information needed for discovery and filtering, or a reference to the authoritative LPDS-013 capability source.

After loading:

- the manager shall be able to request runtime driver capabilities;
- runtime capabilities shall reflect installed optional dependencies and active driver mode;
- simulation-only capabilities shall be distinguishable from hardware-qualified capabilities;
- unsupported capabilities shall remain explicit;
- generic applications shall query capabilities instead of branching on Python class names.

Capability metadata changes shall trigger plugin-manifest, AI-contract, documentation, compatibility, and release review as applicable. An adapter shall never introduce or hide capability information of its own; it may only surface what the wrapped driver already reports.

---

## 21. LPDS-017 Integration

### 21.1 AI Driver Contract

The plugin descriptor shall reference the driver's LPDS-017 `ai_contract.yaml`.

The plugin manager or AI planner shall verify:

- plugin ID and driver identity agreement;
- driver version agreement;
- public driver import agreement (`driver_import_path` and `driver_class`);
- capability-source agreement;
- contract-lock validity where available.

A stale or invalid AI contract shall not necessarily prevent manual diagnostic loading, but it shall prevent the plugin from being declared AI-planning ready.

An adapter has no AI contract of its own under this version of LPDS-015. When an AI planner needs a driver bound into a specific framework, it shall resolve the driver by plugin ID against the AI contract first, and only then resolve a compatible adapter (§15.6) for the framework it is operating under.

---

## 22. Hardware Discovery Extension

### 22.1 Optional extension

A provider may expose `discover_hardware()` only when the device transport permits a bounded and safe discovery operation.

### 22.2 Required search profile

The caller shall provide a profile defining applicable scope, such as:

- VISA backend and resource pattern;
- serial VID/PID and permitted ports;
- LAN subnet and permitted ports;
- USB VID/PID;
- vendor SDK enumeration mode;
- simulator registry.

The provider shall not scan unrestricted networks or all local interfaces without explicit approval.

### 22.3 Discovery result

Each result shall contain:

- plugin ID;
- transport type;
- resource identifier;
- confidence: `VERIFIED`, `PROBABLE`, or `UNVERIFIED`;
- identity response when safely obtained;
- model and serial number when available;
- firmware when available;
- discovery duration;
- warnings;
- evidence reference.

Sensitive or private resource details shall be redacted in shared reports according to deployment policy.

### 22.4 No implicit connection retention

A hardware-discovery operation shall close all temporary resources before returning. It shall not leave a normal driver session active.

---

## 23. Unload and Cleanup

### 23.1 Unload sequence

The manager shall:

1. locate the instance by alias;
2. unbind any adapters currently bound to that instance, in dependency order, before proceeding;
3. block new operations through that manager reference;
4. request driver cleanup using the canonical close-all, disconnect-all, or provider-defined lifecycle operation;
5. preserve cleanup failures;
6. remove any adapter binding registration where the integration API safely supports it;
7. remove the instance from the active registry;
8. update runtime state and evidence.

### 23.2 Safety responsibility

The plugin manager shall request cleanup, but the driver remains responsible for device-specific safe teardown and for reporting when safe state could not be confirmed. An adapter is never responsible for device-specific safe teardown; that responsibility cannot be delegated to it.

### 23.3 Idempotency

Unloading an already unloaded alias should be idempotent when no safety ambiguity exists. An unknown alias shall produce a clear validation failure. The same idempotency rule applies to unbinding an already-unbound adapter alias.

### 23.4 Module unloading

Python module unloading is not guaranteed. LPDS-015 does not require removal of provider, driver, or adapter modules from `sys.modules`.

### 23.5 Package update while loaded

Installing, removing, or updating a plugin or adapter distribution while an instance or binding is active shall require explicit unload/unbind and should require host-process restart before the new code is treated as production-valid.

In-process hot code reload shall be disabled by default.

---

## 24. Conflict Handling

### 24.1 Duplicate plugin ID

If two installed entry points advertise the same plugin ID, both shall be marked `CONFLICT` unless deployment policy explicitly pins one exact distribution and version.

### 24.2 Entry-point and manifest mismatch

A mismatch between entry-point name and manifest plugin ID shall mark the candidate `BROKEN`.

### 24.3 Entry-point provider mismatch

A mismatch between entry-point value and manifest provider shall mark the candidate `BROKEN`.

### 24.4 Distribution mismatch

A manifest claiming a different distribution name or version from installed metadata shall fail validation.

### 24.5 Capability conflict

A static descriptor claiming capabilities not present in the authoritative capability model shall fail validation.

### 24.6 Configuration conflict

A missing, invalid, or stale configuration schema reference shall fail plugin validation for configurable drivers.

### 24.7 Active alias conflict

A request to load a second instance using an existing alias shall fail before provider or driver construction. The same rule applies to binding a second adapter using an existing alias.

### 24.8 Duplicate adapter ID

If two installed entry points advertise the same adapter ID, both shall be marked `CONFLICT` unless deployment policy explicitly pins one exact distribution and version, mirroring §24.1.

### 24.9 Adapter target mismatch

An adapter manifest whose `target_plugin_id` does not follow the §7.1 identifier format shall mark the candidate `BROKEN`. An adapter whose `target_plugin_id` is well-formed but not currently installed shall be marked `AVAILABLE` with `target_plugin_missing` set, per §12.6, rather than `BROKEN`.

---

## 25. Error Model

LPDS-015 errors shall integrate with LPDS-007 and distinguish at least:

- `PluginDiscoveryError` — candidate enumeration failed;
- `PluginManifestError` — manifest missing, malformed, or schema-invalid;
- `PluginValidationError` — cross-artifact validation failed;
- `PluginCompatibilityError` — host or runtime requirement is not satisfied;
- `PluginDependencyError` — mandatory dependency is unavailable;
- `PluginConflictError` — duplicate or contradictory registration exists;
- `PluginResolutionError` — no matching plugin exists;
- `PluginResolutionAmbiguousError` — more than one equally valid plugin remains;
- `PluginLoadError` — provider import or load failed;
- `PluginInstantiationError` — driver creation failed;
- `PluginConfigurationError` — supplied configuration is invalid;
- `PluginSecurityError` — policy, integrity, or trust check failed;
- `PluginTimeoutError` — probe, validation, discovery, load, or unload exceeded its finite timeout;
- `PluginUnloadError` — cleanup or unload failed;
- `PluginNotFoundError` — requested plugin ID or alias does not exist;
- `PluginStateError` — operation is invalid for the current lifecycle state.

Each LPDS-015 error type listed above shall be implemented as a subclass of the applicable LPDS-007 `DriverError` category rather than as an independent root hierarchy — for example, `PluginConfigurationError` extends `DriverConfigurationError`, `PluginDependencyError` extends `DriverDependencyError`, `PluginTimeoutError` extends `DriverTransportError`, and `PluginStateError` extends `DriverStateError`. LPDS-007 remains the sole normative source for the root exception hierarchy and the mandatory error-message format; LPDS-015 defines only the additional plugin-specific and adapter-specific leaf categories and their required fields.

Every adapter-facing operation shall raise the adapter-scoped equivalent of the corresponding plugin error above, named by substituting `Adapter` for `Plugin` (for example `AdapterDiscoveryError`, `AdapterManifestError`, `AdapterResolutionAmbiguousError`, `AdapterLoadError`, `AdapterDependencyError`, `AdapterCompatibilityError`, `AdapterNotFoundError`), each extending the same LPDS-007 base category as its plugin counterpart. `AdapterNotFoundError` shall be distinguished from `PluginNotFoundError` in evidence so that a missing adapter is never mistaken for a missing driver.

Errors shall include:

- operation;
- plugin ID or adapter ID when known;
- distribution name and version when known;
- current status/state;
- actionable reason;
- underlying exception class where safe;
- evidence or diagnostic reference;
- no secrets;

and shall be formatted per LPDS-007 §11.

One plugin or adapter failure shall not be reported as a successful registry refresh.

---

## 26. Security and Trust Requirements

### 26.1 Trust boundary

Plugin and adapter distributions shall both be treated as executable dependencies, not passive data.

### 26.2 Allow-list and block-list

Production deployments should support:

- allowed plugin IDs and allowed adapter IDs;
- allowed distributions;
- allowed versions or version ranges;
- prohibited plugin IDs, adapter IDs, or versions;
- quarantined release hashes;
- approved source repositories or internal package indexes.

### 26.3 Integrity evidence

Where release integrity data is available, validation should compare the installed distribution or deployment artifact against:

- LPDS release manifest;
- SHA-256 checksums;
- SBOM;
- provenance or attestation;
- approved dependency lock.

A failed required integrity check shall result in `QUARANTINED` or `BROKEN`, not a warning-only load, for either a plugin or an adapter.

### 26.4 Isolated probe

Provider probing — for both plugin providers and adapter providers — shall use a separate process by default in production-capable platform implementations so that import failures, `sys.exit`, deadlocks, or crashes do not terminate the host.

### 26.5 Finite resource use

The probe shall enforce configurable limits for:

- wall-clock duration;
- output size;
- returned descriptor size;
- child-process count where enforceable;
- memory where the deployment supports limits.

### 26.6 No security claim from quarantine alone

Marking a plugin or adapter `QUARANTINED` prevents normal loading but does not remove malicious code from the environment. Package removal and host remediation remain deployment responsibilities.

### 26.7 Path loading

Arbitrary user-supplied Python paths shall not be loadable in production mode unless an approved development or laboratory policy explicitly permits them.

---

## 27. Performance and Caching

### 27.1 Discovery cache

The host may cache validated registry records using an environment fingerprint containing at least:

- Python executable identity;
- Python version;
- environment path;
- distribution name and version set;
- entry-point group records, for both `lpds.drivers` and `lpds.adapters`;
- plugin and adapter manifest hashes;
- host plugin API version and adapter API version;
- applicable allow/block policy hash.

### 27.2 Cache invalidation

The cache shall be invalidated when any fingerprint input changes or when the user requests a forced refresh.

### 27.3 Cache trust

Cached records shall not bypass current trust policy, distribution identity checks, or explicit quarantine rules.

### 27.4 Timeouts

All plugin and adapter operations shall have finite timeouts.

Recommended defaults:

- candidate enumeration (drivers or adapters): 10 seconds total;
- provider probe: 5 seconds per plugin or adapter;
- environment validation: 10 seconds per plugin or adapter;
- explicit hardware discovery: device-specific, finite, and shown to the caller;
- unload or unbind cleanup: driver- or adapter-specific, finite, and interruptible where practical.

Different values may be configured, but unbounded waits are prohibited.

### 27.5 Large environments

Discovery should support lazy provider probing so a GUI can first show D0/AD0 candidates and validate selected or visible candidates without blocking on every installed plugin or adapter.

A release-validation workflow shall still perform full validation of the driver — and of any adapter released alongside it.

---

## 28. Diagnostics and Evidence

### 28.1 Registry export

The host shall support a machine-readable export of both the plugin registry and the adapter registry, containing validated non-secret metadata.

Plugin and adapter validation evidence shall follow the LPDS-008 evidence envelope, manifest, and redaction rules; the `results/plugin_validation/<timestamp>/` layout in §28.3 is a plugin-manager-specific view and should be reachable from, or nested under, the LPDS-008 §11 canonical result root for the same run.

### 28.2 Required evidence

A plugin validation run shall record at least:

- timestamp;
- operating system;
- Python executable and version;
- LPDS platform version;
- entry-point group;
- discovered candidate count;
- validated plugin count;
- status counts;
- distribution names and versions;
- plugin IDs;
- manifest hashes;
- compatibility results;
- dependency results;
- conflicts;
- probe durations;
- failures and reasons;
- active instance aliases where applicable;
- redacted effective policy.

An adapter validation run shall additionally record: discovered adapter IDs, target plugin IDs, adapter manifest hashes, adapter compatibility results (including `target_plugin_missing` flags), adapter conflicts, adapter probe durations, and bound adapter aliases where applicable.

### 28.3 Recommended result layout

```text
results/plugin_validation/<timestamp>/
├── registry.json
├── discovery_candidates.json
├── compatibility_report.json
├── dependency_report.json
├── conflicts.json
├── probe_results.json
├── adapter_registry.json
├── adapter_discovery_candidates.json
├── adapter_compatibility_report.json
├── environment.json
├── plugin_validation_summary.md
└── plugin_manager.log
```

### 28.4 Trace correlation

Load, instance creation, hardware discovery, binding, unbinding, and unload records shall include a correlation ID so GUI logs, adapter-side logs (from any framework), driver diagnostics, and plugin/adapter evidence can be related.

### 28.5 Secret redaction

Registry and evidence exports shall redact credentials, tokens, private keys, and sensitive connection information according to LPDS logging requirements.

---

## 29. Required Tests

### 29.1 Driver-package tests

Each driver shall test:

- `lpds.drivers` entry point exists;
- entry-point name equals plugin ID;
- entry-point value resolves to the intended provider;
- provider imports without hardware access;
- driver module imports without hardware access;
- manifest exists and validates;
- provider descriptor equals manifest data;
- installed/distribution version consistency;
- provider API version compatibility;
- referenced capability, configuration, AI-contract, and documentation resources exist;
- `get_descriptor()` returns JSON-serializable data;
- `validate_environment()` reports mandatory and optional dependencies correctly;
- `create_driver()` returns the canonical unconnected driver type;
- no silent simulation fallback occurs;
- multiple instances follow the declared policy;
- cleanup is deterministic and finite;
- provider and driver import do not enumerate or open hardware;
- broken optional dependencies reduce only the affected capabilities;
- manifest drift causes test failure.

### 29.2 Platform-manager tests

The LPDS platform plugin-and-adapter manager shall test:

- empty environment;
- one valid plugin;
- multiple valid plugins;
- duplicate plugin ID;
- malformed entry point;
- missing distribution metadata;
- provider import exception;
- provider timeout;
- provider process crash;
- malformed descriptor;
- manifest mismatch;
- unsupported plugin API major version;
- incompatible Python version;
- missing mandatory dependency;
- missing optional dependency;
- disabled plugin;
- quarantined plugin;
- explicit resolution;
- capability/model/transport resolution;
- ambiguous resolution;
- alias conflict;
- single-instance enforcement;
- multi-instance behavior;
- load failure isolation;
- unload cleanup failure;
- cache invalidation;
- refresh after install/remove/update simulation;
- redaction of secrets;
- deterministic registry export;
- adapter discovery independent of whether its target driver is installed;
- adapter-to-driver binding against a live driver instance;
- adapter unbinding and its effect on subsequent unload;
- `target_plugin_missing` reporting;
- ambiguous adapter resolution.

### 29.3 Adapter conformance tests

Using deterministic fake plugins and a deterministic fake adapter, conformance tests shall verify:

- registry refresh;
- plugin listing;
- explicit plugin resolution;
- adapter discovery and resolution;
- adapter binding to a loaded driver instance;
- access qualified by alias remains distinct across two adapter bindings with common method names;
- unbind behavior;
- clear failure for an unavailable or ambiguous plugin or adapter.

A framework-specific acceptance suite (for example, a pytest suite exercising the same behavior through a pytest fixture adapter) is recommended for any released adapter, but its detailed design is governed by that adapter's own test suite, not by this document.

### 29.4 Import-safety test environment

Import-safety tests should block or instrument common hardware-access mechanisms, including applicable socket, serial, VISA, USB, vendor-SDK, and subprocess calls, and fail when provider, driver, or adapter import attempts prohibited access.

### 29.5 Real-driver and real-adapter validation

A released driver shall pass plugin discovery and load validation from its built wheel in a clean environment. Validation against only the source checkout is insufficient. A released adapter shall similarly pass adapter discovery and binding validation from its own built wheel in a clean environment.

---

## 30. Checklist

**Discovery**
- [ ] The distribution advertises its `lpds.drivers` (or `lpds.adapters`) entry point correctly, and the entry-point name/value agree with the manifest's plugin ID/provider path.
- [ ] Provider and driver imports perform no hardware or network access; probing is time-bounded.
- [ ] The manifest validates against its schema, and its identity fields agree with installed distribution metadata.

**Resolution and loading**
- [ ] Compatibility (plugin API, Python, dependencies) is evaluated before instance creation; a plugin with unmet requirements doesn't get silently selected.
- [ ] Explicit resolution by plugin ID works; an ambiguous resolution fails visibly rather than picking arbitrarily (e.g. by filesystem order).
- [ ] `create_driver()` returns an unconnected instance; a requested hardware mode never silently falls back to simulation.
- [ ] One broken plugin doesn't prevent other valid plugins from loading.

**Adapters**
- [ ] An adapter binds to an already-created driver instance — it never creates or connects the driver itself.
- [ ] An adapter can be discovered, validated, bound, and unbound independently of the driver's own lifecycle.
- [ ] The adapter's `target_plugin_id` actually matches the driver it binds to.

**Cleanup**
- [ ] Unload/unbind is finite and reports incomplete cleanup rather than hiding it.
- [ ] Manifests, registry exports, and logs contain no secrets.

---

## 31. Change Control

Whenever any of the following changes, the same driver revision shall update and validate all affected artifacts:

- plugin ID;
- entry-point name or value;
- provider class;
- plugin API version;
- manifest schema version;
- distribution name;
- driver import path or class;
- supported models or transports;
- capability reference or static summary;
- configuration-schema reference;
- AI-contract reference;
- multi-instance or thread-safety declaration;
- hardware-discovery support;
- dependency or compatibility requirements;
- deprecation state;
- load or unload behavior;
- simulation policy;
- security or trust policy.

Whenever any of the following changes, the same adapter revision shall update and validate all affected artifacts:

- adapter ID;
- entry-point name or value;
- adapter provider class;
- adapter API version;
- manifest schema version;
- distribution name;
- adapter import path or class;
- `target_plugin_id` or target plugin-API range;
- framework or framework-version requirement;
- deprecation state;
- bind or unbind behavior.

A plugin ID change is a breaking integration change and requires a migration path, compatibility review, and a history entry. An adapter ID or `target_plugin_id` change is similarly a breaking integration change for any host configuration that names it explicitly.

A provider or entry-point change without LPDS-015 test and manifest updates shall fail release validation.

---

## 32. Fitting This Into the Implementation Lifecycle

Mapped onto LPDS-020's phases: the plugin ID and a manifest skeleton with a no-hardware-import proof are early-phase (architecture/skeleton) work; the driver factory and registry integration tests land in the core-implementation phase; capability-based resolution and optional hardware discovery are naturally later, extended-feature work; and a clean-install test of the packaged entry point belongs in the tests/release phases, alongside the same review this document's checklist (§30) already covers. An adapter, if one is planned, follows this same shape one step behind — its `target_plugin_id` and manifest skeleton in an early phase, its binding/unbinding tests before release.

---

---

## 33. Goal

Provide a deterministic and production-oriented mechanism by which LPDS applications, automation frameworks (through their adapters), GUIs, and AI planners can discover installed drivers and adapters, validate what they are, select the correct implementation, load it without hidden hardware activity, and preserve safety, compatibility, isolation, and traceable evidence throughout the plugin and adapter lifecycle.

---

## Appendix A — Platform Provider Interface Example

```python
from __future__ import annotations

from typing import Any, ClassVar


class KeysightN6700Plugin:
    """LPDS plugin provider. Importing this class must not access hardware."""

    PLUGIN_ID: ClassVar[str] = "keysight.n6700"

    @classmethod
    def get_descriptor(cls) -> dict[str, Any]:
        from .manifest import load_plugin_manifest

        descriptor = load_plugin_manifest()
        if descriptor["plugin_id"] != cls.PLUGIN_ID:
            raise ValueError("Plugin ID does not match provider identity")
        return descriptor

    @classmethod
    def validate_environment(cls) -> dict[str, Any]:
        return {
            "status": "PASS",
            "checks": [
                {"name": "python", "status": "PASS"},
                {"name": "visa", "status": "WARNING", "optional": True},
            ],
        }

    @classmethod
    def create_driver(cls, *, config: dict[str, Any] | None = None) -> object:
        from .driver import KeysightN6700Driver

        return KeysightN6700Driver(config=config)
```

This appendix is illustrative. The approved platform package shall provide the shared types, schemas, validators, exceptions, and lifecycle utilities.

---

## Appendix B — Registry Record Example

```json
{
  "plugin_id": "keysight.n6700",
  "display_name": "Keysight N6700 Power System Driver",
  "distribution": {
    "name": "keysight-n6700",
    "version": "26.3"
  },
  "entry_point": {
    "group": "lpds.drivers",
    "name": "keysight.n6700",
    "value": "keysight_n6700.plugin:KeysightN6700Plugin"
  },
  "availability": {
    "status": "AVAILABLE",
    "reason": null
  },
  "runtime_state": "NOT_LOADED",
  "plugin_api_version": "1.0",
  "manifest_hash": "sha256:<digest>",
  "supported_transports": ["visa", "tcpip", "usb", "simulator"],
  "simulation_supported": true,
  "multi_instance": true,
  "loaded_aliases": [],
  "validation": {
    "probe_duration_ms": 84,
    "validated_at": "2026-07-26T12:00:00Z"
  }
}
```

---

## Appendix C — Technical Basis

This specification uses Python distribution entry points as the canonical installed-plugin and installed-adapter advertisement mechanism, and `importlib.metadata` as the standard runtime discovery API. It supports any automation framework's own normal model of importing bindings by module and class, through an adapter, and permits runtime driver import for explicitly selected plugins independent of any particular framework.

Reference specifications and documentation:

- Python Packaging User Guide — Entry points specification: https://packaging.python.org/en/latest/specifications/entry-points/
- Python Standard Library — `importlib.metadata`: https://docs.python.org/3/library/importlib.metadata.html
- pytest documentation — fixtures (as one example of a framework an adapter may target): https://docs.pytest.org/en/stable/explanation/fixtures.html

---

## Appendix D — Initial Version 1.0 Decisions

1. `lpds.drivers` is the sole canonical installed-driver entry-point group; `lpds.adapters` is the parallel canonical installed-adapter entry-point group.
2. Entry-point enumeration is separated from provider import, for both groups.
3. Provider probing is isolated and time-bounded, for both plugin providers and adapter providers.
4. Provider and driver imports shall not access hardware.
5. Driver creation shall produce an unconnected instance.
6. Hardware discovery is optional, explicit, scoped, read-only, and separate from plugin discovery.
7. Exact plugin IDs, exact adapter IDs, and explicit aliases are preferred for adapter and bench integration.
8. Ambiguous resolution fails rather than choosing by discovery order, for both plugin and adapter resolution.
9. Dynamic loading does not replace normal static Python imports of a driver or an adapter.
10. In-process hot code reload is not required and is disabled by default.
11. Drivers and adapters are discovered, versioned, and loaded through independent, parallel entry-point groups, so that a driver package never needs to depend on, import, or know about any specific automation framework.

---

## Appendix E — Adapter Provider Interface Example

```python
from __future__ import annotations

from typing import Any, ClassVar


class KeysightN6700CliAdapterPlugin:
    """LPDS adapter provider. Importing this class must not access hardware
    and must not require a driver instance to already be connected."""

    ADAPTER_ID: ClassVar[str] = "cli.keysight.n6700"
    TARGET_PLUGIN_ID: ClassVar[str] = "keysight.n6700"

    @classmethod
    def get_descriptor(cls) -> dict[str, Any]:
        from .manifest import load_adapter_manifest

        descriptor = load_adapter_manifest()
        if descriptor["adapter_id"] != cls.ADAPTER_ID:
            raise ValueError("Adapter ID does not match provider identity")
        if descriptor["target_plugin_id"] != cls.TARGET_PLUGIN_ID:
            raise ValueError("Target plugin ID does not match provider identity")
        return descriptor

    @classmethod
    def validate_environment(cls) -> dict[str, Any]:
        return {
            "status": "PASS",
            "checks": [
                {"name": "python", "status": "PASS"},
                {"name": "cli", "status": "PASS"},
            ],
        }

    @classmethod
    def bind(cls, driver: object, *, alias: str | None = None) -> object:
        from .adapter import KeysightN6700CliLibrary

        return KeysightN6700CliLibrary(driver=driver, alias=alias)
```

This appendix is illustrative. The approved platform package shall provide the shared types, schemas, validators, exceptions, and lifecycle utilities for adapters just as it does for driver plugins (Appendix A).

---

## Appendix F — Adapter Manifest Example

```json
{
  "schema_version": "1.0",
  "adapter_api_version": "1.0",
  "adapter_id": "cli.keysight.n6700",
  "target_plugin_id": "keysight.n6700",
  "target_plugin_api_version": ">=1,<2",
  "adapter_name": "keysight_n6700_cli_adapter",
  "display_name": "Keysight N6700 CLI Adapter",
  "description": "CLI adapter wrapping the keysight.n6700 LPDS driver.",
  "distribution_name": "keysight-n6700-cli-adapter",
  "distribution_version": "26.3",
  "provider": "keysight_n6700_cli_adapter.plugin:KeysightN6700CliAdapterPlugin",
  "adapter_import_path": "keysight_n6700_cli_adapter.adapter",
  "adapter_class": "KeysightN6700CliLibrary",
  "framework": "cli",
  "framework_version": ">=1,<2",
  "minimum_python": ">=3.11",
  "lpds_platform_version": ">=1,<2",
  "deprecation": {
    "deprecated": false,
    "replacement_adapter_id": null,
    "removal_version": null
  },
  "manifest_hash_algorithm": "sha256"
}
```

---

## Appendix G — Combined `pyproject.toml` Entry-Points Example

```toml
# Driver distribution: keysight-n6700
[project.entry-points."lpds.drivers"]
"keysight.n6700" = "keysight_n6700.plugin:KeysightN6700Plugin"
```

```toml
# Separately released adapter distribution: keysight-n6700-cli-adapter
[project.entry-points."lpds.adapters"]
"cli.keysight.n6700" = "keysight_n6700_cli_adapter.plugin:KeysightN6700CliAdapterPlugin"
```

A driver distribution and its adapter distributions are independently versioned, independently installable, and independently releasable. Installing the driver alone never installs, imports, or requires any automation framework.
