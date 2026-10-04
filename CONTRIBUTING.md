# Contributing

Contributions are welcome. All contributions must preserve the project's copyleft integrity and pass test suites.

## Licensing and Developer Certificate of Origin

All contributions are licensed under **AGPL-3.0-or-later**. By submitting a patch, you certify that you have the right to submit the work under this license.

Every commit must include a Developer Certificate of Origin sign-off line:

```text
Signed-off-by: Your Name <your.email@example.com>
```

Copyright remains with the individual authors. No Contributor License Agreements requiring copyright assignment are accepted. Pull requests proposing proprietary relicensing or commercial exemptions are rejected.

## Testing & Verification

Every proposed change to the protocol or tooling must include automated tests:

```bash
# Unit test suite
python -m unittest discover -s tests -v

# Protocol conformance check
PYTHONPATH=src python -m zcabs check

# Repository leak scan
PYTHONPATH=src python -m zcabs scan .

# JavaScript test suite
node --test js/zcabs.test.js
```

Key invariants:
- `zcabs look` must never output the target integer.
- `zcabs mint` must generate cryptographically random, unique 6-digit integers.
- `zcabs scan` must catch uncommitted stores, pointer files, and leaked live integers.
- `zcabs verify` must fail closed and never echo expected integers in failure messages.
- Never commit live integers or static capability tables to the repository.

## Documentation Style

- **Greene/Feynman order**: Explain the intuitive mechanics in plain English first, then define the technical terms.
- **Specification**: Keep `docs/SPEC.md` concise, normative, and dry.
- **Scope**: Keep changes strictly within the boundaries defined in [`docs/BOUNDARY.md`](docs/BOUNDARY.md).
