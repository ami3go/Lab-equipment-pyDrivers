# LPDS-020 — Driver Implementation Lifecycle

**Version:** 1.2
**Document ID:** LPDS-020
**Status:** Project requirement
**Applies to:** All LPDS Python instrument driver projects

---

## Purpose

This document describes a phase-and-gate shape for driver development: breaking work into **Phases**, each divided into **Gates**, so that a delivery stays small enough to build, test, and review in one sitting rather than accumulating into one enormous unreviewable change. It's a useful pacing tool for a solo developer as much as for a team — there's no assumption here that different gates need different people.

## Normative References

- LPDS-005 — Driver Package Specification
- LPDS-009 — Testing Standard
- LPDS-010 — Driver Review Checklist
- LPDS-011 — Release Process
- LPDS-017 — AI Driver Contract Specification

---

## Project Structure

A project is divided into sequential **Phases**. Each Phase moves through **five Gates**:

```text
Phase N
├── Gate 1 – Architecture & Skeleton
├── Gate 2 – Core Implementation
├── Gate 3 – Extended Features
├── Gate 4 – Tests & Documentation
└── Gate 5 – Review & Release
```

A gate should be reasonably complete before starting the next one — the point is avoiding a giant, hard-to-review pile of unrelated changes, not enforcing a formal sign-off chain.

---

## Gate 1 — Architecture & Skeleton

Build the folder structure, base classes, data models, and a buildable (if incomplete) package. Done when: the package builds, coding standards are followed, and the architecture is documented well enough that Gate 2 can build on it without guessing.

## Gate 2 — Core Implementation

Implement the primary functionality: core logic, public API methods, error handling, and a couple of initial examples. Done when: the main functionality works, the public API follows LPDS-002, and unit tests cover what's implemented.

## Gate 3 — Extended Features

Fill in the rest of the phase's scope: edge cases, remaining features, configuration, AI contract updates. Done when: the phase's declared scope is feature-complete, the API stayed backward compatible (or a breaking change was deliberate and documented), and docs reflect the new behavior.

## Gate 4 — Tests & Documentation

Round out tests, examples, and documentation: integration tests, usage examples (plain Python, plus adapter examples if any adapter exists), API docs, and an updated README. Done when: tests pass and examples actually run — against real hardware where you have it, against the simulator otherwise.

## Gate 5 — Review & Release

Run the LPDS-010 checklist against the phase's output, fix what it turns up, update the changelog, and package the release. Done when: nothing safety- or correctness-critical remains open (LPDS-010), and the phase's changes are reflected in history/changelog, examples, tests, and the AI Driver Contract if one is published.

---

## Versioning

Internally, it can help to tag each gate's output with a pre-release identifier distinguishing it from the public release:

```text
Phase 1: v26.01.01 (Gate 1) ... v26.01.05 (Gate 5)
Phase 2: v26.02.01 ... v26.02.05
```

This `vYY.PP.GG` form (year, phase, gate) is purely an internal convenience for tracking your own progress — most solo projects won't bother publishing anything until a phase's Gate 5 is done, at which point the release uses LPDS-011 §5.2's public `vYY.RR` format (e.g. `v26.01`), not the internal gate form.

---

## Note on Adapters

The gates above are about the driver itself. If a phase also delivers one or more adapters (pytest, CLI, REST, etc.), adapter work follows its own, much lighter pass: an adapter has no device logic to gate through five stages — it just needs an implementation-and-translation-verification check against the driver's already-approved public API.

---

## Why Bother

Breaking work into phases and gates keeps each delivery small enough to actually review, keeps tests and docs from falling behind the code, and makes it easier to pick the work back up (or hand it to an AI coding assistant) without having to reconstruct a huge pile of context first. It's a pacing tool, not a compliance process — use as much or as little formality around it as your project's actual size calls for.
