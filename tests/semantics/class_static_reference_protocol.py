#!/usr/bin/env python3
"""A typed static alias retains an authenticated declaration source."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = b'<?php class A { public static int $x=1; } $r =& A::$x; $r=9;'


def main():
    out = Path(tempfile.mkdtemp(prefix='class-static-reference-protocol-', dir=ROOT / '.tools'))
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
        'S.COMPLETION = NORMAL',
        'S.CLASSES = [pclassdesc_a]',
        'pclassdesc_a.PROPERTIES = [ppropertydesc_x]',
        'ppropertydesc_x.STATIC /\\ ppropertydesc_x.TYPE =/= eps',
        'S.CLASSSTATICS = [pclassstatic_x]',
        'pclassstatic_x.DECL = ppropertydesc_x.ORIGIN',
        'pclassstatic_x.STATE = PROP_VALUE (ALIAS n_cell)',
        'S.PROPREFS = [ppropref]',
        'ppropref.CELL = n_cell',
        'ppropref.SOURCES = [CLASS_PROP_SOURCE ppropertydesc_x.ORIGIN]',
        'S.STORE[n_cell] = DEFINED (PINT 9)',
        '$class_statics_valid(S) /\\ $proprefs_valid(S) /\\ $class_state_valid(S)',
        '$heap_valid($heap_graph(S))',
        '~$class_statics_valid(S[.PROPREFS = eps])',
        '~$propref_source_valid(S,n_cell,CLASS_PROP_SOURCE (INTERNAL_PROPERTY "Exception" ($ptascii("message"))))',
        '~$class_statics_valid(S[.CLASSSTATICS = [pclassstatic_x[.STATE = PROP_VALUE (ALIAS $(n_cell + 1))]]])',
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
    print('PASS class static reference protocol', len(checks), out)


if __name__ == '__main__':
    main()
