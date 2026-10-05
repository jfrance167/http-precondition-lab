# ECC actual-code self-review

October 5, 2026. Installed ecc-code-review and pinned checklist applied to actual
preconditionlab/, tests/test_lab.py, tools/verify.py, fixtures, contract, callers and
verification evidence. Implementing-agent self-review; no independent reviewer or
full native ECC runtime installation claimed.

Reviewed correctness (strong/weak/existence/precedence/baseline/trace), complete validation,
error paths, bounds, inert output, file-write semantics, fixed subprocess boundaries,
dependency scope and meaningful tests. Case-sensitive methods and ASCII-invalid versus
Unicode-unsupported behavior match the approved addendum. No application assertions
serve as guards. No unresolved actionable application defect found.

The actual closed-pipe check found a test newline expectation mismatch (Windows CRLF),
not an application exit-code defect. Corrected test normalization and added four size
variants; affected normal/optimized checks pass. No unnecessary production change.
Reused verifier requires frozen-label assertions and failure-only summary, and restored
source; actual three mutants meet those criteria.

Five narrow Bandit exclusions: B404/B603 in verifier and B404/two B603 calls in tests.
Commands select the fixed installed interpreter and own module/checks, with test-owned
file arguments and shell disabled. Case data never selects commands. One duplicate-visit
nosec warning retained in scanner output. No application suppression or broad rule exclusion.

| Severity | Outstanding count | Status |
|---|---:|---|
| Critical | 0 | no finding |
| High | 0 | no finding |
| Medium | 0 | no finding |
| Low | 0 | no finding |

Verdict: approved local scope complete, subject to Jake's manual boundary review.
No merge/deployment/publication approval follows. Dedicated secret/history/advisory
audit, hostile-filesystem isolation and live/hosted/other-runtime behavior unverified.
