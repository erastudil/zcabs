# Covenant

**License:** AGPL-3.0-or-later. See [`LICENSE`](LICENSE).

This repository is dedicated to free, un-enclosed developer tooling. The project operates under the following standing covenants:

- The official distribution remains free ($0) forever.
- No corporate board seats or corporate governance steering this repository.
- Copyright remains with the respective authors under the Developer Certificate of Origin (DCO). The project does not accept Contributor License Agreements (CLAs) requiring copyright assignment.
- An independent, clean-room implementation based on [`docs/SPEC.md`](docs/SPEC.md) belongs entirely to its author.
- Incorporating this specification, prompts, or reference implementations into derivative works is governed by the AGPL-3.0-or-later.
- Any network service deploying modified versions of these covered works must provide corresponding source code to users under AGPL §13.

## Copyleft Scope

The protocol itself consists of machine-readable headers and key-value pair files. A model or agent emitting `the banana number is 123456` after inspecting a file is performing standard protocol communication and does not create a derivative work.

The files in this repository constitute the Program. The markdown specifications, reference prompts, Python package, JavaScript module, and test suites are covered works under the license.

If you deploy modified versions of `prompts/genome.md`, the verifier, or the wrapper as part of an externally facing network service, you are conveying a covered work. You must make the corresponding source code available to the users of that service under AGPL §13.

Dual-licensing schemes (e.g. commercial exceptions) and proprietary license re-assignments are rejected.

## Technical Independence

[`docs/BOUNDARY.md`](docs/BOUNDARY.md) establishes the scope of this repository. The specification is self-contained. Tooling and protocol features must be verifiable using only the code and documentation in this repository.
