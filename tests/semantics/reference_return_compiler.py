#!/usr/bin/env python3
"""Reference return compiler phases and source designation/mode/emission metadata."""
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
CASES = json.loads((ROOT / 'tests/semantics/reference_return_cases.json').read_text())


CONTEXTS = {'ref-bare-multiline': ['P.FUNCTIONS = [pfunction]', 'pfunction.SIGNATURE.BYREF', 'pfunction.ENDLINE = 5', '$code_expression(pfunction.CODE.EXPRESSIONS, [PCINDEX 0,PCFIELD 5,PCINDEX 0]) = ((4,false))'], 'ref-implicit-multiline': ['P.FUNCTIONS = [pfunction]', 'pfunction.SIGNATURE.BYREF', 'pfunction.ENDLINE = 5'], 'ref-outer-value-inner': ['P.FUNCTIONS = [pfunction_g,pfunction_f]', 'pfunction_f.SIGNATURE.BYREF', '~pfunction_g.SIGNATURE.BYREF', 'pfunction_f.CODE.EXPRESSIONS = $ppownexpr([pfunction_g],pfunction_f.CODE.EXPRESSIONS)', '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 1,PCFIELD 0]) = (PPW)', '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = (PPR)'], 'value-outer-ref-inner': ['P.FUNCTIONS = [pfunction_g,pfunction_f]', '~pfunction_f.SIGNATURE.BYREF', 'pfunction_g.SIGNATURE.BYREF', 'pfunction_f.CODE.EXPRESSIONS = $ppownexpr([pfunction_g],pfunction_f.CODE.EXPRESSIONS)', '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 1,PCFIELD 0]) = (PPR)', '$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = (PPW)'], 'ref-return-call-argument-line': ['P.FUNCTIONS = [pfunction_g,pfunction_f]', 'pfunction_f.SIGNATURE.BYREF', 'pfunction_f.ENDLINE = 7', '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 1,PCFIELD 5,PCINDEX 0]) = ((5,false))', '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = ((4,false))', '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = (expression)', '~$ppreturn_variable(expression)', '$ppreturn_call(expression)'], 'ref-return-nested-call-line': ['P.FUNCTIONS = [pfunction_g,pfunction_h,pfunction_f]', 'pfunction_f.SIGNATURE.BYREF', 'pfunction_f.ENDLINE = 10', '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 2,PCFIELD 5,PCINDEX 0]) = ((7,false))', '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 2,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = ((5,false))'], 'ref-return-nullary-call-line': ['P.FUNCTIONS = [pfunction_g,pfunction_f]', 'pfunction_f.SIGNATURE.BYREF', 'pfunction_f.ENDLINE = 6', '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 1,PCFIELD 5,PCINDEX 0]) = ((5,false))', '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = ((5,false))'], 'ref-temporary-call-dim': ['$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = (PPW)', '$ppaccess(P, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0,PCFIELD 0]) = (PPR)', '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = (expression)', '$ppreturn_variable(expression)', '~$ppreturn_call(expression)'], 'ref-computed-variable-mode': ['$ppaccess(P, [PCINDEX 0,PCFIELD 5,PCINDEX 1,PCFIELD 0]) = (PPW)'], 'return-whole-globals-copy': ['$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 1,PCFIELD 5,PCINDEX 0,PCFIELD 0]) = (expression)', '$ppreturn_variable(expression)', '~$ppreturn_call(expression)'], 'return-reference-assignment-value-class': ['$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, [PCINDEX 2,PCFIELD 5,PCINDEX 1,PCFIELD 0]) = (expression)', '~$ppreturn_variable(expression)', '~$ppreturn_call(expression)']}
PENDING = {'suppression': 'ordinary expression or writable operand compilation', 'void-suppression': 'ordinary expression or writable operand compilation'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/reference_return_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='reference-return-compiler-', dir=ROOT / '.tools'))
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
    report = {'scope': 'Reference return compiler source phases, return designation, mode restoration and emission metadata; runtime ownership/demand pairing is separate.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/reference-return-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;',len(PENDING),'explicit pending controls')


if __name__ == '__main__':
    main()
