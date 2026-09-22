#!/usr/bin/env python3
"""Preserve explicit dependencies separately from exit observable agreements."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'ordinary-library': ('<?php strlen("x");', 'registered builtin call'),
    'traversable-protocol': ('<?php class I implements Iterator {function current():mixed{return 1;}function key():mixed{return 0;}function next():void{}function rewind():void{}function valid():bool{return false;}} exit(...new I);', 'class inheritance, interfaces, attributes, or members'),
    'closure-property': ('<?php $c=exit(...);$c->x=1;', 'Closure property write'),
}


def main():
    before = types.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='exit-controls-', dir=ROOT / '.tools'))
    rows = []
    for name, (source, reason) in CASES.items():
        path = out / (name + '.php')
        path.write_text(source)
        command = [str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '45']
        result = subprocess.run(command, cwd=out, env=types.ENV,
                                capture_output=True, timeout=55)
        (out / (name + '.stdout')).write_bytes(result.stdout)
        (out / (name + '.stderr')).write_bytes(result.stderr)
        actual = json.loads(result.stdout)
        assert result.returncode == 1 and not result.stderr, (name, result)
        assert actual['status'] == 'unsupported' and actual['reason'] == reason, (name, actual)
        assert actual['exit_status'] is None, (name, actual)
        rows.append({'id': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'command': command, 'result': actual, 'agreement_claim': False})
    assert before == types.syntax_validation.implementation_fingerprint()
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'fingerprint': before,
                                               'controls': rows, 'raw': str(out)}, indent=2) + '\n')
    print(out, '3 explicit Unsupported controls')


if __name__ == '__main__':
    main()
