#!/usr/bin/env python3
"""Throw and catch compiler effects, header order, CV facts and source lines."""
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
    'throw': '<?php\nthrow 1;\n',
    'folded': '<?php\necho (throw 1) + 2;\n',
    'dead': '<?php\n(throw 1) || $a[];\n',
    'multiline': '<?php\nthrow (\n  1 +\n  2\n);\n',
    'try': '<?php\ntry {$a = 1;} catch (Missing|Throwable $e) {$b = 2;} catch (Error) {$c = 3;}\n',
    'names': '<?php namespace N; use Throwable as T; try {} catch (T|\\Error $e) {}\n',
    'finally': '<?php try {echo 1;} finally {echo 2;}\n',
    'catch-finally': '<?php try {} catch (Throwable) {} finally {}\n',
    'optional': '<?php try {} catch (Throwable) {}\n',
    'globals': '<?php try {} catch (Throwable $_GET) {} catch (Error $GLOBALS) {}\n',
    'header': '<?php try {} catch (Throwable $http_response_header) {echo $http_response_header;}\n',
    'goto-try': '<?php goto L; try {L: echo 1;} catch (Throwable) {}\n',
    'goto-catch': '<?php goto L; try {} catch (Throwable) {L: echo 1;}\n',
    'bad-first': '<?php\ntry{}catch(\n self | Exception\n $this\n){}\n',
    'bad-this': '<?php\ntry{}catch(\n Exception | self\n $this\n){}\n',
    'bad-try-first': '<?php\ntry {echo $a[];} catch (self $e) {}\n',
    'bad-body-first': '<?php\ntry {} catch (Exception $e) {echo $a[];} catch (self $e) {}\n',
    'bad-qualified': '<?php\ntry {} catch (\\self $e) {}\n',
    'bad-relative': '<?php\ntry {} catch (namespace\\self $e) {}\n',
    'bad-second-line': '<?php\ntry{}catch(\n Exception |\n self $e\n){}\n',
    'bad-write': '<?php\n(throw 1)[0] = 2;\n',
    'bad-constant': '<?php\nconst X = throw 1;\n',
}
CONTEXTS = {}
for name in ('throw', 'multiline'):
    CONTEXTS[name] = [
        'pcpath_throw = [PCINDEX 0, PCFIELD 0]',
        '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_throw) = (NExprThrow expression_child metadata_throw)',
        '$ppaccess(P, pcpath_throw) = (PPR)',
        '(PPCEFFECT pcpath_throw) <- P.EXPRESSIONS',
        '$pptemporary(NExprThrow expression_child metadata_throw)',
        '$ppconstants(P) = PPCCONSTANTS (pcpath_constant, pvalue_constant)*',
        '$ppconstant_at((pcpath_constant, pvalue_constant)*, pcpath_throw) = (PBOOL true)',
        '$pffact(P.FOLD.FACTS, pcpath_throw) = eps',
    ]
