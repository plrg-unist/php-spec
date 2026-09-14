#!/usr/bin/env python3
"""Closure template phases, lexical priority, source scopes and emitted lines."""
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
CASES = json.loads((ROOT / 'tests/semantics/closure_compiler_cases.json').read_text())


CONTEXTS = {'closure-basic-return': ['|P.CLOSURETEMPLATES| = 1',
                          '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 0,PCFIELD 1])) = '
                          '(pfunction_0)',
                          'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                          'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                          'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                          '~pfunction_0.EARLY',
                          '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = []',
                          '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps'],
 'closure-magic-main': ['|P.CLOSURETEMPLATES| = 1',
                        '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 0,PCFIELD 1])) = '
                        '(pfunction_0)',
                        'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                        'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                        'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                        '~pfunction_0.EARLY',
                        '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = []',
                        '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps'],
 'closure-magic-nested-named': ['|P.CLOSURETEMPLATES| = 2',
                                '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 1,PCINDEX '
                                '0,PCFIELD 5,PCINDEX 0,PCFIELD 0])) = (pfunction_0)',
                                'pfunction_0.NAME = '
                                '[123,99,108,111,115,117,114,101,58,78,92,109,97,107,101,40,41,58,49,125]',
                                'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 5,PCINDEX '
                                '0,PCFIELD 0,PCFIELD 6])',
                                '~pfunction_0.EARLY',
                                '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = []',
                                '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 1,PCINDEX '
                                '0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCFIELD 6,PCINDEX 1,PCFIELD 0])) = '
                                '(pfunction_1)',
                                'pfunction_1.NAME = '
                                '[123,99,108,111,115,117,114,101,58,123,99,108,111,115,117,114,101,58,78,92,109,97,107,101,40,41,58,49,125,58,49,125]',
                                'pfunction_1.BODY = ([PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 5,PCINDEX '
                                '0,PCFIELD 0,PCFIELD 6,PCINDEX 1,PCFIELD 0,PCFIELD 6])',
                                '~pfunction_1.EARLY',
                                '$fixture_lexicals(pfunction_1.CODE.EXPRESSIONS) = []',
                                '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps'],
 'closure-multiline-capture-warning': ['|P.CLOSURETEMPLATES| = 1',
                                       '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD '
                                       '0,PCFIELD 1])) = (pfunction_0)',
                                       'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                       'SOURCE_FILE_BYTES ++ ([58, 50, 125])',
                                       'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                                       '~pfunction_0.EARLY',
                                       '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = [(CODELEXICAL '
                                       '([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 4,PCINDEX 0]) '
                                       '([109,105,115,115,105,110,103]) false 3),(CODELEXICAL ([PCINDEX '
                                       '0,PCFIELD 0,PCFIELD 1,PCFIELD 4,PCINDEX 1]) '
                                       '([99,114,101,97,116,101,100]) true 4)]',
                                       '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps',
                                       'pfunction_0.CVS = [([109, 105, 115, 115, 105, 110, 103]),([99, 114, '
                                       '101, 97, 116, 101, 100])]'],
 'closure-multiline-call-type': ['|P.CLOSURETEMPLATES| = 1',
                                 '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 0,PCFIELD '
                                 '1])) = (pfunction_0)',
                                 'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                 'SOURCE_FILE_BYTES ++ ([58, 50, 125])',
                                 'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                                 '~pfunction_0.EARLY',
                                 '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = []',
                                 '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps'],
 'closure-static-flag': ['|P.CLOSURETEMPLATES| = 1',
                         '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 0,PCFIELD 1])) = '
                         '(pfunction_0)',
                         'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                         'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                         'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                         '~pfunction_0.EARLY',
                         '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = []',
                         '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps'],
 'closure-nested-named-scope': ['|P.CLOSURETEMPLATES| = 1',
                                '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 0,PCFIELD '
                                '1])) = (pfunction_0)',
                                'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                                '~pfunction_0.EARLY',
                                '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = []',
                                '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps'],
 'closure-named-default-signature': ['|P.CLOSURETEMPLATES| = 1',
                                     '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD '
                                     '0,PCFIELD 1])) = (pfunction_0)',
                                     'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                     'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                     'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                                     '~pfunction_0.EARLY',
                                     '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = []',
                                     '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps',
                                     'pfunction_0.CVS = [([97]),([98])]',
                                     '|pfunction_0.DEFAULTS| = 2'],
 'closure-unpack-reference-signature': ['|P.CLOSURETEMPLATES| = 1',
                                        '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD '
                                        '0,PCFIELD 1])) = (pfunction_0)',
                                        'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                        'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                        'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                                        '~pfunction_0.EARLY',
                                        '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = []',
                                        '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps',
                                        'pfunction_0.CVS = [([97]),([120, 115])]',
                                        'pfunction_0.SIGNATURE.PARAMETERS[0].BYREF = true',
                                        'pfunction_0.SIGNATURE.PARAMETERS[1].VARIADIC = true'],
 'closure-reference-return-signature': ['|P.CLOSURETEMPLATES| = 1',
                                        '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD '
                                        '0,PCFIELD 1])) = (pfunction_0)',
                                        'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                        'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                        'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                                        '~pfunction_0.EARLY',
                                        '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = [(CODELEXICAL '
                                        '([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 4,PCINDEX 0]) ([120]) true '
                                        '1)]',
                                        '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps',
                                        'pfunction_0.CVS = [([120])]',
                                        'pfunction_0.SIGNATURE.BYREF = true'],
 'closure-line-split-reference': ['|P.CLOSURETEMPLATES| = 1',
                                  '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 0,PCFIELD 0,PCFIELD '
                                  '1])) = (pfunction_0)',
                                  'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                  'SOURCE_FILE_BYTES ++ ([58, 50, 125])',
                                  'pfunction_0.BODY = ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                                  '~pfunction_0.EARLY',
                                  '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = [(CODELEXICAL ([PCINDEX '
                                  '0,PCFIELD 0,PCFIELD 1,PCFIELD 4,PCINDEX 0]) ([99,114,101,97,116,101,100]) '
                                  'true 4),(CODELEXICAL ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 4,PCINDEX '
                                  '1]) ([109,105,115,115,105,110,103]) false 5)]',
                                  '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps',
                                  'pfunction_0.CVS = [([99, 114, 101, 97, 116, 101, 100]),([109, 105, 115, '
                                  '115, 105, 110, 103])]'],
 'closure-array-object-cast-alias': ['|P.CLOSURETEMPLATES| = 1',
                                     '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD '
                                     '0,PCFIELD 1])) = (pfunction_0)',
                                     'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) ++ '
                                     'SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                     'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                                     '~pfunction_0.EARLY',
                                     '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = [(CODELEXICAL '
                                     '([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 4,PCINDEX 0]) ([120]) false '
                                     '1)]',
                                     '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps'],
 'closure-object-callable-class-types': ['|P.CLOSURETEMPLATES| = 1',
                                         '$function_at(P.CLOSURETEMPLATES, PORIGIN 91 ([PCINDEX 1,PCFIELD '
                                         '0,PCFIELD 1])) = (pfunction_0)',
                                         'pfunction_0.NAME = ([123, 99, 108, 111, 115, 117, 114, 101, 58]) '
                                         '++ SOURCE_FILE_BYTES ++ ([58, 49, 125])',
                                         'pfunction_0.BODY = ([PCINDEX 1,PCFIELD 0,PCFIELD 1,PCFIELD 6])',
                                         '~pfunction_0.EARLY',
                                         '$fixture_lexicals(pfunction_0.CODE.EXPRESSIONS) = []',
                                         '$fixture_lexicals($ppfunction_code(P).EXPRESSIONS) = eps'],
 'object-parameter': ['P.CLOSURETEMPLATES = eps', '|P.FUNCTIONS| = 1'],
 'callable-parameter': ['P.CLOSURETEMPLATES = eps', '|P.FUNCTIONS| = 1']}

