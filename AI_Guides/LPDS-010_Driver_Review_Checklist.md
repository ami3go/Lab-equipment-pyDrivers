# LPDS-010 — Driver Production Readiness Review Checklist

**Document ID:** LPDS-010  
**Version:** 1.0  
**Status:** Draft Project Standard (Normative)  
**Applies to:** Every LPDS Python instrument driver gate, phase completion, release candidate, and production release

---

## 1. Purpose

This specification defines a review checklist for deciding whether an LPDS Python instrument driver is ready to call `stable` (LPDS-001 §9). It looks at the driver as a whole, not just the source diff: functional correctness, architecture, public API quality, transport/protocol behaviour, error handling, safety and cleanup, tests, real-device validation, AI contract consistency, and packaging/documentation.

The output is simply: what you checked, what you found, and what you fixed or noted for later — written down somewhere visible. There's no formal scoring model or verdict taxonomy; a driver is either ready to call `stable` or it isn't yet, and the reasons why are more useful than a number.

---

## 2. Scope

### 2.1 In scope

LPDS-010 covers:

- review of the final release ZIP and the extracted stable project root;
- review of all files changed in the current gate or release;
- review of unchanged components whose behaviour is affected by the change;
- verification of required LPDS package content;
- source-code and architecture review;
- public API review;
- protocol and transport review;
- safety, state, resource, and cleanup review;
- test strategy, execution results, coverage, and evidence review;
- LPDS-017 and LPDS-019 consistency;
- documentation, examples, scripts, guides, README, and GitHub Pages review;
- versioning, release identity, changelog, history, checksums, and provenance review;
- compatibility, dependency, supply-chain, licence, and secret-handling review;
- known-risk and residual-risk review;
- final release decision.

### 2.2 Out of scope

LPDS-010 does not replace:

- detailed implementation requirements for a specific instrument;
- unit, integration, simulator, HIL, performance, or conformance test execution;
- LPDS-019 protocol-vector execution;
- formal electrical, metrological, calibration, machinery, medical, or functional-safety certification;
- vendor compliance certification;
- independent penetration testing unless required by the device or deployment scope;
- translation correctness of any separate automation-framework adapter (pytest fixtures, a CLI, a REST endpoint, ...) built on top of this driver.

LPDS-010 reviews the evidence from those activities and determines whether the evidence is sufficient for the claimed release status.

**Note on adapters:** if an adapter exists for this driver, its translation correctness should be reviewed separately, against its own adapter-specific checklist. That review is not part of this driver-focused checklist, which concerns itself only with the driver's own public Python API, behaviour, and evidence.

---

## 3. Normative terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement; deviation requires recorded justification;
- **may** — permitted implementation choice;
- **finding** — something the review turned up worth fixing or noting;
- **evidence** — a reproducible file, report, command output, or test result supporting a conclusion, as opposed to an unverified claim.

---

## 4. Normative references

The review shall use the latest approved applicable revision of:

- LPDS-001 — Platform Requirements;
- LPDS-002 — Mandatory Public API Standard;
- LPDS-003 — BaseInstrument Specification;
- LPDS-004 — Transport Layer Specification;
- LPDS-005 — Driver Package Specification;
- LPDS-006 — Coding Standard;
- LPDS-007 — Error and Exception Standard;
- LPDS-008 — Logging and Evidence Standard;
- LPDS-009 — Testing Standard;
- LPDS-011 — Release Process;
- LPDS-017 — AI Driver Contract Specification;
- LPDS-019 — Driver Call and Protocol Conformance Test Specification;
- LPDS-020 — Driver Implementation Lifecycle;
- the device-specific implementation requirements;
- applicable vendor protocol and programming documentation;
- applicable hardware safety limits and approved bench configuration.

When requirements conflict, precedence shall be:

1. safety and legal requirements;
2. approved device-specific hardware constraints;
3. latest approved LPDS normative requirement;
4. approved implementation task;
5. historical package behaviour and examples.

A conflict shall be recorded and resolved. It shall not be silently interpreted.

---

## 5. Review occasions

