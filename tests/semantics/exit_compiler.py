#!/usr/bin/env python3
"""Exit compiler call identity, modes, reference contexts and source lines."""
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
CASES = {'bare': '<?php\nexit\n;\n',
 'empty': '<?php\nexit(\n);\n',
 'value': '<?php\ndie(\n  $x\n);\n',
 'named': '<?php\nexit(status: $x);\n',
 'named_die': '<?php\nnamespace N; die(status: $x);\n',
 'qualified_die': '<?php\n\\die(status: $x);\n',
 'literal': '<?php\n"die"($x);\n',
 'firstclass': '<?php\ndie(...);\n',
 'alias': '<?php\nnamespace N; use function \\die as stop; stop(...);\n',
 'dynamic': '<?php\n$f="exit"; $f($x);\n',
 'unpack': '<?php\nexit(...$a);\n',
 'pipe': '<?php\n1 |> exit(...);\n',
 'refsend': '<?php\nfunction f(&$x) {} f(exit());\n',
 'refassign': '<?php\n$x =& \\exit();\n',
 'writebase': '<?php\n(exit())[0] = 1;\n',
 'refreturn': '<?php\nfunction &f() { return exit(); }\n',
 'badread': '<?php\nexit($a[]);\n',
 'badupdate': '<?php\n++\\exit();\n',
 'badarrayref': '<?php\n$x = [&\\exit($a[])];\n',
 'badconstant': '<?php\nconst X = exit();\n',
 'named_positional': '<?php\nexit(status: 1, 2);\n',
 'named_unpack': '<?php\nexit(status: 1, ...$a);\n',
 'named_multiline': '<?php\nexit(\n status: $x\n);\n',
 'firstclass_multiline': '<?php\ndie(\n ...\n);\n',
 'qualified_multiline': '<?php\n\\die(\n status: $x\n);\n'}
CONTEXTS = {'bare': ['pcpath_exit = [PCINDEX 0, PCFIELD 0]',
          '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_exit) = (NExprExit phpType5_child '
          'metadata_exit)',
          '$ppaccess(P, pcpath_exit) = (PPR)',
          '$code_name($compiled_names(P.NAMES), pcpath_exit) = (($ptascii("exit"), eps))',
          '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_exit) = ((3, false))',
          '$ppsend_var(NExprExit phpType5_child metadata_exit)',
          '$ppreturn_call(NExprExit phpType5_child metadata_exit)',
          '$pffact(P.FOLD.FACTS, pcpath_exit) = eps'],
 'empty': ['pcpath_exit = [PCINDEX 0, PCFIELD 0]',
           '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_exit) = (NExprExit phpType5_child '
           'metadata_exit)',
           '$ppaccess(P, pcpath_exit) = (PPR)',
           '$code_name($compiled_names(P.NAMES), pcpath_exit) = (($ptascii("exit"), eps))',
           '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_exit) = ((3, false))',
           '$ppsend_var(NExprExit phpType5_child metadata_exit)',
           '$ppreturn_call(NExprExit phpType5_child metadata_exit)',
           '$pffact(P.FOLD.FACTS, pcpath_exit) = eps'],
 'value': ['pcpath_exit = [PCINDEX 0, PCFIELD 0]',
           '$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_exit) = (NExprExit phpType5_child '
           'metadata_exit)',
           '$ppaccess(P, pcpath_exit) = (PPR)',
           '$code_name($compiled_names(P.NAMES), pcpath_exit) = (($ptascii("exit"), eps))',
           '$code_expression($compiled_operands(P, P.EXPRESSIONS), pcpath_exit) = ((4, false))',
           '$ppsend_var(NExprExit phpType5_child metadata_exit)',
           '$ppreturn_call(NExprExit phpType5_child metadata_exit)',
           '$pffact(P.FOLD.FACTS, pcpath_exit) = eps',
           '$ppaccess(P, pcpath_exit ++ [PCFIELD 0]) = (PPR)'],
 'named': ['pcpath_exit = [PCINDEX 0, PCFIELD 0]',
           '$code_name($compiled_names(P.NAMES), pcpath_exit) = (($ptascii("exit"), eps))',
           '$ppaccess(P, pcpath_exit ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]) = (PPR)'],
 'qualified_die': ['pcpath_exit = [PCINDEX 0, PCFIELD 0]',
                   '$code_name($compiled_names(P.NAMES), pcpath_exit) = (($ptascii("die"), eps))'],
 'literal': ['pcpath_exit = [PCINDEX 0, PCFIELD 0]',
             '$code_name($compiled_names(P.NAMES), pcpath_exit) = (($ptascii("die"), eps))'],
 'firstclass': ['pcpath_exit = [PCINDEX 0, PCFIELD 0]',
                '$code_name($compiled_names(P.NAMES), pcpath_exit) = (($ptascii("exit"), eps))'],
 'alias': ['pcpath_exit = [PCINDEX 0, PCFIELD 1, PCINDEX 1, PCFIELD 0]',
           '$code_name($compiled_names(P.NAMES), pcpath_exit) = (($ptascii("die"), eps))'],
 'named_die': ['pcpath_exit = [PCINDEX 0, PCFIELD 1, PCINDEX 0, PCFIELD 0]',
               '$code_name($compiled_names(P.NAMES), pcpath_exit) = (($ptascii("exit"), eps))'],
 'named_multiline': ['$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX 0, PCFIELD '
                     '0]) = ((4, false))'],
 'firstclass_multiline': ['$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX 0, '
                          'PCFIELD 0]) = ((4, false))'],
 'qualified_multiline': ['$code_expression($compiled_operands(P, P.EXPRESSIONS), [PCINDEX 0, '
                         'PCFIELD 0]) = ((2, false))']}

