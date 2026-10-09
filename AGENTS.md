---
title: "zcabs — execution genome"
summary: "zero-cost cryptographic authentication bearer protocol, dynamic token generation, and verification gate."
version: "2.0.0"
layer: genome
home: zcabs/AGENTS.md
dialect: progen syntax
status: canon
---

# zcabs

scope : public zero-cost cryptographic authentication bearer protocol and tooling at C:\Users\jpm05\Documents\zcabs.

normative standard : docs/SPEC.md.

license : AGPL-3.0-or-later; copyright retained by original authors.


## protocol invariants

dynamic generation : all store integers generated dynamically at mint time; committing static numbers or golden tables strictly forbidden.

leak prevention : zcabs look stdout never prints target integers.

boundary contract : docs/BOUNDARY.md defines distribution boundaries.

license preservation : all patches maintain AGPL-3.0-or-later license.


## verification and ponytail doctrine

verification command : python -m zcabs check.

exit condition : gate exits 0 only when all cryptographic validations pass.

ponytail wu wei : pull token verification into single-grip deterministic runner python -m zcabs check; reject sprawling test catalogs.

zero fake tests : verify against real cryptographic hashing and bearer token generation without synthetic mocks.

zero stubs : stubs and placeholders paired with completion claims strictly prohibited.
