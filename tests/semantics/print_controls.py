#!/usr/bin/env python3
"""Unimplemented print dependencies remain Unsupported, not PHP agreement."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'stringable': '<?php class C {function __toString():string{return "X";}}print new C;',
    'missing-library': '<?php print strlen("X");',
}


def main():
    out = Path(tempfile.mkdtemp(prefix='print-controls-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, Path(__file__), ROOT / '_build/default/adapter/main.exe']
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    rows = []
    for name, source in CASES.items():
        path = out / (name + '.php')
        path.write_bytes(source.encode())
        command = [str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '45']
        process = subprocess.run(command, capture_output=True, env=types.ENV, timeout=55)
        (out / (name + '.stdout')).write_bytes(process.stdout)
        (out / (name + '.stderr')).write_bytes(process.stderr)
        actual = json.loads(process.stdout)
        assert process.returncode != 0 and actual['status'] == 'unsupported', (name, actual)
        rows.append({'name': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'command': command, 'exit_status': process.returncode, 'actual': actual})
    assert before == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'rows': rows, 'inputs': before}, indent=2) + '\n')
    print(out, '2 Unsupported controls pass')


if __name__ == '__main__':
    main()
