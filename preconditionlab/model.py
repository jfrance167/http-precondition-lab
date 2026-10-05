"""Ordered pure decisions over normalized synthetic snapshots."""

from .contracts import validate

ORDER = ("if_match", "if_unmodified_since", "if_none_match", "if_modified_since")
ASSUMPTIONS = ["synthetic normalized origin snapshot; declared baseline checks",
               "no request, response, resource mutation or cache merge performed",
               "dates supplied on one synthetic integer timeline",
               "no already-applied exception, ranges or negotiation",
               "not authorization, atomic update protection or full HTTP conformance"]


def _strong(left, right):
    return not left["weak"] and not right["weak"] and left["opaque"] == right["opaque"]


def _weak(left, right):
    return left["opaque"] == right["opaque"]


def _matches(condition, representation, strong):
    if condition["star"]:
        return representation["exists"]
    current = representation["etag"]
    if current is None:
        return False
    compare = _strong if strong else _weak
    return any(compare(tag, current) for tag in condition["tags"])


def _decide(case):
    result = {"id": case["id"], "status": "SUPPORTED", "baseline_status": case["baseline_status"],
              "evaluation_applicable": True, "outcome": "CONTINUE_NORMAL_PROCESSING",
              "suggested_status": None, "reason_codes": ["ALL_CONDITIONS_PASSED"], "trace": []}
    if case["scope"]:
        result.update(status="UNSUPPORTED", outcome="UNSUPPORTED", evaluation_applicable=None,
                      reason_codes=case["scope"],
                      trace=[{"condition": name, "state": "UNKNOWN_SCOPE"} for name in ORDER])
        return result
    if not 200 <= case["baseline_status"] < 300:
        result.update(outcome="BYPASS_PRECONDITIONS", evaluation_applicable=False,
                      suggested_status=case["baseline_status"], reason_codes=["NORMAL_CHECKS_TAKE_PRECEDENCE"],
                      trace=[{"condition": name, "state": "BYPASSED_BASELINE"} for name in ORDER])
        return result
    conditions = case["conditions"]
    representation = case["representation"]
    retrieval = case["method"] in {"GET", "HEAD"}
    failed = None
    for name in ORDER:
        value = conditions[name]
        if value is None:
            state = "ABSENT"
        elif failed is not None:
            state = "NOT_REACHED"
        elif name == "if_unmodified_since" and conditions["if_match"] is not None:
            state = "IGNORED_PRECEDENCE"
        elif name == "if_modified_since" and conditions["if_none_match"] is not None:
            state = "IGNORED_PRECEDENCE"
        elif name == "if_modified_since" and not retrieval:
            state = "IGNORED_METHOD"
        elif name in {"if_modified_since", "if_unmodified_since"} and representation["last_modified"] is None:
            state = "IGNORED_NO_LAST_MODIFIED"
        else:
            if name == "if_match":
                passed = _matches(value, representation, strong=True)
            elif name == "if_none_match":
                passed = not _matches(value, representation, strong=False)
            elif name == "if_unmodified_since":
                passed = representation["last_modified"] <= value
            else:
                passed = representation["last_modified"] > value
            state = "PASS" if passed else "FAIL"
            if not passed:
                failed = name
        result["trace"].append({"condition": name, "state": state})
    if failed is not None:
        not_modified = failed == "if_modified_since" or (failed == "if_none_match" and retrieval)
        result.update(outcome="NOT_MODIFIED" if not_modified else "PRECONDITION_FAILED",
                      suggested_status=304 if not_modified else 412,
                      reason_codes=[failed.upper() + "_FAILED"])
    return result


def evaluate(document):
    """Validate all concrete JSON-like data, then return inert hypothetical decisions.

    No caller-supplied label grants authority, and no declared snapshot is observed
    from an actual origin. Invalid data anywhere rejects the document before output.
    """
    cases = validate(document)
    return {"version": 1, "assumptions": list(ASSUMPTIONS),
            "results": [_decide(case) for case in cases]}
