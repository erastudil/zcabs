# Security Policy

This repository provides protocol definitions, a local secret store, verification tooling, a secret leak scanner, and a command execution wrapper.

## Store Security & Secret Management

- The zcabs store contains cryptographically generated dynamic integers.
- Stores reside in `$ZCABS_HOME` or `~/.zcabs`, strictly outside repository worktrees.
- Never commit store files or pointer records to version control.
- Do not log `observe` outputs or active integers into training datasets or persistent log aggregators.
- `zcabs look` and `zcabs scan` outputs are safe to display. `zcabs observe` retrieves secret pairs; treat observed integers as sensitive verification credentials.

## Network Surface

This software does not open network listeners or run background network daemons.

If you deploy modified versions of this tooling as part of a network service, AGPL §13 requires providing corresponding source code to users. See [`COVENANT.md`](COVENANT.md).

## Reporting Vulnerabilities

Report security issues through the GitHub repository issue tracker or security advisory panel. This project does not offer a monetary bug bounty program.
