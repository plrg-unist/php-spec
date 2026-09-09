#!/usr/bin/env python3
"""Pinned compile phase and argument-fetch descriptors, separate from execution."""
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
CASES = json.loads((ROOT / 'tests/semantics/function_argument_cases.json').read_text())


# These paths are original checked declaration/body/argument occurrences.
ARG = '[PCINDEX 0, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]'
SELF_ARG = '[PCINDEX 0, PCFIELD 5, PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]'
KEY_ARG = '[PCINDEX 1, PCFIELD 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]'
CONTEXTS = {
    'forward-value-append': [f'pcpath_arg = {ARG}', f'$ppaccess(P, {ARG}) = (PPF)', f'$ppaccess(P, {ARG} ++ [PCFIELD 0]) = (PPF)', f'$compiled_argument(P, {ARG}) = [(CODEARG pcpath_arg)]', 'pcode = $ppfunction_code(P)', f'(CODEARG pcpath_arg) <- pcode.EXPRESSIONS'],
    'builtin-reference-append': [f'$ppaccess(P, {ARG}) = (PPW)', f'$ppaccess(P, {ARG} ++ [PCFIELD 0]) = (PPW)', f'$compiled_argument(P, {ARG}) = eps'],
    'deferred-header-direct': [f'$ppaccess(P, {ARG}) = (PPR)', f'$compiled_argument(P, {ARG}) = eps', '~P.HEADERASSIGNED'],
    'deferred-outer-key-call': [f'$ppaccess(P, {KEY_ARG}) = (PPF)', f'$ppaccess(P, {KEY_ARG} ++ [PCFIELD 0]) = (PPF)', f'$ppaccess(P, {KEY_ARG} ++ [PCFIELD 1]) = (PPR)', f'$compiled_argument(P, {KEY_ARG} ++ [PCFIELD 1]) = eps'],
    'deferred-skipped-self': [f'pcpath_arg = {SELF_ARG}', '$ppfunction_early(P.FUNCTIONS, ([102])) = (pfunction)', f'(CODEARG pcpath_arg) <- pfunction.CODE.EXPRESSIONS', 'pcode = $ppfunction_code(P)', f'~((CODEARG pcpath_arg) <- pcode.EXPRESSIONS)'],
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'tests/semantics/function_argument_cases.json',
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='function-argument-compiler-', dir=ROOT / '.tools'))
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
    report = {'scope': 'argument compiler phase; execution and descriptor corruption gates are separate',
              'result': 'pass', 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (ROOT / 'coverage/semantics/function-argument-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records), 'exact compiler phase comparisons')


if __name__ == '__main__':
    main()
