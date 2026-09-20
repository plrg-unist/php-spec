#!/usr/bin/env python3
"""Switch boolean-subject compiler fact and projection checks."""
import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tests'))
from validate import ROOT, Worker, require

CASES = [
    (b'<?php switch (true) { case 1: }', 0, '(true)'),
    (b'<?php switch (1 === 1) { case 1: }', 0, '(true)'),
    (b'<?php switch (false) { case 1: }', 0, '(false)'),
    (b'<?php $x=true; switch ($x) { case 1: }', 1, 'eps'),
]
EDIT = '''
dec $is_bool_marker(pcodeexpr) : bool
def $is_bool_marker(CODESWITCH_BOOL pcpath b) = true
def $is_bool_marker(pcodeexpr) = false -- otherwise
dec $edit_bool(pcodeexpr*, nat) : pcodeexpr*
def $edit_bool(eps, n) = eps
def $edit_bool((CODESWITCH_BOOL pcpath b) :: pcodeexpr*, 0) = pcodeexpr*
def $edit_bool((CODESWITCH_BOOL pcpath b) :: pcodeexpr*, 1) = (CODESWITCH_BOOL pcpath false) :: pcodeexpr*
def $edit_bool((CODESWITCH_BOOL pcpath b) :: pcodeexpr*, 2) = [CODESWITCH_BOOL pcpath b, CODESWITCH_BOOL pcpath b] ++ pcodeexpr*
def $edit_bool((CODESWITCH_BOOL pcpath b) :: pcodeexpr*, 3) = [CODESWITCH_BOOL (pcpath ++ [PCFIELD 0]) b, CODESWITCH_BOOL pcpath b] ++ pcodeexpr*
def $edit_bool(pcodeexpr :: pcodeexpr_tail*, n) = pcodeexpr :: $edit_bool(pcodeexpr_tail*, n)
  -- if ~$is_bool_marker(pcodeexpr)
'''


def main():
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', str(ROOT / 'frontend/worker.php')])
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    try:
        with tempfile.TemporaryDirectory(dir=ROOT / '.tools', prefix='switch-bool-check-') as directory:
            directory = Path(directory)
            checks = []
            for i, (source, index, expected) in enumerate(CASES):
                ast = require(frontend.call(op='parse', source=base64.b64encode(source).decode()), 'parse')['ast']
                fixture = require(adapter.call(op='check', ast=ast, fixture=True), 'check')['fixture']
                path = directory / f'{i}.php'
                path.write_bytes(source)
                path_bytes = '[' + ','.join(map(str, str(path).encode())) + ']'
                body = (f'dec $check{i}() : bool\ndef $check{i}() = true\n'
                        f'  -- if P = $ppstart(91, {fixture}, {path_bytes})\n'
                        '  -- if pcode = $ppfunction_code(P)\n'
                        f'  -- if $code_switch_bool(pcode.EXPRESSIONS, [PCINDEX {index}]) = {expected}\n'
                        '  -- if $switch_unit_code_valid(P, pcode)\n')
                if i == 0:
                    body += ''.join(
                        '  -- if $switch_unit_code_valid(P, '
                        f'pcode[.EXPRESSIONS = $edit_bool(pcode.EXPRESSIONS, {mode})]) = false\n'
                        for mode in range(4))
                checks.append(body)
            program = (EDIT + ''.join(checks) + 'dec $main() : bool\ndef $main() = true\n'
                       + ''.join(f'  -- if $check{i}()\n' for i in range(len(CASES))))
            fixture_file = directory / 'checks.watsup'
            fixture_file.write_text(program)
            modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                     *modules, str(fixture_file)], capture_output=True, text=True, timeout=120)
            assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result
    finally:
        frontend.close()
        adapter.close()
    print('4 switch bool facts and 4 missing/inverted/duplicate/foreign projections passed')


if __name__ == '__main__':
    main()
