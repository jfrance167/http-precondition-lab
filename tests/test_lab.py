"""Independent frozen precondition outcomes, input bounds and inert output tests."""

import ast
import copy
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
# Fixed interpreter and own module only, shell disabled, no input-selected commands.
import subprocess  # nosec B404
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from preconditionlab import Invalid, evaluate, parse
from preconditionlab.contracts import INPUT_BYTES, OUTPUT_BYTES
from preconditionlab.report import encode, write_fresh

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = json.loads((ROOT/"fixtures/cases.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((ROOT/"fixtures/expected.json").read_text(encoding="utf-8"))


def one():
    return {"version":1,"cases":[copy.deepcopy(DOCUMENT["cases"][0])]}


def selector(value="A", weak=False):
    return {"star":False,"tags":[{"opaque":value,"weak":weak}]}


@contextmanager
def scratch():
    temporary = tempfile.TemporaryDirectory(dir=ROOT,prefix="test-scratch-")
    if not Path(temporary.name).resolve().is_relative_to(ROOT):
        raise RuntimeError("temporary path outside project")
    try:
        yield temporary.name
    finally:
        temporary.cleanup()


class LabTests(unittest.TestCase):
    def test_frozen_labels(self):
        report = evaluate(DOCUMENT)
        self.assertEqual(len(report["results"]),32)
        for actual, expected in zip(report["results"],EXPECTED):
            with self.subTest(case=expected["id"]):
                self.assertEqual({key:actual[key] for key in expected},expected)
        self.assertEqual(sum(r["status"]=="UNSUPPORTED" for r in report["results"]),4)

    def test_frozen_bytes(self):
        receipt = json.loads((ROOT/"research/fixture-freeze.json").read_text(encoding="utf-8-sig"))
        for entry in receipt:
            name = entry["Path"].replace("\\","/").split("/")[-1]
            path = ROOT/name if name=="CONTRACT.md" else ROOT/"fixtures"/name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest().upper(),entry["Hash"])

    def test_no_mutation_or_result_alias(self):
        doc = one()
        original = copy.deepcopy(doc)
        report = evaluate(doc)
        report["results"][0]["trace"][0]["state"] = "changed"
        self.assertEqual(doc,original)
        self.assertEqual(evaluate(doc)["results"][0]["trace"][0]["state"],"ABSENT")

    def test_complete_strong_weak_pairs(self):
        for left,right,strong in [(False,False,True),(False,True,False),(True,False,False),(True,True,False)]:
            for name,expected in [("if_match",None if strong else 412),("if_none_match",304)]:
                doc = one()
                case = doc["cases"][0]
                case["representation"]["etag"]["weak"] = right
                case["conditions"][name] = selector(weak=left)
                self.assertEqual(evaluate(doc)["results"][0]["suggested_status"],expected)

    def test_empty_literal_star_and_backslash(self):
        for value in ("", "*", "a\\b", "a,b"):
            doc = one()
            case = doc["cases"][0]
            case["representation"]["etag"]["opaque"] = value
            case["conditions"]["if_match"] = selector(value)
            self.assertEqual(evaluate(doc)["results"][0]["outcome"],"CONTINUE_NORMAL_PROCESSING")
        doc = one()
        doc["cases"][0]["conditions"]["if_match"] = selector("a")
        self.assertEqual(evaluate(doc)["results"][0]["suggested_status"],412)

    def test_tag_shapes_duplicates_and_character_rules(self):
        for value in ('"', " ", "a\t", "\x7f", 'é"', 'é '):
            doc = one()
            doc["cases"][0]["representation"]["etag"]["opaque"] = value
            with self.subTest(value=repr(value)), self.assertRaises(Invalid):
                evaluate(doc)
        for condition in ({"star":False,"tags":[]}, {"star":True,"tags":selector()["tags"]},
                          {"star":1,"tags":[]}, {"star":False,"tags":selector()["tags"]*2}):
            doc = one()
            doc["cases"][0]["conditions"]["if_match"] = condition
            with self.assertRaises(Invalid):
                evaluate(doc)
        doc = one()
        doc["cases"][0]["conditions"]["if_match"] = {"star":False,"tags":[
            {"opaque":"A","weak":False},{"opaque":"A","weak":True}]}
        self.assertEqual(evaluate(doc)["results"][0]["outcome"],"CONTINUE_NORMAL_PROCESSING")

    def test_nonascii_is_scope_not_normalization(self):
        doc = one()
        doc["cases"][0]["conditions"]["if_none_match"] = selector("Ａ")
        result = evaluate(doc)["results"][0]
        self.assertEqual(result["status"],"UNSUPPORTED")
        self.assertIsNone(result["suggested_status"])
        self.assertTrue(all(x["state"]=="UNKNOWN_SCOPE" for x in result["trace"]))

    def test_tag_missing_vs_existence(self):
        for name,expected in [("if_match",None),("if_none_match",304)]:
            doc = one()
            case = doc["cases"][0]
            case["representation"]["etag"] = None
            case["conditions"][name] = {"star":True,"tags":[]}
            self.assertEqual(evaluate(doc)["results"][0]["suggested_status"],expected)

    def test_trace_priority_after_failure(self):
        doc = one()
        case = doc["cases"][0]
        case["method"] = "PUT"
        case["baseline_status"] = 204
        case["conditions"].update(if_match=selector("B"),if_unmodified_since=99,if_modified_since=100)
        case["representation"]["last_modified"] = None
        result = evaluate(doc)["results"][0]
        self.assertEqual([x["state"] for x in result["trace"]],["FAIL","NOT_REACHED","ABSENT","NOT_REACHED"])

    def test_trace_precedence_method_metadata_priority(self):
        doc = one()
        case = doc["cases"][0]
        case["method"] = "PUT"
        case["baseline_status"] = 204
        case["representation"]["last_modified"] = None
        case["conditions"].update(if_none_match=selector("B"),if_modified_since=100)
        result = evaluate(doc)["results"][0]
        self.assertEqual(result["trace"][3]["state"],"IGNORED_PRECEDENCE")
        case["conditions"]["if_none_match"] = None
        self.assertEqual(evaluate(doc)["results"][0]["trace"][3]["state"],"IGNORED_METHOD")

    def test_informational_baselines_never_completed(self):
        for status in (100,103,199,412):
            doc = one()
            doc["cases"][0]["baseline_status"] = status
            result = evaluate(doc)["results"][0]
            self.assertEqual(result["status"],"UNSUPPORTED")
            self.assertIsNone(result["evaluation_applicable"])

    def test_baseline_redirect_and_error_bypass(self):
        for status in (301,403,404,500):
            doc = one()
            case = doc["cases"][0]
            case["baseline_status"] = status
            case["conditions"]["if_match"] = selector("B")
            result = evaluate(doc)["results"][0]
            self.assertEqual(result["outcome"],"BYPASS_PRECONDITIONS")
            self.assertEqual(result["suggested_status"],status)
            self.assertTrue(all(x["state"]=="BYPASSED_BASELINE" for x in result["trace"]))

    def test_invalid_later_data_never_masked(self):
        for scope_edit in [lambda c:c.update(baseline_status=403),
                           lambda c:c.update(unsupported_features=["range"]),
                           lambda c:c["conditions"].update(if_match=selector("B")),
                           lambda c:c["representation"]["etag"].update(opaque="é")]:
            doc = one()
            scope_edit(doc["cases"][0])
            second = copy.deepcopy(one()["cases"][0])
            second["id"] = "later"
            second["conditions"]["if_modified_since"] = True
            doc["cases"].append(second)
            with self.assertRaises(Invalid):
                evaluate(doc)
        doc = one()
        doc["cases"][0]["conditions"]["if_match"] = selector("B")
        doc["cases"][0]["conditions"]["if_none_match"] = selector('é"')
        with self.assertRaises(Invalid):
            evaluate(doc)

    def test_snapshot_contradiction_even_unsupported(self):
        doc = one()
        case = doc["cases"][0]
        case["representation"].update(exists=False,etag={"opaque":"é","weak":False})
        case["unsupported_features"] = ["auth-context"]
        with self.assertRaisesRegex(Invalid,"CONTRADICTORY_SNAPSHOT"):
            evaluate(doc)

    def test_schema_and_exact_types(self):
        for edit in [lambda d:d.update(extra=1),lambda d:d.update(version=True),
                     lambda d:d.update(cases=[]),lambda d:d["cases"][0].update(method="bad method"),
                     lambda d:d["cases"][0]["representation"].update(exists=1),
                     lambda d:d["cases"][0]["conditions"].update(if_modified_since=-1),
                     lambda d:d["cases"][0]["conditions"].update(if_modified_since=10**9+1),
                     lambda d:d["cases"][0].update(id="\ud800"),
                     lambda d:d["cases"].append(copy.deepcopy(d["cases"][0])),
                     lambda d:d.update(cases=[d["cases"][0]]*33)]:
            doc = one()
            edit(doc)
            with self.assertRaises(Invalid):
                evaluate(doc)

    def test_feature_bounds_and_scope_reasons(self):
        for features in (["range"]*2,["range"]*9,["BAD"],["a"*33]):
            doc = one()
            doc["cases"][0]["unsupported_features"] = features
            with self.assertRaises(Invalid):
                evaluate(doc)
        doc = one()
        doc["cases"][0].update(method="get",unsupported_features=["range"])
        self.assertEqual(evaluate(doc)["results"][0]["reason_codes"],["UNSUPPORTED_FEATURE","UNSUPPORTED_METHOD"])

    def test_json_decoder_bounds(self):
        for raw in (b'{"a":1,"a":2}',b'{"n":1.5}',b'{"n":NaN}',b'{"n":12345678901}',
                    b'['*9+b'0'+b']'*9,b'\xff',b' '* (INPUT_BYTES+1),b'bad json'):
            with self.assertRaises(Invalid):
                parse(raw)
        self.assertEqual(parse(b'"[[\\\"]]"'),'[["]]')
        with self.assertRaises(Invalid):
            parse(bytearray(b'{}'))

    def test_api_custom_depth_node_bounds(self):
        class Evil(dict):
            def items(self):
                raise RuntimeError("must not execute")
        for value in (Evil(),object(),iter([]),tuple([])):
            with self.assertRaises(Invalid):
                evaluate(value)
        nested = []
        for _ in range(9):
            nested = [nested]
        with self.assertRaises(Invalid):
            evaluate(nested)
        with self.assertRaisesRegex(Invalid,"NODE_LIMIT"):
            evaluate({str(i):[None]*100 for i in range(100)})

    def test_api_size_tag_count_and_output_guard(self):
        doc = one()
        doc["cases"] = []
        for i in range(32):
            case = copy.deepcopy(one()["cases"][0])
            case["id"] = str(i)
            tags = [{"opaque":str(j)+"a"*120,"weak":False} for j in range(16)]
            case["conditions"]["if_match"] = {"star":False,"tags":tags}
            case["conditions"]["if_none_match"] = copy.deepcopy(case["conditions"]["if_match"])
            doc["cases"].append(case)
        with self.assertRaisesRegex(Invalid,"INPUT_LIMIT"):
            evaluate(doc)
        doc = one()
        doc["cases"][0]["conditions"]["if_match"] = {"star":False,"tags":selector()["tags"]*17}
        with self.assertRaisesRegex(Invalid,"TAG_LIST_LIMIT"):
            evaluate(doc)
        for fmt in ("json","markdown"):
            # Honest reporter seam; no claim that valid bounded input reaches this cap.
            with self.assertRaisesRegex(Invalid,"OUTPUT_LIMIT"):
                encode({"results":[],"assumptions":["a"*OUTPUT_BYTES]},fmt)

    def test_report_inert_complete_trace(self):
        doc = one()
        doc["cases"][0]["id"] = '<img src=x>|[link](https://fake.test)'
        report = evaluate(doc)
        markdown = encode(report,"markdown")
        self.assertNotIn(b'<img',markdown)
        self.assertNotIn(b'[link]',markdown)
        self.assertIn(b'&#60;',markdown)
        for field in report["results"][0]:
            if field!="id":
                self.assertIn(field.encode(),markdown)
        self.assertEqual(json.loads(encode(report))["results"],report["results"])

    def test_exclusive_file(self):
        with scratch() as tmp:
            path = Path(tmp)/"report.json"
            write_fresh(path,b'old')
            with self.assertRaises(FileExistsError):
                write_fresh(path,b'new')
            self.assertEqual(path.read_bytes(),b'old')

    def test_output_short_flush_close_cleanup_errors(self):
        for failure in ("short","flush","close"):
            stream = MagicMock()
            stream.__enter__.return_value = stream
            stream.write.return_value = 0 if failure=="short" else 1
            if failure=="flush":
                stream.flush.side_effect = OSError
            if failure=="close":
                stream.__exit__.side_effect = OSError
            with patch("preconditionlab.report.open",return_value=stream),patch("preconditionlab.report.os.unlink") as unlink:
                with self.assertRaises(OSError):
                    write_fresh("own-new",b'x')
                unlink.assert_called_once_with("own-new")
        with patch("preconditionlab.report.open",return_value=stream),patch("preconditionlab.report.os.unlink",side_effect=OSError):
            with self.assertRaisesRegex(Invalid,"CLEANUP_FAILED"):
                write_fresh("own-new",b'x')

    def test_cli_status_alias_existing_and_invalid_no_output(self):
        with scratch() as tmp:
            source,output = Path(tmp)/"in.json",Path(tmp)/"out.json"
            prefix = [sys.executable] + (["-O"] if sys.flags.optimize else []) + ["-m","preconditionlab"]
            def run(*arguments):
                # Own module and test-owned filenames, never input-selected code.
                return subprocess.run(prefix+list(arguments),cwd=ROOT,capture_output=True,timeout=15,check=False)  # nosec B603
            source.write_text(json.dumps(one()),encoding="utf-8")
            self.assertEqual(run(str(source)).returncode,0)
            self.assertEqual(run(str(source),"--output",str(output)).returncode,0)
            self.assertEqual(run(str(source),"--output",str(output)).returncode,1)
            self.assertEqual(run(str(source),"--output",str(source)).returncode,1)
            source.write_text(json.dumps(DOCUMENT),encoding="utf-8")
            self.assertEqual(run(str(source)).returncode,2)
            source.write_text('{"bad":true}',encoding="utf-8")
            fresh = Path(tmp)/"invalid-new.json"
            invalid = run(str(source),"--output",str(fresh))
            self.assertEqual(invalid.returncode,1)
            self.assertEqual(invalid.stdout,b'')
            self.assertFalse(fresh.exists())
            self.assertNotIn(str(source).encode(),invalid.stderr)

    def test_forbidden_capabilities(self):
        allowed = {"json","re","os","sys","argparse","contracts","model","report"}
        for path in (ROOT/"preconditionlab").glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node,ast.Import):
                    self.assertTrue(all(x.name in allowed for x in node.names))
                if isinstance(node,ast.ImportFrom):
                    self.assertIn(node.module,allowed)
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
                    self.assertNotIn(node.func.id,{"eval","exec","__import__","compile"})
                self.assertNotIsInstance(node,ast.Assert)

    def test_actual_closed_stdout_exit(self):
        with scratch() as tmp:
            source = Path(tmp)/"closed-pipe.json"
            for count in (6,8,12,32):
                source.write_text(json.dumps({"version":1,"cases":DOCUMENT["cases"][:count]}),encoding="utf-8")
                arguments = [sys.executable] + (["-O"] if sys.flags.optimize else []) + [
                    "-m","preconditionlab",str(source)]
                # Own CLI/synthetic data; vary buffering sizes, close consumer after byte 1.
                child = subprocess.Popen(arguments,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)  # nosec B603
                try:
                    child.stdout.read(1)
                    child.stdout.close()
                    stderr = child.stderr.read().replace(b"\r\n",b"\n")
                    code = child.wait(timeout=15)
                    with self.subTest(count=count):
                        if stderr:
                            self.assertEqual(code,1,stderr.decode("utf-8","replace"))
                            self.assertEqual(stderr,b"preconditionlab: IO_ERROR\n")
                        else:
                            # The complete payload may enter the pipe before reader closes.
                            self.assertIn(code,(0,2))
                finally:
                    if child.poll() is None:
                        child.kill()
                        child.wait(timeout=15)
                    child.stderr.close()


if __name__ == "__main__":
    unittest.main()
