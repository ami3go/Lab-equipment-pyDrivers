# LPDS-017 — AI Driver Contract Specification

**Version:** 3.0 (Draft)
**Document ID:** LPDS-017
**Status:** Draft project requirement
**Applies to:** all discoverable LPDS driver packages, AI planners and code-generation agents, LPDS-015 plugin managers, LPDS-018 bench managers, and any tool that consumes `ai_contract.yaml`

---

## 1. Purpose

This specification defines the canonical, machine-readable AI contract that describes one Python instrument driver so that an AI agent can understand, safely select, and generate tests for that driver without reading its source code.

The contract describes the driver's public Python API — its methods, signatures, states, and effects — completely independently of any test-automation framework. An agent that has only `ai_contract.yaml` can generate a plain pytest-based test directly against the driver's public API. If the driver also ships an adapter (RF, CLI, REST, …) whose own LPDS-015 entry-points manifest is present, the same agent may additionally generate tests in that adapter's framework by translating capability entries through the adapter's published mapping — but the contract itself is adapter-independent by design: it never encodes Robot Framework syntax, or the syntax of any other framework, at any point.

LPDS-017 is the sole normative source for the structure and required fields of `ai_contract.yaml` and its integrity companion `ai_contract.lock`. Other specifications (LPDS-013, LPDS-014, LPDS-015, LPDS-018) reference these files but shall not redefine their schema.

## 2. Scope Boundary

### 2.1 In scope

- the required files, sections, and fields of one driver's AI contract;
- the mapping between contract fields and the canonical vocabularies owned by other LPDS specifications;
- contract identity, versioning, and integrity (`ai_contract.lock`);
- conformance rules for a valid contract.

### 2.2 Out of scope

LPDS-017 does not define:

- the capability taxonomy itself (owned by LPDS-013);
- the exception hierarchy or error-message format (owned by LPDS-007);
- the connection/session state enum (owned by LPDS-003);
- device configuration schema (owned by LPDS-014);
- plugin discovery, loading, the plugin manifest, or adapter entry-points groups (owned by LPDS-015);
- bench topology or multi-driver system contracts (owned by LPDS-018);
- protocol-level conformance vectors (owned by LPDS-019).

LPDS-017 references these authorities rather than duplicating them; a field in `ai_contract.yaml` that expresses a value governed by another LPDS specification shall use that specification's canonical vocabulary and shall fail contract validation if it diverges.

## 3. Normative Terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement; deviations require documented justification;
- **may** — permitted implementation choice;
- **AI contract** — the `ai_contract.yaml` document described by this specification;
- **contract lock** — the `ai_contract.lock` integrity artifact described in §6;
- **capability entry** — one contract record describing a single public Python method, per §8;
- **oracle** — a machine-checkable pass/fail condition used to verify a capability's postcondition.

## 4. Normative References

- LPDS-001 — Platform Requirements
- LPDS-002 — Mandatory Public API Standard
- LPDS-003 — BaseInstrument: Common Base Class Design
- LPDS-005 — Driver Package Specification
- LPDS-007 — Error and Exception Standard
- LPDS-013 — Capability Model
- LPDS-014 — Driver Configuration Model Specification
- LPDS-015 — Plugin and Adapter Architecture

## 5. Required Files

```text
ai/
├── ai_contract.yaml
└── ai_contract.lock
```

Both files shall be packaged inside the driver's LPDS-005 repository tree and shall be reachable at release time either as a `repository_path` or, when runtime access is required, as a `package_resource` per LPDS-015 §9.2.1.

## 6. Contract Identity and Integrity

### 6.1 Identity fields

`ai_contract.yaml` shall declare, at its root, an `identity` section containing at least:

