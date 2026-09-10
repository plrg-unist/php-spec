#!/usr/bin/env python3
"""Positional variadic compiler phases, signatures, tail send modes and source lines."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import static_types as types
import source_compiler as compiler
import source_context as context
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / 'tests/semantics/variadic_compiler_cases.json').read_text())


CONTEXTS = {'multiline-known-typed-tail': ['P.FUNCTIONS = [pfunction]',
                                'pfunction.SIGNATURE.PARAMETERS = [psparam]',
                                'psparam.VARIADIC',
                                '~psparam.REQUIRED',
                                'psparam.DEFAULT = PSNONE',
                                '~psparam.BYREF',
                                '$ppsupported_signature(pfunction.SIGNATURE)',
                                '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = eps',
                                '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)',
                                '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 2) = (psparam)',
                                '$ppfunction_parameter_ref((pfunction), 0) = false',
                                '$ppfunction_parameter_ref((pfunction), 1) = false',
                                '$ppfunction_parameter_ref((pfunction), 3) = false',
                                '~$ppsupported_params([psparam,psparam])',
                                '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX '
                                '2,PCFIELD 0]) = ((6,false))',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD '
                                '0,PCFIELD 1,PCINDEX 2,PCFIELD 1]) = (expression)',
                                '$expression_line(expression) = 9',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 0,PCFIELD '
                                '3,PCINDEX 0]) = (NParam phpType14 phpType24 phpType18 phpType4_1 '
                                'phpType4_2 phpType10 phpType5 phpType37 metadata)',
                                '$psline(metadata) = 3'],
 'multiline-deferred-typed-tail': ['P.FUNCTIONS = [pfunction]',
                                   'pfunction.SIGNATURE.PARAMETERS = [psparam]',
                                   'psparam.VARIADIC',
                                   '~psparam.REQUIRED',
                                   'psparam.DEFAULT = PSNONE',
                                   '~psparam.BYREF',
                                   '$ppsupported_signature(pfunction.SIGNATURE)',
                                   '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = eps',
                                   '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)',
                                   '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 2) = (psparam)',
                                   '$ppfunction_parameter_ref((pfunction), 0) = false',
                                   '$ppfunction_parameter_ref((pfunction), 1) = false',
                                   '$ppfunction_parameter_ref((pfunction), 3) = false',
                                   '~$ppsupported_params([psparam,psparam])',
                                   '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX '
                                   '1,PCFIELD 0]) = ((3,false))',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD '
                                   '0,PCFIELD 1,PCINDEX 2,PCFIELD 1]) = (expression)',
                                   '$expression_line(expression) = 6',
                                   '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD '
                                   '3,PCINDEX 0]) = (NParam phpType14 phpType24 phpType18 phpType4_1 '
                                   'phpType4_2 phpType10 phpType5 phpType37 metadata)',
                                   '$psline(metadata) = 9'],
 'known-reference-dimension-tail': ['P.FUNCTIONS = [pfunction]',
                                    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
                                    'psparam.VARIADIC',
                                    '~psparam.REQUIRED',
                                    'psparam.DEFAULT = PSNONE',
                                    'psparam.BYREF',
                                    '$ppsupported_signature(pfunction.SIGNATURE)',
                                    '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = eps',
                                    '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)',
                                    '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 2) = (psparam)',
                                    '$ppfunction_parameter_ref((pfunction), 0) = false',
                                    '$ppfunction_parameter_ref((pfunction), 1) = true',
                                    '$ppfunction_parameter_ref((pfunction), 3) = true',
                                    '~$ppsupported_params([psparam,psparam])',
                                    '$ppaccess(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]) '
                                    '= (PPW)',
                                    '$ppaccess(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) '
                                    '= (PPW)',
                                    '$ppaccess(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX 2,PCFIELD 1]) '
                                    '= (PPW)'],
 'deferred-reference-dimension-tail': ['P.FUNCTIONS = [pfunction]',
                                       'pfunction.SIGNATURE.PARAMETERS = [psparam]',
                                       'psparam.VARIADIC',
                                       '~psparam.REQUIRED',
                                       'psparam.DEFAULT = PSNONE',
                                       'psparam.BYREF',
                                       '$ppsupported_signature(pfunction.SIGNATURE)',
                                       '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = eps',
                                       '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = '
                                       '(psparam)',
                                       '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 2) = '
                                       '(psparam)',
                                       '$ppfunction_parameter_ref((pfunction), 0) = false',
                                       '$ppfunction_parameter_ref((pfunction), 1) = true',
                                       '$ppfunction_parameter_ref((pfunction), 3) = true',
                                       '~$ppsupported_params([psparam,psparam])',
                                       '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD '
                                       '1]) = (PPF)',
                                       '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD '
                                       '1]) = (PPF)',
                                       '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCFIELD 1,PCINDEX 2,PCFIELD '
                                       '1]) = (PPF)'],
 'reference-return-tail': ['P.FUNCTIONS = [pfunction]',
                           'pfunction.SIGNATURE.PARAMETERS = [psparam]',
                           'psparam.VARIADIC',
                           '~psparam.REQUIRED',
                           'psparam.DEFAULT = PSNONE',
                           'psparam.BYREF',
                           '$ppsupported_signature(pfunction.SIGNATURE)',
                           '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = eps',
                           '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)',
                           '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 2) = (psparam)',
                           '$ppfunction_parameter_ref((pfunction), 0) = false',
                           '$ppfunction_parameter_ref((pfunction), 1) = true',
                           '$ppfunction_parameter_ref((pfunction), 3) = true',
                           '~$ppsupported_params([psparam,psparam])',
                           'pfunction.SIGNATURE.BYREF',
                           '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = (PPW)',
                           '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 0,PCFIELD 5,PCINDEX '
                           '0,PCFIELD 0]) = (expression)',
                           '$ppreturn_variable(expression)',
                           '~$ppreturn_call(expression)'],
 'variadic-value-cow': ['P.FUNCTIONS = [pfunction]',
                        'pfunction.SIGNATURE.PARAMETERS = [psparam]',
                        'psparam.VARIADIC',
                        '~psparam.REQUIRED',
                        'psparam.DEFAULT = PSNONE',
                        '~psparam.BYREF',
                        '$ppsupported_signature(pfunction.SIGNATURE)',
                        '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = eps',
                        '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)',
                        '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 2) = (psparam)',
                        '$ppfunction_parameter_ref((pfunction), 0) = false',
                        '$ppfunction_parameter_ref((pfunction), 1) = false',
                        '$ppfunction_parameter_ref((pfunction), 3) = false',
                        '~$ppsupported_params([psparam,psparam])'],
 'variadic-reference-value-error': ['P.FUNCTIONS = [pfunction]',
                                    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
                                    'psparam.VARIADIC',
                                    '~psparam.REQUIRED',
                                    'psparam.DEFAULT = PSNONE',
                                    'psparam.BYREF',
                                    '$ppsupported_signature(pfunction.SIGNATURE)',
                                    '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = eps',
                                    '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)',
                                    '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 2) = (psparam)',
                                    '$ppfunction_parameter_ref((pfunction), 0) = false',
                                    '$ppfunction_parameter_ref((pfunction), 1) = true',
                                    '$ppfunction_parameter_ref((pfunction), 3) = true',
                                    '~$ppsupported_params([psparam,psparam])'],
 'variadic-typed-reference-coercion': ['P.FUNCTIONS = [pfunction]',
                                       'pfunction.SIGNATURE.PARAMETERS = [psparam]',
                                       'psparam.VARIADIC',
                                       '~psparam.REQUIRED',
                                       'psparam.DEFAULT = PSNONE',
                                       'psparam.BYREF',
                                       '$ppsupported_signature(pfunction.SIGNATURE)',
                                       '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = eps',
                                       '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = '
                                       '(psparam)',
                                       '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 2) = '
                                       '(psparam)',
                                       '$ppfunction_parameter_ref((pfunction), 0) = false',
                                       '$ppfunction_parameter_ref((pfunction), 1) = true',
                                       '$ppfunction_parameter_ref((pfunction), 3) = true',
                                       '~$ppsupported_params([psparam,psparam])'],
 'suppressed-reference-call-tail': ['P.FUNCTIONS = [pfunction_g,pfunction_f]',
                                    'pfunction_g.SIGNATURE.BYREF',
                                    '$ppfunction_parameter_ref((pfunction_f), 2)',
                                    '$ppaccess(P, [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) '
                                    '= (PPR)',
                                    '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 3,PCFIELD '
                                    '0,PCFIELD 1,PCINDEX 1,PCFIELD 1]) = (expression)',
                                    '$ppsend_var(expression)'],
 'optional-prefix-empty-tail': ['P.FUNCTIONS = [pfunction]',
                                'pfunction.SIGNATURE.PARAMETERS = [psparam_fixed,psparam_tail]',
                                '~psparam_fixed.VARIADIC',
                                'psparam_tail.VARIADIC',
                                'psparam_tail.DEFAULT = PSNONE',
                                '~psparam_tail.REQUIRED',
                                '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = '
                                '[psparam_fixed]',
                                '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = '
                                '(psparam_fixed)',
                                '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 1) = (psparam_tail)',
                                '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 4) = (psparam_tail)',
                                '$ppfunction_parameter_ref((pfunction), 3) = false'],
 'variadic-empty-default-prefix': ['P.FUNCTIONS = [pfunction]',
                                   'pfunction.SIGNATURE.PARAMETERS = [psparam_fixed,psparam_tail]',
                                   '~psparam_fixed.VARIADIC',
                                   'psparam_tail.VARIADIC',
                                   'psparam_tail.DEFAULT = PSNONE',
                                   '~psparam_tail.REQUIRED',
                                   '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = '
                                   '[psparam_fixed]',
                                   '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = '
                                   '(psparam_fixed)',
                                   '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 1) = '
                                   '(psparam_tail)',
                                   '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 4) = '
                                   '(psparam_tail)',
                                   '$ppfunction_parameter_ref((pfunction), 3) = false'],
 'variadic-reference-tail': ['P.FUNCTIONS = [pfunction]',
                             'pfunction.SIGNATURE.PARAMETERS = [psparam_fixed,psparam_tail]',
                             '~psparam_fixed.VARIADIC',
                             'psparam_tail.VARIADIC',
                             'psparam_tail.DEFAULT = PSNONE',
                             '~psparam_tail.REQUIRED',
                             '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = [psparam_fixed]',
                             '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam_fixed)',
                             '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 1) = (psparam_tail)',
                             '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 4) = (psparam_tail)',
                             '$ppfunction_parameter_ref((pfunction), 3) = true'],
 'variadic-reference-forward': ['P.FUNCTIONS = [pfunction]',
                                'pfunction.SIGNATURE.PARAMETERS = [psparam_fixed,psparam_tail]',
                                '~psparam_fixed.VARIADIC',
                                'psparam_tail.VARIADIC',
                                'psparam_tail.DEFAULT = PSNONE',
                                '~psparam_tail.REQUIRED',
                                '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = '
                                '[psparam_fixed]',
                                '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = '
                                '(psparam_fixed)',
                                '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 1) = (psparam_tail)',
                                '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 4) = (psparam_tail)',
                                '$ppfunction_parameter_ref((pfunction), 3) = true'],
 'variadic-missing-required': ['P.FUNCTIONS = [pfunction]',
                               'pfunction.SIGNATURE.PARAMETERS = [psparam_fixed,psparam_tail]',
                               '~psparam_fixed.VARIADIC',
                               'psparam_tail.VARIADIC',
                               'psparam_tail.DEFAULT = PSNONE',
                               '~psparam_tail.REQUIRED',
                               '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = '
                               '[psparam_fixed]',
                               '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam_fixed)',
                               '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 1) = (psparam_tail)',
                               '$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 4) = (psparam_tail)',
                               '$ppfunction_parameter_ref((pfunction), 3) = false']}

PENDING = {'variadic-typed-alias-known-catch-projection': 'ordinary statement compilation', 'variadic-typed-alias-deferred-catch-projection': 'ordinary statement compilation'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/variadic_compiler_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='variadic-compiler-', dir=ROOT / '.tools'))
    print(out, flush=True)

    def run(command, label):
        (out / (label + '.command.json')).write_text(json.dumps(command) + '\n')
        try:
            result = subprocess.run(command, capture_output=True, env=types.ENV, timeout=60)
        except subprocess.TimeoutExpired as error:
            (out / (label + '.stdout')).write_bytes(error.stdout or b'')
            (out / (label + '.stderr')).write_bytes(error.stderr or b'')
            (out / (label + '.status.json')).write_text(json.dumps({'status': 'timeout'}))
            raise
        (out / (label + '.stdout')).write_bytes(result.stdout)
        (out / (label + '.stderr')).write_bytes(result.stderr)
        (out / (label + '.status.json')).write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
        return result

    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend-wire')
    adapter = Worker([str(adapter_path), str(ROOT)], out / 'adapter-wire')
    records, assertions = [], []
    try:
        for index, (name, source) in enumerate(CASES.items()):
            file = out / (name + '.php')
            file.write_bytes(source.encode())
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.encode()).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            native = run([str(types.PHP), '-n', *types.FLAGS, '-l', str(file)], name)
            assert native.returncode in (0, 255), native
            events = context.events(native)
            record = {'name': name, 'source_base64': base64.b64encode(source.encode()).decode(),
                      'checked': checked, 'lint_exit': native.returncode, 'events': events}
            records.append(record)
            (out / 'records.json').write_text(json.dumps(records, indent=2) + '\n')
            body = f'  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n'
            if name in PENDING:
                body += '  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED '+json.dumps(PENDING[name])+')\n'
            else:
                body += '  -- if $pptrace(P) = ' + context.expected_events(events, file) + '\n'
            if name not in PENDING and native.returncode == 0:
                body += '  -- if P.COMPLETION = PPCNORMAL\n  -- if ~P.RETURNREF\n'
                body += ''.join('  -- if '+condition+'\n' for condition in CONTEXTS.get(name, []))
            assertions.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n' + body)
            (out / (name + '.state.watsup')).write_text(f'dec $main() : ppstate\ndef $main() = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n')
        fixture = out / 'compiler.watsup'
        fixture.write_text(compiler.PREFIX + '\n'.join(assertions) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{i}()\n' for i in range(len(assertions))))
        result = run([str(runner), *map(str, modules), str(fixture)], 'spectec')
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in files}
    report = {'scope': 'Positional variadic source compile phases, normalized tail signatures, known/deferred send modes and declaration/call/argument lines; runtime receive ownership and native execution pairing is separate.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/variadic-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;', len(PENDING), 'explicit pending controls;', sum(map(len, CONTEXTS.values())), 'source projections')


if __name__ == '__main__':
    main()
