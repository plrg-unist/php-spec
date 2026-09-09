#!/usr/bin/env python3
"""User constant compiler phases and original declaration descriptors."""
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
CASES = json.loads((ROOT / 'tests/semantics/user_constant_cases.json').read_text())


# Declaration/source paths and emitted compiler lines checked against the pinned compiler.
CONTEXTS = {'literal': ['pcpath_decl = [PCINDEX 0, PCFIELD 1, PCINDEX 0]', '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_decl) = ((1, false))', '(CODENAME pcpath_decl ([67]) eps) <- $compiled_names(P.NAMES)', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_decl) = (NConst phpType11 expression metadata)', 'pcpath_value = pcpath_decl ++ [PCFIELD 1]', '$ppconstants(P) = PPCCONSTANTS (pcpath_constant, pvalue_constant)*', '$ppconstant_at((pcpath_constant, pvalue_constant)*, pcpath_value) = (PINT 1)'], 'unknown': ['pcpath_decl = [PCINDEX 0, PCFIELD 1, PCINDEX 0]', '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_decl) = ((1, false))', '(CODENAME pcpath_decl ([67]) eps) <- $compiled_names(P.NAMES)', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_decl) = (NConst phpType11 expression metadata)', 'pcpath_value = pcpath_decl ++ [PCFIELD 1]', '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_value) = ((1, false))'], 'multiline': ['pcpath_decl = [PCINDEX 0, PCFIELD 1, PCINDEX 0]', '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_decl) = ((3, false))', '(CODENAME pcpath_decl ([67]) eps) <- $compiled_names(P.NAMES)', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_decl) = (NConst phpType11 expression metadata)'], 'namespace': ['pcpath_decl = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1, PCINDEX 0]', '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_decl) = ((1, false))', '(CODENAME pcpath_decl ([78, 92, 67]) eps) <- $compiled_names(P.NAMES)', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_decl) = (NConst phpType11 expression metadata)', '(PLCONSTANT, [78,92,67]) <- P.ENV.SEEN'], 'two': ['pcpath_decl = [PCINDEX 0, PCFIELD 1, PCINDEX 0]', '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_decl) = ((1, false))', '(CODENAME pcpath_decl ([65]) eps) <- $compiled_names(P.NAMES)', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_decl) = (NConst phpType11 expression metadata)', 'pcpath_second = [PCINDEX 0, PCFIELD 1, PCINDEX 1]', '(CODENAME pcpath_second ([66]) eps) <- $compiled_names(P.NAMES)', '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_second) = ((1, false))']}
PENDING = {'object': 'object constant initializer', 'closure': 'closure constant initializer', 'callable': 'first-class callable constant initializer', 'class-constant': 'constant class-constant lookup', 'class-name': 'constant class-name resolution', 'constant-property': 'property constant initializer', 'constant-nullsafe-property': 'property constant initializer', 'literal-nullsafe-property': 'property constant initializer', 'static-first-class-callable': 'first-class callable constant initializer', 'self-class-constant-invalid': 'constant class-constant lookup'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/user_constant_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='user-constant-compiler-', dir=ROOT / '.tools'))
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
    report = {'scope': 'Private user-constant compiler phase; actual declaration/lookup runtime consumer pending. No published source activation.',
              'result': 'pass', 'compared': len(CASES)-len(PENDING), 'pending': PENDING, 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/user-constant-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records)-len(PENDING), 'exact compiler phase comparisons;',len(PENDING),'explicit pending controls')


if __name__ == '__main__':
    main()
