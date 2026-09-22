#!/usr/bin/env python3
"""Public property descriptors, defaults, static phase and access facts."""
from pathlib import Path
import base64
import copy
import json
import subprocess
import tempfile
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / 'tests/semantics/property_compiler_cases.json').read_text())
SOURCES = {
    'typed': b'<?php class C { public int $x; }',
    'untyped': b'<?php class C { public $x; }',
    'array': b'<?php class C { public array $x=[1,2]; }',
    'two': b'<?php class C { public int $a=1,$b=2; } echo "B";',
    'read': b'<?php class C { public $x; } $o=new C; echo $o->x;',
    'write': b'<?php class C { public $x; } $o=new C; $o->x=2;',
    'computed': b'<?php class C { public $x; } $o=new C; $n="x"; echo $o->{$n};',
    'reference': b'<?php class C { public $x; } $o=new C; $o->x =& $a;',
}


def run():
    out = Path(tempfile.mkdtemp(prefix='property-compiler-', dir=ROOT / '.tools'))
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        cases = dict(SOURCES)
        for row in CASES:
            cases[row['name']] = row['source'].encode()
        assertions = {}
        for name, source in cases.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
            original = out / f'{name}.php'
            original.write_bytes(source)
            filename = '[' + ','.join(map(str, str(original).encode())) + ']'
            begin = [f'n_file* = {filename}', f'P = $ppstart(91, {checked["fixture"]}, n_file*)']
            tests = ['P.COMPLETION = PPCNORMAL']
            if name in ('typed', 'untyped', 'array'):
                tests += ['P.CLASSES = [pclassdesc]', 'pclassdesc.PROPERTIES = [ppropertydesc]',
                          'ppropertydesc.ORIGIN = PORIGIN 91 ([PCINDEX 0, PCFIELD 5, PCINDEX 0, PCFIELD 3, PCINDEX 0])',
                          'ppropertydesc.NAME = $ptascii("x")', 'ppropertydesc.LINE = 1', 'P.FOLD.VALUE = eps']
                tests.append('ppropertydesc.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]' if name == 'typed' else
                             'ppropertydesc.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]' if name == 'array' else 'ppropertydesc.TYPE = eps')
                tests.append('ppropertydesc.DEFAULT = PROP_UNINITIALIZED' if name == 'typed' else
                             'ppropertydesc.DEFAULT = PROP_NULL' if name == 'untyped' else
                             'ppropertydesc.DEFAULT = PROP_STORED (PORIGIN 91 ([PCINDEX 0, PCFIELD 5, PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 1]))')
            elif name == 'two':
                tests += ['P.CLASSES = [pclassdesc]', 'pclassdesc.PROPERTIES = [ppropertydesc_a,ppropertydesc_b]',
                          'ppropertydesc_a.NAME = $ptascii("a")', 'ppropertydesc_b.NAME = $ptascii("b")',
                          'ppropertydesc_a.DEFAULT = PROP_STORED (PORIGIN 91 ([PCINDEX 0, PCFIELD 5, PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 1]))',
                          'ppropertydesc_b.DEFAULT = PROP_STORED (PORIGIN 91 ([PCINDEX 0, PCFIELD 5, PCINDEX 0, PCFIELD 3, PCINDEX 1, PCFIELD 1]))']
            elif name == 'read':
                tests += ['([PCINDEX 2, PCFIELD 0, PCINDEX 0], PPR) <- P.ACCESS']
            elif name == 'write':
                tests += ['([PCINDEX 2, PCFIELD 0, PCFIELD 0], PPW) <- P.ACCESS']
            elif name == 'computed':
                tests += ['([PCINDEX 3, PCFIELD 0, PCINDEX 0], PPR) <- P.ACCESS',
                          '([PCINDEX 3, PCFIELD 0, PCINDEX 0, PCFIELD 1], PPR) <- P.ACCESS']
            assertions[name] = (begin, tests)
            if name == 'typed':
                for suffix, field, value in [('missing-line', 'startLine', None),
                                             ('zero-line', 'startLine', 0),
                                             ('inverted-range', 'endLine', 0)]:
                    edited = copy.deepcopy(parsed['ast'])
                    group = edited['program'][0]['fields'][5][0]
                    if value is None:
                        group['meta'].pop(field)
                    else:
                        group['meta'][field] = {'int': str(value)}
                    malformed = adapter.request({'op': 'check', 'ast': edited, 'fixture': True})
                    assert malformed['ok'], (suffix, malformed)
                    assertions[suffix] = ([f'n_file* = {filename}',
                                           f'P = $ppstart(91, {malformed["fixture"]}, n_file*)'],
                                          ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing property compiler line")'])
        for row in CASES:
            if 'static_message' in row:
                text = row['static_message']
                line = row['static_line']
                tests = assertions[row['name']][1]
                error = (f'STATICERROR {json.dumps(text)}' if row['static_kind'] == 'STATICERROR' else
                         f'STATICBYTES $ptascii({json.dumps(text)})')
                tests[:] = [f'P.COMPLETION = PPCABRUPT ({error} {line})']
        assertions['override-type-equivalence'] = ([], [
            '$ppproperty_type_equal([PTBRANCH ([PTBUILTIN "int"]), PTBRANCH ([PTBUILTIN "string"])], [PTBRANCH ([PTBUILTIN "string"]), PTBRANCH ([PTBUILTIN "int"])]) = true',
            '$ppproperty_type_equal([PTBRANCH ([PTCLASS ($ptascii("A"))])], [PTBRANCH ([PTCLASS ($ptascii("a"))])]) = true',
            '$ppproperty_type_equal([PTBRANCH ([PTBUILTIN "int"]), PTBRANCH ([PTBUILTIN "null"])], [PTBRANCH ([PTBUILTIN "null"]), PTBRANCH ([PTBUILTIN "int"])]) = true',
            '$ppproperty_type_equal([PTBRANCH ([PTBUILTIN "int"])], [PTBRANCH ([PTBUILTIN "string"])]) = false',
        ])
        assertions['reference'][1][:] = ['P.COMPLETION = PPCNORMAL',
                                         '([PCINDEX 2, PCFIELD 0, PCFIELD 0], PPW) <- P.ACCESS']
        modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        count = 0
        for name, (begin, tests) in assertions.items():
            fixture = out / f'{name}.watsup'
            fixture.write_text('dec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + line + '\n' for line in begin + tests))
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                     *modules, str(fixture)], capture_output=True, text=True, timeout=120)
            (out / f'{name}.stdout').write_text(result.stdout)
            (out / f'{name}.stderr').write_text(result.stderr)
            assert result.returncode == 0 and result.stdout == 'true\n', (name, result.stderr)
            count += len(begin + tests)
        print(f'PASS property compiler: {count} assertions', out)
    finally:
        frontend.close()
        adapter.close()


if __name__ == '__main__':
    run()