- `contract_schema_version` — the LPDS-017 schema version this file conforms to;
- `plugin_id` — shall equal the LPDS-015 plugin manifest `plugin_id`;
- `driver_name` — shall equal the LPDS-015 plugin manifest `driver_name`;
- `distribution_name` — shall equal the LPDS-015 plugin manifest `distribution_name`;
- `distribution_version` — shall equal the installed distribution version;
- `driver_import_path` — shall equal the LPDS-015 plugin manifest `driver_import_path`;
- `driver_class` — shall equal the LPDS-015 plugin manifest `driver_class`;
- `supported_models` — shall be consistent with the LPDS-015 plugin manifest.

No identity field shall name or imply a specific test-automation framework; the driver's own plugin identity is framework-independent, and any adapter that additionally wraps the driver carries its own, separate identity in the LPDS-015 adapter entry-points group, outside this contract.

A mismatch between any identity field and its corresponding LPDS-015 manifest field shall fail plugin validation per LPDS-015 §21.1.

### 6.2 `ai_contract.lock`

`ai_contract.lock` shall contain:

- `contract_sha256` — the SHA-256 digest of the canonical `ai_contract.yaml` content;
- `generated_at` — an ISO-8601 timestamp;
- `generator` — the tool and version that produced the lock file.

A driver release shall fail validation when `ai_contract.lock` does not match the packaged `ai_contract.yaml`. This is the "contract-lock validity" check referenced by LPDS-015 §21.1.

## 7. Mandatory Sections

`ai_contract.yaml` shall contain the following top-level sections:

1. **Identity** — per §6.1;
2. **Mental model** — a short natural-language description of what the instrument does and how an agent should reason about it;
3. **State machine** — per §9;
4. **Resources consumed/provided** — physical or logical resources (channels, ports, exclusive locks) the driver manages;
5. **Dependencies** — required and optional runtime dependencies, consistent with the LPDS-015 manifest's dependency declarations;
6. **Capabilities** — one entry per mandatory public Python method, per §8;
7. **Error catalogue** — per §10;
8. **Safety rules** — natural-language and machine-checkable constraints an agent shall respect (e.g., voltage limits, interlocks);
9. **Verification objectives** — pass/fail oracles used to confirm a generated test achieved its intent;
10. **Setup/teardown contract** — required preconditions and cleanup obligations for generated tests;
11. **Limitations** — known gaps, unsupported models, or simulation-only behavior;
12. **Planning hints** — ordering constraints, timing guidance, and preferred method call sequences;
13. **UNKNOWN handling** — how the driver reports and how an agent should treat values it cannot determine (see §11);
14. **Conformance rules** — per §12.

A contract missing any mandatory section shall fail LPDS-017 conformance.

## 8. Capability Entries

### 8.1 Required fields

Each capability entry shall correspond to exactly one mandatory public Python method defined by LPDS-002 or LPDS-013, and shall declare:

- `method` — the exact public Python method name, as defined on the driver class;
- `capability_id` — the LPDS-013 §10.1 hierarchical identifier (`<domain>.<object>.<operation>`) this method implements, when one applies;
- `signature` — the Python signature: argument names, types, defaults, and return type;
- `purpose` — a short natural-language description;
- `inputs` / `outputs` — machine-readable argument and return descriptions;
- `preconditions` — required driver state(s) using the LPDS-003 §13.1 canonical state enum;
- `postconditions` — resulting state(s) and observable effects;
- `side_effects` — any effect beyond the return value (e.g., device output enabled);
- `risk_level` — one of the LPDS-002 §16.1 canonical values (`none`, `low`, `medium`, `high`, `critical`);
- `timing` — expected typical execution duration;
- `stabilization_delay` — settling time an agent shall wait before relying on the effect, when applicable;
- `retry_policy` — whether and how a failed call may be retried;
- `errors` — the subset of the §10 error catalogue this method may raise;
- `exclusive_resources` — resources this method locks for the duration of the call.

A capability entry describes the driver's Python API only. It shall not reference keywords, fixtures, CLI commands, endpoints, or any other adapter-side binding; those bindings, where they exist, are published separately in the corresponding adapter's own manifest (LPDS-015), which an agent may consult in addition to this contract when generating tests in that adapter's framework.

### 8.2 Consistency with LPDS-002 and LPDS-013

