# LPDS-011 — Release Process

**Document ID:** LPDS-011  
**Version:** 1.0  
**Status:** Draft Project Standard (Normative)  
**Applies to:** All LPDS Python instrument driver repositories, engineering gate packages, public driver releases, release evidence, and GitHub publication workflows

---

## 1. Purpose

This specification defines the mandatory process for versioning, documenting, building, validating, approving, packaging, publishing, and maintaining releases of LPDS Python instrument drivers.

Its goals are to ensure that every delivered revision:

1. has one unambiguous identity;
2. uses the correct archive name and stable internal folder;
3. records every delivered change;
4. is built from reviewed source;
5. passes the applicable software, simulator, conformance, and hardware gates;
6. contains current code, tests, AI contracts, examples, guides, README, and GitHub Pages content;
7. can be installed and reproduced from published artifacts;
8. provides integrity, dependency, and provenance evidence;
9. preserves compatibility or documents an approved migration;
10. can be audited after publication.

LPDS-011 defines **how a revision becomes an approved release**. LPDS-005 defines where release content belongs. LPDS-009 defines testing. LPDS-010 defines review. LPDS-017 defines the AI Driver Contract. LPDS-019 defines driver call and protocol conformance.

---

## 2. Scope

### 2.1 In scope

LPDS-011 covers the release process for a driver package and, equally, for the shared `lpds-core` package that LPDS-003 requires every driver to depend on — `lpds-core` is versioned and released independently of any driver, through this same process. LPDS-011 covers:

- driver identifiers and release identities;
- engineering gate versions;
- public release versions;
- Python package-version normalization;
- version-source synchronization;
- release sequence allocation;
- change classification;
- changelog, history, release-note, migration, and deprecation records;
- release prerequisites and release-blocking conditions;
- deterministic release construction;
- ZIP, wheel, source-distribution, documentation, evidence, SBOM, checksum, and provenance artifacts;
- clean-install validation;
- GitHub release and GitHub Pages publication;
- release immutability;
- correction, hotfix, rollback, yanking, and supersession procedures;
- post-release verification and audit records.

### 2.2 Out of scope

LPDS-011 does not define:

- the detailed driver repository layout, except where required for release validation;
- the complete public API;
- device-specific functionality;
- vendor protocol behaviour;
- test implementation details owned by LPDS-009 or LPDS-019;
- detailed code-review criteria owned by LPDS-010;
- external package-index, organisation, or signing infrastructure that the project does not control.

---

## 3. Normative references

A conforming release shall follow the applicable approved revisions of:

- **LPDS-001 — Platform Requirements**;
- **LPDS-002 — Mandatory Public API Standard**;
- **LPDS-005 — Driver Package Specification**;
- **LPDS-006 — Coding Standard**;
- **LPDS-007 — Error and Exception Standard**;
- **LPDS-008 — Logging and Evidence Standard**;
- **LPDS-009 — Testing Standard**;
- **LPDS-010 — Review Checklist**;
- **LPDS-017 — AI Driver Contract Specification**;
- **LPDS-019 — Driver Call and Protocol Conformance Test Specification**;
- **LPDS-020 — Driver Implementation Lifecycle**;
- the approved device-specific implementation requirements;
- applicable vendor protocol and safety documentation.

When requirements conflict, the precedence shall be:

1. safety and legal requirements;
2. approved device-specific hardware constraints;
3. the latest approved parent LPDS requirement;
4. the latest approved specialised LPDS requirement;
5. historical package conventions.

A conflict shall not be resolved silently. It shall be recorded in `review/requirement_traceability.md` and resolved before release approval.

---

## 4. Normative terminology

- **shall / shall not** — mandatory requirement;
- **should / should not** — recommended requirement; deviation requires documented justification;
- **may** — permitted implementation choice;
- **engineering gate artifact** — a reviewable package produced for a lifecycle phase and gate;
- **release candidate** — a frozen candidate carrying the intended public release identity but not yet published as final;
- **public release** — an approved immutable package distributed to users;
- **release/update number** — the public sequence number for a driver within a calendar year;
- **promotion** — the controlled conversion of an approved engineering revision into a public release;
- **rebuild** — reconstruction of artifacts from the same source and version;
- **supersession** — publication of a newer release that replaces a previous release for normal use;
- **yank** — retention of a published release for audit while marking it unsuitable for new use;
- **release evidence** — records proving the source, environment, tests, reviews, identity, and integrity of the release.

---

## 5. Release identities

### 5.1 Stable driver identifier

Every driver shall define one stable identifier:

```text
<driver_name>
```

It shall:

- use lowercase ASCII;
- use `snake_case` only;
- contain no spaces or hyphens;
- contain no version number;
- remain stable across releases;
- identify the vendor/model/family or logical device service clearly enough to avoid collisions.

Examples:

```text
hp34401a
bk8500b
keysight_n6700
phidget_relay
climate_chamber
```

### 5.2 Public release version

Every public driver release or update shall use:

```text
vYY.RR
```

Where:

