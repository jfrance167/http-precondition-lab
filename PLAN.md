# HTTP precondition lab — research plan

October 5, 2026. Stages 2–4 approved by coordinator under Jake's directly verified
delegation; SUCCESSORS.md 02:25 approval. Local scope only.
Tier 3 bounded portfolio learning lab. Canonical plan requested at this root path;
ordered task list in tasks/todo.md. Evidence and retrieval limits: RESEARCH.md.

## Problem, gap and success

Teach a hypothetical origin's precondition reasoning: strong/weak tag comparisons,
declared representation existence, method-specific outcomes and evaluation order.
The previous cache lab only proposes conditional contact; this project would explain
one restricted origin decision after contact, without integrating the two applications.
Success: at least 28 independent frozen cases, complete bounded validation, explicit
traces showing evaluated/ignored/not-reached conditions, and reproducible offline evidence.
No response is sent, cached or merged and no resource is read or changed.

## Scope and proposed input contract

Original Python standard-library library plus local file CLI. Versioned normalized
JSON rather than raw HTTP. A document has version=1 and 1–32 cases. Each case has
id, method, baseline_status, representation, conditions, unsupported_features.
Representation: exists (exact bool), etag (null or normalized tag), last_modified
(null or nonnegative synthetic integer seconds). A tag has opaque and weak (bool).
Opaque values use ASCII 0x21 or 0x23–0x7e, at most 128 characters, including empty;
no unquoting, backslash escape conversion, hashing or case folding. Unicode/obs-text
tag values outside this profile are unsupported after common bounded text validation.
Do not use an empty tag's truthiness as evidence that no tag exists.

Conditions have exactly if_match, if_unmodified_since, if_none_match,
if_modified_since. Date conditions are null or synthetic integer seconds on the same
declared timeline. Tag conditions are null (absent) or {star: bool, tags: list}.
Star true requires empty tags; star false requires 1–16 tags. Duplicate identical
normalized tags are rejected by this profile; strong and weak versions of the same
opaque value are distinct list entries. A tag whose opaque value is '*' remains a
tag, not the wildcard selector. Raw empty headers/list syntax are not accepted or
interpreted; normalized presence and absence must remain distinct.

GET, HEAD, PUT and DELETE are the supported methods. Other syntactically bounded
method tokens are unsupported. Snapshot existence/metadata are supplied teaching
assumptions, not facts established by an HTTP request or caller's trusted role.
An absent representation cannot also carry an ETag or last-modified value: invalid
snapshot. Existing representations may lack either or both validators.

baseline_status is a caller-declared hypothetical result of normal request checks
before condition evaluation, exact integer 100–599. Supported evaluation combinations:
GET/HEAD with 200 and exists=true; PUT with 201 and exists=false, or 200/204 with
exists=true; DELETE with 200/204 and exists=true. Other 2xx combinations and baseline
412 are explicitly unsupported in this subset. Other baseline status classes bypass
the conditional algorithm, reporting the supplied status as hypothetical baseline
rather than fabricating a 304/412. Baseline checks are not authentication enforcement.

unsupported_features is a bounded list (0–8 unique visible ASCII identifiers, <=32
characters each) declaring out-of-scope context. Any nonempty list returns UNSUPPORTED
after every common schema/type/resource check. Examples: range, if-range, auth-context,
already-applied, custom-precondition, intermediary, negotiated-selection, clock-unknown.
Unknown object fields and conflicting shapes are invalid. An unsupported first case
or early failing condition must not hide malformed later data.

## Proposed behavior and honest result meanings

After validation and scope/baseline gating, evaluate the selected tag/date branches
in the documented precedence. If-Match uses strong comparison; If-None-Match uses
weak comparison. Wildcards use declared existence, not presence of an ETag. Present
tag conditions suppress their corresponding date alternatives, including when the
tag list does not match. Missing last-modified ignores a date condition. Modification
dates are already normalized; no HTTP-date parser or clock synchronization is claimed.

The model chooses the conservative 412 outcome for failed modification guards;
it does not implement an already-applied success exception. An If-None-Match failure
suggests 304 for GET/HEAD and 412 for PUT/DELETE. If-Modified-Since affects GET/HEAD
only. Failed earlier checks prevent later condition evaluation. Otherwise continue
normal processing; do not infer that a modification succeeded or was authorized.

Proposed result fields: id, status (SUPPORTED/UNSUPPORTED), baseline_status,
evaluation_applicable (bool or null), outcome (CONTINUE_NORMAL_PROCESSING,
NOT_MODIFIED, PRECONDITION_FAILED, BYPASS_PRECONDITIONS, UNSUPPORTED),
suggested_status (304/412/supplied bypass status, otherwise null), reason_codes,
trace and assumptions. Each of the four trace entries identifies the condition and
one state: ABSENT, PASS, FAIL, IGNORED_PRECEDENCE, IGNORED_METHOD,
IGNORED_NO_LAST_MODIFIED, NOT_REACHED, BYPASSED_BASELINE, UNKNOWN_SCOPE.
Freeze exact priority between trace annotations before code; a condition never both
passes and fails. Unsupported outputs have unknown applicability/status suggestion;
no continue/deny decision is guessed. A continue result has no claimed success code.

No 'safe', 'authorized', 'mutation occurred', 'cache updated' or 'protected against
lost updates' verdict. A 304 suggestion is only origin-side metadata reasoning; it
does not simulate an actual 304 response, successful cache revalidation or merging.

