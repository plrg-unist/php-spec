#!/usr/bin/env python3
"""Focused static lowering and compiled facts for no-constructor NEW arguments."""
from pathlib import Path
import base64
import json
import subprocess
import tempfile
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    'positional': b'<?php\nclass C{}\nnew C(1);\n',
    'append': b'<?php\nclass C{}\n$a=[]; new C($a[]);\n',
    'named': b'<?php\nclass C{}\nnew C(foo: 1);\n',
    'multiline_named': b'<?php\nclass C{} function side(){return 1;}\nnew C(\n  foo:\n  side()\n);\n',
    'unpack': b'<?php\nclass C{}\nnew C(...[1]);\n',
    'missing': b'<?php\nnew Missing($a[]);\n',
    'refreturn': b'<?php\nclass C{} $a=1; function &f(){global $a; return $a;} new C(f());\n',
    'dynamic': b'<?php\n$x="C"; new $x(1);\n',
    'placeholder': b'<?php\nclass C{}\nnew C(\n  ...\n);\n',
    'named_pos': b'<?php\nclass C{}\nnew C(\n foo: 1,\n 2\n);\n',
    'named_unpack': b'<?php\nclass C{}\nnew C(\n foo: 1,\n ...[2]\n);\n',
    'noarg': b'<?php\nclass C{}\nnew C();\n',
}
PREFIX = '''
dec $edit_new_send(pcodeexpr*, pcpath, nat) : pcodeexpr*
def $edit_new_send(eps, pcpath, n) = eps
def $edit_new_send((CODEEXPR pcpath z b) :: pcodeexpr_tail*, pcpath, 0) = pcodeexpr_tail*
def $edit_new_send((CODEEXPR pcpath z b) :: pcodeexpr_tail*, pcpath, 1) = [CODEEXPR pcpath z b, CODEEXPR pcpath z b] ++ pcodeexpr_tail*
def $edit_new_send((CODEEXPR pcpath z b) :: pcodeexpr_tail*, pcpath, 2) = (CODEEXPR pcpath $(z + 1) b) :: pcodeexpr_tail*
def $edit_new_send((CODEEXPR pcpath z b) :: pcodeexpr_tail*, pcpath, 3) = (CODEEXPR (pcpath ++ [PCFIELD 0]) z b) :: pcodeexpr_tail*
def $edit_new_send((CODEEXPR pcpath z false) :: pcodeexpr_tail*, pcpath, 4) = (CODEEXPR pcpath z true) :: pcodeexpr_tail*
def $edit_new_send((CODEEXPR pcpath z true) :: pcodeexpr_tail*, pcpath, 4) = (CODEEXPR pcpath z false) :: pcodeexpr_tail*
dec $new_send_here(pcodeexpr, pcpath) : bool
def $new_send_here(CODEEXPR pcpath z b, pcpath) = true
def $new_send_here(pcodeexpr, pcpath) = false -- otherwise
def $edit_new_send(pcodeexpr_head :: pcodeexpr_tail*, pcpath, n) = pcodeexpr_head :: $edit_new_send(pcodeexpr_tail*, pcpath, n)
  -- if ~$new_send_here(pcodeexpr_head, pcpath)
'''


