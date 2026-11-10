#!/usr/bin/env python3
"""Convert one OpenCode V1 JSON export to an experimental V2.2 import shape.
Offline format converter, NOT a personal-data anonymizer.
"""
import argparse
import base64
from collections import Counter
import json
from pathlib import Path
import sys
from urllib.parse import unquote_to_bytes

class ConversionError(Exception):
    pass

def attachment(part):
    url = part.get("url", "")
    if not isinstance(url, str) or not url.startswith("data:") or "," not in url:
        return None
    header, value = url.split(",", 1)
    try:
        raw = base64.b64decode(value, validate=True) if ";base64" in header.lower() else unquote_to_bytes(value)
    except (ValueError, base64.binascii.Error) as exc:
        raise ConversionError("Invalid attachment data URL") from exc
    result = {"data": base64.b64encode(raw).decode("ascii"), "mime": part.get("mime") or "application/octet-stream", "source": {"type": "inline"}}
    if part.get("filename"):
        result["name"] = part["filename"]
    return result

def tool_content(part, created):
    old = part["state"]
    status = old["status"]
    raw_input = old.get("input")
    if status == "pending":
        state = {"status": "streaming", "input": json.dumps(raw_input, ensure_ascii=False) if raw_input else ""}
    elif status == "running":
        state = {"status": "running", "input": raw_input or {}, "metadata": old.get("metadata") or {}}
    elif status == "completed":
        state = {"status": "completed", "input": raw_input or {}, "content": [{"type": "text", "text": str(old.get("output") or "")}]}
    elif status == "error":
        state = {"status": "error", "input": raw_input or {}, "error": {"type": "legacy_tool_error", "message": str(old.get("error") or "Unknown error")}}
    else:
        raise ConversionError("Unsupported tool status: " + repr(status))
    if status != "pending" and not isinstance(state["input"], dict):
        raise ConversionError("Tool input must be an object")
    if status in ("completed", "error") and isinstance(old.get("metadata"), dict):
        state["metadata"] = old["metadata"]
    old_time = old.get("time") or {}
    time = {"created": old_time.get("start", created)}
    if "end" in old_time:
        time["completed"] = old_time["end"]
    return {"type": "tool", "id": part["callID"], "name": part["tool"], "state": state, "time": time}

def convert(data, directory):
    if not isinstance(data, dict) or not isinstance(data.get("info"), dict) or not isinstance(data.get("messages"), list):
        raise ConversionError("Expected a single session with info and messages")
    original_info = data["info"]
    if not str(original_info.get("id", "")).startswith("ses") or not original_info.get("projectID"):
        raise ConversionError("Missing session id or projectID")
    info = dict(original_info)
    info["location"] = {"directory": str(directory)}
    warnings = Counter()
    if "cost" not in info:
        info["cost"] = 0
        warnings["Missing session cost, defaulted to zero"] += 1
    if "tokens" not in info:
        info["tokens"] = {"input": 0, "output": 0, "reasoning": 0, "cache": {"read": 0, "write": 0}}
        warnings["Missing session tokens, defaulted to zero"] += 1
    if info.get("parentID"):
        warnings["Import parent session first"] += 1
    messages, types, seen = [], Counter(), set()
    for index, record in enumerate(data["messages"]):
        try:
            old, parts = record["info"], record["parts"]
            role = old["role"]
            if role not in ("user", "assistant") or not isinstance(parts, list):
                raise ConversionError("Unsupported role or parts")
            msgid = old["id"]
            if not isinstance(msgid, str) or not msgid.startswith("msg_") or msgid in seen:
                raise ConversionError("Invalid or duplicate message ID")
            seen.add(msgid)
            created = old["time"]["created"]
            if not isinstance(created, (int, float)):
                raise ConversionError("Invalid created time")
            msg = {"id": msgid, "type": role, "time": {"created": created}, "metadata": {"v1_info": old, "v1_parts": parts}}
            types[role] += 1
            if role == "user":
                msg["text"] = "\n".join(p["text"] for p in parts if p.get("type") == "text")
                files = []
                for part in parts:
                    typ = part.get("type", "<missing>")
                    types["part:" + typ] += 1
                    if typ == "file":
                        file = attachment(part)
                        if file:
                            files.append(file)
                        else:
                            warnings["External attachment preserved in metadata only"] += 1
                    elif typ != "text":
                        warnings["User part " + typ + " preserved in metadata only"] += 1
                if files:
                    msg["files"] = files
            else:
                if "completed" in old["time"]:
                    msg["time"]["completed"] = old["time"]["completed"]
                provider, model = old.get("providerID"), old.get("modelID")
                if not provider or not model:
                    raise ConversionError("Missing assistant providerID or modelID")
                msg["agent"] = old.get("agent") or old.get("mode") or "build"
                msg["model"] = {"providerID": provider, "id": model}
                content = []
                for part in parts:
                    typ = part.get("type", "<missing>")
                    types["part:" + typ] += 1
                    if typ in ("text", "reasoning"):
                        content.append({"type": typ, "text": part["text"]})
                    elif typ == "tool":
                        content.append(tool_content(part, created))
                    else:
                        warnings["Assistant part " + typ + " preserved in metadata only"] += 1
                msg["content"] = content
                if old.get("finish") in ("stop", "length", "tool-calls", "content-filter", "error", "unknown"):
                    msg["finish"] = old["finish"]
            messages.append(msg)
        except (KeyError, TypeError, ValueError, ConversionError) as exc:
            raise ConversionError("Message " + str(index + 1) + ": " + str(exc)) from exc
    return {"info": info, "messages": messages}, types, warnings

def main():
    parser = argparse.ArgumentParser(description="Convert one V1 session export to V2.2 JSON without importing")
    parser.add_argument("input", type=Path, help="V1 session JSON")
    parser.add_argument("--directory", required=True, type=Path, help="Existing absolute target directory")
    parser.add_argument("--output", type=Path, help="Output JSON; never overwritten")
    args = parser.parse_args()
    try:
        if not args.directory.is_absolute() or not args.directory.is_dir():
            raise ConversionError("--directory must be an existing absolute directory")
        output = args.output or args.input.with_name(args.input.stem + ".v2.json")
        if output.resolve() == args.input.resolve():
            raise ConversionError("Output must differ from input")
        with args.input.open(encoding="utf-8-sig") as f:
            data = json.load(f)
        converted, types, warnings = convert(data, args.directory.resolve())
        with output.open("x", encoding="utf-8", newline="\n") as f:
            json.dump(converted, f, ensure_ascii=False, separators=(",", ":"))
        print("Converted:", output.resolve())
        print("Session:", converted["info"]["id"])
        print("Counts:", ", ".join(str(k) + "=" + str(v) for k, v in sorted(types.items())))
        for warning, count in sorted(warnings.items()):
            print("Warning (" + str(count) + "): " + warning)
        print("Original V1 message metadata is preserved. Output is NOT anonymized.")
        print("Manual import:")
        print('opencode session import "' + str(output.resolve()) + '" --directory "' + str(args.directory.resolve()) + '"')
        return 0
    except (OSError, json.JSONDecodeError, ConversionError) as exc:
        print("Conversion failed: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
