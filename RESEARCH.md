# HTTP precondition research

October 5, 2026. Recommendation: original standard-library normalized origin-decision
lab, with a trace and explicit assumptions, as specified in PLAN.md. No code/package
execution or actual origin/cache testing performed. Research is not a security audit.

## Local/vault reuse and distinct gap

Read completed HTTP-cache STATE/README/CONTRACT and source decision path; it proposes
conditional contact, does not evaluate weak tags or actual 304 responses. Existing CORS,
access-control and network-forensics documentation and targeted filename searches did
not reveal a matching precondition lab. This is a bounded reuse search, not exhaustive
inspection of every file. No new Graphify graph or remote indexing was generated.

Read selected-vault Home/Codex Integration, HTTP cache successor/completion records
and HTTP Idempotency and Retry Decisions.md. Narrow tag/precondition/range note searches
found no dedicated prior model. Retry ambiguity is already assigned elsewhere and is
not included. Previous lab limits remain intact; publication/manual review not implied.

## Primary standard findings

[RFC 9110](https://httpwg.org/specs/rfc9110.html) distinguishes strong and weak comparison,
tag and date conditions, and method-dependent outcomes. Preconditions follow normal
request checks; redirects/errors can take priority. Ordered evaluation prevents lower
priority dates from overriding tag conditions. Wildcards depend on current representation
existence. A matching retrieval condition can suggest 304; a failed modifying condition
can require 412. Already-applied success exceptions and range processing add context
that this proposal excludes. Range is optional and follows preconditions, which makes
it a distinct alternative rather than an automatic extension of this lab.

Reviewed sections: [comparison](https://httpwg.org/specs/rfc9110.html#entity.tag.comparison),
[If-Match](https://httpwg.org/specs/rfc9110.html#field.if-match),
[If-None-Match](https://httpwg.org/specs/rfc9110.html#field.if-none-match),
[evaluation](https://httpwg.org/specs/rfc9110.html#evaluation),
[precedence](https://httpwg.org/specs/rfc9110.html#precedence),
[ranges](https://httpwg.org/specs/rfc9110.html#range.requests).
The proposed profile and conservative choices are not full RFC conformance.

## Strongest candidate: Pallets Werkzeug

Connected GitHub inspection:
[Response.apply_conditions/apply_range](https://github.com/pallets/werkzeug/blob/main/src/werkzeug/wrappers/response.py),
[tag structures](https://github.com/pallets/werkzeug/blob/main/src/werkzeug/datastructures/etag.py),
[condition tests](https://github.com/pallets/werkzeug/blob/main/tests/test_apply_conditions.py),
[wrapper tests](https://github.com/pallets/werkzeug/blob/main/tests/test_wrappers.py),
[manifest](https://github.com/pallets/werkzeug/blob/main/pyproject.toml),
[license](https://github.com/pallets/werkzeug/blob/main/LICENSE.txt),
[changes](https://github.com/pallets/werkzeug/blob/main/CHANGES.rst) and
[CI definition](https://github.com/pallets/werkzeug/blob/main/.github/workflows/tests.yaml).
Per-file identities/limits: research/source-identities.json. These are mutable branch
reads, not a pinned tested distribution or whole-repository snapshot.

Actual response code accepts an exists flag, selects tag/date branches, raises on
failed guards and sets status 304 for retrieval conditions. Range processing is a
separate method. Tag helpers distinguish weak/strong sets and accept normalized ETag
objects. Their raw parser discards invalid items, and truthiness is tied to opaque
value; that is not adopted as the lab's strict normalized contract or independent oracle.
No claim that these observations constitute a validated vulnerability.

Actual condition tests cover weak request/current tags, missing ETag, star with true/
false existence, date equality/missing dates, POST differences and tag/date precedence.
No upstream test ran here. CI declares Python 3.11–3.15/free-threaded/PyPy and Windows/
macOS/Linux jobs, pinned actions, empty default permissions and nonpersistent checkout
credentials; actual job status was not checked. Test file fetch reported September 27,
2026 modification; CHANGES/issue activity provides maintenance evidence, not safety proof.

Inspected manifest is **3.2.0.dev**, Python >=3.11, runtime MarkupSafe >=3.0.3 with
optional watchdog. This unreleased API is a research reference, not a selected runtime.
BSD-3-Clause permits reuse subject to copyright/conditions/disclaimer retention and
non-endorsement obligations. No upstream source is copied into project implementation.

[Issue 3291](https://github.com/pallets/werkzeug/issues/3291) describes prior mixed
conditional/range logic problems and proposes separation. Inspected development source
has that separation. Search response did not supply definitive issue status or release
coverage; do not assert a released fix or independently confirmed exploitation.

## Alternate implementation reference: aiohttp

Read actual [FileResponse](https://github.com/aio-libs/aiohttp/blob/master/aiohttp/web_fileresponse.py),
[manifest](https://github.com/aio-libs/aiohttp/blob/master/pyproject.toml) and
[license](https://github.com/aio-libs/aiohttp/blob/master/LICENSE.txt).
Its file pipeline gets filesystem metadata, checks conditional fields and then performs
file/encoding/range/send operations. The code illustrates why snapshot comparison,
representation selection and response sending have separate responsibilities; no file
or transport behavior was executed. It is too broad for this normalized model.

Manifest: Python >=3.10, dynamic version; dependencies include aiohappyeyeballs, aiosignal,
frozenlist, multidict, propcache and yarl, with version-conditional async-timeout and
typing_extensions. Declared license Apache-2.0 AND MIT includes a vendored llhttp license;
adoption would require checking the exact copied component and notices. No adoption or
install proposed. A guessed test path returned 404 and changelog retrieval failed, so
this comparison does not claim verified test/maintenance/CI coverage. Strongest-candidate
tests and maintenance were successfully inspected instead. No advisory audit performed.

## Candidate selection and access limits

Build, not fork/adopt: preserve a pure trace over declared snapshots without a WSGI or
async transport framework. Deferred range alternative would model byte intervals and
optional server choices; it would add encoded-length/If-Range/multipart complexity.
The precondition model supplies the clearer successor gap under current constraints.

Connected GitHub worked for actual source/manifest/license/change/CI and public-directory
reads; repository search and some file reads failed at transport. Public GitHub fetch
recovered condition tests/tag source after dedicated fetch failures. RFC-editor initial
read failed; official HTTPWG-hosted RFC text succeeded. Raw GitHub web test URL also
failed. No missing retrieval is counted as absence of source or as a passing check.
Firecrawl account access previously failed; available primary-source web access used.
No upstream execution, dependency/Scorecard/advisory audit, live protocol conformance,
full candidate security certification or paid tool/model call.

## Local-first drafting

Existing Ollama helper on loopback: qwen3.5:2b, 770 ms, 56 output tokens, stop completion.
Raw brief/output/metadata preserved. Two supplied definitions accepted; ambiguous strong
comparison wording corrected against the standard. No local result grants authority or
validates the design. Codex retained interpretation/security/source review; complex
security work is unsuitable for the limited worker. No remote fallback or spending.