def main():
    out = Path(tempfile.mkdtemp(prefix='noctor-compiler-', dir=ROOT / '.tools'))
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        fixtures = {}
        for name, source in SOURCES.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
            fixtures[name] = checked['fixture']
        filename = '[' + ','.join(map(str, str(out / 'source.php').encode())) + ']'
        checks = [f'n_file* = {filename}']
        for name in ('positional', 'append', 'named', 'multiline_named', 'unpack', 'missing', 'refreturn', 'noarg'):
            checks += [f'P_{name} = $ppstart(91, {fixtures[name]}, n_file*)',
                       f'P_{name}.COMPLETION = PPCNORMAL']
        checks += [
            'pcode = $ppfunction_code(P_positional)',
            '$code_expression(pcode.EXPRESSIONS, [PCINDEX 1, PCFIELD 0]) = ((3, false))',
            '$code_expression(pcode.EXPRESSIONS, [PCINDEX 1, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = ((3, true))',
            '$code_call_init(pcode.EXPRESSIONS, [PCINDEX 1, PCFIELD 0]) = eps',
            '$code_expression($ppfunction_code(P_refreturn).EXPRESSIONS, [PCINDEX 3, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = ((2, false))',
            '$code_expression($ppfunction_code(P_multiline_named).EXPRESSIONS, [PCINDEX 2, PCFIELD 0]) = ((3, false))',
            '$code_expression($ppfunction_code(P_multiline_named).EXPRESSIONS, [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = ((5, false))',
            '$occurrence_node(P_noarg.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1, PCFIELD 0]) = (NExprNew name_noarg phpType6_noarg metadata_noarg)',
            '$ppsend_var(NExprNew name_noarg phpType6_noarg metadata_noarg)',
            '$occurrence_node(P_positional.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1, PCFIELD 0]) = (NExprNew name_arg phpType6_arg metadata_arg)',
            '$ppsend_var(NExprNew name_arg phpType6_arg metadata_arg)',
            'pcpath_append = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]',
            '(CODEARG pcpath_append) <- $ppfunction_code(P_append).EXPRESSIONS',
            '$code_expression($ppfunction_code(P_noarg).EXPRESSIONS, [PCINDEX 1, PCFIELD 0]) = ((3, false))',
            'pcode_named = $ppfunction_code(P_named)',
            'pcpath_named = [PCINDEX 1, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]',
            '$named_send_root(P_named.FOLD.SOURCE.OCCURRENCES, pcpath_named)',
            '$send_unit_code_valid(P_named, pcode_named)',
            'S_named = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 91 n_file*]], P_named)',
            'S_named.COMPLETION = NORMAL',
            '$call_entry_check(S_named).COMPLETION = NORMAL',
            'S_multiline = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 91 n_file*]], P_multiline_named)',
            'S_multiline.COMPLETION = NORMAL',
            '$call_entry_check(S_multiline).COMPLETION = NORMAL',
        ]
        checks += [f'~$send_unit_code_valid(P_named, pcode_named[.EXPRESSIONS = $edit_new_send(pcode_named.EXPRESSIONS, pcpath_named, {i})])'
                   for i in range(5)]
        checks += ['S_bad = S_named[.CODE = [pcode_named[.EXPRESSIONS = $edit_new_send(pcode_named.EXPRESSIONS, pcpath_named, 2)]]]',
                   '$call_entry_check(S_bad).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
                   'pcode_multiline = $ppfunction_code(P_multiline_named)',
                   'S_bad_multiline = S_multiline[.CODE = [pcode_multiline[.EXPRESSIONS = $edit_new_send(pcode_multiline.EXPRESSIONS, [PCINDEX 2, PCFIELD 0], 2)]]]',
                   '$call_entry_check(S_bad_multiline).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
        errors = {'placeholder': ('Cannot create Closure for new expression', 3),
                  'named_pos': ('Cannot use positional argument after named argument', 4),
                  'named_unpack': ('Cannot use argument unpacking after named arguments', 4)}
        for name, (message, line) in errors.items():
            checks += [f'P_{name} = $ppstart(91, {fixtures[name]}, n_file*)',
                       f'P_{name}.COMPLETION = PPCABRUPT (STATICERROR "{message}" {line})']
        checks += [f'P_dynamic = $ppstart(91, {fixtures["dynamic"]}, n_file*)',
                   'P_dynamic.COMPLETION = PPCABRUPT (UNSUPPORTED "dynamic class target")']
        fixture = out / 'compiler.watsup'
        fixture.write_text(PREFIX + 'dec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *modules, str(fixture)], capture_output=True, text=True, timeout=120)
        (out / 'stdout').write_text(result.stdout)
        (out / 'stderr').write_text(result.stderr)
        assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result.stderr
        print(f'PASS noctor compiler: {len(checks)} assertions', out)
    finally:
        frontend.close()
        adapter.close()


if __name__ == '__main__':
    main()
