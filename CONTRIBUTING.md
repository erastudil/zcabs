# contributing

patches keep the gift intact.

## license

AGPL-3.0-or-later. you certify the patch is yours to give under that license.

Developer Certificate of Origin. append to each commit message:

```
Signed-off-by: Name <email>
```

No CLA. copyright stays with the authors. the project does not take assignment.

PRs that relicense, dual-license, or add a company CLA are rejected.

## tests

```
python -m unittest discover -s tests -v
PYTHONPATH=src python -m zcabs check
PYTHONPATH=src python -m zcabs scan .
node --test js/zcabs.test.js
```

SPEC changes need a test. look must not print the integer. mint must generate. scan must catch a planted leak.

## voice

README teaches in ordinary english first, then names the term. SPEC is dry.

do not dump house life into this tree. `docs/BOUNDARY.md`.
do not bake capability integers into source.
