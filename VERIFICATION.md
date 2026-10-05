# Verification

Final authoritative receipt: reports/verification-reviewed/results.json and adjacent
stdout/stderr logs. Reproduce: python tools/verify.py --output reports/new-verification.
Output must be fresh and under this project. Windows CPython 3.13.7, installed Bandit
1.9.4; no package/framework/model install or remote call.

| Check | Actual outcome |
|---|---|
| Normal tests | 25 pass |
| Optimized tests and optimized CLI children | 25 pass |
| Compileall | pass |
| Bandit application/tests/verifier | zero findings and scan errors |
| Strong-as-weak mutation | 3 fixture assertion failures, detected |
| Ignore If-Match date precedence | 1 fixture assertion failure, detected |
| Ignore If-None-Match date precedence | 2 assertion failures, detected |
| Restoration/final tests | exact original bytes restored; 25 pass |
| JSON/Markdown demos | 32 records each, exit 2 as expected |

Frozen cases: 28 supported/four unsupported. Receipt records ten source/fixture/contract
hashes; frozen contract/case/expected bytes checked by tests. Earlier reports/verification
remains as prior passing evidence before closed-pipe size expansion; latest receipt covers
the expanded test. Original LF-only closed-pipe expectation failed in a one-off test
run; correction and exact observed cause are documented in LEARNING/REVIEW.

Tests cover all strong/weak flag pairs, empty/literal-star/backslash data, tag versus
existence, trace priority, date equality, 1xx/412 exclusions, method/context gating,
complete invalid-over-unsupported validation, duplicate/schema/type/Unicode/byte/depth/
node/tag limits, custom-object rejection, report-text escaping, exclusive output/input
aliases, short/flush/close/cleanup failures, actual closed stdout and static capability
restrictions. Actual closed-pipe test at four sizes allows completed submission before
reader closure, otherwise requires failure exit 1 with fixed metadata. Output cap tested
at a reporter seam; no claim valid inputs necessarily reach the defensive cap.

Five narrow B404/B603 test/verifier exclusions documented in REVIEW; no application
suppression. AST restrictions are limited static checks, not proof of all possible safety.
Relevant source/synthetic fixtures manually reviewed for accidental sensitive data without
printing secrets. No dedicated secret scanner/history audit or separate repository.

No actual HTTP/origin/browser/resource update/cache merge, upstream test execution,
independent audit, Linux/other-runtime or hosted CI/CodeQL evidence. Manual consequential
boundary review remains pending. Normal exceptions restore mutations; forced process
termination cannot guarantee finally execution, so check hashes after interruptions.
