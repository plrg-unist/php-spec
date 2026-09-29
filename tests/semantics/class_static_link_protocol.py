#!/usr/bin/env python3
"""A failed runtime class link does not publish its static declarations."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (b'<?php class A { public static $x=1; } function f(){ class B extends A '
          b'{ public static $y=2; public $x=3; } } f();')


def main():
    out = Path(tempfile.mkdtemp(prefix='class-static-link-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                         ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    source = out / 'source.php'
    source.write_bytes(SOURCE)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        frontend.close()
        adapter.close()
    initial = ('$php_run(' + checked['fixture'] + ', 0, '
               + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')')
    checks = [
        'S_initial = ' + initial,
        'S = $drive(S_initial[.COMPLETION = NORMAL], 2048)',
        'S.COMPLETION = FATAL ptbytes_message 1',
        'ptbytes_message = $ptascii("Cannot redeclare static A::$x as non static B::$x")',
        'S.CLASSES = [pclassdesc_a,pclassdesc_b]',
        'pclassdesc_a.PROPERTIES = [ppropertydesc_ax]',
        'pclassdesc_b.PROPERTIES = [ppropertydesc_by,ppropertydesc_bx]',
        'S.CLASSNAMES = [($ptascii("a"),pclassdesc_a.ORIGIN)]',
        'S.CLASSSTATICS = [pclassstatic_ax]',
        'pclassstatic_ax.DECL = ppropertydesc_ax.ORIGIN',
        '$class_static_at(S.CLASSSTATICS, ppropertydesc_by.ORIGIN) = eps',
        '$class_state_valid(S)',
        '$heap_valid($heap_graph(S))',
    ]
    fixture = out / 'protocol.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + x + '\n' for x in checks))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                             *map(str, modules), str(fixture)], capture_output=True, text=True, timeout=180)
    (out / 'stdout').write_text(result.stdout)
    (out / 'stderr').write_text(result.stderr)
    (out / 'status.json').write_text(json.dumps({'exit_status': result.returncode}))
    assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result.stderr[-3500:]
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == digest for p, digest in hashes.items())
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'inputs': hashes,
        'source_sha256': hashlib.sha256(SOURCE).hexdigest(), 'assertions': len(checks)}, indent=2) + '\n')
    print('PASS class static link protocol', len(checks), out)


if __name__ == '__main__':
    main()
