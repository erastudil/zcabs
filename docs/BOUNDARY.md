# Boundary

This repository defines the zcabs protocol and provides reference tooling for anti-hallucination execution proofs. This document defines what belongs in this repository and what remains strictly out of scope.

## In Scope

| Area | Included Components |
|---|---|
| **Protocol** | Normative specification for `LOOK:`, `FORMAT:`, pair files, dynamic integer generation, decoy generation, and rotation. |
| **Verification** | Fail-closed transcript verification and post-execution command wrapping (`zcabs wrap`). |
| **Leak Prevention** | Static tree scanner (`zcabs scan`) checking for store directories, pointer files, and active integers. |
| **Agent Prompting** | Drop-in reference system prompts (`prompts/genome.md`) teaching observation and format compliance. |
| **Tooling & Ports** | Python CLI reference suite, JavaScript runtime module (`js/zcabs.js`), and GitHub Actions workflow (`action/action.yml`). |
| **Licensing** | AGPL-3.0-or-later governance and copyleft covenants (`COVENANT.md`). |

[`docs/SPEC.md`](SPEC.md) is the normative specification. Tooling conforms to the specification and fails closed on discrepancy.

## Out of Scope

The following concerns belong to external platforms, runtimes, and host applications, and must remain out of this repository:

- **OS Virtualization & Jails**: `zcabs` verifies observations; it does not replace operating system sandboxes, process isolation, chroots, or container virtualization.
- **Daemon & Network Services**: `zcabs` is designed as a local filesystem protocol and CLI utility. It does not run network listeners or host remote execution daemons.
- **Test Runner Re-implementation**: `zcabs wrap` wraps existing test frameworks (pytest, unittest, npm test, cargo test); it does not implement test runners or reporters.
- **Static Capability Registries**: All capability and identity integers are generated dynamically at mint time. No static integer registries or persistent capability keys belong in source code or documentation.
- **Model Training & Fine-Tuning**: No training scripts, dataset pipelines, or model adapters belong in this codebase.

Pull requests that introduce out-of-scope abstractions or project-specific dependencies will be rejected.

## Self-Contained Implementation

An implementer working solely from this repository has everything necessary to mint stores, generate decoys, wrap command runs, verify transcripts, and scan codebases for leaks. All normative references in `docs/SPEC.md` point exclusively to files contained in this repository.
