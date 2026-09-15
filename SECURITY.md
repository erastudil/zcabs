# security

this repository is a protocol, a local store, a verifier, a leak scanner, and a command wrapper.

the store holds generated integers. it lives in `$ZCABS_HOME` or `~/.zcabs`. do not commit it. do not log `observe` output into training data.

`look` and `scan` are safe to print. `observe` is retrieval. treat its output as secret.

this software does not listen on a network port.

if you host a modified copy of the tooling as a network service, AGPL §13 requires you to offer corresponding source to the users of that service. `COVENANT.md`.

report issues on the github tracker. no bounty program.