This is meant as a self-review checklist first and foremost — there's no assumption that a different person has to run it, though a second pair of eyes is always welcome if one's available. Run it before moving a driver from `untested` to `stable` (LPDS-001 §9), and again after any change to the public API, protocol handling, or safety-relevant behavior.

When you find something worth fixing, a simple two-tier distinction is enough for most projects: things that could cause unsafe hardware behaviour, data corruption, or a silently wrong result are worth fixing before you call the driver `stable`; everything else (missing docs, rough edges, nice-to-have coverage) is fine to note in the README or an issue and come back to.

There's no fixed list of required review-output files or formal PASS/FAIL/WAIVED status vocabulary here — write down what you found and fixed however's convenient (a CHANGELOG entry, an issue, notes in `review/` if you keep one). The point is that the check happened and its results are visible, not that it followed a particular template.

---

## 6. Review Domain A — Release identity and package integrity

Verify that:

1. the archive follows `<driver_name>_v<year>.<release>.zip` or the currently approved LPDS release naming rule;
2. the archive contains exactly one stable root named `<driver_name>/`;
3. archive name, Python package version, driver constant, README, history, release notes, AI contract, generated API, and manifests identify the same revision;
4. Python-normalized version forms are documented where they differ from display versions;
5. the archive is generated from a clean, identified source revision;
6. checksums are generated after the final archive is built;
7. the reviewed archive checksum matches the promoted artifact;
8. the release manifest lists included files and versions;
9. temporary files, local results, credentials, private addresses, caches, virtual environments, and editor artifacts are excluded;
10. required licence, governance, support, security, and contribution files are present;
11. wheel and source/archive content are consistent when multiple artifacts are released;
12. clean extraction does not depend on files outside the stable root.

**Blocking examples:** wrong root folder, inconsistent release version, unreviewed rebuilt archive, missing mandatory package content, secret included in archive.

---

## 7. Review Domain B — Installation, import, and basic operation

Verify on each claimed primary platform, or on the approved compatibility matrix, that:

1. a clean virtual environment can be created;
2. production and development dependencies install using documented commands;
3. dependency resolution is bounded and reproducible enough for the support policy;
4. the package builds successfully;
5. the wheel installs successfully when a wheel is provided;
6. the driver imports in Python;
7. the driver is fully importable, constructible, and controllable from a plain Python/pytest session with no automation framework installed;
8. API reference documentation generation succeeds without import side effects;
9. no hardware connection or output activation occurs merely from importing the module;
10. the minimal simulated or safe identity workflow executes;
11. uninstall/reinstall does not leave hidden required state;
12. scripts resolve paths from their own location and work outside the repository working directory.

**Blocking examples:** clean install fails, Python import fails, import activates hardware, documented quick start is not reproducible.

---

## 8. Review Domain C — Architecture and maintainability

Verify that:

1. the driver's device semantics, protocol mapping, and transport responsibilities are cleanly separated from any adapter's translation responsibilities;
2. any adapter does not duplicate protocol or device logic that belongs in the driver;
3. raw transport details are not required for normal driver usage except documented resource configuration;
4. state ownership and state transitions are explicit;
5. connection/session ownership is explicit;
6. cleanup behaviour is defined for normal close, failed connection, method failure, test-run abort, and process exit where practical;
7. retry, timeout, and recovery policy is implemented at the correct layer;
8. protocol knowledge has a single authoritative implementation location;
9. device-specific and bench-specific configuration is not hard-coded into reusable logic;
10. dependencies flow in one direction without circular or test-only production coupling;
11. core logic can be tested without any automation framework or uncontrolled hardware where practical;
12. extension points do not expose unstable internals as public API;
13. concurrency and multi-session behaviour are defined and conservative by default;
14. files, modules, classes, and functions have coherent responsibilities;
15. complex logic is documented and covered by focused tests;
16. approved architectural exceptions are recorded with rationale and risk.

**Blocking examples:** protocol duplicated across conflicting paths, session leak after connection failure, hidden global state causing cross-test contamination, architecture prevents deterministic testing of critical logic.

---

