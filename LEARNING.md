# Learning

Strong comparison requires both non-weak tags and equal opaque values. Weak comparison
only compares opaque values. Empty opaque is a valid present value in this normalized
profile; missing current tag cannot match a list. Wildcard selection uses supplied
representation existence instead of validator presence.

Preconditions are ordered, not a conjunction evaluated indiscriminately. Tags suppress
their date alternatives; a failed earlier guard prevents later evaluation. Retrieval
and modification differ: the same If-None-Match failure suggests 304 versus 412.
A trace must not label ignored/not-reached conditions as passing.

Snapshot assumptions are not an atomic read/check/write transaction. A continue result
does not grant permission or prove a change. Likewise an origin 304 suggestion does
not update a cached entry or prove that a real origin performed validation.

Independent fixture mutations caught weaker strong comparison and loss of both tag/date
precedence checks. A failure must be a fixture assertion, not merely a crashed test run.
Model bytes were restored before declaring success.

Practical test correction: Windows stderr uses CRLF, so the initial closed-pipe assertion
with literal LF failed despite correct exit 1. Normalize only the test's line endings;
no application fix was needed. Four buffering sizes now exercise both completed writes
before closure and actual I/O failure. A closed consumer does not guarantee the writer
observed an error if it had already submitted its entire output.
