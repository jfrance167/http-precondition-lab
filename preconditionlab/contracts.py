"""Strict bounded contract validation, adapted from Jake's MIT HTTP-cache/CORS labs."""

import json
import re

INPUT_BYTES = 65_536
OUTPUT_BYTES = 262_144
MAX_INTEGER = 1_000_000_000
TOKEN = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", re.ASCII)


class Invalid(ValueError):
    """Fixed error code: document cannot be evaluated under this contract."""


def text(value, limit=256, nonempty=False):
    """Validate scalar text without coercion, truncation or replacement."""
    if type(value) is not str or len(value) > limit or (nonempty and not value):
        raise Invalid("TEXT_TYPE_OR_LIMIT")
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise Invalid("TEXT_CONTROL")
    try:
        value.encode("utf-8", "strict")
    except UnicodeError as exc:
        raise Invalid("INVALID_UNICODE") from exc
    return value


def keys(value, required):
    if type(value) is not dict or set(value) != set(required):
        raise Invalid("SCHEMA")


def number(value, lower=0, upper=MAX_INTEGER):
    if type(value) is not int or not lower <= value <= upper:
        raise Invalid("INTEGER_BOUND")
    return value


def boolean(value):
    if type(value) is not bool:
        raise Invalid("BOOLEAN_REQUIRED")
    return value


