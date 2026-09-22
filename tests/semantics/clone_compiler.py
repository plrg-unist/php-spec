#!/usr/bin/env python3
"""Clone compiler result categories, static restrictions and source lines."""
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
CASES = {
    'literal': '<?php\n$x=new stdClass;\n$y=clone $x;\n',
    'multiline': '<?php\nclone\n$missing\n;\n',
    'badwrite': '<?php\n$x=new stdClass;\n(clone $x)[0]=1;\n',
    'badread': '<?php\nclone $a[];\n',
    'badconstant': '<?php\nconst X=clone $x;\n',
    'refsend': '<?php\nfunction f(&$x){}\n$x=new stdClass;f(clone $x);\n',
    'refreturn': '<?php\nfunction &f(){$x=new stdClass;return clone $x;}\n',
    'withprops': '<?php\n$x=new stdClass;clone($x,["a"=>1]);\n',
}
CONTEXTS = {
    'literal': [
        'pcpath_clone = [PCINDEX 1, PCFIELD 0, PCFIELD 1]',
        '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_clone) = (NExprClone expression_child metadata_clone)',
        '$ppaccess(P, pcpath_clone) = (PPR)',
        '$ppaccess(P, pcpath_clone ++ [PCFIELD 0]) = (PPR)',
        '~$ppsend_var(NExprClone expression_child metadata_clone)',
        '~$ppreturn_variable(NExprClone expression_child metadata_clone)',
        '~$ppreturn_call(NExprClone expression_child metadata_clone)',
        '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_clone) = ((3, false))',
        '$ppconstants(P) = PPCCONSTANTS (pcpath_constant, pvalue_constant)*',
        '$ppconstant_at((pcpath_constant, pvalue_constant)*, pcpath_clone) = eps',
        'P_missing = $ppexpr(P, pcpath_clone, NExprClone expression_child eps, PPR)',
        'P_missing.COMPLETION = PPCABRUPT (UNSUPPORTED text)',
        'P_negative = $ppexpr(P, pcpath_clone, NExprClone expression_child ([McloneExprLine $(-1)]), PPR)',
        'P_negative.COMPLETION = PPCABRUPT (UNSUPPORTED text_negative)',
    ],
    'multiline': [
        '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX 0, PCFIELD 0]) = ((3, false))',
    ],
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='clone-compiler-', dir=ROOT / '.tools'))
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
    report = {'scope': 'Clone compilation, native lint diagnostics, temporary result category and source lines; runtime outcomes are checked separately.',
              'result': 'pass', 'compared': len(CASES), 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (out / 'report-full.json').write_text(json.dumps(report, indent=2) + '\n')
    report['cases'] = [{key: value for key, value in record.items() if key != 'checked'} for record in records]
    (ROOT / 'coverage/semantics/clone-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records), 'exact compiler phase comparisons;', sum(map(len, CONTEXTS.values())), 'source projections')


if __name__ == '__main__':
    main()
