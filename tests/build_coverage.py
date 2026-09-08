#!/usr/bin/env python3
"""Build optional parser/scanner instrumentation without changing the oracle."""
import re
import shutil
import subprocess
from pathlib import Path
from corpus import ROOT


def main():
    original = ROOT / ".tools/php-build"
    target = ROOT / ".tools/php-coverage-build"
    scanner = ROOT / ".tools/php-coverage-scanner"
    if not (original / "Makefile").is_file():
        raise SystemExit("Run scripts/build-deps.sh --fresh first; a configured local PHP build is required")
    shutil.copytree(original, target, dirs_exist_ok=True)
    scanner.mkdir(exist_ok=True)
    for name in ("Makefile", "Makefile.objects", "Makefile.fragments", "config.status", "libtool"):
        path = target / name
        if path.exists():
            path.write_text(path.read_text().replace(str(original), str(target)))
    source = ROOT / "vendor/php-src/Zend/zend_language_scanner.l"
    lines = []
    for number, line in enumerate(source.read_text().splitlines(keepends=True), 1):
        lines.append(line)
        if line.startswith("<") and re.search(r" \{(?:\s*/\*.*\*/)?\s*$", line):
            lines.append('\tfprintf(stderr, "LEX_RULE:' + str(number) + '\\n");\n')
    (scanner / source.name).write_text("".join(lines))
    subprocess.run(["re2c", "--no-generation-date", "--case-inverted", "-cbdFt",
                    str(scanner / "zend_language_scanner_defs.h"), "-o",
                    str(scanner / "zend_language_scanner.c"), str(scanner / source.name)], check=True)
    makefile = target / "Makefile"
    text = makefile.read_text()
    # Match either the pristine import or the disposable source used by fresh builds.
    text = re.sub(r"/[^\s]+/Zend/zend_language_scanner\.c", str(scanner / "zend_language_scanner.c"), text)
    makefile.write_text(text)
    for name in ("zend_language_parser", "zend_language_scanner"):
        for suffix in (".lo", ".o"):
            (target / "Zend" / (name + suffix)).unlink(missing_ok=True)
    subprocess.run(["make", "-C", str(target), "-j4", "Zend/zend_language_parser.lo",
                    "EXTRA_CFLAGS=-DYYDEBUG=1 -fvisibility=default"], check=True)
    subprocess.run(["make", "-C", str(target), "-j4", "sapi/cli/php"], check=True)
    subprocess.run(["cc", "-shared", "-fPIC", "-o", str(ROOT / ".tools/trace-enable.so"),
                    str(ROOT / "tests/trace-enable.c"), "-ldl"], check=True)
    print("Optional coverage PHP built; ordinary .tools/php/bin/php remains unchanged")


if __name__ == "__main__":
    main()
