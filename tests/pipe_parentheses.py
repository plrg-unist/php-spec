#!/usr/bin/env python3
"""Pipe arrow grouping survives checked syntax and rejects at compile phase."""
import base64
import copy
import json
from pathlib import Path
import subprocess
import tempfile

from validate import ROOT, Worker, require, normalize, structurally_equal

MESSAGE = 'Arrow functions on the right hand side of |> must be parenthesized'
CASES = [
    (b'<?php echo 2 |> fn($x) => $x + 1;', True, 1),
    (b'<?php echo 2 |> (fn($x) => $x + 1);', False, 1),
    (b'<?php\necho 2 |>\n    fn($x) => $x + 1;', True, 2),
    (b'<?php\necho 1 |> fn(): void => 1;', True, 2),
    (b'<?php echo 1 |> static fn($x) => $x;', True, 1),
    (b'<?php echo 1 |> (static fn($x) => $x);', False, 1),
    (b'<?php echo 1 |> fn&($x) => $x;', True, 1),
    (b'<?php echo 1 |> (fn&($x) => $x);', False, 1),
]


def pipe(ast):
    return ast['program'][0]['fields'][0][0]


def main():
    php = ROOT / '.tools/php/bin/php'
    frontend = Worker([str(php), '-n', str(ROOT / 'frontend/worker.php')])
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    try:
        with tempfile.TemporaryDirectory(dir=ROOT / '.tools') as directory:
            directory = Path(directory)
            for index, (source, bare, line) in enumerate(CASES):
                parsed = require(frontend.call(op='parse', source=base64.b64encode(source).decode()), 'parse')
                assert parsed['accepted'], parsed
                ast = parsed['ast']
                assert pipe(ast)['node'] == 'Expr_BinaryOp_Pipe'
                assert pipe(ast)['meta']['pipeBareArrow'] is bare
                checked = require(adapter.call(op='check', ast=ast, fixture=True), 'check')
                assert checked['ast'] == ast
                printed = require(frontend.call(op='print', ast=checked['ast']), 'print')
                reparsed = require(frontend.call(op='parse', source=printed['source']), 'reparse')
                assert reparsed['accepted'] and pipe(reparsed['ast'])['meta']['pipeBareArrow'] is bare
                assert structurally_equal(normalize(ast), normalize(reparsed['ast']))
                file = directory / f'pipe-{index}.php'
                file.write_bytes(source)
                native = subprocess.run([str(php), '-n', '-l', str(file)], capture_output=True, text=True, timeout=10)
                printed_file = directory / f'pipe-printed-{index}.php'
                printed_file.write_bytes(base64.b64decode(printed['source']))
                printed_native = subprocess.run([str(php), '-n', '-l', str(printed_file)], capture_output=True, text=True, timeout=10)
                assert printed_native.returncode == native.returncode
                if bare:
                    assert native.returncode == 255 and MESSAGE in native.stdout and f'on line {line}' in native.stdout
                    assert MESSAGE in printed_native.stdout
                    model = subprocess.run([str(ROOT / 'bin/php-semantics'), str(file)], capture_output=True, text=True, timeout=30)
                    result = json.loads(model.stdout)
                    assert result['status'] == 'static_rejection' and result['exit_status'] == 255
                    assert result['diagnostic']['line'] == line
                    assert base64.b64decode(result['diagnostic']['message']).decode() == MESSAGE
                else:
                    assert native.returncode == 0
                if index == 0:
                    edited = copy.deepcopy(ast)
                    pipe(edited)['meta'].pop('pipeBareArrow')
                    fixture = require(adapter.call(op='check', ast=edited, fixture=True), 'edited')['fixture']
                    for malformed in (None, {'int': '1'}, 1, 'true'):
                        edited_bad = copy.deepcopy(ast)
                        pipe(edited_bad)['meta']['pipeBareArrow'] = malformed
                        assert not adapter.call(op='check', ast=edited_bad).get('ok')
                    test = directory / 'missing.watsup'
                    test.write_text('dec $main() : bool\ndef $main() = true\n'
                                    f'  -- if P = $ppstart(91, {fixture}, [112,105,112,101,46,112,104,112])\n'
                                    '  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing pipe arrow grouping")\n')
                    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
                    runner = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(test)], capture_output=True, text=True, timeout=120)
                    assert runner.returncode == 0 and runner.stdout == 'true\n' and not runner.stderr, runner
    finally:
        frontend.close()
        adapter.close()
    print('8 pipe arrow source/roundtrip/lint profiles and missing-fact compiler control passed')


if __name__ == '__main__':
    main()
