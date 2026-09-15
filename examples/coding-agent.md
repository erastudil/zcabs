# coding agent

Mint outside the repo. Inject the genome. Wrap the command whose success you need. Verify the transcript.

```
zcabs mint
```

System prompt: output of `zcabs prompt`, plus your tools.

When the agent claims tests:

```
zcabs wrap -- pytest -q
```

Append the printed LOOK/FORMAT to the agent. The agent reads LOOK or runs `zcabs observe canary` and speaks `the canary number is <integer>`.

```
zcabs verify transcript.txt --key canary
```

Exit 0 is proof. A sentence is not.
