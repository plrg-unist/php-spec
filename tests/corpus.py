#!/usr/bin/env python3
"""Inventory syntax inputs without executing application or PHPT code."""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTAX_INI = {"short_open_tag", "zend.multibyte", "zend.script_encoding", "default_charset"}


def sections(data):
    """Match run-tests.php TestFile::readFile, including ===DONE=== handling."""
    # PHP fgets splits only on LF; bytes such as CR/VT inside literals are data.
    lines = data.split(b"\n")
    lines = [line + b"\n" for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])
    if not lines or not lines[0].startswith(b"--TEST--"):
        raise ValueError("PHPT does not begin with --TEST--")
    result, current, done = {"TEST": b""}, "TEST", False
    for line in lines[1:]:
        marker = re.match(rb"^--([_A-Z]+)--", line)
        if marker:
            current = marker[1].decode("ascii")
            if result.get(current):
                raise ValueError("duplicate section " + current)
            result[current], done = b"", False
        elif not done:
            result[current] += line
            if current in {"FILE", "FILEEOF", "FILE_EXTERNAL"} and re.match(rb"^===DONE===\s*$", line):
                done = True
    return result


def config(section):
    values = {}
    for line in section.decode("latin1").splitlines():
        match = re.match(r"\s*([\w.]+)\s*=\s*(.*?)\s*$", line)
        if match and match[1] in SYNTAX_INI:
            values[match[1]] = match[2]
    return values


def record(path, origin, source=None, **extra):
    value = {"id": str(path.relative_to(ROOT)), "origin": origin, **extra}
    if source is not None:
        value.update(sha256=hashlib.sha256(source).hexdigest(), bytes=len(source),
                     source_b64=base64.b64encode(source).decode("ascii"))
    return value


def phpt(path):
    parts = sections(path.read_bytes())
    common = {"ini": config(parts.get("INI", b"")),
              "ini_b64": base64.b64encode(parts.get("INI", b"")).decode("ascii")}
    if "REDIRECTTEST" in parts:
        return record(path, "PHPT", status="redirect_container", **common)
    keys = [key for key in ("FILE", "FILEEOF", "FILE_EXTERNAL") if key in parts]
    if len(keys) != 1:
        return record(path, "PHPT", status="non_source" if not keys and "PHPDBG" in parts else "invalid_container", **common)
    key = keys[0]
    source = parts[key]
    if key == "FILEEOF":
        source = source.rstrip(b"\r\n")
    if key == "FILE_EXTERNAL":
        # This is the runner's removal of '..', not ordinary path normalization.
        relative = source.replace(b"..", b"").strip().decode("utf-8", "surrogateescape")
        external = path.parent / relative
        if not external.resolve().is_relative_to((ROOT / "vendor/php-src").resolve()):
            raise ValueError("external fixture escapes imported PHP tree")
        common["external"] = str(external.relative_to(ROOT))
        if not external.is_file():
            return record(path, "PHPT", status="missing_fixture", section=key, **common)
        source = external.read_bytes()
    return record(path, "PHPT", source, status="source", section=key, **common)


def inputs():
    for path in sorted((ROOT / "vendor/php-src").rglob("*.phpt")):
        yield phpt(path)
    benchmark = ROOT / "corpora/bolaray"
    for path in sorted(benchmark.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        source = path.read_bytes()
        # PHP-bearing template/include files count even with non-PHP extensions.
        if suffix in {".php", ".php3", ".php4", ".php5", ".phtml", ".inc"} or b"<?php" in source or b"<?=" in source:
            yield record(path, "BolaRay", source, status="source", ini={},
                         candidate="extension" if suffix in {".php", ".php3", ".php4", ".php5", ".phtml", ".inc"} else "embedded_tag")
    for path in sorted((ROOT / "tests/fixtures").glob("*.php")):
        meta_path = path.with_suffix(".json")
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        yield record(path, "targeted", path.read_bytes(), status="source", ini=meta.pop("ini", {}), **meta)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "coverage/corpus.jsonl")
    args = parser.parse_args()
    counts = {}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as output:
        for item in inputs():
            output.write(json.dumps(item, ensure_ascii=True, separators=(",", ":")) + "\n")
            key = item["origin"] + ":" + item["status"]
            counts[key] = counts.get(key, 0) + 1
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
