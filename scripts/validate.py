#!/usr/bin/env python3
"""Validate every data file against its schema. Stdlib only — no pip.

Checks, per dataset folder:
- file parses as JSON and matches the folder's schema (subset of JSON Schema:
  type, required, additionalProperties, pattern, enum, min/max, uniqueItems,
  minLength/maxLength, minItems, format noted but not enforced)
- `id` equals the file name (without .json)
- ratings live at data/bewertungen/<entry-id>/<login>.json, reference an
  existing entry, and `login` equals the file name

Exit 0 on success, 1 with a readable report otherwise.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = {
    "wasserhaeuschen": ROOT / "schemas" / "wasserhaeuschen.schema.json",
    "ebbelwei": ROOT / "schemas" / "ebbelwei.schema.json",
    "bewertungen": ROOT / "schemas" / "bewertung.schema.json",
}

errors: list[str] = []


def fail(path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def check(instance, schema, path: Path, where: str = "") -> None:
    t = schema.get("type")
    if t == "object":
        if not isinstance(instance, dict):
            return fail(path, f"{where or 'root'} must be an object")
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                fail(path, f"missing required field '{key}'")
        if not schema.get("additionalProperties", True):
            for key in instance:
                if key not in props:
                    fail(path, f"unknown field '{key}'")
        for key, sub in props.items():
            if key in instance:
                check(instance[key], sub, path, where=f"{where}.{key}".lstrip("."))
    elif t == "array":
        if not isinstance(instance, list):
            return fail(path, f"{where} must be an array")
        if "minItems" in schema and len(instance) < schema["minItems"]:
            fail(path, f"{where} needs at least {schema['minItems']} item(s)")
        if schema.get("uniqueItems") and len(set(map(json.dumps, instance))) != len(instance):
            fail(path, f"{where} has duplicate items")
        for i, item in enumerate(instance):
            check(item, schema.get("items", {}), path, where=f"{where}[{i}]")
    elif t == "string":
        if not isinstance(instance, str):
            return fail(path, f"{where} must be a string")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], instance):
            fail(path, f"{where} does not match {schema['pattern']}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            fail(path, f"{where} is too short")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            fail(path, f"{where} exceeds {schema['maxLength']} characters")
        if schema.get("format") == "uri" and not instance.startswith(("http://", "https://")):
            fail(path, f"{where} must be an http(s) URL")
        if schema.get("format") == "date" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", instance):
            fail(path, f"{where} must be YYYY-MM-DD")
    elif t == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            return fail(path, f"{where} must be an integer")
        _check_bounds(instance, schema, path, where)
    elif t == "number":
        if not isinstance(instance, (int, float)) or isinstance(instance, bool):
            return fail(path, f"{where} must be a number")
        _check_bounds(instance, schema, path, where)
    elif t == "boolean":
        if not isinstance(instance, bool):
            fail(path, f"{where} must be a boolean")
    if "enum" in schema and instance not in schema["enum"]:
        fail(path, f"{where} must be one of {schema['enum']}")


def _check_bounds(value, schema, path: Path, where: str) -> None:
    if "minimum" in schema and value < schema["minimum"]:
        fail(path, f"{where} below minimum {schema['minimum']}")
    if "maximum" in schema and value > schema["maximum"]:
        fail(path, f"{where} above maximum {schema['maximum']}")


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(path, f"invalid JSON: {e}")
        return None


def main() -> int:
    entry_ids: set[str] = set()

    for dataset in ("wasserhaeuschen", "ebbelwei"):
        schema = json.loads(SCHEMAS[dataset].read_text(encoding="utf-8"))
        for file in sorted((ROOT / "data" / dataset).glob("*.json")):
            doc = load(file)
            if doc is None:
                continue
            check(doc, schema, file)
            if isinstance(doc, dict):
                if doc.get("id") != file.stem:
                    fail(file, f"id '{doc.get('id')}' must equal file name '{file.stem}'")
                entry_ids.add(file.stem)

    rating_schema = json.loads(SCHEMAS["bewertungen"].read_text(encoding="utf-8"))
    for file in sorted((ROOT / "data" / "bewertungen").glob("*/*.json")):
        doc = load(file)
        if doc is None:
            continue
        check(doc, rating_schema, file)
        if isinstance(doc, dict):
            if doc.get("entry") != file.parent.name:
                fail(file, f"entry '{doc.get('entry')}' must equal folder '{file.parent.name}'")
            if doc.get("entry") not in entry_ids:
                fail(file, f"rates unknown entry '{doc.get('entry')}'")
            if doc.get("login") != file.stem:
                fail(file, f"login '{doc.get('login')}' must equal file name '{file.stem}'")

    if errors:
        print(f"{len(errors)} problem(s):")
        for line in errors:
            print(f"  - {line}")
        return 1
    print(f"data validation OK ({len(entry_ids)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
