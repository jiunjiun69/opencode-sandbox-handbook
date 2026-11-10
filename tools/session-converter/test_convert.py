import base64
import copy
import unittest
from pathlib import Path
from convert import ConversionError, convert

def example():
    return {"info": {"id": "ses_example", "projectID": "example", "time": {"created": 1, "updated": 2}}, "messages": [
        {"info": {"id": "msg_1", "role": "user", "time": {"created": 1}}, "parts": [
            {"type": "text", "text": "hello"}, {"type": "file", "mime": "text/plain", "url": "data:text/plain;base64,aGk="}]},
        {"info": {"id": "msg_2", "role": "assistant", "time": {"created": 2}, "providerID": "sample", "modelID": "sample-model"}, "parts": [
            {"type": "reasoning", "text": "example"}, {"type": "tool", "callID": "call_example", "tool": "read", "state": {"status": "completed", "input": {}, "output": "done"}},
            {"type": "patch", "files": ["sample.txt"]}]}
    ]}

class ConversionTests(unittest.TestCase):
    def test_preserve_original(self):
        data = example()
        original = copy.deepcopy(data)
        result, counts, warnings = convert(data, Path("/example/workspace"))
        self.assertEqual(data, original)
        self.assertEqual(len(result["messages"]), 2)
        self.assertEqual(base64.b64decode(result["messages"][0]["files"][0]["data"]), b"hi")
        self.assertEqual(result["messages"][1]["content"][1]["state"]["content"][0]["text"], "done")
        self.assertEqual(result["messages"][1]["metadata"]["v1_parts"], original["messages"][1]["parts"])
        self.assertEqual(counts["part:tool"], 1)
        self.assertTrue(any("patch" in k for k in warnings))

    def test_external_attachment(self):
        data = example()
        data["messages"][0]["parts"][1]["url"] = "file:///example/private.txt"
        result, _, warnings = convert(data, Path("/example/workspace"))
        self.assertNotIn("files", result["messages"][0])
        self.assertTrue(any("attachment" in k.lower() for k in warnings))

    def test_bad_ids_and_model(self):
        data = example()
        data["messages"][1]["info"]["id"] = "msg_1"
        with self.assertRaises(ConversionError):
            convert(data, Path("/example/workspace"))
        data = example()
        del data["messages"][1]["info"]["modelID"]
        with self.assertRaises(ConversionError):
            convert(data, Path("/example/workspace"))

    def test_tool_states(self):
        for status in ("pending", "running", "completed", "error"):
            data = example()
            data["messages"][1]["parts"][1]["state"]["status"] = status
            result, _, _ = convert(data, Path("/example/workspace"))
            self.assertEqual(result["messages"][1]["content"][1]["state"]["status"], "streaming" if status == "pending" else status)
        data = example()
        data["messages"][1]["parts"][1]["state"]["status"] = "unexpected"
        with self.assertRaises(ConversionError):
            convert(data, Path("/example/workspace"))

    def test_reject_v2_input(self):
        data = example()
        data["messages"][0] = {"id": "msg_1", "type": "user"}
        with self.assertRaises(ConversionError):
            convert(data, Path("/example/workspace"))

if __name__ == "__main__":
    unittest.main()
