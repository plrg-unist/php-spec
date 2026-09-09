#!/usr/bin/env python3
"""Private reference-send result-kind phase checks, separate from runtime pairing."""
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
CASES = json.loads((ROOT / 'tests/semantics/function_reference_send_cases.json').read_text())


# Source occurrence and expected result kinds audited against pinned compiler and native originals.
CONTEXTS = {'list-variable': ['pcpath_arg = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '~$ppsend_var(expression)'], 'list-call': ['pcpath_arg = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '$ppsend_var(expression)'], 'list-literal': ['pcpath_arg = [PCINDEX 1, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '~$ppsend_var(expression)'], 'list-reference-variable': ['pcpath_arg = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '$ppsend_var(expression)'], 'list-reference-call': ['pcpath_arg = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '$ppsend_var(expression)'], 'list-reference-dimension': ['pcpath_arg = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '$ppsend_var(expression)'], 'list-value-dimension': ['pcpath_arg = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '~$ppsend_var(expression)'], 'list-reference-nested': ['pcpath_arg = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '$ppsend_var(expression)'], 'forward-list-call': ['pcpath_arg = [PCINDEX 1, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '$ppsend_var(expression)'], 'forward-list-reference-variable': ['pcpath_arg = [PCINDEX 1, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '$ppsend_var(expression)'], 'constant-ternary-variable': ['pcpath_arg = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '~$ppsend_var(expression)'], 'constant-coalesce-variable': ['pcpath_arg = [PCINDEX 2, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]', '$origin_node([P.FOLD.SOURCE], PORIGIN 91 pcpath_arg) = (expression)', '~$ppsend_var(expression)']}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/function_reference_send_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='function-reference-send-compiler-', dir=ROOT / '.tools'))
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
            body += '  -- if $pptrace(P) = ' + context.expected_events(events, file) + '\n'
            if native.returncode == 0:
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
    report = {'scope': 'Private positional reference parameter compiler phase; actual reference send/bind runtime consumer pending. No published source activation.',
              'result': 'pass', 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/function-reference-send-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records), 'exact compiler phase comparisons')


if __name__ == '__main__':
    main()