CONTEXTS['throw'] += ['$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_throw) = ((2, true))']
CONTEXTS['multiline'] += ['$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_throw) = ((4, true))']
CONTEXTS['folded'] = [
    'pcpath_parent = [PCINDEX 0, PCFIELD 0, PCINDEX 0]',
    '$ppconstants(P) = PPCCONSTANTS (pcpath_constant, pvalue_constant)*',
    '$ppconstant_at((pcpath_constant, pvalue_constant)*, pcpath_parent) = (PINT 3)',
    '$effect_select($compiled_operands(P, P.EXPRESSIONS), $compiled_operands(P, P.EXPRESSIONS), pcpath_parent) = [CODEEFFECT (pcpath_parent ++ [PCFIELD 0])]',
]
CONTEXTS['dead'] = [
    '$ppaccess(P, [PCINDEX 0, PCFIELD 0, PCFIELD 1]) = eps',
    '(PPCEFFECT ([PCINDEX 0, PCFIELD 0, PCFIELD 0])) <- P.EXPRESSIONS',
]
CONTEXTS['try'] = [
    'P.CVS = [$ptascii("a"), $ptascii("e"), $ptascii("b"), $ptascii("c")]',
    '$code_name($compiled_names(P.NAMES), [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 0, PCINDEX 0]) = (($ptascii("Missing"), eps))',
    '$code_name($compiled_names(P.NAMES), [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 0, PCINDEX 1]) = (($ptascii("Throwable"), eps))',
    '$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 1]) = ((2, false))',
]
CONTEXTS['names'] = [
    '$code_name($compiled_names(P.NAMES), [PCINDEX 0, PCFIELD 1, PCINDEX 1, PCFIELD 1, PCINDEX 0, PCFIELD 0, PCINDEX 0]) = (($ptascii("Throwable"), eps))',
    '$code_name($compiled_names(P.NAMES), [PCINDEX 0, PCFIELD 1, PCINDEX 1, PCFIELD 1, PCINDEX 0, PCFIELD 0, PCINDEX 1]) = (($ptascii("Error"), eps))',
]
CONTEXTS['globals'] = [
    'P.CVS = [$ptascii("_GET"), $ptascii("GLOBALS")]',
    'P.AUTOGLOBALS = eps',
    'P.GLOBALS = eps',
]
CONTEXTS['header'] = ['~P.HEADERASSIGNED', 'P.CVS = [$ptascii("http_response_header")]']
CONTEXTS['optional'] = ['P.CVS = eps']


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
    out = Path(tempfile.mkdtemp(prefix='throwable-compiler-', dir=ROOT / '.tools'))
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
                      'checked': checked, 'lint_exit': native.returncode, 'events': events,
                      'expected_unsupported': name in ('finally', 'catch-finally')}
            records.append(record)
            (out / 'records.json').write_text(json.dumps(records, indent=2) + '\n')
            body = f'  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n'
            if name not in ('finally', 'catch-finally'):
                body += '  -- if $pptrace(P) = ' + context.expected_events(events, file) + '\n'
            if name in ('finally', 'catch-finally'):
                body += '  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED \"finally unwinding\")\n'
            elif native.returncode == 0:
                body += '  -- if P.COMPLETION = PPCNORMAL\n  -- if ~P.RETURNREF\n'
                body += '  -- if pcode = {STRICT P.ENV.STRICT, GLOBALS P.GLOBALS, UNIT P.FOLD.SOURCE.ID, EXPRESSIONS ($compiled_operands(P, P.EXPRESSIONS) ++ $compiled_gotos(P.GOTOS, P.LABELS) ++ $compiled_writes(P.WRITES)), NAMES $compiled_names(P.NAMES), REDIRECTS $compiled_redirects(P.REDIRECTS)}\n'
                body += '  -- if $throwable_unit_code_valid(P, pcode)\n'
                if name in ('throw', 'multiline', 'folded', 'dead', 'try', 'names'):
                    body += '  -- if ~$throwable_unit_code_valid(P, pcode[.EXPRESSIONS = eps])\n'
                if name in ('try', 'names', 'optional'):
                    body += '  -- if ~$throwable_unit_code_valid(P, pcode[.NAMES = eps])\n'
                body += ''.join('  -- if '+condition+'\n' for condition in CONTEXTS.get(name, []))
            record['projection_assertions'] = body.count('  -- if ') - 1 - int(not record['expected_unsupported'])
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
    report = {'scope': 'No-finally throw/catch compilation, native lint diagnostics, constant effects, catch header ordering and CV facts; runtime outcomes are checked separately.',
              'result': 'pass', 'compared': len(CASES) - 2, 'unsupported_controls': 2, 'context_assertions': sum(r['projection_assertions'] for r in records), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (out / 'report-full.json').write_text(json.dumps(report, indent=2) + '\n')
    report['cases'] = [{key: value for key, value in record.items() if key != 'checked'} for record in records]
    (ROOT / 'coverage/semantics/throwable-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records) - 2, 'exact compiler phase comparisons; 2 Unsupported controls;', report['context_assertions'], 'source projections')


if __name__ == '__main__':
    main()
