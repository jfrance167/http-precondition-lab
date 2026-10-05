# Security boundaries

Use invented normalized snapshots, not real accounts, tokens, headers or bodies.
No output grants authorization, proves a method succeeded or establishes actual
origin/cache behavior. The model never reads or changes a selected HTTP resource.

Whole-document validation precedes scope/baseline/first-failure decisions: malformed
later cases cannot hide behind unsupported features or early false conditions.
Exact types, duplicate detection, byte/depth/node/tag/numeric bounds and inert complete
reports are reviewed. No executable commands/imports/paths come from case content.

Only exported parse/evaluate are untrusted-input entry points. Reporter/file helpers
consume evaluated output and caller-selected trusted paths. A malicious host process
can bypass or monkeypatch Python code; no OS isolation or hostile filesystem-race
guarantee. File size is bounded, but a trusted caller's special file could block reads.
Stdout can be partial; fresh-file cleanup can fail and is reported.

The local verifier temporarily changes only this project's model.py and restores it
in finally for normal exceptions. Abrupt process termination can prevent restoration;
check receipt/source hashes after interruption. Mutations count only fixture assertion
failures with a failure-only unittest summary, never a crash/import error. No upstream
framework is installed or executed.

Manual review is required before any deployment/merge; neither is authorized here.
Record prospective issues with a minimal synthetic reproducer and affected contract
or source location. Do not attach private content or automatically message/publish.
