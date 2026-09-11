# LPDS-014 — Driver Configuration Model Specification

**Document ID:** LPDS-014
**Version:** 1.1
**Status:** Draft Project Standard (Normative)
**Applies to:** All LPDS Python instrument driver packages

---

## 1. Purpose

This specification defines a common, lightweight configuration model for LPDS drivers: how a driver describes its configurable settings, validates them, and combines defaults with overrides — so that configuration is predictable, inspectable, and free of undocumented local-file magic, without requiring more machinery than a typical driver actually needs.

A driver's configuration is usually small: a resource string, a timeout, maybe a couple of safety limits. This document scales down accordingly — the full JSON Schema + precedence model is useful even for a small config, but things like cross-process file locking, schema-migration frameworks, and cryptographic fingerprinting are things to reach for only if a driver's configuration genuinely grows complex enough to need them (§17).

---

## 2. Scope Boundary

### 2.1 In scope

LPDS-014 covers host-side driver configuration: a JSON configuration document and schema, package defaults, precedence between defaults/file/environment/constructor arguments, secret references, and the standard public Python methods for getting, validating, and setting configuration.

### 2.2 Out of scope

LPDS-014 does not define:

- vendor protocol commands used to configure a physical device;
- device calibration data;
- measurement or test-result storage;
- credential/secret storage mechanisms themselves (only how a driver references them);
- general application preferences unrelated to driver operation.

A setting that changes physical-device non-volatile memory remains a device-facing operation: it's declared as a normal capability (LPDS-017), safety-classified, and tested through LPDS-019 like any other device-facing method. LPDS-014 only governs the host-side representation of the *intent* to apply that setting.

---

## 3. Normative Terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement;
- **may** — permitted implementation choice;
- **configuration document** — a JSON object representing one driver's settings;
- **schema** — the JSON Schema defining valid configuration structure;
- **effective configuration** — the fully resolved configuration after defaults and overrides are applied;
- **secret reference** — an indirect reference to a secret stored outside the configuration document (e.g. an environment variable name).

---

## 4. Design Principles

**JSON is the interchange format.** Every driver supports JSON configuration import/export without optional dependencies. YAML, TOML, or GUI forms may be used as authoring conveniences, but convert to this JSON model before validation.

**Validate before applying.** Parse, validate, and normalize a configuration completely before changing any active state. A validation failure changes nothing.

**Persistence is explicit.** Changing a runtime value doesn't automatically save it. Saving happens only through an explicit save call.

**Safe defaults.** Package defaults contain no credentials, no personal paths or ports, keep outputs/relays disabled, and use finite timeouts.

**No silent fallback.** If an explicitly requested config file is invalid, fail — don't silently substitute defaults or a different profile.

**No plaintext secrets.** Ever, in the document itself, in exports, or in logs.

---

## 5. Configuration Domains

| Domain | Owner | Treatment |
|---|---|---|
| Driver package defaults | Driver package | Read-only baseline |
| Host transport settings (resource string, timeout, retry) | Driver instance | Importable, exportable, persistable |
| Driver logging settings | Driver instance | Importable, exportable, persistable |
| Simulation/replay settings | Driver instance | Explicit, never silently enabled |
| Driver safety limits | Driver, or an external test-bench config | Elevated validation, no unsafe default |
| Physical-device volatile/non-volatile state | Physical device | Applied only through declared capabilities, never merely by loading a profile |
| Credentials/secrets | External secret provider (env var, OS keychain) | Referenced, never stored as plaintext |
| Test variables, acceptance limits | Test suite | Not driver configuration |

A field doesn't belong in driver configuration just because it's convenient for one test suite.

---

## 6. Package Artifacts

A driver provides, under `src/<driver_name>/resources/configuration/` and mirrored at the project root under `config/`:

```text
config/
├── schema.json      # JSON Schema for the configuration document
├── default.json     # safe, validated package default
└── example.json      # demonstrates the configurable sections with placeholder values
```

`default.json` validates against `schema.json`. `example.json` shows what a filled-in profile looks like, using safe placeholder values (no real credentials or local paths).

A `schema.lock` (digest of the schema, to detect drift) is useful once a driver has external tooling depending on schema stability — not required for a typical driver.

---

## 7. Canonical Configuration Document

```json
{
  "lpds014_version": "1.1",
  "schema_version": "1.0.0",
  "driver": {
    "driver_name": "<driver_name>"
  },
  "settings": {
    "transport": {},
    "timeouts": {},
    "retry": {},
    "logging": {},
    "simulation": {},
    "safety": {},
    "device": {}
  }
}
```

`settings` is the only normal location for behavioral configuration. Driver-specific fields go under `settings.device`, not as new top-level keys. A driver may omit a standard section its schema marks unsupported.

Fields shall be JSON primitives with explicit units where physical (seconds for timeouts, volts for voltage, etc.) — not strings requiring the caller to know an implicit unit convention.

