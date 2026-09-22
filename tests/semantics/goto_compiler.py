#!/usr/bin/env python3
"""Goto code projections, callable scope and label-only source recheck."""
from pathlib import Path
import base64
import json
import subprocess
import tempfile
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    'jump': b'<?php\ngoto Target;\nTarget: echo "yes";\n',
    'label': b'<?php\nL:\n',
    'duplicate': b'<?php\nL:\nL:\n',
    'nested': b'<?php\nfunction f() { goto L; L: }\ngoto O; O:\n',
}
PREFIX = '''
dec $edit_goto(pcodeexpr, nat) : pcodeexpr*
def $edit_goto(CODEGOTO pcpath_src pcpath_dest, 0) = eps
def $edit_goto(CODEGOTO pcpath_src pcpath_dest, 1) = [CODEGOTO pcpath_src pcpath_dest, CODEGOTO pcpath_src pcpath_dest]
def $edit_goto(CODEGOTO pcpath_src pcpath_dest, 2) = [CODEGOTO (pcpath_src ++ [PCFIELD 0]) pcpath_dest]
def $edit_goto(CODEGOTO pcpath_src pcpath_dest, 3) = [CODEGOTO pcpath_src (pcpath_dest ++ [PCFIELD 0])]
def $edit_goto(pcodeexpr, n) = [pcodeexpr] -- otherwise
dec $edit_gotos(pcodeexpr*, nat) : pcodeexpr*
def $edit_gotos(eps, n) = eps
def $edit_gotos(pcodeexpr :: pcodeexpr_tail*, n) = $edit_goto(pcodeexpr, n) ++ $edit_gotos(pcodeexpr_tail*, n)
'''


def main():
    output = Path(tempfile.mkdtemp(prefix='goto-compiler-', dir=ROOT / '.tools'))
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], output / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                     output / 'adapter')
    try:
        fixtures = {}
        for name, source in SOURCES.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
            fixtures[name] = checked['fixture']
        filename = '[' + ','.join(map(str, str(output / 'source.php').encode())) + ']'
        checks = [
            f'n_file* = {filename}',
            f'P = $ppstart(91, {fixtures["jump"]}, n_file*)',
            'P.COMPLETION = PPCNORMAL',
            'pcode = $ppfunction_code(P)',
            '$goto_code(pcode.EXPRESSIONS) = [CODEGOTO ([PCINDEX 0]) ([PCINDEX 1])]',
            '$goto_unit_code_valid(P, pcode)',
            'S = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 91 n_file*]], P)',
            'S.COMPLETION = NORMAL',
            '$call_entry_check(S).COMPLETION = NORMAL',
        ]
        checks += [f'~$goto_unit_code_valid(P, pcode[.EXPRESSIONS = $edit_gotos(pcode.EXPRESSIONS, {i})])'
                   for i in range(4)]
        checks += [
            f'P_label = $ppstart(92, {fixtures["label"]}, n_file*)',
            'P_label.COMPLETION = PPCNORMAL',
            '$call_declarations(P_label.FOLD.SOURCE.OCCURRENCES)',
            'S_label = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 92 n_file*]], P_label)',
            'S_label.COMPLETION = NORMAL',
            f'S_bad = S_label[.SOURCES = [$pcsource(92, {fixtures["duplicate"]})]]',
            '$call_entry_check(S_bad).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
            f'P_nested = $ppstart(93, {fixtures["nested"]}, n_file*)',
            'P_nested.COMPLETION = PPCNORMAL',
            '$goto_code($ppfunction_code(P_nested).EXPRESSIONS) = [CODEGOTO ([PCINDEX 1]) ([PCINDEX 2])]',
            'P_nested.FUNCTIONS = [pfunction]',
            '$goto_code(pfunction.CODE.EXPRESSIONS) = [CODEGOTO ([PCINDEX 0, PCFIELD 5, PCINDEX 0]) ([PCINDEX 0, PCFIELD 5, PCINDEX 1])]',
        ]
        fixture = output / 'compiler.watsup'
        fixture.write_text(PREFIX + 'dec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *modules, str(fixture)], capture_output=True, text=True, timeout=120)
        assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result.stderr
        print(f'PASS goto compiler: {len(checks)} assertions', output)
    finally:
        frontend.close()
        adapter.close()


if __name__ == '__main__':
    main()
