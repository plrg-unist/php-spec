#!/usr/bin/env python3
"""A failed runtime interface obligation leaves static class cells unpublished."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (b'<?php interface I { public function f(); } function go(){ '
          b'class A implements I { public static $x=1; } } go();')


def main():
    out = Path(tempfile.mkdtemp(prefix='class-static-interface-failure-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                         ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
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
        'ptbytes_message = $ptascii("Class A contains 1 abstract method and must therefore be declared abstract or implement the remaining method (I::f)")',
        'S.CLASSES = [pclassdesc_i,pclassdesc_a]',
        'pclassdesc_i.KIND = "interface" /\\ pclassdesc_a.KIND = "class"',
        'pclassdesc_a.PROPERTIES = [ppropertydesc_x]',
        'ppropertydesc_x.STATIC',
        'S.CLASSNAMES = [($ptascii("i"),pclassdesc_i.ORIGIN)]',
        'S.CLASSSTATICS = eps /\\ S.LINKEDINTERFACES = eps /\\ S.LINKEDPARENTS = eps',
        '$class_state_valid(S)',
        '$heap_valid($heap_graph(S))',
    ]
    fixture = out / 'protocol.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + x + '\n' for x in checks))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                             *map(str, modules), str(fixture)], capture_output=True, text=True, timeout=120)
    (out / 'stdout').write_text(result.stdout)
    (out / 'stderr').write_text(result.stderr)
    assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result.stderr[-3500:]
    assert before == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'inputs': before,
        'source_sha256': hashlib.sha256(SOURCE).hexdigest(), 'assertions': len(checks)}, indent=2) + '\n')
    print('PASS class static interface failure protocol', len(checks), out)


if __name__ == '__main__':
    main()
