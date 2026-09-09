#!/usr/bin/env python3
"""Positional default compiler phases and checked parameter/source descriptors."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import static_types as types
import source_compiler as compiler
import source_context as context

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / 'tests/semantics/default_parameter_cases.json').read_text())


# Declaration/source paths and emitted compiler lines checked against the pinned compiler.
CONTEXTS = {'int': ['P.FUNCTIONS = [pfunction]', 'pfunction.DEFAULTS = [{ INDEX 0, ORIGIN PORIGIN 91 ([PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 6]), KIND PDSTORED }]', '$code_expression(pfunction.CODE.EXPRESSIONS, [PCINDEX 0, PCFIELD 3, PCINDEX 0]) = ((1, false))'], 'deferred-unknown': ['P.FUNCTIONS = [pfunction]', 'pfunction.DEFAULTS = [{ INDEX 0, ORIGIN PORIGIN 91 ([PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 6]), KIND PDDEFERRED }]'], 'deferred-builtin': ['P.FUNCTIONS = [pfunction]', 'pfunction.DEFAULTS = [{ INDEX 0, ORIGIN PORIGIN 91 ([PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 6]), KIND PDDEFERRED }]', '$pffact(P.FOLD.FACTS, [PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 6]) = eps'], 'optional-required': ['P.FUNCTIONS = [pfunction]', 'pfunction.DEFAULTS = eps', '$pffact(P.FOLD.FACTS, [PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 6]) = (PINT 3)', '$pfclass_at(P.FOLD.CLASSFACTS, [PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 6]) = (PVSCALAR)', '$code_expression(pfunction.CODE.EXPRESSIONS, [PCINDEX 0, PCFIELD 3, PCINDEX 0]) = ((1, false))', '$code_expression(pfunction.CODE.EXPRESSIONS, [PCINDEX 0, PCFIELD 3, PCINDEX 1]) = ((1, false))'], 'multiline-default': ['P.FUNCTIONS = [pfunction]', '$code_expression(pfunction.CODE.EXPRESSIONS, [PCINDEX 0, PCFIELD 3, PCINDEX 0]) = ((4, false))'], 'multiline-magic': ['P.FUNCTIONS = [pfunction]', '$code_expression(pfunction.CODE.EXPRESSIONS, [PCINDEX 0, PCFIELD 3, PCINDEX 0]) = ((3, false))', '$pffact(P.FOLD.FACTS, [PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 6]) = (PINT 4)'], 'nested-defaults': ['P.FUNCTIONS = [pfunction_g,pfunction_f]', '|pfunction_g.DEFAULTS| = 1', '|pfunction_f.DEFAULTS| = 1', 'pfunction_f.CODE.EXPRESSIONS = $ppownexpr([pfunction_g], pfunction_f.CODE.EXPRESSIONS)', '$code_expression(pfunction_g.CODE.EXPRESSIONS, [PCINDEX 0, PCFIELD 5, PCINDEX 0, PCFIELD 3, PCINDEX 0]) = ((1, false))', '$code_expression(pfunction_f.CODE.EXPRESSIONS, [PCINDEX 0, PCFIELD 3, PCINDEX 0]) = ((1, false))'], 'reference-default': ['P.FUNCTIONS = [pfunction]', 'pfunction.SIGNATURE.PARAMETERS = [psparam]', 'psparam.BYREF', '~psparam.REQUIRED', '|pfunction.DEFAULTS| = 1'], 'all-default-kinds': ['P.FUNCTIONS = [pfunction]', 'pfunction.DEFAULTS = [pdefault_x,pdefault_y,pdefault_z]', 'pdefault_x.INDEX = 0', 'pdefault_y.INDEX = 1', 'pdefault_z.INDEX = 2', 'pdefault_x.KIND = PDSTORED', 'pdefault_y.KIND = PDDEFERRED', 'pdefault_z.KIND = PDSTORED'], 'dropped-deferred': ['P.FUNCTIONS = [pfunction]', 'pfunction.DEFAULTS = eps', '$code_name(pfunction.CODE.NAMES, [PCINDEX 0, PCFIELD 3, PCINDEX 0, PCFIELD 6]) = (([85,78,75,78,79,87,78], eps))'], 'declared-constant-deferred': ['P.FUNCTIONS = [pfunction]', 'pfunction.DEFAULTS = [pdefault]', 'pdefault.KIND = PDDEFERRED'], 'import-default-context': ['P.FUNCTIONS = [pfunction]', 'pfunction.NAME = [78,92,102]', 'pfunction.DEFAULTS = [pdefault_x,pdefault_y,pdefault_z]', 'pdefault_x.KIND = PDDEFERRED', 'pdefault_y.KIND = PDSTORED', 'pdefault_z.KIND = PDSTORED', 'P.FOLD.FUNCTION = eps']}
PENDING = {'callable': 'first-class callable constant initializer', 'closure': 'closure constant initializer', 'object': 'object constant initializer'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/default_parameter_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='default-parameter-compiler-', dir=ROOT / '.tools'))
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

    frontend = types.Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')])
    adapter = types.Worker([str(adapter_path), str(ROOT)])
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
        fixture.write_text(compiler.PREFIX + '\n'.join(assertions) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{i}()\n' for i in range(len(assertions))))
        result = run([str(runner), *map(str, modules), str(fixture)], 'spectec')
        assert result.returncode == 0 and result.stdout.strip() == b'true' and not result.stderr, result
    finally:
        frontend.close()
        adapter.close()
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in files}
    report = {'scope': 'Positional defaults compiler phases and original parameter/code projections; runtime receive pairing is a separate gate.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/default-parameter-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;',len(PENDING),'explicit pending controls')


if __name__ == '__main__':
    main()