- `YY` is the final two digits of the calendar year in which the public release is approved;
- `RR` is the zero-padded release/update sequence for that driver in that year;
- `RR` starts at `01`;
- `RR` increments by one for every new public package;
- `RR` resets to `01` when `YY` changes.

Examples:

```text
v26.01
v26.02
v27.01
```

A skipped sequence number shall remain unused and shall be recorded in the release ledger or release review.

### 5.3 Engineering gate version

Every reviewable lifecycle gate package shall use:

```text
vYY.PP.GG
```

Where:

- `YY` is the two-digit year;
- `PP` is the two-digit implementation phase;
- `GG` is the two-digit gate number.

Examples:

```text
v26.01.01    Phase 1, Gate 1
v26.01.05    Phase 1, Gate 5
v26.02.03    Phase 2, Gate 3
```

An engineering gate version is not a public release number and shall not consume a public `RR` sequence.

### 5.4 Release-candidate identity

A release candidate may use:

```text
vYY.RR-rc.N
```

Where `N` starts at `1` and increments for each candidate built for the same intended public release.

Example:

```text
v26.03-rc.1
```

Release candidates shall not be presented as final releases. Their artifacts shall be replaced by newly generated final artifacts after approval; an RC ZIP shall not merely be renamed.

### 5.5 Python package version

The Python package version shall be a normalized representation of the same release identity.

Recommended mapping:

| LPDS identity | Python package version |
|---|---|
| `v26.01` | `26.1` |
| `v26.02` | `26.2` |
| `v26.01.03` | `26.1.3` |
| `v26.03-rc.1` | `26.3rc1` |

Zero padding remains mandatory in archive names, human-facing history files, review filenames, and release notes even when the package tool normalizes it.

The mapping shall be deterministic and validated by `scripts/build_release.py`.

### 5.6 Version immutability

After publication, a public version identifies one immutable artifact set.

The project shall not:

- replace a published ZIP with different bytes under the same version;
- modify a published wheel or source distribution under the same version;
- edit package-contained history or release notes and republish under the same version;
- rebuild a materially different package without allocating a new public release number.

A rebuild using the same version is permitted only when it produces byte-identical artifacts. Otherwise a new `vYY.RR` shall be allocated.

---

## 6. Archive naming and internal root

### 6.1 Public driver ZIP

The public driver ZIP shall be named exactly:

```text
<driver_name>_vYY.RR.zip
```

Examples:

```text
hp34401a_v26.01.zip
keysight_n6700_v26.04.zip
```

It shall not include:

- spaces;
- words such as `final`, `latest`, `fixed`, `new`, or `production`;
- a date in addition to the version;
- an operator name;
- a branch name or commit hash;
- an RC or gate suffix after final approval.

### 6.2 Engineering gate ZIP

A lifecycle gate package shall be named:

```text
<driver_name>_vYY.PP.GG.zip
```

Example:

```text
keysight34970_v26.03.04.zip
```

### 6.3 Release-candidate ZIP

A candidate may be named:

```text
<driver_name>_vYY.RR-rc.N.zip
```

It shall not be placed in the final public release channel.

### 6.4 Stable internal root

Every driver ZIP shall contain exactly one top-level folder:

```text
<driver_name>/
```

Example:

```text
hp34401a_v26.01.zip
└── hp34401a/
```

The internal folder shall:

- be version-independent;
- contain all driver package content (including any bundled adapters);
- have no sibling file in the ZIP;
- permit a new release to replace the previously extracted project directory.

### 6.5 Separate evidence archive

When release evidence is published separately, it shall use:

```text
<driver_name>_vYY.RR_evidence.zip
```

This is not a driver package and shall not be confused with the distributable ZIP.

The evidence archive may contain test results, traces, review exports, build logs, HIL records, and provenance files that are inappropriate for the main driver ZIP.

---

## 7. Version sources of truth

### 7.1 Authoritative version source

Each project shall designate one authoritative version source, normally:

```text
<driver_name>/version.py
```

It should expose equivalent values to:

```python
DISPLAY_VERSION = "26.01"
ARCHIVE_VERSION = "v26.01"
PYTHON_VERSION = "26.1"
RELEASE_KIND = "public"
```

Gate or candidate builds shall use the corresponding identity.

### 7.2 Synchronized version locations

The release build shall validate all applicable version occurrences, including:

- `<driver_name>/version.py`;
- `pyproject.toml`;
- package `__init__.py` exports;
- package entry-point metadata (e.g. `pyproject.toml` entry-points used for driver/adapter discovery);
- `ai/ai_contract.yaml`;
- `ai/ai_contract.lock`;
- `README.md`;
- `CHANGELOG.md`;
- `docs/index.md`;
- `docs/release_notes.md`;
- `mkdocs.yml` where versioned;
- current `history/` filename and heading;
- current `review/` filenames and headings;
- generated API reference documentation;
- generated API manifest;
- `release/release_manifest.json`;
- ZIP filename;
- wheel and source-distribution metadata.

A stale or contradictory version shall fail the release build.

### 7.3 Version mutation

Version updates shall be performed by an automated script or one controlled source-of-truth change followed by regeneration.

