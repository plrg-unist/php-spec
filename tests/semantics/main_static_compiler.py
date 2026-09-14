#!/usr/bin/env python3
"""Main-script static declaration phases, own-scope markers, CVs and emitted lines."""
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
CASES = json.loads((ROOT / 'tests/semantics/main_static_compiler_cases.json').read_text())


CONTEXTS = {'main-static-stored-global-alias': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = '
                                     '[CODESTATIC ([PCINDEX 2,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                                     '$fixture_statics($ppownexpr(P.FUNCTIONS, $compiled_operands(P, '
                                     'P.EXPRESSIONS))) = [CODESTATIC ([PCINDEX 2,PCFIELD 0,PCINDEX 0]) '
                                     '([120]) 1 1 true]',
                                     '$ppaccess(P, [PCINDEX 2,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                                     '$pffact(P.FOLD.FACTS, [PCINDEX 2,PCFIELD 0,PCINDEX 0,PCFIELD 1]) '
                                     '=/= eps',
                                     '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX '
                                     '2,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = eps'],
 'main-static-dynamic-loop-unset': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = '
                                    '[CODESTATIC ([PCINDEX 1,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX 0]) '
                                    '([120]) 1 1 false]',
                                    '$fixture_statics($ppownexpr(P.FUNCTIONS, $compiled_operands(P, '
                                    'P.EXPRESSIONS))) = [CODESTATIC ([PCINDEX 1,PCFIELD 4,PCINDEX '
                                    '0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                    '$ppaccess(P, [PCINDEX 1,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX '
                                    '0,PCFIELD 0]) = eps'],
 'main-static-autoglobal-views': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = [CODESTATIC '
                                  '([PCINDEX 1,PCFIELD 0,PCINDEX 0]) ([95,71,69,84]) 1 1 true]',
                                  '$fixture_statics($ppownexpr(P.FUNCTIONS, $compiled_operands(P, '
                                  'P.EXPRESSIONS))) = [CODESTATIC ([PCINDEX 1,PCFIELD 0,PCINDEX 0]) '
                                  '([95,71,69,84]) 1 1 true]',
                                  '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                                  '$pffact(P.FOLD.FACTS, [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 1]) =/= '
                                  'eps',
                                  '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX '
                                  '1,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = eps',
                                  'P.CVS = [([95,71,69,84]),([110])]'],
 'main-static-globals-views': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = [CODESTATIC '
                               '([PCINDEX 1,PCFIELD 0,PCINDEX 0]) ([71,76,79,66,65,76,83]) 1 1 true]',
                               '$fixture_statics($ppownexpr(P.FUNCTIONS, $compiled_operands(P, '
                               'P.EXPRESSIONS))) = [CODESTATIC ([PCINDEX 1,PCFIELD 0,PCINDEX 0]) '
                               '([71,76,79,66,65,76,83]) 1 1 true]',
                               '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                               '$pffact(P.FOLD.FACTS, [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 1]) =/= '
                               'eps',
                               '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX '
                               '1,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = eps',
                               'P.CVS = [([120]),([71,76,79,66,65,76,83]),([110])]'],
 'main-static-named-scope-isolation': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = '
                                       '[CODESTATIC ([PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 '
                                       'true,CODESTATIC ([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD '
                                       '0,PCINDEX 0]) ([120]) 1 1 true]',
                                       '$fixture_statics($ppownexpr(P.FUNCTIONS, $compiled_operands(P, '
                                       'P.EXPRESSIONS))) = [CODESTATIC ([PCINDEX 0,PCFIELD 0,PCINDEX '
                                       '0]) ([120]) 1 1 true]',
                                       '$ppaccess(P, [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps',
                                       '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD '
                                       '1]) =/= eps',
                                       '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX '
                                       '0,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = eps',
                                       '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                       '0,PCFIELD 0]) = eps',
                                       '$pffact(P.FOLD.FACTS, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD '
                                       '0,PCINDEX 0,PCFIELD 1]) =/= eps',
                                       '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX '
                                       '1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = eps',
                                       'P.FUNCTIONS = [pfunction]',
                                       '$fixture_statics(pfunction.CODE.EXPRESSIONS) = [CODESTATIC '
                                       '([PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 '
                                       '1 true]'],
 'main-static-multiline-deferred-cv': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = '
                                       '[CODESTATIC ([PCINDEX 0,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX '
                                       '0]) ([120]) 4 5 false]',
                                       '$fixture_statics($ppownexpr(P.FUNCTIONS, $compiled_operands(P, '
                                       'P.EXPRESSIONS))) = [CODESTATIC ([PCINDEX 0,PCFIELD 4,PCINDEX '
                                       '0,PCFIELD 0,PCINDEX 0]) ([120]) 4 5 false]',
                                       '$ppaccess(P, [PCINDEX 0,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX '
                                       '0,PCFIELD 0]) = eps',
                                       '$ppaccess(P, [PCINDEX 0,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX '
                                       '0,PCFIELD 1]) = (PPR)',
                                       '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX '
                                       '0,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = ((5, '
                                       'false))',
                                       'P.CVS = [([105]),([120]),([109,105,115,115,105,110,103])]'],
 'main-static-folded-selected-effect-once': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = '
                                             '[CODESTATIC ([PCINDEX 1,PCFIELD 4,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0]) ([120]) 1 1 false]',
                                             '$fixture_statics($ppownexpr(P.FUNCTIONS, '
                                             '$compiled_operands(P, P.EXPRESSIONS))) = [CODESTATIC '
                                             '([PCINDEX 1,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX 0]) '
                                             '([120]) 1 1 false]',
                                             '$ppaccess(P, [PCINDEX 1,PCFIELD 4,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0,PCFIELD 0]) = eps',
                                             '(CODEREDIRECT ([PCINDEX 1,PCFIELD 4,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0,PCFIELD 1]) ([PCINDEX 1,PCFIELD 4,PCINDEX '
                                             '0,PCFIELD 0,PCINDEX 0,PCFIELD 1,PCFIELD 1]) false) <- '
                                             '$compiled_redirects(P.REDIRECTS)',
                                             '$ppaccess(P, [PCINDEX 1,PCFIELD 4,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0,PCFIELD 1,PCFIELD 2]) = eps'],
 'main-static-preceding-named-declaration': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = '
                                             '[CODESTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0]) ([120]) 1 1 true,CODESTATIC ([PCINDEX '
                                             '1,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                                             '$fixture_statics($ppownexpr(P.FUNCTIONS, '
                                             '$compiled_operands(P, P.EXPRESSIONS))) = [CODESTATIC '
                                             '([PCINDEX 1,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                                             '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0,PCFIELD 0]) = eps',
                                             '$pffact(P.FOLD.FACTS, [PCINDEX 0,PCFIELD 5,PCINDEX '
                                             '0,PCFIELD 0,PCINDEX 0,PCFIELD 1]) =/= eps',
                                             '$code_expression($compiled_operands(P, P.EXPRESSIONS), '
                                             '[PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX '
                                             '0,PCFIELD 1]) = eps',
                                             '$ppaccess(P, [PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = '
                                             'eps',
                                             '$pffact(P.FOLD.FACTS, [PCINDEX 1,PCFIELD 0,PCINDEX '
                                             '0,PCFIELD 1]) =/= eps',
                                             '$code_expression($compiled_operands(P, P.EXPRESSIONS), '
                                             '[PCINDEX 1,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = eps',
                                             'P.FUNCTIONS = [pfunction]',
                                             '$fixture_statics(pfunction.CODE.EXPRESSIONS) = '
                                             '[CODESTATIC ([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD '
                                             '0,PCINDEX 0]) ([120]) 1 1 true]'],
 'main-static-bare-null-cached': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = [CODESTATIC '
                                  '([PCINDEX 0,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 '
                                  'true]',
                                  '$fixture_statics($ppownexpr(P.FUNCTIONS, $compiled_operands(P, '
                                  'P.EXPRESSIONS))) = [CODESTATIC ([PCINDEX 0,PCFIELD 4,PCINDEX '
                                  '0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 true]',
                                  '$ppaccess(P, [PCINDEX 0,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX '
                                  '0,PCFIELD 0]) = eps',
                                  '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX '
                                  '0,PCFIELD 4,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]) = eps',
                                  'P.CVS = [([105]),([120])]'],
 'main-static-namespace-deferred-constant': ['$fixture_statics($compiled_operands(P, P.EXPRESSIONS)) = '
                                             '[CODESTATIC ([PCINDEX 0,PCFIELD 1,PCINDEX 1,PCFIELD '
                                             '4,PCINDEX 0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                             '$fixture_statics($ppownexpr(P.FUNCTIONS, '
                                             '$compiled_operands(P, P.EXPRESSIONS))) = [CODESTATIC '
                                             '([PCINDEX 0,PCFIELD 1,PCINDEX 1,PCFIELD 4,PCINDEX '
                                             '0,PCFIELD 0,PCINDEX 0]) ([120]) 1 1 false]',
                                             '$ppaccess(P, [PCINDEX 0,PCFIELD 1,PCINDEX 1,PCFIELD '
                                             '4,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]) = eps']}

PENDING = {}

EXTRA = 'dec $fixture_static(pcodeexpr) : pcodeexpr*\ndec $fixture_statics(pcodeexpr*) : pcodeexpr*\ndef $fixture_statics(eps) = eps\ndef $fixture_statics(pcodeexpr :: pcodeexpr_tail*) = $fixture_static(pcodeexpr) ++ $fixture_statics(pcodeexpr_tail*)\ndef $fixture_static(CODESTATIC pcpath ptbytes z_begin z_bind b) = [CODESTATIC pcpath ptbytes z_begin z_bind b]\ndef $fixture_static(pcodeexpr) = eps -- otherwise\n'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/main_static_compiler_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='main-static-compiler-', dir=ROOT / '.tools'))
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
                body += ''.join('  -- if '+condition+'\n' for condition in CONTEXTS.get(name, []))
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
    report = {'scope': 'Initial main-script statics compiler phases, aggregate versus main/named marker scopes, pre-evaluation stored mode, special CVs and emitted initializer/bind lines; global cell ownership is separately paired.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/main-static-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;',len(PENDING),'explicit pending controls')


if __name__ == '__main__':
    main()