## Architecture, reuse and alternatives

Pipeline: byte/syntax limits -> complete contract validation -> immutable normalized
snapshot -> pure tag comparison/evaluation trace -> bounded inert JSON/Markdown.
Reuse reviewed strict JSON, report escaping and exclusive-file patterns from Jake's
HTTP-cache/CORS labs after checking the smaller limits. Preserve their source/evidence;
no shared helper rewrites or cross-project code edits. Record attribution for any
copied own MIT code. Standard library suffices; no dependency install, server or API.

Werkzeug's development source and tests are valuable references for separation of
preconditions/ranges and strong/weak helpers. Its WSGI response mutations and parsing
profile exceed this lab; the inspected version is 3.2.0.dev, not a promised released
API. aiohttp's file response adds transport, filesystem, content-coding and range
handling. Neither is adopted. Fewer dependencies are not a security certification.

Alternate: a single-byte-range interval model over a declared encoded length could
teach inclusive endpoints, suffix/open ranges and unsatisfiable versus invalid input.
That adds Range/If-Range and optional server choices; it is deferred to preserve a
clearer precondition learning gap. Retry/idempotency belongs to another workstream.

## Threat model, resource/error boundaries

Assets: host files, report integrity, bounded resources and truthful teaching claims.
Adversary controls all input bytes, nested values and case identifiers. Trusted parts:
reviewed code, fixed contract and independently labelled oracle. CLI-selected paths
and host process are trusted; normalized state remains an explicit synthetic assumption.

Proposed bounds: 64 KiB UTF-8 input; JSON depth 8; 5000 nodes; 32 cases; 16 tags per
condition; opaque 128, ID 64, other text 256 characters; integer tokens <=10 digits,
values 0–1e9. Exact bool/int and built-in dict/list/string checks, duplicate keys/IDs,
invalid Unicode, C0/DEL controls, unknown fields and contradictory snapshots reject
the whole document. Concrete API containers only; no custom-object coercion/generators.
No silent truncation. Clock and raw-header errors are excluded rather than guessed.

Bound fully encoded output to 256 KiB before writing. If that cap is unreachable
under tighter input limits, test its guard at an explicit reporter seam, not by
inventing a reachable end-to-end overflow. Escape every user-derived report field,
including IDs and tag punctuation. Do not report raw request headers or bodies.

Output only to stdout or an exclusively created fresh file. Reject input aliases and
existing destinations. Validate/compute/encode before writing; short write, flush and
close errors must report failure; cleanup only own newly created output, reporting
cleanup failure. No atomic stdout, hostile filesystem-race or hard OS memory guarantee.
Proposed exit 0 all cases supported (including 304/412/bypass outcomes), 2 any unsupported,
1 invalid data or I/O failure; argument-syntax exit 2 is separately documented.

## Stages and verification

1. Research/plan (completed): candidate comparison and source records; present this
   concrete plan and await coordinator approval before any implementation code.
2. Freeze exact contract/oracle: decide trace priority and output fields; at least
   28 independently labelled cases including empty opaque tags, wildcard/existence,
   missing validators, strong/weak combinations, GET/HEAD versus PUT/DELETE, date
   equality, tag/date suppression, first-failure precedence, baseline bypass and
   invalid/unsupported precedence. Retain fixture bytes and hashes before model code.
3. Thin library/CLI: implement validation plus pure reasoning; reports expose declared
   assumptions and every trace field. No networking, file-body reads or resource changes.
4. Verification/docs: normal and optimized tests/CLI children, compilation, existing
   Bandit, capability/source review and ECC actual-code self-review with fixes/tests.
   Mutate strong comparison into weak and reorder/ignore precedence; independent
   fixture assertions must catch each, not merely crash. Restore exact bytes and pass
   tests afterward. Test bounded API, malformed unsupported payloads and output errors.
   Save runtime/source hashes, README/security model/license/AI disclosure, STATE,
   DECISIONS, LEARNING and a verified Obsidian milestone. No unverified results claimed.

Completion is local educational scope only. Manual boundary review remains required
before merge/deployment. No new repository/publication/hosted CI changes authorized.
Preserve prior labs and parent Git. No new chat/scheduler/subagent or return-message loop.

## Local-first worker record

Existing loopback Ollama qwen3.5:2b extracted three supplied definitions in 770 ms,
56 output tokens, with original brief/output/metadata retained under research/.
Weak comparison and origin/cache separation wording accepted. Strong-comparison
sentence ambiguously said 'both the tag'; corrected to BOTH tags non-weak plus equal
opaque values after RFC verification. No raw draft is treated as security evidence.
Complex schema/security judgment remains in Codex; no remote/paid drafting or new service.

## Approved addendum — October 5 02:25

1xx baselines are unsupported, never completed bypass. Freeze trace annotation priority,
case-sensitive methods, invalid ASCII opaque characters versus non-ASCII unsupported.
Empty/literal-star tags, wildcard and existence remain distinct. Common validation of
every case/tag precedes scope/baseline/first-failure decisions. Preserve declared
method/status/existence combinations; no inferred authorization or success. Follow
>=28-case independent freeze, comparison/precedence mutations, normal/optimized/output/
SAST/ECC/docs/vault checks. No live behavior, cache merging, framework installation,
repository creation, publication, merge, new chat/scheduler/subagent or return loop.
