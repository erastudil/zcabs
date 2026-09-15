# wrap

```
zcabs mint
zcabs wrap -- pytest -q
zcabs wrap -- npm test
zcabs wrap -- python -m unittest discover -s tests -v
```

Failure: wrap returns the command's exit code and prints no LOOK.

Success: stdout ends with:

```
LOOK: <absolute path>
FORMAT: the {string} number is {integer}
```

Verify that block's retrieval, not a paraphrase:

```
zcabs observe canary
zcabs verify transcript.txt --key canary
```