Manual search-and-replace across the repository should not be the primary versioning method.

### 7.4 Release sequence allocation

The maintainer allocates `YY.RR` before the first release-candidate build.

The allocation shall be recorded in at least one of:

- the release issue;
- the release pull request;
- the release ledger;
- the release-readiness review.

Two branches shall not publish the same public release identity.

---

## 8. Release types and required treatment

### 8.1 Engineering gate artifact

Purpose:

- review a bounded phase/gate increment;
- demonstrate progress;
- carry gate-specific history and review evidence.

Requirements:

- use `vYY.PP.GG`;
- satisfy the gate acceptance criteria;
- include all mandatory current package folders;
- identify incomplete future-gate work explicitly;
- not claim public production approval.

### 8.2 Public feature release

Purpose:

- deliver approved new capabilities or substantial compatible enhancement.

Requirements:

- allocate the next `vYY.RR`;
- update API, AI contract, tests, examples, docs, compatibility, history, reviews, and release notes;
- execute all mandatory release gates;
- publish complete integrity artifacts.

### 8.3 Public maintenance release

Purpose:

- deliver defect corrections, dependency updates, documentation corrections, packaging fixes, or compatible internal improvements.

Requirements:

- allocate the next `vYY.RR` when package bytes change;
- include regression tests for corrected reproducible defects where practical;
- update history, review, and release notes;
- rerun the full mandatory release workflow, not only the changed test subset.

### 8.4 Emergency security or safety release

Purpose:

- correct an urgent vulnerability or unsafe behaviour.

Requirements:

- allocate the next public release number;
- prioritise containment and verified correction;
- document any temporarily reduced non-critical gate with explicit risk acceptance;
- never waive mandatory safety validation for the affected function;
- publish migration, advisory, and supersession information;
- complete deferred evidence as soon as permitted by the approved incident process.

### 8.5 Documentation-only website update

A GitHub Pages correction that does not change a published package may retain the package version only when:

- the released package bytes are not changed;
- the correction does not change API meaning, safety guidance, compatibility claims, or operational instructions;
- the site records the documentation revision and date;
- the correction is reviewed.

A package-contained documentation change shall use a new public release number.

---

## 9. Change classification

Every release shall classify each delivered change.

Permitted classifications are:

- **Added** — new supported capability, public API method, transport, model, example, or documented workflow;
- **Changed** — compatible behaviour, performance, configuration, documentation, or internal design change;
- **Deprecated** — still supported but scheduled for future removal or replacement;
- **Fixed** — defect correction;
- **Security** — security-relevant correction or hardening;
- **Safety** — safety limit, safe-state, interlock, or recovery correction;
- **Removed** — removed API, capability, platform, model, or configuration;
- **Compatibility** — support matrix or dependency-boundary change;
- **Packaging** — build, archive, dependency metadata, scripts, CI, manifest, SBOM, or publication change;
- **Known limitations** — unresolved restriction or validation gap relevant to users.

Each change shall also be classified as:

- **compatible**;
- **conditionally compatible**;
- **breaking**;
- **internal only**.

A release shall not mark a user-visible change as internal only.

---

## 10. Compatibility and breaking changes

### 10.1 Compatible changes

Examples include:

- adding a new public API method without changing existing methods;
- adding a new optional argument at the end with a backward-compatible default;
- adding a supported device model without weakening existing behaviour;
- correcting implementation to match already documented behaviour;
- adding diagnostics, examples, tests, or documentation;
- improving performance without changing externally visible timing guarantees or results.

### 10.2 Conditionally compatible changes

Examples include:

- tightening validation that rejects values previously accepted but unsupported;
- changing retry timing while preserving documented bounds;
- correcting an ambiguous return field;
- changing a dependency lower or upper bound;
- changing default behaviour to improve safety.

These changes require explicit release-note impact, compatibility review, and migration guidance where a user could be affected.

### 10.3 Breaking changes

A change is breaking when it removes or incompatibly changes any released contract, including:

- canonical public API method name;
- supported alias;
- argument order;
- required arguments;
- default values;
- accepted units or value forms;
- return type or return schema;
- exception type or stable failure/error contract;
- side effects;
- connection/session semantics;
- safe-state semantics;
- configuration key or meaning;
- supported model, firmware, Python, or operating-system range;
- a bundled adapter's declared framework-version support;
- protocol operation where users rely on documented raw-command behaviour.

### 10.4 Approval for breaking changes

A breaking release shall:

1. state `BREAKING CHANGE` prominently in history and release notes;
2. include `docs/migration.md` instructions;
3. update compatibility and support-policy documentation;
4. include an API diff;
5. include affected AI contract and protocol-vector changes;
6. include regression tests for the new behaviour;
7. document why compatibility could not be preserved;
8. receive explicit release-authority approval.

### 10.5 Deprecation before removal

A public API should be deprecated for at least one public release before removal.

Deprecation shall define:

- deprecated capability;
- replacement;
- first deprecated release;
- earliest removal release or condition;
- warning behaviour;
- migration example.