## 9. Review Domain D — Public API

Verify that:

1. only intended public methods and properties are exposed;
2. public methods and properties have unique, unambiguous names within the driver's public surface;
3. names follow LPDS-002 conventions and are consistent with equivalent driver classes;
4. argument order, names, defaults, units, enums, and accepted types are documented;
5. aliases and deprecations are explicit;
6. minor releases preserve compatible names and signatures unless an approved exception exists;
7. return values are plain Python types (or documented value objects) and stable;
8. verification methods raise actionable exceptions or return actionable failure information;
9. setup and teardown methods are usable without private helper calls;
10. connection methods support the documented transport-neutral workflow where required;
11. method and property docstrings state preconditions, postconditions, side effects, risk, timing, and failure behaviour;
12. unsupported capabilities fail explicitly rather than silently doing nothing;
13. raw protocol access, when exposed, is clearly marked diagnostic/high risk and does not bypass safety without warning;
14. the API manifest, generated API reference documentation, README, examples, tests, and LPDS-017 contract agree;
15. public API additions, changes, aliases, deprecations, and removals are recorded in history and release notes.

**Blocking examples:** missing method used by documented workflows, accidental public method exposure, undocumented breaking change, wrong return type, method reports success after failed device operation.

---

## 10. Review Domain E — Transport and protocol correctness

Verify that:

1. supported transports match documentation and package dependencies;
2. open, read, write, query, transaction, and close semantics are bounded by finite timeouts;
3. terminators, encodings, addresses, channels, checksums, byte order, and framing are correct;
4. command/query serialization preserves units and precision;
5. raw responses are validated before semantic conversion;
6. malformed, incomplete, stale, or unexpected responses are rejected;
7. command-only operations do not wait for undefined responses;
8. transport errors are not converted into success;
9. partial connection failures close and reset acquired resources;
10. transport tracing can observe the device boundary without changing functional behaviour;
11. simulator or replay behaviour preserves the relevant real protocol boundary;
12. vendor SDK calls are mapped and observed with equivalent rigor;
13. reconnect and session reset behaviour are defined;
14. representative protocol operations are verified on a real device when safe and practical;
15. LPDS-019 mandatory vectors, traces, matrices, and acceptance criteria pass.

**Blocking examples:** wrong command or frame, parser accepts malformed response as valid, query reads mismatched response, timeout can block indefinitely, LPDS-019 missing or failing for supported device-facing public methods.

---

## 11. Review Domain F — Errors, diagnostics, retry, and recovery

Verify that:

1. exceptions follow LPDS-007 taxonomy;
2. transport, protocol, device, validation, state, configuration, timeout, and safety failures remain distinguishable;
3. error messages identify operation, resource/alias, relevant arguments, and recovery guidance without exposing secrets;
4. invalid user values are rejected before transmission when appropriate;
5. device-rejected values are reported with the original device error where available;
6. retries are limited, observable, and used only for operations safe to repeat;
7. non-idempotent operations are not retried without explicit protection;
8. timeout behaviour is deterministic;
9. recovery leaves the driver in a documented state;
10. a known-good operation is verified after recoverable faults;
11. error queues or status registers are handled according to device semantics;
12. diagnostics export records versions, configuration, state, recent errors, and logs with secrets redacted;
13. cleanup errors are not silently discarded when they affect safety or resource release;
14. regression tests exist for corrected failures.

**Blocking examples:** malformed error response interpreted as “no error,” infinite retry, unsafe repeated command, recovery claims success while session is unusable, critical cleanup failure hidden.

---

## 12. Review Domain G — Safety, limits, and resource ownership

Verify that:

1. safety responsibilities are assigned to driver, adapter, device, fixture, bench, test plan, or operator layers;
2. connection and initialization do not unintentionally energize outputs or alter hazardous state;
3. safe limits are configurable, validated, documented, and represented in LPDS-017 where applicable;
4. unsafe ranges, channel combinations, relay paths, or command sequences are prohibited or explicitly controlled;
5. manual actions and physical reconfiguration are visible and cannot be silently assumed;
6. normal teardown reaches the declared safe state;
7. failure, abort, timeout, and emergency paths attempt the safest achievable state;
8. the driver does not claim a safe state that it cannot verify or enforce;
9. disconnect semantics distinguish logical session closure from physical output state;
10. resources requiring exclusive ownership are declared and locked or otherwise protected;
11. concurrency is disabled unless safe behaviour is demonstrated;
12. current, voltage, power, temperature, pressure, motion, relay, and other applicable risks are reviewed;
13. HIL profiles declare allowed and prohibited operations;
14. HIL tests preserve evidence of startup state, limits, cleanup, and final state;
15. known safety assumptions and residual risks are prominent in README, guides, contracts, and review records.

**Blocking examples:** missing safe teardown for controllable output, wrong-channel actuation, unbounded output, hidden hazardous default, unverified safety claim, concurrent access can produce unsafe state.

---

## 13. Review Domain H — Configuration, state, and resources

Verify that:

1. configuration schema defines names, types, units, defaults, limits, and required values;
2. safe reusable defaults are separated from bench-specific resource assignments;
3. precedence among constructor arguments, environment variables, configuration files, and adapter-supplied variables (where an adapter exists) is documented;
4. unknown keys are handled deterministically;
5. configuration can be exported in normalized form with secrets redacted;
6. local paths, real credentials, private bench addresses, serial numbers, and user names are not committed as reusable defaults;
7. aliases, sessions, channels, and resources have deterministic lifecycle rules;
8. repeated connect/disconnect and failed connect do not leave stale state;
9. configuration changes that require reconnect are enforced or documented;
10. calibration, correction, or persistent device files are versioned and protected from accidental overwrite where applicable;
11. multi-session and multi-channel isolation are tested where supported;
12. resource conflict rules align with LPDS-017 where applicable.

---

## 14. Review Domain I — Tests, coverage, and evidence

Verify that the applicable test layers are present and current:

1. static analysis and packaging checks;
2. Python unit tests;
3. protocol serialization and parser tests;
4. transport-adapter tests;
5. integration tests;
6. deterministic simulator or replay tests;
7. pytest-based acceptance tests;
8. LPDS-019 conformance tests;
9. real-device/HIL tests;
10. safety and recovery tests;
11. regression tests for corrected defects;
12. compatibility tests;
13. performance, soak, memory, or concurrency tests where required.

For test quality, verify that:

14. tests assert meaningful results rather than only absence of exceptions;
15. failure paths and boundary values are covered;
16. tests are independent and declare prerequisites;
17. hardware tests are disabled by default and require explicit enablement and resources;
18. hardware tests never silently fall back to simulation;
19. skipped and excluded tests have reasons;
20. expected failures are not used to hide unresolved defects;
21. coverage is measured against the correct production code;
22. coverage thresholds follow LPDS-009 or the approved task;
23. coverage does not replace protocol or HIL evidence;
24. evidence records driver, Python, OS, transport, simulator/device identity, firmware, configuration profile, and safety limits;
25. result totals in README, review, history, and reports agree;
26. test reports can be reproduced using packaged scripts;
27. evidence corresponds to the exact release candidate.

**Blocking examples:** mandatory tests fail, results are stale or from different bytes, no HIL evidence for a production hardware claim, skipped mandatory conformance tests, false coverage caused by excluding critical modules.

---

## 15. Review Domain J — Hardware qualification, performance, and compatibility

Verify, as applicable, that:

1. representative supported device models and firmware are identified;
2. real-device identity and transport are captured;
3. representative command classes and workflows execute on hardware;
4. physical state/readback confirms device-side operation where feasible;
5. startup, disconnect, abort, and recovery behaviour are observed;
6. unsupported models, cards, modules, firmware, or transport combinations are explicit;
7. timing, stabilization, and timeout values are supported by evidence;
8. repeated operation does not show resource leakage or state drift;
9. long-duration, stress, throughput, memory, or concurrency tests exist when required by scope;
10. supported Python, dependency, OS, architecture, transport, device, and firmware combinations are listed;
11. minimum and maximum supported versions are tested or justified;
12. optional dependencies fail gracefully when absent;
13. deprecation and migration policy is documented;
14. known compatibility limitations are reflected consistently across documentation and contracts.

