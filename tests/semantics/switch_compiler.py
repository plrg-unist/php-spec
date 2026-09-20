#!/usr/bin/env python3
"""Switch compile priority, case lines, and authenticated descriptors."""
from pathlib import Path
import base64
import copy
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from recorded_worker import Worker

CASES = json.loads(Path(__file__).with_name('switch_compiler_cases.json').read_text())
CASE_PATH = '[PCINDEX 5, PCFIELD 1, PCINDEX 0]'
COND_PATH = '[PCINDEX 5, PCFIELD 1, PCINDEX 0, PCFIELD 0]'
PREFIX = f'''
dec $edit_head(pcodeexpr, nat) : pcodeexpr*
def $edit_head(CODESWITCH_COMPARE pcpath z, 0) = [CODESWITCH_COMPARE pcpath 99]
def $edit_head(CODESWITCH_COMPARE pcpath z, 1) = eps
def $edit_head(CODESWITCH_COMPARE pcpath z, 2) = [CODESWITCH_COMPARE pcpath z, CODESWITCH_COMPARE pcpath z]
def $edit_head(CODESWITCH_COMPARE pcpath z, 3) = [CODESWITCH_COMPARE (pcpath ++ [PCFIELD 0]) z]
def $edit_head(CODEEXPR pcpath z b, 4) = [CODEEXPR pcpath 99 b]
  -- if pcpath = {COND_PATH}
def $edit_head(pcodeexpr, n) = [pcodeexpr] -- otherwise
dec $edit(pcodeexpr*, nat) : pcodeexpr*
def $edit(eps, n) = eps
def $edit(pcodeexpr :: pcodeexpr_tail*, n) = $edit_head(pcodeexpr, n) ++ $edit(pcodeexpr_tail*, n)
'''


def main():
    output = Path(tempfile.mkdtemp(prefix='switch-compiler-', dir=ROOT / '.tools'))
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], output / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                     output / 'adapter')
    fixtures = []
    try:
        for name, source in CASES.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.encode()).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
            path = output / (name + '.php')
            path.write_text(source)
            file_bytes = '[' + ','.join(map(str, path.as_posix().encode())) + ']'
            assertions = ['P.SWITCHES = eps', 'P.LOOPS = 0']
            if name in ('semicolon-duplicate-priority', 'prepass-dynamic'):
                line = 6 if name == 'semicolon-duplicate-priority' else 5
                assertions += [f'P.COMPLETION = PPCABRUPT (STATICERROR "Switch statements may only contain one default clause" {line})', '|P.DIAGNOSTICS| = 1']
            elif name == 'prepass-literal':
                assertions += ['P.COMPLETION = PPCABRUPT (STATICERROR "Cannot use [] for reading" 2)', 'P.DIAGNOSTICS = eps']
            elif name == 'prepass-warning':
                assertions += ['P.COMPLETION = PPCABRUPT (STATICERROR "Cannot use [] for reading" 2)',
                               'P.DIAGNOSTICS = [PLDIAGNOSTIC "warning" "constant-warning" ([ptbytes]) pllocation]',
                               'pllocation.LINE = 2',
                               'ptbytes = $ptascii("unexpected NAN value was coerced to bool")']
            elif name == 'prepass-warning-normal':
                assertions += ['P.COMPLETION = PPCNORMAL',
                               'P.DIAGNOSTICS = [PLDIAGNOSTIC "warning" "constant-warning" ([ptbytes_warning]) pllocation_warning, PLDIAGNOSTIC "deprecated" "switch-case-semicolon" eps pllocation_deprecated]',
                               'pllocation_warning.LINE = 2',
                               'pllocation_deprecated.LINE = 3',
                               'ptbytes_warning = $ptascii("unexpected NAN value was coerced to bool")']
            else:
                assertions += ['P.COMPLETION = PPCNORMAL']
            if name.startswith('continue-'):
                assertions += ['|P.DIAGNOSTICS| = 1']
            if name == 'nested-callable-boundary':
                assertions += ['P.DIAGNOSTICS = [PLDIAGNOSTIC "warning" "continue-switch" ([ptbytes]) pllocation]',
                               'pllocation.LINE = 7',
                               'ptbytes = $ptascii("\\\"continue\\\" targeting switch is equivalent to \\\"break\\\"")']
            if name == 'comparison-multiline':
                assertions += [f'$code_switch_compare($ppfunction_code(P).EXPRESSIONS, {CASE_PATH}) = (9)',
                               f'$code_expression($ppfunction_code(P).EXPRESSIONS, {COND_PATH}) = ((8, false))',
                               'pcode = $ppfunction_code(P)', '$switch_unit_code_valid(P, pcode)']
                assertions += [f'$switch_unit_code_valid(P, pcode[.EXPRESSIONS = $edit(pcode.EXPRESSIONS, {mode})]) = false'
                               for mode in range(5)]
            if name == 'switch-only':
                assertions += ['$call_declarations(P.FOLD.SOURCE.OCCURRENCES)',
                               '$code_switch_compare($ppfunction_code(P).EXPRESSIONS, [PCINDEX 0, PCFIELD 1, PCINDEX 0]) = (1)',
                               '$switch_unit_code_valid(P, $ppfunction_code(P))']
            fixtures.append('dec $case' + str(len(fixtures)) + '() : bool\ndef $case' + str(len(fixtures)) +
                            '() = true\n  -- if P = $ppstart(91, ' + checked['fixture'] + ', ' + file_bytes + ')\n' +
                            ''.join('  -- if ' + assertion + '\n' for assertion in assertions))
            if name == 'comparison-multiline':
                edited = copy.deepcopy(parsed['ast'])
                edited['program'][5]['fields'][1][0]['meta'].pop('caseSemicolon')
                missing = adapter.request({'op': 'check', 'ast': edited, 'fixture': True})
                assert missing['ok'], missing
                fixtures.append('dec $case' + str(len(fixtures)) + '() : bool\ndef $case' + str(len(fixtures)) +
                                '() = true\n  -- if P = $ppstart(91, ' + missing['fixture'] + ', ' + file_bytes + ')\n'
                                '  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing switch case separator")\n')
        fixture = output / 'compiler.watsup'
        fixture.write_text(PREFIX + ''.join(fixtures) + 'dec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $case' + str(i) + '()\n' for i in range(len(fixtures))))
        modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *modules, str(fixture)], capture_output=True, text=True, timeout=120)
        assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, (result.stdout, result.stderr)
    finally:
        frontend.close()
        adapter.close()
    print('10 switch compiler sources, 1 edited missing fact, and 5 descriptor edits passed')


if __name__ == '__main__':
    main()