Immediate removal is permitted only for an approved security, safety, legal, or fundamentally non-functional issue. The exception shall be documented.

---

## 11. Changelog, history, and release notes

### 11.1 Required records

Every public release shall update:

```text
CHANGELOG.md
history/vYY.RR.md
docs/release_notes.md
```

Every engineering gate package shall update:

```text
history/vYY.PP.GG.md
```

### 11.2 `CHANGELOG.md`

`CHANGELOG.md` shall be a concise release index, newest first.

Each public release entry shall include:

- version;
- release date;
- release status;
- brief high-value summary;
- change categories used;
- link to the detailed `history/` entry;
- breaking-change indicator;
- migration link when required;
- security or safety advisory link when applicable.

It shall not replace the detailed history file.

### 11.3 Detailed history entry

`history/vYY.RR.md` or `history/vYY.PP.GG.md` shall account for every delivered change.

It shall include at least:

1. identity and date;
2. release or gate objective;
3. source baseline and revision reference;
4. added, changed, deprecated, fixed, security, safety, removed, compatibility, and packaging changes as applicable;
5. public API impact;
6. configuration impact;
7. dependency impact;
8. AI contract and protocol-vector impact;
9. test and evidence summary;
10. documentation and example changes;
11. migration requirements;
12. known limitations and residual risks;
13. linked review records.

Generic entries such as “updates”, “fixes”, or “improvements” without traceable detail are not acceptable.

### 11.4 Current release notes

`docs/release_notes.md` shall describe the current public release for users.

It shall include:

- headline changes;
- supported device and environment changes;
- installation or upgrade instructions;
- compatibility impact;
- breaking changes and migration;
- safety-relevant changes;
- known limitations;
- hardware-validation status;
- links to complete history, reviews, compatibility matrix, and checksums.

### 11.5 Unreleased changes

A project may maintain an `Unreleased` section in `CHANGELOG.md` during development.

Before final release:

- every item shall move into the allocated version;
- the `Unreleased` section shall be empty or contain only post-freeze work not included in the release;
- no included change may remain described only as unreleased.

### 11.6 History-to-review traceability

Every significant history item shall map to:

- an implementation change;
- one or more tests or a justified non-testable classification;
- review evidence;
- documentation updates when user-visible.

The release-readiness review shall verify this mapping.

---

## 12. Getting Ready to Release

Once you're preparing a release, it's worth mentally "freezing" scope: stop adding public API changes, and limit yourself to fixing release-blocking defects, correcting docs to match already-implemented behavior, and syncing version metadata. If something comes up that genuinely needs a new capability or a behavior change, that's fine — just recognize it reopens the scope, and re-run whatever tests or review that change touches before releasing.

---

## 13. Mandatory pre-release prerequisites

Before building a final candidate, the project shall confirm:

### 13.1 Source and repository

- working tree is clean;
- source revision is identified;
- submodules or vendored dependencies are pinned;
- no unresolved merge markers exist;
- no generated content is stale;
- release branch protection and review requirements are satisfied;
- third-party workflow actions are pinned according to project policy.

### 13.2 Version and identity

- the correct `YY.RR` is allocated;
- all version sources agree;
- driver, distribution, import, package entry-point, and archive names agree;
- current history and review filenames match the release;
- previous approved release is identified for API and package comparison.

### 13.3 Implementation

- source compiles;
- package imports without hardware access;
- generated API reference documentation build performs no hardware access;
- no placeholder implementation remains in declared supported scope;
- no debug bypass or unsafe test hook is enabled by default.

### 13.4 Contracts and metadata

- LPDS-017 contract is complete and current;
- LPDS-017 lock validates;
- capability metadata matches code and documentation;
- public API manifest is regenerated;
- protocol vectors are current for device-facing public API methods.

### 13.5 Documentation and examples

- README matches the release;
- GitHub Pages source and navigation match the release;
- setup guides use current names and commands;
- compatibility, migration, support, safety, and hardware-validation pages are current;
- at least ten complete numbered examples exist unless an approved exception applies;
- every example is runnable through the packaged scripts;
- examples use safe setup and teardown and contain no private bench data.

### 13.6 History and review

- current history entry is complete;
- required code, architecture, API, documentation, security, compatibility, and release-readiness reviews exist;
- no Critical finding is open;
- Major findings are corrected or formally accepted with owner and rationale;
- known risks and HIL gaps are explicit;
- requirement traceability is current.

---

## 14. Before You Publish

A rough sequence that catches most problems, roughly in order:

1. **Structure and identity** — correct archive filename, one stable internal root, no forbidden/leftover files.
2. **Static quality** — formatting, linting, type checking pass; no secrets in the diff.
3. **Software tests** — unit, simulator-based, and compatibility tests pass.
4. **LPDS-019 conformance** — passes against the simulator at minimum; label simulator-only results as simulator evidence, not physical-hardware proof.
5. **Hardware validation, if you have the hardware** — record device/firmware/transport identity, verify safe cleanup, don't silently fall back to the simulator if a real connection was expected.
6. **Docs and examples** — README and examples match the code being released; examples actually run.
7. **Build and clean-install** — build the wheel/sdist, install into a clean environment, confirm import and a basic workflow work.