A driver that controls real hardware shouldn't be called `stable` on simulator evidence alone, unless its documented scope explicitly excludes physical-device support.

---

## 16. Review Domain K — AI contracts and traceability

Verify that:

1. LPDS-017 files exist at the required paths;
2. the lock is valid and generated from the released contract;
3. identity and version match the release;
4. every intended public method has a capability entry;
5. capability signatures match the driver class and generated API reference documentation;
6. inputs, outputs, preconditions, postconditions, side effects, risk, timing, stabilization, retry, errors, and resources are complete;
7. state-machine references are valid;
8. setup and teardown workflows use existing public methods;
9. limitations and UNKNOWN handling are explicit;
10. verification objectives have usable pass/fail oracles;
11. protocol intent aligns with LPDS-019 vectors;
12. safety rules align with implementation and documentation;
13. requirement traceability links requirements to code, tests, documentation, contracts, protocol evidence, and hardware evidence, where a project chooses to track this;
14. no requirement is marked complete without implementation and test evidence;
17. deferred and not-applicable requirements have reasons and owners where appropriate.

**Blocking examples:** stale AI contract describes nonexistent method, wrong safety semantics, invalid lock, missing protocol vector mapping, traceability claims hardware-tested without hardware evidence.

---

## 17. Review Domain L — Documentation, examples, scripts, and GitHub Pages

Verify that:

1. README identifies purpose, supported devices, release version, compatibility, transports, installation, quick start, safety, HIL status, limitations, and documentation links;
2. README does not contradict code, AI contract, examples, or release evidence;
3. API reference documentation is generated from the released driver;
4. GitHub Pages builds strictly without broken links or stale generated API content;
5. installation and PyCharm (or equivalent IDE) setup guides are current for Windows and Linux;
6. hardware setup separates reusable guidance from private bench configuration;
7. troubleshooting covers import, permission, resource, vendor-runtime, timeout, protocol, and recovery problems;
8. at least ten numbered, complete plain-Python usage examples are present unless an approved exception exists;
9. examples use only supported public APIs unless explicitly marked as diagnostics;
10. every example states purpose, mode, prerequisites, variables, setup, teardown, expected result, safety limits, and exact run command;
11. examples avoid hard-coded personal paths, credentials, private addresses, and uncontrolled hardware defaults;
12. safe cleanup is visible in every hardware-changing example;
13. Windows PowerShell, Windows batch where required, and Linux shell scripts are present and current;
14. scripts can run one example and the complete example set;
15. simulation examples run in CI where practical;
16. release notes and history describe public API, behaviour, safety, dependency, compatibility, test, and documentation changes;
17. documentation clearly distinguishes simulated, protocol-conformant, and physically validated claims.

**Blocking examples:** stale README for another version, unsafe example, fewer than ten examples without approved exception, scripts cannot run documented workflows, GitHub Pages exposes outdated API.

---

## 18. Review Domain M — Security, dependencies, and release provenance

Verify that:

1. no credentials, tokens, private keys, passwords, or private bench data are present in source, history, tests, examples, traces, reports, or archive metadata;
2. logs and diagnostics redact secrets;
3. dependencies are declared, reviewed, and constrained according to the support policy;
4. dependency licences are compatible with the project licence;
5. known material vulnerabilities are reviewed and dispositioned;
6. CI and release workflows use minimum permissions;
7. third-party actions are pinned according to project policy;
8. release creation is deterministic or sufficiently reproducible to detect unexpected differences;
9. release manifest, SBOM, checksums, and provenance are generated where required;
10. build and release scripts do not download or execute unverified content without control;
11. archive extraction is safe from path traversal and unexpected executables;
12. generated evidence does not disclose sensitive device identifiers when policy requires redaction;
13. raw protocol or file-upload capabilities validate paths, sizes, and inputs appropriate to their risk;
14. security limitations and reporting procedure are documented.