---

## 8. JSON Schema

Use JSON Schema Draft 2020-12. The schema declares `$id`, `title`, `type`, required fields, and `additionalProperties: false` for `settings` and its subsections — unknown keys should fail validation rather than being silently ignored, since a silently-ignored typo in a config key is a common source of "why isn't this working" bugs.

Two custom annotations are worth using consistently:

| Annotation | Values | Purpose |
|---|---|---|
| `x-lpds-unit` | String | Physical or time unit |
| `x-lpds-sensitive` | Boolean | Value should be redacted in logs/exports |
| `x-lpds-risk-level` | `none`/`low`/`medium`/`high`/`critical` | Safety classification (same scale as LPDS-002 §16.1) |

---

## 9. Precedence

Effective configuration resolves from lowest to highest precedence:

```text
1. package default
2. a config file, if one was loaded
3. approved environment-variable overrides
4. constructor arguments
5. explicit method-call arguments, for the current call only
```

Only environment variables the schema explicitly declares may override configuration — don't auto-map every `DRIVERNAME_*` env var without validating each one against the schema. A call-time argument (like `timeout_s` passed to one method call) is never itself persisted.

---

## 10. Merge Semantics

Loading a config file can either `REPLACE` (package defaults + the loaded document, wholesale) or `MERGE` (overlay the loaded document's fields onto the current effective configuration). Objects deep-merge by key; arrays replace wholesale by default (don't try to "merge" a list of channel configs by position — it's rarely what anyone wants). A `VALIDATE_ONLY` mode runs the same parse/validate/normalize pipeline without applying or persisting anything — useful for a "check this config before I use it" step.

---

## 11. Import and Export

Import: read the source (file path, JSON string, or dict) → parse → validate against schema → run any cross-field checks (e.g. "safety.max_voltage must not exceed the device's rated maximum") → only then apply. Nothing before the final validated step should mutate active state.

Export: return the effective configuration as a dict, and optionally write it to a file. Secrets are never included in plaintext — export them as a reference instead:

```json
{"secret_ref": "ENV:DRIVER_DEVICE_PASSWORD"}
```

Export followed by import on a compatible driver should reproduce the same semantic configuration.

---

## 12. Where Config Files Live

If a driver persists named profiles, a reasonable default location is the OS user-config directory:

```text
Windows: %APPDATA%\lpds\<driver_name>\
Linux:   ${XDG_CONFIG_HOME:-~/.config}/lpds/<driver_name>/
```

Don't write profiles into the installed package directory, the current working directory by default, or a temp directory as long-term storage.

A basic atomic-write (write to a temp file, then rename over the destination) is good practice and cheap to implement. Cross-process locking, backup retention policies, and a `rejected/` quarantine folder for corrupt profiles are things to add if a driver's configuration is actually being edited concurrently by multiple processes — most aren't.

---

## 13. Secrets

Plaintext credentials, tokens, and private keys are never stored in a driver profile. Use a secret reference instead:

```json
{"secret_ref": "ENV:DRIVER_DEVICE_PASSWORD"}
```

Environment-variable references are the baseline; an OS credential-store reference is a reasonable addition if a project already uses one. Resolve a secret only when actually needed for an operation, keep it in memory as briefly as possible, and never let it leak into logs, exceptions, diagnostics, or exports — including inside a validation error message that happens to echo back a rejected value.

---

## 14. Safety

A setting that affects energy, motion, temperature, or device persistence should carry the `x-lpds-risk-level` annotation (§8). A driver shouldn't infer bench or DUT safety limits from the connected instrument model alone — package defaults may state conservative instrument-level limits, but a deployment's actual safety limits are the deployment's responsibility to configure.

Loading a profile at driver construction never connects to hardware or energizes outputs by itself — that only happens when the caller explicitly calls `connect()` or an equivalent operation.

A stored setting that *permits* a hazardous operation doesn't itself *authorize* running it — the actual capability call still goes through its own normal risk/precondition checks (LPDS-017).

---

## 15. Standard Public Python Configuration API

Where a driver exposes configuration through its public API (built on LPDS-003's `BaseInstrument`), the canonical method names are:

- `get_driver_configuration_schema()` — return the JSON Schema.
- `get_driver_default_configuration()` — return the validated package default.
- `get_driver_configuration(scope="effective")` — return the current configuration; redact sensitive fields by default.
- `validate_driver_configuration(configuration, mode="replace")` — validate without applying; returns a result dict (`valid`, `errors`, `changed_paths`).
- `import_driver_configuration(source, mode="replace", apply=False)` — validate and, if `apply=True`, apply. Defaults to validation-only.
- `export_driver_configuration(destination=None, scope="effective")` — return (and optionally write) a portable JSON document, secrets redacted.
- `save_driver_configuration(profile_name)` / `load_driver_configuration(profile_name, apply=False)` — for drivers that support named profiles.
- `reset_driver_configuration(path=None)` — reset to package default.

All of these return plain, JSON-serializable Python values (`str`, `int`, `float`, `bool`, `list`, `dict`, `None`) — not `pathlib.Path`, dataclasses, or other non-primitive objects.

---

## 16. Errors

Configuration failures should raise `DriverConfigurationError` (LPDS-007) or an approved subclass, with enough context to say what field failed and why — not a bare `ValueError` with no field information. A few error situations worth distinguishing: schema validation failure, an unresolvable secret reference, and a safety-rule rejection (e.g. a limit above the device's rated maximum) — the caller needs to know which case they hit.

---

## 17. When to Add More

The following are genuinely useful for the right project, but aren't baseline requirements — add them when you actually need them:

- **Schema migration** between versions, if a driver's config schema changes in a breaking way and there are existing saved profiles to carry forward.
- **Configuration fingerprinting** (a hash of the effective config), if you want to correlate test evidence with the exact configuration that produced it (see LPDS-008).
- **Cross-process file locking**, if multiple processes on the same machine might edit the same named profile concurrently.
- **A `schema.lock` digest**, if external tooling depends on detecting schema drift.

Building these in from day one for a driver that doesn't need them yet is effort spent on infrastructure instead of the device logic that actually matters.

---

## 18. Testing

Unit tests should cover: the package default validates against the schema; an invalid document is rejected with a clear error; `VALIDATE_ONLY` doesn't change state; precedence resolves as documented (env var beats file, constructor arg beats env var, etc.); secrets never appear in a validation error or export; and a safety-relevant field rejects an out-of-range value.

---

## 19. Checklist

- [ ] `schema.json`, `default.json`, and `example.json` exist; `default.json` validates.
- [ ] JSON import/export works with no optional dependencies.
- [ ] Every value is validated before being applied; validation failure changes nothing.
- [ ] Precedence (default → file → env → constructor → call-time) is deterministic and documented.
- [ ] No plaintext secrets appear in the document, exports, logs, or error messages.
- [ ] Package defaults are safe (no credentials, outputs disabled, finite timeouts).
- [ ] Loading a profile at construction doesn't touch hardware.
- [ ] Standard config methods (§15) return plain JSON-serializable values.

---

## 20. Goal

Give every LPDS driver one predictable, JSON-based way to describe, validate, and load its configuration — safe by default, free of undocumented local-file behavior, and no heavier than the driver's actual configuration complexity calls for.

---

## Appendix A — Example Profile

```json
{
  "lpds014_version": "1.1",
  "schema_version": "1.0.0",
  "driver": {
    "driver_name": "example_instrument"
  },
  "settings": {
    "transport": {
      "type": "VISA_USB",
      "resource": "${ENV:EXAMPLE_VISA_RESOURCE}",
      "read_termination": "\n",
      "write_termination": "\n"
    },
    "timeouts": {
      "open_timeout_s": 5.0,
      "read_timeout_s": 10.0
    },
    "retry": {
      "enabled": true,
      "max_attempts": 2
    },
    "simulation": {
      "enabled": false
    },
    "safety": {
      "allow_output_enable_from_profile": false
    },
    "device": {
      "default_channel": 1
    }
  }
}
```

---

## Appendix B — Schema Fragment

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:lpds:example_instrument:configuration:1.0.0",
  "title": "Example Instrument Configuration",
  "type": "object",
  "additionalProperties": false,
  "required": ["lpds014_version", "schema_version", "driver", "settings"],
  "properties": {
    "settings": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "timeouts": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "read_timeout_s": {
              "type": "number",
              "minimum": 0.1,
              "maximum": 120.0,
              "default": 10.0,
              "x-lpds-unit": "s",
              "x-lpds-risk-level": "none"
            }
          }
        },
        "safety": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "allow_output_enable_from_profile": {
              "type": "boolean",
              "default": false,
              "x-lpds-risk-level": "high"
            }
          }
        }
      }
    }
  }
}
```

---

## Appendix C — Change Record

### Deep trim to solo/small-team scale (v1.1)

Rewrote from a ~2450-line specification into a much shorter one. Removed as baseline requirements (moved to §17, "add these when you need them"): schema-migration versioning, cross-process file locking with lock-record schemas, an atomic-write protocol with backup retention and a `rejected/` quarantine directory, and mandatory SHA-256 configuration fingerprinting. Collapsed a six-tier scope precedence model (`PACKAGE_DEFAULT`/`SYSTEM_PROFILE`/`USER_PROFILE`/`PROJECT_PROFILE`/`SESSION_OVERRIDE`/`INSTANCE_OVERRIDE`) down to the five practical layers most drivers actually have (§9). Consolidated acceptance criteria, failure conditions, a 30-item test list, and a review checklist into one checklist (§19). Kept: JSON as the canonical format, safe defaults, validate-before-apply, secret references, and the standard public API method names, since those are the parts of the original design that hold up at any project size.
