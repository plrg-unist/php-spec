#!/usr/bin/env python3
"""Suppression compiler phases, operand kinds, retained effects and source lines."""
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
CASES = json.loads((ROOT / 'tests/semantics/suppression_compiler_cases.json').read_text())


CONTEXTS = {'suppress-variable-used-and-restored': ['pcpath_0 = [PCINDEX 0,PCFIELD 0,PCINDEX 0]',
                                         '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                         '(NExprErrorSuppress expression_0 metadata_0)',
                                         '$ppaccess(P, pcpath_0) = (PPR)',
                                         '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = '
                                         '(PPR)',
                                         '~$ppreturn_variable(NExprErrorSuppress expression_0 '
                                         'metadata_0)',
                                         '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                         '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = '
                                         'false'],
 'suppress-computed-variable': ['pcpath_0 = [PCINDEX 1,PCFIELD 0,PCINDEX 0]',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                '(NExprErrorSuppress expression_0 metadata_0)',
                                '$ppaccess(P, pcpath_0) = (PPR)',
                                '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = (PPR)',
                                '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = false'],
 'suppress-variable-reference-send': ['pcpath_0 = [PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]',
                                      '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                      '(NExprErrorSuppress expression_0 metadata_0)',
                                      '$ppaccess(P, pcpath_0) = (PPR)',
                                      '$ppaccess(P, [PCINDEX 2,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD '
                                      '1,PCFIELD 0]) = (PPR)',
                                      '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                      '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                      '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = false'],
 'suppress-call-reference-send': ['pcpath_0 = [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]',
                                  '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                  '(NExprErrorSuppress expression_0 metadata_0)',
                                  '$ppaccess(P, pcpath_0) = (PPR)',
                                  '$ppaccess(P, [PCINDEX 3,PCFIELD 0,PCFIELD 1,PCINDEX 0,PCFIELD '
                                  '1,PCFIELD 0]) = (PPR)',
                                  '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                  '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                  '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = true'],
 'suppress-reference-return-variable': ['pcpath_0 = [PCINDEX 1,PCFIELD 5,PCINDEX 1,PCFIELD 0]',
                                        '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                        '(NExprErrorSuppress expression_0 metadata_0)',
                                        '$ppaccess(P, pcpath_0) = (PPR)',
                                        '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 1,PCFIELD 0,PCFIELD '
                                        '0]) = (PPR)',
                                        '~$ppreturn_variable(NExprErrorSuppress expression_0 '
                                        'metadata_0)',
                                        '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                        '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = '
                                        'false'],
 'suppress-reference-return-call': ['pcpath_0 = [PCINDEX 2,PCFIELD 5,PCINDEX 0,PCFIELD 0]',
                                    '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                    '(NExprErrorSuppress expression_0 metadata_0)',
                                    '$ppaccess(P, pcpath_0) = (PPR)',
                                    '$ppaccess(P, [PCINDEX 2,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCFIELD 0]) '
                                    '= (PPR)',
                                    '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                    '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                    '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = true'],
 'suppress-multiline-call-parent': ['pcpath_0 = [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0]',
                                    '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                    '(NExprErrorSuppress expression_0 metadata_0)',
                                    '$ppaccess(P, pcpath_0) = (PPR)',
                                    '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCFIELD 0]) '
                                    '= (PPR)',
                                    '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                    '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                    '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = true',
                                    'P.FUNCTIONS = [pfunction_g,pfunction_f]',
                                    '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 1,PCFIELD '
                                    '5,PCINDEX 0]) = ((5,false))',
                                    '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 1,PCFIELD '
                                    '5,PCINDEX 0,PCFIELD 0]) = ((5,false))',
                                    '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 1,PCFIELD '
                                    '5,PCINDEX 0,PCFIELD 0,PCFIELD 0]) = ((4,false))'],
 'silence-constant-dead-write': ['pcpath_0 = [PCINDEX 0,PCFIELD 0,PCFIELD 0]',
                                 '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                 '(NExprErrorSuppress expression_0 metadata_0)',
                                 '$ppaccess(P, pcpath_0) = (PPR)',
                                 '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]) = (PPR)',
                                 '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                 '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                 '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = false',
                                 '(PPCEFFECT pcpath_0) <- P.EXPRESSIONS',
                                 '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCFIELD 1]) = eps'],
 'silence-constant-dead-hole': ['pcpath_0 = [PCINDEX 0,PCFIELD 0,PCFIELD 0]',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                '(NExprErrorSuppress expression_0 metadata_0)',
                                '$ppaccess(P, pcpath_0) = (PPR)',
                                '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]) = (PPR)',
                                '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = false',
                                '(PPCEFFECT pcpath_0) <- P.EXPRESSIONS',
                                '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCFIELD 1]) = eps'],
 'silence-constant-folded-list-effects': ['pcpath_0 = [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0,PCFIELD '
                                          '0]',
                                          '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                          '(NExprErrorSuppress expression_0 metadata_0)',
                                          '$ppaccess(P, pcpath_0) = (PPR)',
                                          '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD '
                                          '0,PCFIELD 0,PCFIELD 0]) = (PPR)',
                                          '~$ppreturn_variable(NExprErrorSuppress expression_0 '
                                          'metadata_0)',
                                          '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                          '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = '
                                          'false',
                                          '(PPCEFFECT pcpath_0) <- P.EXPRESSIONS',
                                          '$effect_select($compiled_operands(P, P.EXPRESSIONS), '
                                          '$compiled_operands(P, P.EXPRESSIONS), eps) = [(CODEEFFECT '
                                          'pcpath_0)]'],
 'silence-nested-constant-effects': ['pcpath_0 = [PCINDEX 0,PCFIELD 0,PCINDEX 0]',
                                     '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                     '(NExprErrorSuppress expression_0 metadata_0)',
                                     '$ppaccess(P, pcpath_0) = (PPR)',
                                     '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = (PPR)',
                                     '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                     '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                     '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = false',
                                     '(PPCEFFECT pcpath_0) <- P.EXPRESSIONS',
                                     'pcpath_1 = [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]',
                                     '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_1) = '
                                     '(NExprErrorSuppress expression_1 metadata_1)',
                                     '$ppaccess(P, pcpath_1) = (PPR)',
                                     '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0,PCFIELD 0]) '
                                     '= (PPR)',
                                     '~$ppreturn_variable(NExprErrorSuppress expression_1 metadata_1)',
                                     '~$ppreturn_call(NExprErrorSuppress expression_1 metadata_1)',
                                     '$ppsend_var(NExprErrorSuppress expression_1 metadata_1) = false',
                                     '(PPCEFFECT pcpath_1) <- P.EXPRESSIONS',
                                     '$effect_select($compiled_operands(P, P.EXPRESSIONS), '
                                     '$compiled_operands(P, P.EXPRESSIONS), eps) = [(CODEEFFECT '
                                     'pcpath_0)]'],
 'silence-constant-parent-warning': ['pcpath_0 = [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]',
                                     '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                     '(NExprErrorSuppress expression_0 metadata_0)',
                                     '$ppaccess(P, pcpath_0) = (PPR)',
                                     '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0,PCFIELD 0]) '
                                     '= (PPR)',
                                     '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                     '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                     '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = false',
                                     '(PPCEFFECT pcpath_0) <- P.EXPRESSIONS'],
 'silence-folded-append-once': ['pcpath_0 = [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0,PCFIELD 0]',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                '(NExprErrorSuppress expression_0 metadata_0)',
                                '$ppaccess(P, pcpath_0) = (PPR)',
                                '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0,PCFIELD '
                                '0,PCFIELD 0]) = (PPR)',
                                '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = false',
                                '(PPCEFFECT pcpath_0) <- P.EXPRESSIONS',
                                '$effect_select($compiled_operands(P, P.EXPRESSIONS), '
                                '$compiled_operands(P, P.EXPRESSIONS), eps) = [(CODEEFFECT pcpath_0)]'],
 'silence-nested-append-once': ['pcpath_0 = [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0,PCFIELD 0]',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_0) = '
                                '(NExprErrorSuppress expression_0 metadata_0)',
                                '$ppaccess(P, pcpath_0) = (PPR)',
                                '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0,PCFIELD '
                                '0,PCFIELD 0]) = (PPR)',
                                '~$ppreturn_variable(NExprErrorSuppress expression_0 metadata_0)',
                                '~$ppreturn_call(NExprErrorSuppress expression_0 metadata_0)',
                                '$ppsend_var(NExprErrorSuppress expression_0 metadata_0) = false',
                                '(PPCEFFECT pcpath_0) <- P.EXPRESSIONS',
                                'pcpath_1 = [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0,PCFIELD 0,PCFIELD '
                                '0]',
                                '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_1) = '
                                '(NExprErrorSuppress expression_1 metadata_1)',
                                '$ppaccess(P, pcpath_1) = (PPR)',
                                '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0,PCFIELD '
                                '0,PCFIELD 0,PCFIELD 0]) = (PPR)',
                                '~$ppreturn_variable(NExprErrorSuppress expression_1 metadata_1)',
                                '~$ppreturn_call(NExprErrorSuppress expression_1 metadata_1)',
                                '$ppsend_var(NExprErrorSuppress expression_1 metadata_1) = false',
                                '(PPCEFFECT pcpath_1) <- P.EXPRESSIONS',
                                '$effect_select($compiled_operands(P, P.EXPRESSIONS), '
                                '$compiled_operands(P, P.EXPRESSIONS), eps) = [(CODEEFFECT pcpath_0)]']}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/suppression_compiler_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='suppression-compiler-', dir=ROOT / '.tools'))
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
            body += '  -- if $pptrace(P) = ' + context.expected_events(events, file) + '\n'
            if native.returncode == 0:
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
    report = {'scope': 'Suppression compile phases, source designation, known operand/effect retention and enclosing lines; runtime emission/ownership pairing is separate.',
              'result': 'pass', 'compared': len(CASES), 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/suppression-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records), 'exact compiler phase comparisons;', sum(map(len, CONTEXTS.values())), 'source projections')


if __name__ == '__main__':
    main()
