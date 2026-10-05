# Frozen precondition teaching contract v1

October 5, 2026. Frozen before application code. root {version:1,cases:[1..32]}.
case exactly: id,method,baseline_status,representation,conditions,unsupported_features.
id unique 1–64 Unicode scalar chars, no C0/DEL. Method: case-sensitive ASCII token,
1–16 chars, supported GET/HEAD/PUT/DELETE only. No uppercasing.
representation exactly exists (bool), etag (null/tag), last_modified (null/int).
Absent representation must have both metadata fields null (invalid otherwise).
Existing representation may have no validator. All integers exact int 0..1e9;
baseline_status separately 100..599. Dates normalized synthetic seconds; no date parser.

tag exactly opaque (0–128 chars) and weak (bool). Empty opaque is present. ASCII
allowed 0x21 and 0x23..0x7e, so quote, space, C0/DEL invalid. Backslash and case remain
literal. Validate invalid ASCII chars even when mixed with non-ASCII. Bounded valid
non-ASCII scalar tag text produces UNSUPPORTED_TAG_UNICODE, never silently normalized.
conditions exactly if_match,if_unmodified_since,if_none_match,if_modified_since.
Dates nullable. Tag condition null=absent, else {star:bool,tags:[0..16 tags]}.
star true requires empty list; star false requires nonempty list. Duplicate exact
(opaque,weak) pairs invalid; same value/different weakness allowed. Opaque '*' is
not a selector. Unknown fields, invalid booleans/numbers, duplicates reject document.

unsupported_features: 0..8 unique strings, 1..32 ASCII [a-z][a-z0-9-]*. Any feature
declares unsupported context; it neither authenticates a caller nor enables a capability.
Reasons sorted unique: UNSUPPORTED_FEATURE, UNSUPPORTED_TAG_UNICODE, UNSUPPORTED_METHOD,
UNSUPPORTED_INFORMATIONAL_BASELINE, UNSUPPORTED_412_BASELINE, UNSUPPORTED_SUCCESS_CONTEXT.
Common type/size/schema/contradiction validation of EVERY case precedes all results.

Baseline 1xx and 412 unsupported. Supported 2xx combinations:
GET/HEAD,200,exists=true; PUT,201,exists=false; PUT,200/204,exists=true;
DELETE,200/204,exists=true. Other 2xx combinations unsupported. Other statuses bypass
conditionally only after complete validation and scope checks. Metadata labels do not
establish actual success, authorization, atomicity or origin behavior.

Strong comparison: both weak flags false and opaque exactly equal. Weak comparison:
opaque exactly equal. Missing etag never matches a list; wildcard tests exists.
If-Match failure => 412, success suppresses If-Unmodified-Since. Otherwise date guard
passes iff last_modified <= supplied date, ignored when no metadata. Next If-None-Match
failure => 304 for GET/HEAD, 412 otherwise; presence suppresses If-Modified-Since.
Otherwise If-Modified-Since for GET/HEAD passes iff last_modified > supplied date,
failure => 304; ignored on other methods or missing metadata. No already-applied
exception, range, response sending or cache merging. Continue has no success status.

Results exactly id,status,baseline_status,evaluation_applicable,outcome,suggested_status,
reason_codes,trace. Global report version and fixed assumptions. Supported outcomes:
CONTINUE_NORMAL_PROCESSING/null/ALL_CONDITIONS_PASSED;
PRECONDITION_FAILED/412/IF_MATCH_FAILED or IF_UNMODIFIED_SINCE_FAILED or IF_NONE_MATCH_FAILED;
NOT_MODIFIED/304/IF_NONE_MATCH_FAILED or IF_MODIFIED_SINCE_FAILED;
BYPASS_PRECONDITIONS/supplied baseline/NORMAL_CHECKS_TAKE_PRECEDENCE.
Unsupported: UNSUPPORTED status/outcome, applicability and suggested_status null.

Trace: four {condition,state} entries in listed condition order. Global unsupported
overrides all states => UNKNOWN_SCOPE; supported bypass overrides => BYPASSED_BASELINE.
Otherwise priority: absent => ABSENT, then present after earlier failure => NOT_REACHED,
then suppressed by tag condition => IGNORED_PRECEDENCE, then IMS wrong method =>
IGNORED_METHOD, then missing last_modified => IGNORED_NO_LAST_MODIFIED, then PASS/FAIL.
ABSENT only records known input shape; it never claims an evaluation after failure.
Applicability true for supported conditional path, even all conditions absent; false
for bypass. No trace state suggests an ignored/reached condition was actually evaluated.

Limits: 65536 UTF-8 input bytes, 262144 encoded output bytes; depth 8 (root 1),
5000 value nodes, 100 items per generic container, integer tokens <=10 digits;
strings <=256 chars before field-specific limits. Builtin dict/list/str/int/bool/null
only; no custom objects/generators. Duplicate JSON keys/IDs, malformed Unicode,
C0/DEL/oversize/unknown fields invalid. A snapshot declares one selected representation,
not negotiation or freshness. Only normalized synthetic metadata; no bodies/URIs/headers.

CLI python -m preconditionlab INPUT [--format json|markdown] [--output FRESH_FILE].
Exit 0 all supported, 2 any unsupported, 1 invalid/I/O. argparse syntax separately 2.
Validate/compute/encode whole document before output; ASCII-escaped JSON, numeric
entities for every user-derived Markdown char. Complete trace in both formats.
Exclusive fresh output/no overwrite/input alias; honest short/flush/close/cleanup errors.
Stdout may be partial on I/O failure. Paths/host process trusted, no hostile-race or
OS resource/durability guarantee. Reporter helpers consume evaluated reports only.

Fixture expectations hand-labelled before model code, with exact-byte freeze receipt.
The case limit is 32, so the original >=28 target fits; exactly 32 cases will be frozen.