**Blocking examples:** committed secret, known exploitable dependency with no containment, mutable unreviewed release workflow, checksum generated before final artifact mutation.

---

## 19. What Good Evidence Looks Like

"Tests passed" isn't evidence on its own — a test report, the environment it ran in, and what it actually covered is. When you check something off, prefer something reproducible (a command, a test file, a log) over a bare assertion. Distinguish static read-through from actually running the code, and simulator results from real-hardware results — both are useful, but they prove different things.

When reading a diff, look past line count at behavioral impact: does a changed public method still have matching tests and docs? Are exception handling, retries, and cleanup paths still correct? Are units, channel indexing, and numeric conversions still right? A quick scan for hard-coded resources, leftover `TODO`s, debug prints, or disabled tests catches a lot cheaply.

---

## 20. Doing the Review

For a solo driver, walking through the domain checklists above (§11-23) against the actual code and running the test suite is the review — no separate workflow needed. For something with more at stake (a breaking change, a safety-relevant fix, preparing to call the driver `stable` for the first time), it's worth doing methodically:

1. Build and install in a clean environment; confirm the package imports with no automation framework present.
2. Run the automated suite (unit, simulator, LPDS-019 conformance, and real-hardware tests if available) and look at what actually ran versus what was skipped.
3. Read through the changed code and anything it touches.
4. Check that the public API, the AI contract (if published), and the documentation still agree with each other.
5. Note what you found and fixed, and what's still open, somewhere visible (CHANGELOG, issue tracker, or `review/` notes if you keep them).

---

## 21. Checklist Summary

Before calling a driver `stable` (LPDS-001 §9), you should be able to say yes to each of these:

1. Does the package build, install, and import cleanly with no automation framework installed?
2. Is the public API (LPDS-002) intentional, typed, documented, and stable?
3. Are transport and protocol operations correct and finitely bounded?
4. Are malformed responses, timeouts, device errors, and disconnects handled, with recovery reaching a documented state?
5. Are safe initialization, limits, teardown, and resource ownership defined and verified?
6. Do the applicable test layers (unit, simulator, LPDS-019 conformance, and — for `stable` — real hardware) pass?
7. If published, does the AI Driver Contract (LPDS-017) match the actual API and behavior?
8. Are README, examples, and docs current and consistent with the code?
9. Are dependencies, secrets, and licenses handled reasonably (no committed credentials, no undocumented binaries)?
10. If an adapter exists for this driver, has its translation correctness been reviewed separately, under its own checklist?

A "not yet" on any of these isn't a blocker — it's something to note in the README per LPDS-001 §32, and the honest reason the driver's status is `wip` or `untested` rather than `stable`.

---

## 22. Goal

Provide a repeatable way to check that an LPDS Python instrument driver is safe, correct, and sufficiently validated for the status it claims — usable by one person reviewing their own work, without assuming a dedicated reviewer, a scoring rubric, or a formal approval chain.

The review shall make it impossible to confuse a promising development package, a simulator-only implementation, or a partially documented driver with a production-approved release.

---

## Appendix A — Recommended finding identifiers

Use:

```text
LPDS010-REV-001
LPDS010-REV-002
...
```

Device-specific projects may prefix the driver name while preserving a stable numeric identifier.

---

## Appendix B — Recommended correction priority

A simple two-tier split is usually enough: fix-before-`stable` (anything touching safety, correctness, or a silently wrong result), and everything else (track it, fix it when convenient). Use a finer-grained priority scheme only if a project's actual issue volume justifies it.

---

## Appendix C — Relationship to LPDS-019

LPDS-019 proves that declared public API calls reach the intended protocol operation and correctly return applicable device responses.

LPDS-010 shall consume LPDS-019 evidence but shall not duplicate or weaken it. LPDS-010 adds the wider production-readiness decision covering architecture, safety, tests, hardware qualification, documentation, packaging, AI contracts, compatibility, security, provenance, and release governance.

A driver may pass LPDS-019 and still fail LPDS-010. A device-facing production driver shall not pass LPDS-010 when mandatory LPDS-019 conformance fails.
