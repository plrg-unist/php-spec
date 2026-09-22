#!/usr/bin/env python3
"""Match compiler order, retained diagnostic lines and descriptor authentication."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads(Path(__file__).with_name('match_compiler_cases.json').read_text())
MATCH = '[PCINDEX 0, PCFIELD 0]'
CONDITION = MATCH[:-1] + ', PCFIELD 1, PCINDEX 0, PCFIELD 0, PCINDEX 0]'
BODY = MATCH[:-1] + ', PCFIELD 1, PCINDEX 0, PCFIELD 1]'
SUBJECT = MATCH[:-1] + ', PCFIELD 0]'
PREFIX = f'''
dec $match_edit_entry(pcodeexpr, nat) : pcodeexpr*
def $match_edit_entry(CODEMATCH_LINE pcpath z, 0) = [CODEMATCH_LINE pcpath 99]
def $match_edit_entry(CODEMATCH_LINE pcpath z, 1) = eps
def $match_edit_entry(CODEMATCH_LINE pcpath z, 2) = [CODEMATCH_LINE pcpath z, CODEMATCH_LINE pcpath z]
def $match_edit_entry(CODEMATCH_LINE pcpath z, 3) = [CODEMATCH_LINE (pcpath ++ [PCFIELD 0]) z]
def $match_edit_entry(CODEMATCH_TABLE pcpath b, 4) = [CODEMATCH_TABLE pcpath (~b)]
def $match_edit_entry(CODEMATCH_TABLE pcpath b, 5) = eps
def $match_edit_entry(CODEMATCH_TABLE pcpath b, 6) = [CODEMATCH_TABLE pcpath b, CODEMATCH_TABLE pcpath b]
def $match_edit_entry(CODEMATCH_TABLE pcpath b, 7) = [CODEMATCH_TABLE (pcpath ++ [PCFIELD 0]) b]
def $match_edit_entry(CODEEXPR pcpath z b, 8) = [CODEEXPR pcpath 99 b]
  -- if pcpath = {CONDITION}
def $match_edit_entry(CODEEXPR pcpath z b, 9) = [CODEEXPR pcpath 99 b]
  -- if pcpath = {BODY}
def $match_edit_entry(CODEEXPR pcpath z b, 10) = [CODEEXPR pcpath z (~b)]
  -- if pcpath = {SUBJECT}
def $match_edit_entry(CODEEXPR pcpath z b, 11) = eps
  -- if pcpath = {CONDITION}
def $match_edit_entry(CODEEXPR pcpath z b, 12) = [CODEEXPR pcpath z b, CODEEXPR pcpath z b]
  -- if pcpath = {BODY}
def $match_edit_entry(CODEEXPR pcpath z b, 13) = [CODEEXPR (pcpath ++ [PCFIELD 0]) z b]
  -- if pcpath = {SUBJECT}
def $match_edit_entry(pcodeexpr, n) = [pcodeexpr] -- otherwise
dec $match_edit(pcodeexpr*, nat) : pcodeexpr*
def $match_edit(eps, n) = eps
def $match_edit(pcodeexpr :: pcodeexpr_tail*, n) = $match_edit_entry(pcodeexpr, n) ++ $match_edit(pcodeexpr_tail*, n)
'''


def main():
    before = types.syntax_validation.implementation_fingerprint()
    output = Path(tempfile.mkdtemp(prefix='match-compiler-', dir=ROOT / '.tools'))
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], output / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                     output / 'adapter')
    profile = json.loads(Path(__file__).with_name('profile.json').read_text())
    oracle = [str(ROOT / '.tools/php/bin/php'), '-n']
    for key, value in profile.items():
        oracle += ['-d', f'{key}={value}']
    records, fixtures = [], []
    assertions_count = 0
    lines = {'line_dynamic': (False, 5), 'line_subject': (True, 3),
             'line_nojump': (False, 2), 'line_jump': (True, 2),
             'line_dynamic_before_literal': (False, 4)}
    try:
        for name, source in CASES.items():
            path = output / (name + '.php')
            path.write_text(source)
            native = subprocess.run([*oracle, '-l', str(path)], capture_output=True,
                                    text=True, timeout=30, env=types.ENV, cwd=output)
            records.append({'name': name, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                            'command': [*oracle, '-l', str(path)], 'cwd': str(output), 'exit': native.returncode,
                            'stdout': native.stdout, 'stderr': native.stderr})
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.encode()).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
            assertions = []
            if name == 'dup_subject_static':
                line, error = 2, 'A void function must not return a value'
                assertions += [f'P.COMPLETION = PPCABRUPT (STATICBYTES $ptascii("{error}") {line})']
            elif name.startswith('dup_'):
                line = {'dup_nan_fold': 4, 'dup_nan_fold_stop': 5, 'dup_cond_static': 2}[name]
                error = 'Match expressions may only contain one default arm'
                assertions += [f'P.COMPLETION = PPCABRUPT (STATICERROR "{error}" {line})']
            elif name.startswith('temporary_'):
                line, error = 1, 'Cannot use temporary expression in write context'
                assertions += [f'P.COMPLETION = PPCABRUPT (STATICERROR "{error}" {line})']
            else:
                error = None
                assertions += ['P.COMPLETION = PPCNORMAL', '$call_declarations(P.FOLD.SOURCE.OCCURRENCES)']
                if name != 'reference_return':
                    assertions += ['$match_unit_code_valid(P, pcode)']
            if error:
                assert native.returncode == 255 and error in native.stderr, records[-1]
                assert f'on line {line}' in native.stderr, records[-1]
            else:
                assert native.returncode == 0 and not native.stderr, records[-1]
            if name == 'dup_nan_fold':
                warning = 'unexpected NAN value was coerced to bool'
                assert warning in native.stderr and native.stderr.index(warning) < native.stderr.index(error), records[-1]
                assertions += ['P.DIAGNOSTICS = [PLDIAGNOSTIC "warning" "constant-warning" ([ptbytes]) pllocation]',
                               'pllocation.LINE = 2', f'ptbytes = $ptascii("{warning}")']
            else:
                assertions += ['P.DIAGNOSTICS = eps']
            if name in lines:
                table, line = lines[name]
                assertions += [f'$code_match_table(pcode.EXPRESSIONS, {MATCH}) = ({str(table).lower()})',
                               f'$code_match_line(pcode.EXPRESSIONS, {MATCH}) = ({line})']
            if name == 'line_jump':
                assertions += [f'$code_match_line(pcode.EXPRESSIONS, {CONDITION}) = (2)',
                               f'$code_match_line(pcode.EXPRESSIONS, {BODY}) = (3)']
                assertions += [f'$match_unit_code_valid(P, pcode[.EXPRESSIONS = $match_edit(pcode.EXPRESSIONS, {mode})]) = false'
                               for mode in range(14)]
            file_bytes = '[' + ','.join(map(str, path.as_posix().encode())) + ']'
            fixtures.append('dec $case' + str(len(fixtures)) + '() : bool\ndef $case' + str(len(fixtures)) +
                            '() = true\n  -- if P = $ppstart(91, ' + checked['fixture'] + ', ' + file_bytes + ')\n'
                            '  -- if pcode = $ppfunction_code(P)\n' +
                            ''.join('  -- if ' + assertion + '\n' for assertion in assertions))
            assertions_count += len(assertions)
        fixture = output / 'compiler.watsup'
        fixture.write_text(PREFIX + ''.join(fixtures) + 'dec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $case' + str(i) + '()\n' for i in range(len(fixtures))))
        modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *modules, str(fixture)], capture_output=True, text=True, timeout=120)
        assert before == types.syntax_validation.implementation_fingerprint(), 'inputs changed during compiler gate'
        (output / 'result.json').write_text(json.dumps({'oracle': records, 'profile': profile, 'fingerprint': before,
                    'binary_sha256': hashlib.sha256((ROOT / '.tools/php/bin/php').read_bytes()).hexdigest(),
                    'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
                    'assertions': assertions_count, 'returncode': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr}, indent=2) + '\n')
        assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, (result.stdout, result.stderr)
    finally:
        frontend.close()
        adapter.close()
    print(f'{len(CASES)} match compiler sources, {assertions_count} assertions including 14 forged descriptors passed; {output}')


if __name__ == '__main__':
    main()