# Each case has one root callee; preserve the rest of its source descriptors.
FORGERY_PREFIX = r'''
dec $exit_test_edit(pcodeexpr*, pcpath, nat) : pcodeexpr*
def $exit_test_edit(eps, pcpath, n) = eps
def $exit_test_edit((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath, 0) = (CODEEXPR pcpath $(z + 1) b) :: pcodeexpr*
def $exit_test_edit((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath, 1) = (CODEEXPR pcpath z (~b)) :: pcodeexpr*
def $exit_test_edit((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath, 2) = pcodeexpr*
def $exit_test_edit((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath, 3) = (CODEEXPR pcpath z b) :: (CODEEXPR pcpath z b) :: pcodeexpr*
def $exit_test_edit(pcodeexpr :: pcodeexpr_tail*, pcpath, n) = pcodeexpr :: $exit_test_edit(pcodeexpr_tail*, pcpath, n)
  -- if $call_expr_match(pcodeexpr, pcpath) = 0
'''
for name in ('bare', 'empty', 'value', 'named', 'qualified_die', 'literal', 'firstclass', 'alias', 'named_die'):
    CONTEXTS[name] += ['pcode = $ppfunction_code(P)', '$exit_unit_code_valid(P, pcode)']
    CONTEXTS[name] += [f'~$exit_unit_code_valid(P, pcode[.EXPRESSIONS = $exit_test_edit(pcode.EXPRESSIONS, pcpath_exit, {mode})])'
                       for mode in range(4)]
    CONTEXTS[name] += ['~$exit_unit_code_valid(P, pcode[.NAMES = eps])',
                      '~$exit_unit_code_valid(P, pcode[.NAMES = [CODENAME pcpath_exit $ptascii("forged") eps]])',
                      '~$exit_unit_code_valid(P, pcode[.NAMES = pcode.NAMES ++ pcode.NAMES])',
                      '~$exit_unit_code_valid(P, pcode[.NAMES = [CODENAME pcpath_exit $ptascii("exit") ($ptascii("fallback"))]])']
CONTEXTS['firstclass'] += ['$occurrence_node(P.FOLD.SOURCE.OCCURRENCES, pcpath_exit) = (NExprFuncCall phpType19_callee phpType6_args metadata_call)',
                         '$ppunpack_node(pcode, P.FOLD.SOURCE, pcpath_exit, NExprFuncCall phpType19_callee phpType6_args metadata_call) = (UNPACK_VALUE)']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    modules += [ROOT / 'spec/semantics/147-exit-compiler.watsup'] if ROOT / 'spec/semantics/147-exit-compiler.watsup' not in modules else []
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    files = [*modules, runner, adapter_path, types.PHP, Path(__file__),
             ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
             ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p.relative_to(ROOT)): digest(p) for p in files}
    out = Path(tempfile.mkdtemp(prefix='exit-compiler-', dir=ROOT / '.tools'))
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
        fixture.write_text(compiler.PREFIX + FORGERY_PREFIX + '\n'.join(assertions) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{i}()\n' for i in range(len(assertions))))
        result = run([str(runner), *map(str, modules), str(fixture)], 'spectec')
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in files}
    report = {'scope': 'Exit compilation, native lint diagnostics, call identity, reference category and source lines; runtime outcomes are checked separately.',
              'result': 'pass', 'compared': len(CASES), 'context_assertions':sum(map(len,CONTEXTS.values())), 'cases': records, 'inputs': before, 'raw': str(out.relative_to(ROOT)),
              'fixture_sha256': digest(fixture)}
    (out / 'report-full.json').write_text(json.dumps(report, indent=2) + '\n')
    report['cases'] = [{key: value for key, value in record.items() if key != 'checked'} for record in records]
    (ROOT / 'coverage/semantics/exit-compiler.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(records), 'exact compiler phase comparisons;', sum(map(len, CONTEXTS.values())), 'source projections')


if __name__ == '__main__':
    main()