def _walk(value, depth, budget):
    # Reject custom containers before accessing their methods or iterating them.
    budget[0] += 1
    if budget[0] > 5_000:
        raise Invalid("NODE_LIMIT")
    kind = type(value)
    if kind in (dict, list):
        depth += 1
        if depth > 8 or len(value) > 100:
            raise Invalid("CONTAINER_LIMIT")
        if kind is dict:
            for key, item in value.items():
                text(key, 64, True)
                _walk(item, depth, budget)
        else:
            for item in value:
                _walk(item, depth, budget)
    elif kind is str:
        text(value, 256)
    elif kind is int:
        number(value)
    elif kind is not bool and value is not None:
        raise Invalid("BUILTIN_DATA_REQUIRED")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Invalid("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _integer(token):
    if len(token.lstrip("-")) > 10:
        raise Invalid("NUMERIC_TOKEN_LIMIT")
    return int(token)


def _noninteger(_):
    raise Invalid("INTEGER_ONLY")


def parse(raw):
    """Decode exact bytes with byte/depth/token bounds; evaluate() validates schema."""
    if type(raw) is not bytes or len(raw) > INPUT_BYTES:
        raise Invalid("INPUT_LIMIT")
    try:
        source = raw.decode("utf-8", "strict")
        quoted = escaped = False
        depth = 0
        for char in source:
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char in "[{":
                depth += 1
                if depth > 8:
                    raise Invalid("JSON_DEPTH")
            elif char in "]}":
                depth -= 1
        return json.loads(source, object_pairs_hook=_pairs, parse_int=_integer,
                          parse_float=_noninteger, parse_constant=_noninteger)
    except (UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, Invalid):
            raise
        raise Invalid("INVALID_JSON") from exc



SUPPORTED_METHODS = {"GET", "HEAD", "PUT", "DELETE"}
FEATURE = re.compile(r"[a-z][a-z0-9-]*", re.ASCII)


def _tag(value, scope):
    keys(value, {"opaque", "weak"})
    opaque = text(value["opaque"], 128)
    boolean(value["weak"])
    # Bad ASCII is invalid even in a mixed string that also makes scope unsupported.
    if any(ord(c) < 128 and not (ord(c) == 33 or 35 <= ord(c) <= 126) for c in opaque):
        raise Invalid("INVALID_OPAQUE_ASCII")
    if not opaque.isascii():
        scope.add("UNSUPPORTED_TAG_UNICODE")
    return {"opaque": opaque, "weak": value["weak"]}


def _tag_condition(value, scope):
    if value is None:
        return None
    keys(value, {"star", "tags"})
    boolean(value["star"])
    tags = value["tags"]
    if type(tags) is not list or len(tags) > 16:
        raise Invalid("TAG_LIST_LIMIT")
    if (value["star"] and tags) or (not value["star"] and not tags):
        raise Invalid("TAG_SELECTOR_SHAPE")
    result = [_tag(tag, scope) for tag in tags]
    identities = [(tag["opaque"], tag["weak"]) for tag in result]
    if len(set(identities)) != len(identities):
        raise Invalid("DUPLICATE_TAG")
    return {"star": value["star"], "tags": result}


def _representation(value, scope):
    keys(value, {"exists", "etag", "last_modified"})
    boolean(value["exists"])
    etag = None if value["etag"] is None else _tag(value["etag"], scope)
    if value["last_modified"] is not None:
        number(value["last_modified"])
    if not value["exists"] and (etag is not None or value["last_modified"] is not None):
        raise Invalid("CONTRADICTORY_SNAPSHOT")
    return {"exists": value["exists"], "etag": etag, "last_modified": value["last_modified"]}


def _case(case):
    keys(case, {"id", "method", "baseline_status", "representation", "conditions", "unsupported_features"})
    identity = text(case["id"], 64, True)
    method = text(case["method"], 16, True)
    if not TOKEN.fullmatch(method):
        raise Invalid("METHOD_TOKEN")
    status = number(case["baseline_status"], 100, 599)
    scope = set()
    representation = _representation(case["representation"], scope)
    conditions = case["conditions"]
    keys(conditions, {"if_match", "if_unmodified_since", "if_none_match", "if_modified_since"})
    normalized = {}
    for name in ("if_match", "if_none_match"):
        normalized[name] = _tag_condition(conditions[name], scope)
    for name in ("if_unmodified_since", "if_modified_since"):
        value = conditions[name]
        if value is not None:
            number(value)
        normalized[name] = value
    features = case["unsupported_features"]
    if type(features) is not list or len(features) > 8:
        raise Invalid("FEATURE_LIMIT")
    for feature in features:
        text(feature, 32, True)
        if not FEATURE.fullmatch(feature):
            raise Invalid("FEATURE_IDENTIFIER")
    if len(set(features)) != len(features):
        raise Invalid("DUPLICATE_FEATURE")
    if features:
        scope.add("UNSUPPORTED_FEATURE")
    if method not in SUPPORTED_METHODS:
        scope.add("UNSUPPORTED_METHOD")
    if status < 200:
        scope.add("UNSUPPORTED_INFORMATIONAL_BASELINE")
    elif status == 412:
        scope.add("UNSUPPORTED_412_BASELINE")
    elif 200 <= status < 300 and method in SUPPORTED_METHODS:
        exists = representation["exists"]
        supported = ((method in {"GET", "HEAD"} and status == 200 and exists)
                     or (method == "PUT" and status == 201 and not exists)
                     or (method == "PUT" and status in {200, 204} and exists)
                     or (method == "DELETE" and status in {200, 204} and exists))
        if not supported:
            scope.add("UNSUPPORTED_SUCCESS_CONTEXT")
    return {"id": identity, "method": method, "baseline_status": status,
            "representation": representation, "conditions": normalized, "scope": sorted(scope)}


def validate(document):
    """Validate all cases completely before returning internal immutable-use snapshots."""
    _walk(document, 0, [0])
    if len(json.dumps(document, ensure_ascii=False).encode("utf-8")) > INPUT_BYTES:
        raise Invalid("INPUT_LIMIT")
    keys(document, {"version", "cases"})
    if type(document["version"]) is not int or document["version"] != 1:
        raise Invalid("VERSION")
    cases = document["cases"]
    if type(cases) is not list or not 1 <= len(cases) <= 32:
        raise Invalid("CASE_LIMIT")
    result, seen = [], set()
    for value in cases:
        case = _case(value)
        if case["id"] in seen:
            raise Invalid("DUPLICATE_ID")
        seen.add(case["id"])
        result.append(case)
    return result