A release manifest (§18) is worth generating every time; an SBOM, detached checksums, and build provenance are worth adding once you have consumers who need that level of supply-chain assurance — not a default requirement.

There's no separate "release authority" approval step assumed here — for a solo or small-team driver, working through the list above *is* the approval.

---

## 15. Release build workflow

The canonical release build shall perform the following sequence.

### Step 1 — Establish clean build environment

- create a clean virtual environment or isolated build environment;
- install pinned or locked build dependencies;
- record Python, build backend, operating system, and tool versions (and any bundled adapter's framework version, where applicable);
- avoid developer-global packages.

### Step 2 — Resolve release identity

- read the authoritative version source;
- verify the intended release type;
- validate archive and Python version mapping;
- reject stale or conflicting version references.

### Step 3 — Validate repository state

- validate structure;
- validate contracts;
- validate configuration schemas;
- compare public API with the previous approved release;
- classify all differences;
- validate history and review coverage.

### Step 4 — Run quality gates

- run static checks;
- run required tests;
- run LPDS-019 conformance;
- run required HIL or record the explicit approved status;
- build documentation and validate examples.

### Step 5 — Generate release content

- generate API reference documentation;
- generate API manifest;
- generate capability metadata;
- generate release manifest;
- generate SBOM;
- generate internal payload checksums;
- generate or refresh approved release reviews and summaries.

### Step 6 — Build installable artifacts

- build wheel;
- build source distribution;
- validate package metadata;
- inspect package contents;
- clean-install and smoke-test both artifacts.

### Step 7 — Build public ZIP

- stage the exact canonical project root;
- remove forbidden runtime and developer files;
- normalize file order and metadata where reproducible-build support exists;
- create one root folder only;
- create `<driver_name>_vYY.RR.zip`;
- extract to a clean directory and validate again.

### Step 8 — Generate detached artifact checksums

Generate hashes after all final public artifacts exist.

The detached checksum file should be named:

```text
<driver_name>_vYY.RR_SHA256SUMS.txt
```

It shall include at least the final ZIP, wheel, source distribution, and separately published evidence archive.

### Step 9 — Approval

- freeze final artifact hashes;
- complete release-readiness review;
- obtain release-authority approval;
- create the signed or protected source tag;
- ensure the tag identifies the approved source revision.

### Step 10 — Publish

- publish the GitHub release;
- upload final artifacts and detached checksums;
- publish release notes;
- publish or update GitHub Pages from the approved release source;
- publish wheel/source distribution to the approved package index when applicable;
- publish provenance/attestation when supported.

### Step 11 — Verify publication

- download artifacts from the public location;
- verify checksums;
- perform a minimal clean-install smoke test from the published artifact;
- verify documentation links and Pages version;
- record publication verification.

---

## 16. `build_release.py` requirements

`scripts/build_release.py` shall automate the release workflow or orchestrate equivalent tools.

It shall:

1. accept an explicit release mode: gate, candidate, or public;
2. read the authoritative version;
3. reject an invalid or already published identity;
4. validate repository structure;
5. validate version consistency;
6. validate LPDS-017 and capability metadata;
7. validate LPDS-019 inventory/vector synchronization;
8. run or invoke mandatory quality gates;
9. enforce test and coverage thresholds;
10. compare the public API against the previous approved release;
11. classify or reject unclassified API changes;
12. validate changelog, history, reviews, migration, and compatibility records;
13. generate API reference documentation, API manifest, release manifest, SBOM, and internal checksums;
14. build wheel and source distribution;
15. run clean-install smoke tests;
16. stage and build the correctly named ZIP;
17. verify exactly one stable top-level folder;
18. reject forbidden files, secrets, stale versions, and nested release archives;
19. extract and revalidate the final ZIP;
20. generate detached checksums after final artifacts are complete;
21. produce a machine-readable build summary;
22. exit non-zero when any mandatory requirement fails.

The script shall not publish unless publishing is an explicit separate action or explicitly enabled protected mode.

---

## 17. Release artifact set

### 17.1 Mandatory public artifacts

A public release shall provide, as applicable:

```text
<distribution_name>-<python_version>-py3-none-any.whl
<distribution_name>-<python_version>.tar.gz
<driver_name>_vYY.RR.zip
<driver_name>_vYY.RR_SHA256SUMS.txt
```

The wheel and source distribution are the primary installable Python package artifacts. The project ZIP is a complete-source bundle intended for offline/air-gapped distribution, evidence packaging, and archival; it may separately bundle any framework adapters shipped with the driver.

It shall additionally provide:

- release notes;
- source tag;
- GitHub Pages documentation;
- SBOM;
- release manifest;
- provenance/attestation when supported.

The SBOM and manifest may be included inside the ZIP and may also be published separately.

### 17.2 Main ZIP content

The main ZIP shall contain the complete GitHub-ready project under the stable root, including current:

- driver implementation;
- tests;
- conformance assets;
- any bundled adapters (e.g. pytest, CLI, REST), each kept in its own subdirectory with adapter-specific tests and examples;
- examples;
- scripts;
- guide;
- documentation source;
- README;
- AI contract;
- history;
- reviews;
- configuration examples;
- release manifest;
- SBOM;
- internal payload checksums.

Runtime outputs and private bench evidence shall not be included unless explicitly approved.

### 17.3 Internal checksum recursion rule

A checksum file cannot contain a stable hash of itself or of the outer ZIP that contains it.

Therefore:

- `release/SHA256SUMS` inside the project shall cover staged package payload files according to a documented exclusion rule;
- it shall exclude itself;
- it may exclude `release/release_manifest.json` if the manifest is generated after payload hashing, but the exclusion shall be explicit;
- the final outer ZIP, wheel, source distribution, and evidence archive shall be covered by the detached public checksum file generated after artifact creation.

### 17.4 Evidence archive

A separate evidence archive should contain:

- complete conformance-test outputs (including any adapter-level test outputs, e.g. a pytest adapter's JUnit XML and HTML report);
- test and coverage reports;
- LPDS-019 traces and matrices;
- HIL logs and device identity;
- build logs;
- environment records;
- final review exports;
- API diff;
- package inspection results;
- publication verification.

Secrets, private keys, credentials, and unapproved personal or laboratory identifiers shall be redacted.

---

## 18. Release manifest

### 18.1 Required file

Every public release shall contain:

```text
release/release_manifest.json
```

### 18.2 Required content

The manifest shall include equivalent information to:

```json
{
  "schema_version": "1.0",
  "document": "LPDS-011",
  "driver_name": "hp34401a",
  "release_kind": "public",
  "display_version": "26.01",
  "archive_version": "v26.01",
  "python_version": "26.1",
  "archive_name": "hp34401a_v26.01.zip",
  "internal_root": "hp34401a/",
  "source_revision": "<commit-or-source-id>",
  "source_tag": "hp34401a-v26.01",
  "build_timestamp_utc": "<ISO-8601>",
  "build_environment": {
    "python": "<version>",
    "operating_system": "<value>",
    "build_backend": "<value>",
    "adapters": {"pytest": "<version, if bundled>"}
  },
  "tests": {
    "unit": "PASS",
    "simulated_acceptance": "PASS",
    "integration": "PASS",
    "compatibility": "PASS",
    "lpds_019": "PASS",
    "hil": "PASS|NOT_REQUIRED|APPROVED_GAP"
  },
  "reviews": {
    "critical_open": 0,
    "major_open": 0,
    "release_readiness": "APPROVED"
  },
  "artifacts": [],
  "sbom": "release/sbom.spdx.json",
  "internal_checksums": "release/SHA256SUMS",
  "known_risks": "review/known_risks.md"
}
```

### 18.3 Manifest validation

The release build shall verify that:

- identity fields match the package;
- referenced files exist;
- test statuses match evidence;
- review counts match review records;
- HIL status is not overstated;
- the source revision matches the approved source;
- artifact names use the required pattern.

---

## 19. Software Bill of Materials (optional)

An SBOM (SPDX or CycloneDX, e.g. `release/sbom.spdx.json`) listing dependencies, versions, and licenses is genuinely useful once a release has consumers who need supply-chain guarantees. It's not expected by default — add it when someone actually needs it, and regenerate it from the release environment rather than an unrelated dev machine so it stays accurate.

---

## 20. Reproducibility and deterministic packaging

### 20.1 Deterministic inputs

The release shall use:

- identified source revision;
- pinned or constrained build tooling;
- declared Python compatibility;
- deterministic generated documentation inputs;
- stable dependency resolution or a recorded lock/environment;
- normalized release version.

### 20.2 ZIP determinism

Where supported, the ZIP builder should:

- sort files lexically;
- normalize path separators;
- normalize timestamps;
- normalize permission bits;
- exclude host-specific metadata;
- use a documented compression method and level.

### 20.3 Rebuild comparison

A release-candidate rebuild from identical source and declared environment should produce the same artifact hashes.

When hashes differ, the build report shall identify the cause or the release shall be treated as non-reproducible.

A non-reproducible release may be approved only with documented justification and complete provenance evidence.

---

## 21. Forbidden release content

The main driver ZIP shall not contain:

- `.venv/` or other virtual environments;
- `__pycache__/`, `.pyc`, test caches, lint caches, or coverage working files;
- IDE metadata unless specifically required and reviewed;
- local test-run output files (e.g. `output.xml`, `log.html`, `report.html`, or other adapter/framework-generated run artifacts) outside an intentionally published evidence package;
- personal paths or usernames;
- credentials, tokens, passwords, private keys, or `.env` files;
- private bench addresses or inventory;
- unreviewed hardware profiles;
- proprietary vendor installers or redistributables without explicit permission;
- active HIL lock files;
- temporary files;
- build staging directories;
- prior release ZIPs;
- another copy of the same project archive;
- unreviewed binary captures;
- stale generated documentation;
- source files not represented in review and history when materially changed.

The release build shall scan for forbidden content and fail on detection.

---

## 22. Clean-install validation

### 22.1 Wheel installation

The release shall be installed into a clean environment from the built wheel and shall pass:

- package import;
- driver class instantiation;
- API reference documentation generation;
- version query;
- capability discovery;
- simulator or replay smoke test;
- one representative plain-Python usage test (and, where an adapter is bundled, one representative adapter test).

### 22.2 Source-distribution installation

The same checks shall be performed from the source distribution.

### 22.3 ZIP project validation

The final ZIP shall be extracted to a clean path and validated using only documented package instructions.

Validation shall confirm:

- one stable root;
- setup scripts operate from documented shells;
- dependencies install;
- examples can be listed and selected;
- at least one offline example runs;
- documentation builds;
- no developer-local path is required.

### 22.4 Hardware dependency isolation

Import, installation, API reference documentation generation, and software-only examples shall not require physical hardware.

Optional vendor runtimes may be required only when the selected transport explicitly uses them, and this requirement shall be documented.

---

## 23. Review

Run the LPDS-010 checklist against the actual release candidate — the built artifact, not just the source — before publishing. Anything that could cause unsafe behavior, data corruption, or a silently wrong result should be fixed first; everything else can be noted and tracked. See LPDS-010 for the full checklist; there's no separate release-specific review bureaucracy layered on top of it here.

---

## 24. Git tag and GitHub release

### 24.1 Tag naming

The recommended tag is:

```text
<driver_name>-vYY.RR
```

Example:

```text
hp34401a-v26.01
```

A repository dedicated to one driver may use `vYY.RR` when that convention is documented and unambiguous.

### 24.2 Tag requirements

The final tag shall:

- point to the approved source revision;
- be protected or signed where supported;
- not be moved after publication;
- match the release manifest and notes.

### 24.3 GitHub release contents

The GitHub release shall include:

- exact release title and version;
- release notes;
- driver ZIP;
- wheel;
- source distribution;
- detached checksums;
- SBOM or link to SBOM;
- evidence archive or link where published;
- compatibility and migration links;
- hardware-validation status;
- known limitations;
- superseded or yanked release warning when applicable.

### 24.4 Draft and pre-release states

Release candidates shall be marked as pre-release.

Final release shall not be marked as pre-release and shall use only approved final artifacts.

---

## 25. GitHub Pages publication

### 25.1 Release consistency

GitHub Pages shall be built from reviewed source corresponding to the public release.

It shall display:

- current release version;
- supported devices and transports;
- installation instructions;
- quick start;
- current public API reference;
- configuration;
- examples;
- safety;
- compatibility;
- migration;
- hardware-validation status;
- troubleshooting;
- release notes and history.

### 25.2 Publication gate

A strict documentation build shall pass before deployment.

Stale API pages, broken links, mismatched version labels, or documentation that claims unexecuted HIL status shall block publication.

### 25.3 Post-publication verification

After deployment, verify:

- landing page version;
- API-reference version;
- navigation links;
- release-download link;
- migration and compatibility pages;
- absence of draft-only warnings or stale versions.

---

## 26. Publication order

The recommended order is:

1. approve final candidate and hashes;
2. create protected source tag;
3. publish GitHub release as draft;
4. upload artifacts;
5. verify uploaded hashes;
6. publish package-index artifacts where applicable;
7. publish GitHub Pages;
8. run public download/install verification;
9. publish the GitHub release;
10. record post-release verification.

A project may change the order for platform constraints, but it shall avoid exposing incomplete or inconsistent release components as final.

---

## 27. Post-release verification

Within the release workflow, the project shall verify the published artifacts rather than only local build outputs.

Required checks:

- download the public ZIP;
- verify detached checksum;
- verify one stable internal root;
- inspect version and manifest;
- clean-install wheel or source distribution from the public location when applicable;
- import the driver package (and, where bundled, its adapter);
- run one offline smoke test;
- verify GitHub Pages version and links;
- verify release notes and compatibility claims;
- record the result in release evidence.

A publication verification failure shall trigger correction, yanking, or supersession according to impact.

---

## 28. Hotfix process

A hotfix is a new public release and shall receive the next `vYY.RR`.

The process shall:

1. identify the affected release and defect;
2. reproduce the issue where practical;
3. add a regression test at the lowest effective layer;
4. correct the issue with minimal unrelated scope;
5. rerun all mandatory release gates;
6. update history, changelog, release notes, reviews, AI contract, protocol vectors, and documentation as applicable;
7. publish the new immutable release;
8. mark the previous release as superseded or yanked when necessary.

A hotfix ZIP shall not overwrite the original release ZIP.

---

## 29. Fixing a Bad Release

If a published release turns out to have a serious defect, don't delete it — deleting a release out from under anyone who already installed it is worse than leaving it up. Instead, mark it clearly on the GitHub release page (or PyPI, if published there) as having a known issue, say what the issue is, and point at the fixed release. GitHub's "pre-release" / release-notes editing covers this well enough for most projects; there's no separate formal rollback record needed.

Deleting a release outright should be rare — a genuinely exposed secret or a legal requirement, not "we don't like this version anymore."

---

## 30. Release retention and support status

The project shall define support states, at minimum:

- **Current** — recommended release;
- **Supported** — older release still receiving applicable fixes;
- **Maintenance only** — critical/security/safety fixes only;
- **End of support** — no further corrections planned;
- **Yanked** — retained but not recommended for new use.

The current status shall be documented in `docs/support_policy.md` and reflected on GitHub Pages.

Evidence retention shall follow project policy, but final release manifests, checksums, reviews, history, and source tags shall be retained for the supported lifetime of the product and preferably for the repository lifetime.

---

## 31. Basic Release Hygiene

A few things worth doing regardless of project size: don't commit release credentials or expose them in CI logs; scan release content for secrets before publishing; keep tags/release branches reasonably protected if your Git host supports it. Generating an SBOM, running formal provenance/attestation, and requiring a separate approval step for publication are things to add once a release process has real stakeholders depending on that level of assurance.

A secret that does slip into a published artifact is worth treating seriously regardless of scale: revoke the credential, yank or fix the release (§29), and note what happened in the CHANGELOG.

---

## 32. Checklist

**Identity**
- [ ] Archive is named `<driver_name>_vYY.RR.zip`, with exactly one internal root `<driver_name>/`.
- [ ] Version is consistent across the package, README, and AI contract (if published).

**Changes**
- [ ] `CHANGELOG.md` (or `history/`) is current and describes what changed.
- [ ] A breaking change (LPDS-011 §10) has migration guidance and a version bump.

**Code and tests**
- [ ] The package imports without hardware access or an automation framework.
- [ ] Tests pass; LPDS-019 conformance passes at least against the simulator.
- [ ] If published, the LPDS-017 contract and lock validate against the current API.

**Docs and build**
- [ ] README and examples match the release; examples actually run.
- [ ] Wheel/sdist build and install cleanly in a fresh environment.

**Publication**
- [ ] The Git tag points at the released commit; the GitHub release includes the built artifacts and notes.
- [ ] A quick post-publish sanity check (download, install, import) passes.

As throughout this standard: an unchecked box is something to note honestly (in the README, via the driver's status label — LPDS-001 §9), not something that requires a formal waiver to proceed past.

---

## 33. Goal

Provide a controlled, repeatable, and auditable path from reviewed LPDS driver source to an immutable public release whose identity, contents, compatibility, evidence, documentation, and integrity can be trusted.

---

## Appendix A — Version examples

### A.1 Gate progression

```text
Phase 1 Gate 1  -> example_v26.01.01.zip
Phase 1 Gate 2  -> example_v26.01.02.zip
Phase 1 Gate 3  -> example_v26.01.03.zip
Phase 1 Gate 4  -> example_v26.01.04.zip
Phase 1 Gate 5  -> example_v26.01.05.zip
```

### A.2 Public promotion

After Gate 5 approval:

```text
Engineering artifact: example_v26.01.05.zip
Public release:       example_v26.01.zip
Python package:       example-26.1-py3-none-any.whl
Internal root:        example/
```

The public package shall be regenerated under the public identity. The engineering ZIP shall not merely be renamed.

### A.3 Later public updates

```text
First public release in 2026:  example_v26.01.zip
Maintenance update:            example_v26.02.zip
Feature update:                example_v26.03.zip
First release in 2027:         example_v27.01.zip
```

### A.4 Hotfix

```text
Affected release:  example_v26.03.zip
Hotfix release:    example_v26.04.zip
```

---

## Appendix B — Minimum history template

```markdown
# History — vYY.RR

## Identity
- Driver:
- Release:
- Date:
- Source revision:
- Previous release:

## Objective

## Added

## Changed

## Deprecated

## Fixed

## Security

## Safety

## Removed

## Compatibility

## Packaging

## Public API impact

## AI contract and protocol-vector impact

## Tests and evidence

## Documentation and examples

## Migration

## Known limitations and residual risks

## Review references
```

---

## Appendix C — Changes in version 1.0

Initial LPDS-011 release defining:

- separate engineering-gate and public-release identities;
- canonical zero-padded public ZIP naming;
- stable version-independent internal root;
- version synchronization and immutability;
- change classification and compatibility policy;
- changelog, detailed history, and release-note requirements;
- release freeze and mandatory quality gates;
- deterministic build and clean-install validation;
- release manifest, SBOM, internal and detached checksums;
- GitHub release and GitHub Pages publication;
- hotfix, rollback, yanking, supersession, retention, and post-release verification.

### Deep trim to solo/small-team scale

Removed formal release-freeze governance, the 9-gate approval apparatus, mandatory SBOM/attestation, the 7-document review-record requirement, and the formal release-readiness verdict/approval taxonomy — downgraded to a single practical checklist (§32) plus a short "getting ready to publish" section (§12, §14). `vYY.RR` versioning, CHANGELOG discipline, and basic release hygiene are retained as the parts of this process genuinely worth following at any scale.