A capability entry's `risk_level` shall use LPDS-002 §16.1's lowercase scale. Where the driver also exposes a richer LPDS-013 capability record for the same operation, `capability_id` shall match the LPDS-013 `get_capability_model()` result exactly; a mismatch shall fail LPDS-013 change-control review.

## 9. State Machine

The `state_machine` section shall reference the LPDS-003 §13.1 canonical connection/session state enum by name rather than defining a competing set of state names. It may add driver-specific sub-states only as documented extensions of a canonical state, and shall label them as such.

## 10. Error Catalogue

Each entry in the `error_catalogue` section shall declare:

- `error_code` — an `LPDS-<DOMAIN>-<NNN>` code per LPDS-007 §8–9;
- `exception_class` — the concrete LPDS-007-aligned exception (e.g., `DriverTimeoutError`);
- `condition` — when this error is raised;
- `retryable` — `yes` or `no`;
- `recovery` — the recommended recovery action or `none`.

These fields shall be sufficient to reconstruct an LPDS-007 §11 formatted message; the error catalogue shall not introduce a parallel message format.

## 11. UNKNOWN Handling

The contract shall state, for each capability where applicable, whether an indeterminate result is reported as an explicit `UNKNOWN` value, a `WARNING`-level diagnostic, or a raised exception. An AI agent shall treat `UNKNOWN` as "not verified" rather than as a pass or a fail, and shall not silently substitute a default value in place of an `UNKNOWN` result during test generation.

## 12. Conformance Rules

An `ai_contract.yaml` is LPDS-017 conformant only when:

1. all mandatory sections in §7 are present;
2. identity fields match the LPDS-015 plugin manifest exactly;
3. every mandatory LPDS-002/LPDS-013 method has exactly one capability entry;
4. every `risk_level` uses the LPDS-002 §16.1 scale;
5. every `capability_id` present matches the driver's LPDS-013 capability model;
6. every state name in `state_machine` and in capability pre/postconditions is a valid LPDS-003 §13.1 state or a documented sub-state of one;
7. every error catalogue entry maps to an LPDS-007-aligned exception and a valid `LPDS-<DOMAIN>-<NNN>` code;
8. `ai_contract.lock` validates against the packaged `ai_contract.yaml`;
9. no capability, safety rule, or oracle references hardware behavior that contradicts the driver's LPDS-013 capability model or LPDS-014 configuration schema;
10. no field names or otherwise describes a test-automation-framework-specific binding — framework bindings belong exclusively to an adapter's own LPDS-015 manifest, never to this contract.

A contract failing any rule above shall not be declared AI-planning ready, per LPDS-015 §21.1.

## 13. Review Checklist

1. Are all mandatory sections present?
2. Do identity fields match the LPDS-015 manifest?
3. Does every mandatory method have exactly one capability entry?
4. Do risk levels use the LPDS-002 canonical scale?
5. Do capability IDs match the LPDS-013 capability model?
6. Do state references match LPDS-003's canonical enum?
7. Does the error catalogue map cleanly to LPDS-007 exception classes and error codes?
8. Is `ai_contract.lock` valid against the packaged contract?
9. Are safety rules and oracles consistent with the capability model and configuration schema?
10. Are limitations and UNKNOWN-handling behavior documented?
11. Does the contract remain free of any test-automation-framework-specific syntax or bindings?

## 14. Change Control

Whenever a driver's public methods, capability model, exception usage, state model, or configuration schema changes, `ai_contract.yaml` shall be updated and `ai_contract.lock` regenerated in the same revision. A contract left out of sync with the driver's actual behavior shall fail release validation.

## 15. Goal

Provide a single, schema-defined, machine-verifiable description of one driver's Python public API — reusing the canonical vocabularies owned by LPDS-002, LPDS-003, LPDS-007, and LPDS-013 — so that an AI agent can plan, select, and generate correct tests directly against the driver in plain pytest, or, where an adapter's own manifest is also present, in that adapter's framework, without reading source code or guessing at field meanings.