PENDING = {}

EXTRA = 'dec $fixture_lexical(pcodeexpr) : pcodeexpr*\ndec $fixture_lexicals(pcodeexpr*) : pcodeexpr*\ndef $fixture_lexicals(eps) = eps\ndef $fixture_lexicals(pcodeexpr :: pcodeexpr_tail*) = $fixture_lexical(pcodeexpr) ++ $fixture_lexicals(pcodeexpr_tail*)\ndef $fixture_lexical(CODELEXICAL pcpath ptbytes b z) = [CODELEXICAL pcpath ptbytes b z]\ndef $fixture_lexical(pcodeexpr) = eps -- otherwise\n'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/closure_compiler_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='closure-compiler-', dir=ROOT / '.tools'))
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
            if name not in PENDING:
                body += '  -- if $pptrace(P) = ' + context.expected_events(events, file) + '\n'
            if name in PENDING:
                body += '  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED '+json.dumps(PENDING[name])+')\n'
            elif native.returncode == 0:
                body += '  -- if P.COMPLETION = PPCNORMAL\n'
                body += ''.join('  -- if '+condition+'\n' for raw_condition in CONTEXTS.get(name, []) for condition in [raw_condition.replace('SOURCE_FILE_BYTES', types.byte_expr(str(file)))])
            assertions.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n' + body)
            (out / (name + '.state.watsup')).write_text(f'dec $main() : ppstate\ndef $main() = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n')
        fixture = out / 'compiler.watsup'
        fixture.write_text(compiler.PREFIX + EXTRA + '\n'.join(assertions) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{i}()\n' for i in range(len(assertions))))
        result = run([str(runner), *map(str, modules), str(fixture)], 'spectec')
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in files}
    report = {'scope': 'Explicit closure compiler phases, distinct unregistered templates, lexical priorities, source scopes, magic names, captures, CVs and signature consumers; instance ownership/runtime value behavior are separately paired.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/closure-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;',len(PENDING),'explicit pending controls')


if __name__ == '__main__':
    main()
