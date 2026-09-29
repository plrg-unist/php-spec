#!/usr/bin/env python3
"""Source-derived static declaration storage and class-link integrity."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (b'<?php class A { private static int $x=1; protected static array $y=[2]; '
          b'public $z=3; } class B extends A { private static int $x=4; '
          b'public static $q=5; } $a=new B; echo "E";')


def main():
    out = Path(tempfile.mkdtemp(prefix='class-static-storage-', dir=ROOT / '.tools'))
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
        'S.COMPLETION = NORMAL',
        'S.CLASSES = [pclassdesc_a,pclassdesc_b]',
        'pclassdesc_a.PROPERTIES = [ppropertydesc_ax,ppropertydesc_ay,ppropertydesc_az]',
        'pclassdesc_b.PROPERTIES = [ppropertydesc_bx,ppropertydesc_bq]',
        'ppropertydesc_ax.STATIC /\\ ppropertydesc_ay.STATIC /\\ ppropertydesc_bx.STATIC /\\ ppropertydesc_bq.STATIC',
        '~ppropertydesc_az.STATIC',
        'ppropertydesc_ax.KEY = [0,65,0,120]',
        'ppropertydesc_ay.KEY = [0,42,0,121]',
        'ppropertydesc_bx.KEY = [0,66,0,120]',
        'S.CLASSSTATICS = [pclassstatic_ax,pclassstatic_ay,pclassstatic_bx,pclassstatic_bq]',
        'pclassstatic_ax.DECL = ppropertydesc_ax.ORIGIN',
        'pclassstatic_ay.DECL = ppropertydesc_ay.ORIGIN',
        'pclassstatic_bx.DECL = ppropertydesc_bx.ORIGIN',
        'pclassstatic_bq.DECL = ppropertydesc_bq.ORIGIN',
        'pclassstatic_ax.STATE = PROP_VALUE (DIRECT (PINT 1))',
        'pclassstatic_bx.STATE = PROP_VALUE (DIRECT (PINT 4))',
        'pclassstatic_ay.STATE = PROP_VALUE (DIRECT (PARRAY n_array))',
        '(HARRAY n_array) <- $class_static_roots(S.CLASSSTATICS)',
        '$property_layout(S, pclassdesc_b.ORIGIN, |S.CLASSES|) = [ppropertydesc_az]',
        '$class_state_valid(S)',
        '$heap_valid($heap_graph(S))',
        '~$class_state_valid(S[.CLASSSTATICS = S.CLASSSTATICS ++ [pclassstatic_ax]])',
        '~$class_state_valid(S[.CLASSSTATICS = [pclassstatic_ax,pclassstatic_ay,pclassstatic_bx]])',
        '~$class_state_valid(S[.CLASSSTATICS = [pclassstatic_ax,pclassstatic_ay,pclassstatic_bx,pclassstatic_bq[.DECL = ppropertydesc_az.ORIGIN]]])',
        '~$class_state_valid(S[.CLASSSTATICS = [pclassstatic_ax[.STATE = PROP_VALUE (DIRECT (PSTRING ([120])))],pclassstatic_ay,pclassstatic_bx,pclassstatic_bq]])',
        '~$class_state_valid(S[.CLASSES = [pclassdesc_a[.PROPERTIES = [ppropertydesc_ax[.STATIC = false],ppropertydesc_ay,ppropertydesc_az]],pclassdesc_b]])',
        '$class_static_initial(S[.POOLS = eps], pclassdesc_a.PROPERTIES) = eps',
        'S_missing = $activate_class(S[.CLASSNAMES = eps][.LINKEDPARENTS = eps][.CLASSSTATICS = eps][.POOLS = eps], pclassdesc_a)',
        'S_missing.COMPLETION = UNSUPPORTED "class static default storage"',
        'S_missing.CLASSNAMES = eps /\\ S_missing.LINKEDPARENTS = eps /\\ S_missing.CLASSSTATICS = eps',
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
    print('PASS class static storage protocol', len(checks), out)


if __name__ == '__main__':
    main()
