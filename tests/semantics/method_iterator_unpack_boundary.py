#!/usr/bin/env python3
"""Temporary user Iterator method unpack remains explicitly outside this slice."""
import hashlib
import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('method_iterator_unpack_temporary_control.php')
SOURCE_SHA = '83e531da96c793b178178f7f3d22b3c73adf9220a586b69392d30ea9ba3fd536'


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
    process = subprocess.run([str(ROOT / 'bin/php-semantics'), str(SOURCE),
                              '--steps', '100000', '--timeout', '30'],
                             cwd=SOURCE.parent, env=dict(os.environ, LC_ALL='C', TZ='UTC'),
                             capture_output=True, timeout=60)
    outcome = json.loads(process.stdout)
    assert process.returncode == 1 and process.stderr == b''
    assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
    assert outcome['status'] == 'unsupported'
    assert outcome['reason'] == 'Iterator unpack target or operand ownership'
    assert outcome['stdout'] == outcome['stderr'] == '' and outcome['events'] == []
    assert outcome['exit_status'] is None and outcome['diagnostic'] is None
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
    print('temporary-method-iterator-unpack explicit Unsupported')


if __name__ == '__main__':
    main()
