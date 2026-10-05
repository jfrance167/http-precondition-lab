# Decisions

- Original stdlib pure model, not framework adoption: source references separate
  transport/response/file concerns but are broader than normalized teaching behavior.
  Werkzeug source is 3.2.0.dev, not a selected stable API. No fewer-dependencies safety claim.
- Normalized tags preserve empty/literal star/backslash/case, rather than reuse lossy
  wire parsing or tag truthiness. Non-ASCII scope limits never mask invalid ASCII/type data.
- Complete document validation before decisions; type/size/contradiction errors take
  priority over scope flags and early condition failure. No user label promotes authority.
- Baseline 1xx unsupported, not completed bypass. Normal-check status is a declared
  synthetic assumption, not authentication. Continue produces no success status.
- Trace priority frozen before code: global unknown/bypass, then absence, first-failure
  reachability, tag precedence, method restriction, missing metadata, actual comparison.
  Absence describes input, not an evaluation after failure.
- No already-applied exception, resource effects or 304 cache merge. Atomicity and
  appropriate validator generation remain requirements of real origins, not this lab.
- Reuse own MIT cache/CORS validation/report/output/verifier patterns with narrower
  bounds; no modification of older code/shared tooling. No repository creation under
  local-only approval. Independent hand-labelled fixtures precede model implementation.
